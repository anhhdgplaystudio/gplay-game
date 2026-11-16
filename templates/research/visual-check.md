# Bảng nghiệm thu hình — <tên game>

Đây là thước đo duy nhất để nói "khớp mẫu". Cột **Mẫu** điền ở bước research (trước G1), cột **Game** điền lại **toàn bộ** mỗi vòng build.
`orch.py check` đếm bảng này; `orch.py ms <mốc> done` bị từ chối khi mốc đó còn dòng chưa `đạt`.

- Ảnh chuẩn: `<tmp>/ref/golden/...` (cao ≥ 1080 px; thấp hơn → ghi rõ, số đo chi tiết không tin được).
- Level chuẩn: `.game/research/ref-level.md` (game dựng lại đúng level này để chụp so).
- Mỗi dòng 1 thuộc tính **đo được hoặc chỉ ra được trên ảnh crop**. Không viết "giống mẫu", "đẹp", "đúng style".
- Ảnh crop: `side_by_side.py <chuẩn> <game> <tmp>/check/<mã>.jpg --crop x0,y0,x1,y1 [--grid 25]` (cùng 1 vùng ở 2 ảnh, phóng to).
- Kết quả (ô cuối): `đạt` · `lệch` (ghi lệch gì) · `chưa đo` · `chủ ý` (khác có chủ ý, người dùng đã đồng ý: ghi cổng / ngày).
- Ngưỡng `đạt`: vị trí + cỡ lệch ≤ 2 % bề ngang màn; màu ΔRGB ≤ 20 mỗi kênh; hình dáng / lớp che: nhìn ảnh crop không chỉ ra được điểm khác.
- Mã: `V` hình tĩnh · `C` chuyển động · `U` UI / màn khác. Cột Mốc: mốc phải đạt dòng này (hình tĩnh M1, chuyển động M2, UI theo plan).

## A. Hình tĩnh (mốc M1, cổng GV)

Mỗi vật thể trong visual-spec mục 4 có đủ các dòng: vị trí · cỡ · màu · hình dáng (bo góc, viền, độ dày, chi tiết) · số lượng + khoảng cách · lớp che (cái gì đè lên cái gì).

| Mã | Mốc | Vật · thuộc tính | Mẫu (số đo, đơn vị) | Game (số đo) | Ảnh crop | KQ |
|---|---|---|---|---|---|---|
| V1 | M1 | Camera · góc nhìn (tỉ lệ cao / rộng của 1 ô vuông trên mặt đất) | | | | chưa đo |
| V2 | M1 | <vật A> · tâm (x %, y %) | | | | chưa đo |
| V3 | M1 | <vật A> · bề ngang (% bề ngang màn) | | | | chưa đo |
| V4 | M1 | <vật A> · màu chính (hex lấy từ frame) | | | | chưa đo |
| V5 | M1 | <vật A> · hình dáng: <bo góc / viền / chi tiết thấy được> | | | | chưa đo |
| V6 | M1 | <vật A> · khoảng cách giữa 2 cái kề nhau, cái nào che cái nào | | | | chưa đo |
| V7 | M1 | Nền · màu, hoạ tiết, bóng đổ | | | | chưa đo |

## B. Chuyển động (mốc M2, cổng GS)

Mỗi sự kiện trong visual-spec mục 5 ≥ 1 dòng: đường đi · hình dạng đám / đội hình · thời lượng (đếm frame của clip) · thứ tự · hiệu ứng kèm.
So bằng 2 dải frame cùng nhịp: `study_video.py <video gốc> ... --clip t0 t1 --fps 8` và video tự chơi của game cùng `--fps`.

| Mã | Mốc | Sự kiện · thuộc tính | Mẫu (clip + số đo) | Game (clip + số đo) | Ảnh dải frame | KQ |
|---|---|---|---|---|---|---|
| C1 | M2 | <sự kiện> · đường đi | | | | chưa đo |
| C2 | M2 | <sự kiện> · thời lượng (s) | | | | chưa đo |

## C. UI + màn khác (mốc theo plan)

| Mã | Mốc | Màn · thành phần · thuộc tính | Mẫu | Game | Ảnh crop | KQ |
|---|---|---|---|---|---|---|
| U1 | M1 | HUD · <nút> · vị trí + cỡ | | | | chưa đo |

## D. Soát theo vùng (chống sót)

Chia ảnh chuẩn thành lưới 3 cột × 4 hàng, crop từng ô ở độ phân giải gốc, Read từng ô và liệt kê **mọi thứ nhìn thấy**. Thứ nào chưa có dòng ở trên → thêm dòng.

| Ô (hàng, cột) | Ảnh crop | Thấy gì | Đã có dòng |
|---|---|---|---|
| 1,1 | | | |

## E. Người dùng bổ sung ở G1

Câu hỏi ở G1: "Nhìn ảnh chuẩn, điều gì sai là bạn thấy ngay?" → mỗi ý thêm 1 dòng vào bảng A / B / C, ghi `[người dùng G1]` ở cột Vật.

## Thay đổi
- <ngày>: bản đầu
