# ADIM 01 — Çekirdek modül ve Deney 1 regresyon testi

**Tarih:** 2026-11-06
**Durum:** Tamamlandı

## Basit anlatım (kullanıcı için, 3–6 cümle)
Danışmanın tek dosyalık Deney 1 kodunu, ileride deneylerin ve uygulamanın ortak kullanacağı parçalara ayırdık (`cekirdek/`). Her parçanın tek bir işi var: ölçütleri hesaplamak, iki tekrarı zamanda hizalamak (DTW), kişiye özel "normal aralık" bandını kurmak, sonuçları değerlendirmek. Amaç davranışı değiştirmemekti. Bunu, yeni kodla deneyi yeniden çalıştırıp danışmanın tablosuyla karşılaştırarak kontrol ettik: danışmanın verisiyle tekrar başına skorlar referans kodla **birebir aynı** (fark 0), tablo farkı en fazla 0,0005. Orijinal Zenodo verisiyle tablo farkı en fazla 0,0042; izin verilen sınır 0,01. Ayrıca en yavaş kısmı (DTW) hızlandırdık: deney 46 saniye yerine yaklaşık 13 saniyede bitiyor.

*Jargon:* **DTW (dinamik zaman bükme):** Biri hızlı biri yavaş yapılmış iki tekrarı, "aynı andaki" kareleri eşleyerek hizalar. **Bant:** Kişinin doğru tekrarlarından çıkan, her an için "normalde bu ölçüt şu aralıkta" bilgisi. **AUC:** Bir ölçütün iki grubu (ör. silkmeli / doğru) ne kadar iyi ayırdığı; 0,5 yazı-tura, 1,0 kusursuz. **Regresyon testi:** "Kodu değiştirdim ama sonuç bozulmadı mı?" kontrolü.

## Yapılanlar
- `cekirdek/` altında referans kod modüllere bölündü; mantık, rastgele sayı çekme sırası dahil, birebir korundu.
- Ölçütler için kayıt sistemi kuruldu (`@olcut("AD")`); Adım 4'te yeni ölçüt eklemek tek bir fonksiyon yazmak demek.
- DTW, numba ile derlendi; hizalamadaki Python döngüsü `np.bincount` ile vektörize edildi. Eşitlik durumunda hangi yolun seçileceği referansla aynı (testle kontrol ediliyor).
- Bant hatasına **yönlü** seçenek eklendi (`yon=+1` yalnızca bandın üstüne çıkış, `−1` yalnızca altına iniş). Varsayılan yönsüz (M39, referans). Yönlü seçenek Adım 4'te kullanılacak.
- `deneyler/deney1.py`: deney çekirdekle yeniden yazıldı; `--kaynak zip|npz`, `--en-boy`, `--tohum` seçenekleri var.
- Testler: çekirdek birim testleri ve Deney 1 regresyon testi (iki kaynakla).
- Windows konsolu `Ψ` ve `°` gibi karakterleri yazamadığı için (referans kod bu yüzden tabloyu yazarken çöktü) çıktı UTF-8'e çevrildi (`cekirdek/konsol.py`).

