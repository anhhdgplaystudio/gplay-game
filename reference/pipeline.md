# Pipeline /gplay-game: từ ý tưởng tới báo cáo

Phiên Claude chính = **orchestrator**: nói chuyện với người dùng, viết câu hỏi / plan / đề task, gọi `orch.py`, đọc báo cáo.
**Mọi task (nghiên cứu, đọc base, code, sửa bug, review) chạy bằng claude CLI qua `orch.py run`**. Orchestrator không tự sửa code game.

`O = python "<PLUGIN>/scripts/orch.py"` (chạy ở gốc repo dự án; `<PLUGIN>` = thư mục plugin gplay-game, các lệnh `/gplay-game:*` in sẵn đường dẫn thật).

Lệnh người dùng gõ: `start` (bước 1) · `continue` (vào lại bất kỳ bước nào) · `plan` (4–5) · `split` (6) · `run` (7–8) · `fix` · `test` (9) · `report` (10) · `add-rule` · `history` · `config` · `status` · `help`.

## Mục lục
- Sơ đồ + cổng duyệt
- Từng bước
- Định dạng file task
- Truy vết + báo cáo
- Luật orchestrator

## Sơ đồ

```
/gplay-game:start → 1 Intake ─G0→ 2 Nghiên cứu ∥ Đọc base → 3 Câu hỏi + đề xuất ─G1→ 4 Plan v1..vN ─G2→
5 Chia task → 6 [chạy task → test đơn → (review) → gộp] × N → 7 Test tích hợp → 8 Sửa bug (lặp ≤ 2)
→ 9 Báo cáo ─G3→ 10 Rút bài học
```
Cổng (người dùng duyệt, ghi `O log G<n> "<quyết định>"`):
- **G0** intake đủ để nghiên cứu · **G1** câu hỏi đã trả lời · **G2** plan chốt (kèm đồng ý cho pipeline commit trên nhánh `game/*`) ·
  **G3** nhận báo cáo, quyết định gộp `game/<slug>` vào nhánh chính (người dùng tự gộp hoặc cho phép).

Tiếp tục sau khi gián đoạn: `O status` → đọc `.game/state.json` (phase) + `.game/HISTORY.md` (20 dòng cuối) → làm tiếp bước đó.

## Từng bước

**1. Intake.** `O init --slug <tên>` → đưa người dùng file `.game/intake.md` (ý tưởng, link game tham khảo, ảnh, video, mô tả,
phạm vi bản đầu, base, SDK, ngôn ngữ). Người dùng điền (hoặc dán vào chat, orchestrator ghi vào file).
Kiểm đủ: thiếu mục bắt buộc (cơ chế, tham khảo, base) → hỏi lại. `O log G0 "intake đủ"` · `O phase research`.

**2. Nghiên cứu ∥ Đọc base.** Viết 2 task (mẫu `templates/tasks/`), chạy song song (chỉ đọc):
- `R1` nghiên cứu: game tham khảo (store, video, bài phân tích), cơ chế, vòng meta, monetization, điểm khác biệt, rủi ro.
  Video: worker không xem được video; nếu cần, orchestrator trích frame trước (`ffmpeg -i v.mp4 -vf fps=1/3 frames/%03d.png`, ra ổ tạm) rồi đưa đường dẫn.
- `R2` đọc base: cấu trúc repo, framework tái dùng được, gameplay cũ cần xoá, tàn dư identity / keystore, tool sẵn có, rủi ro kỹ thuật.
`O run R1 R2 --parallel` → đọc `.game/research/R1.md`, `R2.md`.

**3. Câu hỏi + đề xuất.** Orchestrator tổng hợp vào `.game/questions.md`: câu hỏi cần người dùng quyết (mỗi câu 2–4 phương án,
đánh dấu khuyến nghị), đề xuất của Claude, rủi ro. Hỏi người dùng (AskUserQuestion cho câu chọn được). Ghi câu trả lời vào file.
`O log G1 "<tóm tắt quyết định>"` · `O phase plan`.

**4. Plan.** `.game/plan.md` (mẫu `templates/plan.md`): mục tiêu bản đầu, ngoài phạm vi, kiến trúc, cơ chế, pipeline level, các mốc,
danh sách task dự kiến, tiêu chí nghiệm thu, rủi ro. Sửa theo góp ý → tăng phiên bản (`v2`, ghi thay đổi ở cuối file).
Chốt: `O log G2 "plan vN chốt; đồng ý commit trên game/*"` · `O branch` · `O phase tasks`.

