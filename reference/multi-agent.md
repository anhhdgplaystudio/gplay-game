# Giao việc song song (Codex, Gemini / agy, subagent)

Nhờ Codex / Gemini **vẽ art**: xem [art-on-demand.md](art-on-demand.md). Chạy task code bằng phiên claude CLI riêng: [cli-workers.md](cli-workers.md).
File này nói về giao **sản xuất level hàng loạt**.

## Khi nào

Sản xuất nhiều level cùng định dạng, mỗi level độc lập (đọc art + video → viết json + controller). Không dùng cho việc đổi pipeline / base class.

## Vai trò

- Claude: phân tích, viết đề từng level (`templates/level-task.md`), kiểm kết quả, gom lại.
- Agent khác: làm trong phạm vi được ghi, báo cáo theo mẫu.

## Thư mục điều phối (trong repo, vd `Tools/AgentLevels/`)

- `RULES.md`: luật chung (phạm vi được ghi, nguồn kịch bản, lỗi hay gặp, cách tự kiểm, mẫu báo cáo).
- `levels/lvNNN.md`: đề từng level.
- `run.ps1 -Levels lv047,lv048 [-Parallel 1] [-DryRun]`: chạy mỗi level 1 phiên agent, log + `REPORT.md` ra ổ tạm.
- `finish.py`: gom key text, thêm controller vào csproj, build kiểm tra.
- Sau đó **tuần tự**: dựng prefab + tự chơi trong Unity (Unity không chạy song song trên 1 project).

## Luật

- Mặc định chạy **tuần tự**; nhiều agent + build song song dễ treo máy.
- Mỗi agent chỉ ghi vào thư mục level của mình + 1 file controller; không sửa base / importer.
- Build kiểm tra riêng (csproj tạm, output ổ tạm) để chạy song song không giẫm nhau.
- Không tin báo cáo "đã xong": tự chạy validator + xem ảnh tự chơi.

## agy (Gemini CLI) headless

`agy -p "<prompt>" --mode plan|accept-edits|auto [--add-dir <dir>] [--output-format json] [--print-timeout 300s]`.
Headless chặn shell → dặn "chỉ dùng read_file, không chạy lệnh". Phiên giữ sẵn: `--input-format stream-json --output-format stream-json -p=`.
