# cekirdek/

Sistemin bütün hesabı burada: ölçüler, kişiye özel bant, hata türü kararı, Türkçe cümle ve bindirme. Uygulama (`uygulama/`) ve deneyler (`deneyler/`) bu kodu **içe aktarır, kopyalamaz**. Böylece uygulamanın verdiği karar, deneyde ölçülen kararla aynı koddan gelir.

## Bir tekrar nasıl değerlendirilir?

Kişinin 6 doğru tekrarı (kalibrasyon) ve yeni bir tekrarı olduğunu düşünelim:

1. **İskelet → ölçüler** (`ozellikler.py`). MediaPipe'ın 33 eklem noktasından her kare için kol açısı ve beş duruş ölçüsü hesaplanır: kulak–omuz mesafesi (`YENI`, silkme için), baş eğikliği (`bas`), kolun öne kaçması (`on_kacma` ya da `kol_boyu`) ve dirsek açısı (`dirsek`). Uzunluklar gövde boyuna bölünür; böylece kişinin kameraya uzaklığı sonucu etkilemez.
2. **Kalibrasyon → açı bandı** (`aci_bandi.py`). Kol açısı 5°'lik kutulara ayrılır: 0–5°, 5–10°, … Kaldırma ve indirme ayrı tutulur. Her kutu için kişinin doğru tekrarlarından o ölçünün ortalaması (**μ**) ve normal aralığın yarı genişliği (**τ**) hesaplanır. Bu bandın sorduğu soru şudur: *"Kol θ derecedeyken bu kişinin omzu normalde nerede?"*
3. **Yeni tekrar → bant hatası E** (`aci_bandi.py`, `bant.py`). Yeni tekrarın her karesi, kolun o anki açısının kutusuyla karşılaştırılır. Bant içindeyse hata 0'dır, dışına taştıkça 1'e kadar artar. E, karelerin ortalamasıdır.
4. **E → karar** (`hata_turu.py`). Her hata türünün puanı, eğitim kişilerinin doğru tekrarlarına göre ölçeklenir (**z**). En büyük z bir eşiğin (**T**) altındaysa tekrar DOĞRU sayılır. Değilse en büyük z'nin hatası söylenir; ikinci hata da T'yi geçerse o da eklenir. Yetersiz kaldırma bantla değil, tepe kol açısının kalibrasyondakinden ne kadar düşük kaldığıyla ölçülür.
5. **Karar → cümle** (`geribildirim.py`). Söylenecek her hata için bir "sapma kodu" çıkarılır: hangi fazda (kaldırırken, en üstteyken, indirirken), ne yönde, ne kadar. Bu koddan iki cümle yazılır:
   - **hasta cümlesi:** kısa, 5°'ye yuvarlanmış derece ve ne yapılacağı;
   - **uzman ayrıntısı:** "normalde X, sende Y" biçiminde.

   Doğru tekrarda olumlu bir cümle yazılır.
6. **Bindirme** (`bindirme.py`, `hizalama.py`). Kişinin tipik kalibrasyon tekrarı yeni tekrarın üstüne çizilir. Zamanda **DTW** ile hizalanır, geometride öteleme, ölçek ve döndürme ile çakıştırılır. DTW (dinamik zaman bükme), farklı hızda yapılmış iki hareketi kare kare eşleştirir. Puanlamada DTW **yoktur**; yalnızca bu çizim için kullanılır.

Uygulama 1–5. adımları tek çağrıyla yapar: `degerlendirici.py` içinde `Profil` (kalibrasyon) ve `degerlendir()` (bir tekrar).

## Dosyalar

### Veri ve geometri

| Dosya | Görevi |
| --- | --- |
| `veri.py` | REHAB26 veri setini okur: `Segmentation.csv` (etiketler) ve zip içindeki iskeletler. Her tekrar bir `Tekrar` nesnesi olur. Görüş açısını (`gorus_acisi`) ve videoyu zipten çıkarmayı (`video_cikar`) da sağlar. En-boy sabiti `EN_BOY = 9/16` buradadır. |
| `geometri.py` | İki yardımcı: en-boy düzeltmeli nokta (`nokta`) ve iki vektör arasındaki açı (`aci`). |
| `ozellikler.py` | Kare başına ölçüler. Her ölçü `@olcut("AD")` ile `OLCUTLER` sözlüğüne kaydedilir. `DENEY1_OLCUTLERI` omuz ölçülerini (silkme tespiti), `DENEY2_OLCUTLERI` beş duruş ölçüsünü (hata türü) toplar. `omuz_egim` yalnızca cümlede derece vermek için kullanılır, tespite girmez. |

