# ADIM 04b — Ex7'de (omuz ekstansiyonu) ayarsız doğrulama

**Tarih:** 2026-11-07
**Durum:** Tamamlandı. Kullanıcı `python -m deneyler.ex7` komutunu çalıştırdı (7 Kas 00:25–00:27). Sayılar `sonuclar/ex7/` CSV dosyalarından birebir kopyalandı. "Önceden belirlenenler" bölümü sonuçlardan önce yazıldı ve `24ec9f0` commit'inde kayıtlı; o bölüm sonradan değiştirilmedi.

## Basit anlatım
**Soru:** Ex1'de (kolu yana kaldırma) geliştirdiğimiz yöntem, hiçbir ayarı değiştirmeden başka bir harekette (Ex7, kolu geriye götürme) çalışıyor mu?

**Cevap iki parçalı:**
1. **Omuz silkmesini bulma: evet, çalışıyor.** Çapraz + profil görüşte silkmeli ile doğru tekrarı ayırma başarısı (AUC) YENI ölçütüyle 0,939 (zaman bandı, v1b) ve 0,888 (açı bandı, v2). Ex1'deki 0,94–0,97 düzeyine yakın. AUC: rastgele bir silkmeli tekrarın rastgele bir doğru tekrardan daha yüksek puan alma olasılığı; 0,5 = yazı tura, 1 = kusursuz.
2. **Hata türünü bulma: zayıf.** Ana sistem (v2 yönlü) çapraz + profil görüşte makro-F1 0,399. 100 hatalı tekrarın yalnızca 32'sinde tür doğru. Ex1'de bu sayılar 0,568 ve 51 idi. Rastgele tahminde makro-F1 ≈ 0,17.

**Beklenmeyen iki bulgu (dürüstçe):**
- **Açı bandı Ex7'de zaman bandından iyi değil.** Silkme/doğru ayrımında v2 − v1b = −0,051 (GA −0,089 – −0,024). Ex1'deki açı bandı avantajı (silkme/diğer) da Ex7'de görülmüyor: +0,019, GA sıfırı içeriyor. Muhtemel sebep: Ex7'de kol çok az kalkıyor. Doğru tekrarlarda tepe kol açısının medyanı önden 14°, çaprazda 27°, profilde 49°. Bant az sayıda kutuya sıkışıyor ve hatalı tekrarlarda kol çoğu zaman kalibrasyon aralığının dışına çıkıyor; o kareler değerlendirilmiyor.
- **Yönlü bant Ex7'de belirgin şekilde kötü.** v2 yönlü − v2 yönsüz = −0,125 (GA −0,167 – −0,085). Ex1'de tersiydi (+0,056). Sebep büyük olasılıkla şu: gövde dönmesi ve kolun yana kaçması 2B'de **iki yönde de** görünebiliyor (kameraya göre). Eğitimden öğrenilen yön, kişiden kişiye değişiyor: `kol_boyu` 5 seçimin 2'sinde +1, 3'ünde −1. Yönlü bant "yanlış" taraftaki sapmayı sıfır sayıyor.
- En iyi Ex7 sistemi **v1b yönsüz**: makro-F1 0,566, 100 hatalının 50'sinde tür doğru.

## Sonuçlar

### 1. Deney 1 — silkme AUC (`d1_auc.csv`)
YENI ve M33. Silkme / doğru / diğer hatalı sayıları: çapraz+profil 100 / 506 / 404; tüm görüşler 165 / 834 / 666.

| koşul | ölçüt | görüş | AUC silkme/doğru | AUC silkme/diğer |
| --- | --- | --- | --- | --- |
| v1b | YENI | **çapraz+profil** | **0.939** | 0.712 |
| v1b | YENI | tüm görüşler | 0.945 | 0.748 |
| v1b | YENI | önden (0–20°) | 0.959 | 0.815 |
| v1b | YENI | çapraz (30–60°) | 0.959 | 0.763 |
| v1b | YENI | profil (70–90°) | 0.888 | 0.594 |
| v2 | YENI | **çapraz+profil** | **0.888** | 0.731 |
| v2 | YENI | tüm görüşler | 0.895 | 0.736 |
| v2 | YENI | önden (0–20°) | 0.901 | 0.741 |
| v2 | YENI | çapraz (30–60°) | 0.923 | 0.787 |
| v2 | YENI | profil (70–90°) | 0.821 | 0.604 |
| v1b | M33 | çapraz+profil | 0.930 | 0.724 |
| v2 | M33 | çapraz+profil | 0.894 | 0.725 |

