---
name: config
description: Xem / đổi cấu hình pipeline game - model mặc định, budget, số phiên song song, tải tối đa, thư mục worktree, lệnh test chung.
disable-model-invocation: true
argument-hint: "[khoá [giá trị]]"
---
# /gplay-game:config

Chạy ở gốc repo: `python "${CLAUDE_PLUGIN_ROOT}/scripts/orch.py" config $ARGUMENTS`

- Trống → in toàn bộ, giải thích ngắn các khoá hay đổi: `model`, `budget_usd`, `max_parallel`, `max_load`, `max_fix`,
  `fix_model_up`, `worktree_dir` (nên đặt ở ổ còn trống: mỗi worktree chép cả Assets), `tests`, `timeout_s`.
- Có giá trị → orch ghi `.game/config.json` + lịch sử. List / object viết dạng JSON, vd `tests '["dotnet build X.csproj"]'`.
