# Pipeline /gplay-game: từ ý tưởng tới bản chơi được

**Phiên Claude chính làm trực tiếp**: nghiên cứu, plan, code, chạy Unity, xem ảnh, báo người dùng. Không mặc định mở phiên claude CLI riêng cho từng task
(mỗi phiên riêng phải đọc lại code, không chạy được Unity có GPU, làm đầy danh sách phiên). Việc code lớn tách được → **subagent trong cùng phiên** (tool Agent).
Không dùng git worktree, không chạy task bằng phiên CLI nền.

`O = python "<PLUGIN>/scripts/orch.py"` (chạy ở gốc repo dự án): sổ trạng thái + lịch sử trong `.game/`.

Lệnh người dùng gõ: `start` (intake) · `research` · `plan` · `build` (làm mốc kế) · `status` · `learn`.

## Sơ đồ + cổng duyệt

```
start ─G0→ research ─G1→ plan ─G2→ build M1 "khung hình tĩnh" ─GV→ build M2 "level mẫu chơi được" ─GS→ build M3..Mn → report ─G3→ learn
```
| Cổng | Người dùng duyệt gì | Điều kiện để được hỏi |
|---|---|---|
| G0 | Intake: ý tưởng, nguồn tham khảo, phạm vi | Đã tự xem tài liệu người dùng đưa |
| G1 | Thẻ đối chiếu luật + hình (kèm frame), bảng nghiệm thu hình, các quyết định | Luật lõi không còn `[suy luận]`; có level chuẩn + bảng nghiệm thu đủ cột Mẫu ([research.md](research.md)) |
| G2 | Plan + danh sách mốc | M1 = khung hình tĩnh, M2 = level mẫu chơi được; mỗi mốc có cách kiểm |
| **GV** | **Khung hình tĩnh**: game dựng lại đúng frame đầu của level chuẩn, chưa cần chơi | Mọi dòng `V*` của bảng đã đo; ảnh ghép toàn màn + ảnh crop từng vùng đã đưa người dùng |
| **GS** | **Level mẫu**: chơi đúng luật + chuyển động khớp clip | Mọi dòng `C*` đã đo; video tự chơi + dải frame so clip gốc đã đưa người dùng |
| G3 | Báo cáo bản đầu | Mọi mốc done, danh sách tồn rõ ràng |

Ghi cổng: `O log GV "<lời duyệt nguyên văn>"`. Không tự vượt cổng. **Không làm meta / UI đầy đủ / nội dung hàng loạt trước GS**: luật hoặc hình sai thì mọi thứ sau phải làm lại.

**Vì sao tách GV khỏi GS**: gộp luật + bố cục + art + chuyển động vào 1 cổng thì sai chỗ nào cũng phải làm lại cả vòng, và người dùng chỉ thấy hình sau khi
mọi thứ đã code xong. Khung hình tĩnh rẻ (dựng scene, chưa cần input / animation) nên đưa người dùng xem **sớm nhất có thể**; luật lõi C# + test làm song song (subagent).

**Ai được nói "xong"**: Claude chỉ được đưa mốc sang `review` (`O ms <mốc> review`). `done` là khi người dùng đã duyệt, bảng nghiệm thu của mốc hết dòng chưa đạt
và hết góp ý mở; `orch.py` từ chối `ms done` nếu thiếu 1 trong 3.

Tiếp tục sau khi gián đoạn: `O status` + `O history -n 20` + đọc `.game/plan.md` → làm tiếp bước đang dở.

## Từng bước

**1. Intake** (`/gplay-game:start`): xin tài liệu tham khảo trước, tự xem, thẻ "Mình hiểu như sau", chỉ hỏi mục mơ hồ → `.game/intake.md`, G0.

**2. Nghiên cứu** (`/gplay-game:research`): theo [research.md](research.md). Thu video gameplay (hình: cao ≥ 1080 px) → `study_video.py` → `teardown.md` (luật có bằng chứng)
+ `visual-spec.md` (luồng màn, bố cục theo %, camera, vật thể, chuyển động, UI) + `ref-level.md` (level chuẩn chép từ game gốc) +
`visual-check.md` (bảng nghiệm thu: số đo từng vật thể / sự kiện) + `base.md` (subagent đọc base, song song) → thẻ đối chiếu + câu hỏi → G1.

**3. Plan** (`/gplay-game:plan`): `.game/plan.md` theo `templates/plan.md`. Chia theo **mốc chơi được** (4–7 mốc), không chia task nhỏ:
- M1 luôn là **khung hình tĩnh** (→ GV): nền móng tối thiểu + scene màn chơi dựng từ dữ liệu `ref-level.md`, đứng yên ở trạng thái đầu level,
  chụp đúng tỉ lệ ảnh chuẩn. Chưa cần input, animation, thắng / thua. Song song (subagent): luật lõi C# thuần + test.
