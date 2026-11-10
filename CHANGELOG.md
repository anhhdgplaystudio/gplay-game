# Changelog

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
