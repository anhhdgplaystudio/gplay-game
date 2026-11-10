---
name: gplay-game
description: Quy trình làm game puzzle casual mobile mới bằng Unity, từ mở dự án tới phát hành - dựng dự án từ base template, chốt cơ chế chơi (kéo thả, tìm đồ, giải đố từng bước, match/tile, sort, merge), pipeline art PSD sang level dữ liệu, importer, database level, controller riêng từng level, tự chơi thử batchmode, UI theo mockup, localization nhiều ngôn ngữ, quảng cáo / IAP / analytics, checklist phát hành, giao việc song song cho Codex / Gemini. Dùng khi bắt đầu một game puzzle / casual mới, dựng cơ chế hoặc pipeline level đầu tiên, viết AGENTS.md / game-profile cho dự án game, hoặc khi người dùng nhắc "game mới", "dự án mới", "làm game puzzle".
---

# Làm game puzzle casual mới (Unity, mobile)

Thư mục plugin: `${CLAUDE_PLUGIN_ROOT}` (đường dẫn `reference/`, `templates/`, `scripts/` bên dưới tính từ đây).
Skill này là **quy trình chung**. Thông tin riêng từng dự án (namespace, đường dẫn, menu tool, sheet) nằm ở `.claude/game-profile.md` của dự án đó.

## Bước 0: luôn làm trước

1. Đọc luật của repo: `AGENTS.md`, `CLAUDE.md`, `.claude/game-profile.md`. Luật repo **thắng** skill này.
2. Chưa có `game-profile.md` → dự án mới: làm theo [reference/new-project.md](reference/new-project.md) trước mọi việc khác.
3. Đọc `ProjectSettings/ProjectVersion.txt` (lệnh Unity khác theo phiên bản).
4. Xem `LEARNINGS.md` (bài học từ các dự án trước) và `RULES.md` (luật chung thêm bằng `/gplay-game:add-rule`) của plugin.

## Pipeline /gplay-game:* (cách làm mặc định cho dự án mới)

Người dùng gõ `/gplay-game:start` (dự án mới) hoặc `/gplay-game:continue` (làm tiếp); danh sách lệnh: `/gplay-game:help`. Làm theo [reference/pipeline.md](reference/pipeline.md):
intake → nghiên cứu ∥ đọc base → câu hỏi + đề xuất → plan → chia task → **mỗi task chạy bằng claude CLI** (`scripts/orch.py run`)
(song song tối đa 3 phiên theo độ nặng, mỗi task 1 git worktree) → test đơn từng task → gộp → test tích hợp → sửa bug → báo cáo. Có cổng duyệt G0–G3, lịch sử `.game/HISTORY.md` + transcript từng lần chạy,
báo cáo "nơi thực hiện + kết quả" sau mỗi task.
Intake (chưa có G0, từ `start` hay `continue`): luôn xin tài liệu tham khảo trước, tự xem rồi mới hỏi phần thiếu (luồng ở `skills/start/SKILL.md`).
Mọi câu hỏi cho người dùng (intake, câu hỏi G1, duyệt plan, xác nhận) dùng tool **AskUserQuestion**, không liệt kê thành chữ trong chat.

## Các giai đoạn

| Giai đoạn | Việc chính | Tài liệu |
|---|---|---|
| 0. Mở dự án | Clone base, xoá gameplay cũ, đổi identity, viết AGENTS.md ngắn + game-profile, gắn hook | [new-project.md](reference/new-project.md), [rules-and-hooks.md](reference/rules-and-hooks.md) |
| 1. Cơ chế | Chọn playbook cơ chế, dựng 1 level tay chơi được, có hàm tự giải | [mechanics.md](reference/mechanics.md) |
| 2. Pipeline level | Định dạng art xuất, file level dữ liệu, importer, database, validator | [level-pipeline.md](reference/level-pipeline.md), [art-spine.md](reference/art-spine.md) |
| 3. UI + vòng meta | UI theo mockup, popup thắng / thua, coin, hint, quảng cáo | [ui-from-mockup.md](reference/ui-from-mockup.md), [meta-monetization.md](reference/meta-monetization.md) |
| 4. Sản xuất nội dung | Làm level hàng loạt, text / voice, giao việc song song | [localization.md](reference/localization.md), [multi-agent.md](reference/multi-agent.md) |
| 5. Phát hành | Hiệu năng, build, store, cấu hình thật | [release.md](reference/release.md) |

