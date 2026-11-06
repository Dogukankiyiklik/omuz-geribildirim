# ADIM 02c — Deney 1 v2: yöntem düzeltmeleri (ablasyon)

**Tarih:** 2026-11-06
**Durum:** Tamamlandı. Kullanıcı deneyi çalıştırdı ve Petra videolarını v1 ile v2'de izledi. Kullanıcı sonuç tablolarını henüz kendisi yorumlayamadığını belirtti; danışmandan sade bir yorum isteniyor (aşağıda).

## Basit anlatım (kullanıcı için, 3–6 cümle)
Adım 2b'de iki sorun bulmuştun. (1) Petra kolunu az kaldırınca sistem onun omzunu "kol 170°'deyken normal olan" omuzla karşılaştırıyordu, bu yüzden bariz silkmeyi kaçırıyordu. (2) Tekrarın sonundaki pay kareleri yanlış alarm üretiyordu. Bu adımda üç düzeltme yaptık ve her birinin etkisini ayrı ayrı ölçtük. Buna **ablasyon** denir: düzeltmeleri teker teker ekleyip her birinin ne kazandırdığına bakmak. En önemli yenilik **açı bandı**. Zaman yerine kol açısına göre bir "normal aralık" kuruyoruz: "Kol 90°'deyken bu kişinin omzu normalde nerede?" Böylece kol ne kadar kalkarsa kalksın, omuz hep aynı kol açısındaki normal haliyle karşılaştırılıyor. Bu, M39'un zaman bandından ayrışan, projeye özgü bir katkı.

