# Brief art — <tên bộ> (cho Codex / Gemini)

Làm mọi việc trong thư mục này. Kết quả ghi vào `out/`. Không tải / dùng ảnh có bản quyền; không sao chép nhân vật, logo của game khác.

## Phong cách
- Ảnh tham chiếu (chỉ để nắm phong cách): `ref/<file>` ...
- Bảng màu: #...... #...... (nền), #...... (nhấn)
- Nét: <bo tròn / viền đậm / bóng mềm ...>. Thiết kế ở độ phân giải màn 1080×1920.

## Bảng thiết kế chung (vẽ TRƯỚC, các file khác bám theo)
- `out/sheet_<vật>.png` 2048×1024: <vật> nhìn trước / nghiêng / trên, màu, tỉ lệ. Mọi chỗ xuất hiện của <vật> phải khớp bảng này.

## Danh sách file (kích thước pixel CHÍNH XÁC, PNG, nền trong suốt trừ khi ghi khác)
| File | Rộng × cao | Nội dung | Ghi chú (9-slice border, vùng an toàn, không chữ) |
|---|---|---|---|
| `out/btn_play.png` | 520×180 | Nút chính, không chữ | 9-slice: trái/phải 60 |
| `out/bg_home.png` | 1080×1920 | Nền home, không trong suốt | Không đặt chi tiết ở 0–8% trên (HUD) |

## Điều kiện đạt (tự kiểm trước khi báo xong)
- Đúng kích thước từng file; alpha sạch (không viền trắng / nền dính); hình không chạm mép (chừa ≥ 2 px, hình có bóng chừa đủ bóng).
- Không có chữ trong ảnh trừ logo. Cùng bộ thì cùng độ dày viền, cùng hướng sáng.
- Ghi `out/NOTES.md`: file nào làm bằng cách nào, điều chưa đạt.
