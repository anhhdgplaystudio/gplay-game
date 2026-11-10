---
name: done
description: Chốt task làm tay - orch commit thay đổi, chạy test của task, chép transcript, viết REPORT.md + lịch sử như task tự động, gộp nếu đạt.
disable-model-invocation: true
argument-hint: "<T01> [\"tóm tắt đã làm\"]"
---
# /gplay-game:done

`O = python "${CLAUDE_PLUGIN_ROOT}/scripts/orch.py"`.

1. Id task = từ đầu tiên của `$ARGUMENTS`; phần còn lại = tóm tắt. Không có tóm tắt → hỏi người dùng 1 câu (đã làm gì, còn gì chưa làm).
2. Người dùng nói chưa xong / bỏ dở → `O done <id> --note "<tóm tắt>" --fail`. Còn lại → `O done <id> --note "<tóm tắt>" --merge`.
3. Dán **Nơi thực hiện** + **Kết quả** + **Kiểm tra** của REPORT.md. Test trượt → task giữ worktree; gợi ý `/gplay-game:open <id>` làm tiếp
   hoặc `/gplay-game:fix <id>` cho claude CLI sửa.

Hỏi người dùng (chọn phương án, duyệt cổng, xác nhận) bằng tool **AskUserQuestion** (≤ 4 câu / lượt, 2–4 phương án, khuyến nghị đặt đầu + "(Recommended)"), không liệt kê câu hỏi thành chữ.
