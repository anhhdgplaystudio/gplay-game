# Bài học chung (từ các dự án trước)

Mỗi dòng: bài học · nguồn (dự án / level) · ngày. Bài học chỉ đúng 1 dự án → ghi vào game-profile của dự án đó.

- Base clone từ game cũ mang theo keystore, google-services, đường dẫn build, tên thư mục của game cũ → grep và liệt kê cho người dùng ngay khi mở dự án · Fashion Puzzle · 2026-10
- Prefab level có nhân vật anim + vị trí chỉnh tay → importer không bao giờ ghi đè mặc định · Fashion Puzzle · 2026-10
- Art không theo quy ước tên → sinh thư mục `dev_lv` đặt lại tên, không sửa importer cho 1 level; script sinh không xoá `.meta` · Fashion Puzzle · 2026-10
- Số màn = vị trí trong database; thiếu 1 prefab làm lệch mọi màn sau · Fashion Puzzle · 2026-10
- Vùng thả phủ cả cảnh → thả bừa cũng đúng; validator phải kiểm diện tích + chồng vùng · Annoy lv10 · 2026-10
- `mapping.json` sắp theo tên → tường đè lên người; giữ thứ tự PSD / slot Spine · Annoy lv48 · 2026-10
- Bật cắt khung toàn cảnh làm sprite hiện từ đầu vỡ hình; chỉ cắt Spine tràn · Annoy lv50 · 2026-10
- Spine chia trạng thái bằng skin, không có skin default → phải dump skin trước khi viết dữ liệu · Annoy · 2026-10
- Atlas Spine straight alpha hiện quầng theo mesh → `_StraightAlphaInput = 1` · Annoy lv47 · 2026-10
- Kiểm "mọi tên tồn tại" không bắt được lỗi bố cục / người nói; phải ghép ảnh + so video · Annoy · 2026-10
- Nhiều Codex + build song song làm treo máy; mặc định tuần tự · 2026-10
- Banner thật cao hơn banner trong mockup ~30 px; art UI có viền trong suốt lệch 4–8 px ở đáy · UI · 2026-10
