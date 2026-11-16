---
name: build
description: Làm mốc kế tiếp của plan ngay trong phiên này - code, chạy kiểm tra, tự chạy Unity chụp ảnh, so từng vùng với ảnh chuẩn theo bảng nghiệm thu, báo "chờ duyệt" kèm đường dẫn ảnh + các dòng chưa đạt; M1 (khung hình tĩnh) qua cổng GV, M2 (level mẫu chơi được) qua cổng GS.
disable-model-invocation: true
argument-hint: "[mốc, vd M2 | góp ý cần sửa]"
---
# /gplay-game:build

`O = python "${CLAUDE_PLUGIN_ROOT}/scripts/orch.py"`. Quy trình: `${CLAUDE_PLUGIN_ROOT}/reference/pipeline.md` bước 4 + mục "Xử lý góp ý". Kiểm tra: `${CLAUDE_PLUGIN_ROOT}/reference/verification.md`.

**Phiên này tự làm** (code + chạy Unity + xem ảnh). Không mở phiên claude CLI riêng, không tạo git worktree; phần tách được giao subagent cùng phiên.

1. Cần G2 (`O history --event G2`); chưa có → `/gplay-game:plan`. `O status` + đọc `.game/plan.md`, `.game/research/teardown.md`, `visual-spec.md`,
   `ref-level.md`, `visual-check.md`, mọi file `.game/feedback/*.md` còn mở, `AGENTS.md`, `.claude/game-profile.md`.
2. Chọn mốc: `$ARGUMENTS` nếu có; không thì mốc đầu chưa `done`. **Chưa có GV chỉ được làm M1; chưa có GS chỉ được làm tới M2.**
   `$ARGUMENTS` (hoặc tin nhắn) là **góp ý** của người dùng → việc đầu tiên, trước khi nghĩ cách sửa:
   `O fb add --ms <mốc> "<nguyên văn>"` rồi làm đủ 6 bước "Xử lý góp ý" của pipeline.md (tách mục → hỏi lại mục 2 cách hiểu → sửa bảng / spec → soát cả vùng → sửa code).
   Cổng này đã bị trả về 1 lần vì cùng loại → không sửa tiếp: nghiên cứu lại (`${CLAUDE_PLUGIN_ROOT}/skills/research/SKILL.md`).
   Mở lại mốc: `O ms <mốc> start`.
3. `O ms <mốc> start "<tiêu đề>"`. Báo người dùng 2–3 dòng: sẽ làm gì, ước lượng thời gian, khi xong thấy gì. Có bước cần Unity batchmode → hỏi Unity Editor đã đóng chưa.
4. Làm:
   - **M1 khung hình tĩnh**: dọn base + `AGENTS.md` + `.claude/game-profile.md` từ mẫu (`${CLAUDE_PLUGIN_ROOT}/reference/new-project.md`); cài bộ tự chơi;
     scene màn chơi dựng bằng editor script **từ dữ liệu `ref-level.md`**, đứng yên ở trạng thái đầu level, chụp đúng tỉ lệ + độ phân giải ảnh chuẩn.
     Không làm input / animation / thắng thua ở mốc này. Luật lõi C# thuần + test: giao subagent chạy song song (không cần hình).
     **Đưa người dùng xem sớm**: ngay khi có ảnh đầu tiên đủ các vật thể chính thì gửi ảnh ghép (ghi rõ "bản nháp, chưa đo") — hỏng hướng lớn thì biết sau 20 phút, không phải sau cả mốc.
   - **M2 level mẫu chơi được**: nối luật vào scene, input qua đường input thật, chuyển động theo từng dòng `C*` của bảng (đường đi, đội hình, thời lượng), thắng / thua, hàm tự giải.
   - Luật chơi = C# thuần + test; scene / prefab dựng bằng editor script. Chưa có art thật: hình tạm **đúng cỡ, vị trí, camera** của bảng nghiệm thu
     (dòng màu / chi tiết đã ghi `chủ ý` ở G1). Có asset gốc được phép dùng → dùng ngay từ M1, soi từng mesh / sprite riêng lẻ (kích thước thật, điểm gốc, hướng mặt trước) trước khi đặt vào scene.
   - **Mọi số bố cục** (vị trí, cỡ, góc camera, khoảng cách, tốc độ, thời lượng) gom vào 1 file dữ liệu / ScriptableObject, mỗi số ghi mã dòng bảng nghiệm thu nó phục vụ.
     Không rải hằng số trong code: chỉnh 1 số không được kéo theo sửa logic.
   - Có ≥ 2 phần lớn + độc lập → gọi các subagent (tool Agent) trong cùng 1 lượt, vùng file không chồng nhau, theo pipeline.md mục "Giao subagent". Đọc lại kết quả, chạy lại lệnh kiểm.
   - Art: không tự sinh. Người dùng yêu cầu → `${CLAUDE_PLUGIN_ROOT}/reference/art-on-demand.md`.