**5. Chia task.** Mỗi task 1 file `.game/tasks/T<nn>-<tên>.md` (định dạng dưới). Luật chia:
- 1 task = 1 phiên claude làm xong (≈ 30–60 phút, < 10 file); tiêu chí nghiệm thu kiểm được bằng lệnh.
- `scope` hẹp, task nối tiếp không sửa chung file nếu tránh được (giảm xung đột gộp).
- Task cần Unity batchmode (dựng prefab, tự chơi) ghi `unity: true`; Unity phải đóng; luôn chạy một mình ở repo chính.
- Thứ tự: nền móng (base, dữ liệu) → cơ chế → pipeline level → UI → nội dung.
- **Chia để chạy song song được**: các task cùng tầng (không phụ thuộc nhau) có `scope` tách biệt (thư mục khác nhau);
  ghi độ nặng `weight: 1|2|3` (hoặc `size: S|M|L`) cho task chắc chắn nhẹ / nặng.
Cho người dùng xem danh sách task (bảng id / tiêu đề / phụ thuộc / độ nặng) trước khi chạy.

**6. Thực hiện: claude chạy song song theo độ nặng, test đơn luồng.**
`O run T01 T02 T03 T04 --parallel --merge` (mặc định cho cả lượt task; `--parallel 2` để giới hạn phiên). Orch lập lịch:
- **Độ nặng mỗi task**: `weight` / `size` nếu có; không thì tự ước lượng 1–3 (+1 nếu model opus / effort cao, +1 nếu budget ≥ 5 USD,
  +1 nếu scope > 40 file). Research / review = 1. `unity: true` = chiếm hết sức chứa (chạy một mình).
- **Sức chứa**: tối đa `max_parallel` phiên (mặc định 3) VÀ tổng độ nặng ≤ `max_load` (mặc định 4).
  Vd 3 task nhẹ chạy cùng lúc; 1 nặng + 1 nhẹ; 2 vừa. Task xong → task kế được nạp ngay (không chờ cả đợt).
- **Không chạy cùng lúc** 2 task code có scope chồng nhau (hoặc thiếu scope); task phụ thuộc chờ task trước gộp xong (`--merge` tự gộp task đạt).
- **Cách ly**: mỗi task code chạy trong git worktree riêng `<worktree_dir>/<slug>-<id>` trên nhánh `game/<slug>-<id>`;
  orch chép `*.csproj` + tạo junction `Library`, `Temp/Bin` về repo chính để build-check được (KHÔNG mở Unity trong worktree).
  Gộp xong orch gỡ junction rồi xoá worktree (thư mục đích không bị đụng). Đặt `worktree_dir` ở ổ còn trống nhiều.
- **Test đơn luồng**: khi 1 phiên claude xong, luồng chính chạy test của task đó (trong worktree của nó), viết `REPORT.md`, rồi mới tới task khác.
Không `--parallel` = chạy tuần tự từng task trong repo chính (như cũ).

Sau mỗi task:
1. Orch in `REPORT.md` (nơi thực hiện: thư mục làm việc / worktree, nhánh, commit, session; kết quả; test).
2. **Báo người dùng ngay** (copy phần "Nơi thực hiện" + "Kết quả" từ báo cáo; không tóm tắt mất đường dẫn).
3. `failed` → đọc báo cáo + `test.log`: lỗi của task → `O run T01 --fix` (tiếp phiên cũ, trong đúng worktree cũ nếu có, ≤ `max_fix` lần);
   lỗi do đề / plan → sửa file task rồi `O run T01`; vượt giới hạn → dừng, hỏi người dùng.
4. (Tuỳ chọn, task lớn / rủi ro) task review `kind: review` đọc diff nhánh, ghi nhận xét; lỗi nghiêm trọng → `--fix`.
5. `passed` → `O merge T01` (gộp vào nhánh tích hợp để task sau thấy). Xung đột → orch huỷ merge, báo; tạo task sửa xung đột.

**7. Test tích hợp.** Trên nhánh tích hợp: `O test --cmd "<validator>" --cmd "<tự chơi batchmode>"`; xem ảnh tự chơi.

**8. Sửa bug.** Mỗi bug → task `F<nn>` (kind code, mô tả: hiện tượng, log, bước tái hiện, tiêu chí đạt) → chạy → gộp → `O test` lại.
Tối đa 2 vòng tự sửa; còn lỗi → đưa vào báo cáo, hỏi người dùng.

**9. Báo cáo.** `O phase report` · `O report` → `.game/REPORT.md` (task, trạng thái, commit, test, cổng duyệt, chi phí, còn tồn).
Trình bày cho người dùng + hỏi G3 (gộp nhánh tích hợp vào nhánh chính hay chưa).

**10. Rút bài học.** Lỗi lặp / người dùng sửa cách làm → `LEARNINGS.md` (chung) hoặc `.claude/game-profile.md` (riêng). `O phase done`.

## Định dạng file task

