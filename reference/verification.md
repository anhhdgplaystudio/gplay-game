# Kiểm tra

## Thang kiểm tra (rẻ → đắt, dừng ở bậc đủ chứng minh)

| Bậc | Cách | Bắt được |
|---|---|---|
| 1. Build offline | `dotnet build Assembly-CSharp-Editor.csproj -nologo -v q` (~5 s) | Lỗi C# |
| 2. Validator dữ liệu | Script đọc file level / layout / key, so với art + atlas + bảng text | Tên sai, vùng chồng, thiếu key, thứ tự lớp sai |
| 3. Ảnh dựng ngoài Unity | `scripts/compose_dev.py`, preview layout, vẽ vùng thả / bong bóng lên ảnh | Sai vị trí, che mặt, lệch demo |
| 4. Test Unity | EditMode / PlayMode (`-runTests -testPlatform EditMode -testResults <xml>`) | Logic thắng / thua, tiến trình, serialize |
| 5. Tự chơi batchmode | Dựng lại từ nguồn → vào Gameplay → gọi hàm tự giải → chụp ảnh mỗi bước | Level không giải được, kẹt, hiện sai |
| 6. So với ảnh chuẩn | `scripts/side_by_side.py <ảnh chuẩn> <ảnh game> <ra.jpg> --grid 10` rồi Read | Sai bố cục / tỉ lệ / hướng / thiếu vật thể so với game tham khảo |
| 7. Người chơi thử | Agent ghi các bước tái hiện, người dùng kiểm cảm giác / art | Feel, độ khó, UX |

Bậc 1 thay bằng lệnh compile của dự án khi dùng asmdef riêng (ghi trong game-profile). Bậc 5–6 do **phiên chính** chạy: subagent / worker CLI không có quyền chạy Unity có GPU.

Luật:
- **Báo kết quả có hình luôn kèm đường dẫn đầy đủ tới từng ảnh** (người dùng bấm mở được), không chỉ mô tả.
- Không nói "giống mẫu" khi chưa ghép ảnh so; nói thẳng điểm còn khác.
- **Không gọi lỗi là "có sẵn từ trước" rồi bỏ qua**: sửa hoặc báo kèm output.
- Test chỉ chép lại code không tính; test phải fail khi hành vi hỏng.
- Kiểm "mọi tên tồn tại" **chưa đủ**: phải xem ảnh.
- Đổi tên / xoá symbol: grep toàn `Assets` (kể cả string trong json, `-executeMethod`).

## Tự chơi batchmode (mẫu nên có từ dự án đầu)

Mỗi cơ chế cung cấp **hàm tự giải** dùng chính đường input của game (hàm thả / bấm thật, không set trạng thái tắt).
Tool test (editor script, gọi qua `-executeMethod`):
1. Đọc tham số `-levels 3,7 -out <thư mục> [-nobuild]`.
2. (Tuỳ) dựng lại prefab từ nguồn.
3. Mở GameplayScene, vào Play (`EditorApplication.isPlaying = true` + `EditorApplication.update` để chạy tuần tự).
4. Với từng bước: chụp trước / sau (`ScreenCapture.CaptureScreenshot` hoặc render camera → PNG), log `ĐÚNG / KHÔNG thả được`.
5. Ghi `report.txt`, thoát với mã ≠ 0 khi có bước hỏng.

```
Unity -batchmode -projectPath . -executeMethod <Ns>.PlayTest.RunFromCommandLine -levels 3,7 -out D:/tmp/playtest -logFile D:/tmp/playtest/unity.log
```
Batchmode không `-nographics` nếu cần chụp ảnh.

**Xem hết ảnh trước khi báo xong.** So với frame video / demo của level.

Tool tự chơi nên làm thêm (rẻ, bắt được lỗi người dùng hay chê):
- Chụp đúng tỉ lệ khung của ảnh chuẩn (vd 1080×1920 / 1080×2340) để ghép so được; chụp cả các màn ngoài gameplay (loading, home, popup thắng / thua).
- **Kiểm méo UI**: duyệt mọi `Image` không Sliced / Tiled, lỗi khi tỉ lệ rect lệch tỉ lệ sprite > 2%; in số lượng vào log.
- **Kiểm glyph**: chạy từng ngôn ngữ, lỗi khi TMP báo thiếu ký tự hoặc dùng font dự phòng; kiểm chữ tràn khung (`isTextOverflowing`).
- Tham số `-fresh` (hồ sơ người chơi mới) để tutorial / mở khoá hiện đúng như người chơi thật; HUD phải lấy số level đang chơi, không lấy từ hồ sơ.

## So với ảnh chuẩn (mốc nào có hình cũng làm)

1. Ảnh chuẩn từng màn nằm ở visual-spec (`<tmp>/ref/golden/`). Chụp game cùng trạng thái (giữa level, cùng màn).
2. `side_by_side.py <chuẩn> <game> <tmp>/cmp_<mốc>.jpg --grid 10` → Read ảnh ghép. Script cảnh báo khi tỉ lệ khung lệch.
3. Soát danh sách so (visual-spec mục 9): bố cục theo % · hướng + camera · vật thể đủ, đúng hình dáng · nền · UI. Chuyển động: chụp chuỗi ảnh giữa hành động, so với clip.
4. Ghi điểm còn khác vào báo cáo mốc (khác có chủ ý → ghi ở visual-spec mục 8).

## Ngưỡng độ khó (cơ chế có solver / mô phỏng)

"Giải được" chưa đủ. Validator level báo thêm, và level bản đầu phải nằm trong ngưỡng ghi ở plan:
- tỉ lệ thắng khi **chơi ngẫu nhiên** (N lần, seed cố định): level sau tutorial không được = 100%;
- số nước của lời giải ngắn nhất / số lựa chọn mỗi bước; nhịp khó tăng dần theo số thứ tự level.
Không đạt mà không sửa được bằng dữ liệu → vấn đề ở luật / cơ chế tạo khó: báo người dùng quyết, không lặng lẽ nhận.

## Khi Editor đang mở

Unity 6 có Unity CLI / `unity-pipeline` (skill chính chủ: `npx skills add Unity-Technologies/skills`): recompile, `console get --level error`,
`test run`, `capture game_view`, `script run --file <builder> --entry Class.Method`. Dùng khi người dùng không muốn đóng Editor.
Lệnh treo → kiểm hộp thoại modal (`editor status`), báo người dùng.

## Báo cáo cuối

Lệnh đã chạy · file đổi · kết quả từng bậc kiểm · đường dẫn đầy đủ từng ảnh (ảnh ghép so đặt đầu) · việc chưa làm (vd cần mở Unity dựng prefab) ·
tác dụng phụ còn lại (Play Mode, file tạm, prefab bị dựng lại, log debug tạm) · điểm khôi phục (commit / stash).
