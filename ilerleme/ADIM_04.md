# ADIM 04 — Deney 2: hata türünü bulma

**Tarih:** 2026-11-06
**Durum:** Tamamlandı. Kullanıcı `python -m deneyler.deney2` (23:31–23:33) ve `python -m deneyler.deney2_galeri` (23:33) komutlarını çalıştırdı. Sayılar `sonuclar/deney2/` altındaki CSV dosyalarından birebir kopyalandı. Kullanıcının galeri gözlemi ve incelemesi eklendi.

## Basit anlatım
**En önemli tek sonuç:** Ana sistem (açı bandı, yönlü), önden ve çapraz görüşte **100 hatalı tekrarın yaklaşık 57'sinde hatanın türünü doğru söylüyor** (56,6; ek hatalar da doğru sayılırsa 59,8). Yaklaşık 16'sına "doğru" diyor, yani hatayı kaçırıyor. Kalan yaklaşık 28'inde bir hata olduğunu fark ediyor ama türünü yanlış söylüyor.

**Bu ne demek?**
- **"Bir şey yanlış" demek kolay, "ne yanlış" demek zor.** Sistem doğru ile hatalı tekrarı 100 tekrarın yaklaşık 88'inde ayırabiliyor (ikili doğruluk 0,885). Tek bir toplam puan kullanan basit temel çizgi de aynı düzeyde (0,889). Yani zorluk hatayı fark etmekte değil, **türünü** bulmakta.
- **Doğru tekrarların çoğu "doğru" olarak tanınıyor.** 100 doğru tekrarın yaklaşık 92'sine "doğru" deniyor (0,925). Gereksiz uyarı az.
- **Sistem bir hata bulduğunda, türünü 3 tekrardan 2'sinde doğru söylüyor** (%67,0).
- **En büyük karışıklık:** Omzunu silken kişilerde kol da daha az kalkıyor. Sistem bu yüzden bu tekrarların bir kısmına "kolunu yeterince kaldırmadın" diyor (135 silkmeden 37'si). Etiket yalnızca **birincil** hatayı veriyor. Galeriyle bakılması gereken soru şu: Bu tekrarlarda kol gerçekten az mı kalkıyor?
- **Profil görüşte sistem çalışmıyor.** Profilde 100 hatanın yalnızca 16'sında tür doğru. Bu, Karar 6'da önceden öngörülen sınırlılıkla tutarlı.
- **Kişiler arasında fark büyük.** Honza'da 100 hatanın 77'sinde tür doğru; Vasil'de yalnızca 29'unda. Vasil'in hatalı tekrarlarının neredeyse yarısına (137'den 64'üne) sistem "doğru" diyor.

**Terimler:**
- **Makro-F1:** 6 sınıfın (doğru + 5 hata) her biri için "hem bulma hem isabet" puanlarının ortalaması. 1 = kusursuz. Rastgele tahminde yaklaşık 0,17 olur.
- **Katı:** Yalnızca birincil etiket doğru sayılır.
- **Esnek:** Etiketteki ek hatalardan birini söylemek de doğru sayılır.

## Yapılanlar
- **Yeni ölçütler** (`cekirdek/ozellikler.py`). Hepsi açı bandıyla değerlendiriliyor:
  - `bas`: baş eğikliği, M39 F3;
  - `on_kacma`: bilek–omuz–kalça açısı, M39 F1;
  - `kol_boyu`: omuz–bilek mesafesi / gövde;
  - `dirsek`: dirsek açısı, M39 F4.
  Omuz için YENI kullanılıyor.
- **Yetersiz kaldırma:** Bant kullanılmıyor. Ölçü d = (kalibrasyon tepelerinin medyanı − tekrarın tepe kol açısı) / max(IQR, 5°). Pozitif d, kolun normalden az kalktığı anlamına geliyor.
- **Karar kuralı** (`cekirdek/hata_turu.py`; deney ve uygulama aynı kodu kullanır):
  - z = (puan − eğitim doğrularının medyanı) / (IQR + 0,01);
  - max z < T ise "doğru"; değilse en büyük z'nin hatası.
- **Kişi bazlı birini-dışarıda-bırak:** Şunlar 4 kişide seçilip 5. kişide test edildi:
  - ölçekleme;
  - yön (yönlü bantta);
  - `on_kacma` mı `kol_boyu` mu;
  - eşik T.
  Seçim, eğitim kişilerinin önden + çapraz tekrarlarında makro-F1'e göre yapıldı.
- **Dört sistem aynı kodla değerlendirildi:** v2 (açı bandı) ve v1b (zaman bandı, çoklu referans), her biri yönsüz ve yönlü. v1b yalnızca karşılaştırma temel çizgisi (Karar 6).
- **Adillik (Karar 7):**
  - doğru tekrar, kendisi dışarıda bırakılan modelle değerlendirildi;
  - hatalı tekrar, n adet (n−1)'li modelin ortalamasıyla değerlendirildi.
  Grup başına n model bir kez kuruluyor.
- **Kontrol:** Yeni puan kodunun YENI yönsüz E'si, Deney 1 v2'nin `tekrarlar.csv` dosyasıyla v2'de de v1b'de de birebir aynı çıktı (en büyük fark 0,0; Honza + Petra üzerinde denendi).
- **Temel çizgi:** Tek toplam hata (z'lerin ortalaması) ile yalnızca doğru/yanlış ayrımı. Eşiği eğitimde dengeli doğruluğa göre seçildi.
- **Adım 5 hazırlığı (Güncelleme 04, not 1):** `aci_bandi_hatasi(..., ayrinti=True)` artık kare başına şunları da veriyor:
  - `kol`: kol açısı;
  - `deger`: ölçütün ham değeri;
  - `fark`: h − μ;
  - `bant_disi`: imzalı bant dışı büyüklük.
  Önceden olan `faz` ve `mu` alanları duruyor. E değişmedi; regresyon testleri geçiyor.
- **Galeri** (`deneyler/deney2_galeri.py`): Videonun sağ üstünde kararı veren ölçütün açı bandı görünüyor. Kaldırma kararında kol açısı zamana göre ve kalibrasyon tepeleri çiziliyor.
- **Testler:** `testler/test_hata_turu.py` eklendi (8 test) → `50 passed`.

## Değişen / eklenen dosyalar
| Dosya | Ne işe yarıyor |
| --- | --- |
| `cekirdek/hata_turu.py` (yeni) | Hata–ölçüt eşlemesi, kaldırma sapması, yön, z ölçekleme, karar, T seçimi, temel çizgi, esnek etiket |
| `deneyler/deney2.py` (yeni) | Deney 2: puanlar, birini-dışarıda-bırak, tablolar, karışıklık şekilleri |
| `deneyler/deney2_galeri.py` (yeni) | Galeri videoları ve `liste.md` |
| `testler/test_hata_turu.py` (yeni) | Yeni ölçütler, tek geçişli puanların eski hesapla aynılığı, karar kuralı, metrikler |
| `cekirdek/ozellikler.py` | `bas`, `on_kacma`, `kol_boyu`, `dirsek`; `DENEY2_OLCUTLERI` |
| `cekirdek/aci_bandi.py` | Ayrıntı çıktısına `kol`, `deger`, `fark`, `bant_disi`; `aci_bandi_puanlari` |
| `cekirdek/bant.py` | `coklu_model_puanlari` (tek hizalamayla üç yön) |
| `cekirdek/degerlendirme.py` | Karışıklık matrisi, sınıf metrikleri, makro-F1 |
| `cekirdek/bindirme.py`, `cekirdek/etiketler.py` | Yeni ölçütlerin uzuvları ve Türkçe adları |
| `araclar/gorsel_kontrol.py` | Açı bandı görseli ölçüt listesi ve yön alabiliyor (varsayılan davranış aynı) |

## Nasıl çalıştırılır
```bash
python -m deneyler.deney2          # ~1 dk   → sonuclar/deney2/
python -m deneyler.deney2_galeri   # ~1 dk   → sonuclar/deney2/galeri/
```

## Sonuçlar

### 1. Özet (`ozet.csv`)
"ö+ç" = önden + çapraz (|görüş| ≤ 60°), "tüm" = tüm görüşler. Katı = yalnızca birincil hata.

| sistem | görüş | makro-F1 katı | makro-F1 esnek | doğruluk 6 sınıf (katı) | hatalılarda tür doğru /100 (katı) | (esnek) | hatalılarda "doğru" dedi /100 | yakalanan hatalılarda tür doğru % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **v2 yönlü** | ö+ç | **0.6311** | 0.6624 | 0.7454 | **56.60** | 59.82 | 15.54 | 67.01 |
| v2 yönlü | tüm | 0.5806 | 0.6083 | 0.7098 | 49.28 | 52.04 | 23.50 | 64.42 |
| v2 yönlü | profil | 0.2963 | 0.3031 | 0.5508 | 16.45 | 17.11 | 59.21 | 40.32 |
| v2 yönsüz | ö+ç | 0.6270 | 0.6462 | 0.7395 | 58.06 | 59.97 | 11.00 | 65.24 |
| v2 yönsüz | tüm | 0.5762 | 0.5947 | 0.7068 | 50.84 | 52.64 | 16.07 | 60.57 |
| v1b yönlü | ö+ç | 0.6266 | 0.6597 | 0.7417 | 57.33 | 61.29 | 12.17 | 65.28 |
| v1b yönlü | tüm | 0.5754 | 0.6074 | 0.7080 | 50.60 | 54.44 | 17.15 | 61.07 |
| v1b yönsüz | ö+ç | 0.6059 | 0.6226 | 0.7351 | 57.18 | 58.80 | 6.74 | 61.32 |
| v1b yönsüz | tüm | 0.5565 | 0.5727 | 0.7020 | 50.48 | 52.04 | 10.67 | 56.51 |

Tekrar sayıları: ö+ç 1363 (682 hatalı), tüm 1668 (834 hatalı), profil 305 (152 hatalı).

### 2. Temel çizgi ile 6 sınıflı kural (`temel_cizgi.csv`)
| sistem | görüş | yöntem | ikili doğruluk | hatalıyı yakalama | doğruya doğru deme | tür doğru /100 | makro-F1 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| v2 yönlü | ö+ç | temel çizgi (tek toplam hata) | 0.8892 | 0.8680 | 0.9104 | — | — |
| v2 yönlü | ö+ç | 6 sınıflı kural | 0.8848 | 0.8446 | 0.9251 | 56.60 | 0.6311 |
| v2 yönlü | tüm | temel çizgi | 0.8579 | 0.7998 | 0.9161 | — | — |
| v2 yönlü | tüm | 6 sınıflı kural | 0.8459 | 0.7650 | 0.9269 | 49.28 | 0.5806 |
| v2 yönsüz | ö+ç | temel çizgi | 0.9068 | 0.8959 | 0.9178 | — | — |
| v2 yönsüz | ö+ç | 6 sınıflı kural | 0.8944 | 0.8900 | 0.8987 | 58.06 | 0.6270 |
| v1b yönlü | ö+ç | temel çizgi | 0.8936 | 0.8592 | 0.9280 | — | — |
| v1b yönlü | ö+ç | 6 sınıflı kural | 0.8944 | 0.8783 | 0.9104 | 57.33 | 0.6266 |
| v1b yönsüz | ö+ç | temel çizgi | 0.9288 | 0.9326 | 0.9251 | — | — |
| v1b yönsüz | ö+ç | 6 sınıflı kural | 0.9156 | 0.9326 | 0.8987 | 57.18 | 0.6059 |

Tüm görüşler ve profil satırları `temel_cizgi.csv` dosyasında. Bütün sistemlerde temel çizgi ile kuralın ikili doğruluğu birbirine yakın (fark ≤ 0,013). Doğru/yanlış ayrımında en yüksek değer v1b yönsüz temel çizgide: 0,9288 (ö+ç).

### 3. Sınıf başına, v2 yönlü, önden + çapraz, katı (`siniflar.csv`)
| sınıf | destek | duyarlılık | kesinlik | F1 |
| --- | --- | --- | --- | --- |
| doğru | 681 | 0.925 | 0.856 | 0.889 |
| omuz | 135 | 0.415 | 0.544 | 0.471 |
| baş | 138 | 0.514 | 0.740 | 0.607 |
| öne kaçma | 137 | 0.401 | 0.529 | 0.456 |
| dirsek | 137 | 0.562 | 0.828 | 0.670 |
| az kaldırma | 135 | 0.941 | 0.550 | 0.694 |

### 4. Karışıklık matrisi, v2 yönlü, önden + çapraz, katı (`karisiklik_v2_yonlu_oc_kati.csv`, `.png`)
| gerçek \ karar | doğru | omuz | baş | öne kaçma | dirsek | az kaldırma |
| --- | --- | --- | --- | --- | --- | --- |
| doğru | **630** | 6 | 12 | 10 | 7 | 16 |
| omuz | 20 | **56** | 12 | 10 | 0 | 37 |
| baş | 25 | 20 | **71** | 5 | 1 | 16 |
| öne kaçma | 48 | 2 | 1 | **55** | 8 | 23 |
| dirsek | 9 | 16 | 0 | 23 | **77** | 12 |
| az kaldırma | 4 | 3 | 0 | 1 | 0 | **127** |

Esnek matriste (`..._oc_esnek.csv`) omuz köşegeni 56'dan 70'e, baş köşegeni 71'den 78'e, dirsek köşegeni 77'den 78'e çıkıyor. Bunun sebebi, bazı tekrarların ek hata etiketi taşıması: baş, dirsek ve az kaldırma tekrarlarında ek "omuz" (14 tekrar), omuz tekrarlarında ek "baş" (7 tekrar).

En sık karışan hata çiftleri (galeri `liste.md`):
- omuz → az kaldırma: 37
- öne kaçma → az kaldırma: 23
- dirsek → öne kaçma: 23
- baş → omuz: 20
- dirsek → omuz: 16

### 5. Görüş grubuna göre (`gorus_grubu.csv`)
| sistem | önden makro-F1 | çapraz | profil | önden tür doğru /100 | çapraz | profil |
| --- | --- | --- | --- | --- | --- | --- |
| v2 yönlü | 0.6525 | 0.6127 | 0.2963 | 59.71 | 54.46 | 16.45 |
| v2 yönsüz | 0.6152 | 0.6348 | 0.2981 | 57.55 | 58.42 | 18.42 |
| v1b yönlü | 0.6664 | 0.5957 | 0.3099 | 62.23 | 53.96 | 20.39 |
| v1b yönsüz | 0.6191 | 0.5968 | 0.3002 | 58.63 | 56.19 | 20.39 |

### 6. Seçilen eşikler (`esikler.csv`; her satırda ayar diğer 4 kişide yapıldı)
| sistem | Honza | Mima | Petra | Terka | Vasil |
| --- | --- | --- | --- | --- | --- |
| v2 yönlü T | 4.034 | 3.676 | 4.284 | 3.769 | 5.003 |
| v2 yönsüz T | 2.419 | 2.791 | 3.083 | 3.201 | 2.688 |
| v1b yönlü T | 3.944 | 4.153 | 4.323 | 3.831 | 4.562 |
| v1b yönsüz T | 2.601 | 2.583 | 2.566 | 2.493 | 2.753 |

- **Öne kaçma ölçütü:** 20 seçimin 20'sinde `kol_boyu` seçildi; `on_kacma` hiç seçilmedi.
- **Yönler:** Her seçimde aynı çıktı:
  - YENI −1: kulak–omuz mesafesi kısalıyor;
  - bas +1: eğiklik artıyor;
  - kol_boyu −1: kol kısa görünüyor;
  - dirsek −1: dirsek bükülüyor;
  - kaldırma +1: kol az kalkıyor.
  Hepsi fizyolojik beklentiyle uyumlu.
- **Eğitim makro-F1:** v2 yönlü 0.597–0.674. Temel çizgi T değerleri `esikler.csv` dosyasında.

### 7. Kişi bazlı (`kisi.csv`), katı
| sistem | görüş | Honza | Mima | Petra | Terka | Vasil |
| --- | --- | --- | --- | --- | --- | --- |
| v2 yönlü makro-F1 | ö+ç | 0.776 | 0.501 | 0.634 | 0.731 | 0.368 |
| v2 yönlü tür doğru /100 | ö+ç | 77.0 | 47.1 | 60.6 | 69.6 | 29.2 |
| v2 yönsüz makro-F1 | ö+ç | 0.830 | 0.497 | 0.619 | 0.669 | 0.429 |
| v1b yönlü makro-F1 | ö+ç | 0.765 | 0.474 | 0.611 | 0.720 | 0.460 |
| v1b yönsüz makro-F1 | ö+ç | 0.805 | 0.472 | 0.599 | 0.664 | 0.441 |

- **v2 yönlü, kişi özeti (ö+ç):** makro-F1 0,60 (0,37–0,78).
- **Hatalı tekrara "doğru" denen sayı (v2 yönlü, ö+ç; tahminler.csv'den):**

  | Honza | Mima | Petra | Terka | Vasil |
  | --- | --- | --- | --- | --- |
  | 6 / 135 | 9 / 138 | 2 / 137 | 25 / 135 | **64 / 137** |

### 8. Kişi bazlı bootstrap, 2000 tekrar (`bootstrap.csv`)
| görüş | büyüklük | sistem / fark | nokta | %95 GA |
| --- | --- | --- | --- | --- |
| ö+ç | makro-F1 | v2 yönlü | 0.6311 | 0.5018 – 0.7366 |
| ö+ç | tür doğru /100 | v2 yönlü | 56.60 | 42.25 – 70.40 |
| ö+ç | makro-F1 farkı | v2 yönlü − v1b yönlü | +0.0045 | −0.0271 – +0.0194 |
| ö+ç | makro-F1 farkı | v2 yönsüz − v1b yönsüz | +0.0210 | +0.0020 – +0.0339 |
| ö+ç | makro-F1 farkı | v2 yönlü − v2 yönsüz | +0.0041 | −0.0323 – +0.0427 |
| ö+ç | makro-F1 farkı | v1b yönlü − v1b yönsüz | +0.0207 | −0.0142 – +0.0496 |
| tüm | makro-F1 | v2 yönlü | 0.5806 | 0.4641 – 0.6772 |
| tüm | tür doğru /100 | v2 yönlü | 49.28 | 36.92 – 61.25 |
| tüm | makro-F1 farkı | v2 yönlü − v1b yönlü | +0.0052 | −0.0260 – +0.0207 |
| tüm | makro-F1 farkı | v2 yönsüz − v1b yönsüz | +0.0197 | +0.0032 – +0.0272 |
| tüm | makro-F1 farkı | v2 yönlü − v2 yönsüz | +0.0044 | −0.0243 – +0.0361 |
| tüm | makro-F1 farkı | v1b yönlü − v1b yönsüz | +0.0189 | −0.0116 – +0.0461 |

Diğer sistemlerin GA'ları `bootstrap.csv` dosyasında.

### 9. Açı bandı kapsamı ve "kol normalden yüksek" bayrağı (`aralik_disi.csv`, v2, betimsel)
| gerçek sınıf (ö+ç) | tekrar | aralik_disi oranı | kapsam ort. |
| --- | --- | --- | --- |
| doğru | 681 | 0.0015 | 0.9453 |
| omuz | 135 | 0.0370 | 0.9396 |
| baş | 138 | 0.0362 | 0.9206 |
| öne kaçma | 137 | **0.1533** | 0.8768 |
| dirsek | 137 | 0.0073 | 0.9726 |
| az kaldırma | 135 | 0.0074 | 0.9921 |

Hiçbir tekrarın E'si boş (NaN) değil.

### Ne çıktı?
- **Hata türü bulma orta düzeyde.** Ana sistem önden + çapraz görüşte makro-F1 0,631 (GA 0,50–0,74). 100 hatalı tekrarın 57'sinde tür doğru. Rastgele tahmin makro-F1'de yaklaşık 0,17 olurdu.
- **"Yanlış var" demek ile "türünü bulmak" arasındaki fark:**
  - İkili ayrım yaklaşık 0,88–0,93 düzeyinde ve tek toplam puan bunu zaten yapıyor.
  - Tür bulma 0,61–0,63 makro-F1'de kalıyor.
  - Asıl zorluk, türü ayırt etmek.
- **Az kaldırma çok "çekici" bir sınıf.**
  - Duyarlılığı 0,94, ama kesinliği 0,55.
  - Omuz (37), öne kaçma (23), baş (16), dirsek (12) ve doğru (16) tekrarlara da "az kaldırma" deniyor.
  - Muhtemel sebep: Bu hatalarda kol gerçekten daha az kalkıyor olabilir. ADIM_02b'de silkmeli tekrarların %18,2'sinde kol referanstan ≥30° az kalkıyordu. Galerideki 3 Petra örneğinde de kol yaklaşık 120°'de kalıyor, kalibrasyon tepeleri ise yaklaşık 170°.
  - Ayrıca kaldırma z'si çok büyük değerlere çıkıyor (galeride 17–19). Tepe açısının IQR'si küçük olduğu için ölçek dar kalıyor. Bu, z'lerin hata türleri arasında karşılaştırılabilirliği için bir soru işareti; "Açık sorular" bölümüne bakın.
- **Açı bandı ile zaman bandı arasında anlamlı fark yok** (yönlü: +0,0045, GA sıfırı içeriyor).
  - Yönsüz bantta küçük bir fark var: +0,021, GA +0,002 – +0,034.
  - Deney 1 v2'deki silkme/diğer avantajı, 6 sınıflı kurala belirgin bir kazanç olarak yansımadı.
- **Yönlü ile yönsüz bant arasında fark yok** (v2: +0,004, GA sıfırı içeriyor).
  - Yönlü bant daha az yanlış alarm veriyor: doğru tekrarlarda "doğru" deme oranı 0,925'e karşı 0,899.
  - Buna karşılık daha çok hata kaçırıyor: hatalılara "doğru" deme 15,5'e karşı 11,0.
- **`kol_boyu`, `on_kacma`'dan her seferinde daha iyi bulundu.**
- **"Kol normalden yüksek" bayrağı en çok öne kaçmada kalkıyor:** öne kaçmada %15,3, doğruda %0,15. Kol öne kalkınca 2B'de kol açısı kalibrasyondan yüksek görünüyor olabilir. Bayrak karar kuralına **eklenmedi**; aşağıya bakın.
- **Profil görüşte tür bulma çalışmıyor** (makro-F1 0,30). Karar 6'daki sınırlılıkla tutarlı.
- **Vasil:** Hatalı tekrarların %47'sine (64/137) "doğru" deniyor. Galerideki kaçırılan örneklerin üçü de Vasil'den. Vasil'in seçilen eşiği diğerlerinden yüksek (T = 5,00; diğerlerinde 3,68–4,28). Bu, diğer 4 kişide seçilen bir değer. Karar 5 gereği etiketler yorumlanmıyor.

## Kullanıcının galeri gözlemi ve inceleme (6 Kasım gece)
**Kullanıcı:** "Kol yeterince yukarı kalkmıyor şeklinde uyarı veriyor. Ancak kol gayet de yukarı kalkıyor, hatta neredeyse 180 derece kalkmış."

**İnceleme:** Tepe karesi videodan alınıp iskeletle kontrol edildi. Ölçülen tepe kol açıları:

| video | bu tekrar | kişinin doğru tekrarları |
| --- | --- | --- |
| Petra cam2 o40 t5 (silkme) | 108° | 167–171° |
| Petra cam2 o70 t5 (silkme) | 112° | 161–168° |
| Petra cam3 o60 t5 (silkme) | 111° | 165–174° |
| Honza cam1 o20 t4 (öne kaçma) | 128° | 139–147° |
| Honza cam1 o30 t4 (öne kaçma) | 129° | 144–156° |
| Terka cam2 o80 t4 (öne kaçma) | 156° | 156–177° |

İki ayrı durum var:
1. **Petra (omuz → az kaldırma):** Ölçüm doğru. Tepe karesinde kol gerçekten omuz hizasında (~108°). Kişi silkme tekrarlarında kolu da az kaldırmış; etiket yalnızca birincil hatayı (silkme) veriyor.
2. **Terka ve Honza (öne kaçma → az kaldırma):** Kol gerçekte neredeyse tam yukarı kalkıyor, ama **öne doğru** gidiyor. Tek kameranın 2B görüntüsünde öne giden kol daha kısa ve daha eğik görünür, bu yüzden ölçülen kol açısı düşüyor (Terka: 156° / doğru tekrarlar 175°). Kullanıcının gözlemi bu durumu doğru tarif ediyor: sistem "kol az kalktı" diyor, oysa kol öne kaçtı.

**Neden bu kadar hassas?** Hesap iki adımda yapılıyor:
- d = (kişinin normal tepesi − bu tepe) / max(doğru tepelerin IQR'si, 5°)
- z = d / (eğitimdeki doğru tekrarların d dağılımının IQR'si ≈ 0,55–0,65 + 0,01)

T ≈ 3,7–5,0 olunca, kişinin normalinden yaklaşık **11–16° az** kalkmak "az kaldırma" için yetiyor. Kişilerin doğru tekrarları çok tutarlı (IQR çoğu zaman 5°'nin altında) olduğu için, istatistiksel olarak "anormal" sayılan sapma fizyolojik olarak küçük kalıyor. Ayrıca duruş ölçütlerinin E'si 0–1 ile sınırlı, ama d sınırsız. Bu yüzden kaldırma z'si kolayca 10–19'a çıkıp argmax'ı kazanıyor.

**Sayılar** (v2 yönlü, önden + çapraz; `puanlar.csv` + `tahminler.csv`):
- Yanlış "az kaldırma" kararı 104, doğru "az kaldırma" kararı 127.
- Kolun normalden ne kadar az kalktığı (kişinin doğru tekrarlarının medyan tepesi − bu tepe):

  | | medyan | çeyrekler | en az |
  | --- | --- | --- | --- |
  | yanlış kararlar | 26,7° | 19,0–38,1° | 12,0° |
  | gerçek az kaldırma | 41,7° | 30,5–62,5° | — |

- Yanlış kararların 27'sinde açık 20°'nin altında.
- Gerçek sınıfa göre medyan açık: silkme 41,7°, baş 24,5°, dirsek 25,0°, doğru 22,6°, öne kaçma 18,0°.

**Kaçırılan hatalar** (hatalı tekrara "doğru" denmesi): 682 hatalı tekrarın 106'sı (%15,5).
- Hata türüne göre: öne kaçma 48, baş 25, silkme 20, dirsek 9, az kaldırma 4.
- Kişiye göre: Vasil 64, Terka 25, Mima 9, Honza 6, Petra 2.
- Galerideki 3 kaçırılan örneğin üçü de Vasil'den. Rastgele seçimde 106'nın 64'ü Vasil olduğu için bu beklenen bir durum. Bu örneklerde max z (0,06; 3,78; 2,91), Vasil'in eşiği T = 5,00'ın altında kaldığı için karar "doğru" oldu.

**Öneri (danışmana; uygulanmadı, çünkü bu sonuçlar görüldükten sonra düşünüldü):**
- Kaldırma kararını yalnızca 2B kol açısına bırakmamak. Örneğin kol açısı düşükken `kol_boyu` da belirgin kısaysa "öne kaçma" öncelikli olsun.
- Kaldırma z'sini duruş ölçütleriyle karşılaştırılabilir bir ölçeğe getirmek (üst sınır ya da 0–1 biçimi).
- Bir derece alt sınırı koymak; örneğin normalden 20°'den az eksik kalmayı uyarı saymamak.
Yapılacaksa önceden tanımlanmalı ve yine birini-dışarıda-bırak ile ayarlanmalı.

## Kabul ölçütü kontrolü
- [x] 6 sınıflı karışıklık matrisi: CSV + PNG (`karisiklik_*.csv`, `karisiklik_*.png`)
- [x] Sınıf başına duyarlılık, kesinlik ve F1; makro-F1; doğruluk (`siniflar.csv`, `ozet.csv`)
- [x] Görüş grubuna göre makro-F1 (`gorus_grubu.csv`)
- [x] Katı ve esnek değerlendirme
- [x] Temel çizgi ve 6 sınıflı kural aynı tabloda (`temel_cizgi.csv`, Güncelleme 04 not 3)
- [x] Yönsüz ve yönlü bant ayrı ayrı; v1b karşılaştırma temel çizgisi (Karar 6)
- [x] T'nin her kişide hangi değere düştüğü (`esikler.csv`, tablo 6)
- [x] Önden + çapraz ve tüm görüşler; profil ayrı (Karar 6); kişi tablosu (Karar 5); bootstrap
- [x] Galeri `sonuclar/deney2/galeri/`: 2 karışma çifti + kaçırılanlar, her gruptan 3 video (Güncelleme 04 not 2)
- [x] Açı bandı ayrıntı çıktısı Adım 5'e hazır (Güncelleme 04 not 1)
- [x] Testler: `50 passed`
- [x] Kullanıcının galeri gözlemi ve incelemesi (yukarıda)

## Kararlar ve sapmalar
Hepsi kod yazılırken verildi. Kodu sınamak için deney bir kez geçici klasörde çalıştırıldı; ondan sonra hiçbir parametre değiştirilmedi. Yalnızca galeri dosya adları ASCII yapıldı.
- **Ayar kapsamı:** Ölçekleme, yön, öne kaçma ölçütü ve T, eğitim kişilerinin yalnızca **önden + çapraz** tekrarlarıyla seçildi (uygulama senaryosu). Test kişisinin tüm görüşleri bu kuralla değerlendirildi.
- **Ölçek:**
  - ε = 0,01. E 0–1 aralığında olduğu için bu, aralığın %1'i.
  - T adayları: eğitimdeki max z dağılımının %0–100 yüzdelikleri, %0,5 adımla.
  - Eşitlikte küçük T ve `on_kacma` seçilir.
- **Kaldırma:**
  - "Tepe açısı" = kol ölçütünün 5 karelik medyanla yumuşatılmış en büyük değeri. Bu, açı bandındaki tepe tanımıyla aynı.
  - PLAN tablosundaki M39 F5 (bilek–omuz–sol omuz açısı) kullanılmadı. Güncelleme 02 tepe açısını öngörüyordu.
  - Yönsüz kaldırma puanı |d|; yönlü puan, beklenen yöndeki kısım.
  - Karar 7 gereği hatalı tekrarda d, n alt kümenin ortalaması.
- **Yön:** Her ölçüt için işaret(ilgili hatalı tekrarların ortalama imzalı farkı − doğru tekrarlarınki), eğitim kişilerinde. İmzalı fark = geçerli karelerde ortalama (h − μ). v1b'de bu, hizalı eğri üzerinden hesaplanıyor.
- **Esnek değerlendirme:** Esnek gerçek etiket, tahmin {birincil} ∪ {ek hatalar} kümesindeyse tahminin kendisi; değilse birincil hata.
- **Temel çizgi:** "E'lerin ortalaması" yerine **z'lerin ortalaması** kullanıldı. Kaldırmanın E'si yok; z'ler hepsini aynı ölçeğe getiriyor. Eşik eğitimde dengeli doğruluğa göre seçildi.
- **Ana sistem v2 yönlü:** Galeri ve basit anlatım için sonuçlar görülmeden seçildi. Sonuçlara göre yönsüzden farkı anlamlı değil; bu değiştirilmedi.
- **`aralik_disi` karar kuralına eklenmedi.** Güncelleme 02 "eğitim kişilerinde gerekli olup olmadığına bak" diyordu. Tablo 9 betimsel ve test kişileri de içinde. Bu tabloya bakarak kuralı değiştirmek test verisiyle ayar olurdu. Danışmana öneri olarak aşağıda.

## Açık sorular / danışmana notlar
- **Az kaldırma sınıfının baskınlığı.** İki olası çözüm var; ikisi de bu sonuçlar görüldükten sonra düşünüldüğü için uygulanmadı:
  - (a) Kaldırma z'sinin ölçeğini genişletmek. Örneğin tepe IQR alt sınırını 5°'den büyütmek ya da z'yi duruş ölçütleriyle aynı biçimde (E benzeri, 0–1) tanımlamak.
  - (b) Kaldırmayı ancak diğer duruş z'lerinin hepsi düşükken söylemek (öncelik kuralı).
  Yapılacaksa önceden tanımlanıp yine birini-dışarıda-bırak ile ayarlanmalı. Ayrıca Ex7'de (Adım 4b) ayarsız doğrulanabilir.
- **Etiketin birincil olması:** Silkmeli tekrarların bir kısmında kol gerçekten az kalkıyorsa, "omuz → az kaldırma" kararları tamamen yanlış sayılmamalı. Esnek değerlendirme bunu yakalamıyor, çünkü ek hata etiketi yok. Galeri gözlemi bu soruyu cevaplayabilir.
- **`aralik_disi` bayrağı öne kaçmaya ek kanıt olabilir** (%15,3'e karşı doğruda %0,15). Eklenip eklenmeyeceği danışmanın kararı.
- **Adım 5 için:** Ana sistem yönlü mü yönsüz mü olsun? Makro-F1 farkı yok. Yönlü bant daha az gereksiz uyarı veriyor (doğru tekrarlarda "doğru" deme 0,925'e karşı 0,899), ama daha çok hata kaçırıyor. Geri bildirim uygulaması için yanlış alarmın az olması tercih edilebilir.
- **Vasil:** Hatalı tekrarların %47'si kaçırılıyor. Kişi farkı Deney 1'deki gibi büyük.

---

# Ek: Güncelleme 05 — Deney 2 revize (Karar 13–14)

**Tarih:** 2026-11-07
**Durum:** Tamamlandı. Kullanıcı `python -m deneyler.deney2` ve `python -m deneyler.deney2_galeri` komutlarını çalıştırdı (7 Kas 00:05–00:09). Sayılar `sonuclar/deney2/` altındaki CSV dosyalarından birebir kopyalandı. İlk sürüm `sonuclar/deney2_ilk/` altında korunuyor; yukarıdaki tablolar ilk sürüme ait.

## Basit anlatım
**En önemli tek sonuç:** Yeni "az kaldırma" puanı sorunu **çözmedi, büyüttü.** Ana sistemde (v2 yönlü, önden + çapraz) makro-F1 0,631'den **0,568**'e düştü (fark −0,064, GA −0,117 – −0,007; sıfırı içermiyor). Yanlış "az kaldırma" kararı 104'ten **205**'e çıktı.

**Neden?**
- Yeni puan (E), doğru tekrarların %97'sinde tam **0**.
- Bu yüzden z ölçeklemesindeki "doğruların yayılımı" (IQR), beş eğitim kümesinin beşinde de 0 çıktı. Paydada yalnızca ε = 0,01 kaldı.
- Sonuç: z = 100 × E. Eşik T ≈ 3,1–3,7 olduğu için E ≈ 0,035 yetiyor.
- Yani kol, kişinin normalinden **τ'nun yaklaşık %3,5 fazlası** kadar az kalktığında (τ = 10° iken ≈ 10,4°) sistem "az kaldırma" diyor. İlk sürümde bu sınır yaklaşık 11–16° idi.

10° alt sınırın kendisi doğru çalışıyor. Sorun, z ölçeğinin 0'da yığılan bir dağılıma uygulanması. Bu bir **kod hatası değil**; Karar 13'teki "aynı z ölçeklemesi" adımının bu ölçütte doğurduğu sonuç.

**İyi haberler:**
- **İlk iki (Karar 14):** 100 hatalı tekrarın **76**'sında gerçek birincil hata, sistemin en yüksek iki z'si içinde (75,81). Kuralın söyleyeceği ilk iki hatanın içinde olma oranı ise **69** (68,62); 2. hata ancak o da T'yi geçerse söyleniyor.
- **Kaçırma azaldı:** Hatalı tekrara "doğru" deme 15,5'ten 10,1'e indi (GA −14,8 – −0,4).
- **Yönlü bant artık yönsüzden anlamlı olarak iyi:** +0,0555 (GA +0,023 – +0,078). Sebebi, yönsüz kaldırma puanının "fazla kalkmayı" da hata sayması.

## Yapılanlar
- `cekirdek/hata_turu.py`:
  - `tepe_bandi(tepeler)`: μ = ortalama, τ = max(t(0,975; n−1)·s/√n, 10°); s örneklem standart sapması.
  - `kaldirma_puanlari(tepe, tepeler)`: eksik = μ − tepe. Sapma ≤ τ ise E = 0; değilse E = min(1, (sapma − τ)/τ).
    - yönlü (+1): yalnızca eksik;
    - −1: yalnızca fazla;
    - yönsüz: |eksik|.
  - Kaldırma artık diğer ölçütlerle aynı biçimde işleniyor: `E_kaldirma_{0,p,n}` sütunları, aynı z, aynı karar kuralı.
  - Kaldırmanın yönü sabit +1 (Karar 13: "yalnızca eksik"). Eskiden eğitimden öğreniliyordu; 20 seçimin 20'sinde zaten +1 çıkmıştı.
  - `ilk_iki(z, T)`: en yüksek iki z'nin hataları ve kuralın söyleyeceği hatalar. Adım 5 aynı fonksiyonu kullanacak.
  - Eski `kaldirma_sapmasi` (d) kaldırıldı. İlk sürüm kodu git'te, `573edcf` commit'inde duruyor.
- `deneyler/deney2.py` yeni çıktılar üretiyor:
  - `ilk_iki.csv`;
  - `kaldirma.csv`: az kaldırma kararlarında eksik açı;
  - `ilk_surum_karsilastirma.csv`: revize − ilk, aynı tekrarlarda, kişi bazlı bootstrap (2000).
- `deneyler/deney2_galeri.py`: Kaldırma grafiği μ ± τ bandını ve eksik açıyı gösteriyor.
- Testler: `test_tepe_bandi`, `test_kaldirma_puanlari`, `test_ilk_iki` eklendi → `52 passed`.
- Kod önce geçici klasörde bir kez çalıştırıldı (sınama). Kullanıcının çalıştırmasında bütün tablolar birebir aynı çıktı. Sınamadan sonra hiçbir parametre değiştirilmedi.

## Sonuçlar (revize)

### 1. Revize − ilk sürüm (`ilk_surum_karsilastirma.csv`; aynı 1363 / 1668 tekrar)
Makro-F1, katı:

| görüş | sistem | ilk | revize | fark | %95 GA |
| --- | --- | --- | --- | --- | --- |
| ö+ç | **v2 yönlü** | 0.6311 | **0.5676** | −0.0635 | −0.1168 – −0.0068 |
| ö+ç | v2 yönsüz | 0.6270 | 0.5121 | −0.1149 | −0.1475 – −0.0738 |
| ö+ç | v1b yönlü | 0.6266 | 0.5619 | −0.0647 | −0.1100 – −0.0263 |
| ö+ç | v1b yönsüz | 0.6059 | 0.4966 | −0.1093 | −0.1356 – −0.0855 |
| tüm | v2 yönlü | 0.5806 | 0.5243 | −0.0563 | −0.1014 – −0.0087 |

Ana sistem (v2 yönlü), diğer büyüklükler:

| görüş | büyüklük | ilk | revize | fark | %95 GA |
| --- | --- | --- | --- | --- | --- |
| ö+ç | hatalılarda tür doğru /100 | 56.60 | 51.17 | −5.43 | −12.32 – +3.36 |
| ö+ç | hatalılarda "doğru" dedi /100 | 15.54 | 10.12 | −5.43 | −14.83 – −0.44 |
| ö+ç | doğrularda "doğru" dedi /100 | 92.51 | 90.02 | −2.50 | −4.42 – −0.74 |
| ö+ç | "az kaldırma" kararı kesinliği | 0.550 | 0.390 | −0.160 | −0.224 – −0.099 |
| tüm | hatalılarda tür doğru /100 | 49.28 | 45.32 | −3.96 | −9.83 – +3.47 |

### 2. Özet (`ozet.csv`)
| sistem | görüş | makro-F1 katı | esnek | doğruluk 6 sınıf | hatalılarda tür doğru /100 (katı) | (esnek) | hatalılarda "doğru" dedi /100 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **v2 yönlü** | ö+ç | **0.568** | 0.577 | 0.706 | **51.17** | 52.05 | 10.12 |
| v2 yönlü | tüm | 0.524 | 0.532 | 0.674 | 45.32 | 46.04 | 17.63 |
| v2 yönlü | profil | 0.305 | 0.305 | 0.531 | 19.08 | 19.08 | 51.32 |
| v2 yönsüz | ö+ç | 0.512 | 0.519 | 0.668 | 46.04 | 46.63 | 7.48 |
| v1b yönlü | ö+ç | 0.562 | 0.572 | 0.703 | 50.73 | 51.76 | 10.26 |
| v1b yönsüz | ö+ç | 0.497 | 0.506 | 0.668 | 44.87 | 45.60 | 5.87 |

Temel çizgi (tek toplam hata, yalnızca doğru/yanlış), v2 yönlü, ö+ç: ikili doğruluk 0.892. Aynı veride 6 sınıflı kuralın ikili doğruluğu 0.899.

### 3. İlk iki (Karar 14; `ilk_iki.csv`)
| sistem | görüş | birincil = 1. z /100 | birincil ilk iki z içinde /100 | birincil söylenen ilk iki içinde /100 | hatalılarda 2. z ≥ T /100 | yakalanan hatalılarda 2. z ≥ T (%) | söylenen 2. hata = birincil /100 | doğrularda 2. z ≥ T /100 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **v2 yönlü** | ö+ç | 55.13 | **75.81** | **68.62** | 55.57 | 61.83 | 17.45 | 1.62 |
| v2 yönlü | tüm | 50.96 | 71.94 | 60.43 | 49.88 | 60.55 | 15.11 | 1.68 |
| v2 yönlü | profil | 32.24 | 54.61 | 23.68 | 24.34 | 50.00 | 4.61 | 1.96 |
| v2 yönsüz | ö+ç | 50.29 | 80.94 | 72.58 | 62.17 | 67.19 | 26.54 | 1.91 |
| v1b yönlü | ö+ç | 54.99 | 74.93 | 66.86 | 55.43 | 61.76 | 16.13 | 1.17 |
| v1b yönsüz | ö+ç | 48.09 | 76.25 | 69.50 | 73.17 | 77.73 | 24.63 | 2.79 |

Not: "birincil = 1. z" (55,13) eşikten bağımsız. "Tür doğru" (51,17) daha düşük, çünkü max z < T olan tekrarlar "doğru" sayılıyor.

### 4. Sınıf başına ve karışıklık (v2 yönlü, ö+ç, katı)
| sınıf | destek | duyarlılık | kesinlik | F1 |
| --- | --- | --- | --- | --- |
| doğru | 681 | 0.900 | 0.899 | 0.899 |
| omuz | 135 | 0.311 | 0.545 | 0.396 |
| baş | 138 | 0.341 | 0.580 | 0.429 |
| öne kaçma | 137 | 0.409 | 0.560 | 0.473 |
| dirsek | 137 | 0.533 | 0.839 | 0.652 |
| az kaldırma | 135 | 0.970 | 0.390 | 0.556 |

| gerçek \ karar | doğru | omuz | baş | öne kaçma | dirsek | az kaldırma |
| --- | --- | --- | --- | --- | --- | --- |
| doğru | **613** | 10 | 17 | 13 | 8 | 20 |
| omuz | 6 | **42** | 13 | 13 | 0 | 61 |
| baş | 19 | 12 | **47** | 6 | 0 | 54 |
| öne kaçma | 37 | 3 | 3 | **56** | 6 | 32 |
| dirsek | 4 | 9 | 1 | 12 | **73** | 38 |
| az kaldırma | 3 | 1 | 0 | 0 | 0 | **131** |

### 5. Az kaldırma kararlarında kol ne kadar eksik kalktı? (`kaldirma.csv`; v2 yönlü, ö+ç; eksik = μ − tepe)
| grup | tekrar | eksik medyan | Ç1–Ç3 | en az | eksik < 20° |
| --- | --- | --- | --- | --- | --- |
| doğru "az kaldırma" kararı | 131 | 39.6° | 29.5–61.2° | 12.6° | 8 |
| yanlış "az kaldırma" kararı | 205 | 19.6° | 15.0–27.0° | 10.3° | 107 |
| gerçek sınıf: doğru | 681 | −0.2° | −3.2–2.8° | | |
| gerçek sınıf: omuz | 135 | 9.0° | −3.9–24.5° | | |
| gerçek sınıf: baş | 138 | 5.3° | −6.2–15.0° | | |
| gerçek sınıf: öne kaçma | 137 | 0.3° | −10.8–8.5° | | |
| gerçek sınıf: dirsek | 137 | 4.7° | −0.5–12.1° | | |
| gerçek sınıf: az kaldırma | 135 | 38.7° | 28.3–61.1° | | |

Not: İlk sürümdeki "eksik" tablosu μ yerine kalibrasyon tepelerinin **medyanını** kullanıyordu. Bu yüzden iki tablo birebir karşılaştırılamaz.

### 6. Eşikler ve ölçek (`esikler.csv`, v2 yönlü)
| | Honza | Mima | Petra | Terka | Vasil |
| --- | --- | --- | --- | --- | --- |
| T | 3.137 | 3.676 | 3.688 | 3.748 | 3.457 |
| kaldırma medyanı | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| kaldırma ölçeği (IQR + ε) | **0.01** | **0.01** | **0.01** | **0.01** | **0.01** |
| YENI ölçeği (karşılaştırma için) | 0.0811 | 0.0771 | 0.0836 | 0.0797 | 0.0847 |

- Doğru tekrarların %3,1'inde kaldırma E'si 0'dan büyük. Yüzdelikler (50/75/90/95): 0, 0, 0, 0.
- E en fazla 1 olduğu için kaldırma z'si 100'e kadar çıkabiliyor (galeride max z = 100,00). Duruş ölçütlerinde z yaklaşık 12'de kalıyor.
- Öne kaçma ölçütü 20 seçimin 20'sinde yine `kol_boyu`. Yönler ilk sürümle aynı.

### 7. Kişi bazlı (v2 yönlü, ö+ç; `kisi.csv`)
| | Honza | Mima | Petra | Terka | Vasil |
| --- | --- | --- | --- | --- | --- |
| makro-F1 revize | 0.749 | 0.400 | 0.500 | 0.608 | 0.422 |
| makro-F1 ilk | 0.776 | 0.501 | 0.634 | 0.731 | 0.368 |
| tür doğru /100 revize | 77.04 | 35.51 | 48.91 | 56.30 | 38.69 |
| hatalılarda "doğru" dedi /100 | 2.96 | 6.52 | 0.73 | 17.78 | 22.63 |
| birincil ilk iki z içinde /100 | 84.44 | 60.87 | 82.48 | 88.15 | 63.50 |

Makro-F1 Vasil dışındaki dört kişide düştü. Vasil'de 0,368'den 0,422'ye yükseldi; sebebi daha az kaçırma.

### 8. Sistemler arası bootstrap farkları (revize; `bootstrap.csv`)
| görüş | fark | nokta | %95 GA |
| --- | --- | --- | --- |
| ö+ç | v2 yönlü − v1b yönlü | +0.0057 | −0.0055 – +0.0130 |
| ö+ç | v2 yönsüz − v1b yönsüz | +0.0155 | +0.0056 – +0.0251 |
| ö+ç | v2 yönlü − v2 yönsüz | **+0.0555** | +0.0234 – +0.0778 |
| ö+ç | v1b yönlü − v1b yönsüz | +0.0653 | +0.0369 – +0.0886 |

### Galeri (`sonuclar/deney2/galeri/`)
- En sık karışan iki çift artık **omuz → az kaldırma (61)** ve **baş → az kaldırma (54)**.
- Sonra gelenler: dirsek → az kaldırma (38), öne kaçma → az kaldırma (32).
- Kaçırılan hata: 69 tekrar.
- İlk sürümün galeri videoları `sonuclar/deney2_ilk/galeri/` altında.

### Ne çıktı?
- **Karar 13'ün amacı sağlanamadı.** Amaç, az kaldırmanın argmax'ı haksız yere kazanmasını önlemekti. Puanı 0–1 aralığına getirmek yetmedi, çünkü z ölçeği puanın kendisini değil, doğru tekrarlardaki **yayılımını** kullanıyor. Kaldırma E'si doğrularda 0'da yığıldığı için yayılım 0, ölçek de ε oldu.
- **10° alt sınır çalışıyor ama tek başına yetmiyor.** Yanlış kararlarda en küçük eksik 10,3°; yani 10°'nin altında hiçbir "az kaldırma" kararı yok. Ancak eksiği 10,3–20° arasında kalan 107 yanlış karar, z = 100·E yüzünden eşiği kolayca geçiyor.
- **Etiket sınırlılığı görünür oldu.** Gerçek "omuz" sınıfında eksik medyanı 9,0°, Ç3 24,5°. Silkmeli tekrarların en az dörtte birinde kol, normalden yaklaşık 25°'den fazla az kalkıyor. "İlk iki" metriği bunu kısmen yakalıyor: birincil hata 100 tekrarın 76'sında ilk iki içinde.
- **Yönlü bant artık yönsüzden anlamlı olarak iyi** (+0,056). Bu, Karar 15 ile (ana sistem v2 yönlü) tutarlı.

## Kararlar ve sapmalar
- **Kaldırmanın yönü sabit +1** (Karar 13: "yönlüde yalnızca eksik"). Eğitimden öğrenme kaldırıldı; ilk sürümde 20 seçimin 20'sinde zaten +1 idi.
- **n ve s:** n, bir modeldeki kalibrasyon tepesi sayısı. Doğru tekrarda bu, birini-dışarıda-bırak modelinin n−1 tekrarı; hatalıda n alt modelin her biri. s, örneklem standart sapması (ddof = 1). Karar 7 gereği hatalı tekrarda E ve eksik, n alt modelin ortalaması.
- **Tablo 5'te eksik μ'ye (ortalama) göre.** İlk sürümün incelemesi medyan kullanıyordu.
- **Ölçeklemeye dokunulmadı.** Sorun sınamada görüldü. Kuralı sonuç gördükten sonra değiştirmek, test verisiyle ayar yapmak olurdu. Danışmana soru olarak aşağıda.
- Galeri klasöründeki ilk sürüm videoları (9 dosya) `deney2/galeri/` altından kaldırıldı; kopyaları `deney2_ilk/galeri/` içinde.

## Açık sorular / danışmana notlar
- **Adım 5 ve uygulama hangi kaldırma sürümünü kullanacak?** Seçenekler aşağıda. Hepsi sonuçlar görüldükten sonra düşünüldü; hiçbiri uygulanmadı.
  - (a) İlk sürüme dönmek (makro-F1 0,631) ve sınırlılığı yazmak.
  - (b) Revizeyi korumak, ama 0'da yığılan kaldırma dağılımı için IQR yerine sabit bir ölçek kullanmak. Örneğin ölçek = 1, yani z = E; o zaman "τ'nun bir katı kadar fazladan eksik" z = 1 eder. Bu, duruş ölçütleriyle aynı "birim" değil; önceden gerekçelendirilmesi gerekir.
  - (c) Duruş ölçütlerinde de z'yi kaldırıp E'leri (0–1) doğrudan karşılaştırmak: tek bir T, ölçekleme yok.
  - Hangisi seçilirse seçilsin, sonuçlara bakılarak seçildiği raporda açıkça yazılmalı ve Ex7 ile kendi kayıtlarımızda doğrulanmalı. Ex7'de az kaldırma sınıfı olmadığı için Adım 4b bu karardan etkilenmiyor.
- **"İlk iki" Adım 5 için umut verici.** Geri bildirim iki hata söylerse, birincil hata 100 hatalı tekrarın 69'unda söylenmiş oluyor. Doğru tekrarlarda ikinci bir uyarı yalnızca %1,6 oranında çıkıyor.
