"""Chạy Unity batchmode cho dự án ở thư mục hiện tại: compile, gọi 1 method editor, hoặc tự chơi bằng GPlayTestKit.

  python unity_run.py compile                          biên dịch (không GPU), in các dòng "error CS", exit 1 nếu có lỗi
  python unity_run.py exec <Class.Method> [--nographics] [--no-quit] [-- <tham số thêm cho Unity>]
  python unity_run.py playtest [--levels 1-3] [--out D:/tmp/playtest] [--size 1080x1920] [--driver Tên]
                               [--editmode] [--video] [--timeout 600] [-- <cờ riêng của dự án, vd -fresh -lang vi>]
      → gọi GPlay.TestKit.GPlayTest.RunFromCommandLine (có GPU), đọc report.json, in bảng kết quả +
        ĐƯỜNG DẪN ĐẦY ĐỦ từng ảnh, ghép các chuỗi khung hình thành .mp4 (cần opencv-python).
  python unity_run.py video <thư mục khung hình> [ra.mp4] [--fps 30]     ghép f_00001.jpg... thành mp4

Chung: --project <thư mục> (mặc định thư mục hiện tại) · --log <file> · biến môi trường UNITY_EXE để chỉ Unity.
Exit: 0 đạt · 1 lỗi / level không thắng · 2 Unity Editor đang mở project này · 3 thiếu Unity / license / driver.
Unity Editor phải ĐÓNG. License: Unity Hub phải đang mở và đã đăng nhập.
"""
import argparse
import glob
import json
import os
import re
import subprocess
import sys
import time


def out(*a):
    print(*a, flush=True)


def find_unity(project):
    exe = os.environ.get("UNITY_EXE")
    if exe and os.path.isfile(exe):
        return exe
    ver = None
    pv = os.path.join(project, "ProjectSettings", "ProjectVersion.txt")
    if os.path.isfile(pv):
        m = re.search(r"m_EditorVersion:\s*(\S+)", open(pv, encoding="utf-8").read())
        ver = m.group(1) if m else None
    if not ver:
        sys.exit("Không đọc được ProjectSettings/ProjectVersion.txt (chạy ở gốc dự án Unity hoặc thêm --project)")
    roots = [r"C:\Program Files\Unity\Hub\Editor", "/Applications/Unity/Hub/Editor", os.path.expanduser("~/Unity/Hub/Editor")]
    sec = os.path.join(os.environ.get("APPDATA", ""), "UnityHub", "secondaryInstallPath.json")
    if os.path.isfile(sec):
        try:
            p = json.load(open(sec, encoding="utf-8"))
            if p:
                roots.insert(0, p)
        except (ValueError, OSError):
            pass
    for r in roots:
        for rel in (("Editor", "Unity.exe"), ("Unity.app", "Contents", "MacOS", "Unity"), ("Editor", "Unity")):
            p = os.path.join(r, ver, *rel)
            if os.path.isfile(p):
                return p
    print(f"Không thấy Unity {ver}. Cài qua Unity Hub hoặc đặt biến UNITY_EXE.")
    sys.exit(3)


def unity_is_open(project):
    lock = os.path.join(project, "Temp", "UnityLockfile")
    if not os.path.exists(lock):
        return False
    try:
        with open(lock, "a"):
            pass
        return False
    except OSError:
        return True


