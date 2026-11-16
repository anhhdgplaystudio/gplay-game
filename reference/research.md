# Nghiên cứu game tham khảo (bước quan trọng nhất)

Mục tiêu: trước khi lập plan, phiên chính phải **tự nhìn thấy** game gốc chơi thế nào và trông ra sao, ghi thành tài liệu có bằng chứng:
`.game/research/teardown.md` (luật chơi), `visual-spec.md` (hình + luồng màn), `ref-level.md` (level chuẩn chép từ game gốc) và
`visual-check.md` (bảng nghiệm thu hình: thước đo duy nhất để nói "khớp mẫu"). Sai ở bước này = viết lại code về sau.

Luật thì dễ đúng, **hình mới là chỗ bị trả về nhiều vòng**: người dùng so từng chi tiết với game gốc, còn tả bằng lời + vài dải % thì không bắt được chi tiết nào.
Vì vậy phần hình phải ra **số đo từng vật thể** trước khi code, không phải sau khi bị chê.

Phiên chính tự làm (cần xem ảnh, cần hỏi người dùng). Chỉ giao subagent phần đọc nhiều file: thống kê dữ liệu level / config, đọc base (`base.md`).

`<tmp>` = ổ tạm ngoài repo (vd `D:/tmp/<slug>`). `<PLUGIN>` = thư mục plugin.

## Mục lục
1. Thu nguồn · 2. Mổ video · 3. Teardown luật chơi · 4. Spec hình + luồng màn · 4b. Level chuẩn · 4c. Bảng nghiệm thu hình ·
5. Dữ liệu có sẵn · 6. Đọc base · 7. Cổng G1 · Lỗi hay gặp

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

**Độ nét quyết định phần hình**: mở `study.json` xem kích thước khung game sau khi cắt viền. Luật chơi đọc được ở video nhỏ, nhưng
ảnh chuẩn + số đo hình phải lấy từ khung **cao ≥ 1080 px, ≥ 30 fps** (soi chuyển động: 60 fps nếu có). Video đầu tiên tải về nhỏ hơn →
tìm tiếp ngay ở bước này (`ytsearch10`, thêm `-f "bv*[height>=1080]"`), đừng đợi người dùng chê mới đi tìm. Không có → ghi rõ ở đầu visual-spec
"nguồn cao <N> px" và hỏi người dùng xin ảnh chụp màn hình thật / file quay màn hình.
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
  Người dùng gửi ảnh nào → ảnh đó là chuẩn. Ảnh chuẩn gameplay lấy từ **level chuẩn** (mục 4b): 1 frame đầu level (chưa thao tác),
  1 frame giữa hành động, 1 frame cuối level; chép bản gốc không nén lại (PNG từ frame gốc, không lấy từ sheet thu nhỏ).
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

## 4b. Level chuẩn → `.game/research/ref-level.md`

Level mẫu của dự án **là 1 level của game gốc chép lại**, không tự nghĩ level mới: chỉ khi 2 ảnh cùng nội dung mới so được cỡ, mật độ, màu, bố cục.
- Chọn level có frame đầu level rõ + có clip đủ các chuyển động chính (thường level 2–5: đã hết tutorial, chưa có cơ chế phụ).
- Chép **dữ liệu** của nó từ frame đầu level: lưới / vị trí từng vật, màu từng ô (ký hiệu + hex), số ghi trên vật, thứ tự hàng chờ, số lượng từng loại.
  Đếm trên frame gốc phóng to (crop từng phần), kiểm tổng (vd tổng ô mỗi màu = tổng sức chứa cùng màu).
- Ghi vào `ref-level.md`: nguồn (video, giây), ảnh chuẩn 3 thời điểm, dữ liệu ở dạng nạp thẳng được vào game (lưới ký tự / json), phần nào không đọc được (ghi `?` + cách kiểm).
- Level này chỉ để **dựng + so**; level phát hành tự thiết kế (ghi ở teardown mục "Không đem vào bản phát hành").

## 4c. Bảng nghiệm thu hình → `.game/research/visual-check.md`