Diğer ölçütler (M01, M01_tek, M39_F2) `d1_auc.csv` dosyasında. Çapraz+profil silkme/doğru en yüksek değer: v1b M33 0,930 ve YENI 0,939. v2'de boş (NaN) E: çapraz+profil 6, tüm görüşler 15 tekrar.

**Ex1 ile karşılaştırma** (`sonuclar/deney1_v2/ozet.csv`, Ex1 tüm görüşler / önden+çapraz):

| | Ex1 v1b YENI | Ex1 v2 YENI | Ex7 v1b YENI | Ex7 v2 YENI |
| --- | --- | --- | --- | --- |
| silkme/doğru, tüm görüşler | 0.940 | 0.947 | 0.945 | 0.895 |
| silkme/diğer, tüm görüşler | 0.721 | 0.829 | 0.748 | 0.736 |
| silkme/doğru, önden+çapraz | 0.955 | 0.968 | 0.959 | 0.915 |
| silkme/diğer, önden+çapraz | 0.752 | 0.862 | 0.785 | 0.770 |

### 2. Deney 1 — kişi bazlı AUC silkme/doğru, YENI (`d1_kisi_auc.csv`)
| koşul | görüş | Honza | Mima | Petra | Terka | Vasil |
| --- | --- | --- | --- | --- | --- | --- |
| v1b | çapraz+profil | 0.968 | 0.926 | 0.987 | 0.896 | 0.910 |
| v2 | çapraz+profil | 0.941 | 0.910 | 0.951 | 0.779 | 0.885 |
| v1b | tüm görüşler | 0.980 | 0.952 | 0.993 | 0.925 | 0.882 |
| v2 | tüm görüşler | 0.959 | 0.935 | 0.959 | 0.805 | 0.856 |

### 3. Deney 1 — kişi bazlı bootstrap %95 GA (`d1_auc_ga.csv`, `d1_farklar.csv`; 2000 tekrar)
| görüş | ayrım | ölçüt | v1b AUC (GA) | v2 AUC (GA) | v2 − v1b (GA) |
| --- | --- | --- | --- | --- | --- |
| çapraz+profil | silkme/doğru | YENI | 0.939 (0.910–0.967) | 0.888 (0.826–0.938) | **−0.051 (−0.089 – −0.024)** |
| çapraz+profil | silkme/doğru | M33 | 0.930 (0.909–0.955) | 0.894 (0.854–0.938) | −0.036 (−0.063 – −0.007) |
| çapraz+profil | silkme/diğer | YENI | 0.712 (0.650–0.782) | 0.731 (0.659–0.811) | +0.019 (−0.031 – +0.081) |
| çapraz+profil | silkme/diğer | M33 | 0.724 (0.643–0.803) | 0.725 (0.649–0.818) | +0.001 (−0.053 – +0.049) |
| tüm görüşler | silkme/doğru | YENI | 0.945 (0.911–0.979) | 0.895 (0.843–0.950) | −0.050 (−0.091 – −0.023) |
| tüm görüşler | silkme/diğer | YENI | 0.748 (0.685–0.822) | 0.736 (0.655–0.827) | −0.012 (−0.062 – +0.040) |

### 4. Deney 2 — özet (`d2_ozet.csv`)
Çapraz+profil: 1010 tekrar (504 hatalı). Tüm görüşler: 1665 (831 hatalı).