def run_unity(project, args, log, timeout):
    if unity_is_open(project):
        out("Unity Editor đang mở project này: đóng Editor rồi chạy lại (batchmode không mở được project đang mở).")
        sys.exit(2)
    exe = find_unity(project)
    os.makedirs(os.path.dirname(os.path.abspath(log)), exist_ok=True)
    if os.path.exists(log):
        os.remove(log)
    cmd = [exe, "-batchmode", "-projectPath", project, "-logFile", log] + args
    t0 = time.time()
    p = subprocess.Popen(cmd)
    try:
        code = p.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        # kill ONLY the Unity this script started (never other Editors the user has open)
        if os.name == "nt":
            subprocess.call(["taskkill", "/F", "/T", "/PID", str(p.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            p.kill()
        p.wait()
        code = 124
    text = open(log, encoding="utf-8", errors="replace").read() if os.path.exists(log) else ""
    if "No valid Unity Editor license" in text:
        out("Unity không có license: mở Unity Hub, đăng nhập, rồi chạy lại.")
        sys.exit(3)
    return code, text, time.time() - t0


def compile_errors(text):
    seen, errs = set(), []
    for line in text.splitlines():
        if re.search(r"\berror CS\d+", line) and line not in seen:
            seen.add(line)
            errs.append(line.strip())
    return errs


def cmd_compile(a):
    code, text, sec = run_unity(a.project, ["-nographics", "-quit"], a.log or default_log("compile"), a.timeout)
    errs = compile_errors(text)
    for e in errs[:40]:
        out(e)
    if errs or code:
        out(f"LỖI: {len(errs)} lỗi biên dịch, Unity exit {code} ({sec:.0f}s). Log: {a.log or default_log('compile')}")
        return 1
    out(f"OK: compile sạch ({sec:.0f}s)")
    return 0


def cmd_exec(a):
    args = ["-executeMethod", a.method] + a.extra
    if a.nographics:
        args.insert(0, "-nographics")
    if not a.no_quit:
        args.insert(0, "-quit")
    log = a.log or default_log("exec")
    code, text, sec = run_unity(a.project, args, log, a.timeout)
    for e in compile_errors(text)[:40]:
        out(e)
    for line in text.splitlines():
        if re.match(r"^\[[A-Za-z][\w.]*\]", line):  # dòng log có nhãn [Tên] của tool dự án
            out(line)
    out(f"{'OK' if code == 0 else 'LỖI'}: {a.method} exit {code} ({sec:.0f}s). Log: {log}")
    return 0 if code == 0 else 1


def make_video(frames_dir, dst, fps):
    try:
        import cv2
        import numpy as np
    except ImportError:
        out("  (thiếu opencv-python: không ghép video; khung hình ở " + frames_dir + ")")
        return None
    files = sorted(glob.glob(os.path.join(frames_dir, "f_*.jpg")))
    if not files:
        return None
    first = cv2.imdecode(np.fromfile(files[0], np.uint8), cv2.IMREAD_COLOR)
    h, w = first.shape[:2]
    vw = cv2.VideoWriter(dst, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
    for f in files:
        img = cv2.imdecode(np.fromfile(f, np.uint8), cv2.IMREAD_COLOR)
        if img is not None and img.shape[:2] == (h, w):
            vw.write(img)
    vw.release()
    return dst if os.path.exists(dst) and os.path.getsize(dst) > 0 else None


def cmd_video(a):
    fps = a.fps
    meta = os.path.join(a.frames, "frames.json")
    if os.path.isfile(meta):
        fps = json.load(open(meta, encoding="utf-8")).get("fps", fps)
    dst = a.dst or a.frames.rstrip("/\\") + ".mp4"
    p = make_video(a.frames, dst, fps)
    out(("Đã ghi " + os.path.abspath(p).replace("\\", "/")) if p else "Không có khung hình f_*.jpg trong " + a.frames)
    return 0 if p else 1


def cmd_playtest(a):
    outdir = os.path.abspath(a.out).replace("\\", "/")
    os.makedirs(outdir, exist_ok=True)
    rep_path = os.path.join(outdir, "report.json")
    if os.path.exists(rep_path):
        os.remove(rep_path)
    log = a.log or os.path.join(outdir, "unity.log")
    args = ["-executeMethod", "GPlay.TestKit.GPlayTest.RunFromCommandLine", "-out", outdir, "-size", a.size,
            "-timeout", str(a.timeout)]
    if a.levels:
        args += ["-levels", a.levels]
    if a.driver:
        args += ["-driver", a.driver]
    if a.editmode:
        args.append("-editmode")
    if a.video:
        args.append("-video")
    args += a.extra
    code, text, sec = run_unity(a.project, args, log, a.timeout + 300)
    errs = compile_errors(text)
    for e in errs[:40]:
        out(e)
    for line in text.splitlines():
        if line.startswith("[GPlayUiCheck]") or line.startswith("[GPlayTest] FAIL"):
            out(line)
    if not os.path.exists(rep_path):
        out(f"LỖI: không có report.json (Unity exit {code}, {sec:.0f}s). Chưa chép GPlayTestKit / chưa có driver / lỗi biên dịch? Log: {log}")
        return 3 if code == 3 else 1
    rep = json.load(open(rep_path, encoding="utf-8"))
    if rep["levels"]:
        out(f"{'level':<16}{'kết quả':<9}ghi chú")
        for l in rep["levels"]:
            out(f"{l['level']:<16}{('WIN' if l['won'] else 'FAIL'):<9}{l.get('note', '')}")
    out(f"UI: {rep['uiImages']} ảnh, méo {rep['uiStretched']} · {rep['uiTexts']} chữ, tràn {rep['uiOverflow']}, "
        f"thiếu glyph {rep['uiMissingGlyph']}, font dự phòng {rep['uiFallbackFont']}")
    for f in rep["failures"]:
        out("FAIL: " + f)
    for e in rep["errors"][:10]:
        out("log lỗi: " + e)
    if rep["shots"]:
        out("Ảnh:")
        for s in rep["shots"]:
            out("  " + s)
    elif not rep.get("gpu", True):
        out("Không có ảnh: Unity chạy không GPU.")
    for v in rep["videos"]:
        p = make_video(v["dir"], v["dir"] + ".mp4", v["fps"])
        out(f"Video {v['name']}: {v['frames']} khung @{v['fps']} → " + (p.replace('\\', '/') if p else v["dir"]))
    won = sum(1 for l in rep["levels"] if l["won"])
    out(f"{'OK' if rep['ok'] and code == 0 else 'LỖI'}: {won}/{len(rep['levels'])} level thắng, Unity exit {code}, {sec:.0f}s · "
        f"báo cáo {rep_path.replace(chr(92), '/')} · log {log}")
    return 0 if rep["ok"] and code == 0 else 1


def default_log(name):
    import tempfile
    return os.path.join(tempfile.gettempdir(), f"unity_{name}.log")


def main():
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8", errors="replace")
    argv, extra = sys.argv[1:], []
    if "--" in argv:
        i = argv.index("--")
        argv, extra = argv[:i], argv[i + 1:]
    ap = argparse.ArgumentParser(description="Chạy Unity batchmode: compile / exec / playtest / video")
    sp = ap.add_subparsers(dest="cmd", required=True)

    def common(p, timeout):
        p.add_argument("--project", default=".")
        p.add_argument("--log")
        p.add_argument("--timeout", type=int, default=timeout)

    p = sp.add_parser("compile"); common(p, 1800); p.set_defaults(f=cmd_compile)
    p = sp.add_parser("exec"); common(p, 1800); p.add_argument("method")
    p.add_argument("--nographics", action="store_true"); p.add_argument("--no-quit", action="store_true",
                                                                         help="method tự gọi EditorApplication.Exit")
    p.set_defaults(f=cmd_exec)
    p = sp.add_parser("playtest"); common(p, 600); p.add_argument("--levels", default="")
    p.add_argument("--out", default=os.path.join(os.environ.get("TEMP", "/tmp"), "gplaytest"))
    p.add_argument("--size", default="1080x1920"); p.add_argument("--driver", default="")
    p.add_argument("--editmode", action="store_true"); p.add_argument("--video", action="store_true")
    p.set_defaults(f=cmd_playtest)
    p = sp.add_parser("video"); p.add_argument("frames"); p.add_argument("dst", nargs="?")
    p.add_argument("--fps", type=int, default=30); p.set_defaults(f=cmd_video)
    a = ap.parse_args(argv)
    a.extra = extra
    if hasattr(a, "project"):
        a.project = os.path.abspath(a.project)
    sys.exit(a.f(a))


if __name__ == "__main__":
    main()
