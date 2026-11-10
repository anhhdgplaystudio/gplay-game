# Vòng meta, quảng cáo, analytics

## Vòng chơi

Play level → Win (coin, video nhân x2 / x3 level khó) hoặc Lose (video hồi sinh / chơi lại) → level kế.
Coin dùng cho hint / skip / booster. Phụ: daily reward, lucky spin, starter pack, remove ads.

## Đặt quảng cáo (mặc định, chỉnh theo game-profile)

- **Rewarded**: chỉ khi người chơi chủ động bấm (hint, skip, hồi sinh, nhân thưởng, quay thêm). Không ép.
- **Interstitial**: giữa level (sau Win / trước level kế), có khoảng cách thời gian tối thiểu và không hiện ở vài level đầu.
- **Banner**: đáy màn; UI chừa chỗ (xem ui-from-mockup.md).
- Remove ads: tắt interstitial + banner, **giữ** rewarded.
- Không có mạng: không chặn chơi; nút rewarded báo "chưa có video".
- Level dạy chơi (1–3): không quảng cáo, không thua.

## Analytics (tên event thống nhất)

`level_start {level, mode}` · `level_complete {level, time, mistakes, hint_used}` · `level_fail {level, reason, step}` ·
`ad_rewarded_show/complete {placement}` · `ad_inter_show {placement}` · `iap_purchase {product}` · `tutorial_step {n}`.
Theo dõi bước bị kẹt (`step`) để chỉnh level khó.

## Độ khó

- Đường độ khó răng cưa: dễ → khó → 1 level dễ thư giãn.
- Level khó đánh dấu trong database (thưởng cao hơn).
- Cơ chế có solver: dùng số liệu solver (số nước, tỉ lệ thua random) để xếp thứ tự level.
