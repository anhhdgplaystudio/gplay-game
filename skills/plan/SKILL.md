---
name: plan
description: Lập hoặc sửa plan.md của game theo mốc thấy được (M1 = khung hình tĩnh → GV, M2 = level mẫu chơi được → GS), sau khi nghiên cứu đã qua cổng G1, tới khi người dùng duyệt G2.
disable-model-invocation: true
argument-hint: "[yêu cầu sửa plan]"
---
# /gplay-game:plan

`O = python "${CLAUDE_PLUGIN_ROOT}/scripts/orch.py"`. Mẫu: `${CLAUDE_PLUGIN_ROOT}/templates/plan.md`. Chi tiết: `${CLAUDE_PLUGIN_ROOT}/reference/pipeline.md` bước 3.

1. Cần G1 (`O history --event G1`). Chưa có, hoặc `.game/research/teardown.md` mục "Luật lõi" còn `[suy luận]`, hoặc thiếu
   `.game/research/ref-level.md` / `visual-check.md` (cột Mẫu trống) → quay lại `/gplay-game:research`. Dừng.
2. Đọc `.game/intake.md`, `.game/research/*`, `.game/questions.md`, plan cũ nếu có.
3. Chưa có plan → viết `.game/plan.md` theo mẫu. Có rồi → sửa theo `$ARGUMENTS`, tăng số phiên bản, ghi mục "Thay đổi".
   - Chia theo **mốc thấy được** (5–8 mốc), không chia task nhỏ. **M1 = khung hình tĩnh** của level chuẩn → cổng GV (luật lõi + test làm song song);
     **M2 = level mẫu chơi được**, chuyển động khớp clip → cổng GS. Không gộp 2 mốc này.
   - Mỗi dòng của `visual-check.md` phải thuộc 1 mốc (cột Mốc); mốc nào có hình thì "Kiểm" của mốc đó là các dòng ấy.
   - Luật chơi không chép lại vào plan: trỏ tới teardown. Hình trỏ tới visual-spec. Luồng màn (Loading / Home / Game) phải có mốc riêng hoặc nằm rõ trong 1 mốc.
   - Mỗi mốc: người dùng thấy gì khi xong, lệnh kiểm, ảnh bằng chứng, phần giao subagent được, ước lượng thời gian.
   - Art thật, SDK thật, build store: để "ngoài phạm vi" trừ khi người dùng đã yêu cầu.
4. `O log PLAN "v<n>: <tóm tắt>"`, `O phase plan`.
5. Đưa người dùng bảng mốc + câu hỏi còn mở (AskUserQuestion), gồm nếu chưa rõ:
   - Repo chưa có git → `git init` cục bộ để hoàn tác được (Recommended) / không dùng git (sao lưu thư mục trước M1).
   - Có git → cho phép commit sau mỗi mốc trên nhánh `game/<slug>`?
6. Người dùng duyệt → `O log G2 "chốt plan v<n>; <quyết định git>"`, `O phase slice` → gợi ý `/gplay-game:build`.

Bước này chỉ ghi file trong `.game/`, chưa sửa code game.

Hỏi người dùng bằng tool **AskUserQuestion** (≤ 4 câu / lượt, 2–4 phương án, khuyến nghị đặt đầu + "(Recommended)"), không liệt kê câu hỏi thành chữ.