## Değişen / eklenen dosyalar
| Dosya | Ne işe yarıyor |
| --- | --- |
| `cekirdek/geometri.py` | En-boy düzeltmeli nokta (`nokta`), açı (`aci`) |
| `cekirdek/ozellikler.py` | `Iskelet` yardımcı sınıfı, ölçüt kayıt sistemi (`OLCUTLER`, `@olcut`), `kol`, M01, M01_tek, M39_F2, M33, YENI; `ozellikler()` |
| `cekirdek/hizalama.py` | `dtw_yol` (numba), `hizala` |
| `cekirdek/bant.py` | `bant_modeli` (μ, τ, Q1 alt sınırı), `kare_hatasi` (yönsüz/yönlü), `bant_hatasi` (`ayrinti=True` ile kare bazında hata da döner) |
| `cekirdek/degerlendirme.py` | `auc`, `ham_skor`, `psi`, `kisi_bootstrap`, `guven_araligi` |
| `cekirdek/konsol.py` | Konsol çıktısını UTF-8 yapar |
| `deneyler/deney1.py` | Deney 1 (çekirdeği içe aktarır) |
| `testler/test_cekirdek.py` | DTW referansla aynı mı, hizalama, açı, yönlü/yönsüz bant hatası, AUC, ölçüt kaydı |
| `testler/test_deney1_regresyon.py` | Deneyi zip ve npz ile yeniden çalıştırıp beklenen tabloyla karşılaştırır; ayrıca `sonuclar/deney1/ozet.csv` varsa onu da |
| `requirements.txt` | `numba>=0.60` eklendi |
| `araclar/veri_tanit.py` | Yalnızca UTF-8 çıktı satırı eklendi |

## Nasıl çalıştırılır
```bash
python -m deneyler.deney1                 # orijinal veri; ~15 s
python -m deneyler.deney1 --kaynak npz    # danışmanın küçük kopyası; ~15 s
python -m pytest testler -q               # ~10 s
```
Çıktı: `sonuclar/deney1/tekrarlar.csv` (tekrar başına skorlar), `ozet.csv` (AUC/Ψ tablosu), `bootstrap.csv` (güven aralıkları), `hata_turu_ortalama.csv`.
Not: `sonuclar/deney1/` bu adımda bilerek üretilmedi; PLAN'a göre Adım 2'de kullanıcı çalıştıracak. Aşağıdaki sayılar geçici klasördeki çalıştırmalardan kopyalandı.

## Sonuçlar

**Regresyon (beklenen tabloya göre en büyük mutlak fark), pytest çıktısından:**

| Kaynak | En büyük fark | Nerede | Sınır |
| --- | --- | --- | --- |
| orijinal zip | 0.00424837 | bant, M39_F2, AUC profil (70–90°) | 0,01 ✔ |
| küçük npz | 0.000544662 | bant, M01, AUC profil (70–90°) | 0,01 ✔ |

**Tekrar bazında referans kodla karşılaştırma (npz, aynı ortam):** Referans kod (`referans/deney1_omuz_olcutleri.py`) geçici klasörde çalıştırıldı (46 s). 1668 tekrarın 10 skor sütununda **en büyük fark 0.0**: çekirdek, referansla bit düzeyinde aynı sonucu veriyor.

**Deney 1, orijinal veri (zip), en-boy 0.5625, tohum 0** (terminal çıktısından):
```
Tekrar sayıları (3 kamera dahil): silkme=165, doğru=834, diğer hatalar=612

yöntem   ölçüt  AUC silkme/doğru  AUC silkme/diğer hatalar  AUC önden (0–20°)  AUC çapraz (30–60°)  AUC profil (70–90°)  Ψ (M39)
   ham     M01             0.650                     0.683              0.751                0.673                0.544      NaN
   ham M01_tek             0.658                     0.712              0.763                0.690                0.579      NaN
   ham  M39_F2             0.600                     0.644              0.684                0.599                0.559      NaN
   ham     M33             0.638                     0.695              0.746                0.664                0.593      NaN
   ham    YENI             0.704                     0.699              0.767                0.759                0.554      NaN
  bant     M01             0.822                     0.642              0.885                0.830                0.670    0.221
  bant M01_tek             0.866                     0.662              0.898                0.889                0.743    0.275
  bant  M39_F2             0.888                     0.637              0.888                0.924                0.794    0.281
  bant     M33             0.904                     0.646              0.918                0.914                0.849    0.300
  bant    YENI             0.909                     0.705              0.942                0.933                0.779    0.330

Bant yöntemi, AUC silkme/doğru için %95 güven aralığı (kişi bazlı bootstrap, 2000 tekrar):
  M01            ort. 0.822, %95 GA 0.776 – 0.884
  M01_tek        ort. 0.866, %95 GA 0.815 – 0.919
  M39_F2         ort. 0.888, %95 GA 0.811 – 0.955
  M33            ort. 0.903, %95 GA 0.823 – 0.968
  YENI           ort. 0.909, %95 GA 0.849 – 0.961
  YENI − M39_F2  ort. 0.021, %95 GA -0.017 – 0.060
```
Süre: 13.1 s.

