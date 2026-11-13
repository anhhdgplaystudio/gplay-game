# Bộ tự chơi dùng chung (GPlayTestKit) + quay video

Mỗi dự án không phải viết lại phần chụp ảnh / kiểm UI / quay video / chạy Unity: chép kit, viết **1 class driver** chơi game của mình.

## Cài vào dự án (mốc M1)

1. Chép `<PLUGIN>/templates/unity/GPlayTestKit/` → `Assets/<thư mục tool>/GPlayTestKit/` (asmdef `GPlay.TestKit.Editor`, chỉ Editor, cần `com.unity.ugui` có TextMeshPro).
2. Chép `<PLUGIN>/templates/unity/SampleDriver.cs.txt` → 1 thư mục Editor của dự án, đổi tên `<Game>PlayTestDriver.cs`, sửa phần `TODO`:
   - `Prepare`: mở scene bắt đầu (edit mode, trước Play); cờ `-fresh` thì xoá save để chơi như người mới.
   - `Run`: coroutine chơi qua **đường input thật** của game (hàm mà chạm / kéo gọi), chụp ảnh các mốc, `ctx.UiCheck(...)` ở mỗi màn, `ctx.Result(level, won)`.
   - Driver nằm trong assembly Editor của dự án, tham chiếu `GPlay.TestKit.Editor` + assembly game.
3. Chạy (Unity Editor của dự án phải đóng; Unity Hub mở để có license):
   ```
   python "<PLUGIN>/scripts/unity_run.py" playtest --levels 1-3 --out D:/tmp/playtest_m1 [--size 1080x1920] [--video] [-- -fresh -lang vi]
   ```
   In bảng thắng / thua, tổng kiểm UI, **đường dẫn đầy đủ từng ảnh**, video `.mp4`; exit 0 = đạt.
   Cờ sau `--` đi thẳng vào Unity (driver đọc bằng `ctx.Flag` / `ctx.Arg`).

`unity_run.py` còn có: `compile` (biên dịch, in `error CS`), `exec <Class.Method>` (chạy editor script: dựng scene, import...), `video <thư mục khung>`.
Nó tự tìm Unity đúng phiên bản theo `ProjectVersion.txt`, dừng nếu Editor đang mở project, báo rõ khi thiếu license,
quá giờ thì **chỉ tắt tiến trình Unity nó tự mở**.

## API trong driver (`GPlayTestContext ctx`)

| Gọi | Làm gì |
|---|---|
| `yield return null` / `ctx.Wait(s)` / `AsyncOperation` / `IEnumerator` | Chờ 1 khung / s giây game / nạp scene / routine con |
| `ctx.Shot("ten")` | PNG camera + UI (canvas Overlay được dựng lại đúng cỡ `-size`) → trả đường dẫn |
| `ctx.BeginVideo("ten", 30)` … `ctx.EndVideo()` | Quay mọi khung giữa 2 lệnh; game tiến đúng 1/30 s mỗi khung (`Time.captureFramerate`) nên chuyển động khớp thời gian thật; ra `video_ten.mp4` |
| `ctx.UiCheck("nhãn")` | Ảnh méo (lệch tỉ lệ > 2 % / scale lệch), chữ tràn khung, thiếu glyph trong font, chữ rơi về font dự phòng |
| `ctx.Result(level, won, ghiChú)` · `ctx.Expect(đk, "lỗi")` · `ctx.Fail("lỗi")` | Kết quả level / điều kiện phải đúng |
| `GPlayTestContext.Click(go)` | Bấm nút UI như ngón tay (pointer down / up / click) |
| `ctx.Levels`, `ctx.Flag("-x")`, `ctx.Arg("-x", mặcĐịnh)` | Tham số dòng lệnh |

Kết quả `report.json` (trong `--out`): level, ảnh, video, tổng kiểm UI, lỗi log. Run **trượt** khi: level thua, `Expect` sai, exception, có lỗi log của game
(lỗi nội bộ Editor được lọc), hoặc kiểm UI có vấn đề (bỏ qua bằng cờ `-allow-ui` / `-allow-errors` khi đang sửa dần).
Mặc định chạy trong **Play mode** thật; game tự tick được ở edit mode thì thêm `--editmode` (nhanh hơn, không quay video tự động, driver tự gọi `ctx.Frame()`).

## Quay video để so chuyển động

- Chỉ quay đoạn cần so (1 thao tác, xe vào / ra, thắng), 2–5 s: 30 khung/s × 960 px mỗi giây ~1–2 MB ảnh.
- So với clip game gốc: `study_video.py <video_game.mp4> <thư mục> --clip 0 3` và cùng lệnh với clip gốc → Read 2 `strip.jpg` đặt cạnh nhau
  (cùng số khung / giây): đường đi, thứ tự, thời lượng phải khớp visual-spec mục 5.

## Lỗi hay gặp

- Chạy với `-nographics` → không có ảnh / video (kit cảnh báo `no GPU`). `unity_run.py playtest` không thêm cờ này.
- Font TMP tạo lúc runtime / object tạo ở `Prepare` mà không lưu scene sẽ **mất khi vào Play** (domain reload): dựng nội dung trong scene đã lưu, hoặc tạo trong `Run`.
- Dự án chưa import **TMP Essential Resources** → chữ không hiện, kiểm chữ đếm 0. Import 1 lần (`unity_run.py exec` gọi `AssetDatabase.ImportPackage`).
- Canvas `Screen Space - Overlay` không vẽ vào RenderTexture: kit tạm đổi sang `Screen Space - Camera` lúc chụp rồi trả lại; canvas World Space giữ nguyên.
- Scaler `Scale With Screen Size` đọc kích thước camera → ảnh chụp ở `-size` khác màn thật thì bố cục theo `-size` (đúng ý: chụp đúng tỉ lệ ảnh chuẩn).

## Đã kiểm (dự án Unity 6000.3 trống, 2026-11)

Ảnh chụp có UI ✓ · bắt ảnh méo 300 % ✓ · bắt chữ VI tràn khung ✓ · bắt thiếu glyph CJK ✓ · không báo nhầm chữ VI đủ dấu ✓ ·
video 30 khung, vật đi đúng 2,00 đơn vị / 1 s game ✓ · lọc lỗi nội bộ Editor (search index) ✓ · ~15 s / lần chạy.
