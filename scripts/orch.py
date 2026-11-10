"""Điều phối pipeline làm game: mọi task chạy bằng claude CLI, mọi hoạt động ghi lịch sử để truy vết ngược.

Lệnh (chạy ở gốc repo dự án):
  orch.py init [--slug ten-game] [--no-git] [--no-guard]
                                                 tạo .game/ (intake, config, state, lịch sử, task R1/R2) + .claude/guard.json
  orch.py phase <tên>                            chuyển giai đoạn (ghi lịch sử)
  orch.py log <mã> "<nội dung>" [--task T01]     ghi 1 sự kiện tay (cổng duyệt, quyết định người dùng)
  orch.py branch                                 tạo nhánh tích hợp game/<slug> từ nhánh hiện tại
  orch.py run T01 [T02 ...] [--parallel [N]] [--merge] [--fix] [--dry-run]
                                                 chạy task bằng claude CLI, test, ghi báo cáo.
                                                 --parallel: song song theo độ nặng (mỗi task code 1 git worktree),
                                                 test vẫn tuần tự từng task; --merge: tự gộp task đạt
  orch.py merge T01 [T02 ...]                    gộp nhánh task đã đạt vào nhánh tích hợp
  orch.py test [--cmd "<lệnh>"]                  test tích hợp trên nhánh hiện tại
  orch.py status                                 bảng trạng thái task
  orch.py report                                 sinh .game/REPORT.md
  orch.py history [--task T] [--file F] [--event E] [--since 2026-11-01] [-n 40]
                                                 lọc lịch sử; --file: task / commit nào đã sửa file đó
  orch.py config [khoá [giá trị]]                xem / đổi .game/config.json (giá trị dạng JSON hoặc chuỗi)
  orch.py open T01 [--here]                      làm tay 1 task: dựng nhánh / worktree, in lệnh mở claude (tiếp phiên cũ nếu có)
  orch.py done T01 [--note "..."] [--fail]       chốt task làm tay: commit, test, REPORT.md, lịch sử như task tự động

Mỗi lần chạy task: .game/runs/<T>/<thời điểm>-a<lần>/ gồm prompt.md, transcript.jsonl (mọi lượt gọi tool),
result.json, test.log, diff.txt, REPORT.md. Lịch sử: .game/history.jsonl (máy) + .game/HISTORY.md (người).
"""
import argparse
import datetime as dt
import fnmatch
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import uuid
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

G = ".game"
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCK = threading.Lock()

