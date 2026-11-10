# Phát hành

## Trước khi build bản store

```
- [ ] Identity: productName, package id, icon, splash đúng game MỚI (không còn tàn dư game cũ)
- [ ] Keystore của game mới (người dùng tự đặt; agent không đọc mật khẩu)
- [ ] google-services.json / plist, ad unit id, IAP product id, key analytics: bản thật, đúng package
- [ ] Tắt log debug tạm, cheat, nút test; GameLogger mức release
- [ ] Version name + code tăng
- [ ] Chạy thử toàn bộ level (tự chơi batchmode) + 3 level đầu bằng tay trên máy thật
- [ ] Localization đã đồng bộ, font đủ ký tự
- [ ] Không có Missing Script / Missing reference trong scene chính (trừ cái đã ghi chú cố ý)
- [ ] Target API level theo yêu cầu Google Play hiện hành; AAB
- [ ] Privacy policy, consent (UMP) với khu vực cần
```

## Build

- Ra ổ có chỗ trống (không trong repo, không ổ hệ thống đang đầy).
- Xem BuildReport: asset to nhất, texture không nén, audio không nén.

## Hiệu năng mobile

- Texture nén ASTC / ETC2, kích thước bội số 4, không mipmap cho UI / sprite 2D.
- Sprite atlas theo màn; ít material → ít draw call.
- Audio: nhạc nền streaming, SFX nén Vorbis / ADPCM.
- Không cấp phát mỗi frame (LINQ, string concat trong Update).
- Spine: giảm số bone / mesh vertex với nhân vật phụ.
