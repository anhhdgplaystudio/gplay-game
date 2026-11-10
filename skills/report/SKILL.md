---
name: report
description: Sinh báo cáo tổng pipeline game (.game/REPORT.md) - task, commit, test tích hợp, cổng duyệt, chi phí, còn tồn; xin duyệt G3.
disable-model-invocation: true
---
# /gplay-game:report

1. `python "${CLAUDE_PLUGIN_ROOT}/scripts/orch.py" report`.
2. Tóm tắt cho người dùng: đã làm gì, kết quả test, việc CHƯA làm, rủi ro, tổng chi phí, đường dẫn `.game/REPORT.md`.
3. Hỏi duyệt G3 (gộp nhánh `game/<slug>` vào nhánh chính). Chỉ gộp / commit khi người dùng đồng ý, rồi
   `python "${CLAUDE_PLUGIN_ROOT}/scripts/orch.py" log G3 "..."`.
4. Gợi ý rút kinh nghiệm: lỗi lặp, người dùng sửa cách làm → `/gplay-game:add-rule`.
