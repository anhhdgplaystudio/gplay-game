---
id: R2
title: Đọc base dự án
kind: research
model: sonnet
budget: 3
---
## Việc cần làm (chỉ đọc, không sửa repo)
1. Unity version (`ProjectSettings/ProjectVersion.txt`), package chính (`Packages/manifest.json`), SDK có trong Assets.
2. Cấu trúc thư mục, scene, framework tái dùng được (popup, loading, audio, lưu dữ liệu, ads / IAP wrapper): class chính + cách dùng.
3. Gameplay / level / art cũ cần xoá; tàn dư identity (productName, package id, keystore path, tên thư mục build trong script build).
   Chỉ ghi đường dẫn file, KHÔNG đọc nội dung keystore / google-services / file key.
4. Tool editor sẵn có (menu, builder, importer), script ngoài Unity, test có sẵn.
5. Cách build kiểm tra không cần Unity (csproj có sẵn chưa), rủi ro kỹ thuật.
6. Đối chiếu `.game/intake.md`: base hỗ trợ cơ chế mới tới đâu, phải viết mới gì.

## Kết quả (ghi vào .game/research/R2.md)
Mục: Tóm tắt · Giữ lại (đường dẫn + vai trò) · Xoá · Tàn dư phải đổi · Tool sẵn có · Thiếu / phải viết mới · Rủi ro · Đề xuất game-profile (giá trị điền sẵn).
