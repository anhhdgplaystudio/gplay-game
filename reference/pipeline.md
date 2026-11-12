# Pipeline /gplay-game: từ ý tưởng tới bản chơi được

**Phiên Claude chính làm trực tiếp**: nghiên cứu, plan, code, chạy Unity, xem ảnh, báo người dùng. Không mặc định mở phiên claude CLI riêng cho từng task
(mỗi phiên riêng phải đọc lại code, không chạy được Unity có GPU, làm đầy danh sách phiên). Việc code lớn tách được → **subagent trong cùng phiên** (tool Agent).
Worker CLI (`orch.py run`) chỉ dùng khi người dùng yêu cầu chạy song song / qua đêm và dự án có git: [cli-workers.md](cli-workers.md).

`O = python "<PLUGIN>/scripts/orch.py"` (chạy ở gốc repo dự án): sổ trạng thái + lịch sử trong `.game/`.

Lệnh người dùng gõ: `start` (intake) · `research` · `plan` · `build` (làm mốc kế) · `status` · `learn`.

## Sơ đồ + cổng duyệt

```
start ─G0→ research ─G1→ plan ─G2→ build M1 "level mẫu" ─GS→ build M2..Mn → report ─G3→ learn
```
| Cổng | Người dùng duyệt gì | Điều kiện để được hỏi |
|---|---|---|
| G0 | Intake: ý tưởng, nguồn tham khảo, phạm vi | Đã tự xem tài liệu người dùng đưa |
| G1 | Thẻ đối chiếu luật + hình (kèm frame) và các quyết định | Luật lõi không còn `[suy luận]` ([research.md](research.md)) |
| G2 | Plan + danh sách mốc | Mốc 1 là level mẫu; mỗi mốc có cách kiểm |
| **GS** | **Level mẫu**: chơi đúng luật + hình khớp ảnh chuẩn | Ảnh ghép cạnh ảnh chuẩn đã đưa người dùng xem |
| G3 | Báo cáo bản đầu | Mọi mốc done, danh sách tồn rõ ràng |

Ghi cổng: `O log G1 "<quyết định>"`. Không tự vượt cổng. **Không làm meta / UI đầy đủ / nội dung hàng loạt trước GS**: luật hoặc hình sai thì mọi thứ sau phải làm lại.

Tiếp tục sau khi gián đoạn: `O status` + `O history -n 20` + đọc `.game/plan.md` → làm tiếp bước đang dở.

## Từng bước

**1. Intake** (`/gplay-game:start`): xin tài liệu tham khảo trước, tự xem, thẻ "Mình hiểu như sau", chỉ hỏi mục mơ hồ → `.game/intake.md`, G0.

**2. Nghiên cứu** (`/gplay-game:research`): theo [research.md](research.md). Thu video gameplay → `study_video.py` → `teardown.md` (luật có bằng chứng)
+ `visual-spec.md` (luồng màn, bố cục theo %, camera, vật thể, chuyển động, UI) + `base.md` (subagent đọc base, song song) → thẻ đối chiếu + câu hỏi → G1.

