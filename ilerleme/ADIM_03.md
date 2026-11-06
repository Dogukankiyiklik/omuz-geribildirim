# ADIM 03 — Deney 1b (genel bant / kişiye özel bant) + Deney 1c (zamansal yumuşatma)

**Tarih:** 2026-11-06
**Durum:** Tamamlandı. Kullanıcı iki deneyi çalıştırdı (Deney 1b 22:51, Deney 1c 23:05). Sayılar `sonuclar/deney1b/` ve `sonuclar/deney1c/` altındaki CSV dosyalarından birebir kopyalandı.

## Basit anlatım
**En önemli tek sonuç:** Kişiye özel kalibrasyon şart. Başkalarının doğru tekrarlarından kurulan "genel" bant, omuz silkmesini bulmada kişiye özel banttan çok daha kötü. Hatta bant hiç kullanmamaktan bile iyi değil.

**Bu sayı ne demek?** 100 çift düşün: her çiftte rastgele bir silkmeli tekrar ve aynı kamera açısından rastgele bir doğru tekrar var. Sistem kaç çiftte silkmeli olana daha yüksek hata puanı veriyor? (açı bandı, YENI ölçütü)
- kişiye özel bant: yaklaşık **95** çiftte (AUC 0,947);
- bant yok: yaklaşık **70** çiftte (AUC 0,704);
- genel bant, diğer 4 kişinin tüm tekrarları: yaklaşık **67** çiftte (AUC 0,666);
- genel bant, başka tek bir kişinin kalibrasyonu: yaklaşık **62** çiftte (AUC 0,618).

50, yazı-tura demek. Yani genel bant neredeyse yazı-turaya yaklaşıyor. **Sebep:** İnsanların "normal" omuz duruşu birbirinden çok farklı. Başkasının normaline göre bakınca, kişinin **doğru** tekrarları bile "anormal" görünüyor: YENI'de doğru tekrarların ortalama hata puanı genel bantta 0,54–0,65, kişiye özel bantta 0,10 (aynı kodla yapılan kod denemesinin tekrar tablosundan). Bu yüzden asıl farkı, yani silkmeyi, ayırt edemiyor.

**İkinci sonuç (yumuşatma):** Filtreler noktalardaki titremeyi büyük ölçüde azaltıyor; omuzdaki titreme ölçüsü ayara göre %38–87 düşüyor. Ama silkmeyi bulma başarısı **değişmiyor**. Bütün farklar ±0,006 içinde ve büyük çoğunluğunun güven aralığı sıfırı içeriyor. Yorum: MediaPipe'ın kare kare titremesi silkmeyi kaçırmamızın sebebi değil. Bu yöntem, hocanın önerdiği bir iyileştirmenin işe **yaramadığını** gösteren dürüst bir olumsuz sonuç.

## Yapılanlar
- **Deney 1b** (`deneyler/deney1b.py`): "Kalibrasyon kişiye özel olmak zorunda mı?" Dört koşul, iki bant türüyle (v1b ve v2):

  | koşul | bant neyle kuruluyor? |
  | --- | --- |
  | `bant_yok` | Bant yok. Deney 1'deki "ham" skor (tekrar başına göre mutlak sapmanın %90 yüzdeliği). |
  | `genel_tum` | Aynı kamera ve yönelimde **diğer 4 kişinin bütün doğru tekrarları** (~20). |
  | `genel_tek` | **Başka tek bir kişinin** doğru tekrarları (~5). Diğer 4 kişinin her biri sırayla denenir, E'lerin ortalaması alınır. |
  | `kisiye_ozel` | Deney 1 v2'deki v1b / v2, aynı kod (Karar 7 dahil). |

- **Deney 1c** (`deneyler/deney1c.py`): "Noktalardaki titremeyi filtrelemek silkmeyi bulmayı iyileştiriyor mu?"
  - İki filtre (`cekirdek/yumusatma.py`):
    - **One Euro:** yalnızca geçmiş kareleri kullanır, canlı uygulamaya uygun.
    - **Savitzky–Golay:** geleceği de kullanır, tekrar bittikten sonra uygulanır.
  - Filtreler noktaların x, y koordinatlarına, ölçütler hesaplanmadan önce uygulanıyor.
  - Bant kişiye özel (v1b ve v2); ölçütler YENI, M33 ve M39_F2.
  - Filtre ayarı her test kişisi için **diğer 4 kişide** seçiliyor (birini-dışarıda-bırak).
  - Ayrıca titreme ölçüsü (`titreme.csv`) ve şekil (`titreme.png`) üretiliyor.
- **Çekirdek:**
  - `cekirdek/bant.py`: `coklu_referans_modelleri` ve `coklu_model_hatasi` eklendi. Çoklu referans bantları bir kez kurulup birçok tekrarda kullanılabiliyor (genel bant için). `coklu_referans_hatasi` bunları çağırıyor; sonucu aynı.
  - `cekirdek/yumusatma.py` (yeni).
