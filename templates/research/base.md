# Đọc base dự án — đề cho subagent (chỉ đọc, không sửa repo)

Ghi kết quả vào `.game/research/base.md`. Chỉ ghi đường dẫn file bí mật, KHÔNG đọc nội dung keystore / google-services / file key.

1. Unity version (`ProjectSettings/ProjectVersion.txt`), render pipeline, package chính (`Packages/manifest.json`), SDK có trong Assets.
2. Cấu trúc thư mục, scene, asmdef; framework dùng lại được (popup, loading, audio, lưu dữ liệu, ads / IAP wrapper): class chính + cách dùng.
3. Gameplay / level / art cũ cần xoá; tàn dư identity (productName, package id, đường dẫn keystore, tên thư mục build trong script build).
4. Tool editor sẵn có (menu, builder, importer), script ngoài Unity, test có sẵn.
5. Cách compile / test không mở Editor: csproj có sẵn chưa, dự án dùng asmdef hay Assembly-CSharp, lệnh batchmode nào chạy được.
6. Thư mục asset bên thứ ba (bóc từ game khác, mua ngoài): ở đâu, chỉ được dùng làm gì.
7. Đối chiếu `.game/intake.md` + `.game/research/teardown.md` (nếu đã có): base hỗ trợ cơ chế tới đâu, phải viết mới gì.

Mục kết quả: Tóm tắt · Giữ lại (đường dẫn + vai trò) · Xoá · Tàn dư phải đổi · Tool sẵn có · Lệnh kiểm tra dùng được ·
Thiếu / phải viết mới · Rủi ro · Đề xuất game-profile (giá trị điền sẵn).