# Báo cáo bắt buộc của worker (claude --json-schema): orch tự đo thêm nhánh, commit, file đổi, test
REPORT_SCHEMA = {
    "type": "object",
    "properties": {
        "result": {"type": "string", "enum": ["done", "partial", "failed"]},
        "summary": {"type": "string", "description": "Đã làm gì, 2-5 câu"},
        "files_changed": {"type": "array", "items": {"type": "object", "properties": {
            "path": {"type": "string"}, "change": {"type": "string"}}, "required": ["path", "change"]}},
        "checks_run": {"type": "array", "items": {"type": "object", "properties": {
            "cmd": {"type": "string"}, "ok": {"type": "boolean"}, "note": {"type": "string"}},
            "required": ["cmd", "ok"]}},
        "not_done": {"type": "array", "items": {"type": "string"}},
        "risks": {"type": "array", "items": {"type": "string"}},
        "notes_for_next": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["result", "summary", "files_changed", "checks_run", "not_done"],
}

WORKER_RULES = """Bạn là WORKER trong pipeline làm game do orchestrator điều phối. Luật:
- Chỉ làm đúng task được giao, chỉ sửa file trong PHẠM VI. Cần sửa ngoài phạm vi: không sửa, ghi vào not_done.
- KHÔNG git commit / checkout / merge / reset / stash (orchestrator làm). KHÔNG sửa thư mục .game/ trừ file output được chỉ định.
- Tuân thủ AGENTS.md / CLAUDE.md / .claude/game-profile.md của repo. Không sửa tay YAML Unity, không xoá .meta, không đọc file bí mật.
- Không hỏi lại người dùng (không ai trả lời). Thiếu thông tin: chọn phương án an toàn nhất, ghi vào risks.
- Thư mục làm việc đã là gốc repo: chạy lệnh trực tiếp, KHÔNG "cd ... &&" (quyền chỉ cho lệnh bắt đầu đúng tên công cụ).
- Chạy các lệnh kiểm tra được giao trước khi báo cáo. Báo cáo trung thực: lỗi còn thì result = partial/failed.
- Kết thúc bằng báo cáo theo schema (tiếng Việt)."""

DEFAULT_CONFIG = {
    "slug": "",
    "git": True,
    "base_branch": "",
    "integration_branch": "",
    "claude": "",
    "model": "sonnet",
    "effort": "",
    "budget_usd": 3.0,
    "timeout_s": 3600,
    "max_fix": 2,
    "fix_model_up": {"haiku": "sonnet"},  # lần sửa (--fix) tự lên model mạnh hơn
    "max_parallel": 3,          # số phiên claude tối đa cùng lúc
    "max_load": 4,              # tổng độ nặng tối đa cùng lúc (nhẹ 1, vừa 2, nặng 3; task Unity chiếm hết)
    "worktree_dir": "",         # mặc định <repo>-wt cạnh repo; nên đặt ở ổ còn trống nhiều
    "commit_ignore": ["*.pyc", "*/__pycache__/*", "__pycache__/*", ".DS_Store", "Thumbs.db"],  # file rác không commit / không tính scope
    "worktree_copy": ["*.csproj", "*.sln"],
    "worktree_links": ["Library", "Temp/Bin"],
    "allowed_tools": ["Read", "Edit", "Write", "Glob", "Grep", "TodoWrite",
                      "Bash(dotnet build:*)", "Bash(python:*)", "Bash(git status:*)", "Bash(git diff:*)",
                      "Bash(ls:*)", "Bash(node:*)"],
    "research_tools": ["Read", "Glob", "Grep", "Write", "WebSearch", "WebFetch", "TodoWrite",
                       "Bash(git log:*)", "Bash(ls:*)"],
    "review_tools": ["Read", "Glob", "Grep", "Write", "Bash(git diff:*)", "Bash(git log:*)", "Bash(git show:*)"],
    "tests": [],
}

INTAKE = """# Intake — điền rồi báo Claude

## 1. Ý tưởng
- Tên game (tạm):
- Thể loại / cơ chế chính:
- Mô tả ngắn (người chơi làm gì, thắng / thua thế nào):
- Điểm khác biệt so với game tham khảo:

## 2. Tham khảo
- Link game tham khảo (store / video):
- Ảnh (đường dẫn file hoặc thư mục):
- Video gameplay (link / file):
- Art mẫu / mockup UI có sẵn:

## 3. Phạm vi bản đầu
- Số level / màn bản đầu:
- Tính năng bắt buộc (vd hint, daily, spin, shop):
- Không làm ở bản đầu:
- Hạn / mốc:

## 4. Kỹ thuật
- Base dự án dùng (repo / thư mục clone từ):
- Unity version, nền tảng (Android / iOS):
- Spine / animation:
- SDK quảng cáo / analytics / IAP (chỉ tên, không ghi key):
- Ngôn ngữ (localization):

## 5. Khác
- Ràng buộc / mong muốn riêng:
"""


# ---------------------------------------------------------------- tiện ích

def now():
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


def stamp():
    return dt.datetime.now().strftime("%Y%m%d-%H%M%S")


def rd(path, default=None):
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8-sig") as f:
        return json.load(f) if path.endswith(".json") else f.read()


def wr(path, data):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        if isinstance(data, (dict, list)):
            json.dump(data, f, ensure_ascii=False, indent=2)
        else:
            f.write(data)


def sh(cmd, check=False, **kw):
    r = subprocess.run(cmd, shell=isinstance(cmd, str), capture_output=True, text=True,
                       encoding="utf-8", errors="replace", **kw)
    if check and r.returncode:
        raise SystemExit(f"Lệnh lỗi: {cmd}\n{r.stdout}\n{r.stderr}")
    return r


def git(*args, check=True, cwd=None):
    return sh(["git", *args], check=check, cwd=cwd).stdout.strip()


def cfg():
    c = dict(DEFAULT_CONFIG)
    c.update(rd(f"{G}/config.json", {}))
    return c


def state():
    return rd(f"{G}/state.json", {"phase": "intake", "tasks": {}})


def save_state(s):
    wr(f"{G}/state.json", s)


def history(event, msg, **fields):
    """Ghi 1 sự kiện vào history.jsonl + HISTORY.md (luồng an toàn)."""
    rec = {"ts": now(), "event": event, "msg": msg, **fields}
    with LOCK:
        with open(f"{G}/history.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        extra = " · ".join(f"{k}={v}" for k, v in fields.items() if v not in (None, "", [], {}))
        with open(f"{G}/HISTORY.md", "a", encoding="utf-8") as f:
            f.write(f"- `{rec['ts']}` **{event}** {msg}" + (f" — {extra}" if extra else "") + "\n")


def need_init():
    if not os.path.isdir(G):
        raise SystemExit("Chưa có .game/. Chạy: orch.py init")


def claude_exe(c):
    """Ưu tiên claude.exe native: gọi thẳng, không qua cmd.exe (giữ nguyên dấu nháy trong JSON)."""
    if c.get("claude"):
        return c["claude"]
    for name in ("claude.exe", "claude"):
        p = shutil.which(name)
        if p and not p.lower().endswith((".cmd", ".ps1")):
            return p
    npm = os.path.join(os.environ.get("APPDATA", ""), "npm", "node_modules", "@anthropic-ai", "claude-code", "bin", "claude.exe")
    if os.path.isfile(npm):
        return npm
    return shutil.which("claude") or "claude"


# ---------------------------------------------------------------- task

def parse_task(tid):
    files = glob.glob(f"{G}/tasks/{tid}.md") + glob.glob(f"{G}/tasks/{tid}-*.md")
    if not files:
        raise SystemExit(f"Không thấy file task {G}/tasks/{tid}*.md")
    text = rd(files[0])
    meta, body = {}, text
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.S)
    if m:
        body = m.group(2)
        for line in m.group(1).splitlines():
            if ":" not in line or line.strip().startswith("#"):
                continue
            k, v = line.split(":", 1)
            k = k.strip()
            v = re.split(r"\s+#\s", " " + v.strip() + " ", maxsplit=1)[0].strip()  # bỏ chú thích cuối dòng " # ..."
            if k == "test":
                meta.setdefault("test", []).append(v)
            else:
                meta[k] = v
    meta.setdefault("id", tid)
    meta.setdefault("title", os.path.basename(files[0])[:-3])
    meta.setdefault("kind", "code")
    meta["scope"] = [s.strip() for s in meta.get("scope", "").split(",") if s.strip()]
    meta["depends"] = [s.strip() for s in meta.get("depends", "").split(",") if s.strip()]
    meta["output"] = meta.get("output", f"{G}/research/{tid}.md" if meta["kind"] in ("research", "review") else "")
    meta["file"] = files[0].replace("\\", "/")
    meta["body"] = body.strip()
    return meta


def in_scope(path, t):
    p = path.replace("\\", "/")
    if t["output"] and p == t["output"].replace("\\", "/"):
        return True
    if t["kind"] in ("research", "review"):
        return p.startswith(G + "/")
    return any(fnmatch.fnmatch(p, s) or p.startswith(s.rstrip("*").rstrip("/") + "/") for s in t["scope"]) if t["scope"] else True


def changed_files(tracked_only=False, cwd=None):
    out = sh(["git", "status", "--porcelain", "-uno" if tracked_only else "-uall"], cwd=cwd).stdout
    files = []
    for line in out.splitlines():
        p = line[3:].strip().strip('"')
        if " -> " in p:
            p = p.split(" -> ", 1)[1]
        files.append(p.replace("\\", "/"))
    return files


def is_true(v):
    return str(v).strip().lower() in ("1", "true", "yes", "có")


# ---------------------------------------------------------------- độ nặng + song song

def count_scope_files(t, limit=300):
    n = 0
    for s in t["scope"]:
        pat = s if any(ch in s for ch in "*?[") else s.rstrip("/") + "/**"
        for f in glob.iglob(pat, recursive=True):
            if os.path.isfile(f):
                n += 1
                if n >= limit:
                    return n
    return n


def task_weight(t, c):
    """Độ nặng 1 (nhẹ) .. 3 (nặng). Task Unity = cả sức chứa (chạy một mình)."""
    cap = int(c["max_load"])
    if is_true(t.get("unity", "")):
        return cap
    w = t.get("weight") or {"s": 1, "m": 2, "l": 3}.get(str(t.get("size", "")).lower()[:1])
    if w:
        return max(1, min(int(w), cap))
    if t["kind"] in ("research", "review"):
        return 1
    score = 1
    if (t.get("model") or c["model"]) == "opus" or (t.get("effort") or c["effort"]) in ("high", "xhigh", "max"):
        score += 1
    if float(t.get("budget") or c["budget_usd"]) >= 5:
        score += 1
    if count_scope_files(t) > 40:  # phạm vi rộng → nhiều file phải đọc / sửa
        score += 1
    return min(score, 3, cap)


def scope_prefix(s):
    return re.split(r"[*?\[]", s.replace("\\", "/"))[0].rstrip("/")


def overlap(a, b):
    """2 task code có thể sửa chung file? (không rõ phạm vi = coi như chồng)."""
    if a["kind"] != "code" or b["kind"] != "code":
        return False
    if not a["scope"] or not b["scope"]:
        return True
    for x in a["scope"]:
        for y in b["scope"]:
            px, py = scope_prefix(x), scope_prefix(y)
            if not px or not py or px.startswith(py) or py.startswith(px):
                return True
    return False


def wt_path(c, tid):
    main = os.path.abspath(".")
    base = c.get("worktree_dir") or os.path.join(os.path.dirname(main), os.path.basename(main) + "-wt")
    return os.path.join(base, f"{c['slug']}-{tid}")


def link_dir(link, target):
    os.makedirs(os.path.dirname(link), exist_ok=True)
    if os.path.lexists(link):
        return
    if os.name == "nt":
        sh(["cmd", "/c", "mklink", "/J", link, target], check=True)  # junction: không cần quyền admin
    else:
        os.symlink(target, link, target_is_directory=True)


def make_worktree(c, tid, branch, integ):
    path = wt_path(c, tid)
    if os.path.isdir(path):
        return path
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if git("branch", "--list", branch):
        git("worktree", "add", path, branch)
    else:
        git("worktree", "add", "-b", branch, path, integ)
    main = os.path.abspath(".")
    # csproj (Unity sinh, gitignore) + Library / Temp/Bin dùng chung để worker build-check được trong worktree
    for pat in c["worktree_copy"]:
        for f in glob.glob(os.path.join(main, pat)):
            shutil.copy2(f, path)
    for rel in c["worktree_links"]:
        src = os.path.join(main, rel)
        if os.path.isdir(src):
            link_dir(os.path.join(path, rel), src)
    history("worktree_add", f"{tid} → {path}", task=tid, branch=branch)
    return path


def drop_worktree(c, path, tid=None):
    if not path or not os.path.isdir(path):
        return
    for rel in c["worktree_links"]:
        p = os.path.join(path, rel)
        if os.path.lexists(p):
            try:
                os.rmdir(p) if os.name == "nt" else os.unlink(p)  # chỉ gỡ liên kết, KHÔNG xoá thư mục đích
            except OSError as e:
                raise SystemExit(f"Không gỡ được liên kết {p}: {e}. Dừng để không xoá nhầm dữ liệu repo chính.")
    git("worktree", "remove", "--force", path)
    history("worktree_remove", path, task=tid)


# ---------------------------------------------------------------- chạy task: chuẩn bị → claude → kiểm tra

def build_prompt(t, c, branch, fix_log=None, attempt=1, repo=None, isolated=False):
    gdir = os.path.abspath(G).replace("\\", "/")
    tests = t.get("test", []) + (c["tests"] if t["kind"] == "code" else [])
    lines = [f"# Task {t['id']}: {t['title']}", "",
             f"- Repo (thư mục làm việc): {repo or os.getcwd()}",
             f"- Nhánh: {branch or '(không dùng git)'} — đã checkout sẵn, không đổi nhánh.",
             f"- Loại: {t['kind']} · lần chạy: {attempt}",
             "- Đọc trước: AGENTS.md / CLAUDE.md / .claude/game-profile.md (nếu có), "
             f"{gdir}/intake.md, {gdir}/plan.md (phần liên quan task này).",
             ]
    if isolated:
        lines.append("- Đây là git worktree riêng, đang chạy SONG SONG với task khác. Library / Temp/Bin là liên kết tới repo chính: "
                     "KHÔNG mở Unity, KHÔNG chạy Unity batchmode, KHÔNG sửa Library.")
    if t["kind"] == "code":
        lines.append("- PHẠM VI được sửa: " + (", ".join(t["scope"]) if t["scope"] else "(theo mô tả task)"))
    if t["output"]:
        lines.append(f"- Ghi kết quả vào: {os.path.abspath(t['output'])} (markdown, có nguồn / đường dẫn file đã đọc).")
    if tests:
        lines.append("- Lệnh kiểm tra phải chạy và đạt trước khi báo cáo:")
        lines += [f"  - `{x}`" for x in tests]
    if t["depends"]:
        lines.append("- Task trước đã xong: " + ", ".join(t["depends"]) + f" (báo cáo ở {gdir}/runs/<task>/).")
    lines += ["", "## Mô tả", t["body"]]
    rules = rd(os.path.join(SKILL_DIR, "RULES.md"), "") or ""
    rules = "\n".join(l for l in rules.splitlines() if l.startswith("- "))
    if rules:
        lines += ["", "## Luật chung GPlay (mọi game)", rules]
    if fix_log:
        lines += ["", "## LẦN SỬA: lần trước chưa đạt", "Sửa nguyên nhân gốc, không lách test. Log:", "```", fix_log[-6000:], "```"]
    return "\n".join(lines)


def run_tests(cmds, log_path, cwd=None):
    results, out = [], []
    env = {**os.environ, "PYTHONUTF8": "1"}  # Windows: python mặc định đọc file cp1252, test có tiếng Việt sẽ lỗi
    for cmd in cmds:
        r = sh(cmd, cwd=cwd, env=env)
        results.append({"cmd": cmd, "exit": r.returncode})
        out.append(f"$ {cmd}\n(cwd {cwd or os.getcwd()}, exit {r.returncode})\n{r.stdout[-8000:]}\n{r.stderr[-4000:]}\n")
    wr(log_path, "\n".join(out) or "(không có lệnh test)\n")
    return results


def render_report(t, info):
    w = info.get("worker") or {}
    L = [f"# Báo cáo {t['id']}: {t['title']}", "",
         f"- Thời điểm: {info['ended']} · lần chạy: {info['attempt']} · trạng thái: **{info['status']}**"
         f" · độ nặng {info.get('weight', '-')}" + (" · chạy song song" if info.get("isolated") else ""), "",
         "## Nơi thực hiện",
         f"- Repo: `{os.getcwd()}`",
         f"- Thư mục làm việc: `{info.get('cwd')}`" + (" (git worktree riêng)" if info.get("isolated") else ""),
         f"- Nhánh: `{info.get('branch') or '-'}` · commit: `{info.get('commit') or '-'}`",
         f"- Thư mục chạy: `{info['run_dir']}` (prompt, transcript, test log)",
         f"- Phiên claude: `{info.get('session_id')}` (xem lại: `claude --resume {info.get('session_id')}`)",
         f"- File đổi ({len(info['files'])}):"]
    L += [f"  - `{f}`" + ("" if f not in info["out_of_scope"] else "  ⚠ NGOÀI PHẠM VI") for f in info["files"]] or ["  - (không có)"]
    L += ["", "## Kết quả", f"- Worker báo: **{w.get('result', '?')}**", f"- {w.get('summary', info.get('error', ''))}"]
    for f in w.get("files_changed", []):
        L.append(f"  - `{f.get('path')}`: {f.get('change')}")
    L += ["", "## Kiểm tra"]
    L += [f"- Worker chạy `{x.get('cmd')}`: {'đạt' if x.get('ok') else 'LỖI'} {x.get('note', '')}" for x in w.get("checks_run", [])]
    L += [f"- Orchestrator chạy `{x['cmd']}`: {'đạt' if x['exit'] == 0 else 'LỖI (exit %d)' % x['exit']}" for x in info["tests"]]
    if not w.get("checks_run") and not info["tests"]:
        L.append("- (không có lệnh kiểm tra)")
    if info.get("denials"):
        L += ["", "## Bị từ chối quyền"] + [f"- {d}" for d in info["denials"]]
    for title, key in (("Chưa làm", "not_done"), ("Rủi ro", "risks"), ("Ghi chú cho task sau", "notes_for_next")):
        if w.get(key):
            L += ["", f"## {title}"] + [f"- {x}" for x in w[key]]
    L += ["", "## Chi phí", f"- ${info.get('cost', 0):.4f} · {info.get('turns', 0)} lượt · {info.get('duration_s', 0)} s"]
    return "\n".join(L) + "\n"


def deps_state(t, c, batch_ids=()):
    """'ok' | 'wait' (phụ thuộc còn trong lượt chạy này) | thông báo lỗi."""
    s = state()
    for d in t["depends"]:
        st = s["tasks"].get(d, {})
        need = ("merged",) if c["git"] and t["kind"] == "code" and st.get("kind", "code") == "code" else ("passed", "merged")
        if st.get("status") in need:
            continue
        if d in batch_ids:
            return "wait"
        return f"{t['id']} phụ thuộc {d} đang '{st.get('status', 'todo')}' (cần {' / '.join(need)})"
    return "ok"


def prepare(tid, fix=False, dry=False, isolate=False, manual=False):
    c, s = cfg(), state()
    t = parse_task(tid)
    ts = s["tasks"].get(tid, {"attempts": 0, "runs": []})
    dep = deps_state(t, c)
    if dep != "ok":
        raise SystemExit(dep if dep != "wait" else f"{tid}: phụ thuộc chưa xong")
    if fix and not manual and ts["attempts"] > c["max_fix"]:  # làm tay = lối thoát khi sửa tự động hết lượt
        raise SystemExit(f"{tid} đã sửa {ts['attempts'] - 1} lần (tối đa {c['max_fix']}): báo người dùng")
    attempt = ts["attempts"] + 1
    main = os.path.abspath(".")
    use_git = c["git"] and t["kind"] == "code"
    branch, cwd, isolated = None, main, False
    old_wt = ts.get("worktree") if ts.get("worktree") and os.path.isdir(ts.get("worktree", "")) else None
    if use_git:
        integ = c["integration_branch"]
        if not integ or not git("branch", "--list", integ):
            raise SystemExit("Chưa có nhánh tích hợp. Chạy: orch.py branch")
        branch = f"{integ}-{tid}"  # git không cho nhánh con của nhánh đang có (game/x và game/x/T01)
        if (isolate or old_wt) and not is_true(t.get("unity", "")):
            isolated = True
            cwd = wt_path(c, tid) if dry else make_worktree(c, tid, branch, integ)
        else:
            dirty = changed_files(tracked_only=True)
            if dirty:
                raise SystemExit("Working tree có file đã track bị sửa (commit / stash trước):\n  " + "\n  ".join(dirty[:20]))
            junk = changed_files()
            if junk:
                print(f"Cảnh báo: {len(junk)} file chưa track (không tính cho task, nên thêm vào .gitignore): {junk[:5]}")
            if not dry:
                git("checkout", branch) if git("branch", "--list", branch) else git("checkout", "-b", branch, integ)

    run_dir = f"{G}/runs/{tid}/{stamp()}-a{attempt}"
    fix_log = None
    if fix and ts.get("runs"):
        last = ts["runs"][-1]
        fix_log = (rd(f"{last}/test.log") or "") + "\n" + (rd(f"{last}/REPORT.md") or "")
    prompt = build_prompt(t, c, branch, fix_log, attempt, repo=cwd, isolated=isolated)
    wr(f"{run_dir}/prompt.md", prompt)

    tools = c["research_tools"] if t["kind"] == "research" else c["review_tools"] if t["kind"] == "review" else c["allowed_tools"]
    model = t.get("model") or c["model"]
    if fix and ts.get("model") and ts["model"] != "manual":
        up = (c.get("fix_model_up") or {}).get(ts["model"])
        model = up or ts["model"]
        if up:
            history("model_up", f"{tid}: lần sửa lên {up} (lần trước {ts['model']} chưa đạt)", task=tid)
    resume = fix and ts.get("session_id")
    sid = ts["session_id"] if resume else str(uuid.uuid4())
    cmd = [claude_exe(c), "-p", "--output-format", "stream-json", "--verbose",
           "--permission-mode", "acceptEdits", "--allowedTools", " ".join(tools),
           "--append-system-prompt", WORKER_RULES, "--json-schema", json.dumps(REPORT_SCHEMA, ensure_ascii=False),
           "--max-budget-usd", str(t.get("budget") or c["budget_usd"]), "-n", f"game-{tid}-a{attempt}"]
    cmd += ["--resume", sid] if resume else ["--session-id", sid]
    if isolated:
        cmd += ["--add-dir", os.path.abspath(G)]  # .game/ (gitignore) chỉ có ở repo chính
    if model:
        cmd += ["--model", model]
    if t.get("effort") or c["effort"]:
        cmd += ["--effort", t.get("effort") or c["effort"]]
    shown = ["<WORKER_RULES>" if x == WORKER_RULES else "<REPORT_SCHEMA>" if x.startswith('{"type"') else x for x in cmd]
    wr(f"{run_dir}/command.txt", f"cwd: {cwd}\n" + " ".join(f'"{x}"' if " " in x else x for x in shown) + "\n(prompt qua stdin: prompt.md)\n")

    weight = task_weight(t, c)
    if manual:
        model = "manual"
    history("task_dry_run" if dry else "manual_open" if manual else "task_start", f"{tid} {t['title']}", task=tid, attempt=attempt, kind=t["kind"],
            branch=branch, cwd=cwd if isolated else None, weight=weight, model=model, session_id=sid, run_dir=run_dir)
    if dry:
        print(f"[dry-run] {tid} (nặng {weight}{', worktree ' + cwd if isolated else ''}): {' '.join(cmd[:6])} ... → {run_dir}")
        return None
    return {"t": t, "c": c, "tid": tid, "attempt": attempt, "use_git": use_git, "branch": branch, "cwd": cwd,
            "isolated": isolated, "run_dir": run_dir, "prompt": prompt, "cmd": cmd, "sid": sid, "weight": weight, "model": model}


def execute(ctx):
    """Gọi claude CLI + commit. Chạy được song song (mỗi task 1 thư mục làm việc)."""
    c, t, cwd, run_dir = ctx["c"], ctx["t"], ctx["cwd"], ctx["run_dir"]
    before = set(changed_files(cwd=cwd)) if c["git"] else set()  # file bẩn từ trước không tính cho task này
    started = dt.datetime.now()
    result_line, err = None, ""
    with open(f"{run_dir}/transcript.jsonl", "w", encoding="utf-8") as tf:
        try:
            p = subprocess.Popen(ctx["cmd"], cwd=cwd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
            threading.Thread(target=lambda: (p.stdin.write(ctx["prompt"]), p.stdin.close()), daemon=True).start()
            errbuf = []
            threading.Thread(target=lambda: errbuf.append(p.stderr.read()), daemon=True).start()
            for line in p.stdout:
                tf.write(line)
                if '"type":"result"' in line:  # thứ tự key không cố định → parse để chắc
                    try:
                        if json.loads(line).get("type") == "result":
                            result_line = line
                    except ValueError:
                        pass
            p.wait(timeout=c["timeout_s"])
            err = "".join(errbuf)
        except subprocess.TimeoutExpired:
            p.kill()
            err = f"Quá thời gian {c['timeout_s']} s"
        except FileNotFoundError:
            err = f"Không chạy được claude: {ctx['cmd'][0]}"
    if err.strip():
        wr(f"{run_dir}/stderr.txt", err)
    res = json.loads(result_line) if result_line else {}
    wr(f"{run_dir}/result.json", res)
    junk = c.get("commit_ignore") or []
    files = [f for f in changed_files(cwd=cwd) if f not in before
             and not any(fnmatch.fnmatch(f, g) or fnmatch.fnmatch(os.path.basename(f), g) for g in junk)] if c["git"] else []
    if c["git"]:
        wr(f"{run_dir}/diff.txt", sh(["git", "diff", "--stat"], cwd=cwd).stdout + "\n" + sh(["git", "diff"], cwd=cwd).stdout[:200000])
    commit = None
    if ctx["use_git"] and files:
        with LOCK:  # commit nhiều worktree cùng lúc: tránh tranh khoá ref
            git("add", "--", *files, cwd=cwd)
            git("commit", "-q", "-m", f"[game] {ctx['tid']}: {t['title']} (lần {ctx['attempt']})\n\nRun: {run_dir}\nSession: {ctx['sid']}", cwd=cwd)
            commit = git("rev-parse", "--short", "HEAD", cwd=cwd)
    ctx.update(res=res, err=err, files=files, commit=commit,
               duration_s=int((dt.datetime.now() - started).total_seconds()))
    return ctx


def finalize(ctx):
    """Test đơn luồng (gọi tuần tự từ luồng chính) + báo cáo + lịch sử."""
    c, t, res, run_dir = ctx["c"], ctx["t"], ctx["res"], ctx["run_dir"]
    worker = res.get("structured_output") or {}
    oos = [f for f in ctx["files"] if not in_scope(f, t)]
    tests = run_tests(t.get("test", []) + (c["tests"] if t["kind"] == "code" else []), f"{run_dir}/test.log", cwd=ctx["cwd"])
    ok = (worker.get("result") == "done" and not res.get("is_error") and all(x["exit"] == 0 for x in tests)
          and not oos and (not t["output"] or os.path.exists(t["output"])))
    status = "passed" if ok else "failed"
    info = {"attempt": ctx["attempt"], "status": status, "branch": ctx["branch"], "commit": ctx["commit"],
            "run_dir": run_dir, "cwd": ctx["cwd"], "isolated": ctx["isolated"], "weight": ctx["weight"],
            "session_id": res.get("session_id", ctx["sid"]), "files": ctx["files"], "out_of_scope": oos, "worker": worker,
            "tests": tests, "cost": res.get("total_cost_usd", 0), "turns": res.get("num_turns", 0),
            "duration_s": ctx["duration_s"], "ended": now(),
            "denials": [f"{d.get('tool_name')}: {json.dumps(d.get('tool_input', {}), ensure_ascii=False)[:200]}"
                        for d in res.get("permission_denials", [])],
            "error": ctx["err"].strip()[:500] if not res else ""}
    report = render_report(t, info)
    wr(f"{run_dir}/REPORT.md", report)
    if ctx["use_git"] and not ctx["isolated"]:
        git("checkout", c["integration_branch"])
    tid = ctx["tid"]
    with LOCK:
        s = state()
        ts = s["tasks"].setdefault(tid, {"status": "todo", "attempts": 0, "runs": []})
        ts.update({"status": status, "attempts": ctx["attempt"], "session_id": info["session_id"], "branch": ctx["branch"],
                   "commit": ctx["commit"], "title": t["title"], "kind": t["kind"], "weight": ctx["weight"],
                   "model": ctx.get("model"), "worktree": ctx["cwd"] if ctx["isolated"] else None,
                   "cost": round(ts.get("cost", 0) + info["cost"], 4)})
        ts["runs"].append(run_dir)
        save_state(s)
    history("task_end", f"{tid} → {status}", task=tid, attempt=ctx["attempt"], result=worker.get("result"),
            branch=ctx["branch"], commit=ctx["commit"], files=len(ctx["files"]), out_of_scope=oos,
            tests=[f"{x['exit']}" for x in tests], cost=round(info["cost"], 4), report=f"{run_dir}/REPORT.md")
    print(report)
    return status


def is_manual(t):
    return t.get("mode", "").lower() == "manual"


def skip_manual(tid):
    print(f"Bỏ {tid}: mode manual (làm tay: orch.py open {tid}, xong: orch.py done {tid})")
    with LOCK:
        s = state()
        ts = s["tasks"].setdefault(tid, {"status": "todo", "attempts": 0, "runs": []})
        if ts.get("status") in (None, "todo"):
            ts["status"] = "manual"
            save_state(s)
    return "manual"


def run_one(tid, fix=False, dry=False):
    if is_manual(parse_task(tid)):
        return skip_manual(tid)
    ctx = prepare(tid, fix, dry)
    return finalize(execute(ctx)) if ctx else None


def merge_one(tid):
    c, s = cfg(), state()
    integ = c["integration_branch"]
    ts = s["tasks"].get(tid, {})
    if ts.get("status") != "passed" or not ts.get("branch"):
        print(f"Bỏ qua {tid}: trạng thái {ts.get('status')}")
        return ts.get("status")
    if git("rev-parse", "--abbrev-ref", "HEAD") != integ:
        git("checkout", integ)
    if not git("rev-list", f"{integ}..{ts['branch']}", check=False):
        ts["status"] = "merged"
        history("merge", f"{tid}: không có thay đổi", task=tid)
    else:
        r = sh(["git", "merge", "--no-ff", ts["branch"], "-m", f"[game] gộp {tid}: {ts.get('title', '')}"])
        if r.returncode:
            sh(["git", "merge", "--abort"])
            history("merge_conflict", f"{tid} xung đột, đã huỷ merge", task=tid, detail=r.stdout[-500:])
            print(f"XUNG ĐỘT {tid}:\n{r.stdout}")
            ts["status"] = "conflict"
        else:
            ts["status"] = "merged"
            ts["merge_commit"] = git("rev-parse", "--short", "HEAD")
            history("merge", f"Gộp {tid} vào {integ}", task=tid, commit=ts["merge_commit"])
            print(f"Đã gộp {tid} ({ts['merge_commit']})")
    if ts["status"] == "merged" and ts.get("worktree"):
        drop_worktree(c, ts["worktree"], tid)
        ts["worktree"] = None
    with LOCK:
        s2 = state()
        s2["tasks"][tid] = ts
        save_state(s2)
    return ts["status"]


def run_parallel(tids, a):
    """Lập lịch theo độ nặng: chạy cùng lúc tới khi chạm max_parallel phiên hoặc max_load tổng độ nặng.
    claude chạy song song; test + báo cáo tuần tự từng task khi task đó xong."""
    c = cfg()
    cap_n = a.parallel if a.parallel and a.parallel > 0 else int(c["max_parallel"])
    cap_load = int(c["max_load"])
    tasks = {tid: parse_task(tid) for tid in tids}
    weights = {tid: task_weight(t, c) for tid, t in tasks.items()}
    print(f"Lập lịch: tối đa {cap_n} phiên, tổng độ nặng ≤ {cap_load}. Độ nặng: "
          + ", ".join(f"{k}={v}" for k, v in weights.items()))
    history("schedule", f"{len(tids)} task, tối đa {cap_n} phiên / tải {cap_load}", weights=weights)
    pending, running, results = list(tids), {}, {}
    with ThreadPoolExecutor(max_workers=cap_n) as ex:
        while pending or running:
            for tid in list(pending):
                if len(running) >= cap_n:
                    break
                t, w = tasks[tid], weights[tid]
                if is_manual(t):
                    results[tid] = skip_manual(tid)
                    pending.remove(tid)
                    continue
                load = sum(r[2] for r in running.values())
                if running and load + w > cap_load:
                    continue
                if any(overlap(t, r[0]) for r in running.values()):
                    continue
                dep = deps_state(t, c, batch_ids=set(pending) | {r[0]["id"] for r in running.values()})
                if dep == "wait":
                    continue
                if dep != "ok":
                    print(f"Bỏ {tid}: {dep}")
                    results[tid] = "blocked"
                    pending.remove(tid)
                    continue
                isolate = t["kind"] == "code" and not is_true(t.get("unity", ""))
                if t["kind"] == "code" and not isolate and running:
                    continue  # task chạy ở repo chính (Unity) phải đứng một mình
                ctx = prepare(tid, a.fix, a.dry_run, isolate=isolate)
                pending.remove(tid)
                print(f"▶ {tid} bắt đầu (nặng {w}, tải {load + w}/{cap_load}, {len(running) + 1}/{cap_n} phiên)")
                if ctx is None:
                    results[tid] = "dry-run"
                    continue
                running[ex.submit(execute, ctx)] = (t, ctx, w)
            if not running:
                for tid in pending:
                    print(f"Không chạy được {tid}: phụ thuộc chưa gộp (thêm --merge để tự gộp task đạt)")
                    results[tid] = "blocked"
                break
            done, _ = wait(list(running), return_when=FIRST_COMPLETED)
            for f in done:
                t, ctx, w = running.pop(f)
                f.result()
                st = finalize(ctx)  # luồng chính → test đơn luồng
                results[t["id"]] = st
                if a.merge and st == "passed":
                    results[t["id"]] = merge_one(t["id"])
    return results


# ---------------------------------------------------------------- lệnh

def cmd_init(a):
    os.makedirs(f"{G}/tasks", exist_ok=True)
    os.makedirs(f"{G}/research", exist_ok=True)
    c = cfg()
    c["slug"] = a.slug or c["slug"] or re.sub(r"[^a-z0-9]+", "-", os.path.basename(os.getcwd()).lower()).strip("-")
    has_git = os.path.isdir(".git") and not a.no_git
    c["git"] = has_git
    if has_git:
        c["base_branch"] = c["base_branch"] or git("rev-parse", "--abbrev-ref", "HEAD")
        c["integration_branch"] = c["integration_branch"] or f"game/{c['slug']}"
        ign = rd(".gitignore", "") or ""
        if not re.search(r"^/?\.game/?\s*$", ign, re.M):
            with open(".gitignore", "a", encoding="utf-8") as f:
                f.write(("\n" if ign and not ign.endswith("\n") else "") + "# lịch sử pipeline (không đổi theo nhánh)\n.game/\n")
    if not c["tests"] and glob.glob("Assembly-CSharp-Editor.csproj"):
        c["tests"] = [f'python "{SKILL_DIR}/scripts/check_build.py" Assembly-CSharp-Editor.csproj']
    wr(f"{G}/config.json", c)
    if not os.path.exists(f"{G}/intake.md"):
        wr(f"{G}/intake.md", INTAKE)
    if not os.path.exists(f"{G}/HISTORY.md"):
        wr(f"{G}/HISTORY.md", f"# Lịch sử pipeline — {c['slug']}\n\n")
    if not os.path.exists(f"{G}/state.json"):
        save_state({"phase": "intake", "tasks": {}})
    # task nghiên cứu R1 / R2 dựng sẵn từ mẫu (điền đường dẫn plugin)
    plugin = SKILL_DIR.replace("\\", "/")
    for src in glob.glob(os.path.join(SKILL_DIR, "templates", "tasks", "R*.md")):
        dst = f"{G}/tasks/{os.path.basename(src)}"
        if not os.path.exists(dst):
            wr(dst, (rd(src, "") or "").replace("<PLUGIN>", plugin))
    guard = None
    if not a.no_guard and not os.path.exists(".claude/guard.json"):
        guard = ".claude/guard.json"
        wr(guard, rd(os.path.join(SKILL_DIR, "templates", "guard.json")) or {"enabled": True})
    history("init", f"Khởi tạo .game/ ({'git' if has_git else 'không git'})", base=c["base_branch"],
            integration=c["integration_branch"], guard=guard)
    print(f"Đã tạo {G}/. Điền {G}/intake.md. Cấu hình: {G}/config.json"
          + (f". Bật guard: {guard}" if guard else ""))


def cmd_phase(a):
    need_init()
    s = state()
    old, s["phase"] = s.get("phase"), a.name
    save_state(s)
    history("phase", f"{old} → {a.name}")
    print(f"Giai đoạn: {a.name}")


def cmd_log(a):
    need_init()
    history(a.code, a.message, task=a.task)
    print("Đã ghi.")


def cmd_branch(a):
    need_init()
    c = cfg()
    if not c["git"]:
        raise SystemExit("Dự án không dùng git")
    integ = c["integration_branch"]
    if git("branch", "--list", integ):
        print(f"Nhánh {integ} đã có")
    else:
        git("branch", integ, c["base_branch"] or "HEAD")
        history("branch", f"Tạo nhánh tích hợp {integ} từ {c['base_branch']}", commit=git("rev-parse", "--short", integ))
    if git("rev-parse", "--abbrev-ref", "HEAD") != integ:
        if changed_files(tracked_only=True):
            raise SystemExit(f"Working tree có file đã track bị sửa, không checkout được {integ}")
        git("checkout", integ)
    print(f"Đang ở {integ}")


def cmd_run(a):
    need_init()
    if a.parallel is not None:
        res = run_parallel(a.tasks, a)
    else:
        res = {}
        for tid in a.tasks:
            st = run_one(tid, a.fix, a.dry_run)
            res[tid] = merge_one(tid) if a.merge and st == "passed" else st
    print("Tóm tắt:", ", ".join(f"{t}={r}" for t, r in res.items()))


def cmd_merge(a):
    need_init()
    for tid in a.tasks:
        merge_one(tid)


def cmd_test(a):
    need_init()
    c = cfg()
    cmds = c["tests"] + (a.cmd or [])
    d = f"{G}/runs/_integration/{stamp()}"
    res = run_tests(cmds, f"{d}/test.log")
    ok = all(x["exit"] == 0 for x in res)
    branch = git("rev-parse", "--abbrev-ref", "HEAD", check=False) if c["git"] else None
    history("integration_test", "đạt" if ok else "LỖI", branch=branch,
            tests=[f"{x['cmd']} → {x['exit']}" for x in res], log=f"{d}/test.log")
    for x in res:
        print(f"{'ĐẠT' if x['exit'] == 0 else 'LỖI'}  {x['cmd']}")
    print(f"Log: {d}/test.log")
    sys.exit(0 if ok else 1)


def cmd_status(a):
    need_init()
    s = state()
    print(f"Giai đoạn: {s.get('phase')}")
    print(f"{'Task':<6} {'Loại':<9} {'Trạng thái':<10} {'Lần':<4} {'Nặng':<5} {'Chi phí':<9} Nhánh / báo cáo")
    for tid in sorted(set(s["tasks"]) | {os.path.basename(f).split("-")[0].split(".")[0] for f in glob.glob(f"{G}/tasks/*.md")}):
        ts = s["tasks"].get(tid, {})
        last = ts.get("runs", [""])[-1] if ts.get("runs") else ""
        print(f"{tid:<6} {ts.get('kind', '-'):<9} {ts.get('status', 'todo'):<10} {ts.get('attempts', 0):<4} {ts.get('weight', '-')!s:<5} "
              f"${ts.get('cost', 0):<8} {ts.get('branch') or '-'}  {last + '/REPORT.md' if last else ''}")


def cmd_report(a):
    need_init()
    c, s = cfg(), state()
    hist = [json.loads(l) for l in (rd(f"{G}/history.jsonl", "") or "").splitlines() if l.strip()]
    total = sum(t.get("cost", 0) for t in s["tasks"].values())
    L = [f"# Báo cáo pipeline — {c['slug']}", "", f"- Thời điểm: {now()} · giai đoạn: {s.get('phase')}",
         f"- Repo: `{os.getcwd()}`" + (f" · nhánh tích hợp `{c['integration_branch']}` (từ `{c['base_branch']}`)" if c["git"] else ""),
         f"- Tổng chi phí claude CLI: ${total:.4f}", "", "## Task", "",
         "| Task | Tiêu đề | Loại | Trạng thái | Lần | Commit | Báo cáo |", "|---|---|---|---|---|---|---|"]
    for tid, ts in sorted(s["tasks"].items()):
        last = ts["runs"][-1] if ts.get("runs") else ""
        L.append(f"| {tid} | {ts.get('title', '')} | {ts.get('kind', '')} | {ts.get('status')} | {ts.get('attempts', 0)} | "
                 f"{ts.get('merge_commit') or ts.get('commit') or '-'} | {last}/REPORT.md |")
    tests = [h for h in hist if h["event"] == "integration_test"]
    L += ["", "## Test tích hợp"] + ([f"- `{h['ts']}` {h['msg']} — {h.get('log')}" for h in tests[-5:]] or ["- (chưa chạy)"])
    gates = [h for h in hist if h["event"].upper().startswith("G")]
    L += ["", "## Cổng duyệt / quyết định"] + ([f"- `{h['ts']}` {h['event']}: {h['msg']}" for h in gates] or ["- (chưa có)"])
    bad = [tid for tid, ts in s["tasks"].items() if ts.get("status") not in ("merged", "passed")]
    L += ["", "## Còn tồn"] + ([f"- {tid}: {s['tasks'][tid].get('status')}" for tid in bad] or ["- Không"])
    L += ["", f"Lịch sử đầy đủ: `{G}/HISTORY.md`, `{G}/history.jsonl`. Transcript từng lần chạy: `{G}/runs/<task>/<lần>/transcript.jsonl`."]
    wr(f"{G}/REPORT.md", "\n".join(L) + "\n")
    history("report", f"Sinh {G}/REPORT.md", cost=round(total, 4))
    print("\n".join(L))


def cmd_history(a):
    need_init()
    hist = [json.loads(l) for l in (rd(f"{G}/history.jsonl", "") or "").splitlines() if l.strip()]
    if a.task:
        hist = [h for h in hist if h.get("task") == a.task or a.task in h.get("msg", "").split()]
    if a.event:
        hist = [h for h in hist if a.event.lower() in h["event"].lower()]
    if a.since:
        hist = [h for h in hist if h["ts"] >= a.since]
    if a.file:
        f = a.file.replace("\\", "/").lstrip("./")
        s = state()
        print(f"# File {f}")
        hits = []
        for tid, ts in sorted(s["tasks"].items()):
            for run in ts.get("runs", []):
                res = rd(f"{run}/result.json") or {}
                if not isinstance(res, dict):
                    continue
                files = [x.get("path", "") for x in (res.get("structured_output") or {}).get("files_changed", [])]
                diff = rd(f"{run}/diff.txt", "") or ""
                if any(x.replace("\\", "/").endswith(f) for x in files) or f in diff:
                    hits.append(f"- {tid} ({ts.get('title', '')}) · {run}/REPORT.md")
        print("\n## Task đã sửa (theo báo cáo / diff)")
        print("\n".join(hits) or "- (không thấy)")
        if cfg()["git"]:
            log = git("log", "--all", "--date=format:%Y-%m-%d %H:%M", "--format=%h %ad %s", "--", f, check=False)
            print("\n## Commit (git log, mọi nhánh)")
            print(log or "- (không có)")
        hist = [h for h in hist if f in json.dumps(h, ensure_ascii=False)]
        if not hist:
            return
        print("\n## Sự kiện nhắc tới file")
    for h in hist[-a.n:]:
        extra = " · ".join(f"{k}={v}" for k, v in h.items() if k not in ("ts", "event", "msg") and v not in (None, "", [], {}))
        print(f"{h['ts']}  {h['event']:<16} {h['msg']}" + (f"  [{extra}]" if extra else ""))


MANUAL_NOTE = """## Chế độ LÀM TAY
- Người dùng đang ngồi cùng: được hỏi lại, được đề xuất, được dùng Unity Editor đang mở nếu người dùng đồng ý.
- Vẫn giữ PHẠM VI và luật repo. KHÔNG git commit / checkout / merge (orchestrator làm).
- Xong việc: tóm tắt đã làm gì, chưa làm gì, rủi ro; nhắc người dùng chạy `/gplay-game:done {tid}` (hoặc `orch.py done {tid} --note "..."`)
  ở phiên orchestrator để commit + test + ghi báo cáo."""


def session_file(sid):
    hits = glob.glob(os.path.join(os.path.expanduser("~"), ".claude", "projects", "*", f"{sid}.jsonl"))
    return hits[0] if hits else None


def cmd_open(a):
    need_init()
    c, s = cfg(), state()
    tid = a.task
    t = parse_task(tid)
    ts = s["tasks"].get(tid, {})
    if ts.get("manual"):
        m = ts["manual"]
        print(f"{tid} đang mở làm tay từ {m['started']}. Thư mục: {m['cwd']}\nLệnh: {m['command']}")
        return
    if ts.get("status") == "merged":
        raise SystemExit(f"{tid} đã gộp. Muốn làm tiếp: tạo task mới.")
    # phiên cũ chạy ở repo chính thì phải mở lại ở repo chính (claude --resume tìm phiên theo thư mục)
    here = a.here or is_true(t.get("unity", "")) or (ts.get("session_id") and not ts.get("worktree"))
    ctx = prepare(tid, fix=bool(ts.get("runs")), isolate=not here, manual=True)
    cwd, sid = ctx["cwd"], ctx["sid"]
    manual_md = os.path.abspath(f"{ctx['run_dir']}/manual.md")
    wr(manual_md, ctx["prompt"] + "\n\n" + MANUAL_NOTE.format(tid=tid) + "\n")
    exe = "claude"
    add = f' --add-dir "{os.path.abspath(G)}"' if ctx["isolated"] else ""
    if ts.get("session_id") and session_file(ts["session_id"]):
        sid = ts["session_id"]
        command = f'claude --resume {sid}{add} "Tiếp task {tid} ở chế độ làm tay: đọc {manual_md}"'
    else:
        command = f'{exe} --session-id {sid}{add} -n game-{tid}-tay "Làm task theo file {manual_md}"'
    before = changed_files(cwd=cwd) if c["git"] else []
    with LOCK:
        s = state()
        ts = s["tasks"].setdefault(tid, {"status": "todo", "attempts": 0, "runs": []})
        ts.update({"status": "manual", "title": t["title"], "kind": t["kind"], "branch": ctx["branch"],
                   "worktree": cwd if ctx["isolated"] else ts.get("worktree"),
                   "manual": {"run_dir": ctx["run_dir"], "cwd": cwd, "branch": ctx["branch"], "isolated": ctx["isolated"],
                              "attempt": ctx["attempt"], "sid": sid, "before": before, "started": now(),
                              "weight": ctx["weight"], "command": command}})
        save_state(s)
    wr(f"{ctx['run_dir']}/command.txt", f"cwd: {cwd}\n{command}\n")
    print(f"Mở {tid} làm tay.\n- Thư mục: {cwd}\n- Nhánh: {ctx['branch'] or '-'}\n- Đề bài: {manual_md}\n"
          f"- Mở terminal mới ở thư mục trên rồi chạy:\n    {command}\n- Xong: orch.py done {tid} --note \"tóm tắt\"")


def cmd_done(a):
    need_init()
    c, s = cfg(), state()
    tid = a.task
    ts = s["tasks"].get(tid, {})
    m = ts.get("manual")
    if not m:
        raise SystemExit(f"{tid} không ở chế độ làm tay (chạy orch.py open {tid} trước)")
    t = parse_task(tid)
    cwd, run_dir = m["cwd"], m["run_dir"]
    use_git = c["git"] and t["kind"] == "code"
    junk = c.get("commit_ignore") or []
    files = [f for f in changed_files(cwd=cwd) if f not in set(m["before"])
             and not any(fnmatch.fnmatch(f, g) or fnmatch.fnmatch(os.path.basename(f), g) for g in junk)] if c["git"] else []
    if c["git"]:
        wr(f"{run_dir}/diff.txt", sh(["git", "diff", "--stat"], cwd=cwd).stdout + "\n" + sh(["git", "diff"], cwd=cwd).stdout[:200000])
    src = session_file(m["sid"])
    if src:
        shutil.copy2(src, f"{run_dir}/transcript.jsonl")  # phiên làm tay: chép transcript để truy vết
    commit = None
    if use_git and files:
        git("add", "--", *files, cwd=cwd)
        git("commit", "-q", "-m", f"[game] {tid}: {t['title']} (làm tay, lần {m['attempt']})\n\nRun: {run_dir}\nSession: {m['sid']}", cwd=cwd)
        commit = git("rev-parse", "--short", "HEAD", cwd=cwd)
    started = dt.datetime.fromisoformat(m["started"])
    worker = {"result": "failed" if a.fail else "done", "summary": a.note or "Làm tay (không ghi chú).",
              "files_changed": [{"path": f, "change": "làm tay"} for f in files], "checks_run": [], "not_done": []}
    history("manual_done", f"{tid}: {worker['summary']}", task=tid, files=len(files), commit=commit,
            transcript=f"{run_dir}/transcript.jsonl" if src else None)
    ctx = {"c": c, "t": t, "tid": tid, "attempt": m["attempt"], "use_git": use_git, "branch": m["branch"], "cwd": cwd,
           "isolated": m["isolated"], "run_dir": run_dir, "sid": m["sid"], "weight": m.get("weight"), "model": "manual",
           "res": {"structured_output": worker, "session_id": m["sid"]}, "err": "", "files": files, "commit": commit,
           "duration_s": int((dt.datetime.now().astimezone() - started).total_seconds())}
    st = finalize(ctx)
    with LOCK:
        s = state()
        s["tasks"][tid].pop("manual", None)
        save_state(s)
    if st == "passed" and a.merge:
        merge_one(tid)


def cmd_config(a):
    need_init()
    c = rd(f"{G}/config.json") or {}
    if not a.key:
        print(json.dumps({**DEFAULT_CONFIG, **c}, ensure_ascii=False, indent=2))
        return
    if a.value is None:
        print(json.dumps({**DEFAULT_CONFIG, **c}.get(a.key), ensure_ascii=False, indent=2))
        return
    if a.key not in DEFAULT_CONFIG:
        raise SystemExit(f"Khoá lạ: {a.key}. Có: {', '.join(DEFAULT_CONFIG)}")
    try:
        v = json.loads(a.value)
    except ValueError:
        v = a.value
    old = c.get(a.key, DEFAULT_CONFIG[a.key])
    c[a.key] = v
    wr(f"{G}/config.json", c)
    history("config", f"{a.key}: {json.dumps(old, ensure_ascii=False)} → {json.dumps(v, ensure_ascii=False)}")
    print(f"{a.key} = {json.dumps(v, ensure_ascii=False)}")


def main():
    ap = argparse.ArgumentParser(description="Điều phối pipeline làm game bằng claude CLI")
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("init"); p.add_argument("--slug"); p.add_argument("--no-git", action="store_true")
    p.add_argument("--no-guard", action="store_true", help="không tạo .claude/guard.json"); p.set_defaults(f=cmd_init)
    p = sp.add_parser("phase"); p.add_argument("name"); p.set_defaults(f=cmd_phase)
    p = sp.add_parser("log"); p.add_argument("code"); p.add_argument("message"); p.add_argument("--task"); p.set_defaults(f=cmd_log)
    p = sp.add_parser("branch"); p.set_defaults(f=cmd_branch)
    p = sp.add_parser("run"); p.add_argument("tasks", nargs="+")
    p.add_argument("--parallel", nargs="?", type=int, const=0, help="chạy song song; số = phiên tối đa (mặc định max_parallel)")
    p.add_argument("--merge", action="store_true", help="tự gộp task đạt (mở khoá task phụ thuộc trong cùng lượt)")
    p.add_argument("--fix", action="store_true"); p.add_argument("--dry-run", action="store_true"); p.set_defaults(f=cmd_run)
    p = sp.add_parser("merge"); p.add_argument("tasks", nargs="+"); p.set_defaults(f=cmd_merge)
    p = sp.add_parser("test"); p.add_argument("--cmd", action="append"); p.set_defaults(f=cmd_test)
    p = sp.add_parser("status"); p.set_defaults(f=cmd_status)
    p = sp.add_parser("report"); p.set_defaults(f=cmd_report)
    p = sp.add_parser("history"); p.add_argument("--task"); p.add_argument("--file"); p.add_argument("--event")
    p.add_argument("--since"); p.add_argument("-n", type=int, default=40); p.set_defaults(f=cmd_history)
    p = sp.add_parser("config"); p.add_argument("key", nargs="?"); p.add_argument("value", nargs="?"); p.set_defaults(f=cmd_config)
    p = sp.add_parser("open"); p.add_argument("task"); p.add_argument("--here", action="store_true",
                                                                       help="làm ở repo chính (cần Unity Editor đang mở)")
    p.set_defaults(f=cmd_open)
    p = sp.add_parser("done"); p.add_argument("task"); p.add_argument("--note", default="")
    p.add_argument("--fail", action="store_true", help="ghi là chưa đạt"); p.add_argument("--merge", action="store_true")
    p.set_defaults(f=cmd_done)
    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
