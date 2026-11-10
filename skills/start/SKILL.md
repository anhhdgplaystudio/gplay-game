---
name: start
description: Bắt đầu dự án game mới theo pipeline GPlay - xin tài liệu tham khảo trước, tự xem link / video / ảnh, chỉ hỏi phần còn thiếu, ghi intake + bật guard.
disable-model-invocation: true
argument-hint: "[tên-game] [link / đường dẫn tham khảo...]"
---
# /gplay-game:start

`O = python "${CLAUDE_PLUGIN_ROOT}/scripts/orch.py"`, chạy ở gốc repo dự án.
Quy trình đầy đủ: `${CLAUDE_PLUGIN_ROOT}/reference/pipeline.md`. Luật chung: skill `gplay-game` + `${CLAUDE_PLUGIN_ROOT}/RULES.md`.

**Nguyên tắc hỏi** (học từ Claude-Code-Game-Studios `/start`, `/brainstorm`):
- Xin **tài liệu trước**, tự xem, rồi mới hỏi. Không hỏi điều đã đọc ra được hoặc có mặc định hợp lý: đoán, ghi nhãn *(đoán)* / *(mặc định)* trên thẻ tóm tắt, người dùng sửa ở đó.
- Hỏi bằng tool **AskUserQuestion**: ≤ 4 câu / lượt, 2–4 phương án lấy từ thứ đã thấy, khuyến nghị đặt đầu + "(Recommended)", `header` ≤ 12 ký tự.
  Câu hỏi là thứ cuối cùng trong câu trả lời. Bỏ qua / tắt hộp hỏi không phải là trả lời: hỏi lại bằng chữ.
- Tổng cộng tối đa 2 lượt hỏi chi tiết. Chỉ hỏi câu mà câu trả lời làm đổi plan.

## 1. Đọc dự án (im lặng, chưa báo)
- Đã có `.game/` → không init lại; báo dùng `/gplay-game:continue`. Dừng.
- Ghi nhận: thư mục ở gốc repo (thư mục lạ như `Buzzy Bus/` có thể là base hoặc art), `ProjectSettings/ProjectVersion.txt`,
  `AGENTS.md`, `.claude/game-profile.md`, ảnh / video / PSD có sẵn trong repo (Glob `*.mp4|*.mov|*.png|*.jpg|*.psd`, ngoài `Library/`).
- Slug = `$ARGUMENTS` (từ đầu không phải link / đường dẫn), không có thì tự đặt theo tên repo / thư mục (chữ thường, gạch ngang). **Không hỏi**, hiện trên thẻ.

## 2. Xin tài liệu tham khảo (câu hỏi đầu tiên, duy nhất của lượt này)
`$ARGUMENTS` đã có link / đường dẫn → bỏ qua bước này. Không thì hỏi bằng chữ (câu trả lời tự do, nhiều dòng) rồi **dừng chờ**:
> Gửi mình tài liệu tham khảo cho game (bao nhiêu cũng được, mỗi dòng 1 cái): link store / YouTube / TikTok, file hoặc thư mục video gameplay,
> ảnh, mockup UI, art, PSD, tài liệu thiết kế. Kèm 1–2 câu ý tưởng nếu có. Chưa có gì thì gõ "chưa có" + tên game tương tự.

Nếu thấy file sẵn trong repo ở bước 1, nhắc tên chúng trong câu hỏi ("mình thấy `Buzzy Bus/Video/demo.mp4`, có phải tài liệu tham khảo không?").

## 3. Tự xem tài liệu
`O init --slug <slug>` (tạo `.game/`, task R1 / R2, `.claude/guard.json`). Rồi xem từng nguồn, ghi đường dẫn / URL vào `.game/intake.md` mục 2:
- **Link store** (Google Play / App Store): WebFetch tên game, thể loại, mô tả, số tải, ảnh chụp; ghi cơ chế, meta, kiểu quảng cáo / IAP thấy được.
- **YouTube / TikTok**: WebFetch tiêu đề + mô tả; không xem được hình → ghi "cần frame" (người dùng tải video về thì trích frame được).
- **Video file**: `python "${CLAUDE_PLUGIN_ROOT}/scripts/frames.py" <video> <ổ tạm>/frames/<tên> --sheet` rồi Read `sheet.jpg` + vài frame
  (ổ tạm: `D:/tmp` nếu có, không thì scratchpad; không để trong repo). Ghi: vòng chơi 1 level, thao tác, thắng / thua, UI (HUD, nút), meta.
- **Ảnh / mockup / art**: Read ảnh (thư mục nhiều ảnh: xem tối đa ~12 ảnh tiêu biểu). PSD: chỉ ghi tên + kích thước, xử lý ở pipeline art.
- **Chỉ có tên game tương tự**: WebSearch tên game + "gameplay", lấy trang store.
- **Thư mục base / dự án Unity**: liệt kê `Assets/` cấp 1–2, Unity version, có framework nào (popup, UI, SDK). R2 sẽ đọc kỹ.
Gom kết quả thành thẻ tóm tắt.

## 4. Thẻ "Mình hiểu như sau" + hỏi phần thiếu
Hiện bảng (mỗi dòng: mục · giá trị · nguồn: link / file / *(đoán)* / *(mặc định)*):
slug, cơ chế chính, vòng chơi 1 level, thắng / thua, điểm khác biệt, nền tảng, base, số level bản đầu, tính năng meta,
SDK (chỉ tên), ngôn ngữ, art / Spine, file bí mật chặn trong guard.

Mặc định khi không có dữ liệu (ghi *(mặc định)*, không hỏi): nền tảng Android + iOS · ngôn ngữ như game GPlay trước ·
SDK quảng cáo + Firebase Analytics · guard chặn thêm `.keystore`, `.jks`, `google-services.json`, `GoogleService-Info.plist`.

Rồi **một lượt AskUserQuestion** chỉ gồm các mục quan trọng còn mơ hồ (thường: cơ chế khi tài liệu cho nhiều hướng, base khi có nhiều ứng viên,
số level / phạm vi bản đầu, điểm khác biệt). Phương án lấy từ thẻ ("Giống game X", "X + thêm Y"...). Không có gì mơ hồ → bỏ qua lượt này.
Trả lời mở ra mơ hồ mới thì được thêm tối đa 1 lượt.

## 5. Ghi + chốt G0
- Cập nhật thẻ theo câu trả lời, hiện lại, rồi AskUserQuestion "Ghi vào `.game/intake.md`?": `Ghi (Recommended)` / `Sửa 1 mục` / `Chưa ghi`.
  Chỉ ghi khi chọn Ghi. Sửa → hỏi mục nào (bằng chữ), hiện thẻ lại, hỏi lại.
- Ghi: điền mọi mục của `.game/intake.md` (giữ nhãn *(đoán)* / *(mặc định)*), thêm bí mật vào `secrets` của `.claude/guard.json`
  (chỉ tên / đuôi file, không đọc nội dung). Frame video đã trích: ghi đường dẫn vào intake mục 2 để R1 dùng.
- Chưa có `AGENTS.md` / `.claude/game-profile.md` → ghi 1 dòng "tạo ở bước plan" (mẫu `${CLAUDE_PLUGIN_ROOT}/templates/`).
- `O log G0 "intake xong: <cơ chế>, <số nguồn> nguồn tham khảo"` → làm tiếp như `/gplay-game:continue` (chạy R1 / R2).
