# Kiểm tra

## Thang kiểm tra (rẻ → đắt, dừng ở bậc đủ chứng minh)

| Bậc | Cách | Bắt được |
|---|---|---|
| 1. Build offline | `dotnet build Assembly-CSharp-Editor.csproj -nologo -v q` (~5 s) | Lỗi C# |
| 2. Validator dữ liệu | Script đọc file level / layout / key, so với art + atlas + bảng text | Tên sai, vùng chồng, thiếu key, thứ tự lớp sai |
| 3. Ảnh dựng ngoài Unity | `scripts/compose_dev.py`, preview layout, vẽ vùng thả / bong bóng lên ảnh | Sai vị trí, che mặt, lệch demo |
| 4. Test Unity | EditMode / PlayMode (`-runTests -testPlatform EditMode -testResults <xml>`) | Logic thắng / thua, tiến trình, serialize |
| 5. Tự chơi batchmode | Dựng lại từ nguồn → vào Gameplay → gọi hàm tự giải → chụp ảnh mỗi bước | Level không giải được, kẹt, hiện sai |
| 6. So với ảnh chuẩn | `scripts/side_by_side.py` toàn màn (`--grid 10`) + **crop từng vùng** (`--crop`), điền `visual-check.md`, `orch.py check` | Sai bố cục / tỉ lệ / hướng / thiếu vật thể; lệch chi tiết (viền, khe, bo góc, cỡ từng vật) |
| 7. Người chơi thử | Agent ghi các bước tái hiện, người dùng kiểm cảm giác / art | Feel, độ khó, UX |

Bậc 1 thay bằng lệnh compile của dự án khi dùng asmdef riêng (ghi trong game-profile). Bậc 5–6 do **phiên chính** chạy: subagent không có quyền chạy Unity có GPU.

Luật:
- **Báo kết quả có hình luôn kèm đường dẫn đầy đủ tới từng ảnh** (người dùng bấm mở được), không chỉ mô tả.
- Không nói "giống mẫu" / "khớp" khi `orch.py check --ms <mốc>` còn dòng chưa đạt; chép nguyên các dòng đó vào báo cáo.
- Claude tự kiểm xong = `review` (chờ duyệt). `done` = người dùng đã duyệt. Không ghi "Còn tồn: không" khi người dùng chưa xem.
- Ảnh ghép toàn màn chỉ bắt được sai lớn (bố cục, thiếu vật). Chi tiết phải so bằng ảnh crop cùng vùng: 2 ảnh "trông giống nhau" ở cỡ thu nhỏ
  vẫn lệch vị trí từng vật, độ dày viền, khe giữa các khối.
- So phải cùng nội dung: game chụp **level chuẩn** (`ref-level.md`), cùng trạng thái, cùng tỉ lệ khung với ảnh chuẩn.
- **Không gọi lỗi là "có sẵn từ trước" rồi bỏ qua**: sửa hoặc báo kèm output.
- Test chỉ chép lại code không tính; test phải fail khi hành vi hỏng.
- Kiểm "mọi tên tồn tại" **chưa đủ**: phải xem ảnh.
- Đổi tên / xoá symbol: grep toàn `Assets` (kể cả string trong json, `-executeMethod`).

## Tự chơi batchmode

**Dùng bộ kit có sẵn**: [autoplay-kit.md](autoplay-kit.md) (`templates/unity/GPlayTestKit` + `scripts/unity_run.py playtest`): chụp ảnh đúng cỡ,
kiểm méo UI / chữ tràn / thiếu glyph, quay video, `report.json`. Dự án chỉ viết 1 driver. Editor đang mở → [unity-mcp.md](unity-mcp.md).
Phần dưới là nguyên lý (khi phải tự viết).

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

1. Ảnh chuẩn từng màn nằm ở visual-spec (`<tmp>/ref/golden/`). Game dựng level chuẩn (`ref-level.md`), chụp cùng trạng thái + cùng tỉ lệ khung.
2. Toàn màn: `side_by_side.py <chuẩn> <game> <tmp>/cmp_<mốc>.jpg --grid 10` → Read. Script cảnh báo khi tỉ lệ khung lệch.
3. Từng dòng của `.game/research/visual-check.md` thuộc mốc: `side_by_side.py <chuẩn> <game> <tmp>/check/<mã>.jpg --crop x0,y0,x1,y1 [--grid 25]` → Read →
   điền cột Game (số đo), cột ảnh crop, kết quả `đạt` / `lệch: <lệch gì>`. Ngưỡng ở đầu bảng (vị trí + cỡ ≤ 2 % bề ngang, màu ΔRGB ≤ 20).
4. Chuyển động: quay video tự chơi, `study_video.py --clip` video gốc và video game cùng `--fps`, đặt 2 dải frame cạnh nhau; đo thời lượng bằng số frame, so đường đi + đội hình.
5. Sửa xong 1 dòng → đo lại **cả** bảng của mốc (đổi camera / cỡ 1 vật làm lệch dòng khác).
6. `orch.py check --ms <mốc>`: các dòng chưa đạt đi nguyên vào báo cáo mốc. Khác có chủ ý → kết quả `chủ ý` + ghi ở visual-spec mục 8, phải được người dùng đồng ý.

## Ngưỡng độ khó (cơ chế có solver / mô phỏng)

"Giải được" chưa đủ. Validator level báo thêm, và level bản đầu phải nằm trong ngưỡng ghi ở plan:
- tỉ lệ thắng khi **chơi ngẫu nhiên** (N lần, seed cố định): level sau tutorial không được = 100%;
- số nước của lời giải ngắn nhất / số lựa chọn mỗi bước; nhịp khó tăng dần theo số thứ tự level.
Không đạt mà không sửa được bằng dữ liệu → vấn đề ở luật / cơ chế tạo khó: báo người dùng quyết, không lặng lẽ nhận.

## Khi Editor đang mở

Dùng unity-mcp ([unity-mcp.md](unity-mcp.md)): chụp Game View, Play / Stop, đọc console, chạy C#, gọi menu dựng scene.
Không chạy batchmode trên project đang mở. Lệnh treo → kiểm hộp thoại modal trong Editor, báo người dùng.

## Báo cáo cuối

Lệnh đã chạy · file đổi · kết quả từng bậc kiểm · đường dẫn đầy đủ từng ảnh (ảnh ghép so đặt đầu) · việc chưa làm (vd cần mở Unity dựng prefab) ·
tác dụng phụ còn lại (Play Mode, file tạm, prefab bị dựng lại, log debug tạm) · điểm khôi phục (commit / stash).
