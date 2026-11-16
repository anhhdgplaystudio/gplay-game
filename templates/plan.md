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
- So hình: toàn màn `side_by_side.py <ảnh chuẩn> <ảnh game> ... --grid 10` + crop từng dòng bảng nghiệm thu `--crop x0,y0,x1,y1` → `orch.py check --ms <mốc>`
- Số bố cục (vị trí, cỡ, camera, tốc độ) nằm ở: `<file dữ liệu / ScriptableObject>` (không rải hằng số trong code)
- Ngưỡng độ khó (nếu cơ chế có solver): ...

## 5. Mốc
| Mốc | Người dùng thấy được gì khi xong | Việc chính | Kiểm + ảnh bằng chứng | Giao subagent | Ước lượng |
|---|---|---|---|---|---|
| M1 **Khung hình tĩnh** (→ cổng GV) | Ảnh màn chơi đứng yên ở đầu level chuẩn, đặt cạnh ảnh chuẩn + ảnh crop từng vùng. Chưa chơi được | Dọn base, bộ tự chơi, scene dựng từ `ref-level.md`, camera, vật thể, nền, HUD tĩnh, file số bố cục | mọi dòng `V*` của bảng nghiệm thu đã đo; ảnh ghép + ảnh crop | luật lõi + test (song song, không cần hình) | |
| M2 **Level mẫu chơi được** (→ cổng GS) | Level chuẩn chơi đúng luật từ đầu tới thắng / thua, chuyển động khớp clip | Nối luật, input, chuyển động theo dòng `C*`, thắng / thua, tự giải | test, tự chơi, video + dải frame so clip gốc, dòng `C*` đã đo | | |
| M3 Cơ chế phụ + booster | | | | | |
| M4 Pipeline level | N level thật qua importer, validator / solver | | | tool level | |
| M5 Luồng màn + UI + meta | Loading → Home → Game → thắng / thua, coin, lưu | | ảnh từng màn, dòng `U*` của bảng, kiểm méo UI | | |
| M6 Nội dung | Đủ level bản đầu theo nhịp khó | | tự chơi hết level, bảng độ khó | | |
| M7 Localization + hoàn thiện | | | ảnh từng ngôn ngữ, glyph thiếu = 0 | | |

Không làm M2 khi chưa có GV; không làm M3+ khi chưa có GS. Mốc chỉ `done` khi người dùng đã duyệt (Claude tự kiểm xong = `review`).

## 6. Tiêu chí nghiệm thu cuối
- [ ] Compile sạch, test + validator sạch, tự chơi hết level đạt
- [ ] `orch.py check`: bảng nghiệm thu hình không còn dòng chưa đạt, không còn góp ý mở; người dùng đã xem ảnh
- [ ] Danh sách "phải thay trước phát hành" rõ ràng (asset tạm, tên, package id, SDK)

## 7. Rủi ro + điều còn mở
- ...

## Thay đổi
- v1: bản đầu
