# sonuclar/

Deneylerin çıktıları. Belgelerdeki (`docs/DENEYLER.md`, rapor, sunum) her sayı buradaki bir dosyadan kopyalanır. Klasörlerin adı onu üreten betiğin adıdır; betikler [`deneyler/README.md`](../deneyler/README.md)'de anlatılıyor.

- **CSV** dosyaları asıl kayıttır. UTF-8 ile yazılır ve ondalık ayırıcı noktadır.
- **`sonuclar.xlsx`** aynı tabloların Excel kopyasıdır. Türkçe Excel, CSV'deki ondalık noktayı binlik ayırıcı sanabildiği için tablolara Excel'de bakarken bu dosyayı açın.
- **Videolar** (`.mp4`) yeniden üretilebilir ve büyük oldukları için depoya girmez. Bunlar `deney1/galeri/` (görsel kontrol aracının `--galeri` çıktısı) ve `sunum/demo_*.mp4` gibi dosyalardır.

Bütün CSV'lerin bugünkü koddan aynen yeniden üretildiği `python -m deneyler.hepsi` ile denetlenir.

## Klasörler

| Klasör | Ne var | En önemli dosya |
| --- | --- | --- |
| `deney1/` | Omuz silkmesini ayırma: dört omuz ölçüsü × üç puanlama (`ham`, `genel`, `kisiye_ozel`) | `ozet.csv` (AUC'ler; `docs/DENEYLER.md` Soru 1; regresyon testi bunu `referans/beklenen_deney1_ozet.csv` ile karşılaştırır), `kisi_auc.csv` (kişi başına AUC) |
| `deney2/` | Hata türü kararı (açı bandı, yönlü) | `ozet.csv` (makro-F1, hatalılarda tür doğru, gereksiz uyarı…), `ilk_iki.csv`, `tahminler.csv` (her tekrarın kararı), `puanlar.csv` (her tekrarın ölçü puanları; Deney 3 ve kural dosyası bunu okur), `karisiklik_*` (karışıklık matrisleri), `esikler.csv` (her test kişisi için seçilen T) |
| `deney3/` | Kararın Türkçe cümleye çevrilmesi | `ozet.csv`, `cumleler.csv` (her tekrarın cümlesi), `ornek_cumleler_saglam.md` (okunabilir örnekler), `siddet_esikleri.csv` |
| `kendi_kayit/` | Kendi çektiğimiz videoda değerlendirme (kişi 1) | `kisi1/ozet.csv` (`docs/DENEYLER.md` Soru 3), `kisi1/cumle_etiket.csv` (her tekrarın etiketi ve cümlesi) |
| `tekrar_ayirma/` | Otomatik tekrar ayırmanın veri setinin etiketlerine karşı sınanması | `ozet.csv` |
| `kamera_acisi/` | Kamera açısı uyarısının eşiği (`modeller/kamera_esigi.json`) | `dagilim.csv` |
| `hiz_esigi/` | Hız notunun eşiği (`modeller/hiz_esigi.json`) | `ozet.csv` |
| `kural_disa_aktar/` | Uygulamanın kural dosyasının (`modeller/kural_ex1.json`) deneydeki kurallarla karşılaştırması | `loso_karsilastirma.csv` |
| `uygulama_saglik/` | Uygulamanın MediaPipe sürümü (1.2.2) ile veri setininki (0.10.20) aynı videoda ne kadar farklı (`python -m uygulama.toplu --veri-seti ex1_Honza`) | `ex1_Honza_cam1_o0_poz_farki.csv` |
| `sunum/` | Sunum şekilleri (`deneyler/sunum_sekilleri.py`). `4b_*` ve `5b_*` kişisel görüntü içerdiği için depoya girmez. | `1_problem.png` … `5_bindirme.png` |
| `gorsel_kontrol/` | Görsel kontrol aracının videoları (`araclar/gorsel_kontrol.py`); yalnızca yerelde | – |

`hepsi/` son yeniden üretimin raporudur (`python -m deneyler.hepsi` her çalıştırmada yeniden yazar): `ozet.md`, adım süreleri (`adimlar.csv`) ve dosya dosya karşılaştırma (`regresyon.csv`).

## Kısaltmalar

- **yönlü bant:** yalnızca hatanın beklenen yönündeki sapmayı sayar (örneğin omuz yukarı). Deney 2 ve uygulama yönlü bant kullanır. Kural dosyasındaki `"sistem": "v2_yonlu"` bu demektir (v2 = açı bandı).
- **oc / tum:** önden + çapraz görüş ve tüm görüşler.
- **kati / esnek:** katı değerlendirmede yalnızca birincil hata doğru sayılır, esnekte ek hatalar da doğru sayılır.
- **saglam:** uygulamanın kullandığı sağlam ölçü. Cümledeki ölçü tek kare yerine birkaç karenin medyanından alınır.
