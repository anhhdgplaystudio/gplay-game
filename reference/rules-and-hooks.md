# Luật an toàn + hook

Luật viết trong tài liệu, agent vẫn vi phạm được. Hook chặn thật.

## Hook của plugin (bật theo dự án)

Plugin gplay-game có sẵn hook PreToolUse (`hooks/hooks.json` → `scripts/guard.py`, exit 2 = chặn, lý do qua stderr).
Hook chỉ chặn ở dự án có `.claude/guard.json` `"enabled": true` (mẫu `templates/guard.json`; `/gplay-game:start` tự chép), dự án khác cho qua.
guard.json: `yaml` (bật / tắt chặn YAML), `secrets`, `no_edit` (glob từ gốc dự án), `no_cmd` (`{pattern, why}`). `guard.json` của plugin = luật chung mọi game, gộp với của dự án.
Thêm luật: `/gplay-game:add-rule`.

| Sự kiện | Chặn / làm |
|---|---|
| PreToolUse `Edit|Write|MultiEdit` | Đường dẫn `.unity .prefab .asset .mat .controller .anim .overrideController .physicsMaterial2D`; sửa / ghi đè `.meta` đã có |
| PreToolUse `Read|Edit|Write` | File bí mật: `*.keystore`, `*.jks`, `google-services.json`, `GoogleService-Info.plist`, mẫu thêm trong `GUARD_SECRETS` |
| PreToolUse `Bash|PowerShell` | Lệnh nhắc tới file bí mật ở trên; `rm -rf` thư mục `Assets`; `git push --force` |
| (tuỳ chọn) PostToolUse `Edit|Write` `*.cs` | Chạy build nhanh, in dòng lỗi |

Thêm mẫu bí mật riêng dự án vào `secrets` của `.claude/guard.json` (biến môi trường `GUARD_SECRETS`, phân cách `;`, vẫn được nhận).

Codex / agy không dùng hook của Claude: muốn chặn chung thì thêm git `pre-commit` kiểm diff YAML lạ (dòng YAML đổi mà không có commit message "builder").

## Lý do từng luật (để agent hiểu, không chỉ tuân)

- **YAML scene / prefab**: file lớn, fileID / GUID chéo nhau; sửa text dễ hỏng tham chiếu mà Unity không báo ngay.
- **`.meta`**: xoá → Unity sinh GUID mới → mọi prefab / scene tham chiếu asset đó thành Missing.
- **Field serialized**: thêm thì an toàn; đổi tên / xoá thì dữ liệu cũ mất im lặng (dùng `[FormerlySerializedAs]` khi đổi tên).
- **Domain reload**: recompile / vào Play / đổi package reset static + bridge → gom sửa rồi kiểm 1 lần.
- **Editor lock**: batchmode không mở được project đang mở trong Editor.
- **Log**: Unity 6 xem `Logs/` của project hoặc `%LOCALAPPDATA%/Unity/Editor/Editor.log`; batchmode thêm `-logFile <file>`.

## Thứ tự ưu tiên khi đổi asset Unity

1. Sửa file nguồn (json / art) → chạy importer.
2. Editor script / menu có sẵn.
3. Viết builder mới (static method, gọi qua menu hoặc `-executeMethod`).
4. Không bao giờ: sửa YAML bằng tay.
