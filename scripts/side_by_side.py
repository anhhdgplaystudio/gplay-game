"""Ghép ảnh mẫu (frame game tham khảo / mockup) cạnh ảnh chụp game đang làm để so bằng mắt.

python side_by_side.py <ảnh mẫu> <ảnh game> <ra.jpg> [--labels "Mẫu" "Game"] [--grid 10] [--blend] [--height 1280]
                       [--crop-ref x0,y0,x1,y1] [--crop-ours x0,y0,x1,y1]
  --grid N      kẻ lưới mỗi N% chiều cao / rộng lên cả 2 ảnh, có số % → đọc tỉ lệ bố cục (vùng nào chiếm bao nhiêu %)
  --blend       thêm cột thứ 3 trộn 50% (chỉ có nghĩa khi 2 ảnh cùng tỉ lệ khung)
  --crop-*      cắt trước khi so, toạ độ theo phần trăm 0..100 (vd bỏ thanh trạng thái: 0,4,100,100)
In ra tỉ lệ khung 2 ảnh và cảnh báo khi lệch > 3% (so bố cục sẽ không chính xác).
Cần Pillow (pip install pillow).
"""
import argparse
import sys


def crop_pct(img, spec):
    if not spec:
        return img
    x0, y0, x1, y1 = [float(v) for v in spec.split(",")]
    w, h = img.size
    return img.crop((int(w * x0 / 100), int(h * y0 / 100), int(w * x1 / 100), int(h * y1 / 100)))


def font(size):
    from PIL import ImageFont
    for name in ("arial.ttf", "segoeui.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def draw_grid(img, step):
    from PIL import ImageDraw
    d = ImageDraw.Draw(img, "RGBA")
    w, h = img.size
    f = font(max(12, h // 70))
    p = step
    while p < 100:
        y, x = int(h * p / 100), int(w * p / 100)
        d.line([(0, y), (w, y)], fill=(255, 0, 255, 150), width=1)
        d.line([(x, 0), (x, h)], fill=(0, 255, 255, 90), width=1)
        d.rectangle([0, y - f.size - 2, f.size * 2.4, y], fill=(0, 0, 0, 150))
        d.text((2, y - f.size - 2), f"{int(p)}%", fill=(255, 255, 255, 255), font=f)
        p += step
    return img


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Ghép ảnh mẫu cạnh ảnh game để so")
    ap.add_argument("ref")
    ap.add_argument("ours")
    ap.add_argument("out")
    ap.add_argument("--labels", nargs=2, default=["Mẫu", "Game"])
    ap.add_argument("--grid", type=float, default=0)
    ap.add_argument("--blend", action="store_true")
    ap.add_argument("--height", type=int, default=1280)
    ap.add_argument("--crop-ref")
    ap.add_argument("--crop-ours")
    a = ap.parse_args()
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        sys.exit("Thiếu Pillow: pip install pillow")
    ref = crop_pct(Image.open(a.ref).convert("RGB"), a.crop_ref)
    ours = crop_pct(Image.open(a.ours).convert("RGB"), a.crop_ours)
    r1, r2 = ref.width / ref.height, ours.width / ours.height
    H = a.height
    ref = ref.resize((max(1, int(H * r1)), H), Image.LANCZOS)
    ours = ours.resize((max(1, int(H * r2)), H), Image.LANCZOS)
    cols = [(a.labels[0], ref), (a.labels[1], ours)]
    if a.blend:
        cols.append(("Trộn 50%", Image.blend(ref, ours.resize(ref.size, Image.LANCZOS), 0.5)))
    if a.grid:
        cols = [(n, draw_grid(im.copy(), a.grid)) for n, im in cols]
    gap, head = 12, max(36, H // 28)
    W = sum(im.width for _, im in cols) + gap * (len(cols) - 1)
    canvas = Image.new("RGB", (W, H + head), (24, 24, 24))
    d = ImageDraw.Draw(canvas)
    f = font(head - 12)
    x = 0
    for name, im in cols:
        d.text((x + 8, 4), name, fill=(255, 255, 255), font=f)
        canvas.paste(im, (x, head))
        x += im.width + gap
    canvas.save(a.out, quality=88)
    print(f"Đã ghi {a.out}")
    print(f"Tỉ lệ khung (rộng/cao): mẫu {r1:.3f} · game {r2:.3f}")
    if abs(r1 - r2) / r1 > 0.03:
        print("CẢNH BÁO: tỉ lệ khung lệch > 3%: chụp game đúng tỉ lệ ảnh mẫu (hoặc --crop-*) rồi so lại.")


if __name__ == "__main__":
    main()
