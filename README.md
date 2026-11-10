# gplay-game (plugin Claude Code)

Quy trình làm game puzzle casual mobile mới bằng Unity cho GPlay: intake → nghiên cứu + đọc base → câu hỏi → plan → chia task →
mỗi task chạy bằng claude CLI (song song theo độ nặng, mỗi task 1 git worktree) → test → gộp → báo cáo, có lịch sử truy vết.

## Lệnh

`/gplay-game:help` liệt kê đủ. Chính: `start`, `continue`, `status`, `plan`, `split`, `run`, `fix`, `test`, `report`,
`add-rule`, `history`, `config`. Skill kiến thức `gplay-game` (cơ chế, pipeline level, UI, localization, phát hành) Claude tự dùng.

## Cài

- Máy tác giả: thư mục này nằm ở `~/.claude/skills/gplay-game/`, tự nạp thành `gplay-game@skills-dir` (sửa là có hiệu lực từ phiên sau / `/reload-plugins`).
- Máy khác: chép thư mục này vào `~/.claude/skills/gplay-game/` (hoặc clone repo chứa nó vào đó). Cần Python 3, git, claude CLI.

## Hook guard

Chặn sửa tay YAML Unity, sửa `.meta`, đọc file bí mật, lệnh nguy hiểm. Chỉ bật ở dự án có `.claude/guard.json` với `"enabled": true`.

## Cấu trúc

`SKILL.md` (skill kiến thức) · `skills/*` (lệnh) · `reference/` · `templates/` · `scripts/` (orch.py, guard.py, check_build.py,
check_dev.py, compose_dev.py) · `hooks/hooks.json` · `RULES.md` + `guard.json` (luật chung) · `LEARNINGS.md` · `CHANGELOG.md` · `evals/`.