5. Kiểm (mốc có hình thì phải tới bảng nghiệm thu):
   compile → test logic → validator → **tự chạy Unity** dựng scene + tự chơi + chụp ảnh ra ổ tạm → **Read ảnh**
   (bộ kit: `python "${CLAUDE_PLUGIN_ROOT}/scripts/unity_run.py" playtest ...`, cài ở M1 theo `${CLAUDE_PLUGIN_ROOT}/reference/autoplay-kit.md`;
   Editor đang mở và có unity-mcp → `${CLAUDE_PLUGIN_ROOT}/reference/unity-mcp.md`) →
   - toàn màn: `python "${CLAUDE_PLUGIN_ROOT}/scripts/side_by_side.py" <ảnh chuẩn> <ảnh game> <ổ tạm>/cmp_<mốc>.jpg --grid 10` (game chụp **cùng level, cùng trạng thái** với ảnh chuẩn);
   - từng dòng của bảng: `... <ổ tạm>/check/<mã>.jpg --crop x0,y0,x1,y1` → Read → ghi số đo + đường dẫn + `đạt` / `lệch: <lệch gì>` vào cột Game;
   - chuyển động (M2): `--video` rồi `study_video.py --clip` cả video gốc lẫn video game cùng `--fps`, so 2 dải frame, điền dòng `C*`.
   `O check --ms <mốc>` → còn `lệch` → sửa, chụp lại, **điền lại cả cột Game của mốc**, lặp. Cùng 1 dòng quá 2 vòng → dừng, báo người dùng kèm ảnh crop.
   Lệnh bị từ chối quyền → không gọi vòng, nói lệnh cần người dùng cho phép.
6. `O ms <mốc> review --note "<kết quả 1 dòng>" --evidence <ảnh ghép> <ảnh crop...>` (hỏng: `O ms <mốc> done --fail`). **Không tự `done`.**
7. Báo người dùng: đã làm gì · lệnh đã chạy + kết quả · **đường dẫn đầy đủ từng ảnh** (ảnh ghép toàn màn đặt đầu, rồi ảnh crop) ·
   **bảng các dòng chưa đạt** chép từ output `ms review` (không còn dòng nào mới được viết "khớp ảnh chuẩn") · điều chưa làm · thời gian thực tế.
   - Xong **M1** → hỏi cổng **GV** (AskUserQuestion): `Đạt, làm tiếp` / `Sửa hình (ghi ở Other)` / `Nghiên cứu lại`.
   - Xong **M2** → hỏi cổng **GS**: `Đạt, làm tiếp` / `Sửa chuyển động` / `Sửa luật` / `Sửa hình`.
   - Được duyệt → `O log <GV|GS> "<lời duyệt nguyên văn>"` → `O ms <mốc> done` (lệnh từ chối khi còn dòng chưa đạt / góp ý mở: xử lý cho hết, không tìm cách lách). GS xong → `O phase build`.
   - Mốc khác → `review`, hỏi làm tiếp mốc kế hay chỉnh; người dùng đồng ý → `ms done`. Người dùng đã nói "làm hết, review sau" → lời đó là lời duyệt cho các mốc không có cổng, vẫn `review` + ảnh từng mốc.
   - Hết mốc → `O phase report`, `O report`, trình `.game/REPORT.md`, hỏi G3.
8. Người dùng sửa cách làm, hoặc 1 lỗi lặp lần 2 → ghi ngay bằng `/gplay-game:learn` (không đợi cuối dự án).

Hỏi người dùng bằng tool **AskUserQuestion** (≤ 4 câu / lượt, 2–4 phương án, khuyến nghị đặt đầu + "(Recommended)"), không liệt kê câu hỏi thành chữ.
