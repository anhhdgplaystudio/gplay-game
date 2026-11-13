"""Sổ trạng thái + lịch sử của pipeline làm game (.game/). Phiên Claude chính tự làm từng mốc; script này chỉ ghi sổ.

Lệnh (chạy ở gốc repo dự án):
  orch.py init [--slug ten-game] [--no-guard]    tạo .game/ (intake, config, state, lịch sử) + .claude/guard.json
  orch.py phase <tên>                            chuyển giai đoạn: intake | research | plan | slice | build | report | done
  orch.py log <mã> "<nội dung>"                  ghi 1 sự kiện (cổng duyệt G0 G1 G2 GS G3, PLAN, NOTE, LEARN, ART).
                                                 nội dung "-" = đọc stdin (UTF-8); --file f = đọc từ file (giữ dấu tiếng Việt)
  orch.py ms                                     bảng mốc (trạng thái, thời gian, file đổi, ảnh bằng chứng)
  orch.py ms M1 start "<tiêu đề>"                bắt đầu 1 mốc
  orch.py ms M1 done [--note "..."] [--evidence a.png b.png] [--fail]
                                                 chốt mốc: ghi file đã đổi từ lúc start, ảnh bằng chứng, sinh lại REPORT.md
  orch.py status                                 giai đoạn, cổng đã qua, mốc
  orch.py report                                 sinh .game/REPORT.md
  orch.py history [--event E] [--file F] [--since 2026-11-01] [-n 40]
  orch.py config [khoá [giá trị]]                xem / đổi .game/config.json (giá trị dạng JSON hoặc chuỗi)
  orch.py test [--cmd "<lệnh>"]                  chạy lệnh test chung (config tests) + lệnh thêm, ghi log

Lịch sử: .game/history.jsonl (máy) + .game/HISTORY.md (người). File đổi từng mốc: .game/milestones/<mốc>-files.txt.
"""
import argparse
import datetime as dt
import fnmatch
import glob
import json
import os
import re
import subprocess
import sys

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