### Bant ve karar

| Dosya | Görevi |
| --- | --- |
| `aci_bandi.py` | **Kullanılan yöntem.** Kol açısına koşullu kişiye özel bant: `aci_bandi_modeli` bandı kurar, `aci_bandi_hatasi` bir tekrarın E'sini verir. |
| `bant.py` | Zamana göre bant (M39 yöntemi). Tekrarlar DTW ile hizalanır, her an için μ ± τ hesaplanır. Deneylerde açı bandıyla karşılaştırmak için duruyor. Kare hatası formülü `kare_hatasi` iki bant için de ortak. |
| `hizalama.py` | DTW (`dtw_yol`, `hizala`). numba kuruluysa hızlı çalışır, değilse saf Python ile aynı sonucu verir. |
| `adil_model.py` | Deney protokolü: hatalı bir tekrar da doğru tekrarlar gibi (n−1) tekrarlık modellerle değerlendirilir ve sonuçların ortalaması alınır. Uygulamada kullanılmaz. |
| `hata_turu.py` | Karar kuralı. `KararKurali` sınıfı z'yi ve kararı hesaplar, `esik_sec` eğitim kişilerinde T'yi seçer. Az kaldırmanın iki sürümü var: `"ilk"` kullanılan yöntem, `"revize"` denenip elenen sürüm (yalnızca karşılaştırma için). |
| `degerlendirici.py` | Tek bir tekrarın bütün yolu (puan → karar → sapma kodu → cümle); Deney 2, Deney 3 ve uygulama ortak kullanır. |
| `kural_dosyasi.py` | Uygulamanın karar kuralını JSON'a yazar ve okur (`modeller/kural_ex1.json`). Dosyayı `araclar/kural_disa_aktar.py` üretir. |

### Geri bildirim

| Dosya | Görevi |
| --- | --- |
| `geribildirim.py` | Sapma kodu (`SapmaKodu`), şiddet (hafif, belirgin, çok belirgin), hasta cümlesi ve uzman ayrıntısı (`iki_katman`). Türkçe sayı ekleri de burada; örneğin "%30'u", "%30'a". |
| `metin_cozumleyici.py` | Bir Türkçe cümlede hangi hataların söylendiğini anahtar kelimelerle bulur. Deney 3, üretilen cümlenin doğru hatayı söyleyip söylemediğini bununla ölçer. |
| `etiketler.py` | Hata kodlarının ve ölçülerin Türkçe adları (şekiller ve videolar için). |

### Uygulamaya yardımcı olanlar

| Dosya | Görevi |
| --- | --- |
| `tekrar_ayirici.py` | Canlı görüntüde tekrarları ayırır. Kol 30°'yi geçince tekrar başlar, 20°'nin altına inince biter. En az 60° ve 0,8 sn şartı var. `eslestir`, bulunan tekrarları veri setinin etiketleriyle eşleştirir. |
| `kamera_acisi.py` | Kişi kameraya fazla yan dönmüşse uyarı verir: dinlenmedeki omuz genişliği / gövde boyu oranı eşiğin altına düşerse. Eşik `modeller/kamera_esigi.json` dosyasında. |
| `bilgi_notlari.py` | Karara girmeyen notlar: hareket çok hızlıysa, sol kol da kalktıysa ya da kamera açısı değiştiyse. |
| `konsol.py` | Çıktı yardımcıları: Windows konsolunda UTF-8 ve sonuç tablolarını CSV ile Excel'e yazma. |

## Değişiklik yaparken

- Yöntem donduruldu: eşikler, puanlama ve karar kuralı değiştirilmez.
- Çekirdekte bir değişiklikten sonra `pytest -q` çalışmalı. Regresyon testleri (`testler/test_deney1_regresyon.py`, `testler/test_deney2_regresyon.py`) sonuçların değişmediğini denetler. Bu testler için veri setinin `veri/rehab26/` altında olması gerekir; yoksa atlanırlar.
