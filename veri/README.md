# veri/

## Ana veri: REHAB26-ViewAngles (Zenodo)

https://zenodo.org/records/23018128 — lisans CC BY-NC 4.0. Tüm dosyaları `veri/rehab26/` klasörüne indir:

| Dosya | Boyut | Ne içeriyor |
| --- | --- | --- |
| `Segmentation.csv` | 83 kB | 1665 tekrarın her biri için bir satır: hangi video, hangi kişi, kaçıncı tekrar, başlangıç ve bitiş karesi, kişinin kameraya göre yönelimi, doğru/yanlış, birincil hata, ek hatalar. **Cevap anahtarı budur.** |
| `Segmentation.txt` | 2 kB | `Segmentation.csv` sütunlarının açıklaması. |
| `Error_types.csv` | 1 kB | Hata kodları ve açıklamaları, örneğin `ERR_ELEVATED_SHOULDER` = "egzersiz yapan omzun yükselmesi". |
| `joint_names.txt` | 0,5 kB | MediaPipe'ın 33 eklem noktasının adları; sırası `.npy` dosyalarındaki sırayla aynı. |
| `jointSequences-mediapipe.zip` | 686 MB | Yazarların her videoya MediaPipe çalıştırarak çıkardığı iskeletler. Her video için bir `_2d.npy` (görüntü koordinatı) ve bir `_3d.npy` (metre cinsinden tahmini 3B) dosyası. |
| `videos.zip` | 8,4 GB | Orijinal videolar; 3 egzersiz × 5 kişi × 3 kamera, 30 FPS. Görsel kontrol için gerekli. |

Zip'leri açmak zorunlu değil; kod doğrudan zip'ten okuyabilir.

## Yardımcı dosya

`rehab26_kucuk.npz`: Veri setinin küçültülmüş kopyası (yalnızca tekrar kareleri, 13 eklem, 2B, float16). Silkme tespitinin ilk sonuçları (`referans/beklenen_deney1_ozet.csv`) bu dosyadan üretildi. Varsa `veri/` klasörüne konur; test, aynı sonucun hem bu dosyadan hem orijinal zip'ten yeniden üretildiğini kontrol eder. Yoksa ilgili test atlanır.

## Kendi kayıt

`kendi_kayit/kisi1/`: Projenin kendi çekimi (kalibrasyon ve test videosu, tekrar etiketleri). Kişisel görüntü olduğu için depoya girmez.

`ara/`: Programların oluşturduğu ara dosyalar. `ara/videolar/` veri setinden çıkarılmış videolar, `ara/kendi_kayit/` kendi kaydın MediaPipe iskelet noktaları (önbellek). Depoya girmez.