**Hız:** referans kod 46 s (npz, bootstrap dahil) → çekirdek 13–15 s (bootstrap dahil).

## Kabul ölçütü kontrolü
- [x] Tohum 0, en-boy 9/16 ile bant ve ham AUC değerleri beklenen tablodan en fazla ±0,01 sapıyor: zip 0.00424837, npz 0.000544662.
- [x] Hızlandırma sonrası sonuç aynı: DTW yolu 6 testte referansla birebir aynı, tekrar skorları referans kodla fark 0.0.
- [x] Testler geçti: `18 passed, 1 skipped in 9.97s` (atlanan: `sonuclar/deney1/ozet.csv` henüz yok; Adım 2'de oluşacak).

## Kararlar ve sapmalar
- **Beklenen tablo ile npz arasındaki küçük fark (≤ 0.000545) neden var?** Bu ortamda referans kodun kendisi de çekirdekle bit düzeyinde aynı tekrar skorlarını üretiyor. Ham satırları beklenen tabloyla tam aynı; fark yalnızca bant satırlarında (24 hücre, en çok 0.000545). Demek ki `beklenen_deney1_ozet.csv`, danışmanın farklı bir ortamında (büyük olasılıkla farklı numpy/scipy sürümü) üretilmiş. Kesin sebep belirlenemedi; sınırın çok altında olduğu için kabul edildi.
- **Zip ile npz farkı:** Orijinal veri float64, npz float16. Tablo düzeyinde fark ≤ 0,0042. Tekrar düzeyinde bantsız M39_F2'de 3.93°'ye varan fark var (ex1_Mima cam1, yönelim 90, profil): profilde iki omuz üst üste düştüğü için omuz vektörü çok kısalır ve açı küçük yuvarlamalara çok duyarlı olur.
- **Yönlü bant hatası** eklendi (PLAN'da isteniyor); varsayılan davranış değişmedi.
- **Ölçütler `Iskelet` nesnesi üzerinden hesaplanıyor.** Noktalar ve gövde uzunluğu önbellekte tutuluyor, böylece yeni ölçütler aynı noktaları tekrar hesaplamıyor. `g0` = ilk 8 karenin medyan gövde uzunluğu (referansla aynı).
- **numba** `requirements.txt`'e eklendi. Kurulu değilse kod saf Python'a döner; sonuç aynı, sadece yavaş.

## Açık sorular / danışmana notlar
- **Tek tekrarın bant hatası E, rastgele seçimlere çok duyarlı.** Aynı veriyle yalnızca tohum 0 → 1 yapılınca (yani bandın kurulduğu referans tekrar ve dışarıda bırakılan doğru tekrar değişince) E, YENI'de tekrarların %26,7'sinde, M39_F2'de %30,2'sinde 0,05'ten fazla değişiyor (medyan değişim 0,0192 / 0,022; E'nin ortalaması ≈ 0,21, standart sapması ≈ 0,2). Karşılaştırma için veri hassasiyeti (zip ↔ npz) etkisi: medyan 0,0045, tekrarların yalnızca %2,1'inde > 0,05. AUC gibi toplu sonuçlar sağlam kalıyor, ama Adım 4–6'da **tek bir tekrar için karar** verilecek. Öneri: modeli tek bir rastgele referans yerine birkaç referansla (ör. her doğru tekrar sırayla referans) kurup E'lerin ortalamasını almak. Bu, M39'dan bir sapma olur ve Deney 1 sonuçlarını değiştirir. Bu yüzden kendiliğimden yapmadım; danışman ve kullanıcı karar versin.
