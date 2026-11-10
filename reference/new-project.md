# Mở dự án game mới

## 1. Hỏi người dùng (ngắn, 1 lần)

- Tên game, package id, nền tảng (Android / iOS), phiên bản Unity.
- Cơ chế chính (xem [mechanics.md](mechanics.md)) và cơ chế phụ nếu có.
- Clone từ base / dự án nào? (giữ framework nào, bỏ gì).
- Namespace cho code mới, thư mục code game.
- Có mockup UI, art mẫu, video mẫu chưa? Ở đâu?
- Nguồn text: Google Sheet localization (id) hay file local? Bao nhiêu ngôn ngữ?
- SDK quảng cáo / analytics / IAP dùng gì (chỉ hỏi tên, **không** hỏi key).

Không đoán các giá trị này. Thiếu thì để `TODO` trong game-profile và nhắc.

## 2. Dựng từ base template

Nếu clone từ dự án cũ có framework chung (vd `0GAME` + `01_BaseCode`: `PopUp<T>`, `LoadingPanel`, `MusicManager`, 3 scene Loading / Home / Gameplay):

1. **Giữ** framework (popup, UI, loading, audio, SDK wrapper, IAP / ads controller). **Xoá** gameplay core cũ + level + art riêng.
2. GameplayScene → placeholder có 1 entry script cho game mới.
3. Thêm mode mới vào enum `GameMode` (thường ở `Datas/GameEnums.cs`).
4. Đường dẫn scene: tìm script build (vd `ConfigBuild.cs`) có đường dẫn cố định → giữ scene đúng chỗ hoặc sửa script.
5. **Đổi identity**: productName, package id, icon, version về 1.0 / code 1.
6. Tìm tàn dư game cũ: `grep -ri "<tên game cũ>|keystore|folderPath"` trong script build. Script build thường còn
   đường dẫn keystore / thư mục build của game cũ.
7. Ghi rõ cho người dùng danh sách **phải thay trước khi phát hành**: keystore, `google-services.json`, ad unit id, IAP product id,
   AppsFlyer / Firebase key. Không tự sửa các file này.

Dự án trắng (không base): tạo 3 scene Loading / Home / Gameplay, singleton audio, hệ popup đơn giản, lưu dữ liệu (PlayerPrefs hoặc json).

## 3. Tài liệu cho agent

- `AGENTS.md` (từ `templates/AGENTS.md`): **≤ 100 dòng**, chỉ luật cứng + thứ agent không tự tìm ra được. Chi tiết trỏ sang file khác.
  Agent khác (Codex đọc `AGENTS.md`, Gemini đọc `GEMINI.md`) không nạp skill của Claude → `GEMINI.md` chỉ `@./AGENTS.md`, `CLAUDE.md` cũng vậy.
- `.claude/game-profile.md` (từ `templates/game-profile.md`): giá trị riêng dự án.
- Hook: chép `templates/guard.json` vào `.claude/guard.json` (bật hook guard của plugin), thêm file bí mật riêng vào `secrets`.

## 4. Kiểm tra biên dịch không cần Unity

- Mở Unity 1 lần để sinh `.csproj` (Preferences > External Tools > Regenerate project files).
- `dotnet build Assembly-CSharp-Editor.csproj -nologo -v q`, chỉ xem dòng ` error `.
- File `.cs` mới chưa có trong csproj tới khi Unity mở lại → `scripts/check_build.py` thêm vào bản tạm.
- Unity vẫn là nơi quyết định cuối (define, asmdef, Editor-only).

## 5. Thứ tự sau khi mở

1. Prototype cơ chế: **1 level dựng tay chơi được** + hàm tự giải (playbook trong mechanics.md).
2. Chốt định dạng level dữ liệu + importer + validator ([level-pipeline.md](level-pipeline.md)).
3. Làm 3–5 level thật qua pipeline, chạy thử → sửa pipeline.
4. UI theo mockup + vòng meta.
5. Sản xuất hàng loạt.
