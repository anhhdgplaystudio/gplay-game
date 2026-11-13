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
- Lập luật chơi từ mô tả store + ảnh tĩnh → sai thứ người chơi chạm vào và sai chiều bố cục, phải viết lại luật 2 lần; bắt buộc xem video gameplay, mỗi luật gắn frame · dự án thử pipeline · 2026-11
- Hỏi người dùng "luật game gốc thế nào" khi chưa tự xem video: câu trả lời theo trí nhớ vẫn sai; tự soi rồi chỉ hỏi kèm frame đang phân vân · 2026-11
- Chuyển động (vật vào / ra đường nào, thứ tự) không đọc được từ frame rời; phải trích đoạn frame liên tiếp (`study_video.py --clip`) · 2026-11
- Phân tích hình phải tới từng vật thể (khối hay nhân vật có mặt, nền trơn hay chia ô, mái che, bóng); có asset gốc thì dựng lại model / sprite để soi; tả chung chung → người dùng chê từng chi tiết qua 6 vòng · 2026-11
- Làm đủ meta + UI + 30 level trước khi người dùng duyệt 1 level mẫu → sửa luật / bố cục kéo theo làm lại mọi thứ; phải có cổng duyệt level mẫu · 2026-11
- Quên luồng màn (Loading → Home → Game) trong plan vì chỉ phân tích màn chơi · 2026-11
- Mỗi task 1 phiên claude CLI riêng mà không có git: không song song được, worker không chạy được Unity có GPU, 20/33 task phải đóng tay; mặc định phiên chính tự làm · 2026-11
- Windows: worker dùng PowerShell là chính, quyền chỉ có `Bash(...)` → bị từ chối hàng loạt; lệnh ghép (`cd x; python y`, pipe, for) bị từ chối dù từng lệnh được phép · 2026-11
- Worker bị chặn lệnh sẽ tìm đường gọi vòng (script tạm gọi Unity.exe) nếu không cấm rõ · 2026-11
- Unity batchmode `-nographics` không chụp được ảnh; tự chơi có ảnh phải chạy có GPU ở phiên có quyền · 2026-11
- Extension Claude Code tự cập nhật đổi đường dẫn claude.exe; không ghi cứng đường dẫn có số phiên bản · 2026-11
- Nút / khung UI bị kéo dãn khi đặt sprite vào rect khác tỉ lệ; vẽ đúng kích thước thật + kiểm méo tự động trong tự chơi · 2026-11
- Chữ có dấu rơi về font dự phòng (2 kiểu chữ trên 1 màn), chữ dịch tràn nút; chọn font đủ glyph từ đầu + kiểm glyph thiếu + chụp từng ngôn ngữ · 2026-11
- 1 vật thể xuất hiện ở logo, loading, home, trong game mà vẽ rời từng chỗ → không đồng nhất; phải có 1 bảng thiết kế chung · 2026-11
- AI tự dựng model 3D từ bản vẽ (code ghép khối, Blender script) qua nhiều vòng vẫn không đạt; hỏi sớm nguồn model, mặc định hình tạm · 2026-11
- Level sinh tự động "giải được" nhưng chạm bừa cũng thắng (17/30 level); validator phải có ngưỡng độ khó (tỉ lệ thắng khi chơi ngẫu nhiên) · 2026-11
- Báo chi phí bằng USD làm người dùng gói tháng hiểu nhầm là tiền phải trả; ghi rõ "quy đổi" · 2026-11
- Người dùng phải hỏi "bao giờ xong", "tiến độ": báo ước lượng khi bắt đầu mốc và thời gian thực khi xong · 2026-11
- Script dọn tiến trình khi quá giờ mà tắt theo tên (`taskkill /IM Unity.exe`) đã tắt luôn Editor người dùng đang mở; chỉ tắt PID do chính mình khởi chạy · 2026-11
- `pip install uv` có thể đặt `uvx.exe` ngoài PATH (thư mục Scripts của user) → tool cần `uvx` báo "not recognized"; kiểm `pip show -f` · 2026-11
