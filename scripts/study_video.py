"""Mổ xẻ video gameplay để Claude đọc được (Read ảnh): frame đánh số, điểm cắt cảnh, bảng màu, đoạn quay chậm.

Tổng quan cả video:
  python study_video.py <video> <thư mục ra> [--max 36] [--cut 0.45] [--no-crop]
    → frames/NNN_<giây>s.jpg   frame rải đều + frame ngay sau mỗi điểm cắt cảnh (đổi màn, popup, chuyển scene)
      sheet.jpg                lưới mọi frame, mỗi ô có nhãn "#số giây" (xem 1 ảnh là thấy cả video)
      palette.png              8 màu chính + tỉ lệ
      study.json               thời lượng, fps, kích thước, danh sách frame (giây, có phải điểm cắt, mức chuyển động), bảng màu

Soi kỹ 1 đoạn (đọc chuyển động, thứ tự, thời gian: xe vào / ra, vật bay, popup hiện):
  python study_video.py <video> <thư mục ra> --clip 12.0 15.5 [--fps 8]
    → clip_12.0-15.5/NNN_<giây>.jpg + strip.jpg (các frame liên tiếp có nhãn thời gian)

Cần opencv-python + numpy (pip install opencv-python). Thư mục ra để ở ổ tạm, không để trong repo.
"""
import argparse
import json
import os
import sys


def need_cv():
    try:
        import cv2  # noqa: F401
        import numpy  # noqa: F401
    except ImportError:
        sys.exit("Thiếu opencv-python: pip install opencv-python")


def imwrite(path, img, q=85):
    import cv2
    jpg = path.lower().endswith(".jpg")
    ok, buf = cv2.imencode(".jpg" if jpg else ".png", img, [cv2.IMWRITE_JPEG_QUALITY, q] if jpg else [])
    if ok:
        buf.tofile(path)  # ghi được cả đường dẫn có dấu


def content_box(imgs):
    """Khung nội dung chung (cắt viền đen của video quay màn hình điện thoại đặt trong khung ngang)."""
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
    return int(x0), int(y0), int(x1), int(y1)


def fit(img, longest=960):
    import cv2
    h, w = img.shape[:2]
    if max(h, w) > longest:
        k = longest / max(h, w)
        img = cv2.resize(img, (int(w * k), int(h * k)), interpolation=cv2.INTER_AREA)
    return img


def label(img, text):
    import cv2
    img = img.copy()
    (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2)
    cv2.rectangle(img, (0, 0), (tw + 10, th + 12), (0, 0, 0), -1)
    cv2.putText(img, text, (5, th + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2, cv2.LINE_AA)
    return img


def sheet(tiles, cols, tile_h):
    import cv2
    import numpy as np
    tiles = [cv2.resize(m, (max(1, int(m.shape[1] * tile_h / m.shape[0])), tile_h)) for m in tiles]
    cw = max(m.shape[1] for m in tiles)
    tiles = [cv2.copyMakeBorder(m, 0, 0, 0, cw - m.shape[1], cv2.BORDER_CONSTANT) for m in tiles]
    while len(tiles) % cols:
        tiles.append(np.zeros_like(tiles[0]))
    return np.vstack([np.hstack(tiles[r:r + cols]) for r in range(0, len(tiles), cols)])


def open_video(path):
    import cv2
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        sys.exit(f"Không mở được video: {path} (đường dẫn có dấu tiếng Việt thì chép video sang đường dẫn không dấu)")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0
    return cap, fps, total, (total / fps if total else 0)


def scan(cap, fps, total, scan_fps):
    """Đọc lướt cả video: mỗi mẫu trả (giây, chênh histogram so mẫu trước, mức chuyển động)."""
    import cv2
    import numpy as np
    step = max(1, int(round(fps / scan_fps)))
    out, prev_h, prev_g, i = [], None, None, 0
    while True:
        if i % step:
            if not cap.grab():
                break
            i += 1
            continue
        ok, img = cap.read()
        if not ok:
            break
        small = cv2.resize(img, (96, 96), interpolation=cv2.INTER_AREA)
        hsv = cv2.cvtColor(small, cv2.COLOR_BGR2HSV)
        hist = cv2.calcHist([hsv], [0, 1, 2], None, [8, 4, 4], [0, 180, 0, 256, 0, 256])
        cv2.normalize(hist, hist)
        gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY).astype(np.int16)
        d = float(cv2.compareHist(prev_h, hist, cv2.HISTCMP_BHATTACHARYYA)) if prev_h is not None else 0.0
        mo = float(np.abs(gray - prev_g).mean()) if prev_g is not None else 0.0
        out.append((i / fps, d, mo))
        prev_h, prev_g = hist, gray
        i += 1
    return out


