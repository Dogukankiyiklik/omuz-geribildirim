# modeller/

Uygulamanın çalışırken okuduğu dosyalar. Burada makine öğrenmesiyle eğitilmiş bir model yok, yalnızca MediaPipe'ın hazır poz modeli var. JSON dosyaları veri setinden hesaplanmış **sabit eşikler** ve **karar kuralıdır**. Her biri bir betikle yeniden üretilir; `python -m deneyler.hepsi` yeniden üretilen dosyanın kayıtlıyla aynı olduğunu denetler.

| Dosya | Ne | Üreten | Okuyan |
| --- | --- | --- | --- |
| `kural_ex1.json` | Hata türü karar kuralı: hangi hata hangi ölçüyle bakılır, yönler, ölçekleme (medyan, IQR), eşik T, şiddet eşikleri. Beş kişinin önden + çapraz tekrarlarıyla kuruldu. | `python -m araclar.kural_disa_aktar` | `uygulama/oturum.py` → `cekirdek/kural_dosyasi.py` |
| `kamera_esigi.json` | Kamera açısı uyarısının eşiği: dinlenmedeki omuz genişliği / gövde boyu oranı bunun altına düşerse "kameraya daha önden dur" uyarısı verilir. | `python -m deneyler.kamera_acisi` | `cekirdek/kamera_acisi.py` |
| `hiz_esigi.json` | Hız notunun eşiği (saniye): tekrar bundan kısa sürerse "hareketi biraz daha yavaş yap" notu çıkar. | `python -m deneyler.hiz_esigi` | `cekirdek/bilgi_notlari.py` |
| `pose_landmarker_full.task` | MediaPipe'ın poz modeli ("Full"; veri seti de bu modelle üretildi). Büyük olduğu için **depoya girmez**; uygulama ilk çalıştırmada Google'ın sunucusundan indirir. | MediaPipe (hazır) | `uygulama/poz.py` |

JSON'lardaki `bilgi` ve `tarih` alanları dosyanın ne zaman ve hangi commit'le üretildiğini gösterir. Bu alanlar karara girmez; yeniden üretim karşılaştırmasında da yok sayılır.

Yöntem donduruldu: bu dosyalar elle değiştirilmez. Bir eşik değişecekse üreten betik yeniden çalıştırılır.
