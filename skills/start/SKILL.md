---
name: start
description: Bắt đầu dự án game mới theo pipeline GPlay - tạo .game/, bật guard, hỏi intake bằng hộp chọn (AskUserQuestion).
disable-model-invocation: true
argument-hint: "[tên-game]"
---
# /gplay-game:start

`O = python "${CLAUDE_PLUGIN_ROOT}/scripts/orch.py"`, chạy ở gốc repo dự án.
Quy trình đầy đủ: `${CLAUDE_PLUGIN_ROOT}/reference/pipeline.md`. Luật chung: skill `gplay-game` + `${CLAUDE_PLUGIN_ROOT}/RULES.md`.

**Cách hỏi:** mọi câu hỏi người dùng chọn được thì hỏi bằng tool **AskUserQuestion**, không liệt kê câu hỏi thành chữ trong chat.
Mỗi lượt tối đa 4 câu, mỗi câu 2–4 phương án, phương án khuyến nghị đặt đầu và thêm "(Recommended)", `header` ≤ 12 ký tự.
Phương án lấy từ thứ đã thấy trong repo (tên thư mục, file có sẵn), không bịa. Ô "Other" có sẵn để người dùng gõ tự do (link, mô tả).
Câu đã có trả lời (từ `$ARGUMENTS`, intake.md đã điền) thì bỏ qua.

1. Đã có `.game/` → không init lại; báo người dùng dùng `/gplay-game:continue`. Dừng.
2. Xem nhanh gốc repo (thư mục, `ProjectSettings/ProjectVersion.txt`, `AGENTS.md`) để làm phương án cho câu hỏi.
   Tên game = `$ARGUMENTS`; trống → AskUserQuestion "Tên game (slug)?" với 2 phương án suy từ tên repo / thư mục.
3. `O init --slug <tên>`: tạo `.game/` (intake, config, lịch sử, task R1 / R2) và `.claude/guard.json` (chặn sửa YAML / .meta / bí mật).
4. **Lượt 1** (AskUserQuestion, 4 câu):
   - `Cơ chế`: cơ chế chính (phương án theo tên game + `${CLAUDE_PLUGIN_ROOT}/reference/mechanics.md`);
   - `Nền tảng`: Android + iOS / Android / iOS;
   - `Base`: thư mục lạ ở gốc repo (vd `Buzzy Bus/`) là base / clone base template GPlay / dự án Unity đang mở là base;
   - `Bí mật` (multiSelect): file bí mật chặn thêm trong guard.json: keystore (`*.keystore`, `*.jks`), `google-services.json`,
     `GoogleService-Info.plist`, không thêm. Chỉ ghi tên / mẫu file vào `secrets`, không đọc nội dung.
5. **Lượt 2** (AskUserQuestion, 4 câu):
   - `Số level`: số level bản đầu (vd 20 / 50 / 100);
   - `Tính năng` (multiSelect): hint, daily reward, lucky spin, shop / IAP;
   - `SDK` (multiSelect): quảng cáo (AdMob / AppLovin MAX), Firebase Analytics, Unity IAP, chưa chọn (chỉ tên, không key);
   - `Ngôn ngữ`: chỉ EN / EN + VI / đủ bộ ngôn ngữ như game GPlay trước.
6. **Lượt 3** (AskUserQuestion, 2 câu, câu trả lời tự do qua "Other"):
   - `Ý tưởng`: mô tả ngắn người chơi làm gì, thắng / thua (phương án: "Gõ ở Other", "Điền vào intake.md", "Lấy theo game tham khảo");
   - `Tham khảo`: link store / video / ảnh / mockup (phương án: "Dán link ở Other", "Điền vào intake.md", "Chưa có, tự tìm theo cơ chế").
7. Sau mỗi lượt chép câu trả lời vào đúng mục của `.game/intake.md`; bí mật → thêm vào `secrets` của `.claude/guard.json`.
   Chưa có `AGENTS.md` / `.claude/game-profile.md` → ghi 1 dòng "tạo ở bước plan" (mẫu `${CLAUDE_PLUGIN_ROOT}/templates/`).
8. Báo ngắn: những gì đã ghi vào intake (bảng 2 cột), mục còn trống. Người dùng chọn "Điền vào intake.md" ở câu nào thì dừng chờ họ điền.
9. Đủ thông tin → `O log G0 "intake xong"` → làm tiếp như `/gplay-game:continue`.