def grab_at(cap, t):
    import cv2
    cap.set(cv2.CAP_PROP_POS_MSEC, max(0.0, t) * 1000)
    ok, img = cap.read()
    return img if ok else None


def palette(imgs, k=8):
    import cv2
    import numpy as np
    px = np.vstack([cv2.resize(m, (48, 48), interpolation=cv2.INTER_AREA).reshape(-1, 3) for m in imgs]).astype(np.float32)
    if len(px) > 60000:
        px = px[np.random.default_rng(0).choice(len(px), 60000, replace=False)]
    crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
    _, labels, centers = cv2.kmeans(px, k, None, crit, 3, cv2.KMEANS_PP_CENTERS)
    counts = np.bincount(labels.ravel(), minlength=k)
    order = np.argsort(-counts)
    return [{"hex": "#%02x%02x%02x" % (int(centers[i][2]), int(centers[i][1]), int(centers[i][0])),
             "share": round(float(counts[i]) / len(px), 3)} for i in order]


def palette_image(pal):
    import cv2
    import numpy as np
    img = np.zeros((90, 110 * len(pal), 3), np.uint8)
    for i, p in enumerate(pal):
        h = p["hex"].lstrip("#")
        bgr = (int(h[4:6], 16), int(h[2:4], 16), int(h[0:2], 16))
        cv2.rectangle(img, (i * 110, 0), (i * 110 + 110, 90), bgr, -1)
        txt = f"{p['hex']} {int(p['share'] * 100)}%"
        col = (0, 0, 0) if sum(bgr) > 380 else (255, 255, 255)
        cv2.putText(img, txt, (i * 110 + 4, 82), cv2.FONT_HERSHEY_SIMPLEX, 0.36, col, 1, cv2.LINE_AA)
    return img