- **Ortak tablolar** (`deneyler/tablolar.py`, yeni): AUC özeti (tüm görüşler + önden/çapraz, Karar 6), kişi AUC'si ve koşul farkları için kişi bazlı bootstrap. Adım 4'te de kullanılacak.
- **Testler:** `test_yumusatma` ve `test_genel_bant_test_kisisini_icermez` eklendi → `42 passed`.

## Değişen / eklenen dosyalar
| Dosya | Ne işe yarıyor |
| --- | --- |
| `deneyler/deney1b.py` | Deney 1b: bant yok / genel (tümü) / genel (tek kişi) / kişiye özel |
| `deneyler/deney1c.py` | Deney 1c: yumuşatma, birini-dışarıda-bırak parametre seçimi, titreme tablosu ve şekli |
| `deneyler/tablolar.py` | Ortak AUC, kişi AUC ve bootstrap tabloları |
| `cekirdek/yumusatma.py` | One Euro ve Savitzky–Golay filtreleri |
| `cekirdek/bant.py` | `coklu_referans_modelleri`, `coklu_model_hatasi` |
| `testler/test_aci_bandi.py` | 2 yeni test |

## Nasıl çalıştırılır
```bash
python -m deneyler.deney1b      # ~1–2 dk  → sonuclar/deney1b/
python -m deneyler.deney1c      # ~15 dk   → sonuclar/deney1c/ (21 filtre ayarı × 2 bant)
```

## Sonuçlar — Deney 1b

### 1. AUC tablosu (`sonuclar/deney1b/ozet.csv`; YENI, M33, M39_F2)
"ö+ç" = önden + çapraz (|görüş| ≤ 60°, uygulama senaryosu). "kişi özeti" = 5 kişinin silkme/doğru AUC'si, ortalama (en düşük–en yüksek). `bant_yok` satırları iki bant türünde aynı olduğu için bir kez verildi.

| bant | koşul | ölçüt | silkme/doğru | silkme/doğru (ö+ç) | silkme/diğer | silkme/diğer (ö+ç) | önden | çapraz | profil | kişi özeti |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| — | bant_yok | YENI | 0.704 | 0.761 | 0.699 | 0.753 | 0.767 | 0.759 | 0.554 | 0,78 (0,72–0,87) |
| — | bant_yok | M33 | 0.638 | 0.689 | 0.695 | 0.765 | 0.746 | 0.664 | 0.593 | 0,66 (0,49–0,81) |
| — | bant_yok | M39_F2 | 0.600 | 0.617 | 0.644 | 0.695 | 0.684 | 0.599 | 0.559 | 0,61 (0,50–0,74) |
| v1b | genel_tum | YENI | 0.643 | 0.673 | 0.560 | 0.578 | 0.661 | 0.683 | 0.494 | 0,67 (0,39–0,86) |
| v1b | genel_tum | M33 | 0.705 | 0.724 | 0.565 | 0.561 | 0.781 | 0.692 | 0.616 | 0,71 (0,54–0,88) |
| v1b | genel_tum | M39_F2 | 0.635 | 0.660 | 0.557 | 0.566 | 0.675 | 0.645 | 0.529 | 0,64 (0,44–0,75) |
| v1b | genel_tek | YENI | 0.665 | 0.707 | 0.575 | 0.596 | 0.708 | 0.723 | 0.565 | 0,68 (0,45–0,85) |
| v1b | genel_tek | M33 | 0.720 | 0.745 | 0.597 | 0.603 | 0.840 | 0.678 | 0.636 | 0,72 (0,63–0,89) |
| v1b | genel_tek | M39_F2 | 0.622 | 0.652 | 0.571 | 0.582 | 0.687 | 0.626 | 0.533 | 0,63 (0,43–0,75) |
| v1b | kisiye_ozel | YENI | 0.940 | 0.955 | 0.721 | 0.752 | 0.949 | 0.958 | 0.863 | 0,94 (0,84–0,99) |
| v1b | kisiye_ozel | M33 | 0.925 | 0.934 | 0.649 | 0.652 | 0.938 | 0.932 | 0.877 | 0,92 (0,79–0,99) |
| v1b | kisiye_ozel | M39_F2 | 0.914 | 0.924 | 0.645 | 0.655 | 0.910 | 0.934 | 0.859 | 0,91 (0,78–0,99) |
| v2 | genel_tum | YENI | 0.666 | 0.683 | 0.649 | 0.651 | 0.653 | 0.704 | 0.603 | 0,72 (0,47–0,92) |
| v2 | genel_tum | M33 | 0.709 | 0.741 | 0.633 | 0.651 | 0.798 | 0.705 | 0.586 | 0,71 (0,59–0,88) |
| v2 | genel_tum | M39_F2 | 0.663 | 0.706 | 0.596 | 0.621 | 0.766 | 0.664 | 0.538 | 0,65 (0,31–0,80) |
| v2 | genel_tek | YENI | 0.618 | 0.634 | 0.603 | 0.612 | 0.562 | 0.689 | 0.701 | 0,64 (0,37–0,81) |
| v2 | genel_tek | M33 | 0.728 | 0.768 | 0.654 | 0.678 | 0.872 | 0.699 | 0.615 | 0,71 (0,64–0,84) |
| v2 | genel_tek | M39_F2 | 0.692 | 0.743 | 0.629 | 0.661 | 0.829 | 0.686 | 0.578 | 0,68 (0,44–0,80) |
| v2 | kisiye_ozel | YENI | 0.947 | 0.968 | 0.829 | 0.862 | 0.979 | 0.960 | 0.842 | 0,95 (0,84–0,98) |
| v2 | kisiye_ozel | M33 | 0.924 | 0.957 | 0.754 | 0.779 | 0.971 | 0.947 | 0.756 | 0,92 (0,83–0,97) |
| v2 | kisiye_ozel | M39_F2 | 0.909 | 0.942 | 0.719 | 0.750 | 0.949 | 0.938 | 0.731 | 0,91 (0,85–0,96) |

