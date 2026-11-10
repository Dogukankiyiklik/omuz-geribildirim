# ADIM 00 — Ortam ve veri: orijinal dosyalardan doğrudan okuma

**Tarih:** 2026-11-06
**Durum:** Tamamlandı

## Basit anlatım (kullanıcı için, 3–6 cümle)
Bu adımda bilgisayarda projenin çalışacağı Python ortamını kurduk ve veri setini "tanıdık". Veri setinde her video karesi için MediaPipe'ın bulduğu 33 vücut noktası var; her noktanın x, y konumu, z (derinlik tahmini) ve "görünürlük" (MediaPipe'ın o noktadan ne kadar emin olduğu) değeri. Önemli soru şuydu: x ve y **piksel** mi (ör. 540, 960), yoksa resmin genişliğine/yüksekliğine bölünmüş **0–1 arası** sayılar mı? Cevap: 0–1 arası (normalize). Bunu iki yoldan doğruladık: değerler 0–1 civarında ve noktaları x·1080, y·1920 ile videoya çizince tam kişinin üstüne oturuyor (`sonuclar/adim0/iskelet_kontrol.png`). Videolar dikey (1080 geniş, 1920 yüksek) olduğu için açı hesaplamadan önce x'i 1080/1920 = 9/16 ile çarpıyoruz; yoksa yatay mesafeler olduğundan uzun görünür ve açılar bozulur.

