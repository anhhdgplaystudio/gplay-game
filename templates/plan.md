# Plan — <Tên game> · v1

Trạng thái: nháp | chốt (G2: <ngày>) · Nguồn: `.game/research/teardown.md`, `visual-spec.md`, `base.md`, quyết định G1.

## 1. Mục tiêu bản đầu
- Người chơi: ...
- Luật lõi (tóm tắt 3–5 dòng từ teardown; chi tiết ở teardown.md, không chép lại): ...
- Số level / màn: ... · Luồng màn: Loading → Home → Game (theo visual-spec mục 1)
- Tiêu chí "chơi được": ...
- Khác game tham khảo ở: ...

## 2. Ngoài phạm vi bản đầu
- ... (vd SDK quảng cáo thật, build store, art cuối: làm khi người dùng yêu cầu)

## 3. Kiến trúc
- Base dùng lại: ... · xoá: ...
- Thư mục code / namespace / asmdef: ... (luật chơi C# thuần, test không cần Unity)
- Dữ liệu level: định dạng ..., importer ..., database ...
- Hình: tạm bằng khối / sprite đơn sắc đúng cỡ + bố cục; art thật theo yêu cầu (art-on-demand)

## 4. Cách kiểm (lệnh thật, dùng lại ở mọi mốc)
- Compile: `...` · Test logic: `...` · Validator level: `...`
- Tự chơi + chụp ảnh (phiên chính chạy, Unity đóng): `...` → ảnh ở `<tmp>/playtest_<mốc>/`
- So hình: `side_by_side.py <ảnh chuẩn> <ảnh game> ... --grid 10`
- Ngưỡng độ khó (nếu cơ chế có solver): ...

## 5. Mốc
| Mốc | Người dùng thấy được gì khi xong | Việc chính | Kiểm + ảnh bằng chứng | Giao subagent | Ước lượng |
|---|---|---|---|---|---|
| M1 **Level mẫu** (→ cổng GS) | 1 level chơi đúng luật, màn chơi khớp ảnh chuẩn | Dọn base, luật lõi + test, 1 level tay, hình màn chơi, tự chơi | test, tự chơi, ảnh ghép cạnh ảnh chuẩn | luật lõi + test | |
| M2 Cơ chế phụ + booster | | | | | |
| M3 Pipeline level | N level thật qua importer, validator / solver | | | tool level | |
| M4 Luồng màn + UI + meta | Loading → Home → Game → thắng / thua, coin, lưu | | ảnh từng màn, kiểm méo UI | | |
| M5 Nội dung | Đủ level bản đầu theo nhịp khó | | tự chơi hết level, bảng độ khó | | |
| M6 Localization + hoàn thiện | | | ảnh từng ngôn ngữ, glyph thiếu = 0 | | |

Không làm M2+ khi chưa có GS.

## 6. Tiêu chí nghiệm thu cuối
- [ ] Compile sạch, test + validator sạch, tự chơi hết level đạt
- [ ] Danh sách so của visual-spec mục 9 đạt, người dùng đã xem ảnh
- [ ] Danh sách "phải thay trước phát hành" rõ ràng (asset tạm, tên, package id, SDK)

## 7. Rủi ro + điều còn mở
- ...

## Thay đổi
- v1: bản đầu