| sistem | görüş | makro-F1 katı | esnek | ikili doğruluk | hatalılarda tür doğru /100 | hatalılarda "doğru" dedi /100 | doğrulara "doğru" deme |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **v2 yönlü** | **çapraz+profil** | **0.399** | 0.418 | 0.765 | **32.34** | 30.36 | 0.834 |
| v2 yönlü | tüm görüşler | 0.395 | 0.411 | 0.768 | 32.37 | 28.16 | 0.817 |
| v2 yönlü | önden (0–20°) | 0.379 | 0.391 | 0.753 | 31.77 | 26.72 | 0.773 |
| v2 yönlü | çapraz (30–60°) | 0.421 | 0.438 | 0.782 | 35.98 | 26.06 | 0.824 |
| v2 yönlü | profil (70–90°) | 0.340 | 0.363 | 0.756 | 23.84 | 36.42 | 0.875 |
| v2 yönsüz | çapraz+profil | 0.524 | 0.541 | 0.780 | 46.23 | 25.20 | 0.812 |
| v1b yönlü | çapraz+profil | 0.380 | 0.396 | 0.820 | 31.55 | 19.64 | 0.836 |
| v1b yönsüz | çapraz+profil | **0.566** | 0.581 | 0.845 | **49.60** | 17.66 | 0.866 |
| v1b yönsüz | tüm görüşler | 0.531 | 0.545 | 0.843 | 45.73 | 18.29 | 0.868 |

**Temel çizgi** (tek toplam hata, doğru/yanlış), v2 yönlü, çapraz+profil: ikili doğruluk 0.779. Aynı veride 6 sınıflı kural 0.765.

### 5. Deney 2 — kişi bazlı bootstrap (`d2_bootstrap.csv`)
| görüş | büyüklük | nokta | %95 GA |
| --- | --- | --- | --- |
| çapraz+profil | makro-F1 v2 yönlü | 0.3986 | 0.3725 – 0.4202 |
| çapraz+profil | makro-F1 v1b yönsüz | 0.5657 | 0.5195 – 0.6203 |
| çapraz+profil | v2 yönlü − v1b yönlü | +0.0190 | −0.0060 – +0.0595 |
| çapraz+profil | v2 yönlü − v2 yönsüz | **−0.1251** | −0.1669 – −0.0851 |
| çapraz+profil | v2 yönsüz − v1b yönsüz | −0.0421 | −0.0635 – −0.0163 |
| tüm görüşler | v2 yönlü − v2 yönsüz | −0.0797 | −0.1278 – −0.0277 |
| tüm görüşler | v2 yönsüz − v1b yönsüz | −0.0557 | −0.0756 – −0.0439 |

### 6. Sınıf başına, çapraz+profil, katı (`d2_siniflar.csv`)
| sınıf | destek | v2 yönlü duy. / kes. / F1 | v2 yönsüz F1 | v1b yönsüz F1 |
| --- | --- | --- | --- | --- |
| doğru | 506 | 0.834 / 0.734 / 0.781 | 0.787 | 0.848 |
| omuz | 100 | 0.720 / 0.319 / 0.442 | 0.518 | 0.493 |
| gövde öne | 100 | 0.230 / 0.274 / 0.250 | 0.489 | 0.495 |
| gövde dönme | 100 | 0.280 / 0.491 / 0.357 | 0.471 | 0.566 |
| dirsek | 102 | 0.304 / 0.660 / 0.416 | 0.530 | 0.537 |
| kol yana | 102 | 0.088 / 0.429 / 0.146 | 0.346 | 0.456 |

**Karışıklık, v2 yönlü, çapraz+profil** (`d2_karisiklik_v2_yonlu_cp.csv`):

| gerçek \ karar | doğru | omuz | gövde öne | gövde dönme | dirsek | kol yana |
| --- | --- | --- | --- | --- | --- | --- |
| doğru | **422** | 29 | 29 | 15 | 5 | 6 |
| omuz | 16 | **72** | 2 | 2 | 5 | 3 |
| gövde öne | 28 | 44 | **23** | 3 | 0 | 2 |
| gövde dönme | 28 | 28 | 16 | **28** | 0 | 0 |
| dirsek | 22 | 37 | 7 | 4 | **31** | 1 |
| kol yana | 59 | 16 | 7 | 5 | 6 | **9** |

- Ex7'de "çekici" sınıf **omuz**. Diğer hatalı tekrarlara 125 kez yanlışlıkla "omuz" deniyor: gövde öne 44, dirsek 37, gövde dönme 28, kol yana 16. Kesinlik bu yüzden 0,319.
- **Kol yana kaçma** çoğunlukla kaçırılıyor: 102 tekrarın 59'una "doğru" deniyor.