def overview(a):
    cap, fps, total, dur = open_video(a.video)
    samples = scan(cap, fps, total, a.scan_fps)
    if not samples:
        sys.exit("Video không có frame đọc được")
    if not dur:
        dur = samples[-1][0]
    # điểm cắt: chênh histogram vượt ngưỡng, cách nhau >= 1 s; lấy frame sau điểm cắt 0.4 s cho hình đã ổn định
    cuts, last = [], -9.0
    for t, d, _ in samples:
        if d >= a.cut and t - last >= 1.0:
            cuts.append(round(t + 0.4, 2))
            last = t
    n_uniform = max(4, a.max - min(len(cuts), a.max // 2))
    uniform = [round(dur * (i + 0.5) / n_uniform, 2) for i in range(n_uniform)]
    cut_keep = cuts if len(cuts) <= a.max // 2 else [cuts[int(i * len(cuts) / (a.max // 2))] for i in range(a.max // 2)]
    times = sorted(set(uniform + cut_keep))
    times = [t for i, t in enumerate(times) if i == 0 or t - times[i - 1] >= 0.3]

    def motion_at(t):
        return round(min(samples, key=lambda s: abs(s[0] - t))[2], 1)

    raw = [(t, grab_at(cap, t)) for t in times]
    raw = [(t, m) for t, m in raw if m is not None]
    cap.release()
    box = None if a.no_crop else content_box([m for _, m in raw])
    fdir = os.path.join(a.out, "frames")
    os.makedirs(fdir, exist_ok=True)
    frames, tiles, keep = [], [], []
    for i, (t, img) in enumerate(raw, 1):
        if box:
            img = img[box[1]:box[3], box[0]:box[2]]
        img = fit(img)
        name = f"{i:03d}_{t:.1f}s.jpg"
        imwrite(os.path.join(fdir, name), img)
        is_cut = t in cut_keep
        frames.append({"n": i, "t": t, "file": f"frames/{name}", "cut": is_cut, "motion": motion_at(t)})
        tiles.append(label(fit(img, 480), f"#{i} {t:.1f}s" + (" CUT" if is_cut else "")))
        keep.append(img)
    cols = 6 if len(tiles) > 24 else 4
    imwrite(os.path.join(a.out, "sheet.jpg"), sheet(tiles, cols, 420), 80)
    pal = palette(keep)
    imwrite(os.path.join(a.out, "palette.png"), palette_image(pal))
    h, w = keep[0].shape[:2]
    info = {"video": os.path.abspath(a.video), "duration_s": round(dur, 1), "fps": round(fps, 2),
            "frame_size": [w, h], "orientation": "dọc" if h > w else "ngang", "cropped_black_border": bool(box),
            "cuts_s": cuts, "frames": frames, "palette": pal}
    with open(os.path.join(a.out, "study.json"), "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=1)
    out = os.path.abspath(a.out).replace("\\", "/")
    print(f"Video {dur:.0f}s {w}x{h} ({info['orientation']}), {len(cuts)} điểm cắt cảnh → {len(frames)} frame")
    print(f"  {out}/sheet.jpg   (xem trước, rồi Read frame cần soi: {out}/frames/NNN_<giây>s.jpg)")
    print(f"  {out}/palette.png · {out}/study.json")
    print("Soi chuyển động 1 đoạn: thêm --clip <giây đầu> <giây cuối> [--fps 8]")


def clip(a):
    t0, t1 = a.clip
    if t1 <= t0:
        sys.exit("--clip: giây cuối phải lớn hơn giây đầu")
    cap, fps, total, dur = open_video(a.video)
    n = min(60, max(2, int(round((t1 - t0) * a.fps)) + 1))
    times = [round(t0 + (t1 - t0) * i / (n - 1), 2) for i in range(n)]
    raw = [(t, grab_at(cap, t)) for t in times]
    raw = [(t, m) for t, m in raw if m is not None]
    cap.release()
    if not raw:
        sys.exit("Không đọc được frame trong đoạn này")
    box = None if a.no_crop else content_box([m for _, m in raw])
    cdir = os.path.join(a.out, f"clip_{t0:.1f}-{t1:.1f}")
    os.makedirs(cdir, exist_ok=True)
    tiles = []
    for i, (t, img) in enumerate(raw, 1):
        if box:
            img = img[box[1]:box[3], box[0]:box[2]]
        img = fit(img)
        imwrite(os.path.join(cdir, f"{i:03d}_{t:.2f}.jpg"), img)
        tiles.append(label(fit(img, 480), f"{t:.2f}s"))
    cols = min(8, len(tiles))
    imwrite(os.path.join(cdir, "strip.jpg"), sheet(tiles, cols, 420), 80)
    out = os.path.abspath(cdir).replace("\\", "/")
    print(f"Đoạn {t0:.1f}–{t1:.1f}s: {len(tiles)} frame (cách nhau {(t1 - t0) / max(1, len(tiles) - 1):.2f}s)")
    print(f"  {out}/strip.jpg")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Mổ xẻ video gameplay: frame, điểm cắt cảnh, bảng màu, đoạn quay chậm")
    ap.add_argument("video")
    ap.add_argument("out")
    ap.add_argument("--max", type=int, default=36, help="số frame tối đa của tổng quan")
    ap.add_argument("--cut", type=float, default=0.45, help="ngưỡng cắt cảnh 0..1 (thấp = nhạy hơn)")
    ap.add_argument("--scan-fps", type=float, default=3, help="số mẫu / giây khi đọc lướt tìm điểm cắt")
    ap.add_argument("--clip", type=float, nargs=2, metavar=("T0", "T1"), help="soi kỹ đoạn T0..T1 (giây)")
    ap.add_argument("--fps", type=float, default=8, help="frame / giây cho --clip")
    ap.add_argument("--no-crop", action="store_true", help="không cắt viền đen")
    a = ap.parse_args()
    need_cv()
    os.makedirs(a.out, exist_ok=True)
    clip(a) if a.clip else overview(a)


if __name__ == "__main__":
    main()