M01 ve M01_tek satırları `ozet.csv`'de; örüntü aynı (ör. v2 M01: bant_yok 0.650, genel_tum 0.700, genel_tek 0.724, kisiye_ozel 0.858). Hiçbir tekrarın E'si boş değil.

### 2. Kişi bazlı AUC silkme/doğru, YENI (`kisi_auc.csv`)
| bant | koşul | Honza | Mima | Petra | Terka | Vasil |
| --- | --- | --- | --- | --- | --- | --- |
| — | bant_yok | 0.873 | 0.802 | 0.719 | 0.774 | 0.719 |
| v1b | genel_tum | 0.794 | 0.864 | 0.388 | 0.606 | 0.706 |
| v1b | genel_tek | 0.782 | 0.852 | 0.447 | 0.608 | 0.713 |
| v1b | kisiye_ozel | 0.991 | 0.971 | 0.929 | 0.971 | 0.844 |
| v2 | genel_tum | 0.920 | 0.753 | 0.465 | 0.676 | 0.773 |
| v2 | genel_tek | 0.737 | 0.812 | 0.370 | 0.562 | 0.713 |
| v2 | kisiye_ozel | 0.975 | 0.954 | 0.981 | 0.982 | 0.844 |

Önden + çapraz kişi tablosu: `kisi_auc_onden_capraz.csv`.

