---
name: split
description: Chia plan đã chốt thành các file task nhỏ (.game/tasks/*.md) có phạm vi tách biệt, phụ thuộc, độ nặng, lệnh test.
disable-model-invocation: true
argument-hint: "[phần plan cần chia]"
---
# /gplay-game:split

`O = python "${CLAUDE_PLUGIN_ROOT}/scripts/orch.py"`. Mẫu task: `${CLAUDE_PLUGIN_ROOT}/templates/tasks/` (T00 code, V00 review).
Định dạng + luật chia: pipeline.md bước 6.

1. Cần G2 (`O history --event G2`); chưa có → báo người dùng duyệt plan trước. Dừng.
2. Chia mỗi việc lớn trong plan (hoặc phần `$ARGUMENTS`) thành task làm xong trong 1 phiên claude:
   - `scope` tách biệt giữa các task chạy cùng đợt (chồng scope thì orch tự cho chạy lần lượt);
   - `depends` rõ; `test:` kiểm được bằng lệnh; `weight` 1/2/3; `unity: true` nếu cần Unity batchmode;
   - `mode: manual` cho task cần phán đoán bằng mắt / Unity Editor đang mở / đối chiếu video (người dùng làm cùng qua `/gplay-game:open`);
   - `model`: haiku chỉ cho việc máy móc weight 1, opus cho task khó weight 3, còn lại để trống (mặc định config).
3. Ghi `.game/tasks/<id>-<tên>.md`; chưa có nhánh tích hợp → `O branch`; `O run <các task> --dry-run` để kiểm parse + lịch.
4. Đưa người dùng bảng: id, tiêu đề, phụ thuộc, nặng, model, scope. Đồng ý → `O log SPLIT "<n> task"`, gợi ý `/gplay-game:run`.

Hỏi người dùng (chọn phương án, duyệt cổng, xác nhận) bằng tool **AskUserQuestion** (≤ 4 câu / lượt, 2–4 phương án, khuyến nghị đặt đầu + "(Recommended)"), không liệt kê câu hỏi thành chữ.
