# Localization

## Nguồn

- 1 Google Sheet: cột key + mỗi ngôn ngữ 1 cột. Menu Unity đồng bộ sheet → file text trong `Resources`.
- File `LocalizationExtra.csv` trong repo: key mới chưa có trên sheet (sheet thắng khi trùng).
- Đẩy key lên sheet qua Apps Script web app (token để file riêng, **gitignore, không đọc / in**).

## Key

- Key chung: `s_<màn>_<ý>` (vd `s_win_title`). Key level: `s_lvN_prompt`, `s_lvN_stepI`, `s_lvN_stepI_say`, `s_lvN_stepI_sayJ`, `s_lvN_endK`.
- Dữ liệu level chỉ ghi key, không ghi câu.
- Sắp xếp sheet: key chung trên, key level xuống cuối theo số level.

## Thêm key mới

1. Ghi dòng vào Extra CSV (en + ngôn ngữ biết chắc).
2. Script đẩy: dịch ô trống bằng AI (Gemini qua `agy`, hoặc Claude), ghi lên sheet, sắp lại.
3. Người dùng chạy menu đồng bộ trong Unity.
Sửa câu cũ: sửa Extra + đẩy với cờ ghi đè. Có `--dry-run`.

## Kiểm

- Font phủ đủ ký tự mọi ngôn ngữ (CJK, Thái, Ả Rập, Hindi cần font fallback; font tròn kiểu casual thường chỉ có Latin).
- Câu dài nhất (thường tiếng Đức / Nga) không tràn khung với Best Fit.
- Ả Rập: phải nối chữ + phải sang trái nếu bật ngôn ngữ này.
- Validator: mọi key dùng trong level / UI tồn tại trong sheet hoặc Extra.