### 3. AUC farkları, silkme/doğru, kişi bazlı bootstrap 2000 tekrar (`bootstrap.csv`)
| bant | görüş | ölçüt | fark | nokta tahmini | %95 GA |
| --- | --- | --- | --- | --- | --- |
| v1b | tüm görüşler | YENI | genel_tum − kisiye_ozel | −0.2971 | −0.4303 – −0.1523 |
| v1b | tüm görüşler | YENI | genel_tek − kisiye_ozel | −0.2756 | −0.3899 – −0.1510 |
| v1b | tüm görüşler | YENI | kisiye_ozel − bant_yok | +0.2361 | +0.1463 – +0.2870 |
| v1b | tüm görüşler | M33 | genel_tum − kisiye_ozel | −0.2191 | −0.3370 – −0.1167 |
| v1b | tüm görüşler | M33 | genel_tek − kisiye_ozel | −0.2045 | −0.3051 – −0.1097 |
| v1b | tüm görüşler | M33 | kisiye_ozel − bant_yok | +0.2865 | +0.2129 – +0.3527 |
| v1b | tüm görüşler | M39_F2 | genel_tum − kisiye_ozel | −0.2787 | −0.4049 – −0.1929 |
| v1b | tüm görüşler | M39_F2 | genel_tek − kisiye_ozel | −0.2918 | −0.4246 – −0.1845 |
| v1b | tüm görüşler | M39_F2 | kisiye_ozel − bant_yok | +0.3133 | +0.2342 – +0.3887 |
| v1b | önden+çapraz | YENI | genel_tum − kisiye_ozel | −0.2822 | −0.4425 – −0.1257 |
| v1b | önden+çapraz | YENI | genel_tek − kisiye_ozel | −0.2481 | −0.3957 – −0.0916 |
| v1b | önden+çapraz | YENI | kisiye_ozel − bant_yok | +0.1939 | +0.0795 – +0.2506 |
| v1b | önden+çapraz | M33 | genel_tum − kisiye_ozel | −0.2103 | −0.3322 – −0.1088 |
| v1b | önden+çapraz | M33 | genel_tek − kisiye_ozel | −0.1893 | −0.2954 – −0.0934 |
| v1b | önden+çapraz | M33 | kisiye_ozel − bant_yok | +0.2457 | +0.1484 – +0.3449 |
| v1b | önden+çapraz | M39_F2 | genel_tum − kisiye_ozel | −0.2645 | −0.4116 – −0.1583 |
| v1b | önden+çapraz | M39_F2 | genel_tek − kisiye_ozel | −0.2717 | −0.4366 – −0.1295 |
| v1b | önden+çapraz | M39_F2 | kisiye_ozel − bant_yok | +0.3075 | +0.2378 – +0.3767 |
| v2 | tüm görüşler | YENI | genel_tum − kisiye_ozel | −0.2804 | −0.4063 – −0.1405 |
| v2 | tüm görüşler | YENI | genel_tek − kisiye_ozel | −0.3285 | −0.4839 – −0.1838 |
| v2 | tüm görüşler | YENI | kisiye_ozel − bant_yok | +0.2424 | +0.1417 – +0.3046 |
| v2 | tüm görüşler | M33 | genel_tum − kisiye_ozel | −0.2146 | −0.3012 – −0.1443 |
| v2 | tüm görüşler | M33 | genel_tek − kisiye_ozel | −0.1961 | −0.2689 – −0.1425 |
| v2 | tüm görüşler | M33 | kisiye_ozel − bant_yok | +0.2859 | +0.2105 – +0.3631 |
| v2 | tüm görüşler | M39_F2 | genel_tum − kisiye_ozel | −0.2459 | −0.4226 – −0.1255 |
| v2 | tüm görüşler | M39_F2 | genel_tek − kisiye_ozel | −0.2172 | −0.3620 – −0.1168 |
| v2 | tüm görüşler | M39_F2 | kisiye_ozel − bant_yok | +0.3087 | +0.2530 – +0.3619 |
| v2 | önden+çapraz | YENI | genel_tum − kisiye_ozel | −0.2848 | −0.4023 – −0.1447 |
| v2 | önden+çapraz | YENI | genel_tek − kisiye_ozel | −0.3337 | −0.5173 – −0.1534 |
| v2 | önden+çapraz | YENI | kisiye_ozel − bant_yok | +0.2064 | +0.0865 – +0.2700 |
| v2 | önden+çapraz | M33 | genel_tum − kisiye_ozel | −0.2159 | −0.3186 – −0.1133 |
| v2 | önden+çapraz | M33 | genel_tek − kisiye_ozel | −0.1884 | −0.2926 – −0.0999 |
| v2 | önden+çapraz | M33 | kisiye_ozel − bant_yok | +0.2683 | +0.1551 – +0.3749 |
| v2 | önden+çapraz | M39_F2 | genel_tum − kisiye_ozel | −0.2366 | −0.4484 – −0.1140 |
| v2 | önden+çapraz | M39_F2 | genel_tek − kisiye_ozel | −0.1995 | −0.3850 – −0.0951 |
| v2 | önden+çapraz | M39_F2 | kisiye_ozel − bant_yok | +0.3254 | +0.2686 – +0.3882 |

**36 farkın hiçbirinin güven aralığı sıfırı içermiyor.** Genel bant her zaman kişiye özelden kötü (−0,19 ile −0,33 arası). Kişiye özel bant her zaman bantsızdan iyi (+0,19 ile +0,33 arası).

