# Luật chung GPlay (mọi game)

Luật thêm bằng `/gplay-game:learn` (loại "luật bắt buộc mọi game"). Mỗi luật 1 dòng bắt đầu bằng `- `: phiên chính chép các dòng này vào đề giao cho subagent / Codex / Gemini. Luật cứng gốc nằm ở SKILL.md; luật riêng 1 dự án ghi vào AGENTS.md của dự án đó.
Luật kiểm được bằng máy (cấm sửa đường dẫn, cấm lệnh, file bí mật) ghi thêm vào `guard.json` cạnh file này.

- Lệnh bị từ chối quyền thì không gọi vòng (script bọc, wrapper, đổi shell); ghi nguyên lệnh vào báo cáo để người điều phối chạy.
- Ảnh UI hiện đúng tỉ lệ gốc; cần co giãn thì dùng 9-slice, không scale lệch 2 chiều.
- Báo kết quả có hình thì kèm đường dẫn đầy đủ tới từng ảnh.
- Tự kiểm xong chỉ được báo "chờ duyệt" kèm các điểm còn lệch so với mẫu; "xong" là lời của người dùng.
- Góp ý của người dùng ghi lại nguyên văn trước khi làm; diễn giải ghi riêng, có 2 cách hiểu thì hỏi lại kèm ảnh.
