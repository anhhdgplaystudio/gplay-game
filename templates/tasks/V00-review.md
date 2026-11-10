---
id: V00
title: Review <Txx>
kind: review
depends: <Txx>
model: sonnet
budget: 2
---
Đọc diff nhánh task: `git diff <nhánh tích hợp>...<nhánh task>` và báo cáo `.game/runs/<Txx>/<lần cuối>/REPORT.md`.

Kiểm: đúng tiêu chí nghiệm thu trong `.game/tasks/<Txx>*.md`; lỗi logic / null / trường hợp biên; vi phạm AGENTS.md
(namespace, YAML, .meta, bí mật); sửa ngoài phạm vi; test có thật sự kiểm hành vi không.

Ghi `.game/research/V00.md`: mỗi phát hiện = mức (nghiêm trọng / nên sửa / gợi ý), file:dòng, lý do, cách sửa.
result = done nếu không có phát hiện nghiêm trọng, ngược lại partial.
