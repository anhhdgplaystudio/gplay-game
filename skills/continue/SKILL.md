---
name: continue
description: Tiếp tục pipeline game đang làm dở - đọc state + lịch sử, báo đang ở bước nào và làm tiếp bước đó.
disable-model-invocation: true
argument-hint: "[ghi chú thêm]"
---
# /gplay-game:continue

`O = python "${CLAUDE_PLUGIN_ROOT}/scripts/orch.py"`. Quy trình: `${CLAUDE_PLUGIN_ROOT}/reference/pipeline.md` (đọc phần của bước hiện tại).

1. Không có `.game/` → bảo người dùng chạy `/gplay-game:start`. Dừng.
2. `O status` + `O history -n 25`. Đọc `.game/plan.md` nếu có.
3. Báo ngắn: giai đoạn, cổng duyệt đã qua (G0–G3), task xong / trượt / đang chờ, việc tiếp theo.
4. Làm tiếp đúng bước đó theo pipeline.md:
   - **chưa có G0** (giai đoạn intake): làm đúng luồng intake của `${CLAUDE_PLUGIN_ROOT}/skills/start/SKILL.md` (đọc file đó),
     bỏ bước init. Đọc `.game/intake.md` trước: mục đã điền thì giữ. **Câu hỏi đầu tiên là xin tài liệu tham khảo** (link / video / ảnh / mockup)
     bằng chữ rồi dừng chờ; không hỏi cơ chế / nền tảng / base trước khi xem tài liệu;
   - sau G0: `O run R1 R2 --parallel` (task R1 / R2 đã có sẵn trong `.game/tasks/` từ lúc init),
     rồi câu hỏi + đề xuất từ kết quả nghiên cứu → chờ G1;
   - sau G1: `/gplay-game:plan`; sau G2: `/gplay-game:split` rồi `/gplay-game:run`;
   - có task failed: đề xuất `/gplay-game:fix <task>`; mọi task merged: `/gplay-game:test` → `/gplay-game:report`.
5. Bước cần người dùng quyết định (cổng duyệt) → hỏi rồi dừng; không tự vượt cổng.

Phiên này là orchestrator: không tự sửa code / asset game, mọi việc thực hiện qua `O run`.
`$ARGUMENTS` là ghi chú của người dùng: ghi lại bằng `O log NOTE "..."`.

Hỏi người dùng (chọn phương án, duyệt cổng, xác nhận) bằng tool **AskUserQuestion** (≤ 4 câu / lượt, 2–4 phương án, khuyến nghị đặt đầu + "(Recommended)"), không liệt kê câu hỏi thành chữ.
