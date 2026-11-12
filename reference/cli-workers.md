# Worker CLI (tuỳ chọn): chạy task bằng phiên claude riêng

**Không phải cách mặc định.** Chỉ dùng khi người dùng yêu cầu rõ (chạy song song nhiều việc độc lập, chạy qua đêm) **và** dự án có git.
Không git thì mọi task chạy tuần tự trong repo chính: chậm hơn phiên chính tự làm, không có lợi gì.

Cái giá: mỗi worker đọc lại code từ đầu; không hỏi được người dùng; không chạy được Unity có GPU; mỗi lần chạy thêm 1 dòng trong danh sách phiên
(tắt lưu phiên: `O config persist_sessions false`, khi đó `--fix` không tiếp phiên cũ được).

`O = python "<PLUGIN>/scripts/orch.py"`.

## Hợp với việc nào

| Giao worker được | Phiên chính tự làm |
|---|---|
| Logic thuần có test, tool dòng lệnh, sinh dữ liệu, sửa lỗi có test tái hiện, review chỉ đọc | Mọi thứ phải nhìn (hình, UI, feel), đối chiếu video, cần Unity có GPU, đề bài còn mơ hồ |

## File task `.game/tasks/T<nn>-<tên>.md`

```markdown
---
id: T03
title: Solver + chỉ số độ khó
kind: code            # code | research | review
depends: T01, T02
scope: Assets/Game/Scripts/Core/**, Tools/**
test: dotnet test Tools/Game.Tests
verify: python Tools/playtest.py --levels 1-3 --out D:/tmp/playtest_t03
evidence: D:/tmp/playtest_t03/*.png
model: sonnet         # tuỳ chọn
weight: 2             # 1..3; unity: true = chạy một mình ở repo chính
---
## Bối cảnh / Việc cần làm / Tiêu chí nghiệm thu / Không làm
```
- `test:` worker phải chạy đạt; orch chạy lại. Lệnh chung cho mọi task code: `O config tests '["<lệnh compile>"]'`.
- `verify:` lệnh **orch chạy sau worker** (worker không có quyền: Unity có GPU, tự chơi chụp ảnh). Chỉ chạy khi `test` đạt.
- `evidence:` glob ảnh sinh ra → liệt kê đường dẫn đầy đủ trong `REPORT.md`.
- Mẫu: `templates/tasks/T00-code.md`, `V00-review.md`.

## Chạy

`O branch` (1 lần) → `O run T01 T02 T03 --parallel --merge` (lâu thì chạy nền). Lập lịch theo độ nặng: tối đa `max_parallel` phiên, tổng `max_load`;
mỗi task code 1 git worktree; task `unity: true` chạy một mình; task scope chồng nhau không chạy cùng lúc.

Kết quả mỗi task (`.game/runs/<T>/<lần>/REPORT.md`):

| Trạng thái | Nghĩa | Làm gì |
|---|---|---|
| `passed` | Worker xong, test + verify đạt, không có ảnh phải xem | `O merge` (hoặc `--merge`) |
| `review` | Lệnh kiểm đạt nhưng worker báo còn việc, hoặc task có `evidence` | Phiên chính **Read từng ảnh**, đọc mục "Chưa làm" → `O accept T03 --note "..."` hoặc `O run T03 --fix` |
| `failed` | Test / verify lỗi, sửa ngoài phạm vi (có git), claude lỗi | Lỗi của task → `O run T03 --fix` (≤ `max_fix`); lỗi do đề → sửa file task rồi chạy lại |
| `interrupted` | Lần chạy bị ngắt (tắt máy / dừng phiên) | Chạy lại; orch tự ghi nhận khi gặp |

Làm tay 1 task trong phiên tương tác riêng: `O open T03 [--here]` → làm → `O done T03 --note "..." [--evidence ...]`.

## Quyền worker

`acceptEdits` + `allowed_tools` trong config. Mặc định có cả luật `Bash(...)` và `PowerShell(...)` (Windows dùng PowerShell là chính).
Quyền xét **từng lệnh con**: `cd x; python y`, pipe, vòng `for` đều bị từ chối dù `python` được phép → đề task dặn worker 1 lệnh đơn mỗi lần
(orch đã chép luật này vào prompt). Worker gọi vòng lệnh bị chặn = vi phạm: xem mục "Bị từ chối quyền" trong báo cáo.
Thêm quyền cho dự án: `O config allowed_tools '[...]'` (vd thêm `"PowerShell(dotnet:*)"` đã có sẵn; lệnh riêng của dự án thì thêm vào).

## Ghi chú vận hành

- claude CLI: orch tự dò (PATH → npm → bản mới nhất trong extension IDE). Đường dẫn trong config mất thì tự dò lại; không tìm thấy thì dừng trước khi tính lần chạy.
- Chi phí trong báo cáo là **USD quy đổi** từng lần chạy (lần `--fix` tiếp phiên cũ chỉ tính phần tăng thêm). Gói tháng: chỉ để so sánh.
  Trần mỗi lần chạy: `O config budget_usd 3` (mặc định 0 = không đặt).
- Không git: file đổi lấy theo thời điểm sửa trong `track_dirs`; file ngoài phạm vi chỉ cảnh báo.
- Nhiều phiên + build song song dễ treo máy: bắt đầu với `--parallel 2`.