G = ".game"
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEFAULT_CONFIG = {
    "slug": "",
    "git": True,
    "tests": [],                # lệnh test chung (compile, test logic): orch.py test
    "track_dirs": ["Assets", "Packages", "ProjectSettings", "Tools"],  # không git: quét mtime ở đây để biết file đã đổi
    "ignore": ["*.pyc", "*.meta", ".DS_Store", "Thumbs.db"],
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
- Video gameplay đã tải / frame đã trích (đường dẫn, cho bước research):
- Nhận xét từ tài liệu (cơ chế, vòng chơi, UI, meta thấy được):

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

SKIP_DIRS = {"Library", "Temp", "Logs", "obj", "bin", ".git", ".vs", "node_modules", "__pycache__"}


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


def sh(cmd, **kw):
    return subprocess.run(cmd, shell=isinstance(cmd, str), capture_output=True, text=True,
                          encoding="utf-8", errors="replace", **kw)


def cfg():
    c = dict(DEFAULT_CONFIG)
    c.update(rd(f"{G}/config.json", {}))
    return c


def state():
    return rd(f"{G}/state.json", {"phase": "intake", "milestones": {}})


def save_state(s):
    wr(f"{G}/state.json", s)


def read_history():
    return [json.loads(l) for l in (rd(f"{G}/history.jsonl", "") or "").splitlines() if l.strip()]


def history(event, msg, **fields):
    """Ghi 1 sự kiện vào history.jsonl + HISTORY.md."""
    rec = {"ts": now(), "event": event, "msg": msg, **fields}
    with open(f"{G}/history.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    extra = " · ".join(f"{k}={v}" for k, v in fields.items() if v not in (None, "", [], {}))
    with open(f"{G}/HISTORY.md", "a", encoding="utf-8") as f:
        f.write(f"- `{rec['ts']}` **{event}** {msg}" + (f" — {extra}" if extra else "") + "\n")


def need_init():
    if not os.path.isdir(G):
        raise SystemExit("Chưa có .game/. Chạy: orch.py init")


def changed_files(since, c, limit=500):
    """File đã đổi từ `since` (giây epoch): có git thì hợp của git status + mtime, không git thì theo mtime trong track_dirs."""
    junk = c.get("ignore") or []
    out = set()
    for d in c.get("track_dirs") or []:
        for root, dirs, files in os.walk(d):
            dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
            for f in files:
                if any(fnmatch.fnmatch(f, g) for g in junk):
                    continue
                p = os.path.join(root, f)
                try:
                    if os.path.getmtime(p) >= since:
                        out.add(p.replace("\\", "/"))
                except OSError:
                    pass
                if len(out) >= limit:
                    return sorted(out)
    return sorted(out)


def expand_evidence(patterns):
    """Glob ảnh / file bằng chứng → đường dẫn đầy đủ; trả thêm các mẫu không khớp file nào."""
    out, missing = [], []
    for pat in patterns or []:
        hits = [f for f in sorted(glob.glob(pat, recursive=True)) if os.path.isfile(f)]
        if not hits:
            missing.append(pat)
        out += [os.path.abspath(f).replace("\\", "/") for f in hits]
    return out[:80], missing


def fmt_dur(sec):
    sec = int(sec)
    return f"{sec // 3600}h{sec % 3600 // 60:02d}" if sec >= 3600 else f"{sec // 60}m"


def ms_rows(s):
    rows = []
    for mid, m in sorted((s.get("milestones") or {}).items()):
        end = m.get("ended") or now()
        dur = (dt.datetime.fromisoformat(end) - dt.datetime.fromisoformat(m["started"])).total_seconds() if m.get("started") else 0
        rows.append((mid, m.get("status", "todo"), fmt_dur(dur) if m.get("started") else "-", len(m.get("files") or []),
                     len(m.get("evidence") or []), m.get("title", "")))
    return rows


def gates_passed(hist):
    return sorted({h["event"].upper() for h in hist if re.fullmatch(r"G[0-9S]", h["event"].upper())})


# ---------------------------------------------------------------- lệnh

def cmd_init(a):
    os.makedirs(f"{G}/research", exist_ok=True)
    c = cfg()
    c["slug"] = a.slug or c["slug"] or re.sub(r"[^a-z0-9]+", "-", os.path.basename(os.getcwd()).lower()).strip("-")
    has_git = os.path.isdir(".git")
    c["git"] = has_git
    if has_git:
        ign = rd(".gitignore", "") or ""
        if not re.search(r"^/?\.game/?\s*$", ign, re.M):
            with open(".gitignore", "a", encoding="utf-8") as f:
                f.write(("\n" if ign and not ign.endswith("\n") else "") + "# lịch sử pipeline\n.game/\n")
    if not c["tests"] and glob.glob("Assembly-CSharp-Editor.csproj"):
        c["tests"] = [f'python "{SKILL_DIR}/scripts/check_build.py" Assembly-CSharp-Editor.csproj']
    wr(f"{G}/config.json", c)
    if not os.path.exists(f"{G}/intake.md"):
        wr(f"{G}/intake.md", INTAKE)
    if not os.path.exists(f"{G}/HISTORY.md"):
        wr(f"{G}/HISTORY.md", f"# Lịch sử pipeline — {c['slug']}\n\n")
    if not os.path.exists(f"{G}/state.json"):
        save_state({"phase": "intake", "milestones": {}})
    guard = None
    if not a.no_guard and not os.path.exists(".claude/guard.json"):
        guard = ".claude/guard.json"
        wr(guard, rd(os.path.join(SKILL_DIR, "templates", "guard.json")) or {"enabled": True})
    history("init", f"Khởi tạo .game/ ({'git' if has_git else 'không git'})", guard=guard)
    print(f"Đã tạo {G}/. Điền {G}/intake.md. Cấu hình: {G}/config.json" + (f". Bật guard: {guard}" if guard else ""))
    if c["tests"]:
        print(f"Lệnh test chung: {c['tests'][0]} (dự án dùng asmdef / lệnh compile riêng thì đổi: orch.py config tests '[\"<lệnh>\"]')")
    if not has_git:
        print("Không có git: không hoàn tác được. Nên hỏi người dùng `git init` cục bộ (hoặc sao lưu) trước khi sửa code.")


def cmd_phase(a):
    need_init()
    s = state()
    old, s["phase"] = s.get("phase"), a.name
    save_state(s)
    history("phase", f"{old} → {a.name}")
    print(f"Giai đoạn: {a.name}")


def cmd_log(a):
    need_init()
    msg = a.message
    if a.file:
        msg = (rd(a.file, "") or "").strip()
    elif msg == "-":
        msg = sys.stdin.buffer.read().decode("utf-8", errors="replace").strip()
    if not msg:
        raise SystemExit("Thiếu nội dung (đối số, \"-\" để đọc stdin, hoặc --file)")
    history(a.code, " ".join(msg.split()))
    print("Đã ghi.")


def cmd_ms(a):
    need_init()
    c, s = cfg(), state()
    ms = s.setdefault("milestones", {})
    if not a.id:
        print(f"{'Mốc':<5} {'Trạng thái':<10} {'Thời gian':<10} {'File':<5} {'Ảnh':<4} Tiêu đề")
        for r in ms_rows(s):
            print(f"{r[0]:<5} {r[1]:<10} {r[2]:<10} {r[3]:<5} {r[4]:<4} {r[5]}")
        return
    m = ms.setdefault(a.id, {"status": "todo"})
    if a.action == "start":
        doing = [k for k, v in ms.items() if v.get("status") == "doing" and k != a.id]
        if doing:
            print(f"Cảnh báo: mốc {', '.join(doing)} còn đang 'doing'")
        m.update({"status": "doing", "started": now(), "ended": None, "title": a.title or m.get("title") or a.id})
        save_state(s)
        history("ms_start", f"{a.id} {m['title']}", milestone=a.id)
        print(f"Bắt đầu {a.id}: {m['title']}")
    elif a.action == "done":
        if not m.get("started"):
            raise SystemExit(f"{a.id} chưa start")
        files = changed_files(dt.datetime.fromisoformat(m["started"]).timestamp(), c)
        ev, missing = expand_evidence(a.evidence)
        if missing:
            print("Cảnh báo: không thấy bằng chứng: " + ", ".join(missing))
        old = m.get("evidence") or []
        m.update({"status": "failed" if a.fail else "done", "ended": now(), "note": a.note or m.get("note", ""),
                  "files": files, "evidence": old + [p for p in ev if p not in old]})
        save_state(s)
        wr(f"{G}/milestones/{a.id}-files.txt", "\n".join(files) + "\n")
        history("ms_done", f"{a.id} → {m['status']}: {m['note']}", milestone=a.id, files=len(files), evidence=m["evidence"][:12])
        write_report(quiet=True)
        print(f"{a.id} → {m['status']} · {len(files)} file đổi ({G}/milestones/{a.id}-files.txt) · {len(m['evidence'])} ảnh bằng chứng")
        for p in m["evidence"]:
            print(f"  {p}")
    else:
        raise SystemExit("Dùng: orch.py ms <id> start \"<tiêu đề>\" | orch.py ms <id> done [--note] [--evidence ...] [--fail]")


def cmd_test(a):
    need_init()
    cmds = cfg()["tests"] + (a.cmd or [])
    log = f"{G}/tests/{stamp()}.log"
    env = {**os.environ, "PYTHONUTF8": "1"}  # Windows: python mặc định đọc file cp1252, test có tiếng Việt sẽ lỗi
    res, out = [], []
    for cmd in cmds:
        r = sh(cmd, env=env)
        res.append((cmd, r.returncode))
        out.append(f"$ {cmd}\n(exit {r.returncode})\n{r.stdout[-8000:]}\n{r.stderr[-4000:]}\n")
    wr(log, "\n".join(out) or "(không có lệnh)\n")
    ok = all(code == 0 for _, code in res)
    history("test", "đạt" if ok else "LỖI", tests=[f"{c} → {code}" for c, code in res], log=log)
    for cmd, code in res:
        print(f"{'ĐẠT' if code == 0 else 'LỖI'}  {cmd}")
    print(f"Log: {log}")
    sys.exit(0 if ok else 1)


def cmd_status(a):
    need_init()
    s = state()
    print(f"Giai đoạn: {s.get('phase')} · cổng đã qua: {' '.join(gates_passed(read_history())) or '(chưa)'}")
    rows = ms_rows(s)
    if rows:
        print(f"\n{'Mốc':<5} {'Trạng thái':<10} {'Thời gian':<10} {'File':<5} {'Ảnh':<4} Tiêu đề")
        for r in rows:
            print(f"{r[0]:<5} {r[1]:<10} {r[2]:<10} {r[3]:<5} {r[4]:<4} {r[5]}")
        last = [m for _, m in sorted((s.get("milestones") or {}).items()) if m.get("evidence")]
        if last:
            print("\nẢnh bằng chứng mốc gần nhất:")
            for p in last[-1]["evidence"][:8]:
                print(f"  {p}")
    else:
        print("(chưa có mốc)")
    if s.get("tasks"):
        print(f"\nDự án có {len(s['tasks'])} task kiểu cũ (worker CLI, đã bỏ): xem {G}/runs/ và {G}/HISTORY.md.")


def write_report(quiet=False):
    c, s = cfg(), state()
    hist = read_history()
    ms = s.get("milestones") or {}
    L = [f"# Báo cáo pipeline — {c['slug']}", "", f"- Thời điểm: {now()} · giai đoạn: {s.get('phase')}"
         f" · cổng đã qua: {' '.join(gates_passed(hist)) or '(chưa)'}", f"- Repo: `{os.getcwd()}`"]
    if ms:
        L += ["", "## Mốc", "", "| Mốc | Tiêu đề | Trạng thái | Thời gian | File đổi | Ghi chú |", "|---|---|---|---|---|---|"]
        for (mid, st, dur, nfiles, _nev, title) in ms_rows(s):
            L.append(f"| {mid} | {title} | {st} | {dur} | {nfiles} | {ms[mid].get('note', '')} |")
        for mid, m in sorted(ms.items()):
            if m.get("evidence"):
                L += ["", f"Ảnh bằng chứng {mid}:"] + [f"- `{p}`" for p in m["evidence"]]
    tests = [h for h in hist if h["event"] in ("test", "integration_test")]
    L += ["", "## Test chung"] + ([f"- `{h['ts']}` {h['msg']} — {h.get('log')}" for h in tests[-5:]] or ["- (chưa chạy)"])
    gates = [h for h in hist if re.fullmatch(r"G[0-9S]|PLAN", h["event"].upper())]
    L += ["", "## Cổng duyệt / quyết định"] + ([f"- `{h['ts']}` {h['event']}: {h['msg']}" for h in gates] or ["- (chưa có)"])
    notes = [h for h in hist if h["event"].upper() in ("NOTE", "LEARN", "RULE", "ART")]
    if notes:
        L += ["", "## Góp ý của người dùng / bài học / art"] + [f"- `{h['ts']}` {h['event']}: {h['msg']}" for h in notes[-40:]]
    bad = [f"- {mid}: {m.get('status')}" for mid, m in sorted(ms.items()) if m.get("status") != "done"]
    L += ["", "## Còn tồn"] + (bad or ["- Không"])
    L += ["", f"Lịch sử đầy đủ: `{G}/HISTORY.md`, `{G}/history.jsonl`. File đổi từng mốc: `{G}/milestones/<mốc>-files.txt`."]
    wr(f"{G}/REPORT.md", "\n".join(L) + "\n")
    if not quiet:
        history("report", f"Sinh {G}/REPORT.md")
        print("\n".join(L))


def cmd_report(a):
    need_init()
    write_report()


def cmd_history(a):
    need_init()
    hist = read_history()
    if a.event:
        hist = [h for h in hist if a.event.lower() in h["event"].lower()]
    if a.since:
        hist = [h for h in hist if h["ts"] >= a.since]
    if a.file:
        f = a.file.replace("\\", "/").lstrip("./")
        print(f"# File {f}\n\n## Mốc đã sửa")
        hits = [os.path.basename(p).replace("-files.txt", "") for p in sorted(glob.glob(f"{G}/milestones/*-files.txt"))
                if any(line.strip().endswith(f) for line in (rd(p, "") or "").splitlines())]
        print("\n".join(f"- {m}" for m in hits) or "- (không thấy)")
        if cfg()["git"]:
            log = sh(["git", "log", "--date=format:%Y-%m-%d %H:%M", "--format=%h %ad %s", "--", f]).stdout.strip()
            print("\n## Commit (git log)\n" + (log or "- (không có)"))
        hist = [h for h in hist if f in json.dumps(h, ensure_ascii=False)]
        if not hist:
            return
        print("\n## Sự kiện nhắc tới file")
    for h in hist[-a.n:]:
        extra = " · ".join(f"{k}={v}" for k, v in h.items() if k not in ("ts", "event", "msg") and v not in (None, "", [], {}))
        print(f"{h['ts']}  {h['event']:<12} {h['msg']}" + (f"  [{extra}]" if extra else ""))


def cmd_config(a):
    need_init()
    c = rd(f"{G}/config.json") or {}
    merged = {**DEFAULT_CONFIG, **c}
    if not a.key:
        print(json.dumps(merged, ensure_ascii=False, indent=2))
        return
    if a.value is None:
        print(json.dumps(merged.get(a.key), ensure_ascii=False, indent=2))
        return
    if a.key not in DEFAULT_CONFIG:
        raise SystemExit(f"Khoá lạ: {a.key}. Có: {', '.join(DEFAULT_CONFIG)}")
    try:
        v = json.loads(a.value)
    except ValueError:
        v = a.value
    old = merged[a.key]
    c[a.key] = v
    wr(f"{G}/config.json", c)
    history("config", f"{a.key}: {json.dumps(old, ensure_ascii=False)} → {json.dumps(v, ensure_ascii=False)}")
    print(f"{a.key} = {json.dumps(v, ensure_ascii=False)}")


def main():
    ap = argparse.ArgumentParser(description="Sổ trạng thái + lịch sử pipeline làm game (.game/)")
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("init"); p.add_argument("--slug")
    p.add_argument("--no-guard", action="store_true", help="không tạo .claude/guard.json"); p.set_defaults(f=cmd_init)
    p = sp.add_parser("phase"); p.add_argument("name"); p.set_defaults(f=cmd_phase)
    p = sp.add_parser("log"); p.add_argument("code"); p.add_argument("message", nargs="?", default="")
    p.add_argument("--file", help="đọc nội dung từ file UTF-8"); p.set_defaults(f=cmd_log)
    p = sp.add_parser("ms"); p.add_argument("id", nargs="?"); p.add_argument("action", nargs="?", choices=["start", "done"])
    p.add_argument("title", nargs="?"); p.add_argument("--note", default=""); p.add_argument("--evidence", nargs="*")
    p.add_argument("--fail", action="store_true"); p.set_defaults(f=cmd_ms)
    p = sp.add_parser("test"); p.add_argument("--cmd", action="append"); p.set_defaults(f=cmd_test)
    p = sp.add_parser("status"); p.set_defaults(f=cmd_status)
    p = sp.add_parser("report"); p.set_defaults(f=cmd_report)
    p = sp.add_parser("history"); p.add_argument("--file"); p.add_argument("--event")
    p.add_argument("--since"); p.add_argument("-n", type=int, default=40); p.set_defaults(f=cmd_history)
    p = sp.add_parser("config"); p.add_argument("key", nargs="?"); p.add_argument("value", nargs="?"); p.set_defaults(f=cmd_config)
    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