## Yapılanlar
- `ilerleme/GUNCELLEME_02.md` kararları `KARARLAR.md`'ye işlendi: 4 "AÇIK" satırı kapatıldı, 7 yeni karar satırı eklendi.
- `PLAN.md` güncellendi: Adım 2c eklendi. Adım 3 ve 4'e Güncelleme 02 notları eklendi. Yeni **Adım 4b** (Ex7'de ayarsız doğrulama) eklendi. Adım 11, 4b'ye taşındı.
- **Pay hariç (Karar 3):** `Tekrar` artık etiketli tekrarın sınırlarını biliyor (`etiketli` dilimi = `first_frame … last_frame`). Ölçütler tüm dizide hesaplanıyor, çünkü dinlenme tabanı pay dahil ilk 8 kare. DTW, bant ve E ise yalnızca etiketli karelerde.
- **Çoklu referans (Karar 1):** `cekirdek/bant.py` içine `bant_modeli_ref` (referansı dışarıdan verilen bant) ve `coklu_referans_hatasi` (her doğru tekrar sırayla referans, E'lerin ortalaması) eklendi. Eski `bant_modeli` aynı rastgele sayı sırasıyla çalışıyor; Deney 1 regresyonu değişmedi.
- **Açı bandı (Karar 2):** `cekirdek/aci_bandi.py`, Güncelleme 02'deki tanımın birebir uygulaması (ayrıntılar aşağıda, "Kararlar ve sapmalar").
- **Deney:** `deneyler/deney1_v2.py`. Dört koşul (v1, v1a, v1b, v2), ablasyon tablosu, kişi bazlı AUC, bootstrap farkları, v2 kapsam tablosu ve tohum duyarlılığı.
  - v1 koşulu Deney 1'i **birebir** yeniden üretiyor: 1668 tekrarın hepsinde 5 ölçütte fark 0,0 (`test_v1_deney1_ile_ayni`).
- **Şekiller:** `deneyler/deney1_v2_sekiller.py`.
  - `auc.png`: koşullara göre YENI AUC'si. Çubuk tüm veriyi, noktalar kişileri gösteriyor (Karar 5).
  - `ornekler/`: üç tekrar için v1 ve v2 yan yana. Sağ panelde "kol 90°'deyken bu kişinin omzu normalde ..." işareti var (sunum adayı).
- **Görsel kontrol aracı:** `--bant aci` seçeneği eklendi. Sağ üstte x ekseni kol açısı, y ekseni ölçüt; kalkış mavi, iniş turuncu, bant ve tekrarın noktaları, hareketli imleç var. Turkuaz referans iskelet bu görünümde aynı fazda **en yakın kol açısındaki** kalibrasyon karesi. Yani "kol bu açıdayken senin normal duruşun".

## Değişen / eklenen dosyalar
| Dosya | Ne işe yarıyor |
| --- | --- |
| `cekirdek/aci_bandi.py` | Açı bandı: `fazlar`, `kutular`, `aci_bandi_modeli`, `aci_bandi_hatasi`, `aci_eslemesi`, `tepe_acisi` |
| `cekirdek/bant.py` | `bant_modeli_ref`, `coklu_referans_hatasi` eklendi (eski davranış aynı) |
| `cekirdek/veri.py` | `Tekrar.etiket_bas`, `Tekrar.etiket_son`, `Tekrar.etiketli` |
| `cekirdek/bindirme.py` | `Bindirici(..., esleme=)`: DTW yerine dışarıdan kare eşlemesi |
| `deneyler/deney1_v2.py` | Ablasyon deneyi |
| `deneyler/deney1_v2_sekiller.py` | `auc.png` ve üç örnek şekil |
| `araclar/gorsel_kontrol.py` | `--bant aci` (`AciBandiGorseli`); kare çizimi kancalara bölündü (v1 çıktısı aynı) |
| `testler/test_aci_bandi.py` | 12 test (açı bandı, çoklu referans, v1 = Deney 1, etiketli kareler) |
| `PLAN.md`, `ilerleme/KARARLAR.md` | Güncelleme 02 işlendi |

## Nasıl çalıştırılır
```bash
python -m deneyler.deney1_v2                       # ~1 dk: 4 koşul + tohum 1 + bootstrap 2000 + şekiller
python -m araclar.gorsel_kontrol --video ex1_Petra --kamera cam1 --yonelim 0 --tekrar 5              # v1 (zaman bandı)
python -m araclar.gorsel_kontrol --video ex1_Petra --kamera cam1 --yonelim 0 --tekrar 5 --bant aci   # v2 (açı bandı)
```
Çıktılar:
- `sonuclar/deney1_v2/`: `tekrarlar.csv`, `ozet.csv`, `kisi_auc.csv`, `bootstrap.csv`, `kapsam.csv`, `tohum.csv`, `auc.png`, `ornekler/*.png`
- `sonuclar/gorsel_kontrol/*_aci.mp4`

## Sonuçlar
Kullanıcının çalıştırması (`python -m deneyler.deney1_v2`, tohum 0, bootstrap 2000, 6 Kasım 21:54). Sayılar `sonuclar/deney1_v2/*.csv` dosyalarından birebir kopyalandı. Tekrar sayıları (3 kamera dahil): silkme = 165, doğru = 834, diğer hatalar = 669. Hiçbir koşulda E'si boş (NaN) tekrar yok.

### 1. Ablasyon tablosu (AUC; tamamı `ozet.csv`)
| koşul | ölçüt | silkme/doğru | silkme/diğer | önden | çapraz | profil | kişi özeti | Ψ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v1 | YENI | 0.909 | 0.705 | 0.942 | 0.933 | 0.779 | 0,91 (0,80–0,98) | 0.330 |
| v1a | YENI | 0.927 | 0.720 | 0.948 | 0.945 | 0.834 | 0,93 (0,82–0,99) | 0.394 |
| v1b | YENI | 0.941 | 0.713 | 0.949 | 0.961 | 0.862 | 0,94 (0,85–0,99) | 0.393 |
| v2 | YENI | 0.935 | 0.812 | 0.973 | 0.957 | 0.802 | 0,94 (0,82–0,98) | 0.425 |
| v1 | M33 | 0.904 | 0.646 | 0.918 | 0.914 | 0.849 | 0,90 (0,74–0,99) | 0.300 |
| v1b | M33 | 0.924 | 0.650 | 0.936 | 0.930 | 0.889 | 0,92 (0,79–0,99) | 0.357 |
| v2 | M33 | 0.914 | 0.746 | 0.967 | 0.935 | 0.745 | 0,91 (0,81–0,97) | 0.376 |
| v1 | M39_F2 | 0.888 | 0.637 | 0.888 | 0.924 | 0.794 | 0,89 (0,73–0,99) | 0.281 |
| v1b | M39_F2 | 0.905 | 0.643 | 0.901 | 0.925 | 0.850 | 0,90 (0,78–0,98) | 0.330 |
| v2 | M39_F2 | 0.883 | 0.700 | 0.929 | 0.915 | 0.698 | 0,88 (0,80–0,96) | 0.332 |
| v1 | M01_tek | 0.866 | 0.662 | 0.898 | 0.889 | 0.743 | 0,86 (0,79–0,96) | 0.275 |
| v1b | M01_tek | 0.891 | 0.672 | 0.898 | 0.909 | 0.827 | 0,89 (0,81–0,97) | 0.320 |
| v2 | M01_tek | 0.870 | 0.783 | 0.903 | 0.907 | 0.709 | 0,87 (0,75–0,97) | 0.330 |
| v1 | M01 | 0.822 | 0.642 | 0.885 | 0.830 | 0.670 | 0,82 (0,75–0,94) | 0.221 |
| v1b | M01 | 0.839 | 0.638 | 0.875 | 0.852 | 0.717 | 0,84 (0,79–0,93) | 0.250 |
| v2 | M01 | 0.845 | 0.754 | 0.893 | 0.880 | 0.643 | 0,84 (0,78–0,93) | 0.262 |

("kişi özeti" = 5 kişinin silkme/doğru AUC'si, ortalama (en düşük–en yüksek). v1a satırları `ozet.csv`'de.)

### 2. Kişi bazlı AUC silkme/doğru (YENI; tüm ölçütler `kisi_auc.csv`)
| koşul | Honza | Mima | Petra | Terka | Vasil |
| --- | --- | --- | --- | --- | --- |
| v1 | 0.985 | 0.947 | 0.884 | 0.926 | 0.800 |
| v1a | 0.987 | 0.972 | 0.908 | 0.956 | 0.817 |
| v1b | 0.988 | 0.974 | 0.924 | 0.969 | 0.852 |
| v2 | 0.976 | 0.953 | 0.960 | 0.967 | 0.821 |

### 3. AUC farkları (YENI, silkme/doğru), kişi bazlı bootstrap, 2000 tekrar (`bootstrap.csv`)
| fark | nokta tahmini | %95 GA |
| --- | --- | --- |
| v2 − v1 | +0.025852 | −0.000337 – +0.055158 |
| v1a − v1 (pay hariç) | +0.017913 | +0.006914 – +0.027639 |
| v1b − v1a (çoklu referans) | +0.013593 | +0.003924 – +0.024958 |
| v2 − v1b (açı bandı) | −0.005654 | −0.023485 – +0.014208 |

### 4. v2 kapsam ve aralık dışı oranı (`kapsam.csv`)
| hata | tekrar | kapsam ort. | kapsam medyan | aralik_disi oranı |
| --- | --- | --- | --- | --- |
| DOGRU | 834 | 0.937 | 0.981 | 0.001 |
| ERR_ARM_FORWARD | 168 | 0.837 | 0.963 | 0.196 |
| ERR_BENT_ARM | 168 | 0.937 | 1.000 | 0.030 |
| ERR_ELEVATED_SHOULDER | 165 | 0.910 | 1.000 | 0.061 |
| ERR_HEAD_TO_SIDE | 168 | 0.895 | 1.000 | 0.077 |
| ERR_LOW_ABDUCTION | 165 | 0.971 | 1.000 | 0.012 |
| HEPSİ | 1668 | 0.923 | 1.000 | 0.038 |

### 5. Tohum duyarlılığı (YENI; tohum 0 ile 1 arasında aynı tekrarın |ΔE|'si, `tohum.csv`)
| koşul | grup | n | medyan |ΔE| | |ΔE| > 0,05 oranı | en büyük |ΔE| |
| --- | --- | --- | --- | --- | --- |
| v1 | doğru | 834 | 0.0062 | 0.1295 | 0.5462 |
| v1 | hatalı | 834 | 0.0372 | 0.4041 | 0.7083 |
| v1b | doğru | 834 | 0.0000 | 0.0000 | 0.0000 |
| v1b | hatalı | 834 | 0.0252 | 0.3405 | 0.3557 |
| v2 | doğru | 834 | 0.0000 | 0.0000 | 0.0000 |
| v2 | hatalı | 834 | 0.0269 | 0.3321 | 0.8903 |

### 6. Örnek görseller (`sonuclar/deney1_v2/ornekler/`)
E (YENI), `tekrarlar.csv`'den:

| Tekrar | Gerçek etiket | v1 | v1a | v1b | v2 | v2 kapsam | v2 tepe açısı |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Petra cam1 o0 t5 | omuz silkme | 0.175986 | 0.230199 | 0.205257 | 0.583999 | 1.0 | 113.4° |
| Honza cam1 o0 t5 | omuz silkme | 0.646400 | 0.652891 | 0.671168 | 0.781882 | 1.0 | 148.9° |
| Terka cam1 o20 t10 | doğru | 0.352687 | 0.228859 | 0.250407 | 0.197376 | 1.0 | 173.5° |

- **Petra:** Pay ve çoklu referans düzeltmesi E'yi pek değiştirmiyor (0.18–0.23). Yalnızca açı bandı silkmeyi ortaya çıkarıyor (0.584). v1 referansının kol tepesi 170°, bu tekrarınki 113°.
- **Terka:** Yanlış alarmı asıl düzelten **pay hariç** (0.353 → 0.229). Kalan hata, kolun son inişindeki (0–45°, indirme) karelerden geliyor; bu kareler etiketli tekrarın içinde.
- **Honza:** Bariz silkme, her koşulda yüksek E.

### Ne çıktı? (özet)
- **Pay hariç** (v1a − v1) ve **çoklu referans** (v1b − v1a) ayrı ayrı küçük ama güven aralığı sıfırı içermeyen kazançlar veriyor: +0.018 ve +0.014.
- **Açı bandı**, silkme/doğru ayrımında zaman bandından (v1b) farklı değil: −0.006, GA sıfırı içeriyor. Toplam v2 − v1 = +0.026; GA'nın alt ucu −0.0003, yani sınırda.
- **Açı bandının asıl kazancı silkmeyi diğer hatalardan ayırmakta:** YENI 0.713 (v1b) → 0.812 (v2). Bu iyileşme 5 ölçütün hepsinde görülüyor (M01 0.638 → 0.754, M33 0.650 → 0.746). Bu fark için bootstrap hesaplanmadı.
- **Kişiler:** v2'de Petra 0.924 → 0.960 (beklenen yönde). Honza, Mima ve Vasil v1b'ye göre biraz düşüyor (0.988 → 0.976, 0.974 → 0.953, 0.852 → 0.821).
- **Görüş:** v2 önden en iyi (YENI 0.973). Profilde ise v1b'den **kötü**: YENI 0.862 → 0.802, M39_F2 0.850 → 0.698.
- **Tohum:** v1b ve v2'de doğru tekrarların E'si tohumdan tamamen bağımsız (0 değişim). Hatalı tekrarlarda "atla" rastgeleliği yüzünden değişim sürüyor. v2'de en büyük değişim (0.890), v1b'dekinden (0.356) büyük.

## Kabul ölçütü kontrolü
- [x] Ablasyon tablosu (kullanıcının çalıştırması, `ozet.csv`)
- [x] Kişi tablosu (`kisi_auc.csv`)
- [x] Tohum duyarlılığı (`tohum.csv`)
- [x] Üç örnek görsel (`ornekler/`) ve üç açı bandı videosu (`sonuclar/gorsel_kontrol/*_aci.mp4`)
- [x] Kullanıcı Petra örneğini v1 ve v2'de izledi; yorumu aşağıda
- [x] Testler: `38 passed`

## Kullanıcı gözlemleri
Petra cam1 o0 t5, v1 (`ex1_Petra_cam1_o0_t5_YENI.mp4`) ve v2 (`..._YENI_aci.mp4`) videoları. Kullanıcının sözleri:

> "Videolardaki özellikler eskiye göre daha iyi duruyor."

Kullanıcı ayrıca şunu belirtti: Sonuç tablolarını (ablasyon, bootstrap, tohum) tam yorumlayıp anlamlandıramadı ve `auc.png` ile örnek şekillere henüz bakmadı. Claude Code tabloları sohbette YENI üzerinden adım adım anlattı, ama kullanıcı **danışmanın da sonuçları sade bir dille açıklamasını** istiyor. Danışmana `auc.png` ve üç örnek şekil de gönderiliyor.

## Kararlar ve sapmalar
Güncelleme 02'nin bırakmadığı ayrıntılarda verilen kararlar. Hepsi kod yazılırken, sonuçlara bakılmadan verildi:
- **Kutulama ham kol açısıyla, faz yumuşatılmış açıyla yapılıyor.** Tepe karesi 5 karelik medyanla bulunur, tepe karesi "kaldırma"ya dahildir. Her kare kendi ölçülen (ham) kol açısının kutusuna düşer.
- **τ alt sınırı (Q1)** her ölçüt için **iki fazın geçerli kutuları birlikte** alınarak hesaplanır, ardından ara değer uygulanır. M39'da tek bir zaman ekseni var; burada en yakın karşılığı iki fazın birleşimi.
- **"Kalibrasyonun en yüksek açısı"** = kalibrasyon tekrarlarının yumuşatılmış tepe açılarının en büyüğü. `aralik_disi` ise karelerin ham kol açısıyla hesaplanır.
- **Geçerli karesi olmayan tekrar** (kapsam 0) için E = NaN olur ve AUC'den çıkarılır; sayısı `ozet.csv`'deki "E boş (NaN) tekrar" sütununda raporlanır.
- **Kişi AUC'si NaN olursa** (kişide silkme yoksa) ortalamaya girmez. Ex1'de beş kişinin hepsinde silkme var.
- **Tohum duyarlılığı:** Aynı tekrarın tohum 0 ve tohum 1'deki E'si karşılaştırılır. "Doğru", "hatalı" ve "hepsi" ayrı raporlanır. Çoklu referans (v1b) ve açı bandı (v2) **referans** rastgeleliğini kaldırır, ama hatalı tekrarlarda **adil model için hangi doğru tekrarın dışarıda bırakılacağı** (atla) hâlâ rastgele. Bu yüzden v1b ve v2'de doğru tekrarların E'si tohumdan bağımsızdır; hatalıların E'si değişebilir.
- **Açı bandı videosundaki referans iskelet yalnızca görseldir.** Modeldeki doğru tekrarlardan tepe açısı bu tekrara en yakın olan seçilir. Kareler aynı fazda en yakın kol açısına göre eşlenir. E hesabına girmez.
- **Görsel araçtaki geçici eşik:** v2 için de "diğer 4 kişinin doğru E'lerinin %90'ı" (Adım 2b ile aynı kural).

**Dürüstlük notu:** Bu düzeltmeler (pay hariç, çoklu referans, açı bandı) aynı veriye bakılarak bulundu. Bu yüzden v1→v2 kazancı **iyimser** olabilir. Doğrulama:
- son yöntem Ex7'de **hiç ayar yapılmadan** çalıştırılacak (Adım 4b);
- kendi kayıtlarımızda denenecek (Adım 7).

v2'nin parametreleri (5° kutu, en az 3 tekrar, %20 bayrağı, 5° pay, 5 karelik medyan) önceden sabitlendi ve deneyde **değiştirilmedi**.

## Açık sorular / danışmana notlar
- **"Açı bandı belirgin şekilde kötü mü?"** (Güncelleme 02: kötüyse Adım 4'ten önce sor.)
  - Silkme/doğru ayrımında hayır: v2 − v1b = −0.006, GA −0.023 – +0.014.
  - Silkme/diğer ayrımında belirgin şekilde iyi: 0.713 → 0.812.
  - **Profil görüşte ise kötü:** YENI 0.862 → 0.802, M39_F2 0.850 → 0.698, M01_tek 0.827 → 0.709. Olası açıklama (test edilmedi): profilde yana kaldırma kameraya doğru/kameradan uzağa bir hareket. 2B kol açısı bu yüzden gerçek açıyı yansıtmıyor ve açıya göre kutulama güvenilmez oluyor. Zaman bandı açının değerine değil şekline baktığı için bundan daha az etkileniyor olabilir.
  - Karar danışmanın: Adım 4'te profil için zaman bandı mı, açı bandı mı, yoksa "açı bandı önden/çaprazda, profil sınırlılık olarak raporlanır" mı?
- **Silkme/diğer farkı için bootstrap GA yok.** En büyük kazanç orada olduğu için `bootstrap_tablosu`na eklenmesi önerilir; Adım 4'te zaten hata türü ayrımı ölçülecek.
- **Tohum duyarlılığı (Karar 1):** Referans rastgeleliği kalktı: doğru tekrarlarda v1b ve v2'de değişim 0. Hatalı tekrarlarda "atla" rastgeleliği sürüyor (|ΔE| > 0,05 oranı v1'de 0.404, v1b'de 0.341, v2'de 0.332). v2'de en büyük değişim 0.890. Muhtemel sebep: 4 kalibrasyon tekrarında "en az 3 tekrar" kuralı sınırda kalıyor; bir tekrarın çıkması bazı kutuları geçersiz yapıp bandın şeklini değiştiriyor (incelenmedi). Uygulamada (Adım 6) kalibrasyon 5 tekrar. Bu, kalibrasyon tekrar sayısının artırılması gerekip gerekmediği sorusunu doğuruyor.
- **`aralik_disi` bayrağı** kolu öne kaçan tekrarlarda %19.6, doğru tekrarlarda %0.1. Adım 4'te "öne kaçma" için bir girdi olabilir.
- **Terka'daki kalan hata:** Kolun son inişindeki kareler etiketli tekrarın içinde ve bandın altında kalıyor. Yöntemin bir sınırı mı, yoksa kişinin gerçek bir hareketi mi? Kullanıcının videoda bakması önerilir.
