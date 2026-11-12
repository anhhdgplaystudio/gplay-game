# Art theo yêu cầu (Codex / Gemini vẽ)

Art **không phải một bước cố định** của pipeline. Mặc định game dùng hình tạm: khối / sprite đơn sắc đúng kích thước + đúng bố cục theo visual-spec,
đủ để kiểm luật và bố cục. Chỉ vẽ khi **người dùng yêu cầu** ("vẽ lại UI", "làm icon", "vẽ nền"...). Không tự ý sinh art, không tự dựng model 3D.

## Hỏi trước khi vẽ (1 lượt AskUserQuestion, bỏ câu đã rõ)

- Vẽ gì: bộ UI / icon / nền / logo / bảng thiết kế nhân vật, vật thể.
- Dùng công cụ nào: Codex (`codex exec`, có sinh ảnh) hay Gemini (`agy` / gemini CLI). Kiểm công cụ có trên máy trước khi đưa làm phương án.
- Phong cách: theo ảnh chuẩn nào trong visual-spec, khác game gốc ở đâu (không sao chép nhân vật / logo của game gốc).

## Quy trình

1. **Brief** `.game/art/<tên>/BRIEF.md` (mẫu `templates/art-brief.md`): danh sách file, **kích thước pixel thật từng file** (đúng cỡ sẽ hiện trong game ở độ phân giải thiết kế,
   vd 1080×1920), nền trong suốt hay không, vùng 9-slice (nếu phải co giãn), bảng màu (từ `palette.png`), ảnh tham chiếu (đường dẫn), điều cấm.
   Một vật thể dùng ở nhiều nơi (logo, loading, home, trong game) → **1 bảng thiết kế chung**, vẽ từ đó ra, ghi rõ trong brief.
2. **Vẽ** ở thư mục tạm ngoài repo (`<tmp>/art/<tên>`), không cho công cụ ghi vào repo:
   - Codex: `codex exec --skip-git-repo-check -C <tmp>/art/<tên> -s workspace-write -o <tmp>/art/<tên>/last.md "Read BRIEF.md in this folder and do everything in it"` (đóng stdin: `< /dev/null`).
   - Gemini: `agy -p "<prompt>" --mode accept-edits --add-dir <tmp>/art/<tên>`.
3. **Kiểm bằng script trước, bằng mắt sau**: mỗi file đúng kích thước brief, có alpha khi cần, không bị cắt mép (viền trong suốt ≥ 2 px với hình có bóng / viền),
   không dính nền. Read từng ảnh (hoặc 1 sheet ghép). Sai → gửi lại danh sách lỗi cụ thể cho công cụ, tối đa 3 vòng rồi báo người dùng.
4. **Đưa vào game** bằng editor script (không sửa tay YAML): import đúng kiểu (Sprite, không nén mờ UI), dựng UI **đúng kích thước gốc**.
5. **Kiểm trong game**: tự kiểm méo (dưới) + chụp ảnh, ghép cạnh ảnh chuẩn. Báo người dùng kèm đường dẫn ảnh.
6. Ghi `O log ART "<tên>: <n> file, công cụ, thư mục>"`; chép `BRIEF.md` + ghi chú nguồn gốc vào `.game/art/<tên>/`.

## Luật

- **Không kéo dãn**: ảnh UI hiện đúng tỉ lệ gốc (native size hoặc scale đều 2 chiều). Cần co giãn (thanh, khung popup) → 9-slice có border khai báo, không scale lệch.
  Dự án nên có hàm kiểm tự động trong tự chơi: duyệt mọi `Image` không phải Sliced / Tiled, báo lỗi khi tỉ lệ rect lệch tỉ lệ sprite > 2%.
- Chữ trong ảnh: không nhúng chữ cần dịch vào ảnh (trừ logo); chữ là TMP + key localization. Font phải có đủ glyph mọi ngôn ngữ bản đầu (kiểm glyph thiếu trong tự chơi).
- Asset bên thứ ba / bóc từ game khác chỉ để trong thư mục placeholder riêng, có danh sách phải thay trước phát hành.
- Model 3D: AI dựng model từ bản vẽ thường không đạt (đã thử: code ghép khối, Blender script). Cần model đẹp → nói thẳng với người dùng:
  dùng hình tạm + đưa bảng thiết kế cho 3D artist, hoặc dùng asset có sẵn người dùng chỉ định.
- Art sinh ra phải được người dùng duyệt trước khi dùng làm chuẩn cho phần khác.