**3. Plan** (`/gplay-game:plan`): `.game/plan.md` theo `templates/plan.md`. Chia theo **mốc chơi được** (4–7 mốc), không chia task nhỏ:
- M1 luôn là **level mẫu**: nền móng tối thiểu + luật lõi (C# thuần có test) + 1 level dựng tay + hình màn chơi theo visual-spec + tự chơi chụp ảnh.
- Sau đó thường: cơ chế phụ → pipeline level + validator / solver → luồng màn (Loading / Home / Game) + UI + meta → nội dung (N level) → localization → phát hành.
- Mỗi mốc ghi: kết quả người dùng thấy được, lệnh kiểm, ảnh bằng chứng sẽ có, phần nào giao subagent được.
- Hỏi ở G2 (nếu chưa rõ): dự án chưa có git → đề xuất `git init` cục bộ (để hoàn tác được); ai làm art (mặc định khối đơn giản, art vẽ khi người dùng yêu cầu).

**4. Thực hiện từng mốc** (`/gplay-game:build`):
1. `O ms M2 start "<tiêu đề>"`. Nói trước với người dùng: mốc này làm gì, ước lượng thời gian, khi xong sẽ thấy gì.
2. Làm: phiên chính code trực tiếp. Phần lớn + độc lập (vd logic thuần + test, tool level, 1 màn UI) → subagent với đề rõ: phạm vi file, luật repo,
   lệnh kiểm phải đạt, không chạy Unity. Phiên chính đọc lại diff / chạy lại lệnh kiểm, không tin báo cáo.
3. Kiểm theo [verification.md](verification.md): compile → test logic → validator → **phiên chính chạy Unity** (dựng scene, tự chơi, chụp ảnh) →
   Read ảnh → mốc có hình thì `side_by_side.py` với ảnh chuẩn, đối chiếu danh sách so của visual-spec.
4. Chưa đạt → sửa ngay trong phiên (không mở task sửa riêng). Kẹt quá 2 vòng cùng 1 lỗi → dừng, báo người dùng kèm ảnh.
5. `O ms M2 done --note "<kết quả>" --evidence <ảnh...>` → báo người dùng: đã làm gì, lệnh đã chạy + kết quả,
   **đường dẫn đầy đủ từng ảnh**, điều chưa làm, câu hỏi cần quyết. M1 xong → hỏi GS.
6. Người dùng góp ý về hình / luật → sửa `visual-spec.md` / `teardown.md` trước, `O log NOTE "<góp ý>"`, rồi sửa code. Góp ý lặp lại lần 2 → `/gplay-game:learn`.

**5. Art** (chỉ khi người dùng yêu cầu): [art-on-demand.md](art-on-demand.md): brief → Codex / Gemini vẽ → kiểm kích thước → đưa vào game.

**6. Báo cáo**: `O phase report` · `O report` → `.game/REPORT.md` (mốc, thời gian, ảnh, cổng, góp ý, còn tồn) → trình người dùng, hỏi G3.

**7. Rút bài học** (`/gplay-game:learn`): bài học chung → `LEARNINGS.md` của plugin; riêng dự án → `AGENTS.md` / game-profile. Ghi **ngay khi gặp**, không đợi cuối.

## File trong `.game/`

| File | Nội dung |
|---|---|
| `intake.md` · `questions.md` · `plan.md` | Đầu vào, quyết định, kế hoạch theo mốc |
| `research/teardown.md` · `visual-spec.md` · `base.md` | Kết quả nghiên cứu (nguồn sự thật về luật + hình) |
| `state.json` | Giai đoạn, mốc (thời gian, file đổi, ảnh), task CLI nếu có |
| `HISTORY.md` · `history.jsonl` | Nhật ký: cổng duyệt, mốc, góp ý (NOTE), bài học (LEARN) |
| `milestones/<mốc>-files.txt` | File đã đổi trong mốc (không git: theo thời điểm sửa) |
| `art/<tên>/` | Brief + kết quả art theo yêu cầu |
| `REPORT.md` | Báo cáo, sinh lại mỗi lần chốt mốc |

Ảnh / video / build để ở ổ tạm ngoài repo; `.game/` chỉ giữ đường dẫn.

## Luật của phiên chính

- Không bỏ cổng duyệt; không lập plan khi luật lõi còn `[suy luận]`; không làm quá M1 khi chưa có GS.
- Mỗi lần báo "xong" phải có: lệnh đã chạy + kết quả, đường dẫn ảnh đã XEM, điều chưa làm. Không nói "đã giống mẫu" khi chưa ghép ảnh so.
- Ước lượng thời gian khi bắt đầu mốc; mốc dài > 30 phút thì báo tiến độ giữa chừng.
- Lệnh bị từ chối quyền → không gọi vòng; nói với người dùng lệnh cần chạy.
- Không sửa test cho xanh; không gọi lỗi là "có sẵn" rồi bỏ qua.
- Commit chỉ khi người dùng đã đồng ý (hỏi ở G2: commit sau mỗi mốc trên nhánh `game/<slug>`).
