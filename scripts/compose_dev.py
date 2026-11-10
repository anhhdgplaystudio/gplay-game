"""Ghép ảnh cảnh từ thư mục dev (png + .cor + mapping.json) để kiểm bằng mắt, không cần Unity.

python compose_dev.py <thư mục dev> <out.png> [--canvas 1080x1920] [--hidden] [--only a,b] [--skip a,b]
                      [--box x,y,w,h[,nhãn]] ...   (vẽ khung: vùng thả, bong bóng...)
Cần Pillow (pip install pillow).
"""
import argparse
import json
import os
import sys

# Console Windows mặc định cp1252: ép UTF-8 để in tiếng Việt
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

try:
    from PIL import Image, ImageDraw
except ImportError:
    print("Cần Pillow: pip install pillow")
    sys.exit(1)

REF = {"ui", "khung", "thumb", "choose", "background"}


def walk(nodes, prefix="", parent_visible=True):
    for n in nodes:
        vis = parent_visible and n.get("visible", True)
        if n.get("isGroup"):
            yield from walk(n.get("children", []), prefix + n["name"] + "/", vis)
        else:
            yield prefix + n["name"], vis


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dev")
    ap.add_argument("out")
    ap.add_argument("--canvas", default="1080x1920")
    ap.add_argument("--hidden", action="store_true", help="vẽ cả layer ẩn")
    ap.add_argument("--only", default="", help="chỉ vẽ layer chứa các chuỗi này")
    ap.add_argument("--skip", default="", help="bỏ layer chứa các chuỗi này")
    ap.add_argument("--box", action="append", default=[])
    a = ap.parse_args()
    cw, ch = (int(v) for v in a.canvas.lower().split("x"))
    only = [s for s in a.only.split(",") if s]
    skip = [s for s in a.skip.split(",") if s]

    with open(os.path.join(a.dev, "mapping.json"), encoding="utf-8-sig") as f:
        layers = list(walk(json.load(f)))
    canvas = Image.new("RGBA", (cw, ch), (40, 40, 40, 255))
    drawn = 0
    for name, vis in reversed(layers):  # mapping: trên cùng trước → vẽ từ dưới lên
        base = name.split("/")[-1]
        if base.split(" ")[0].lower() in REF:
            continue
        if not vis and not a.hidden:
            continue
        if only and not any(s in name for s in only):
            continue
        if any(s in name for s in skip):
            continue
        png, cor = os.path.join(a.dev, name + ".png"), os.path.join(a.dev, name + ".cor")
        if not (os.path.isfile(png) and os.path.isfile(cor)):
            continue
        with open(cor, encoding="utf-8-sig") as f:
            x, y = (int(round(float(v))) for v in f.read().split()[:2])
        img = Image.open(png).convert("RGBA")
        canvas.alpha_composite(img, (max(x, 0), max(y, 0)),
                               (max(-x, 0), max(-y, 0)))
        drawn += 1

    d = ImageDraw.Draw(canvas)
    for b in a.box:
        p = b.split(",")
        x, y, w, h = (float(v) for v in p[:4])
        d.rectangle([x, y, x + w, y + h], outline=(255, 0, 0, 255), width=4)
        if len(p) > 4:
            d.text((x + 6, y + 6), p[4], fill=(255, 0, 0, 255))
    canvas.convert("RGB").save(a.out)
    print(f"Đã vẽ {drawn} layer → {a.out}")


if __name__ == "__main__":
    main()
