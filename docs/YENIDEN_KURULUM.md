# Yeniden kurulum

Bu belge, başka bir öğrencinin sistemi sıfırdan kurup deneyleri yeniden üretebilmesi için yazıldı. Başlıklar hocanın rapor şablonundaki 7 başlığı izler. Komutlar Windows'ta Git Bash ya da PowerShell'de, proje kökünde çalıştırılır. Sonuçların özeti: [`sonuclar/OZET.md`](../sonuclar/OZET.md).

## 1. Ortam
- Python **3.11** (sınandığı sürüm 3.11.9). Paket sürümleri: [`docs/SURUMLER.md`](SURUMLER.md).
```bash
python -m venv .venv
.venv\Scripts\activate            # Git Bash: source .venv/Scripts/activate · macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
pytest -q                         # birkaç dakika; Deney 1 regresyonu dahil, hepsi geçmeli
```
- GPU gerekmez. `numba` DTW'yi hızlandırır; yoksa aynı sonuç daha yavaş çıkar.
- Uygulama için ek dosya: `modeller/pose_landmarker_full.task` (MediaPipe Pose Landmarker, Full). İlk çalıştırmada kendiliğinden indirilir.

## 2. Girdi hazırlığı
- **Veri seti:** REHAB26-ViewAngles, https://zenodo.org/records/23018128 (DOI 10.5281/zenodo.23018128, CC BY-NC 4.0). Dosyalar `veri/rehab26/` altına konur: `Segmentation.csv`, `Segmentation.txt`, `Error_types.csv`, `joint_names.txt`, `jointSequences-mediapipe.zip` (686 MB), `videos.zip` (8,4 GB; yalnızca görsel kontrol, galeri, siluet segmentasyonu ve uygulama denemesi için). Ayrıntı: `veri/README.md`.
- Zip'ler açılmaz; kod doğrudan zip'ten okur. `veri/` git'e girmez.
- Veriyi tanımak için: `python -m araclar.veri_tanit`.
- Kullanılan kısım: Ex1 (kolu yana kaldırma, sağ kol) ve doğrulama için Ex7 (omuz ekstansiyonu). Her tekrar `Segmentation.csv`'deki `first_frame…last_frame` aralığından, başına ve sonuna 10 kare pay eklenerek kesilir (`cekirdek/veri.py`).
- En-boy: 2B koordinatlar görüntüye göre 0–1; videolar 1080×1920 olduğu için açı ve mesafeden önce `x *= 9/16`. Uygulamada gerçek kare boyutu kullanılır.

## 3. Pose çıkarımı
- **Deneylerde:** veri setindeki hazır MediaPipe iskeletleri (v0.10.20, Full model; `_2d.npy`, `(kare, 33, 4)`). Deney 1–4 MediaPipe'ı çalıştırmaz.
- **Uygulamada, Adım 7'de ve 6b'de:** MediaPipe Tasks `PoseLandmarker` 1.2.2, `pose_landmarker_full`, VIDEO modu (`uygulama/poz.py`). Sürüm farkı aynı Honza karelerinde ölçüldü: kol açısı farkı medyan 0,92°, %95 3,09° (ADIM_06); YENI ölçütünün AUC'si iki sürümde 0,968 ve 0,969 (ADIM_06b).
- Zamansal yumuşatma yok (Karar 10; Deney 1c'de etkisiz çıktı).

## 4. Ölçüm ve hizalama
- Ölçütler (`cekirdek/ozellikler.py`): kol açısı (üst kolun aşağı dikeyle açısı), kulak–omuz dikey mesafesi / gövde boyu (YENI), baş–gövde açısı, kolun görünen boyu / gövde boyu, dirsek açısı. Uzunluklar dinlenme gövde boyuna bölünür.
- **Kişiye özel açı bandı** (`cekirdek/aci_bandi.py`): kişinin doğru (kalibrasyon) tekrarlarından, kol açısının 5°'lik kutularında, kaldırma ve indirme fazı ayrı, "normal aralık" μ ± τ (M39'dan). Yani "kol θ°'deyken bu kişinin omzu normalde nerede?".
- Zamansal hizalama: DTW, kol açısına göre (`cekirdek/hizalama.py`). Geometrik hizalama (bindirme): gövde merkezine öteleme, gövde boyuna ölçekleme, gövde eksenine döndürme (`cekirdek/bindirme.py`).
- Adil model (Karar 7): değerlendirilen tekrar modele girmez; doğru ve hatalı tekrarlar aynı sayıda doğru tekrardan kurulan modellerle değerlendirilir.

