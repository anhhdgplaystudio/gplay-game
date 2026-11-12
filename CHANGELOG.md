# Changelog

- 2026-11-13 (0.2.0): làm lại sau dự án thử đầu tiên chạy trọn pipeline (33 task, 49 lần chạy CLI: 21 lần đầu "partial", 20 task phải đóng tay,
  168 lệnh bị từ chối quyền, plan viết lại 4 lần vì nghiên cứu hời hợt).
  - **Nghiên cứu là trọng tâm**: lệnh `research` + `reference/research.md` + mẫu `templates/research/` (teardown luật có nhãn bằng chứng, visual-spec:
    luồng màn, bố cục theo %, camera, vật thể, chuyển động, UI). Bắt buộc có video gameplay; `scripts/study_video.py` (frame đánh số, điểm cắt cảnh,
    bảng màu, `--clip` soi chuyển động) thay `frames.py`. Cổng G1: luật lõi không còn `[suy luận]`, không hỏi người dùng luật của game gốc.
  - **Cổng GS (level mẫu)**: mốc 1 = 1 level chơi đúng luật + hình khớp ảnh chuẩn (`scripts/side_by_side.py`, lưới %), người dùng duyệt rồi mới làm tiếp.
  - **Phiên chính tự làm theo mốc** (4–7 mốc, subagent cho phần lớn), không còn mặc định mỗi task 1 phiên claude CLI. 15 lệnh → 6:
    `start`, `research`, `plan`, `build`, `status`, `learn`. `orch.py ms` ghi mốc: thời gian, file đổi, ảnh bằng chứng; REPORT.md sinh lại mỗi mốc.
  - **Art theo yêu cầu** (`reference/art-on-demand.md`, `templates/art-brief.md`): Codex / Gemini vẽ khi người dùng bảo; đúng kích thước, không kéo dãn.
  - **Plugin tổng quát**: không thêm playbook theo 1 game; cơ chế chưa có playbook → teardown là playbook của dự án (`mechanics.md`).
  - Worker CLI thành tuỳ chọn (`reference/cli-workers.md`), sửa `orch.py`: tự dò claude CLI (extension IDE tự cập nhật) + kiểm trước khi tính lần chạy;
    quyền mặc định có `PowerShell(...)`; luật worker "1 lệnh đơn, không gọi vòng lệnh bị chặn"; `verify:` / `evidence:` (orch chạy Unity có GPU, liệt kê ảnh);
    trạng thái `review` + `accept` thay cho việc lạm dụng `open` / `done`; chi phí không cộng trùng khi `--fix` tiếp phiên, ghi rõ là USD quy đổi,
    `budget_usd` mặc định 0; lần chạy bị ngắt được ghi `interrupted`; không git vẫn biết file đổi (mtime); `log` nhận stdin / `--file` (giữ dấu tiếng Việt);
    `persist_sessions`; `init` không còn tạo task R1 / R2.

- 2026-11-03: bản đầu. Tổng hợp từ quy trình Fashion Puzzle (khái quát hoá) + học từ Claude-Code-Game-Studios, awesome-gamedev-agent-skills,
  Unity-Technologies/skills (unity-pipeline), m4bwav/unity-agent (thang kiểm tra, LEARNINGS), Unity-Skills (dry-run, transaction),
  devdavv/unity-ai-workflow (file nạp sẵn ngắn), Anthropic skill best practices.
- 2026-11-03: thêm pipeline /start (skill `start` + reference/pipeline.md + scripts/orch.py). Mọi task chạy bằng `claude -p`
  (stream-json transcript, --json-schema báo cáo, --session-id / --resume để sửa), nhánh git riêng mỗi task, gộp --no-ff,
  lịch sử .game/HISTORY.md + history.jsonl, cổng duyệt G0–G3. Đã chạy thử đầu cuối trên repo giả (haiku, $0.05).
- 2026-11-03: đổi tên skill `start` → `new-game` (gọi bằng /new-game).
- 2026-11-03: chạy song song theo độ nặng (`run ... --parallel [N] --merge`): tối đa max_parallel=3 phiên, tổng độ nặng ≤ max_load=4,
  mỗi task code 1 git worktree (chép csproj, junction Library / Temp/Bin), test vẫn đơn luồng, task phụ thuộc chờ gộp,
  task scope chồng nhau không chạy cùng lúc, task Unity chạy một mình. Đã chạy thử 5 task (3 song song + 1 nặng + 1 phụ thuộc): 50 s.
- 2026-11-08: chuyển thành plugin `gplay-game` (~/.claude/skills/gplay-game, nạp thành gplay-game@skills-dir). Skill kiến thức
  `casual-puzzle-game` → `gplay-game`; `/new-game` thay bằng 13 lệnh `/gplay-game:` start, continue, status, plan, split, run, fix,
  test, report, add-rule, history, config, help. orch.py: `history` (lọc task / file / sự kiện / ngày), `config`, `init` tạo sẵn
  R1/R2 + `.claude/guard.json`, lần sửa tự lên model (`fix_model_up` haiku→sonnet), `RULES.md` chép vào prompt worker,
  `commit_ignore` bỏ file rác. Hook guard thành hook của plugin, chỉ bật ở dự án có `.claude/guard.json` enabled; luật thêm qua
  guard.json (`no_edit`, `no_cmd`, `secrets`). Đã chạy thử: start, task haiku, history --file, config, dry-run fix lên sonnet, hook chặn .prefab.
- 2026-11-08: task làm tay: `mode: manual` (run bỏ qua), lệnh `/gplay-game:open` (dựng nhánh / worktree, in lệnh claude tiếp phiên cũ)
  + `/gplay-game:done` (commit, chép transcript, test, REPORT.md, gộp). Làm tay được cả khi đã hết `max_fix`. Test chạy với
  PYTHONUTF8=1 (Windows). parse_task: `T1` không còn khớp nhầm `T10`. Đã chạy thử: open → sửa → done trượt → open lại cùng worktree → done đạt → gộp.
- 2026-11-10: `/gplay-game:start` làm lại theo Claude-Code-Game-Studios (`/start`, `/brainstorm`): xin tài liệu tham khảo trước
  (link store / video / ảnh / mockup), tự xem, đoán mục còn lại kèm nhãn *(đoán)* / *(mặc định)*, thẻ "Mình hiểu như sau",
  chỉ hỏi mục mơ hồ bằng AskUserQuestion (≤ 2 lượt), đồng ý mới ghi intake; slug tự đặt. Thêm `scripts/frames.py`
  (trích frame video, tự cắt viền đen, `--sheet`). Mọi lệnh hỏi bằng AskUserQuestion. guard.json mẫu chặn sẵn keystore / google-services.
