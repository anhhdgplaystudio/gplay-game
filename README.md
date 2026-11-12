# gplay-game (plugin Claude Code)

Quy trình làm game casual / puzzle mobile mới bằng Unity cho GPlay (dùng chung cho mọi cơ chế, không riêng game nào):
intake → **nghiên cứu kỹ game tham khảo** (mổ video, teardown luật có bằng chứng, spec hình) → plan theo mốc →
**level mẫu được duyệt** → làm từng mốc ngay trong phiên chính (tự chạy Unity, ghép ảnh so mẫu) → báo cáo. Lịch sử ở `.game/`.

## Lệnh

`/gplay-game:start` (intake) · `research` (mổ game tham khảo) · `plan` (mốc) · `build` (làm mốc kế) · `status` (tiến độ, bước kế, lịch sử, config) ·
`learn` (thêm luật / bài học). Skill kiến thức `gplay-game` (cơ chế, pipeline level, UI, localization, phát hành) Claude tự dùng.

Art không phải bước cố định: vẽ bằng Codex / Gemini khi người dùng yêu cầu (`reference/art-on-demand.md`).
Chạy task bằng phiên claude CLI riêng (song song, worktree) là tuỳ chọn (`reference/cli-workers.md`).

## Cài

- Máy tác giả: thư mục này nằm ở `~/.claude/skills/gplay-game/`, tự nạp thành `gplay-game@skills-dir` (sửa là có hiệu lực từ phiên sau / `/reload-plugins`).
- Máy khác: chép thư mục này vào `~/.claude/skills/gplay-game/`. Cần Python 3 + `opencv-python`, `pillow` (mổ video, ghép ảnh). git và claude CLI chỉ cần cho worker CLI.

## Hook guard

Chặn sửa tay YAML Unity, sửa `.meta`, đọc file bí mật, lệnh nguy hiểm. Chỉ bật ở dự án có `.claude/guard.json` với `"enabled": true`.

## Cấu trúc

`SKILL.md` (skill kiến thức) · `skills/*` (6 lệnh) · `reference/` · `templates/` (plan, research/, art-brief, tasks/, AGENTS, game-profile) ·
`scripts/` (orch.py sổ trạng thái + worker CLI, study_video.py, side_by_side.py, guard.py, check_build.py, check_dev.py, compose_dev.py) ·
`hooks/hooks.json` · `RULES.md` + `guard.json` (luật chung) · `LEARNINGS.md` · `CHANGELOG.md` · `evals/`.
