---
name: fix
description: Chạy lại task trượt (tiếp phiên claude cũ, đưa log lỗi vào, task haiku tự lên sonnet) hoặc tạo task F sửa bug tích hợp.
disable-model-invocation: true
argument-hint: "<T01> | bug \"<mô tả lỗi>\""
---
# /gplay-game:fix

`O = python "${CLAUDE_PLUGIN_ROOT}/scripts/orch.py"`.

- `$ARGUMENTS` là id task: đọc `REPORT.md` + `test.log` lần cuối, tóm nguyên nhân cho người dùng, rồi `O run <id> --fix --merge`.
  Lần sửa tiếp phiên cũ; model lên theo `fix_model_up` (mặc định haiku → sonnet). Quá `max_fix` lần → dừng, báo người dùng
  (đề bài sai? test mâu thuẫn? cần chia lại task?) và đề xuất `/gplay-game:open <id>` để làm tay cùng người dùng.
- `$ARGUMENTS` bắt đầu bằng `bug`: tạo `.game/tasks/F<số>-<tên>.md` (kind code, scope hẹp nhất có thể, test tái hiện lỗi),
  `O log BUG "<mô tả>"`, rồi `O run F<số> --merge`.
- Sau mỗi lần chạy: dán **Nơi thực hiện** + **Kết quả** của REPORT.md.
