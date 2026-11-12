# Nghiên cứu game tham khảo (bước quan trọng nhất)

Mục tiêu: trước khi lập plan, phiên chính phải **tự nhìn thấy** game gốc chơi thế nào và trông ra sao, ghi thành 2 tài liệu có bằng chứng:
`.game/research/teardown.md` (luật chơi) và `.game/research/visual-spec.md` (hình + luồng màn). Sai ở bước này = viết lại code về sau.

Phiên chính tự làm (cần xem ảnh, cần hỏi người dùng). Chỉ giao subagent phần đọc nhiều file: thống kê dữ liệu level / config, đọc base (`base.md`).

`<tmp>` = ổ tạm ngoài repo (vd `D:/tmp/<slug>`). `<PLUGIN>` = thư mục plugin.

## Mục lục
1. Thu nguồn · 2. Mổ video · 3. Teardown luật chơi · 4. Spec hình + luồng màn · 5. Dữ liệu có sẵn · 6. Đọc base · 7. Cổng G1 · Lỗi hay gặp

## 1. Thu nguồn (đủ rồi mới phân tích)

Tối thiểu phải có **video gameplay liên tục ≥ 3 phút, từ đầu level tới màn thắng** (tốt nhất 2 video: level đầu có tutorial + level giữa game có đủ cơ chế). Ảnh store / mô tả **không đủ** để suy ra luật.

| Nguồn | Cách lấy | Cho biết |
|---|---|---|
| Trang store | WebFetch link store | Tên, thể loại, mô tả, ảnh chụp, IAP / quảng cáo |
| Video gameplay | Người dùng đưa file; không có thì tự tìm + tải (dưới) | Luật, nhịp, hình, luồng màn, feel |
| Ảnh người dùng gửi | Read | Điều người dùng coi là chuẩn → ưu tiên cao nhất |
| Asset / config / level của game gốc (nếu người dùng có) | Đọc json, thống kê bằng script | Số liệu thật: kích thước bàn, số màu, kinh tế, mốc mở khoá |
| Chơi thật | Người dùng chơi / quay màn hình khi video không trả lời được | Trường hợp biên: thua thế nào, bấm sai thì sao |

Tự tải video (không cài vào hệ thống, không để trong repo):
```
python -m pip install --quiet --target <tmp>/pytools yt-dlp
PYTHONPATH=<tmp>/pytools python -m yt_dlp --no-playlist -f "bv*[height<=1080]+ba/b[height<=1080]/b" -o "<tmp>/ref/%(id)s.%(ext)s" "ytsearch3:<tên game> gameplay walkthrough"
```
(PowerShell: `$env:PYTHONPATH='<tmp>/pytools'; python -m yt_dlp ...`.) Chọn video quay màn hình thật, không phải trailer / quảng cáo dựng.
Không tải được → hỏi người dùng xin file video hoặc quay màn hình; **không** lập luật từ ảnh tĩnh rồi đi tiếp.

## 2. Mổ video

```
python "<PLUGIN>/scripts/study_video.py" <video> <tmp>/study/<tên>
```
→ `sheet.jpg` (lưới frame có nhãn `#số giây`, `CUT` = đổi cảnh: popup, chuyển màn), `frames/`, `palette.png`, `study.json`.
1. Read `sheet.jpg` trước để nắm cả video; ghi lại các mốc: bắt đầu level, thao tác đầu, thắng, popup, đổi level, loading, home.
2. Read từng frame gốc ở mốc quan trọng (sheet thu nhỏ không đọc được số / chữ).
3. **Mọi chuyển động phải soi bằng `--clip`** (vật đi đường nào, cái gì xảy ra trước / sau, mất bao lâu):
   `python "<PLUGIN>/scripts/study_video.py" <video> <tmp>/study/<tên> --clip 20 23 --fps 8` → Read `strip.jpg`.
   Soi ít nhất: 1 thao tác của người chơi từ lúc chạm tới lúc xong · vật thể vào màn / ra màn · thắng 1 level · thua (nếu có) · chuyển màn.

Ảnh tĩnh không cho biết hướng đi, thứ tự, thời gian; đoán từ 1 frame là nguồn lỗi lớn nhất.

## 3. Teardown luật chơi → `.game/research/teardown.md`

Mẫu: `<PLUGIN>/templates/research/teardown.md`. Nguyên tắc:

- Mỗi luật 1 dòng, gắn **bằng chứng**: `[V1 #12 149s]` (video 1, frame 12), `[clip 20–23s]`, `[store]`, `[config <file>]`, `[người dùng]`.
  Không có bằng chứng → ghi `[suy luận]` + cách kiểm (soi đoạn nào, hỏi gì).
- Viết dạng kiểm được: "Chạm X → Y xảy ra", không viết "người chơi sắp xếp hợp lý".
- Bảng **thao tác → phản hồi**: người chơi chạm / kéo cái gì, cái gì di chuyển, đi tới đâu, khi nào bị từ chối.
- Tự hỏi đủ 8 câu, câu nào chưa trả lời bằng frame thì chưa xong:
  1. Người chơi chạm / kéo **vào cái gì**? (thứ được chạm, không phải thứ di chuyển)
  2. Một thao tác tác động **bao nhiêu** vật (1 / cả cụm / cả hàng)?
  3. Vật đi **đường nào, tới đâu**; cái gì chặn nó?
  4. Cái gì **tự động** xảy ra không cần người chơi?
  5. Sức chứa / giới hạn (số ô, số chỗ, số lượt, thời gian)?
  6. **Thắng** khi nào? **Thua** khi nào (đã thấy màn thua chưa)?
  7. Bấm sai / không hợp lệ thì sao?
  8. Cơ chế phụ / booster mở ở level nào, làm gì?
