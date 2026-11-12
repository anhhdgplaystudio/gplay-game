# Game profile — <Tên game>

Skill `gplay-game` đọc file này trước. Giá trị chưa biết để `TODO`.

## Định danh
- Tên / package id: TODO
- Unity: TODO · Spine runtime: TODO (phải trùng bản export)
- Clone từ: TODO (giữ: ..., bỏ: ...)

## Code
- Namespace: TODO (editor: TODO.EditorTools)
- Thư mục code game: TODO · framework: TODO
- Scene: TODO (script build cố định đường dẫn: TODO)
- Enum mode: TODO
- Menu tool: `Tools/<Tên game>/...`

## Cơ chế
- Luật lõi (tóm tắt từ `.game/research/teardown.md`, sửa teardown trước rồi mới sửa ở đây): TODO
- Hình + luồng màn: `.game/research/visual-spec.md` · ảnh chuẩn: TODO (đường dẫn)

| Cơ chế | Runtime | Importer | File dữ liệu |
|---|---|---|---|
| TODO | | | |

## Level
- Prefab: `TODO/Level_XXX.prefab` · Database: TODO · menu Refresh: TODO
- Art: `TODO/Level XXX/{demo,dev,dev_lv}` · Spine: TODO
- Canvas: 1080×1920, 100 px/unit, vùng cảnh y = TODO..TODO
- Quy ước tên layer: TODO (file)
- Video / kịch bản mẫu: TODO

## Text / âm thanh
- Sheet localization id: TODO · số ngôn ngữ: TODO · file Extra: TODO · lệnh đẩy: TODO
- Voice: `TODO/Voice/Level_XXX/<key>.ogg`

## Bí mật (agent không đọc)
- TODO (keystore, google-services.json, file key SDK, token web app)

## Lệnh
- Build / compile: `dotnet build Assembly-CSharp-Editor.csproj -nologo -v q` (dự án dùng asmdef riêng: TODO lệnh compile Unity batchmode)
- Test logic thuần: TODO
- Validator (kèm ngưỡng độ khó): TODO
- Tự chơi + chụp ảnh (Unity đóng, chạy có GPU, không `-nographics`): TODO · ảnh ra: TODO (ổ tạm)
- Art tạm / bên thứ ba phải thay trước phát hành: TODO (thư mục + lệnh kiểm)
- Dump Spine: TODO

## Quảng cáo / analytics
- SDK: TODO · khoảng cách interstitial: TODO · level không quảng cáo: TODO

## Bài học riêng dự án
- (ghi khi gặp: level nào, lỗi gì, cách tránh)
