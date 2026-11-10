---
name: history
description: Truy vết ngược lịch sử pipeline game - lọc theo task, theo file (task / commit nào đã sửa), loại sự kiện, thời gian.
disable-model-invocation: true
argument-hint: "[T01 | đường/dẫn/file | G1 | 2026-11-01]"
---
# /gplay-game:history

`O = python "${CLAUDE_PLUGIN_ROOT}/scripts/orch.py"`. Hiểu `$ARGUMENTS`:
- id task (T01, R1, F2) → `O history --task <id>`
- có `/` hoặc đuôi file → `O history --file <đường dẫn>` (task đã sửa, commit mọi nhánh, sự kiện liên quan)
- G0–G3, PLAN, RULE, BUG, config, merge, test... → `O history --event <x>`
- ngày → `O history --since <ngày>`; trống → `O history -n 40`

Trả lời câu hỏi của người dùng từ kết quả (task nào / lúc nào / commit nào / vì sao), kèm đường dẫn REPORT.md
và transcript (`.game/runs/<task>/<lần>/transcript.jsonl`) để xem chi tiết. Không sửa gì.