```markdown
---
id: T03
title: Dựng importer level kéo thả
kind: code            # code | research | review
depends: T01, T02
scope: Assets/Game/Scripts/Editor/**, Assets/Game/Data/**
test: python "<skill>/scripts/check_build.py" Assembly-CSharp-Editor.csproj
test: python Tools/validate_level.py Assets/Game/Levels/Level 001
model: sonnet         # tuỳ chọn: haiku việc đơn giản, opus việc khó
effort: high          # tuỳ chọn
budget: 3             # USD tối đa cho 1 lần chạy
weight: 2             # tuỳ chọn: độ nặng 1..3 (hoặc size: S|M|L); không ghi thì orch tự ước lượng
unity: false          # true: cần Unity batchmode → chạy một mình ở repo chính, không worktree
mode: auto            # manual: làm tay trong session tương tác (open / done), run tự động bỏ qua
output:               # research / review: file kết quả (mặc định .game/research/<id>.md)
---
## Bối cảnh
(phần plan liên quan, file nên đọc)
## Việc cần làm
1. ...
## Tiêu chí nghiệm thu
- [ ] ... (kiểm được bằng lệnh / ảnh)
## Không làm
- ...
```
Nhiều dòng `test:` được. Test trong `config.json` → `tests` chạy thêm cho mọi task code (mặc định build C#).

## Task làm tay (CLI hay session tương tác?)

| Chạy bằng CLI (mặc định) | Làm tay (`mode: manual` hoặc `/gplay-game:open`) |
|---|---|
| Đề bài rõ, kiểm được bằng lệnh: code theo spec, sinh dữ liệu, sửa lỗi có test tái hiện | Cần phán đoán bằng mắt (UI, vị trí), đối chiếu video, Unity Editor đang mở, đề bài mơ hồ, CLI đã trượt quá `max_fix` |

`O open T03 [--here]`: dựng nhánh / worktree như task thường, ghi `manual.md` (đề bài + luật làm tay), in lệnh mở claude:
tiếp phiên CLI cũ (`claude --resume`) nếu task đã chạy, không thì phiên mới có `--session-id` biết trước.
`O done T03 --note "..." [--fail] [--merge]`: commit phần người dùng + claude đã sửa, chép transcript phiên tương tác vào thư mục run,
chạy test của task, viết REPORT.md + lịch sử (`manual_open`, `manual_done`, `task_end`) như task tự động.

## Truy vết + báo cáo

| File | Nội dung |
|---|---|
| `.game/HISTORY.md` | Nhật ký người đọc: mọi sự kiện (init, phase, cổng duyệt, task bắt đầu / kết thúc, merge, test, báo cáo) |
| `.game/history.jsonl` | Cùng nội dung, dạng máy (lọc bằng `jq` / python) |
| `.game/state.json` | Phase hiện tại, trạng thái từng task, session id, nhánh, commit, chi phí |
| `.game/runs/<T>/<thời điểm>-a<lần>/` | `prompt.md`, `command.txt`, `transcript.jsonl` (mọi lượt gọi tool), `result.json`, `diff.txt`, `test.log`, `REPORT.md` |
| Lịch sử lập lịch | Sự kiện `schedule` (độ nặng từng task), `worktree_add` / `worktree_remove`, `task_start` ghi thư mục làm việc |
| Git | Mỗi lần chạy 1 commit `[game] T03: ... (lần n)` trên nhánh task, ghi `Run:` + `Session:`; gộp `--no-ff` |
| Phiên claude | `claude --resume <session id>` mở lại đúng phiên worker để hỏi tiếp |

Truy ngược 1 dòng code: `git log -L` / `git blame` → commit `[game] Txx` → `Run:` trong message → thư mục run → transcript.

`REPORT.md` mỗi task luôn có: **Nơi thực hiện** (repo, nhánh, commit, thư mục chạy, session, file đổi + cờ ngoài phạm vi),
**Kết quả** (worker tự báo theo schema + mô tả từng file), **Kiểm tra** (lệnh worker chạy + lệnh orch chạy lại, đạt / lỗi),
quyền bị từ chối, chưa làm, rủi ro, ghi chú cho task sau, chi phí. Orch tự đo nhánh / commit / file / test, không tin lời worker.

## Luật orchestrator

- Không tự sửa code / asset game; mọi thay đổi qua task. Được viết: `.game/*.md`, file task, trả lời người dùng.
- Không bỏ cổng duyệt. Không gộp vào nhánh chính khi chưa có G3.
- Task `failed` không được gộp. Không sửa test cho xanh.
- `.game/` gitignore (lịch sử không đổi theo nhánh); không xoá `.game/runs`.
- Worker không hỏi được người dùng: đề task phải đủ thông tin; thiếu thì orchestrator hỏi trước khi chạy.
- Giới hạn chi phí: `budget_usd` mỗi lần chạy (config / task); báo tổng chi phí trong báo cáo.
- Quyền worker: `acceptEdits` + `allowed_tools` trong config (không dùng bypass). Hook guard của repo vẫn áp dụng cho worker.
