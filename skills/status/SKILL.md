---
name: status
description: Xem tiến độ pipeline game (giai đoạn, cổng đã qua, mốc + thời gian + ảnh bằng chứng, việc dở) và bước nên làm tiếp; cũng là lệnh vào lại sau khi gián đoạn.
disable-model-invocation: true
argument-hint: "[ghi chú | history <bộ lọc> | config <khoá> <giá trị> | report]"
---
# /gplay-game:status

`O = python "${CLAUDE_PLUGIN_ROOT}/scripts/orch.py"`, chạy ở gốc repo.

1. Không có `.game/` → bảo người dùng chạy `/gplay-game:start`. Dừng.
2. `$ARGUMENTS`:
   - trống → `O status` + `O history -n 15`;
   - `history ...` → `O history` với bộ lọc (`--task`, `--file`, `--event`, `--since`, `-n`);
   - `config [khoá [giá trị]]` → `O config ...` (đổi thì nói rõ đã đổi gì);
   - `report` → `O report`, trình `.game/REPORT.md`;
   - còn lại = ghi chú của người dùng → `O log NOTE "<ghi chú>"` rồi báo trạng thái.
3. Tóm tắt (≤ 10 dòng): giai đoạn · cổng đã qua · mốc xong / đang làm (thời gian) · đường dẫn ảnh bằng chứng mới nhất · việc dở (mốc `doing`, task CLI `review` / `ngắt?`) · **bước kế**:

| Trạng thái | Bước kế |
|---|---|
| chưa G0 | `/gplay-game:start` |
| G0, chưa G1 | `/gplay-game:research` |
| G1, chưa G2 | `/gplay-game:plan` |
| G2, chưa GS | `/gplay-game:build` (M1 level mẫu) |
| GS, còn mốc | `/gplay-game:build` |
| hết mốc | `O report` → G3 → `/gplay-game:learn` |

4. Người dùng nói "làm tiếp" → làm luôn bước kế (đọc SKILL.md của lệnh đó trong `${CLAUDE_PLUGIN_ROOT}/skills/`), không bắt gõ lại lệnh. Không tự vượt cổng duyệt.

Danh sách lệnh: `start` (intake) · `research` (mổ game tham khảo) · `plan` (mốc) · `build` (làm mốc kế) · `status` · `learn` (thêm luật / bài học).