## Yapılanlar
- Python 3.11.9 ile `.venv` oluşturuldu, `requirements.txt` kuruldu.
- `cekirdek/veri.py`: iskeletleri zip'i açmadan **doğrudan** `jointSequences-mediapipe.zip` içinden okuyor. Her tekrarı `first_frame − 10 … last_frame + 10` aralığında kesiyor, etiketleri `Segmentation.csv` satır numarasıyla bağlıyor ve (video, kamera, yönelim) gruplarına ayırıyor. 33 eklemin hepsi tutuluyor. İstenirse aynı biçimde `rehab26_kucuk.npz`'den de okuyor (Adım 1'deki regresyon testi için).
- `araclar/veri_tanit.py`: veri tanıtım betiği (aşağıda çıktı özeti; tam çıktı `sonuclar/adim0/veri_tanit_cikti.txt`).
- Video çözünürlüğü, videoyu açmadan `videos.zip` içindeki MP4 başlığından okundu (15 Ex1 videosu). Bir video ayrıca OpenCV ile açılarak doğrulandı.
- `testler/test_veri.py`: görüş açısı, tekrar sayıları ve npz eşdeğerlik testleri.

## Değişen / eklenen dosyalar
| Dosya | Ne işe yarıyor |
| --- | --- |
| `.venv/` | Sanal ortam (git'e girmez) |
| `cekirdek/__init__.py`, `araclar/__init__.py`, `deneyler/__init__.py`, `testler/__init__.py` | Klasörleri Python paketi yapar (`python -m ...` için) |
| `cekirdek/veri.py` | Orijinal zip'ten / npz'den okuma, tekrar kesme, gruplama, görüş açısı ve grubu, sabitler (`EN_BOY`, `KAMERA_KONUMU`, `EKLEMLER_13`) |
| `araclar/veri_tanit.py` | Veri setini tanıtan betik; `--resim` ile videoya iskelet bindirilmiş bir kare kaydeder |
| `testler/test_veri.py` | Adım 0 testleri |
| `sonuclar/adim0/veri_tanit_cikti.txt` | Tanıtım betiğinin tam çıktısı |
| `sonuclar/adim0/iskelet_kontrol.png` | ex1_Honza cam1, kare 102: iskelet videoya oturuyor mu? |

## Nasıl çalıştırılır
```bash
.venv\Scripts\activate
python -m araclar.veri_tanit --resim     # ~10 saniye
python -m pytest testler -q              # ~2 saniye
```
Çıktı: ekrana tanıtım metni, `sonuclar/adim0/iskelet_kontrol.png`.

## Sonuçlar
Sayılar `sonuclar/adim0/veri_tanit_cikti.txt` dosyasından kopyalandı.

**Zip içeriği:** 90 dosya; ex1, ex6, ex7 için her birinde 15 `_2d` + 15 `_3d` (5 kişi × 3 kamera). Not: zip'te ex6 (squat) de var; biz kullanmıyoruz.

**Bir dosyanın biçimi** (`mediapipe/ex1/ex1_Honza_cam1_2d.npy`): `shape = (24388, 33, 4)`, `dtype = float64`. Tamamen sıfır (iskelet bulunamamış) kare: 10.

| Sütun | en küçük | en büyük |
| --- | --- | --- |
| x | -0.1514 | 1.1255 |
| y | 0.2187 | 1.6739 |
| z | -1.8675 | 2.3160 |
| görünürlük | 0.0358 | 1.0000 |

(0–1 dışına taşan değerler kadraj dışına çıkan el/ayak noktaları; 13 ana eklemde Honza cam1 için x∈[-0.139, 1.125], y∈[0.221, 0.875].)

**Koordinat kontrolü — sonuç: normalize (0–1), piksel değil.**
- 15 Ex1 videosunun hepsi `1080x1920`, döndürme 0° (dikey telefon videosu).
- İskelet `x·1080, y·1920` ile çizildiğinde videoya tam oturuyor (`iskelet_kontrol.png`).
- En-boy düzeltmesi: `x *= 1080/1920 = 0.5625` (= 9/16). CLAUDE.md'deki kullanılan değerle aynı; danışmanın kemik uzunluğundan tahmini 0,62'ydi.

**Tekrar sayıları** (`Segmentation.csv`, kamera başına):

| Egzersiz | DOGRU | ARM_FORWARD | BENT_ARM | ELEVATED_SHOULDER | HEAD_TO_SIDE | LOW_ABDUCTION | Toplam |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ex1 | 278 | 56 | 56 | 55 | 56 | 55 | 556 |

Ex1, kişi × birincil hata:

| kişi | DOGRU | ARM_FORWARD | BENT_ARM | ELEVATED_SHOULDER | HEAD_TO_SIDE | LOW_ABDUCTION |
| --- | --- | --- | --- | --- | --- | --- |
| Honza | 55 | 11 | 11 | 11 | 11 | 11 |
| Mima | 56 | 11 | 11 | 11 | 12 | 11 |
| Petra | 55 | 11 | 12 | 11 | 11 | 11 |
| Terka | 55 | 11 | 11 | 11 | 11 | 11 |
| Vasil | 57 | 12 | 11 | 11 | 11 | 11 |

Ex1 ek hatalar: `ERR_ELEVATED_SHOULDER` 17, `ERR_BENT_ARM` 3, `ERR_HEAD_TO_SIDE,ERR_BENT_ARM` 3, `ERR_HEAD_TO_SIDE` 3, `ERR_ELEVATED_SHOULDER,ERR_BENT_ARM` 2. (Ex7: 555, ex6: 554 tekrar; ayrıntı çıktı dosyasında.)

**`cekirdek.veri` ile yükleme:** zip'ten yüklenen Ex1 tekrar parçası 1668 (beklenen 556 × 3 = 1668) → **TUTUYOR**. Hata türüne göre (3 kamera dahil): DOGRU 834, ERR_ARM_FORWARD 168, ERR_BENT_ARM 168, ERR_ELEVATED_SHOULDER 165, ERR_HEAD_TO_SIDE 168, ERR_LOW_ABDUCTION 165. (video, kamera, yönelim) grubu: 165. İçinde boş (sıfır) kare olan tekrar parçası: 0.

**Eşdeğerlik testi:**
- **Danışmanın dosyasıyla (asıl test):** `rehab26_kucuk.npz` (23 815 861 bayt, 5 Kas 20:48) kullanıcının masaüstünde (`Desktop/Yeni klasör/`) bulundu ve `veri/rehab26_kucuk.npz` konumuna kopyalandı (`cmp` ile birebir aynı; orijinali yerinde). İçerik: 3333 tekrar parçası (ex1: 1668, ex7: 1665), hepsi 2d, 13 eklem, pay 10. Sonuç: **en büyük mutlak fark 0.000487566** (13 eklem, 4 sütun, 1668 Ex1 parçası; şekil ve başlangıç karesi hepsinde aynı) → `1 passed`.
- İlk ara kontrol (dosya bulunmadan önce): danışmanın kendi küçültme aracı (`araclar/rehab26_kucult.py --egzersiz 1`) orijinal zip'ten geçici klasörde çalıştırıldı (1668 tekrar parçası, 12.9 MB). Bu kopyaya karşı: **en büyük mutlak fark 0.000487566** (13 eklem, 4 sütun) → `1 passed`. Bu, bizim kesme/eşleştirme mantığımızın danışmanın aracıyla birebir aynı olduğunu gösterir; ama danışmanın gerçekte kullandığı dosyayla karşılaştırma değildir.

## Kabul ölçütü kontrolü
- [x] Veri tanıtım çıktısı ADIM_00'da var (özet yukarıda, tam hali `sonuclar/adim0/veri_tanit_cikti.txt`).
- [x] Ex1 tekrar sayıları `Segmentation.csv` ile tutuyor (1668 = 556 × 3).
- [x] Eşdeğerlik testi geçti: danışmanın dosyasıyla en büyük fark 0.000487566 ≤ 1e-3.
- [x] Koordinat biçimi netleşti: normalize (0–1); videolar 1080×1920; `x *= 9/16`.
- [x] Testler: `4 passed in 2.06s` (npz `veri/` altındayken, tüm testler).

## Kararlar ve sapmalar
- **33 eklem tutuluyor.** `cekirdek/veri.py` her tekrarı `(kare, 33, 4)` float64 döndürür. npz kaynağında tutulmayan 20 eklem NaN yapılır; böylece ölçüt kodu iki kaynakta da aynı MediaPipe indeksleriyle (12 = sağ omuz vb.) çalışır.
- **Boş kareler değiştirilmedi.** Bazı videolarda iskeletin bulunamadığı (tamamen sıfır) kareler var (ör. Vasil cam1: 66), ama hiçbiri Ex1 tekrar aralıklarına (±10 pay dahil) düşmüyor; bu yüzden şimdilik bir işlem gerekmiyor.
- **Kırpılan pay:** Ex1'de 2 tekrarın ilk karesi 10'dan küçük; bunların başındaki pay videonun başında kırpılıyor (danışmanın aracıyla aynı davranış).
- **Video ile iskelet kare sayısı bazı videolarda farklı.** Ör. ex1_Mima cam1: video 14027 kare (OpenCV ile tek tek sayıldı), iskelet 13724 kare; ex1_Honza cam2: video ≈24634, iskelet 24485. Mima cam1'in son tekrarında iskelet kare 0 hizasıyla kişinin üstüne oturuyor (303 kare kaydırınca oturmuyor), yani fazla video kareleri sonda görünüyor. Tek kareyle yapılan bir kontrol; Adım 2b'de (görsel kontrol aracı) birkaç videoda tekrar doğrulanmalı.
- **Kurulan paket sürümleri** (Adım 9'da rapor için): Python 3.11.9, numpy 2.4.6, pandas 3.1.1, scipy 1.17.1, mediapipe 1.2.2, opencv 5.0.0. `requirements.txt` yalnızca alt sınır veriyor; değiştirilmedi.
- **mediapipe 1.x notu:** Kurulan sürüm 1.2.2. Adım 6'daki `PoseLandmarker` (Tasks API) için sorun beklemiyorum, ama eski `mp.solutions.pose` API'si bu sürümde olmayabilir; uygulamada Tasks API kullanılacak (PLAN ile aynı).

## Açık sorular / danışmana notlar
- Video/iskelet kare sayısı farkının nedeni (değişken kare hızı mı, sonda işlenmemiş kareler mi) belli değil; Adım 2b'de bakılacak.
