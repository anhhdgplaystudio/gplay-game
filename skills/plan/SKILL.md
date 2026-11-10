---
name: plan
description: Lập hoặc sửa plan.md của game (sau khi chốt câu hỏi G1), tới khi người dùng duyệt G2.
disable-model-invocation: true
argument-hint: "[yêu cầu sửa plan]"
---
# /gplay-game:plan

`O = python "${CLAUDE_PLUGIN_ROOT}/scripts/orch.py"`. Mẫu: `${CLAUDE_PLUGIN_ROOT}/templates/plan.md`. Chi tiết: pipeline.md bước 4–5.

1. Đọc `.game/intake.md`, `.game/research/*`, quyết định G1 (`O history --event G1`), plan cũ nếu có.
2. Chưa có plan → viết `.game/plan.md` theo mẫu (mục tiêu bản đầu, cơ chế, kiến trúc, pipeline level, việc lớn, rủi ro, cách kiểm,
   ngoài phạm vi). Có rồi → sửa theo `$ARGUMENTS`, tăng số phiên bản ở đầu file, ghi mục "Thay đổi" cuối file.
3. `O log PLAN "v<n>: <tóm tắt thay đổi>"`, `O phase plan`.
4. Đưa người dùng phần chính + câu hỏi còn mở. Người dùng duyệt → `O log G2 "chốt plan v<n>"`, gợi ý `/gplay-game:split`.

Plan là việc của orchestrator (chỉ ghi file trong .game/), không sửa code game ở bước này.
