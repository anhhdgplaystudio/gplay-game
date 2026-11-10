"""Trích frame từ video gameplay để Claude xem (Read ảnh).

python frames.py <video> <thư mục ra> [--every 3] [--max 24] [--sheet]
  --every  giây giữa 2 frame (mặc định 3)
  --max    số frame tối đa (mặc định 24, video dài thì giãn đều)
  --sheet  ghép thêm sheet.jpg (lưới 4 cột) để xem nhanh 1 ảnh
Cần opencv-python (pip install opencv-python); không có thì dùng ffmpeg nếu có trong PATH.
Thư mục ra nên ở ổ tạm (D:/tmp/...), không để trong repo.
"""
import argparse, os, shutil, subprocess, sys


def content_box(imgs):
    """Khung chứa nội dung chung của mọi frame (cắt viền đen của video quay ngang / quay màn hình)."""
    import numpy as np
    if not imgs:
        return None
    m = np.zeros(imgs[0].shape[:2], bool)
    for img in imgs:
        m |= img.max(axis=2) > 24
    ys, xs = np.where(m)
    if not len(xs):
        return None
    h, w = m.shape
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    if (x1 - x0) * (y1 - y0) > 0.95 * w * h:
        return None
    return x0, y0, x1, y1


def with_cv2(video, out, every, mx, sheet):
    import cv2
    cap = cv2.VideoCapture(video)
    if not cap.isOpened():
        sys.exit(f"Không mở được video: {video}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0
    dur = total / fps if total else 0
    step = max(every, dur / mx) if dur else every
    times, t = [], 0.0
    while (not dur or t < dur) and len(times) < mx:
        times.append(t)
        t += step
    frames = []
    for t in times:
        cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
        ok, img = cap.read()
        if not ok:
            break
        frames.append((t, img))
    cap.release()
    box = content_box([m for _, m in frames])
    files = []
    for i, (t, img) in enumerate(frames):
        if box:
            x0, y0, x1, y1 = box
            img = img[y0:y1, x0:x1]
        h, w = img.shape[:2]
        if max(h, w) > 960:
            k = 960 / max(h, w)
            img = cv2.resize(img, (int(w * k), int(h * k)))
        f = os.path.join(out, f"{i + 1:03d}_{int(t)}s.jpg")
        cv2.imwrite(f, img, [cv2.IMWRITE_JPEG_QUALITY, 85])
        files.append(f)
    if sheet and files:
        import numpy as np
        imgs = [cv2.imread(f) for f in files]
        th = 360
        imgs = [cv2.resize(m, (int(m.shape[1] * th / m.shape[0]), th)) for m in imgs]
        cw = max(m.shape[1] for m in imgs)
        imgs = [cv2.copyMakeBorder(m, 0, 0, 0, cw - m.shape[1], cv2.BORDER_CONSTANT) for m in imgs]
        cols = 4
        while len(imgs) % cols:
            imgs.append(np.zeros_like(imgs[0]))
        rows = [np.hstack(imgs[r:r + cols]) for r in range(0, len(imgs), cols)]
        cv2.imwrite(os.path.join(out, "sheet.jpg"), np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 80])
    print(f"Video {dur:.0f}s → {len(files)} frame (mỗi {step:.1f}s) ở {out}" + (" + sheet.jpg" if sheet else ""))


def with_ffmpeg(video, out, every, mx):
    subprocess.run(["ffmpeg", "-loglevel", "error", "-i", video, "-vf", f"fps=1/{every},scale='min(960,iw)':-2",
                    "-frames:v", str(mx), os.path.join(out, "%03d.jpg")], check=True)
    print(f"ffmpeg: frame ở {out}")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("video"); ap.add_argument("out")
    ap.add_argument("--every", type=float, default=3); ap.add_argument("--max", type=int, default=24)
    ap.add_argument("--sheet", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    try:
        import cv2  # noqa: F401
        with_cv2(a.video, a.out, a.every, a.max, a.sheet)
    except ImportError:
        if not shutil.which("ffmpeg"):
            sys.exit("Thiếu opencv-python và ffmpeg: pip install opencv-python")
        with_ffmpeg(a.video, a.out, a.every, a.max)


if __name__ == "__main__":
    main()
