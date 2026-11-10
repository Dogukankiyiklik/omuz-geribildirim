# deneyler/

Sistemin ölçüldüğü betikler. Her betik çekirdeği (`cekirdek/`) içe aktarır, veri setinde (ya da kendi kaydımızda) çalışır ve sonuçlarını `sonuclar/<ad>/` altına CSV olarak yazır. Her klasördeki `sonuclar.xlsx`, aynı tabloların Excel'de doğru açılan bir kopyasıdır. Bulguların özeti ve sayılar: [`docs/DENEYLER.md`](../docs/DENEYLER.md).

**Ortak kurallar:**
- Eşikler kişi bazlı birini-dışarıda-bırak ile ayarlanır: 4 kişide ayarlanır, 5. kişide sınanır, her kişi için tekrarlanır.
- Değerlendirilen tekrar hiçbir zaman kendi bandına girmez.
- Ana sonuç "önden + çapraz" görüşte verilir (|görüş| ≤ 60°); "tüm görüşler" ve "profil" ayrıca raporlanır.

## Hangi betik hangi soruyu cevaplıyor?

`docs/DENEYLER.md`'deki üç soruya göre:

| Betik | Soru | Ne ölçer | Süre* | Çıktı |
| --- | --- | --- | --- | --- |
| `deney1.py` | Soru 1 | Omuz silkmesini ayırma (AUC): dört omuz ölçüsü × üç puanlama (ham ölçü / genel bant / kişiye özel açı bandı). `docs/DENEYLER.md` Soru 1 tablolarının kaynağı; regresyon testi bu sonucu karşılaştırır. | ~20 sn | `sonuclar/deney1/` |
| `deney2.py` | Soru 2 | Hata türü kararı: doğru mu, değilse hangi hata? Uygulamanın yöntemi (kişiye özel açı bandı, yönlü; karar kuralı `cekirdek/hata_turu.py`). Karışıklık matrisleri, makro-F1, "ilk iki", görüş grupları, kişiler. | ~15 sn | `sonuclar/deney2/` |
| `deney3.py` | Soru 2 | Kararın Türkçe cümleye çevrilmesi: cümle doğru hatayı söylüyor mu, doğru tekrara gereksiz uyarı veriyor mu? Cümle uygulamanın kullandığı sağlam ölçüyle yazılır, sonra kararı bilmeyen bir okuyucuyla (`cekirdek/metin_cozumleyici.py`) geri okunur. Önce `deney2` çalışmış olmalı. | ~20 sn | `sonuclar/deney3/` |
| `kendi_kayit.py` | Soru 3 | Kendi çektiğimiz videoda (6 kalibrasyon + 21 test tekrarı) uygulamanın yığın moduyla aynı değerlendirme. | ~3 sn (önbellekten) | `sonuclar/kendi_kayit/` |

\* Süreler son yeniden üretimden alındı (`python -m deneyler.hepsi`, `sonuclar/hepsi/adimlar.csv`).

## Uygulamanın kullandığı eşikleri üretenler

Bunlar yeni bir yöntem değil, uygulamanın okuduğu `modeller/*.json` dosyalarını veri setinden hesaplar:

| Betik | Ne üretir |
| --- | --- |
| `tekrar_ayirma.py` | Canlı tekrar ayırıcıyı (`cekirdek/tekrar_ayirici.py`) veri setinin etiketli tekrarlarına karşı sınar: kaçı bulundu, sınırlar ne kadar örtüşüyor. Eşik üretmez, yalnızca ölçer. |
| `kamera_acisi.py` | Kamera açısı uyarısının eşiği → `modeller/kamera_esigi.json`. Çapraz görüşteki doğru tekrarların omuz genişliği / gövde boyu oranının 10. yüzdeliği. |
| `hiz_esigi.py` | "Hareketi biraz daha yavaş yap" notunun eşiği → `modeller/hiz_esigi.json`. Doğru tekrar sürelerinin 5. yüzdeliği. |

Uygulamanın karar kuralı dosyası `modeller/kural_ex1.json` ise `araclar/kural_disa_aktar.py` ile üretilir (Deney 2 ve 3'ten sonra).

## Yardımcılar

| Dosya | Görevi |
| --- | --- |
| `tablolar.py` | Deneylerin ortak tabloları: görüş grubu maskesi, AUC, kişi bazlı AUC. |
| `hepsi.py` | **Bütün deneyleri temiz bir kopyada yeniden çalıştırır** ve çıkan her CSV'yi kayıtlı sonuçla karşılaştırır. Son commit'in kopyasını açar (`git worktree`), veriyi yalnızca okur ve özeti `sonuclar/hepsi/ozet.md`'ye yazar. |

```bash
python -m deneyler.hepsi            # hepsi (~1,5 dk)
python -m deneyler.hepsi --hizli    # yalnızca deney1, kamera açısı, hız eşiği (~1 dk)
python -m deneyler.hepsi --temizle  # temiz kopyayı kaldırır
```

## Sıra

Bazı betikler öncekinin çıktısını okur. Baştan çalıştırma sırası (`hepsi.py` ile aynı):

`deney1` → `deney2` → `deney3` → `tekrar_ayirma` → `kamera_acisi` → `hiz_esigi` → `araclar.kural_disa_aktar` → `kendi_kayit`

Bütün betikler proje kökünden `python -m deneyler.<ad>` ile çalışır ve `veri/rehab26/` gerektirir. Kendi kayıt deneyi `veri/kendi_kayit/` ve `veri/ara/kendi_kayit/` (önbellek) ister; bunlar kişisel olduğu için depoda yoktur.