### 7. İlk iki (`d2_ilk_iki.csv`, çapraz+profil)
| sistem | birincil = 1. z /100 | birincil ilk iki z içinde /100 | birincil söylenen ilk iki içinde /100 | doğrularda 2. z ≥ T /100 |
| --- | --- | --- | --- | --- |
| v2 yönlü | 38.10 | 61.31 | 42.66 | 1.98 |
| v2 yönsüz | 53.97 | 73.02 | 54.76 | 3.16 |
| v1b yönlü | 34.52 | 62.50 | 52.78 | 2.37 |
| v1b yönsüz | 53.57 | 75.60 | 63.49 | 1.58 |

### 8. Seçilen eşikler ve yönler (`d2_esikler.csv`; her satırda ayar diğer 4 kişide)
| sistem | Honza | Mima | Petra | Terka | Vasil |
| --- | --- | --- | --- | --- | --- |
| v2 yönlü T | 4.435 | 3.907 | 3.179 | 3.857 | 3.983 |
| v2 yönsüz T | 2.060 | 2.028 | 2.107 | 2.205 | 2.045 |
| v1b yönlü T | 4.495 | 4.039 | 4.264 | 4.132 | 3.974 |
| v1b yönsüz T | 2.219 | 2.774 | 2.509 | 2.678 | 2.766 |

Öğrenilen yönler:
- **Sabit olanlar:** YENI −1, govde_egim +1, dirsek −1. Beş seçimin beşinde ve dört sistemin hepsinde aynı.
- **Kararsız olanlar:**
  - `govde_donme`: v2'de 5 seçimin 4'ünde −1 (Petra testinde +1); v1b'de 4'ünde +1 (Terka testinde −1).
  - `kol_boyu`: v2'de 3 seçimde −1, 2 seçimde +1 (Mima ve Terka testlerinde); v1b'de 5'inde −1.

### 9. Kişi bazlı, çapraz+profil (`d2_kisi.csv`)
| sistem | Honza | Mima | Petra | Terka | Vasil |
| --- | --- | --- | --- | --- | --- |
| v2 yönlü makro-F1 | 0.435 | 0.355 | 0.385 | 0.410 | 0.385 |
| v2 yönlü tür doğru /100 | 37.0 | 26.9 | 32.0 | 31.0 | 35.0 |
| v2 yönlü hatalılarda "doğru" /100 | 24.0 | 26.9 | 35.0 | 49.0 | 17.0 |
| v1b yönsüz makro-F1 | 0.668 | 0.571 | 0.554 | 0.537 | 0.482 |

### 10. Açı bandı kapsamı (v2; `d2_kapsam.csv`; betimsel)
| görüş grubu | sınıf | tekrar | kapsam ort. | aralik_disi oranı | tepe kol açısı medyan |
| --- | --- | --- | --- | --- | --- |
| önden | doğru | 278 | 0.761 | 0.004 | 13.8° |
| önden | kol yana | 56 | 0.340 | 0.911 | 48.0° |
| çapraz | doğru | 404 | 0.862 | 0.000 | 26.6° |
| çapraz | gövde öne | 80 | 0.565 | 0.612 | 53.7° |
| çapraz | kol yana | 81 | 0.641 | 0.457 | 48.7° |
| profil | doğru | 152 | 0.923 | 0.007 | 48.6° |
| profil | gövde öne | 30 | 0.607 | 0.867 | 75.7° |

Diğer satırlar dosyada. Hatalı tekrarlarda kol, doğru tekrarlardan belirgin şekilde yüksek kalkıyor. Bu yüzden açı bandı karelerin önemli bir kısmını değerlendiremiyor; kapsam önden "kol yana" sınıfında %34'e kadar düşüyor.

