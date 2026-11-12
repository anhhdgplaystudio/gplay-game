---
name: build
description: Làm mốc kế tiếp của plan ngay trong phiên này - code, chạy kiểm tra, tự chạy Unity chụp ảnh, ghép cạnh ảnh chuẩn, báo kết quả kèm đường dẫn ảnh; mốc 1 (level mẫu) phải qua cổng GS.
disable-model-invocation: true
argument-hint: "[mốc, vd M2 | góp ý cần sửa | 'cli' để giao worker]"
---
# /gplay-game:build

`O = python "${CLAUDE_PLUGIN_ROOT}/scripts/orch.py"`. Quy trình: `${CLAUDE_PLUGIN_ROOT}/reference/pipeline.md` bước 4. Kiểm tra: `${CLAUDE_PLUGIN_ROOT}/reference/verification.md`.

**Phiên này tự làm** (code + chạy Unity + xem ảnh). Không mở phiên claude CLI riêng trừ khi người dùng yêu cầu (`$ARGUMENTS` có "cli" / "song song" / "qua đêm"
→ làm theo `${CLAUDE_PLUGIN_ROOT}/reference/cli-workers.md`).

1. Cần G2 (`O history --event G2`); chưa có → `/gplay-game:plan`. `O status` + đọc `.game/plan.md`, `.game/research/teardown.md`, `visual-spec.md`,
   `AGENTS.md`, `.claude/game-profile.md`.
2. Chọn mốc: `$ARGUMENTS` nếu có; không thì mốc đầu chưa `done`. **Chưa có GS thì chỉ được làm M1.**
   `$ARGUMENTS` là góp ý của người dùng về mốc đã xong → `O log NOTE "<góp ý>"`, sửa teardown / visual-spec nếu góp ý về luật / hình, rồi sửa code trong mốc đang mở
   (hoặc mở lại mốc: `O ms <mốc> start`).
3. `O ms <mốc> start "<tiêu đề>"`. Báo người dùng 2–3 dòng: sẽ làm gì, ước lượng thời gian, khi xong thấy gì. Có bước cần Unity batchmode → hỏi Unity Editor đã đóng chưa.
4. Làm:
   - M1 dự án mới: dọn base + `AGENTS.md` + `.claude/game-profile.md` từ mẫu (`${CLAUDE_PLUGIN_ROOT}/reference/new-project.md`).
   - Luật chơi = C# thuần + test; scene / prefab dựng bằng editor script; hình tạm bằng khối / sprite đơn sắc **đúng bố cục % và camera của visual-spec**.
   - Phần lớn + độc lập → subagent (tool Agent) với đề: phạm vi file, luật repo, lệnh kiểm phải đạt, không chạy Unity, báo file đã đổi. Đọc lại kết quả, chạy lại lệnh kiểm.
   - Art: không tự sinh. Người dùng yêu cầu → `${CLAUDE_PLUGIN_ROOT}/reference/art-on-demand.md`.
5. Kiểm (dừng ở bậc đủ chứng minh, mốc có hình thì phải tới ảnh):
   compile → test logic → validator → **tự chạy Unity** dựng scene + tự chơi + chụp ảnh ra ổ tạm → **Read ảnh** →
   `python "${CLAUDE_PLUGIN_ROOT}/scripts/side_by_side.py" <ảnh chuẩn> <ảnh game> <ổ tạm>/cmp_<mốc>.jpg --grid 10` → Read → soát danh sách so (visual-spec mục 9).
   Lệch → sửa ngay, lặp. Cùng 1 lỗi quá 2 vòng → dừng, báo người dùng kèm ảnh. Lệnh bị từ chối quyền → không gọi vòng, nói lệnh cần người dùng cho phép.
6. `O ms <mốc> done --note "<kết quả 1 dòng>" --evidence <ảnh ghép> <ảnh chính...>` (chưa đạt: thêm `--fail`).
7. Báo người dùng: đã làm gì · lệnh đã chạy + kết quả · **đường dẫn đầy đủ từng ảnh** · điều chưa làm / khác ảnh chuẩn (nói thẳng) · thời gian thực tế.
   - Xong **M1** → hỏi cổng **GS** (AskUserQuestion): `Đạt, làm tiếp` / `Sửa hình` / `Sửa luật` / `Nghiên cứu lại`. Đạt → `O log GS "<nhận xét>"`, `O phase build`.
   - Mốc khác → hỏi làm tiếp mốc kế hay chỉnh. Người dùng đã nói "làm hết, review sau" → làm tiếp không hỏi, nhưng vẫn `ms done` + ảnh từng mốc.
   - Hết mốc → `O phase report`, `O report`, trình `.game/REPORT.md`, hỏi G3.
8. Người dùng sửa cách làm, hoặc 1 lỗi lặp lần 2 → ghi ngay bằng `/gplay-game:learn` (không đợi cuối dự án).

Hỏi người dùng bằng tool **AskUserQuestion** (≤ 4 câu / lượt, 2–4 phương án, khuyến nghị đặt đầu + "(Recommended)"), không liệt kê câu hỏi thành chữ.
