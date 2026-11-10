---
name: start
description: Bắt đầu dự án game mới theo pipeline GPlay - tạo .game/, bật guard, đưa form intake để điền.
disable-model-invocation: true
argument-hint: "[tên-game]"
---
# /gplay-game:start

`O = python "${CLAUDE_PLUGIN_ROOT}/scripts/orch.py"`, chạy ở gốc repo dự án.
Quy trình đầy đủ: `${CLAUDE_PLUGIN_ROOT}/reference/pipeline.md`. Luật chung: skill `gplay-game` + `${CLAUDE_PLUGIN_ROOT}/RULES.md`.

1. Đã có `.game/` → không init lại; báo người dùng dùng `/gplay-game:continue`. Dừng.
2. Tên game = `$ARGUMENTS`; trống thì hỏi (slug chữ thường, gạch ngang).
3. `O init --slug <tên>`: tạo `.game/` (intake, config, lịch sử, task R1 / R2 dựng sẵn) và `.claude/guard.json`
   (bật hook chặn sửa YAML / .meta / bí mật). Hỏi người dùng có file bí mật riêng nào thêm vào `secrets` của guard.json không
   (chỉ tên file, không đọc nội dung).
4. Chưa có `AGENTS.md` / `.claude/game-profile.md` → ghi chú "cần tạo ở bước plan" (mẫu ở `${CLAUDE_PLUGIN_ROOT}/templates/`).
5. Đưa người dùng các đề mục trong `.game/intake.md` (ý tưởng, link game tham khảo, ảnh, video, phạm vi, kỹ thuật) để điền:
   điền thẳng vào file hoặc trả lời trong chat (khi đó chép vào file). Dừng chờ.
6. Người dùng điền xong → `O log G0 "intake xong"` → làm tiếp như `/gplay-game:continue`.
