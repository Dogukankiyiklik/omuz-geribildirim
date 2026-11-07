# TASLAK — Yeniden kurulum (Karar 37; sayılar 13 Kasım dondurmasında kesinleşir)

Bu belge, başka bir öğrencinin sistemi sıfırdan kurup deneyleri yeniden üretebilmesi için yazıldı. Başlıklar hocanın rapor şablonundaki 7 başlığı izler. Komutlar Windows'ta Git Bash ya da PowerShell'de, proje kökünde çalıştırılır.

## 1. Ortam
- Python **3.11** (sınandığı sürüm 3.11.9). Paket sürümleri: `docs/SURUMLER.md`.
```bash
python -m venv .venv
.venv\Scripts\activate            # Git Bash: source .venv/Scripts/activate
pip install -r requirements.txt
pytest -q                         # ~1,5 dk; Deney 1 regresyonu dahil, hepsi geçmeli
```
- GPU gerekmez. `numba` DTW'yi hızlandırır; yoksa aynı sonuç daha yavaş çıkar.
- Uygulama için ek dosya: `modeller/pose_landmarker_full.task` (MediaPipe Pose Landmarker, Full). İlk çalıştırmada kendiliğinden indirilir.

## 2. Girdi hazırlığı
- Veri: REHAB26-ViewAngles, https://zenodo.org/records/23018128 (CC BY-NC 4.0). Dosyalar `veri/rehab26/` altına konur: `Segmentation.csv`, `Segmentation.txt`, `Error_types.csv`, `joint_names.txt`, `jointSequences-mediapipe.zip` (686 MB), `videos.zip` (8,4 GB; yalnızca görsel kontrol, galeri ve uygulama denemesi için). Ayrıntı: `veri/README.md`.
- Zip'ler açılmaz; kod doğrudan zip'ten okur. `veri/` git'e girmez.
- Veriyi tanımak için: `python -m araclar.veri_tanit`.
- Kullanılan kısım: Ex1 (kolu yana kaldırma, sağ kol). Her tekrar `Segmentation.csv`'deki `first_frame…last_frame` aralığından, başına ve sonuna 10 kare pay eklenerek kesilir (`cekirdek/veri.py`). Birim: (satır, kamera).
- En-boy: 2B koordinatlar görüntüye göre 0–1; videolar 1080×1920 olduğu için açı ve mesafeden önce `x *= 9/16`. Uygulamada gerçek kare boyutu kullanılır.

## 3. Pose çıkarımı
- Deneylerde: veri setindeki hazır MediaPipe iskeletleri (v0.10.20, Full model; `_2d.npy`, `(kare, 33, 4)`).
- Uygulamada: MediaPipe Tasks `PoseLandmarker` 1.2.2, `pose_landmarker_full`, VIDEO modu (`uygulama/poz.py`). Sürüm farkı aynı Honza karelerinde ölçüldü (kol açısı farkı medyan 0,92°, %95 3,09°; ADIM_06).
- Zamansal yumuşatma yok (Karar 10; Deney 1c'de etkisiz çıktı).

## 4. Ölçüm ve hizalama
- Ölçütler (`cekirdek/ozellikler.py`): kol açısı (üst kolun aşağı dikeyle açısı), kulak–omuz dikey mesafesi / gövde boyu (YENI), baş–gövde açısı, kolun gövde düzlemindeki açısı, kolun görünen boyu / gövde boyu, dirsek açısı. Uzunluklar dinlenme gövde boyuna bölünür.
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
- Deneyler: `sonuclar/<deney>/` altında CSV (ham), `ozet.csv` ve PNG. Hepsini temiz bir kopyada yeniden üretip kayıtlı sonuçlarla karşılaştırmak için:
```bash
python -m deneyler.hepsi          # ~45–60 dk; özet: sonuclar/hepsi/ozet.md
python -m deneyler.hepsi --hizli  # ~30 s; kurulum denemesi
```
- Uygulama:
```bash
python -m uygulama.main --isim adim                                   # canlı kamera: kalibrasyon + değerlendirme
python -m uygulama.main --veri-seti ex1_Honza --kamera cam1 --yonelim 0   # veri setinden video, pencere modu
python -m uygulama.toplu --profil profiller/adim.npz --video test.mp4     # pencere açmadan, CSV
```
- Uygulamanın çıktıları: `oturumlar/<tarih>.csv` (tekrar başına karar, cümleler, z'ler) ve `profiller/<isim>.npz` (kalibrasyon).
