# Đề bài level <NNN> (<cơ chế>)

Đọc trước: `AGENTS.md`, `Tools/AgentLevels/RULES.md`.

## Nguồn
- Art: `<art>/Level <NNN>/dev` (hoặc dev_lv) · Spine: `<anim>/Level<N>-ani/` (dump: `<file dump>`)
- Video / kịch bản: <link / file> · ảnh demo: <thư mục>

## Được ghi
- `<art>/Level <NNN>/` (dev_lv, file level json, Tools~/)
- `<code>/Levels/LevelController<N>.cs` (nếu cần diễn biến riêng)
- `<art>/Level <NNN>/Tools~/loc.csv` (key text mới: key,en,vi)

## Không được
- Sửa base class, importer, prefab khác, YAML; xoá `.meta`; đọc file bí mật.

## Diễn biến cần làm
1. <bước 1: vật, vùng, người nói, câu>
2. ...

## Tự kiểm trước khi báo
- Validator: `<lệnh>` không lỗi.
- Ảnh preview từng bước (vùng thả, bong bóng) đã xem, so với video.
- Build kiểm tra controller.

## Báo cáo (`REPORT.md`)
File đã đổi · key mới · bước chưa chắc (vì sao) · ảnh preview đã xem · lỗi còn lại.
