# Playbook cơ chế

Mọi cơ chế: chung 1 class `PuzzleLevel` (thời gian, thưởng, thắng / thua) + 1 database. Mỗi cơ chế cần:
**mô hình dữ liệu · class runtime · trường json · hàm tự giải · tiến trình `done/total` cho HUD · lỗi hay gặp**.
Logic luật (đúng / sai, xong bước) để trong class C# thuần → test được không cần scene.

Playbook dưới đây là các cơ chế **đã làm ở ≥ 1 game GPlay**. Game tham khảo không khớp mục nào (hoặc chỉ gần giống) → **không ép về playbook gần nhất**:
luật lấy từ `.game/research/teardown.md` (xem [research.md](research.md)), viết theo khung ở mục "Cơ chế chưa có playbook".

## Mục lục
- Cơ chế chưa có playbook (làm từ teardown)
- Kéo thả vào chỗ (dress-up / lắp ghép)
- Tìm đồ (bấm / soi kính lúp)
- Giải đố từng bước (trick / "annoying")
- Match / tile
- Sort (ball / water / hàng)
- Merge

## Cơ chế chưa có playbook (làm từ teardown)

1. Teardown đã trả lời 8 câu (chạm vào gì, tác động bao nhiêu vật, đường đi, cái gì tự động, sức chứa, thắng / thua, bấm sai, cơ chế phụ) bằng frame.
2. Viết luật thành **mô hình thuần C#** (không `UnityEngine`): trạng thái + `Apply(nước đi) → danh sách sự kiện`; runtime chỉ diễn lại sự kiện. Mỗi dòng "Luật lõi" của teardown = ≥ 1 test.
3. Dữ liệu level: file text / json đọc được bằng mắt, validator kiểm cấu trúc + giải được.
4. **Hàm tự giải**: cơ chế xác định, không gian nhỏ → solver (BFS / DFS + hash trạng thái); không thì kịch bản bước theo dữ liệu level. Dùng cho tự chơi và đo độ khó.
5. **Chơi ngẫu nhiên** N lần → tỉ lệ thắng: phát hiện level / luật "bấm bừa cũng thắng" (xem verification.md mục ngưỡng độ khó).
6. Hình: theo visual-spec (bố cục %, camera, danh mục vật thể), tạm bằng khối đúng cỡ; ghép ảnh so trước khi làm tiếp.
7. Ghi tóm tắt luật + tên class + lệnh vào `.claude/game-profile.md` của dự án. Chỉ chép thành playbook vào file này khi làm game thứ 2 cùng cơ chế.

## Kéo thả vào chỗ

- Dữ liệu: N tranh × M ô; mỗi ô: món đúng, outline (bóng chỉ chỗ), thứ bị thay, icon ở khay, ảnh khi kéo; đồ lừa.
- Runtime: `Level > Page > Slot`, khay chứa mọi món + đồ lừa. Đặt đúng → hiện món, ẩn outline / thứ cũ.
- Tên layer: `bg<t> deco<t>-<note> outline<t>.<o> item<t>.<o> old<t>.<o> mini<t>.<o> drag<t>.<o> char<t>/nv<t> fake<n>`.
- Tự giải: với mỗi ô, gọi hàm thả của khay với món đúng tại tâm ô.
- Lỗi hay gặp: khay quá nhiều món trên màn nhỏ; vùng nhận thả nhỏ hơn ngón tay (≥ 120 px canvas); nhân vật có anim làm lệch outline.

## Tìm đồ

- Hai dạng: **bấm** thẳng vào đồ; **kính lúp**: đồ ẩn chỉ thấy trong kính (SpriteMask, `VisibleInsideMask`), vỏ che ẩn trong kính (`VisibleOutsideMask`).
- Dữ liệu: `targets`, `hidden`, `magnifier`, `reveal`, `covers`, `points` (điểm tròn x, y, r khi đồ không có layer riêng), `raise` (đẩy lớp khi tìm thấy).
- Vai trò layer trong prefab bằng nhóm con (Thường / Đồ ẩn / Vỏ che / Kính lúp / Nền / Anim / Điểm cần tìm).
- Tự giải: bấm vào tâm từng target (dạng kính: kéo kính tới đó trước). Bấm ngoài kính không tính.
- Lỗi hay gặp: vùng chạm lệch vì art có viền trong suốt; Spine không bị mask (đặt `maskInteraction`).
- Đoán target từ ảnh demo có vòng đỏ: so ảnh demo với cảnh ghép.

## Giải đố từng bước

- Dữ liệu: `drags` (vật kéo / vuốt / bấm / bấm đúp), `spines` (nhân vật, skin, thay layer nào), `steps` (vùng nhận, vật chấp nhận, ẩn / hiện, câu thoại, `phases` có delay + anim).
- Kiểu input: kéo vào vùng; `swipe` đo hướng vuốt (vật đứng yên); `tap`; `doubleTap` (2 lần / 0.5 s). Vuốt chưa đủ / bấm trượt không tính lỗi.
- Thoại: bong bóng, đuôi chỉ **người nói** (đối chiếu video từng câu); câu nhân vật phụ đặt bong bóng riêng.
- Tự giải: duyệt `steps`, thả vật `accept` vào tâm `area` qua hàm thả thật, chờ `phases` xong.
- Lỗi hay gặp (đã gặp thật):
  - `area` phủ cả cảnh / chồng nhau → thả bừa cũng đúng.
  - `replaces` gồm cả vật có sẵn trong cảnh → vật biến mất khi Spine hiện.
  - Nhân vật biến mất cùng lúc câu thoại của chính họ (phải đợi nói xong).
  - Mapping sắp theo tên → tường đè lên người.
  - Bật cắt khung toàn cảnh làm sprite vỡ hình → chỉ cắt Spine tràn.
  - Spine không có skin default → đặt skin rỗng = nhân vật trống.

## Match / tile

- Dữ liệu: lưới / lớp xếp chồng, loại tile, khay chứa (n ô), mục tiêu.
- Luật thuần C#: chọn tile → vào khay → đủ 3 cùng loại thì xoá; khay đầy = thua. Lớp trên che lớp dưới (chỉ chọn tile không bị che).
- **Bắt buộc** solver kiểm level giải được (DFS / greedy + random seed), sinh số liệu độ khó (số nước, tỉ lệ thua random).
- Booster: undo, shuffle, hint, thêm ô khay.

## Sort

- Dữ liệu: các ống / cột, sức chứa, màu theo thứ tự đáy → đỉnh.
- Luật: đổ phần đỉnh cùng màu sang ống trống / cùng màu đỉnh còn chỗ. Thắng khi mỗi ống 1 màu đầy hoặc rỗng.
- Solver BFS với hash trạng thái; sinh level ngược từ trạng thái giải xong.

## Merge

- Dữ liệu: lưới, chuỗi cấp vật phẩm, nguồn sinh, đơn hàng.
- Luật: 2 vật cùng cấp → cấp +1. Cân bằng kinh tế: thời gian sinh, giá đơn, năng lượng.
- Mô phỏng kinh tế bằng script (không cần Unity) trước khi chỉnh số.

## Thêm playbook mới vào file này

Chỉ khi cơ chế đã dùng ở ≥ 2 game (qua `/gplay-game:learn`): viết theo cùng 6 mục, dạng chung, không tên class / số liệu của 1 game.
Cơ chế của 1 game đơn lẻ ở lại trong teardown + game-profile của dự án đó.
