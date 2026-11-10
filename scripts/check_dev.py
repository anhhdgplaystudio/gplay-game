"""Kiểm thư mục art xuất từ PSD (định dạng dev/): png + .cor + mapping.json.

python check_dev.py <thư mục dev> [--canvas 1080x1920]
Lỗi: thiếu cặp png/cor, .cor sai định dạng, layer trong mapping không có file, png không bội số 4,
layer nằm ngoài canvas. Exit 1 nếu có lỗi.
"""
import argparse
import json
import os
import struct
import sys

# Console Windows mặc định cp1252: ép UTF-8 để in tiếng Việt
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

REF = {"ui", "khung", "thumb", "choose", "background"}  # layer tham khảo, importer bỏ qua


def png_size(path):
    with open(path, "rb") as f:
        head = f.read(24)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", head[16:24])


def walk_mapping(nodes, prefix=""):
    for n in nodes:
        name = n.get("name", "")
        if n.get("isGroup"):
            yield from walk_mapping(n.get("children", []), prefix + name + "/")
        else:
            yield prefix + name, n.get("visible", True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dev")
    ap.add_argument("--canvas", default="1080x1920")
    a = ap.parse_args()
    cw, ch = (int(v) for v in a.canvas.lower().split("x"))
    root = a.dev
    if not os.path.isdir(root):
        print(f"Không có thư mục: {root}")
        sys.exit(1)

    errors, warns = [], []
    pngs, cors = set(), set()
    for d, _, files in os.walk(root):
        rel = os.path.relpath(d, root).replace("\\", "/")
        rel = "" if rel == "." else rel + "/"
        if "/spine/" in "/" + rel or rel.startswith("spine/"):
            continue  # spine riêng từng layer có định dạng khác
        for f in files:
            stem, ext = os.path.splitext(f)
            if ext.lower() == ".png":
                pngs.add(rel + stem)
            elif ext.lower() == ".cor":
                cors.add(rel + stem)

    # Đọc mapping trước: file không có trong mapping thường do tool sinh (icon, mask...) → chỉ cảnh báo
    mapped = set()
    mpath = os.path.join(root, "mapping.json")
    if os.path.isfile(mpath):
        try:
            with open(mpath, encoding="utf-8-sig") as f:
                mapped = {n for n, _ in walk_mapping(json.load(f))}
        except Exception:
            pass

    strip_png = {k.strip(): k for k in pngs}
    for k in sorted(cors - pngs):
        if k.strip() in strip_png:
            errors.append(f"Tên lệch dấu cách: '{strip_png[k.strip()]}.png' vs '{k}.cor'")
        else:
            errors.append(f"Thiếu .png: {k}")
    strip_cor = {k.strip() for k in cors}
    for k in sorted(pngs - cors):
        if k.strip() in strip_cor or k.split("/")[-1].split(" ")[0].lower() in REF:
            continue
        (errors if k in mapped else warns).append(f"Thiếu .cor: {k}" + ("" if k in mapped else " (không có trong mapping, file tool sinh?)"))

    for k in sorted(pngs & cors):
        try:
            with open(os.path.join(root, k + ".cor"), encoding="utf-8-sig") as f:
                x, y = (float(v) for v in f.read().split()[:2])
        except Exception:
            errors.append(f".cor sai định dạng (cần 'x y'): {k}")
            continue
        size = png_size(os.path.join(root, k + ".png"))
        if not size:
            errors.append(f"PNG hỏng: {k}")
            continue
        w, h = size
        if w % 4 or h % 4:
            warns.append(f"Kích thước không bội số 4 ({w}x{h}): {k}")
        if x + w <= 0 or y + h <= 0 or x >= cw or y >= ch:
            warns.append(f"Nằm ngoài canvas ({x:.0f},{y:.0f} {w}x{h}): {k}")

    if not os.path.isfile(mpath):
        errors.append("Thiếu mapping.json (importer không biết thứ tự lớp)")
    else:
        try:
            with open(mpath, encoding="utf-8-sig") as f:
                tree = json.load(f)
            names = [n for n, _ in walk_mapping(tree)]
            for n in names:
                if n not in pngs and n.split("/")[-1].split(" ")[0].lower() not in REF:
                    warns.append(f"mapping có nhưng không có file: {n}")
            for k in sorted(pngs - set(names)):
                warns.append(f"Có file nhưng không có trong mapping: {k}")
            flat = [n.split("/")[-1] for n in names]
            if len(flat) > 4 and flat == sorted(flat):
                warns.append("mapping.json đang sắp theo tên? Phải theo thứ tự PSD (trên cùng trước).")
        except Exception as e:
            errors.append(f"mapping.json lỗi: {e}")

    for w in warns:
        print("CẢNH BÁO", w)
    for e in errors:
        print("LỖI", e)
    print(f"{len(pngs)} layer, {len(errors)} lỗi, {len(warns)} cảnh báo")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
