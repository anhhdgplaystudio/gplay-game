---
name: learn
description: Ghi bài học hoặc thêm luật làm việc ngay khi gặp - cho dự án này (AGENTS.md / game-profile) hoặc mọi game (LEARNINGS.md / RULES.md của plugin); luật kiểm được bằng máy thì thêm vào guard.json.
disable-model-invocation: true
argument-hint: "\"<bài học / luật>\" (trống = rà lại góp ý của người dùng trong lịch sử)"
---
# /gplay-game:learn

`O = python "${CLAUDE_PLUGIN_ROOT}/scripts/orch.py"`. Dùng **ngay** khi người dùng sửa cách làm hoặc 1 lỗi lặp lần 2; không đợi cuối dự án.

Nội dung = `$ARGUMENTS`. Trống → `O history --event NOTE -n 40` + rà hội thoại: liệt kê các lần người dùng phải sửa hướng, đề xuất bài học cho từng lần, hỏi người dùng giữ cái nào.

1. Phân loại (hỏi nếu chưa rõ):

| Loại | Ghi vào | Cách viết |
|---|---|---|
| Bài học chung mọi game (cách nghiên cứu, kiểm tra, làm UI, Unity) | `${CLAUDE_PLUGIN_ROOT}/LEARNINGS.md` | 1 dòng: bài học · nguồn (dự án) · tháng. **Không** tên class / luật chơi / đường dẫn riêng 1 game |
| Luật bắt buộc mọi game | `${CLAUDE_PLUGIN_ROOT}/RULES.md` (dòng `- ...`, được chép vào prompt worker CLI) + `CHANGELOG.md` | Câu mệnh lệnh ngắn |
| Riêng dự án này (luật chơi, cấu trúc, lệnh, bẫy của game này) | mục "Bài học" của `AGENTS.md` hoặc `.claude/game-profile.md` | Đúng giọng file, kèm lý do nếu không hiển nhiên |
| Sở thích của người dùng về cách làm việc với Claude | memory của Claude (không phải plugin) | |

   Plugin là quy trình **chung**: cơ chế / luật của 1 game cụ thể không đưa vào `reference/` trừ khi đã dùng lại ở ≥ 2 game (khi đó thêm playbook vào `mechanics.md`).
2. Bài học trái với nội dung plugin (reference / skill đang dặn làm khác) → sửa luôn chỗ đó + ghi `CHANGELOG.md`, không chỉ thêm dòng.
3. Luật kiểm được bằng máy → thêm vào guard.json (dự án: `.claude/guard.json`; mọi game: `${CLAUDE_PLUGIN_ROOT}/guard.json`):
   cấm sửa đường dẫn → `no_edit` (glob từ gốc dự án); cấm lệnh → `no_cmd` `{"pattern": "<regex>", "why": "<lý do>"}`; file bí mật → `secrets`.
   Kiểm ngay, phải ra exit 2:
   `echo '{"tool_name":"Write","tool_input":{"file_path":"<gốc>/<đường dẫn mẫu>"},"cwd":"<gốc>"}' | python "${CLAUDE_PLUGIN_ROOT}/scripts/guard.py"; echo $?`
4. Trùng / mâu thuẫn luật có sẵn → sửa luật cũ, không thêm dòng mới.
5. Có `.game/` → `O log LEARN "<phạm vi>: <bài học>"`.
6. Báo: ghi ở file nào, có được guard chặn không.

Hỏi người dùng bằng tool **AskUserQuestion** (≤ 4 câu / lượt, 2–4 phương án, khuyến nghị đặt đầu + "(Recommended)"), không liệt kê câu hỏi thành chữ.
