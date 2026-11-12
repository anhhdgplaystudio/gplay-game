---
name: research
description: Nghiên cứu kỹ game tham khảo trước khi lập plan - thu video gameplay, mổ frame, viết teardown luật chơi có bằng chứng + spec hình và luồng màn, đọc base, chốt cổng G1.
disable-model-invocation: true
argument-hint: "[link / file video bổ sung, hoặc phần cần nghiên cứu lại]"
---
# /gplay-game:research

`O = python "${CLAUDE_PLUGIN_ROOT}/scripts/orch.py"`. Phương pháp đầy đủ: `${CLAUDE_PLUGIN_ROOT}/reference/research.md` (**đọc trước khi làm**).
Mẫu: `${CLAUDE_PLUGIN_ROOT}/templates/research/` (teardown.md, visual-spec.md, base.md).

Phiên này tự làm (phải xem ảnh). Đây là bước được đầu tư nhiều nhất của pipeline: thà chậm ở đây còn hơn viết lại luật / bố cục về sau.

1. Cần G0 (`O history --event G0`); chưa có → `/gplay-game:start`. Đọc `.game/intake.md`. `O phase research`.
   Đã có `.game/research/teardown.md` → đây là nghiên cứu lại: chỉ làm phần `$ARGUMENTS` / phần người dùng vừa chê, cập nhật file, ghi mục "Thay đổi".
2. **Thu nguồn** (research.md mục 1). Bắt buộc có video gameplay liên tục từ đầu level tới thắng. Chưa có → tự tìm + tải bằng yt-dlp vào ổ tạm;
   không tải được → hỏi người dùng xin file / quay màn hình rồi dừng chờ. Không đi tiếp chỉ với ảnh store.
3. **Song song**: giao 1 subagent (tool Agent, chỉ đọc) đọc base theo `templates/research/base.md` → `.game/research/base.md`;
   có thư mục asset / config game gốc → thêm 1 subagent thống kê số liệu. Trong lúc đó phiên chính mổ video.
4. **Mổ video**: `study_video.py` → Read `sheet.jpg` → Read frame gốc ở các mốc → `--clip` cho từng chuyển động quan trọng (≥ 5 đoạn:
   1 thao tác trọn vẹn, vật vào màn, vật ra màn, thắng, chuyển màn). Xem thêm video thứ 2 cho level có cơ chế phụ.
5. Viết `.game/research/teardown.md`: trả lời đủ 8 câu của research.md mục 3, mỗi luật kèm nhãn bằng chứng.
6. Viết `.game/research/visual-spec.md`: ảnh chuẩn từng màn (chép vào `<ổ tạm>/ref/golden/`), luồng màn, bố cục theo % (ảnh lưới `side_by_side.py --grid 10`),
   camera, danh mục vật thể, chuyển động, UI, nền.
7. **Tự soát trước khi hỏi**: mục "Luật lõi" còn `[suy luận]` → soi thêm clip / video khác. Hết cách mới đưa vào câu hỏi, kèm đường dẫn frame.
8. Trình người dùng **thẻ đối chiếu** (5–8 dòng: luật lõi, bố cục, luồng màn; mỗi dòng 1 đường dẫn đầy đủ tới frame bằng chứng) + ghi `.game/questions.md`,
   rồi hỏi bằng AskUserQuestion: (a) thẻ đúng chưa; (b) các quyết định của người dùng: phạm vi bản đầu, khác biệt so với gốc, tên / package id,
   art (mặc định hình tạm, vẽ khi yêu cầu). Không hỏi người dùng luật của game gốc khi video trả lời được.
9. Người dùng xác nhận → ghi câu trả lời vào `questions.md`, `O log G1 "<tóm tắt>"`, `O phase plan` → gợi ý `/gplay-game:plan`.
   Người dùng sửa luật / hình → cập nhật teardown / visual-spec, trình lại dòng đã sửa.

Hỏi người dùng bằng tool **AskUserQuestion** (≤ 4 câu / lượt, 2–4 phương án, khuyến nghị đặt đầu + "(Recommended)"), không liệt kê câu hỏi thành chữ.
Báo kết quả luôn kèm đường dẫn đầy đủ tới ảnh (sheet, frame, ảnh lưới) để người dùng mở xem.