- Vòng meta thấy được: coin, tim, thưởng, mở khoá, quảng cáo (ghi vị trí + frame).
- Đối chiếu [mechanics.md](mechanics.md): khớp playbook nào thì dùng; không khớp → teardown này **là** playbook của dự án
  (ghi tóm tắt vào `.claude/game-profile.md`), không ép về playbook gần giống.

## 4. Spec hình + luồng màn → `.game/research/visual-spec.md`

Mẫu: `<PLUGIN>/templates/research/visual-spec.md`. Đây là thứ để so khi nghiệm thu, nên phải đo, không tả chung chung.

- **Ảnh chuẩn**: chọn 1 frame cho mỗi màn (gameplay giữa level, home, loading, thắng, thua, popup), chép vào `<tmp>/ref/golden/`.
  Người dùng gửi ảnh nào → ảnh đó là chuẩn.
- **Luồng màn**: sơ đồ Loading → Home → Game → Thắng / Thua → ... (lấy từ các frame `CUT`), ghi cách chuyển (fade, trượt).
- **Bố cục màn chơi**: kẻ lưới lên ảnh chuẩn để đọc tỉ lệ:
  `python "<PLUGIN>/scripts/side_by_side.py" <frame> <frame> <tmp>/ref/grid.jpg --grid 10` → ghi mỗi vùng chiếm từ % nào tới % nào theo chiều cao
  (vd HUD 0–8, khu A 8–35, bàn chơi 35–88, thanh dưới 88–100), cái gì ở trên / dưới / trái / phải.
- **Camera**: 2D hay 3D, nhìn từ đâu (thẳng trên, nghiêng bao nhiêu), phối cảnh hay trực giao, hướng "trên màn hình" là hướng nào trong thế giới.
- **Danh mục vật thể**: mỗi thứ nhìn thấy 1 dòng: hình dáng (khối / nhân vật có mặt / bo tròn...), kích thước tương đối, màu, số lượng,
  trạng thái (bình thường / được chọn / khoá...), có chuyển động riêng không. Dựng lại model / sprite gốc nếu có asset: soi tư thế, shader, chi tiết.
- **Chuyển động + feel** (từ `--clip`): mỗi sự kiện: cái gì động, đường đi, thời lượng ước tính, hiệu ứng kèm (nảy, hạt, rung, số bay).
- **UI**: danh mục nút / thanh / popup từng màn, vị trí, kiểu chữ (đậm, viền), màu chủ đạo (lấy từ `palette.png`).
- **Nền / môi trường**: nền trơn hay có hoạ tiết / chia ô, có bóng đổ không.

## 5. Dữ liệu có sẵn (khi người dùng có asset / config game gốc)

Giao 1 subagent (hoặc viết script) thống kê, không đọc tay từng file: số level, kích thước bàn, số màu / loại theo level, mốc mở cơ chế,
bảng kinh tế (giá, thưởng), tham số độ khó. Kết quả ghi mục "Số liệu" của teardown. Asset bên thứ ba **chỉ để tham khảo**:
ghi rõ trong teardown cái gì không được đem vào bản phát hành.

## 6. Đọc base → `.game/research/base.md`

Giao 1 subagent chỉ đọc (mẫu `<PLUGIN>/templates/research/base.md`): Unity version, package, framework dùng lại được, gameplay cũ phải xoá,
tàn dư identity, tool sẵn có, cách compile / test không mở Editor, rủi ro. Chạy song song lúc phiên chính mổ video.

## 7. Cổng G1: không còn "suy luận" ở luật lõi

Trước khi hỏi người dùng:
1. Mục "Luật lõi" của teardown **không còn dòng `[suy luận]`**. Còn → soi thêm clip / tìm video khác; hết cách mới hỏi người dùng,
   và câu hỏi phải **kèm đường dẫn frame** đang phân vân ("ở frame này A hay B?"), không hỏi trống.
2. Viết `.game/questions.md`: chỉ những quyết định thật sự của người dùng (phạm vi bản đầu, khác biệt so với gốc, ai làm art, tên / package id),
   mỗi câu 2–4 phương án có khuyến nghị. **Không hỏi người dùng luật của game gốc** khi video trả lời được.
3. Trình **thẻ đối chiếu**: 5–8 dòng luật lõi + bố cục + luồng màn, mỗi dòng kèm đường dẫn frame bằng chứng, để người dùng sửa chỗ hiểu sai.
4. Hỏi bằng AskUserQuestion; người dùng xác nhận → `O log G1 "<tóm tắt>"`, `O phase plan`.

Người dùng sửa 1 luật sau G1 → cập nhật teardown / visual-spec **trước**, rồi mới sửa plan / code; ghi `O log NOTE`.

## Lỗi hay gặp (đã gặp thật)

- Lập luật từ mô tả store + ảnh tĩnh → sai đối tượng người chơi chạm vào, sai chiều bố cục; phải viết lại luật 2 lần.
- Hỏi người dùng "luật thế nào?" thay vì tự xem video: người dùng trả lời theo trí nhớ, vẫn sai.
- Tả hình bằng lời ("nhìn từ trên xuống") không kèm ảnh chuẩn + tỉ lệ → dựng ngược hướng, sai tỉ lệ.
- Bỏ qua chuyển động (vật vào / ra đường nào) vì chỉ xem frame rời.
- Coi vật thể là "khối" trong khi gốc là nhân vật có mặt / model riêng → người dùng chê "chỉ là khối vuông".
- Chỉ phân tích màn chơi, quên Loading / Home / popup → thiếu cả luồng màn trong plan.