- M2 luôn là **level mẫu chơi được** (→ GS): nối luật vào scene, input, chuyển động theo clip, thắng / thua, tự chơi + quay video.
- Sau đó thường: cơ chế phụ → pipeline level + validator / solver → luồng màn (Loading / Home / Game) + UI + meta → nội dung (N level) → localization → phát hành.
- Mỗi dòng của `visual-check.md` gắn với 1 mốc (cột Mốc): hình tĩnh M1, chuyển động M2, UI / màn khác theo mốc làm màn đó.
- Mỗi mốc ghi: kết quả người dùng thấy được, lệnh kiểm, ảnh bằng chứng sẽ có, phần nào giao subagent được.
- Hỏi ở G2 (nếu chưa rõ): dự án chưa có git → đề xuất `git init` cục bộ (để hoàn tác được); ai làm art (mặc định khối đơn giản, art vẽ khi người dùng yêu cầu).

**4. Thực hiện từng mốc** (`/gplay-game:build`):
1. `O ms M2 start "<tiêu đề>"`. Nói trước với người dùng: mốc này làm gì, ước lượng thời gian, khi xong sẽ thấy gì.
2. Làm: phiên chính code trực tiếp. Phần lớn + độc lập (vd logic thuần + test, tool level, 1 màn UI) → subagent với đề rõ: phạm vi file, luật repo,
   lệnh kiểm phải đạt, không chạy Unity. Phiên chính đọc lại diff / chạy lại lệnh kiểm, không tin báo cáo.
3. Kiểm theo [verification.md](verification.md): compile → test logic → validator → **phiên chính chạy Unity** (dựng scene, tự chơi, chụp ảnh) →
   Read ảnh → mốc có hình: ghép toàn màn + **crop từng vùng** với ảnh chuẩn, điền cột Game của **mọi** dòng thuộc mốc trong `visual-check.md`.
4. Còn dòng `lệch` → sửa ngay trong phiên, chụp lại, điền lại cả bảng (sửa 1 chỗ hay làm lệch chỗ khác). Kẹt quá 2 vòng cùng 1 dòng → dừng, báo người dùng kèm ảnh crop.
5. `O ms M2 review --note "<kết quả>" --evidence <ảnh...>` → báo người dùng: đã làm gì, lệnh đã chạy + kết quả, **đường dẫn đầy đủ từng ảnh**
   (ảnh ghép toàn màn + ảnh crop các dòng còn lệch), **bảng các dòng chưa đạt** (chép từ output của lệnh), điều chưa làm, câu hỏi cần quyết.
   Không viết "khớp ảnh chuẩn" khi còn dòng chưa đạt. Mốc có cổng (M1 → GV, M2 → GS) → hỏi cổng; được duyệt → `O log <cổng> "<lời duyệt nguyên văn>"` → `O ms <mốc> done`.
6. Người dùng góp ý → làm theo mục **"Xử lý góp ý"** bên dưới (lưu nguyên văn trước, sửa spec, rồi mới sửa code).

**Giao subagent** (khi 1 mốc có ≥ 2 phần độc lập, mỗi phần đủ lớn): gọi các subagent trong **cùng 1 lượt** để chạy song song, tối đa 3.
Đề cho mỗi subagent phải tự đủ (nó không thấy hội thoại):
- mục tiêu + tiêu chí xong; file nên đọc (AGENTS.md, game-profile, mục liên quan của teardown / plan);
- **vùng file được sửa, không chồng nhau giữa các subagent** (vd A: `Scripts/Core/**` + test; B: `Tools/LevelTool/**`); file chung (asmdef, csproj, scene) do phiên chính sửa;
- lệnh kiểm phải chạy đạt (test logic, build offline); KHÔNG chạy Unity, không commit; luật chung trong `RULES.md` của plugin;
- báo lại: file đã đổi, lệnh đã chạy + kết quả, điều chưa làm.
Xong: phiên chính đọc diff / file, chạy lại lệnh kiểm + compile Unity 1 lần cho tất cả, rồi mới sang bước có hình.
Không giao subagent: việc phải nhìn (hình, UI, feel), việc sửa chung file, việc nhỏ hơn công viết đề.

**Xử lý góp ý** (mọi lần người dùng chê / sửa, kể cả 1 câu):
1. `O fb add --ms <mốc> "<nguyên văn>" [--attach <ảnh người dùng gửi>]` (dài / nhiều dòng: `--file` hoặc stdin). **Không tóm tắt, không dịch, không gộp**:
   bản tóm tắt làm mất các ý chưa kịp làm. Người dùng gửi cả một spec nhiều mục → lưu nguyên cả spec.
