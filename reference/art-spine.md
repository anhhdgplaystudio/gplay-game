# Art + Spine

## Sprite

- 100 px / unit, canvas dọc 1080×1920; vùng cảnh thường chừa HUD trên + banner dưới.
- Kích thước bội số 4 (nén ETC2 / ASTC không lỗi, không padding thừa).
- Gom sprite UI vào Sprite Atlas theo màn; sprite level theo level (tránh 1 atlas khổng lồ).
- Thứ tự vẽ: `sortingOrder` (layer +2), không dựa vào thứ tự Hierarchy.
- Art có viền trong suốt lệch: căn theo phần nhìn thấy (script đo bbox alpha).

## Spine

- Ghi rõ **phiên bản Spine export = runtime spine-unity** trong game-profile (3.8 ≠ 4.x, không đọc lẫn).
- Atlas: giữ kích thước gốc, không mipmap; importer tự đặt.
- Quầng sáng theo khung mesh → atlas xuất straight alpha: material `_StraightAlphaInput = 1` (hoặc xuất premultiplied + tắt cờ).
- Art hay chia trạng thái bằng **skin**; không có skin default → phải đặt skin. Ghép skin: `Skin.AddSkin`.
- Trước khi viết dữ liệu level: dump slot / skin / animation của mọi skeleton ra file (tool editor `-executeMethod`), không đoán tên.
- Tên region trong Spine nên trùng tên layer PSD; không trùng → `names.json` `{"names":[{"spine":"Hoa 1","layer":"item1.1"}]}`.
- Gốc khung xương: thống nhất (vd góc trên-trái canvas, hoặc `origin.cor`) để importer đặt đúng chỗ.
- Đồ bám tay nhân vật: `BoneFollower` theo xương của slot.
- Spine tràn ra ngoài khung cảnh: cắt riêng Spine đó, không cắt toàn cảnh.
- Không có anim làm tay: sinh anim thở / đung đưa tự động (shader sway hoặc Spine sinh bằng tool); anim làm tay luôn ưu tiên.

## Âm thanh / voice

- Voice theo key text: `Audio/Voice/Level_XXX/<key>.ogg`, menu tự gán vào level; reimport tự gán lại.
- SFX chung qua 1 manager, tên theo sự kiện (`tap`, `correct`, `wrong`, `win`, `lose`, `coin`).
