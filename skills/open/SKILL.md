---
name: open
description: Làm tay 1 task trong session claude tương tác - dựng nhánh / worktree, in lệnh mở claude (tiếp phiên CLI cũ nếu có) để người dùng làm cùng.
disable-model-invocation: true
argument-hint: "<T01> [--here]"
---
# /gplay-game:open

Dùng khi task cần phán đoán / tương tác: chỉnh UI theo mắt, đối chiếu video, cần Unity Editor đang mở, đề bài mơ hồ,
hoặc task CLI đã trượt quá `max_fix` lần.

1. `python "${CLAUDE_PLUGIN_ROOT}/scripts/orch.py" open $ARGUMENTS`
   - `--here`: làm ở repo chính (bắt buộc khi cần Unity Editor đang mở project; task `unity: true` tự làm ở repo chính).
   - Task đã chạy CLI trước đó: lệnh in ra là `claude --resume <id>` (giữ nguyên context cũ, cùng thư mục).
2. Đưa người dùng: thư mục, nhánh, lệnh mở claude (chạy ở terminal MỚI, đúng thư mục in ra). Đề bài ở `manual.md` trong thư mục chạy.
3. Phiên này (orchestrator) không làm thay task. Người dùng làm xong → `/gplay-game:done <id>`.
