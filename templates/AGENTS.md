# AGENTS.md — <Tên game>

Luật cho mọi AI agent (Claude, Codex, Gemini). Giữ file này ≤ 100 dòng; chi tiết ở `.claude/game-profile.md` và tài liệu trong `Docs/`.

## Dự án

- Unity <phiên bản>, <2D / 3D> mobile dọc. Cơ chế (luật đầy đủ: `.game/research/teardown.md`): <3 dòng tóm tắt luật lõi>.
- Hình màn chơi theo `.game/research/visual-spec.md` (ảnh chuẩn: `<đường dẫn>`).
- Code game: `<thư mục>`; framework: `<thư mục>`. Scene: `<thư mục>` (script build cố định đường dẫn).
- Level: `<Levels>/Level_XXX.prefab`, dựng từ `<art>/Level XXX/dev` bằng `<menu importer>`.

## Luật bắt buộc

1. Namespace `<NS>` cho file C# mới / đang sửa (editor: `<NS>.EditorTools`).
2. Không sửa tay YAML scene / prefab / asset; không xoá / sinh lại `.meta`.
3. Không ghi đè prefab level đã chỉnh tay khi chưa được đồng ý.
4. Logic riêng 1 level → `LevelControllerN`, không thêm vào class base.
5. Không đọc / in / copy: <danh sách file bí mật>. Không đụng cấu hình SDK, keystore.
6. Chỉ commit khi người dùng yêu cầu.
7. File nặng (build, cache, video, ảnh test) để `<ổ / thư mục tạm>`.
8. Comment + chuỗi UI tool: <ngôn ngữ>, ngắn, giống code xung quanh.
9. Text mới: key localization, đẩy lên sheet (`<lệnh>`).

## Kiểm tra

- Build: `dotnet build Assembly-CSharp-Editor.csproj -nologo -v q` (file `.cs` mới phải thêm vào csproj trước).
- Validator level: `<lệnh>`.
- Tự chơi (Unity đóng): `Unity -batchmode -projectPath . -executeMethod <NS>.EditorTools.PlayTest.RunFromCommandLine -levels N -out <thư mục>`; xem hết ảnh.

## Quy trình 1 level

1. Art → `dev/` (PNG + .cor + mapping.json). 2. Importer dựng prefab. 3. Refresh database.
4. Voice / text. 5. Validator + tự chơi.

- So hình: `python <plugin>/scripts/side_by_side.py <ảnh chuẩn> <ảnh game> <ra.jpg> --grid 10`. Báo kết quả kèm đường dẫn đầy đủ từng ảnh.

## Bài học (thêm khi gặp lỗi lặp lại)

- Lệnh bị từ chối quyền: KHÔNG gọi vòng (script tạm, wrapper). Ghi lệnh vào báo cáo để người điều phối chạy.
- Đổi `ProjectSettings` / scene / prefab qua editor script (`-executeMethod`), guard chặn sửa tay.
- <...>
