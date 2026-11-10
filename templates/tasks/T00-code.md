---
id: T00
title: <động từ + đối tượng>
kind: code
depends:
scope: <glob thư mục được sửa, phân cách dấu phẩy>
test: <lệnh kiểm tra riêng task (build chung đã có trong config)>
model: sonnet
budget: 3
weight:          # 1 nhẹ / 2 vừa / 3 nặng; bỏ trống = tự ước lượng
unity: false     # true nếu cần Unity batchmode (chạy một mình)
mode: auto       # manual = làm tay (/gplay-game:open), run tự động bỏ qua
---
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
