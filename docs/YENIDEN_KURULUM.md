# Yeniden kurulum

Bu belge, başka birinin sistemi sıfırdan kurup deneyleri yeniden üretebilmesi için yazıldı. Yöntemin anlatımı [`SISTEM.md`](SISTEM.md)'de, sonuçların özeti [`DENEYLER.md`](DENEYLER.md)'de. Komutlar proje kökünde çalıştırılır; Windows'ta Git Bash ya da PowerShell olabilir.

## 1. Ortam

Python **3.11** gerekir (sınandığı sürüm 3.11.9). Tam paket listesi [`SURUMLER.md`](SURUMLER.md)'de.

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows; macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
pytest -q                         # ~1 dk; veri yoksa veri gerektiren testler atlanır
```

- GPU gerekmez.
- `numba` DTW'yi hızlandırır; yoksa aynı sonuç daha yavaş çıkar.
- Uygulama MediaPipe modelini (`modeller/pose_landmarker_full.task`) ilk çalıştırmada kendiliğinden indirir.

## 2. Veri

- **Veri seti:** REHAB26-ViewAngles, https://zenodo.org/records/23018128 (DOI 10.5281/zenodo.23018128, CC BY-NC 4.0).
- **Nereye:** dosyalar `veri/rehab26/` altına konur. Hangi dosyanın ne olduğu [`veri/README.md`](../veri/README.md)'de. `videos.zip` (8,4 GB) yalnızca video gösteren işler için gerekir: görsel kontrol, galeriler, sunum şekilleri ve uygulamanın `--veri-seti` modu.
- **Zip'ler:** açılmaz; kod doğrudan zip'ten okur. `veri/` git'e girmez.
- **Deneyler MediaPipe çalıştırmaz:** veri setindeki hazır iskeletleri kullanırlar (MediaPipe 0.10.20). Uygulama ise MediaPipe 1.2.2 kullanır; aradaki fark [`SURUMLER.md`](SURUMLER.md)'de.

## 3. Testler ve deneylerin yeniden üretimi

Önce `pytest -q`. Veri yerindeyken bütün testler geçmeli (1 tanesi bilerek `xfailed`; [`testler/README.md`](../testler/README.md)).

Bütün deneyleri temiz bir kopyada yeniden üretip kayıtlı sonuçlarla karşılaştırmak için:

```bash
python -m deneyler.hepsi            # ~1,5 dk; özet: sonuclar/hepsi/ozet.md
python -m deneyler.hepsi --hizli    # ~1 dk; kurulum denemesi (Deney 1, kamera açısı, hız eşiği)
python -m deneyler.hepsi --temizle  # bittikten sonra temiz kopyayı kaldırır
```

`hepsi` son commit'in temiz bir kopyasını (git worktree) açar, `sonuclar/` olmadan bütün deneyleri sırayla çalıştırır ve her CSV'yi kayıtlı olanla karşılaştırır. Sonunda "Yeniden üretim: N/N aynı" yazar. Son çalıştırmanın raporu `sonuclar/hepsi/ozet.md`'de.

Tek bir deneyi çalıştırıp sonucun değişmediğini görmek için:

```bash
python -m deneyler.deney1
git status sonuclar/deney1          # CSV'ler "değişti" görünmüyorsa sonuç birebir aynı
```

Betiklerin sırası ve her birinin ne ürettiği [`deneyler/README.md`](../deneyler/README.md)'de.

**Kendi kayıt adımı** videonun MediaPipe noktalarını `veri/ara/kendi_kayit/` önbelleğinden okur. Kişisel videolar ve bu önbellek depoda olmadığı için bu adım başka bir bilgisayarda "üretilmedi" olur.

## 4. Uygulama

```bash
python -m uygulama.main --isim adin                                      # canlı kamera: 6 doğru tekrarla kalibrasyon + değerlendirme
python -m uygulama.main --profil profiller/adin.npz --video test.mp4     # kayıtlı profille video dosyası
python -m uygulama.main --veri-seti ex1_Honza --kamera cam1 --yonelim 0  # veri setinden video
python -m uygulama.toplu --profil profiller/adin.npz --video test.mp4    # pencere açmadan, CSV
```

Çıktılar `oturumlar/<tarih>.csv` ve `profiller/<isim>.npz` dosyalarıdır; ikisi de git'e girmez. Ayrıntı: [`uygulama/README.md`](../uygulama/README.md).

## 5. Kendi videonla deneme

1. **Çekim:** telefon sabit, göğüs hizasında, 2–2,5 m uzakta. Kişi önden ya da en fazla 30° çapraz durur. Baştan kalçaya kadar ve yukarı kalkan sağ kol kadrajda olmalı. Sade arka plan, ışık önden, 30 FPS. Bütün çekimde aynı noktaya bakılır. Ayrıntılı kontrol listesi: [`arsiv/docs/CEKIM_LISTESI.md`](../arsiv/docs/CEKIM_LISTESI.md).
2. **İki video:** `kalibrasyon` (6 doğru tekrar) ve `test` (sırası önceden üretilmiş tekrarlar). Sıra ve etiket şablonu:
   ```bash
   python -m deneyler.kendi_kayit --sablon veri/kendi_kayit/kisiN/etiketler.csv --tohum N
   ```
3. **Değerlendirme:** MediaPipe ilk çalıştırmada birkaç dakika sürer, sonraki çalıştırmalar önbellekten gelir.
   ```bash
   python -m deneyler.kendi_kayit --kisi kisi1 --kalibrasyon veri/kendi_kayit/kisi1/kalibrasyon.MOV \
       --test veri/kendi_kayit/kisi1/test.MOV --etiketler veri/kendi_kayit/kisi1/etiketler.csv
   ```
   Çıktı `sonuclar/kendi_kayit/<kisi>/` klasörüne yazılır (`ozet.csv`, `karisiklik.csv`, `cumle_etiket.csv`). iPhone `.MOV` dosyaları dönüştürülmeden okunur.
