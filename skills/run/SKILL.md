---
name: run
description: Chạy task bằng claude CLI - song song tối đa 3 phiên theo độ nặng, mỗi task 1 worktree, test đơn luồng, tự gộp task đạt.
disable-model-invocation: true
argument-hint: "[T01 T02 ...] (trống = mọi task chưa xong)"
---
# /gplay-game:run

`O = python "${CLAUDE_PLUGIN_ROOT}/scripts/orch.py"`.

1. Danh sách task = `$ARGUMENTS`; trống → mọi task trong `.game/tasks/` còn todo / failed chưa sửa (xem `O status`).
2. Có task `unity: true` → hỏi người dùng đã đóng Unity Editor chưa.
3. `O run <task...> --parallel --merge` (lâu thì chạy nền, chờ thông báo, không poll dồn dập).
4. Sau MỖI task xong: dán cho người dùng phần **Nơi thực hiện** + **Kết quả** trong `REPORT.md` của task đó (giữ nguyên đường dẫn, nhánh, commit).
5. Task `mode: manual` bị bỏ qua (trạng thái manual) → nhắc `/gplay-game:open <task>`.
6. Cuối lượt: bảng tổng (đạt / trượt / chờ phụ thuộc / làm tay); task trượt → gợi ý `/gplay-game:fix <task>`; hết task → `/gplay-game:test`.

Không tự sửa code thay worker. Task failed không gộp.

Hỏi người dùng (chọn phương án, duyệt cổng, xác nhận) bằng tool **AskUserQuestion** (≤ 4 câu / lượt, 2–4 phương án, khuyến nghị đặt đầu + "(Recommended)"), không liệt kê câu hỏi thành chữ.
