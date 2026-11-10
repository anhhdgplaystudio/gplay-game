# Kiểm tra

## Thang kiểm tra (rẻ → đắt, dừng ở bậc đủ chứng minh)

| Bậc | Cách | Bắt được |
|---|---|---|
| 1. Build offline | `dotnet build Assembly-CSharp-Editor.csproj -nologo -v q` (~5 s) | Lỗi C# |
| 2. Validator dữ liệu | Script đọc file level / layout / key, so với art + atlas + bảng text | Tên sai, vùng chồng, thiếu key, thứ tự lớp sai |
| 3. Ảnh dựng ngoài Unity | `scripts/compose_dev.py`, preview layout, vẽ vùng thả / bong bóng lên ảnh | Sai vị trí, che mặt, lệch demo |
| 4. Test Unity | EditMode / PlayMode (`-runTests -testPlatform EditMode -testResults <xml>`) | Logic thắng / thua, tiến trình, serialize |
| 5. Tự chơi batchmode | Dựng lại từ nguồn → vào Gameplay → gọi hàm tự giải → chụp ảnh mỗi bước | Level không giải được, kẹt, hiện sai |
| 6. Người chơi thử | Agent ghi các bước tái hiện, người dùng kiểm cảm giác / art | Feel, độ khó, UX |

Luật:
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

## Khi Editor đang mở

Unity 6 có Unity CLI / `unity-pipeline` (skill chính chủ: `npx skills add Unity-Technologies/skills`): recompile, `console get --level error`,
`test run`, `capture game_view`, `script run --file <builder> --entry Class.Method`. Dùng khi người dùng không muốn đóng Editor.
Lệnh treo → kiểm hộp thoại modal (`editor status`), báo người dùng.

## Báo cáo cuối

Lệnh đã chạy · file đổi · kết quả từng bậc kiểm · việc chưa làm (vd cần mở Unity dựng prefab) ·
tác dụng phụ còn lại (Play Mode, file tạm, prefab bị dựng lại, log debug tạm) · điểm khôi phục (commit / stash).