### Ne çıktı? (Deney 1b)
- **Kişiye özel kalibrasyon gerekli:** İki bant türünde, üç ölçütte ve iki görüş kapsamında genel bant kişiye özel banttan 0,19–0,33 AUC geride.
- **Genel bant, bant kullanmamaktan da iyi değil:** YENI'de genel bant bantsızın **altında** (0.704'e karşı v1b 0.643 / v2 0.666 / genel_tek 0.618–0.665). M33 ve M39_F2'de biraz üstünde (ör. M33 0.638 → 0.705–0.728). Bu farklar için bootstrap hesaplanmadı.
- **Az ama kişinin kendi tekrarı, çok ama başkasının tekrarından iyi:** 20 tekrarlık genel bant (`genel_tum`) ile 5 tekrarlık tek kişi bandı (`genel_tek`) arasında tutarlı bir fark yok. Kişiye özel bant ise yalnızca 4 tekrarla çok daha iyi.
- **Kişiler arası fark büyük:** Petra'da genel bant rastgeleden kötü (YENI 0.370–0.465). Silkmeli tekrarlarına doğru tekrarlarından **düşük** puan veriyor. Muhtemel sebep: Petra'nın doğal kulak–omuz mesafesi diğerlerinden farklı, bu yüzden doğru tekrarları da genel bandın dışında kalıyor (incelenmedi).
- **Silkme/diğer ayrımında** da genel bant kişiye özelden kötü (v2 YENI 0.649 / 0.603'e karşı 0.829).

## Sonuçlar — Deney 1c

### 4. AUC tablosu (`sonuclar/deney1c/ozet.csv`)
`one_euro` ve `savgol` satırları: her test kişisi, diğer 4 kişide seçilen ayarla puanlandı.

| bant | koşul | ölçüt | silkme/doğru | silkme/doğru (ö+ç) | silkme/diğer | silkme/diğer (ö+ç) | önden | çapraz | profil | kişi özeti |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v1b | yumusatmasiz | YENI | 0.940 | 0.955 | 0.721 | 0.752 | 0.949 | 0.958 | 0.863 | 0,94 (0,84–0,99) |
| v1b | one_euro | YENI | 0.940 | 0.954 | 0.721 | 0.752 | 0.944 | 0.961 | 0.869 | 0,94 (0,84–0,99) |
| v1b | savgol | YENI | 0.940 | 0.956 | 0.720 | 0.752 | 0.949 | 0.960 | 0.859 | 0,94 (0,84–0,99) |
| v1b | yumusatmasiz | M33 | 0.925 | 0.934 | 0.649 | 0.652 | 0.938 | 0.932 | 0.877 | 0,92 (0,79–0,99) |
| v1b | one_euro | M33 | 0.920 | 0.931 | 0.647 | 0.650 | 0.934 | 0.928 | 0.864 | 0,92 (0,79–0,99) |
| v1b | savgol | M33 | 0.924 | 0.934 | 0.650 | 0.652 | 0.939 | 0.930 | 0.870 | 0,92 (0,79–0,99) |
| v1b | yumusatmasiz | M39_F2 | 0.914 | 0.924 | 0.645 | 0.655 | 0.910 | 0.934 | 0.859 | 0,91 (0,78–0,99) |
| v1b | one_euro | M39_F2 | 0.914 | 0.922 | 0.647 | 0.658 | 0.908 | 0.931 | 0.876 | 0,91 (0,79–0,99) |
| v1b | savgol | M39_F2 | 0.915 | 0.924 | 0.646 | 0.655 | 0.910 | 0.933 | 0.870 | 0,91 (0,78–0,99) |
| v2 | yumusatmasiz | YENI | 0.947 | 0.968 | 0.829 | 0.862 | 0.979 | 0.960 | 0.842 | 0,95 (0,84–0,98) |
| v2 | one_euro | YENI | 0.943 | 0.966 | 0.824 | 0.860 | 0.974 | 0.960 | 0.834 | 0,94 (0,83–0,99) |
| v2 | savgol | YENI | 0.947 | 0.967 | 0.826 | 0.860 | 0.978 | 0.960 | 0.844 | 0,95 (0,84–0,98) |
| v2 | yumusatmasiz | M33 | 0.924 | 0.957 | 0.754 | 0.779 | 0.971 | 0.947 | 0.756 | 0,92 (0,83–0,97) |
| v2 | one_euro | M33 | 0.925 | 0.954 | 0.751 | 0.777 | 0.962 | 0.947 | 0.778 | 0,93 (0,82–0,97) |
| v2 | savgol | M33 | 0.924 | 0.950 | 0.756 | 0.775 | 0.963 | 0.940 | 0.786 | 0,92 (0,81–0,98) |
| v2 | yumusatmasiz | M39_F2 | 0.909 | 0.942 | 0.719 | 0.750 | 0.949 | 0.938 | 0.731 | 0,91 (0,85–0,96) |
| v2 | one_euro | M39_F2 | 0.915 | 0.944 | 0.728 | 0.760 | 0.946 | 0.942 | 0.759 | 0,91 (0,82–0,96) |
| v2 | savgol | M39_F2 | 0.913 | 0.942 | 0.722 | 0.749 | 0.948 | 0.937 | 0.760 | 0,91 (0,86–0,96) |

v2 + One Euro satırlarında **1 tekrarın E'si boş (NaN)**, AUC'den çıkarıldı: `ex1_Vasil cam1 yönelim 90 tekrar 9`, doğru tekrar, profil (−90°). Bazı One Euro ayarlarında bu tekrarın hiçbir karesi açı bandının geçerli kutularına düşmüyor (kapsam 0).

### 5. AUC farkı (silkme/doğru), filtre − yumuşatmasız, bootstrap 2000 (`bootstrap.csv`)
| bant | görüş | ölçüt | fark | nokta tahmini | %95 GA |
| --- | --- | --- | --- | --- | --- |
| v1b | tüm görüşler | YENI | one_euro − yumusatmasiz | −0.0004 | −0.0036 – +0.0038 |
| v1b | tüm görüşler | YENI | savgol − yumusatmasiz | −0.0005 | −0.0020 – +0.0018 |
| v1b | tüm görüşler | M33 | one_euro − yumusatmasiz | −0.0051 | −0.0096 – −0.0010 |
| v1b | tüm görüşler | M33 | savgol − yumusatmasiz | −0.0011 | −0.0031 – +0.0014 |
| v1b | tüm görüşler | M39_F2 | one_euro − yumusatmasiz | +0.0007 | −0.0031 – +0.0060 |
| v1b | tüm görüşler | M39_F2 | savgol − yumusatmasiz | +0.0011 | −0.0014 – +0.0038 |
| v1b | önden+çapraz | YENI | one_euro − yumusatmasiz | −0.0007 | −0.0036 – +0.0014 |
| v1b | önden+çapraz | YENI | savgol − yumusatmasiz | +0.0006 | −0.0008 – +0.0025 |
| v1b | önden+çapraz | M33 | one_euro − yumusatmasiz | −0.0037 | −0.0084 – −0.0006 |
| v1b | önden+çapraz | M33 | savgol − yumusatmasiz | −0.0002 | −0.0016 – +0.0010 |
| v1b | önden+çapraz | M39_F2 | one_euro − yumusatmasiz | −0.0026 | −0.0048 – +0.0007 |
| v1b | önden+çapraz | M39_F2 | savgol − yumusatmasiz | −0.0006 | −0.0020 – +0.0019 |
| v2 | tüm görüşler | YENI | one_euro − yumusatmasiz | −0.0037 | −0.0181 – +0.0074 |
| v2 | tüm görüşler | YENI | savgol − yumusatmasiz | +0.0002 | −0.0031 – +0.0035 |
| v2 | tüm görüşler | M33 | one_euro − yumusatmasiz | +0.0008 | −0.0107 – +0.0142 |
| v2 | tüm görüşler | M33 | savgol − yumusatmasiz | +0.0002 | −0.0108 – +0.0091 |
| v2 | tüm görüşler | M39_F2 | one_euro − yumusatmasiz | +0.0056 | −0.0165 – +0.0253 |
| v2 | tüm görüşler | M39_F2 | savgol − yumusatmasiz | +0.0045 | +0.0008 – +0.0095 |
| v2 | önden+çapraz | YENI | one_euro − yumusatmasiz | −0.0013 | −0.0102 – +0.0045 |
| v2 | önden+çapraz | YENI | savgol − yumusatmasiz | −0.0002 | −0.0032 – +0.0033 |
| v2 | önden+çapraz | M33 | one_euro − yumusatmasiz | −0.0031 | −0.0187 – +0.0083 |
| v2 | önden+çapraz | M33 | savgol − yumusatmasiz | −0.0070 | −0.0198 – +0.0015 |
| v2 | önden+çapraz | M39_F2 | one_euro − yumusatmasiz | +0.0015 | −0.0250 – +0.0209 |
| v2 | önden+çapraz | M39_F2 | savgol − yumusatmasiz | −0.0004 | −0.0027 – +0.0024 |

24 farktan 21'inin GA'sı sıfırı içeriyor. Sıfırı içermeyen üç fark çok küçük:
- v1b M33 One Euro: −0.0051 (tüm görüşler) ve −0.0037 (önden + çapraz); ikisi de kötüleşme;
- v2 M39_F2 Savitzky–Golay, tüm görüşler: +0.0045.

### 6. Seçilen ayarlar (`secim.csv`)
| bant | filtre | ölçüt | Honza | Mima | Petra | Terka | Vasil |
| --- | --- | --- | --- | --- | --- | --- | --- |
| v1b | One Euro | YENI | 4 / 1 | 4 / 1 | 4 / 1 | 4 / 1 | 2 / 1 |
| v1b | One Euro | M33 | 4 / 10 | 4 / 10 | 4 / 1 | 4 / 10 | 4 / 10 |
| v1b | One Euro | M39_F2 | 0,5 / 10 | 1 / 10 | 0,5 / 10 | 0,5 / 10 | 0,5 / 10 |
| v1b | Sav.–Gol. | YENI | 9 / 2 | 9 / 2 | 9 / 2 | 5 / 3 | 5 / 2 |
| v1b | Sav.–Gol. | M33 | 5 / 2 | 5 / 2 | 5 / 2 | 5 / 2 | 5 / 2 |
| v1b | Sav.–Gol. | M39_F2 | 5 / 2 | 5 / 2 | 5 / 2 | 5 / 2 | 5 / 2 |
| v2 | One Euro | YENI | 4 / 1 | 4 / 10 | 0,5 / 10 | 4 / 1 | 2 / 1 |
| v2 | One Euro | M33 | 0,5 / 10 | 0,5 / 1 | 0,5 / 10 | 4 / 10 | 0,5 / 1 |
| v2 | One Euro | M39_F2 | 0,5 / 10 | 0,5 / 10 | 0,5 / 10 | 0,5 / 10 | 0,5 / 1 |
| v2 | Sav.–Gol. | YENI | 15 / 2 | 5 / 2 | 15 / 2 | 15 / 2 | 9 / 3 |
| v2 | Sav.–Gol. | M33 | 5 / 2 | 5 / 2 | 5 / 2 | 5 / 2 | 21 / 3 |
| v2 | Sav.–Gol. | M39_F2 | 5 / 2 | 5 / 2 | 5 / 2 | 5 / 2 | 5 / 2 |

(One Euro: min_kesim Hz / beta. Savitzky–Golay: pencere / derece. Test kişisi sütundaki kişi; ayar diğer 4 kişide seçildi.)

### 7. Titreme ölçüsü (`titreme.csv`; doğru tekrarlar, ikinci farkın medyan RMS'inin ham değere oranı)
| ayar | sağ omuz | sağ kulak |
| --- | --- | --- |
| ham | 1.0000 | 1.0000 |
| One Euro 0,5 Hz, beta 0 (en güçlü) | 0.1308 | 0.1073 |
| One Euro 4 Hz, beta 10 (en zayıf) | 0.4965 | 0.4512 |
| Savitzky–Golay pencere 5, derece 2 (en zayıf) | 0.6215 | 0.5929 |
| Savitzky–Golay pencere 21, derece 2 (en güçlü) | 0.2055 | 0.1625 |

21 ayarın tamamı `titreme.csv`'de. Ham değerler: sağ omuz 0.0005, sağ kulak 0.0003 (görüntü yüksekliği birimi/kare²).

### Ne çıktı? (Deney 1c)
- **Filtreler titremeyi azaltıyor:** Omuz noktasının ivme benzeri titreme ölçüsü, ayara göre ham değerin %13–62'sine iniyor.
- **Ama silkmeyi bulma başarısı değişmiyor:** Bütün farklar ±0,006 içinde; çoğunun GA'sı sıfırı içeriyor.
- **Seçilen ayarlar kişiden kişiye değişiyor** (ör. v2 YENI One Euro'da min_kesim 0,5 ile 4 arası). Bu da ayarlar arasındaki AUC farklarının gürültü düzeyinde olduğunu gösteriyor.
- **Yorum:** Silkme, MediaPipe'ın kare kare titremesinden çok daha büyük ve daha yavaş bir hareket. Bant yöntemi zaten tekrar boyunca ortalama alıyor (E = kare hatalarının ortalaması). Bu yüzden ek yumuşatma bir şey kazandırmıyor. Hatanın kaynağı titreme değil; kişiler arası farklar, görüş açısı ve etiket belirsizliği gibi daha büyük etkenler.
- **One Euro gecikmesi:** `titreme.png`'de One Euro eğrisi ham eğrinin gerisinde kalıyor (gözle bakıldı, ölçülmedi). Canlı uygulamada kullanılırsa geri bildirim biraz gecikebilir.

## Kabul ölçütü kontrolü
- [x] Üç koşulun tablosu (bant yok / genel / kişiye özel) ve "genel bant − kişiye özel bant" farkı için güven aralığı (`deney1b/ozet.csv`, `deney1b/bootstrap.csv`)
- [x] Yumuşatmalı ve yumuşatmasız karşılaştırma tablosu (`deney1c/ozet.csv`, `deney1c/bootstrap.csv`) ve titreme şekli (`deney1c/titreme.png`)
- [x] Her ana sonuç iki biçimde: "önden + çapraz" ve "tüm görüşler" (Karar 6)
- [x] Kişi bazlı AUC tabloları (Karar 5)
- [x] Testler: `42 passed`

## Kararlar ve sapmalar
Hepsi kod yazılırken, tam deney sonuçlarına bakılmadan verildi.

**Deney 1b**
- **İki genel bant var.** PLAN "adil olmak için kişiye özel bantla aynı sayıda tekrar kullanılabilir (örneğin 4)" diyor. Rastgele 4 tekrar seçmek yeniden rastgelelik getirirdi. Onun yerine iki deterministik koşul kuruldu:
  - `genel_tum`: elimizdeki en güçlü genel model (~20 tekrar).
  - `genel_tek`: başka tek bir kişinin kalibrasyonu (~5 tekrar). Bu, kişiye özel modeldeki n−1 ≈ 4 tekrara yakın. 4 kişinin her biri sırayla kullanılıyor ve E'lerin ortalaması alınıyor; bu Karar 7'deki ortalamaya benzer.
- **Adillik:** Genel bantta test kişisinin hiçbir tekrarı modelde değil. Bu yüzden kişinin bütün tekrarları (doğru ve hatalı) aynı modelle değerlendiriliyor; birini-dışarıda-bırak gerekmiyor.
- **v1b genel bant:** Modeldeki her doğru tekrar sırayla referans (çoklu referans), tıpkı kişiye özel v1b'de olduğu gibi.
- **`bant_yok`:** Deney 1'deki ham skor tanımı aynen kullanıldı (pay dahil tüm dizi). Bant türüne bağlı olmadığı için v1b ve v2 tablolarında aynı sayılar görünüyor.
- **Hata arama:** Kod denemesinde genel bandın bant yok koşulunun altına düşmesi beklenmedikti. Şunlara bakıldı:
  - genel bantta test kişisinin hiçbir tekrarı yok (test eklendi);
  - E'nin üst sınıra (1) dayanması az: genel bantta doğru tekrarların ~%10'unda E > 0,95;
  - dinlenmeye göre ölçülen M01'de de aynı örüntü var.
  Hata bulunmadı.

**Deney 1c**
- **Parametre ızgarası** (önceden sabit):
  - One Euro: min_kesim ∈ {0,5; 1; 2; 4} Hz × beta ∈ {0; 1; 10}, d_kesim = 1 Hz → 12 ayar.
  - Savitzky–Golay: pencere ∈ {5; 9; 15; 21} kare × derece ∈ {2; 3} → 8 ayar.
- **Seçim ölçütü:** Eğitim kişilerinin (test kişisi hariç 4 kişi) birleşik AUC silkme/doğru değeri, tüm görüşler üzerinden. Seçim her (bant, filtre, ölçüt) için ayrı yapılıyor. Eşitlikte ızgaradaki ilk ayar seçiliyor.
- **E bir kez hesaplanıyor:** Kişiye özel bantta bir tekrarın E'si yalnızca o kişinin verisine bağlı. Bu yüzden her ayar için E bir kez hesaplanıyor; test kişisinin verisi seçime hiç girmiyor.
- **"Seçilmiş" sonuç:** Her kişinin tekrarları kendi seçilen ayarıyla puanlanıyor, sonra AUC bütün kişiler üzerinden hesaplanıyor. `izgara.csv` her ayarın AUC'sini de veriyor. Bu tablo yalnızca şeffaflık için; test sonucu değil, çünkü "en iyi ayara" bakmak test verisiyle seçmek olur.
- **Filtre ham (0–1) koordinatlara uygulanıyor,** en-boy düzeltmesinden önce. Tekrarlar kesik dizi olduğu için One Euro her tekrarın ilk karesinden (pay başı) yeniden başlıyor. Canlı uygulamada filtre kesintisiz çalışacak.
- **Titreme ölçüsü:** Doğru tekrarlarda sağ omuz ve sağ kulak noktasının ikinci farkının (ivme benzeri) RMS'i. Hareketin kendisi de bu sayıya katkı veriyor; değer saf gürültü değil, filtrelerin karşılaştırması için kaba bir gösterge.
- **`titreme.png` örneği:** `ex1_Honza cam1 yönelim 0`'ın ilk doğru tekrarı. Çizilen ayarlar, v2 / YENI seçiminde en sık seçilen ayarlar.

## Açık sorular / danışmana notlar
- **Önerim: yumuşatma ana yöntemde kullanılmasın.** Kazanç yok, One Euro ise gecikme ekliyor. Raporda Problem 2 için "denendi, etkisiz" diye olumsuz sonuç olarak verilebilir: titreme %38–87 azaldı, AUC değişmedi. Karar danışmanın.
- **Genel bandın bant yok koşulundan kötü olması:** Özellikle YENI'de. YENI, M33 ve M39_F2 dinlenmeye göre ölçülmüyor; kişinin vücut yapısını (kulak–omuz mesafesi) içeriyor. Genel bant bu anatomik farkı "hata" sayıyor. Dinlenmeye göre ölçülen M01'de de genel bant kişiye özelden çok kötü (v2: 0.700'e karşı 0.858). Bu yüzden sorun yalnızca anatomi değil, hareket biçimi de kişiden kişiye değişiyor. Sunumda "neden kişiye özel kalibrasyon?" sorusunun cevabı bu deney.
- **Ara bir yol (denenmedi, kapsam dışı):** Genel bandı kişinin kendi dinlenme duruşuna göre kaydırmak, yani "kalibrasyonsuz ama dinlenme ayarlı" bir bant. Uygulamada kalibrasyon zaten yapılacağı için gerekli görmüyorum; danışman isterse Adım 4'ten sonra eklenebilir.
- **Profil görüşte açı bandının kapsam sorunu:** Vasil cam1 o90 t9 (doğru), bazı One Euro ayarlarında kapsam 0 olduğu için değerlendirilemedi. Karar 6'daki "profil sınırlılık" bulgusuyla tutarlı.
