---
name: status
description: Xem tiến độ pipeline game - giai đoạn, bảng task (trạng thái, độ nặng, chi phí, nhánh), sự kiện gần nhất.
disable-model-invocation: true
---
# /gplay-game:status

Chạy ở gốc repo: `python "${CLAUDE_PLUGIN_ROOT}/scripts/orch.py" status` và `python "${CLAUDE_PLUGIN_ROOT}/scripts/orch.py" history -n 10`.

Tóm tắt cho người dùng: giai đoạn, số task theo trạng thái, tổng chi phí, task trượt (kèm đường dẫn REPORT.md), việc nên làm tiếp.
Không làm gì thêm.