Mọi giai đoạn dùng chung: [verification.md](reference/verification.md) (thang kiểm tra + tiêu chí xong).

Mặc định **gọn nhẹ**: không viết GDD dài trước khi có bản chơi được. Thời gian dồn vào level chơi được, validator, chạy thử, ảnh bằng chứng.

## Luật cứng (mọi dự án Unity)

1. **Không sửa tay YAML** `.unity .prefab .asset .mat .controller .anim`: đổi qua editor script / importer / menu / batchmode.
2. **Giữ `.meta`** đi cùng asset, không xoá / sinh lại (GUID = danh tính asset). Script sinh file không được xoá `.meta`.
3. **Không ghi đè asset người đã chỉnh tay** (prefab level có anim, vị trí chỉnh tay) khi chưa được đồng ý. Importer mặc định *không ghi đè*.
4. **Nguồn sự thật là file dữ liệu** (json / csv / thư mục art), asset sinh ra từ nó. Sửa asset sinh ra thì lần import sau mất → sửa nguồn + importer.
5. Logic riêng 1 level → class con riêng (`LevelControllerN`), **không** nhồi vào class base.
6. **Không đọc / in / copy bí mật**: keystore, `google-services.json`, file key SDK / API, token web app. Không đụng cấu hình SDK khi chưa được yêu cầu.
7. Hỏi trước khi: thêm package, asmdef, DI container, Addressables; đổi tên / xoá field serialized (mất dữ liệu im lặng).
8. Chỉ commit khi người dùng yêu cầu.
9. File nặng (build, cache, video, ảnh chạy thử) để ổ có chỗ trống, không để trong repo.
10. Batchmode không mở được project khi Editor đang mở: hỏi / chờ người dùng đóng, hoặc dùng cách điều khiển Editor đang mở.

## Tiêu chí "xong" (copy vào câu trả lời và đánh dấu)

```
- [ ] Build C# sạch (không dòng " error ")
- [ ] Validator dữ liệu (level / layout / key) không lỗi
- [ ] Chạy thử: tự chơi hết level / màn đổi, đã XEM ảnh chụp, so với demo / video
- [ ] Không sửa tay YAML, không ghi đè asset chỉnh tay, không chạm bí mật
- [ ] Text mới có key localization và đã đẩy lên nguồn
- [ ] Báo: lệnh đã chạy, file đổi, kết quả kiểm tra, việc CHƯA làm, tác dụng phụ còn lại
```

## Vòng học

- Người dùng sửa cách làm, hoặc 1 lỗi lặp lần 2 → ghi 1 dòng vào `LEARNINGS.md` (bài học chung) hoặc `game-profile.md` (chỉ dự án đó).
- Bài học trái với nội dung skill → sửa skill + ghi `CHANGELOG.md`.
- Sửa skill xong → chạy lại tình huống trong `evals/evals.json`.

## Templates + scripts

- `templates/AGENTS.md`, `templates/game-profile.md`: khung cho dự án mới.
- `hooks/hooks.json` + `scripts/guard.py`: hook của plugin chặn sửa YAML / .meta / bí mật / lệnh nguy hiểm; chỉ bật ở dự án có
  `.claude/guard.json` `"enabled": true` (mẫu `templates/guard.json`, `/gplay-game:start` tự chép). Luật chung: `guard.json` của plugin.
- `templates/level-task.md`: đề bài 1 level giao cho agent khác.
- `scripts/check_dev.py <thư mục dev>`: kiểm thư mục art xuất (cặp png / cor, kích thước bội 4, mapping.json).
- `scripts/compose_dev.py <thư mục dev> <out.png>`: ghép ảnh cảnh từ thư mục art để kiểm bằng mắt, không cần Unity.
- `scripts/check_build.py <csproj> [file.cs ...]`: build kiểm tra, tự thêm file `.cs` mới vào bản csproj tạm.
- `scripts/orch.py`: điều phối pipeline (init / phase / log / branch / run / merge / test / status / report / history / config), xem pipeline.md.
- `templates/plan.md`, `templates/tasks/` (R1 nghiên cứu, R2 đọc base, T00 code, V00 review).