## 5. Hata hesabı
- Her ölçüt için bant dışı hata E; z ölçeği ve eşik T (`cekirdek/hata_turu.py`). Eşik ve ölçekleme kişi bazlı birini-dışarıda-bırak ile ayarlanır (4 kişide ayarla, 5.'de sına).
- En fazla 2 hata söylenir; 2. hata yalnızca onun z'si de T'yi geçerse.
- Az kaldırma: tepe açısının kalibrasyon tepelerinin medyanından sapması (Karar 17).
- Uygulamanın parametreleri: beş kişinin hepsiyle aynı prosedür → `modeller/kural_ex1.json` (`python -m araclar.kural_disa_aktar`, Karar 24).

## 6. Geri bildirim
- Kural tabanlı Türkçe cümle (`cekirdek/geribildirim.py`), iki katman (Karar 28): **hasta cümlesi** (kısa; ne oldu + ne yapmalı; sayı yalnızca 5°'ye yuvarlanmış derece) ve **uzman ayrıntısı** (ölçülü; "normalde X, sende Y").
- Cümleden hata listesini geri okuyan çıkarıcı: `cekirdek/metin_cozumleyici.py`.
- LLM yalnızca karşılaştırma için (Deney 4); ürün yöntemi değil.

## 7. Çıktı
### Deneyler
Her deney `sonuclar/<deney>/` altına CSV (ham), `ozet.csv` ve gerekirse PNG yazar. Hepsini temiz bir kopyada yeniden üretip kayıtlı sonuçlarla karşılaştırmak için:
```bash
python -m deneyler.hepsi          # ~1–1,5 sa; özet: sonuclar/hepsi/ozet.md
python -m deneyler.hepsi --hizli  # ~30 s; kurulum denemesi (Deney 1, kamera açısı, hız eşiği)
python -m deneyler.hepsi --temizle   # bittikten sonra temiz kopyayı kaldırır
```
`hepsi` son commit'in temiz bir kopyasını (git worktree) açar, `sonuclar/` olmadan bütün deneyleri sırayla çalıştırır ve her CSV'yi kayıtlı olanla karşılaştırır. Sonunda "aynı: N" ve "Yeniden üretim: N/N aynı" yazar.

**Önbellekten üretilen adımlar (Karar 53).** Üç adım ağ, video ya da saatler süren segmentasyon gerektirdiği için `hepsi` bunları yeniden çalıştırmaz, kayıtlı ara çıktılardan tabloları üretir. Önbellek yoksa adım "üretilmedi" olur. Baştan üretmek için:

| Adım | `hepsi`'nin kullandığı önbellek | Baştan üretmek için |
| --- | --- | --- |
| 6b (siluet) | `veri/ara/siluet/` (MediaPipe segmentasyonu, ~100 MB) | `python -m araclar.siluet_segment` (~1,5 sa, `videos.zip` gerekir), sonra `python -m deneyler.siluet` |
| Deney 4 (LLM) | `sonuclar/deney4/onbellek.jsonl` (Gemini yanıtları; git'e girmez) | Google AI Studio'dan ücretsiz bir API anahtarı → `.env` dosyasına `GEMINI_API_KEY=...`; `python -m deneyler.deney4_orneklem`, `python -m deneyler.deney4 hazirla`, `python -m deneyler.deney4 calistir --model gemini-3.5-flash-lite` (300 istek; ücretsiz katmanın günlük sınırına takılabilir, kesilirse aynı komut kaldığı yerden devam eder). Model zamanla kaldırılabilir; başka bir modelle sonuçlar farklı çıkar. İnsan etiketleri (`elle_kaldirma.xlsx`) depoda |
| Adım 7 (kendi kayıt) | `veri/ara/kendi_kayit/` (videonun MediaPipe noktaları) | Kendi videon gerekir (aşağıya bak); kişisel videolar depoya girmez |

### Uygulama
```bash
python -m uygulama.main --isim adin                                    # canlı kamera: 6 doğru tekrarla kalibrasyon + değerlendirme
python -m uygulama.main --profil profiller/adin.npz --video test.mp4   # kayıtlı profille video dosyası (pencere)
python -m uygulama.main --veri-seti ex1_Honza --kamera cam1 --yonelim 0  # veri setinden video, pencere modu
python -m uygulama.toplu --profil profiller/adin.npz --video test.mp4  # pencere açmadan, CSV
```
- Çıktılar: `oturumlar/<tarih>.csv` (tekrar başına karar, cümleler, z'ler) ve `profiller/<isim>.npz` (kalibrasyon). İkisi de git'e girmez.
- Ayrıntılı demo sırası ve sorun çıkarsa ne yapılacağı: [`docs/DEMO.md`](DEMO.md).

### Kendi videonla kullanım (Adım 7 protokolü)
1. Kontrol listesi: [`docs/CEKIM_LISTESI.md`](CEKIM_LISTESI.md). Telefon sabit, göğüs hizasında, 2–2,5 m uzakta; kişi önden (en fazla 30° çapraz); baştan kalçaya ve yukarı kalkan sağ kol kadrajda; sade arka plan, ışık önden; 30 FPS.
2. Çekim sırasında suflör sayfası: [`docs/cekim_suflor.html`](cekim_suflor.html) (tarayıcıda aç; hareketi sesli okur, kaldır/indir anlarında bip çalar). Bütün çekimde ekrandaki aynı noktaya bak.
3. İki video: `kalibrasyon` (6 doğru tekrar) ve `test` (sırası önceden üretilmiş tekrarlar). Sıra ve etiket şablonu: `python -m deneyler.kendi_kayit --sablon veri/kendi_kayit/kisiN/etiketler.csv --tohum N`.
4. Değerlendirme (MediaPipe ilk çalıştırmada birkaç dakika, sonra önbellekten):
```bash
python -m deneyler.kendi_kayit --kisi kisi1 --kalibrasyon veri/kendi_kayit/kisi1/kalibrasyon.MOV --test veri/kendi_kayit/kisi1/test.MOV --etiketler veri/kendi_kayit/kisi1/etiketler.csv
```
   Çıktı: `sonuclar/kendi_kayit/<kisi>/` (`ozet.csv`, `karisiklik.csv`, `cumle_etiket.csv`). iPhone `.MOV` dosyaları dönüştürülmeden okunur.