### Ne çıktı?
- **Silkme tespiti başka harekete taşınıyor.** Ayarsız Ex7'de YENI ile AUC 0,89–0,94. Bu, Deney 1'in iyimserlik riskine karşı olumlu bir kanıt.
- **Açı bandının Ex1'deki üstünlüğü Ex7'de tekrarlanmadı.** Ex7'de v2, silkme/doğru ayrımında v1b'den kötü; silkme/diğer ayrımında fark yok. Açı bandı, kolun geniş bir açı aralığında gezdiği hareketler için tasarlandı. Ex7'de kol küçük bir aralıkta hareket ediyor ve hata yapınca bu aralığın dışına çıkıyor. Bu, açı bandının **ön koşulu** olarak sınırlılık bölümüne yazılmalı.
- **Hata türü bulma Ex7'de Ex1'den zayıf.** En iyi sistem (v1b yönsüz) bile makro-F1 0,566. Ana sistem 0,399.
- **Yönlü bandın yararı hareket ve görüşe bağlı.** Ex1'de yardım ediyordu; Ex7'de, iki yönde de görülebilen hatalar (dönme, kolun yana kaçması) yüzünden zarar veriyor.
- **Ex7 profil görüşü Ex1'deki kadar kötü değil** (v2 yönlü 0,340; v1b yönsüz 0,538). Ama önden + çapraz da iyi değil. "Ex7 için yan/çapraz daha iyi" beklentisi Deney 2'de yalnızca kısmen doğrulandı: çapraz 0,421, profil 0,340, önden 0,379.

## Kabul ölçütü kontrolü
- [x] Ex7 silkme/doğru AUC tablosu: görüş grubu (tablo 1) ve kişi bazlı (tablo 2), bootstrap GA (tablo 3)
- [x] Hiçbir Ex1 sabitinin değiştirilmediği yazıldı (yukarıda "Değişmeyen Ex1 sabitleri"); sınama çalıştırmasından sonra kodda parametre değişikliği yok, kullanıcı çalıştırmasıyla tablolar birebir aynı
- [x] Deney 2 kuralı Ex7 hata türleriyle; önceden yazılmış eşleme ve uygulama senaryosu
- [x] Testler: `55 passed`

## Kararlar ve sapmalar
- **Ex7 ayarı çapraz + profil üzerinde** (önceden yazıldığı gibi). Ex1 ise önden + çapraz üzerinde ayarlanmıştı. Bu nedenle Ex1 ile Ex7 sayıları farklı görüş kümelerinden; tablo 1'deki karşılaştırma aynı görüş kümelerinde (tüm, önden+çapraz) verildi.
- **Argmax eşitlik sırası** Güncelleme 05 tablosunun sırası: omuz, gövde öne, gövde dönme, dirsek, kol yana.
- **Ex7'de esnek değerlendirme:** Ek hata yalnızca 6 tekrarda var (hepsi `ERR_TORSO_FORWARD`).
- **Kod yeniden düzenlemesi:** `hata_turu` artık bir `HataTanimi` (EX1 / EX7) alıyor. Ex1 Deney 2 çıktılarının birebir aynı olduğu doğrulandı.
- **Hiçbir şey sonuçlara göre değiştirilmedi.** Yönlü bandın Ex7'deki zararı ve açı bandının Ex7'deki zayıflığı olduğu gibi raporlanıyor.

## Açık sorular / danışmana notlar
- **Karar 15 (ana sistem v2 yönlü) Ex7'de doğrulanmadı.** Ex7'de en iyi sistem v1b yönsüz (0,566). Ex1'de ise v2 yönlü ile v1b yönlü arasında fark yoktu. Raporda "yöntem başka harekette" iddiası yalnızca **silkme tespiti** için güçlü; hata türü için zayıf. Ana sistem seçimi değişmeli mi, yoksa bu bir sınırlılık olarak mı yazılmalı?
- **Açı bandının ön koşulu:** Kolun kalibrasyonda geniş bir açı aralığını taraması gerekiyor. Ex7 gibi küçük açılı hareketlerde zaman bandı daha güvenli olabilir. Bu bir gelecek çalışma / sınırlılık.
- **Ex1 az kaldırma kararı (ADIM_04 Ek) Ex7'yi etkilemiyor.** Ancak Ex7'deki yönlü/yönsüz bulgusu, Ex1 için yapılacak düzeltme seçimini etkileyebilir.
- **Ex7'de "omuz" çekici sınıf:** Gövde öne eğilince ve dirsek bükülünce kulak–omuz mesafesi de değişiyor olabilir (44 ve 37 yanlış "omuz" kararı). Ex1'deki "az kaldırma" çekiciliğinin benzeri.

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
