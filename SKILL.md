---
name: gplay-game
description: Quy trình làm game puzzle casual mobile mới bằng Unity, từ mở dự án tới phát hành - nghiên cứu kỹ game tham khảo (mổ video gameplay, teardown luật chơi có bằng chứng, spec hình và luồng màn), dựng dự án từ base template, chốt cơ chế chơi (kéo thả, tìm đồ, giải đố từng bước, match/tile, sort, merge, hoặc cơ chế mới theo teardown), level mẫu được duyệt rồi mới làm tiếp theo mốc, pipeline art PSD sang level dữ liệu, importer, database level, tự chơi thử batchmode và ghép ảnh so mẫu, UI theo mockup, localization nhiều ngôn ngữ, quảng cáo / IAP / analytics, checklist phát hành, art theo yêu cầu bằng Codex / Gemini. Dùng khi bắt đầu một game puzzle / casual mới, phân tích / clone cơ chế một game tham khảo, dựng cơ chế hoặc pipeline level đầu tiên, viết AGENTS.md / game-profile cho dự án game, hoặc khi người dùng nhắc "game mới", "dự án mới", "làm game puzzle".
---

# Làm game puzzle casual mới (Unity, mobile)

Thư mục plugin: `${CLAUDE_PLUGIN_ROOT}` (đường dẫn `reference/`, `templates/`, `scripts/` bên dưới tính từ đây).
Skill này là **quy trình chung**. Thông tin riêng từng dự án (namespace, đường dẫn, menu tool, sheet) nằm ở `.claude/game-profile.md` của dự án đó.

## Bước 0: luôn làm trước

1. Đọc luật của repo: `AGENTS.md`, `CLAUDE.md`, `.claude/game-profile.md`. Luật repo **thắng** skill này.
2. Chưa có `game-profile.md` → dự án mới: làm theo [reference/new-project.md](reference/new-project.md) trước mọi việc khác.
3. Đọc `ProjectSettings/ProjectVersion.txt` (lệnh Unity khác theo phiên bản).
4. Xem `LEARNINGS.md` (bài học từ các dự án trước) và `RULES.md` (luật chung thêm bằng `/gplay-game:learn`) của plugin.

Skill này dùng cho **mọi** game casual / puzzle, không riêng cơ chế nào: luật của game cụ thể nằm ở `.game/research/teardown.md` + game-profile của dự án đó.

## Pipeline /gplay-game:* (cách làm mặc định cho dự án mới)

Lệnh: `start` (intake) · `research` · `plan` · `build` (làm mốc kế) · `status` (tiến độ + bước kế) · `learn`. Làm theo [reference/pipeline.md](reference/pipeline.md):

```
start ─G0→ research ─G1→ plan ─G2→ build M1 "level mẫu" ─GS→ build M2..Mn → report ─G3→ learn
```
- **Nghiên cứu là bước quan trọng nhất** ([research.md](reference/research.md)): phải có video gameplay, mổ bằng `scripts/study_video.py`, viết teardown luật chơi
  (mỗi luật gắn frame bằng chứng) + spec hình và luồng màn. Luật lõi còn `[suy luận]` thì chưa được lập plan. Không hỏi người dùng luật của game gốc khi video trả lời được.
- **Level mẫu trước, mọi thứ khác sau** (cổng GS): 1 level chơi đúng luật, màn chơi ghép cạnh ảnh chuẩn (`scripts/side_by_side.py`), người dùng duyệt rồi mới làm meta / UI / nội dung.
- **Phiên chính tự làm từng mốc** (code, chạy Unity, xem ảnh); phần lớn + độc lập giao subagent trong cùng phiên. Không mặc định mở phiên claude CLI riêng cho từng task
  và không dùng git worktree (cách chia việc: pipeline.md mục "Giao subagent").
- **Art theo yêu cầu**: mặc định hình tạm đúng kích thước + bố cục; người dùng bảo vẽ thì dùng Codex / Gemini ([art-on-demand.md](reference/art-on-demand.md)).
- Mỗi mốc: `scripts/orch.py ms` ghi thời gian, file đổi, ảnh bằng chứng; báo người dùng kèm **đường dẫn đầy đủ từng ảnh** và ước lượng thời gian mốc kế.
- Mọi câu hỏi cho người dùng dùng tool **AskUserQuestion**, không liệt kê thành chữ trong chat.

