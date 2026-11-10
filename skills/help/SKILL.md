---
name: help
description: Liệt kê các lệnh /gplay-game:* và luồng nên gõ.
disable-model-invocation: true
---
# /gplay-game:help

In bảng này cho người dùng, không chạy gì:

| Lệnh | Việc |
|---|---|
| `/gplay-game:start [tên]` | Dự án mới: tạo `.game/`, bật guard, form intake |
| `/gplay-game:continue` | Làm tiếp từ chỗ dừng |
| `/gplay-game:status` | Tiến độ, chi phí |
| `/gplay-game:plan [sửa gì]` | Lập / sửa plan, duyệt G2 |
| `/gplay-game:split` | Chia plan thành task |
| `/gplay-game:run [task...]` | Chạy task bằng claude CLI (song song theo độ nặng) |
| `/gplay-game:fix <task>` / `fix bug "..."` | Sửa task trượt / bug tích hợp |
| `/gplay-game:open <task>` | Làm tay 1 task trong session tương tác (tiếp phiên CLI cũ nếu có) |
| `/gplay-game:done <task> "..."` | Chốt task làm tay: commit, test, báo cáo |
| `/gplay-game:test` | Test tích hợp |
| `/gplay-game:report` | Báo cáo tổng, duyệt G3 |
| `/gplay-game:add-rule "..."` | Thêm luật dự án / mọi game (+ hook chặn) |
| `/gplay-game:history [task / file / G1]` | Truy vết ngược |
| `/gplay-game:config [khoá giá trị]` | Cấu hình model, song song, worktree |

Luồng: `start` → điền intake → `continue` (nghiên cứu + câu hỏi) → `plan` → `split` → `run` → `fix` → `test` → `report`.
Kiến thức chung (cơ chế, pipeline level, UI, phát hành) nằm ở skill `gplay-game`, Claude tự dùng khi cần.
