---
name: test
description: Test tích hợp trên nhánh game sau khi gộp các task - build, validator, test riêng dự án; lỗi thì đề xuất task sửa.
disable-model-invocation: true
argument-hint: "[lệnh test thêm]"
---
# /gplay-game:test

`O = python "${CLAUDE_PLUGIN_ROOT}/scripts/orch.py"`. Thang kiểm tra: `${CLAUDE_PLUGIN_ROOT}/reference/verification.md`.

1. Còn task passed chưa gộp → `O merge <...>` trước.
2. `O test` (thêm `--cmd "<lệnh>"` cho từng lệnh trong `$ARGUMENTS`). Có Unity batchmode trong lệnh test → hỏi đóng Editor trước.
3. Đọc log, báo kết quả. Có ảnh chụp chạy thử: phải XEM ảnh trước khi nói đạt.
4. Lỗi → mỗi lỗi độc lập đề xuất 1 task F (`/gplay-game:fix bug "..."`). Đạt → gợi ý `/gplay-game:report`.
