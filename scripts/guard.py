"""Hook PreToolUse của plugin gplay-game: chặn sửa tay YAML Unity, sửa/ghi đè .meta, đọc file bí mật, lệnh nguy hiểm.

Chỉ chạy ở dự án BẬT guard: có `.claude/guard.json` với "enabled": true (lệnh /gplay-game:start tạo sẵn).
Dự án khác: cho qua hết (exit 0).

guard.json (dự án) và <plugin>/guard.json (luật chung mọi game) được gộp:
{
  "enabled": true,
  "yaml": true,                                   # chặn sửa tay YAML Unity (false = cho phép)
  "secrets": ["ApiKey.txt"],                      # chuỗi con trong đường dẫn / lệnh = file bí mật
  "no_edit": ["Assets/Plugins/**"],               # glob (tính từ gốc dự án) cấm Edit / Write
  "no_cmd": [{"pattern": "regex", "why": "lý do"}] # lệnh Bash / PowerShell bị cấm
}
Biến môi trường GUARD_SECRETS (phân cách ';') vẫn được nhận. Exit 2 + stderr = chặn (Claude thấy lý do).
"""
import fnmatch
import json
import os
import re
import sys

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

PLUGIN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

YAML_EXT = (".unity", ".prefab", ".asset", ".mat", ".controller", ".anim",
            ".overridecontroller", ".physicsmaterial2d", ".mask", ".playable")

SECRETS = ["google-services.json", "googleservice-info.plist", ".keystore", ".jks",
           "keystore.properties", ".p12", ".mobileprovision"]

DANGER_CMD = [
    (r"rm\s+-rf?\s+[\"']?\.?/?Assets\b", "xoá thư mục Assets"),
    (r"Remove-Item[^\n]*\bAssets\b[^\n]*-Recurse", "xoá thư mục Assets"),
    (r"git\s+push\s+[^\n]*(--force|-f\b)", "git push --force"),
]


def block(msg):
    sys.stderr.write("[guard] " + msg + "\n")
    sys.exit(2)


def norm(p):
    return (p or "").replace("\\", "/").lower()


def load(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def find_project_cfg(cwd):
    d = os.path.abspath(cwd or ".")
    while True:
        p = os.path.join(d, ".claude", "guard.json")
        if os.path.isfile(p):
            return d, load(p)
        parent = os.path.dirname(d)
        if parent == d:
            return None, {}
        d = parent


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)  # không đọc được thì không chặn nhầm
    root, proj = find_project_cfg(data.get("cwd") or os.getcwd())
    if not proj.get("enabled"):
        sys.exit(0)
    glob_cfg = load(os.path.join(PLUGIN_DIR, "guard.json"))

    secrets = SECRETS + [s.strip().lower() for s in os.environ.get("GUARD_SECRETS", "").split(";") if s.strip()]
    secrets += [s.lower() for s in glob_cfg.get("secrets", []) + proj.get("secrets", [])]
    no_edit = glob_cfg.get("no_edit", []) + proj.get("no_edit", [])
    no_cmd = [(x["pattern"], x.get("why", "luật dự án")) for x in glob_cfg.get("no_cmd", []) + proj.get("no_cmd", [])]
    yaml_on = proj.get("yaml", glob_cfg.get("yaml", True))

    def is_secret(text):
        t = norm(text)
        return next((s for s in secrets if s in t), None)

    tool = data.get("tool_name", "")
    inp = data.get("tool_input", {}) or {}

    if tool in ("Edit", "Write", "MultiEdit", "Read", "NotebookEdit"):
        raw = inp.get("file_path") or inp.get("notebook_path") or ""
        path = norm(raw)
        hit = is_secret(path)
        if hit:
            block(f"File bí mật ({hit}): không đọc / sửa. Hỏi người dùng nếu thật sự cần.")
        if tool == "Read":
            sys.exit(0)
        if yaml_on and path.endswith(YAML_EXT):
            block("Không sửa tay YAML Unity (" + os.path.basename(path) +
                  "). Đổi qua importer / editor script / menu / -executeMethod.")
        if path.endswith(".meta") and (tool != "Write" or os.path.exists(raw)):
            block("Không sửa / ghi đè .meta đã có (GUID là danh tính asset).")
        rel = norm(os.path.relpath(os.path.abspath(raw), root)) if raw else ""
        for g in no_edit:
            if fnmatch.fnmatch(rel, norm(g)):
                block(f"Đường dẫn bị khoá theo luật ({g}): {rel}.")
        sys.exit(0)

    if tool in ("Bash", "PowerShell"):
        cmd = inp.get("command", "")
        hit = is_secret(cmd)
        if hit:
            block(f"Lệnh chạm file bí mật ({hit}).")
        for pat, why in DANGER_CMD + no_cmd:
            if re.search(pat, cmd, re.I):
                block(f"Lệnh bị cấm: {why}. Hỏi người dùng trước.")
    sys.exit(0)


if __name__ == "__main__":
    main()
