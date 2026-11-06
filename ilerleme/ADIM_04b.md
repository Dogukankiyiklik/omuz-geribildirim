# ADIM 04b — Ex7'de (omuz ekstansiyonu) ayarsız doğrulama

**Tarih:** 2026-11-07
**Durum:** Kod hazır; kullanıcının `python -m deneyler.ex7` çalıştırması bekleniyor. Bu bölüm sonuçlar görülmeden yazıldı ve commit'lendi (önceden kayıt).

## Önceden belirlenenler (sonuçlardan önce)
Kaynak: Güncelleme 05. Kod bu tanımlarla yazıldı; sınama çalıştırmasından sonra hiçbiri değiştirilmeyecek.

**Ölçüt–hata eşlemesi** (`cekirdek/hata_turu.EX7`):

| Ex7 hata kodu | ölçüt | tanım (`cekirdek/ozellikler.py`) |
| --- | --- | --- |
| `ERR_ELEVATED_SHOULDER` | `YENI` | (y sağ omuz − y sağ kulak) / gövde (Ex1 ile aynı) |
| `ERR_TORSO_FORWARD` | `govde_egim` | (kalça ortası → omuz ortası) vektörünün yukarı dikeyle açısı (°) |
| `ERR_TORSO_ROTATION` | `govde_donme` | omuz genişliği / kalça genişliği |
| `ERR_BENT_ARM` | `dirsek` | sağ omuz – sağ dirsek – sağ bilek açısı (Ex1 ile aynı) |
| `ERR_ARM_TO_SIDE` | `kol_boyu` | sağ omuz – sağ bilek mesafesi / dinlenme gövde boyu (Ex1 ile aynı) |

- Ex7'de "az kaldırma" sınıfı yok, tepe bandı (10° alt sınır) kullanılmıyor.
- Kol açısı tanımı Ex1 ile aynı: üst kolun aşağı dikeyle açısı. Ex7'de de sağ kol çalışıyor (`exercise_subtype = right`, 555 tekrarın 555'i).
- Argmax eşitliğinde öncelik sırası yukarıdaki tablonun sırası.

**Değişmeyen Ex1 sabitleri:** 5° kutu, kutu başına en az 3 tekrar, %20 "aralık dışı" bayrağı, pay hariç, Karar 7 adil model, z = (puan − medyan)/(IQR + 0,01), T ızgarası (max z'nin %0–100 yüzdelikleri, 0,5 adım), eşitlikte küçük T.

**Ex7 içinde, kişi bazlı birini-dışarıda-bırak ile seçilenler:** ölçekleme (medyan, IQR), yön (Ex1'deki gibi eğitim verisinden), T.

**Uygulama senaryosu:** çapraz + profil (|görüş| ≥ 30°). Gerekçe: ekstansiyon sagital düzlemde, önden zor görülür. Ayar yalnızca eğitim kişilerinin bu görüşlerdeki tekrarlarıyla yapılır. Sonuçlar ayrıca "tüm görüşler", "önden + çapraz" ve üç görüş grubu için verilir.

**Ana sistem:** v2 yönlü (Karar 15). v2 yönsüz, v1b yönlü/yönsüz karşılaştırma.

**Deney 1:** v1b ve v2, 5 omuz ölçütü, silkme/doğru ve silkme/diğer AUC; kişi bazlı AUC; YENI ve M33 için kişi bazlı bootstrap GA ve v2 − v1b farkları.

## Değişen / eklenen dosyalar
| Dosya | Ne işe yarıyor |
| --- | --- |
| `deneyler/ex7.py` (yeni) | Adım 4b: Ex7'de Deney 1 + Deney 2, tablolar |
| `cekirdek/hata_turu.py` | `HataTanimi`, `EX1`, `EX7`; kural egzersizden bağımsız (z sütunları eşlemeden). Ex1 davranışı aynı |
| `cekirdek/ozellikler.py` | `govde_egim`, `govde_donme`, `EX7_OLCUTLERI` |
| `cekirdek/etiketler.py` | Ex7 hata ve ölçüt adları |
| `deneyler/deney2.py` | `puan_tablosu`, `loso`, `ozet_satiri` ölçüt / tanım / ayar görüşü parametresi alıyor (Ex1 varsayılanları aynı) |
| `deneyler/tablolar.py` | `CAPRAZ_PROFIL` görüş maskesi (|görüş| ≥ 30°) |
| `testler/test_hata_turu.py` | Ex7 ölçütleri, eşlemeler, Ex7 kuralı yapay veride → `55 passed` |

**Ex1 regresyonu:** Yeniden düzenlemeden sonra `deney2` geçici klasörde yeniden çalıştırıldı. `puanlar`, `tahminler`, `esikler`, `ozet`, `ilk_iki`, `kaldirma`, `siniflar`, `kisi` tabloları `sonuclar/deney2/` ile birebir aynı.

## Nasıl çalıştırılır
```bash
python -m deneyler.ex7
```
Beklenen süre: birkaç dakika (bootstrap'sız ~50 s). Çıktı: `sonuclar/ex7/`.

## Sonuçlar
(Kullanıcı çalıştırdıktan sonra eklenecek.)
