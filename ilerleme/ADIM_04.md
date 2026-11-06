# ADIM 04 — Deney 2: hata türünü bulma

**Tarih:** 2026-11-06
**Durum:** Tamamlandı. Kullanıcı `python -m deneyler.deney2` (23:31–23:33) ve `python -m deneyler.deney2_galeri` (23:33) komutlarını çalıştırdı. Sayılar `sonuclar/deney2/` altındaki CSV dosyalarından birebir kopyalandı. Galeri gözlemleri henüz eklenmedi (bkz. "Açık sorular").

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
- [ ] Kullanıcının galeri gözlemleri (isteğe bağlı; eklenecek)

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
