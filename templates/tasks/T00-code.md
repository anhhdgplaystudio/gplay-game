---
id: T00
title: <động từ + đối tượng>
kind: code
depends:
scope: <glob thư mục được sửa, phân cách dấu phẩy>
test: <lệnh kiểm tra riêng task, worker chạy được (build chung đã có trong config)>
verify: <lệnh orch chạy SAU worker: Unity có GPU / tự chơi chụp ảnh; bỏ dòng này nếu không cần>
evidence: <glob ảnh sinh ra từ verify, vd D:/tmp/playtest_t00/*.png; có dòng này thì task dừng ở `review` chờ xem ảnh>
model: sonnet
weight:          # 1 nhẹ / 2 vừa / 3 nặng; bỏ trống = tự ước lượng
unity: false     # true nếu cần Unity batchmode (chạy một mình ở repo chính)
mode: auto       # manual = làm tay (orch.py open), run tự động bỏ qua
---
<!-- Task file chỉ dùng cho worker CLI (reference/cli-workers.md). Mặc định phiên chính tự làm theo mốc, không cần file này. -->
## Bối cảnh
- Plan: .game/plan.md mục <...>
- File nên đọc: <...>
- Task trước liên quan: <Txx: đã làm gì>

## Việc cần làm
1. ...

## Tiêu chí nghiệm thu
- [ ] <kiểm được bằng lệnh trong test: hoặc ảnh>

## Không làm
- Sửa ngoài scope, sửa YAML Unity, đổi base class / importer (trừ khi task là việc đó)
- Chạy Unity có GPU / lệnh trong `verify` (orchestrator chạy); gọi vòng lệnh bị từ chối quyền