## Các giai đoạn

| Giai đoạn | Việc chính | Tài liệu |
|---|---|---|
| 0. Nghiên cứu | Thu video, teardown luật, spec hình + luồng màn, đọc base | [research.md](reference/research.md) |
| 1. Mở dự án | Clone base, xoá gameplay cũ, đổi identity, viết AGENTS.md ngắn + game-profile, gắn hook | [new-project.md](reference/new-project.md), [rules-and-hooks.md](reference/rules-and-hooks.md) |
| 2. Cơ chế + level mẫu | Luật C# thuần có test, 1 level tay chơi được, hàm tự giải, hình khớp ảnh chuẩn | [mechanics.md](reference/mechanics.md), [verification.md](reference/verification.md) |
| 3. Pipeline level | Định dạng art xuất, file level dữ liệu, importer, database, validator, ngưỡng độ khó | [level-pipeline.md](reference/level-pipeline.md), [art-spine.md](reference/art-spine.md) |
| 4. Luồng màn + UI + meta | Loading / Home / Game, UI theo mockup, popup thắng / thua, coin, hint, quảng cáo | [ui-from-mockup.md](reference/ui-from-mockup.md), [meta-monetization.md](reference/meta-monetization.md) |
| 5. Sản xuất nội dung | Làm level hàng loạt, text / voice, giao việc song song | [localization.md](reference/localization.md), [multi-agent.md](reference/multi-agent.md) |
| 6. Phát hành | Hiệu năng, build, store, cấu hình thật | [release.md](reference/release.md) |

Mọi giai đoạn dùng chung: [verification.md](reference/verification.md) (thang kiểm tra + tiêu chí xong).

Mặc định **gọn nhẹ**: không viết GDD dài; tài liệu duy nhất phải kỹ là teardown + visual-spec. Thời gian dồn vào nghiên cứu, level chơi được, validator, chạy thử, ảnh bằng chứng.

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
- [ ] Chạy thử: tự chơi hết level / màn đổi, đã XEM ảnh chụp
- [ ] Có hình: đã ghép cạnh ảnh chuẩn (side_by_side) và soát danh sách so của visual-spec; UI không méo, không thiếu glyph
- [ ] Không sửa tay YAML, không ghi đè asset chỉnh tay, không chạm bí mật
- [ ] Text mới có key localization và đã đẩy lên nguồn
- [ ] Báo: lệnh đã chạy, file đổi, kết quả kiểm tra, ĐƯỜNG DẪN ĐẦY ĐỦ từng ảnh, việc CHƯA làm, tác dụng phụ còn lại
```

## Vòng học

- Người dùng sửa cách làm, hoặc 1 lỗi lặp lần 2 → ghi **ngay** (`/gplay-game:learn`): bài học chung vào `LEARNINGS.md`, riêng dự án vào `AGENTS.md` / `game-profile.md`.
- Không đưa luật chơi / tên class của 1 game vào plugin; playbook cơ chế mới chỉ thêm vào `mechanics.md` khi đã dùng ở ≥ 2 game.
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
- `templates/unity/GPlayTestKit/` + `scripts/unity_run.py` (compile / exec / playtest / video): bộ tự chơi dùng chung, chụp ảnh, kiểm méo UI /
  chữ tràn / thiếu glyph, quay video ([autoplay-kit.md](reference/autoplay-kit.md)). Editor đang mở: [unity-mcp.md](reference/unity-mcp.md).
- `scripts/study_video.py <video> <thư mục ra> [--clip t0 t1]`: mổ video gameplay (sheet frame đánh số, điểm cắt cảnh, bảng màu, đoạn frame liên tiếp).
- `scripts/side_by_side.py <ảnh mẫu> <ảnh game> <ra.jpg> [--grid 10] [--blend]`: ghép ảnh so, lưới % để đọc tỉ lệ bố cục.
- `scripts/orch.py`: sổ trạng thái + lịch sử `.game/` (init / phase / log / ms / status / report / history / config / test), xem pipeline.md.
- `templates/plan.md` (theo mốc), `templates/research/` (teardown, visual-spec, base), `templates/art-brief.md`.
