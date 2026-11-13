# Điều khiển Unity Editor đang mở (unity-mcp) — tuỳ chọn

Dùng khi người dùng **không muốn đóng Editor** (batchmode không mở được project đang mở), hoặc cần thao tác nhanh nhiều lần:
xem Game View, vào / ra Play, đọc console, chạy đoạn C#, dựng / sửa object. Tự chơi cả level + kiểm UI + quay video vẫn dùng
[autoplay-kit.md](autoplay-kit.md) (batchmode, lặp lại được, có report). Cả hai có thể gọi chung code driver qua `execute_code`.

Package: CoplayDev **MCP for Unity** (`com.coplaydev.unity-mcp`), đã thử bản v10.3.0 trên Unity 6000.3.

## Cài (người dùng làm trong Unity; Claude hướng dẫn)

1. Cần `uv` (`uvx`): `python -m pip install uv`. pip có thể đặt `uvx.exe` vào thư mục **ngoài PATH**
   (`%APPDATA%\Python\Python3xx\Scripts`) → server không chạy được, log `Library/MCPForUnity/Logs/server-launch-8080.log` ghi "'uvx' is not recognized".
   Sửa: thêm thư mục đó vào Path của tài khoản rồi **tắt hẳn Unity + Hub, mở lại** (hoặc chỉ đường dẫn trong tab Advanced của cửa sổ MCP).
2. Package Manager → Add package from git URL: `https://github.com/CoplayDev/unity-mcp.git?path=/MCPForUnity#v10.3.0` (ghim bản).
3. `Window → MCP for Unity → Toggle MCP Window` (Ctrl+Shift+M) → tab Connect:
   - Client: **Claude Code** → **Claude CLI Path**: chọn `claude.exe` khi báo "Not found" (claude không trong PATH, vd bản trong extension IDE) → **Configure**.
     Đường dẫn extension đổi theo số phiên bản khi tự cập nhật → phải chọn lại.
   - **Start Server** (HTTP Local, `http://127.0.0.1:8080`), chấm xanh = có phiên.
   - Chưa cần **Install Skills** (chép thêm skill vào dự án).
4. Claude Code: `/mcp` hoặc mở phiên mới để nạp tool `UnityMCP` (đăng ký HTTP trong `~/.claude.json` theo thư mục dự án).
   Kiểm server không cần phiên mới: `curl http://127.0.0.1:8080/health` → `"status":"healthy"`.

## Tool dùng nhiều (≈ 50 tool)

| Việc | Tool / action | Ghi chú |
|---|---|---|
| Chụp Game View (gồm UI Overlay) | `manage_camera` `screenshot`, `include_image: true`, `max_resolution` | Ảnh theo cỡ cửa sổ Game View hiện tại. **Ghi thêm file vào `Assets/Screenshots/`** (sinh `.meta`) → xoá sau khi xem hoặc cho vào ignore |
| Chụp Scene View | như trên + `capture_source: "scene_view"` | |
| Vào / tạm dừng / ra Play | `manage_editor` `play` / `pause` / `stop` | ~0,1 s; `stop` ~5 s |
| Đọc console | `read_console` `get` (`types`, `count`, `filter_text`) | |
| Chạy đoạn C# trong Editor | `execute_code` `execute` (`code` = thân method, có `return`) | Chạy tốt ở edit mode; **đang Play thì treo 30 s rồi lỗi** (đã gặp) |
| Scene / object / component / prefab | `manage_scene`, `find_gameobjects`, `manage_gameobject`, `manage_components`, `manage_prefabs` | Thay đổi scene vẫn phải lưu bằng editor; luật "không sửa tay YAML" vẫn giữ |
| Test Unity | `run_tests` → `get_test_job` | |
| Nhiều lệnh 1 lần | `batch_execute` | |
| Gọi menu | `execute_menu_item` | Gọi được menu dựng scene / builder của dự án |

Tool sinh art / model / âm thanh (`generate_*`, `import_model`) cần key dịch vụ ngoài (fal, Tripo, Sketchfab): **không dùng** khi người dùng chưa yêu cầu
(art theo [art-on-demand.md](art-on-demand.md)), không đọc / ghi key.

## Luật

- Editor đang mở + MCP: **không chạy batchmode** trên cùng project (lock); dùng MCP. Muốn batchmode → nhờ người dùng đóng Editor.
- Tool của MCP thao tác trực tiếp trên Editor của người dùng: trước khi sửa scene / asset, kiểm `manage_scene get_active` (`isDirty`) và báo nếu đang có thay đổi chưa lưu.
- Ảnh chụp qua MCP là cỡ Game View hiện tại, không phải cỡ chuẩn: để so với ảnh chuẩn, đặt Game View đúng tỉ lệ (vd 1080×1920) hoặc dùng kit (`-size`).
- Xoá `Assets/Screenshots/` do MCP tạo trước khi báo xong (hoặc thêm vào `.gitignore` nếu dự án có git).
