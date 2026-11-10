---
name: add-rule
description: Thêm luật làm việc - cho dự án này (AGENTS.md) hoặc mọi game GPlay (RULES.md của plugin); luật kiểm được bằng máy thì thêm vào guard.json để hook chặn thật.
disable-model-invocation: true
argument-hint: "\"<nội dung luật>\""
---
# /gplay-game:add-rule

Luật = `$ARGUMENTS` (trống thì hỏi).

1. Hỏi phạm vi nếu chưa rõ:
   - **Dự án này** → thêm 1 dòng vào mục quy tắc của `AGENTS.md` (không có thì `CLAUDE.md`; không có nữa thì tạo AGENTS.md từ
     `${CLAUDE_PLUGIN_ROOT}/templates/AGENTS.md`). Viết ngắn, đúng giọng file, kèm lý do nếu không hiển nhiên.
   - **Mọi game GPlay** → thêm dòng `- <luật>` vào `${CLAUDE_PLUGIN_ROOT}/RULES.md` (orch chép các dòng này vào prompt mọi worker).
     Viết dạng chung, không tên class / đường dẫn riêng 1 game. Ghi 1 dòng vào `${CLAUDE_PLUGIN_ROOT}/CHANGELOG.md`.
2. Luật kiểm được bằng máy → thêm vào guard.json (dự án: `.claude/guard.json`; mọi game: `${CLAUDE_PLUGIN_ROOT}/guard.json`):
   cấm sửa đường dẫn → `no_edit` (glob tính từ gốc dự án); cấm lệnh → `no_cmd` `{"pattern": "<regex>", "why": "<lý do>"}`;
   file bí mật → `secrets`. Kiểm ngay bằng cách gửi JSON hook mẫu vào guard, phải ra exit 2:
   `echo '{"tool_name":"Write","tool_input":{"file_path":"<gốc>/<đường dẫn mẫu>"},"cwd":"<gốc>"}' | python "${CLAUDE_PLUGIN_ROOT}/scripts/guard.py"; echo $?`
   (guard chỉ chạy ở dự án có `.claude/guard.json` `"enabled": true`).
3. Trùng / mâu thuẫn luật có sẵn (skill `gplay-game` mục "Luật cứng", RULES.md, AGENTS.md) → báo người dùng, sửa luật cũ thay vì thêm dòng.
4. Có `.game/` → `python "${CLAUDE_PLUGIN_ROOT}/scripts/orch.py" log RULE "<phạm vi>: <luật>"`.
5. Báo: luật ghi ở file nào, có được guard chặn không (kết quả kiểm).
