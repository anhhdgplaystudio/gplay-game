# UI theo mockup

## Quy trình

1. Mockup 1080×1920 mỗi màn (`UI/DEMO/<màn>.jpg`) + slice art (`UI/dev/<màn>/*.png`).
2. Script tìm vị trí từng slice trong mockup (OpenCV template match) → `UILayout/<màn>.json`: `{ name, sprite, x, y, w, h }`,
   `x, y` = **tâm cả ảnh** (kể cả viền trong suốt).
3. Builder (editor) đọc json dựng prefab màn / popup. Không kéo tay vị trí → dựng lại được.
4. Preview ngoài Unity: ảnh 3 cột mockup / dựng lại / trộn 50% để so lệch.

Script nên có: `make_layouts`, `preview <layout>`, `crop <mockup> x0 y0 x1 y1` (phóng + lưới để đọc toạ độ),
`region_match`, `art_padding` (art có viền trong suốt lệch), `sheet <thư mục>` (bảng xem nhanh slice).

## Luật

- Art **giữ kích thước gốc**, vị trí khớp mockup; không thu nhỏ nút để lấy chỗ.
- **Không kéo dãn**: `Image` hiện đúng tỉ lệ sprite (SetNativeSize hoặc scale đều); phần phải co giãn (thanh, khung popup, nút dài theo chữ) dùng 9-slice có border,
  hoặc vẽ riêng đúng cỡ. Tự chơi có bước kiểm méo tự động (verification.md).
- Chưa có mockup / art: dựng UI tạm bằng khối màu **đúng vị trí + kích thước theo visual-spec**; art thật vẽ khi người dùng yêu cầu ([art-on-demand.md](art-on-demand.md)),
  brief ghi kích thước pixel thật từng file lấy từ layout này.
- Font: chọn font đủ glyph cho mọi ngôn ngữ bản đầu ngay từ đầu (tiếng Việt cần dấu); 1 font chính cho cả game, kiểm glyph thiếu + chữ tràn ở từng ngôn ngữ.
- HUD không đè lên vùng chơi: chia vùng theo % của visual-spec.
- Banner thật cao hơn banner trong mockup thường ~30 px → phần tử bám đáy nâng thêm (1 hằng số chung).
- Safe area (tai thỏ) cho HUD trên; thử tỉ lệ 9:16, 9:19.5, 9:21, tablet 3:4.
- Text dùng 1 prefab chuẩn (font, Best Fit, Min = ½ Max), gắn component localize, không gõ chữ cứng.
- Popup kế thừa base popup (hiện / ẩn có anim, singleton `Instance`, `ShowPopUp` / `ClosePopUp`).
- Mỗi popup / màn có builder menu riêng (đánh số để chạy lại theo thứ tự).

## Màn thường có ở game casual

Loading · Home (danh sách level / nút Play) · Gameplay HUD (level, thời gian, tiến trình `done/total`, hint, pause) ·
Pause · Win (coin, nút video nhân thưởng) · Lose (hồi sinh bằng video / chơi lại) · Daily reward · Lucky spin ·
Shop / Remove ads / Starter pack · Rate · No internet · Unlock level · Settings (âm thanh, rung, ngôn ngữ).