Mẫu: `<PLUGIN>/templates/research/visual-check.md`. Viết cột **Mẫu** ngay ở bước research; build chỉ việc điền cột Game.
1. Mỗi vật thể ở mục 4 → các dòng: tâm (x %, y %) · bề ngang (% màn) · màu (hex đọc từ frame) · hình dáng (bo góc, viền, độ dày, chi tiết) ·
   số lượng + khoảng cách · lớp che. Mỗi sự kiện ở mục 5 → đường đi · đội hình · thời lượng (đếm frame) · thứ tự.
2. Đo bằng crop phóng to, không ước lượng trên ảnh toàn màn:
   `python "<PLUGIN>/scripts/side_by_side.py" <chuẩn> <chuẩn> <tmp>/check/ref_<mã>.jpg --crop x0,y0,x1,y1 --grid 10`.
3. **Soát theo vùng** (bảng D của mẫu): chia ảnh chuẩn 3 × 4 ô, crop + Read từng ô, liệt kê mọi thứ nhìn thấy; thứ chưa có dòng → thêm.
   Bước này bắt các thứ hay sót: viền, gờ nổi, vạch kẻ, nhãn nhỏ, bóng, mái che, hoạ tiết nền.
4. Có asset gốc (mesh, sprite, shader) → dựng lại từng vật riêng lẻ để soi kích thước thật, điểm gốc, hướng "mặt trước", rồi ghi vào bảng.
5. Số dòng ít hơn ~4 × số vật thể + 2 × số sự kiện → bảng còn thiếu, chưa được hỏi G1.

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
4. Phần hình đã đủ: ảnh chuẩn cao ≥ 1080 px (hoặc đã ghi rõ là không có), `ref-level.md` có dữ liệu level chuẩn, `visual-check.md` có cột Mẫu
   cho mọi vật thể + sự kiện và đã soát theo vùng. Đưa người dùng đường dẫn ảnh chuẩn + bảng, hỏi 1 câu: **"Nhìn ảnh chuẩn, điều gì sai là bạn thấy ngay?"**
   (phương án lấy từ các nhóm dòng của bảng, multiSelect + Other) → mỗi ý thêm 1 dòng `[người dùng G1]`. Đây là lúc rẻ nhất để biết người dùng soi cái gì.
5. Hỏi bằng AskUserQuestion; người dùng xác nhận → `O log G1 "<tóm tắt>"`, `O phase plan`.

Người dùng sửa 1 luật / 1 điểm hình sau G1 → `O fb add` lưu nguyên văn, cập nhật teardown / visual-spec / visual-check **trước**, rồi mới sửa plan / code.

**Nghiên cứu lại** (cổng GV / GS bị trả về lần 2 về hình): không vá tiếp từng mục. Tìm nguồn nét hơn nếu nguồn < 1080 px, làm lại mục 4c cho **cả màn**
(đặc biệt bước soát theo vùng), so bảng mới với bảng cũ để thấy mình đã sót loại chi tiết nào, trình bảng cho người dùng rồi mới quay lại build.

## Lỗi hay gặp (đã gặp thật)

- Lập luật từ mô tả store + ảnh tĩnh → sai đối tượng người chơi chạm vào, sai chiều bố cục; phải viết lại luật 2 lần.
- Hỏi người dùng "luật thế nào?" thay vì tự xem video: người dùng trả lời theo trí nhớ, vẫn sai.
- Tả hình bằng lời ("nhìn từ trên xuống") không kèm ảnh chuẩn + tỉ lệ → dựng ngược hướng, sai tỉ lệ.
- Bỏ qua chuyển động (vật vào / ra đường nào) vì chỉ xem frame rời.
- Coi vật thể là "khối" trong khi gốc là nhân vật có mặt / model riêng → người dùng chê "chỉ là khối vuông".
- Chỉ phân tích màn chơi, quên Loading / Home / popup → thiếu cả luồng màn trong plan.
- Làm visual-spec từ video 374 × 854 trong 12 phút, danh sách so chỉ 5 dòng chung chung → level mẫu bị trả về 5 vòng; video 1080p chỉ đi tìm sau lần chê thứ 2.
- Level mẫu tự vẽ (khác level trong ảnh chuẩn) → không so được 1 : 1, mỗi vòng người dùng lại thấy một chỗ lệch mới.
- Đã ghi đúng trong spec ("chỉ hàng cuối lộ chân") nhưng không có dòng nghiệm thu nào kiểm → game vẫn sai mà báo "khớp".
