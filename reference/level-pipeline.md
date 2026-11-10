# Pipeline level dữ liệu

Mục tiêu: art xuất 1 lần → importer dựng level → validator + tự chơi kiểm. Thêm level = thêm dữ liệu, không thêm code (trừ diễn biến riêng).

## 1. Định dạng art xuất (thư mục `dev/`)

Định dạng chuẩn studio, dùng cho mọi thể loại:

- `<tên layer>.png`: nội dung cắt sát, **kích thước làm tròn lên bội số 4** (nén ETC2 / ASTC), gốc trên-trái.
- `<tên layer>.cor`: 1 dòng `x y` = góc trên-trái layer trên canvas PSD (gốc trên-trái, y xuống).
- Nhóm PSD → thư mục con cùng tên.
- `mapping.json`: cây layer **trên cùng trước** `[{ "name", "isGroup", "children"?, "visible"? }]`. Importer lấy thứ tự lớp từ đây.
- Canvas chuẩn dọc **1080×1920**; quy đổi 100 px = 1 unit.

Công cụ xuất: plugin Photoshop / trang web đọc PSD (ag-psd) xuất ZIP đúng định dạng trên. Hiệu ứng layer (đổ bóng, viền) phải rasterize trước.
Kiểm: `python scripts/check_dev.py <dev>`; xem: `python scripts/compose_dev.py <dev> out.png`.

**Quy ước tên layer** theo vai trò trong cơ chế (vd `bg1`, `item1.2`, `outline1.2`, `fake1`, `ui`): viết vào file quy ước của dự án,
gửi art **trước khi** họ làm PSD. Layer tham khảo (`ui`, `khung`, `thumb`, `background`...) importer bỏ qua.
Art không theo quy ước → script sinh thư mục `dev_lv/` đặt lại tên (+ `names.json` map tên Spine → layer). **Không** sửa importer cho 1 level.

Thư mục level nên có: `demo/` (ảnh / video mẫu), `dev/` (xuất PSD), `dev_lv/` (nếu cần), file level json.

## 2. File level (json cạnh art)

```json
{ "prompt": "<key text>", "timeLimit": 180, "coinReward": 10,
  "...": "trường riêng cơ chế (xem mechanics.md)",
  "controller": "", "hidden": [], "orders": [] }
```
- Text trong json là **key localization**, không ghi câu thật (`s_lvN_prompt`, `s_lvN_stepI`...).
- Tạo độ: theo canvas PSD (px), importer quy đổi.
- Mỗi trường mới trong json → validator kiểm nó.

## 3. Importer (editor window + hàm batch)

- Đầu vào: thư mục level. Đầu ra: `Levels/Level_XXX.prefab` (XXX 3 chữ số).
- Có nút **Xem trước** (liệt kê đối tượng + cảnh báo) trước nút **Dựng**.
- **Ghi đè prefab đã có: mặc định tắt.**
- Thứ tự vẽ = `sortingOrder` theo mapping (mỗi layer +2 để chèn được), không theo Hierarchy.
- Gom object vào nhóm (Scene / Characters / DragItems / Targets / UI...).
- Gắn `LevelController<N>` nếu có class trùng số level (hoặc `controller` trong json).
- Có hàm static gọi được qua `-executeMethod` để tool tự chơi dựng lại.

## 4. Database level

- ScriptableObject trong `Resources` liệt kê prefab, menu **Refresh** quét `Levels/Level_*.prefab`.
- **Số màn trong game = vị trí trong database**, không phải số trong tên file. Thiếu 1 prefab → mọi màn sau lệch 1.
  Hoặc lưu `levelId` riêng, hoặc refresh luôn báo lỗ hổng.
- Level có thể đánh dấu khó (thưởng x3), bỏ qua quảng cáo...

## 5. Controller riêng từng level

`LevelControllerN : <Mode>LevelController` override các hook (`OnStepDone`, `OnAllDone`, `CanAccept`, `SayStepLine`...).
Base chỉ có hook rỗng + hành vi mặc định. Thua theo kịch bản: gọi `Host.Lose()`. Hiện lại vật có từ đầu: `Reveal` trong controller.

## 6. Validator (viết ngay khi chốt định dạng)

Kiểm ít nhất:
- Mọi tên trong json tồn tại (layer trong dev / dev_lv, region trong atlas Spine, skin / animation trong skeleton).
- Vùng thả không phủ cả cảnh, không chồng nhau (trừ đích mở khoá tuần tự cùng chỗ).
- Mọi key text có trong bảng localization.
- `mapping.json` không sắp theo tên (so với thứ tự PSD).
- Vật trong `show` của bước sau không bị ẩn sai từ đầu.
In lỗi rõ: `steps[2].accept "money" không có trong drags. Có: coin, card`.
