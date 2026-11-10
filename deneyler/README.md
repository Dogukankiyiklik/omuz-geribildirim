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
| `deney1.py` | Soru 1 | İlk sürüm: zaman bandı (M39) ile ham ölçü, beş omuz ölçüsünde silkme tespiti (AUC). Regresyon testinin karşılaştırdığı sonuç budur. | ~15 sn | `sonuclar/deney1/` |
| `deney1_v2.py` | Soru 1 | Yöntem düzeltmelerinin adım adım etkisi: v1 (Deney 1 aynen) → v1a (pay hariç) → v1b (çoklu referans) → v2 (**açı bandı**). | ~2 dk | `sonuclar/deney1_v2/` |
| `deney1b.py` | Soru 1 | Kalibrasyon kişiye özel olmak zorunda mı? Bant yok / genel bant (başkalarının tekrarları) / kişiye özel bant. `docs/DENEYLER.md` Soru 1 tablosunun kaynağı. | ~2 dk | `sonuclar/deney1b/` |
| `deney2.py` | Soru 2 | Hata türü kararı: doğru mu, değilse hangi hata? Karışıklık matrisleri, makro-F1, "ilk iki", görüş grupları, kişiler. `--kaldirma-surumu revize` denenip elenen sürümü `sonuclar/deney2_revize/`'ye yazar. | ~2 dk | `sonuclar/deney2/` |
| `deney3.py` | Soru 2 | Kararın Türkçe cümleye çevrilmesi: cümle doğru hatayı söylüyor mu, doğru tekrara gereksiz uyarı veriyor mu? `--olcu-surumu saglam` uygulamanın kullandığı sağlam ölçü çıktılarını ekler. Önce `deney2` çalışmış olmalı. | ~1 dk | `sonuclar/deney3/` |
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

## Şekiller ve galeriler

| Betik | Ne üretir |
| --- | --- |
| `sekiller.py` | Deney 1 şekilleri: `auc.png`, `bant_ornegi.png`, `dagilim.png`. |
| `deney1_v2_sekiller.py` | Deney 1 v2 şekilleri: koşullara göre AUC ve aynı tekrarın zaman bandı ile açı bandında yan yana görünümü (`ornekler/`). |
| `deney2_galeri.py` | Deney 2'nin en sık karıştırdığı ve kaçırdığı tekrarlardan videolar ve `liste.md` (`sonuclar/deney2/galeri/`). |
| `sunum_sekilleri.py` | Sunumun şekilleri (`sonuclar/sunum/`). Yalnızca kayıtlı sonuç dosyalarından okur; 4 ve 5 numaralı şekiller ile demo videosu, uygulamanın kendi çizim koduyla pencere açmadan üretilir. `--kendi-kayit` kişisel kayıttan 4b, 5b ve `demo_kisi1.mp4` üretir (bunlar git'e girmez). |

## Yardımcılar

| Dosya | Görevi |
| --- | --- |
| `tablolar.py` | Deneylerin ortak tabloları: görüş grubu maskesi, AUC, kişi bazlı AUC, bootstrap güven aralığı. |
| `hepsi.py` | **Bütün deneyleri temiz bir kopyada yeniden çalıştırır** ve çıkan her CSV'yi kayıtlı sonuçla karşılaştırır. Son commit'in kopyasını açar (`git worktree`), veriyi yalnızca okur ve özeti `sonuclar/hepsi/ozet.md`'ye yazar. |

```bash
python -m deneyler.hepsi            # hepsi (~8 dk)
python -m deneyler.hepsi --hizli    # yalnızca deney1, kamera açısı, hız eşiği (~1 dk)
python -m deneyler.hepsi --temizle  # temiz kopyayı kaldırır
```

## Sıra

Bazı betikler öncekinin çıktısını okur. Baştan çalıştırma sırası (`hepsi.py` ile aynı):

`deney1` → `deney1_v2` → `deney1b` → `deney2` → `deney3` (+ `--olcu-surumu saglam`) → `tekrar_ayirma` → `kamera_acisi` → `hiz_esigi` → `araclar.kural_disa_aktar` → `kendi_kayit`

Bütün betikler proje kökünden `python -m deneyler.<ad>` ile çalışır ve `veri/rehab26/` gerektirir. Kendi kayıt deneyi `veri/kendi_kayit/` ve `veri/ara/kendi_kayit/` (önbellek) ister; bunlar kişisel olduğu için depoda yoktur.
