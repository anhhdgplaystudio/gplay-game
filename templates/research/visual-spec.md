# Spec hình + luồng màn — <tên game>

Ảnh chuẩn (đường dẫn đầy đủ): gameplay `<tmp>/ref/golden/game.jpg` · home `...` · loading `...` · thắng `...` · thua `...` · popup `...`
Ảnh lưới tỉ lệ: `<tmp>/ref/grid.jpg`. Ảnh người dùng gửi = chuẩn cao nhất.
Nguồn đo: video `<id>` khung game `<rộng> × <cao>` px, `<fps>` fps (cao < 1080 → ghi rõ: số đo chi tiết chưa tin được, đang tìm nguồn nét hơn).
Level chuẩn: `.game/research/ref-level.md` · Bảng nghiệm thu (số đo từng vật thể): `.game/research/visual-check.md`.

## 1. Luồng màn
```
Loading → Home → Game → (Thắng → Game kế | Thua → Hồi sinh / Chơi lại) ; Home ↔ Settings ; ...
```
| Chuyển | Kiểu (fade / trượt / tức thì) | Bằng chứng |
|---|---|---|

## 2. Bố cục màn chơi (theo % chiều cao, đo trên ảnh lưới)
| Vùng | Từ % | Tới % | Nội dung | Ghi chú (căn trái / giữa, lề) |
|---|---|---|---|---|
| HUD | 0 | | | |

- Hướng: cái gì ở trên, cái gì ở dưới; vật di chuyển từ đâu tới đâu trên màn hình.

## 3. Camera
- 2D / 3D · góc nhìn (thẳng trên / nghiêng ~°) · phối cảnh / trực giao · vật gần đáy màn có to hơn không.

## 4. Danh mục vật thể
| Vật | Hình dáng (khối, bo tròn, nhân vật có mặt...) | Cỡ tương đối | Màu | Trạng thái | Chuyển động riêng | Frame |
|---|---|---|---|---|---|---|

## 5. Chuyển động + feel (từ --clip)
| Sự kiện | Cái gì động, đường đi | Thời lượng | Hiệu ứng kèm (nảy, hạt, rung, số bay, âm) | Clip |
|---|---|---|---|---|

## 6. UI từng màn
| Màn | Thành phần (nút, thanh, nhãn) | Vị trí | Kiểu (màu, viền, chữ) |
|---|---|---|---|

## 7. Màu + nền
- Bảng màu chính (palette.png): ... · Nền: trơn / hoạ tiết / chia ô · Bóng đổ: ...

## 8. Điểm sẽ khác game gốc (đã thống nhất với người dùng)
- ...

## 9. Nghiệm thu
Không dùng danh sách chung chung ở đây. So theo **`.game/research/visual-check.md`** (mỗi vật thể / sự kiện có dòng số đo + ảnh crop);
mỗi vòng build điền lại cả cột Game, `orch.py check` đếm số dòng đạt.

## Thay đổi
- <ngày>: bản đầu