2. Mở `.game/feedback/NN.md`, điền bảng "Tách mục": mỗi ý 1 dòng: trích nguyên văn → "tôi hiểu là" → dòng bảng nghiệm thu / spec sẽ sửa.
3. Ý có ≥ 2 cách hiểu, hoặc cách hiểu sẽ thành **quy tắc chung** thay vì 1 con số (vd "to quá" → "luôn rộng N %"?) → `hỏi lại` bằng AskUserQuestion
   kèm ảnh crop 2 phương án, **trước** khi sửa. Đoán sai ở đây = vòng sau người dùng chê điều ngược lại.
4. Góp ý về một thứ mà bảng nghiệm thu đang ghi `đạt`, hoặc chưa có dòng nào → bảng đo sai / thiếu: sửa cột Mẫu hoặc thêm dòng, rồi **soát lại cả vùng ảnh đó**
   (crop vùng, liệt kê mọi thứ thấy được) vì chỗ sót hiếm khi đứng một mình.
5. Sửa code → chụp → điền lại **cả** cột Game của mốc (không chỉ các dòng vừa sửa) → cập nhật trạng thái từng mục trong file góp ý (`xong` kèm ảnh crop) → `O ms <mốc> review`.
6. Cùng 1 cổng bị trả về **lần 2** vì cùng loại (hình, chuyển động, luật) → dừng sửa code: `/gplay-game:research` nghiên cứu lại loại đó cho cả màn
   (nguồn nét hơn, soát theo vùng), trình bảng mới cho người dùng rồi mới build tiếp; ghi `/gplay-game:learn` vì sao lần nghiên cứu đầu sót.

**5. Art** (chỉ khi người dùng yêu cầu): [art-on-demand.md](art-on-demand.md): brief → Codex / Gemini vẽ → kiểm kích thước → đưa vào game.

**6. Báo cáo**: `O phase report` · `O report` → `.game/REPORT.md` (mốc, thời gian, ảnh, cổng, góp ý, còn tồn) → trình người dùng, hỏi G3.

**7. Rút bài học** (`/gplay-game:learn`): bài học chung → `LEARNINGS.md` của plugin; riêng dự án → `AGENTS.md` / game-profile. Ghi **ngay khi gặp**, không đợi cuối.

## File trong `.game/`

| File | Nội dung |
|---|---|
| `intake.md` · `questions.md` · `plan.md` | Đầu vào, quyết định, kế hoạch theo mốc |
| `research/teardown.md` · `visual-spec.md` · `base.md` | Kết quả nghiên cứu (nguồn sự thật về luật + hình) |
| `research/ref-level.md` | Level chuẩn chép từ game gốc: dữ liệu để dựng level mẫu + ảnh chuẩn 3 thời điểm |
| `research/visual-check.md` | Bảng nghiệm thu hình: số đo Mẫu / Game từng vật thể, sự kiện; `O check` đếm |
| `feedback/NN.md` | Góp ý của người dùng **nguyên văn** + bảng tách mục, trạng thái từng mục |
| `state.json` | Giai đoạn, mốc (thời gian, file đổi, ảnh) |
| `HISTORY.md` · `history.jsonl` | Nhật ký: cổng duyệt, mốc, góp ý (FB: trỏ tới file nguyên văn), ghi chú (NOTE), bài học (LEARN) |
| `milestones/<mốc>-files.txt` | File đã đổi trong mốc (không git: theo thời điểm sửa) |
| `art/<tên>/` | Brief + kết quả art theo yêu cầu |
| `REPORT.md` | Báo cáo, sinh lại mỗi lần chốt mốc |

Ảnh / video / build để ở ổ tạm ngoài repo; `.game/` chỉ giữ đường dẫn.

## Luật của phiên chính

- Không bỏ cổng duyệt; không lập plan khi luật lõi còn `[suy luận]` hoặc chưa có bảng nghiệm thu; không làm quá M1 khi chưa có GV, quá M2 khi chưa có GS.
- Tự kiểm xong thì báo "chờ duyệt" (`ms review`), không báo "xong". Mỗi lần báo phải có: lệnh đã chạy + kết quả, đường dẫn ảnh đã XEM,
  **các dòng bảng nghiệm thu chưa đạt**, điều chưa làm. "Khớp / giống mẫu" chỉ được viết khi `O check --ms <mốc>` không còn dòng chưa đạt.
- Góp ý của người dùng lưu nguyên văn (`O fb add`) trước khi làm bất cứ gì; diễn giải của Claude ghi riêng ở cột "Tôi hiểu là".
- Level mẫu dựng từ `ref-level.md` (level của game gốc), không tự nghĩ level khác để so với ảnh chuẩn.
- Ước lượng thời gian khi bắt đầu mốc; mốc dài > 30 phút thì báo tiến độ giữa chừng.
- Lệnh bị từ chối quyền → không gọi vòng; nói với người dùng lệnh cần chạy.
- Không sửa test cho xanh; không gọi lỗi là "có sẵn" rồi bỏ qua.
- Commit chỉ khi người dùng đã đồng ý (hỏi ở G2: commit sau mỗi mốc trên nhánh `game/<slug>`).
