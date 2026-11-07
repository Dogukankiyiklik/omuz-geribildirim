# ADIM 06b — Omuz bölgesi siluet ölçütü (`SILUET`)

**Tarih:** 2026-11-07 (önceden kayıt)
**Durum:** Devam ediyor — önceden kayıt yazıldı; kod, segmentasyon çalıştırması ve sonuçlar bekleniyor.

> Bu dosyanın "Önceden belirlenenler" bölümü **kod yazılmadan önce** commit'lendi (Güncelleme 11, Karar 48).
> Sonuçlar geldikten sonra bu bölüm değiştirilmez; sonuçlar ve sapmalar aşağıya eklenir.

## Önceden belirlenenler (Karar 48, madde 1–8; danışman)

1. **Kapsam:** Ex1, önden + çapraz görüş (|görüş| ≤ 60°), bütün tekrarlar (1363), tekrar kareleri ±10 pay. Profil dahil edilmez (ana senaryo, Karar 6).

2. **Kaynak:** Her videoda MediaPipe 1.2.2, `pose_landmarker_full`, VIDEO modu, `output_segmentation_masks=True` bir kez çalıştırılır. **Aynı çalıştırmanın** pose noktaları ROI'nin konumu, gövde boyu ve kol açısı için kullanılır; maske ile noktalar aynı karede olsun diye. Veri setinin 0.10.20 noktaları kullanılmaz.

3. **Ölçüt `SILUET`** (piksel koordinatlarında; gerçek piksel olduğu için en-boy düzeltmesi gerekmez):
   - Her karede sağ kulak (8) ve sağ omuz (12) noktaları alınır. İkisinin görünürlüğü ≥ 0,5 değilse kare NaN olur.
   - Yatay aralık: kulağın x'i ile omzun x'i arası. Bu aralığın **ortadaki %50'sinde**, eşit aralıklı **5 sütun** seçilir. Kenarlar baş ve kola fazla yakın olduğu için atılır.
   - Dikey arama: her sütunda, y = (kulak y − 0,10 · gövde) noktasından aşağı, (omuz y + 0,20 · gövde) noktasına kadar inilir. Maske değeri ilk kez > 0,5 olan piksel **siluet sınırı**dır. Bulunamazsa o sütun NaN olur.
   - Kare değeri = (5 sütunun siluet sınırı y'lerinin medyanı − kulak y) / gövde boyu (piksel). En az 3 sütun geçerli olmalı; değilse NaN.
   - Yönü YENI ile aynıdır: omuz silkilince küçülür.
   - Gövde boyu, YENI ile aynı tanımla bu çalıştırmanın noktalarından hesaplanır.

4. **Kolun ROI'ye girmesi:** Kol yukarıdayken silüete karışabilir. Bunun için ayrı bir kural **konmaz**. Açı bandı kol açısına koşullu olduğundan, kişinin kendi doğru tekrarlarında da aynı karışma olur ve bant bunu kişiye özel olarak içerir. Bu varsayım raporda belirtilir.

5. **Değerlendirme (Deney 1 v2 biçimi):**
   - Açı bandı (v2), yönsüz bant (Deney 1 ile aynı), Karar 7 adil modeli, 5° kutu, en az 3 tekrar; bütün sabitler aynı.
   - Karşılaştırılan ölçütler: `SILUET` ve aynı çalıştırmanın noktalarından hesaplanan `YENI_mp122`. İkisi de **aynı tekrarlarda** değerlendirilir. Bilgi için, Deney 1 v2'deki kayıtlı YENI değeri yanına yazılır.
   - Metrikler: AUC silkme/doğru ve silkme/diğer; kişi bazlı AUC; kişi bazlı bootstrap ile `SILUET − YENI_mp122` farkı (2000 tekrar, tohum 1).
   - Ayrıca betimsel: geçerli kare oranı (NaN olmayan) ve açı bandı kapsamı.
   - **Birleşik ölçüt ve ağırlık yok.** İki ölçütü birleştirmek ayar gerektirir; gelecek çalışmaya yazılır.

6. **Görsel:** Görsel kontrol aracında 3 örnek video: aynı kişinin bir doğru ve bir silkmeli tekrarı ile bir yanlış alarm ya da kaçırma. Üzerine ROI, 5 sütun ve siluet sınırı çizilir. Seçim tohumla yapılır (tohum 0).

7. **Raporlama:** Sonuç ne olursa olsun yazılır. `SILUET` YENI'den kötü çıkarsa da bu bir bulgudur: "görüntüden omuz silueti denendi; bu tanımla anahtar noktalardan daha iyi değil". Hiçbir tanım sonuçlara bakılarak değiştirilmez.

8. **Önbellek:** Maskenin tamamı saklanmaz. Her kare için 5 sütunun sınır y'leri, kullanılan noktalar ve görünürlükler `veri/ara/siluet/` altına yazılır. Yalnızca görsel örneklerin tekrarları için ikili, sıkıştırılmış ROI maskesi saklanır.

## Uygulama ayrıntıları (Claude Code; kod yazılmadan önce, Karar 48'in boş bıraktığı yerler)

Bunlar tanımı değiştirmez; Karar 48'in söylemediği teknik ayrıntıları önceden sabitler. Sonuçlara bakılarak değiştirilmez.

a. **Hangi kareler işlenir:** Her video×kamera baştan sona sırayla çözülür (OpenCV). Model yalnızca önden + çapraz Ex1 tekrarlarının ±10 pay dahil kare aralıklarının **birleşiminde** çalışır; zaman damgası = kare no · 1000 / fps. Aradaki kareler çözülür ama modele verilmez (süre tahmini de böyle yapılmıştı, Karar 45). Komşu tekrarların payları örtüşürse kare bir kez işlenir.

b. **Piksel koordinatı:** x_px = x · W, y_px = y · H (W × H video boyutu, 1080 × 1920). Gövde boyu (piksel) = omuz ortası – kalça ortası mesafesi, tekrarın ilk 8 karesinin (pay dahil) medyanı (YENI'deki `g0`); NaN kareler bu medyana girmez. Sütun x'leri, kulak ve omuz x'inden küçük olanı `a`, büyük olanı `b` olmak üzere `a + (b − a) · {0,25; 0,375; 0,5; 0,625; 0,75}`, en yakın piksele yuvarlanır. Arama sınırları en yakın piksele yuvarlanır ve görüntü içine kırpılır; iki uç da aramaya dahildir.

c. **Kişi bulunamayan kare** (1.2.2 o karede nokta vermedi, kol açısı NaN): Kare her iki ölçüt için de tekrardan çıkarılır (kol açısı olmadan açı bandında yeri yoktur). Sayısı raporlanır.

d. **NaN değerler açı bandında** (yalnızca `SILUET`'te olur): Bir kalibrasyon tekrarının kutu ortalaması o kutudaki NaN olmayan karelerden alınır; bir kutu, NaN olmayan değer veren **en az 3 tekrar** varsa geçerlidir (Karar 48'deki "en az 3 tekrar"); E, geçerli kutulardaki NaN olmayan karelerin ortalamasıdır. Her ölçüt kendi modeliyle değerlendirilir (geçerli kutular ölçüte göre değişebilir). Bu değişiklik `cekirdek/aci_bandi.py`'de yapılır; NaN içermeyen ölçütlerde sonucu **değiştirmez** (Deney 1 ve Deney 2 regresyon testleri bunu sınar).

e. **"Aynı tekrarlar":** Birincil AUC ve bootstrap, iki ölçütün de E'si NaN olmayan tekrarlarda (ortak küme) hesaplanır. Ortak kümenin dışında kalan tekrar sayısı ölçüte göre raporlanır. Grubunda 3'ten az doğru tekrar olan tekrarlar Deney 1 v2'deki gibi değerlendirilmez.

f. **Betimsel ölçüler:** "geçerli kare oranı" = etiketli karelerde `SILUET`'in NaN olmayan kare oranı (tekrar başına, sonra ortalama); "kapsam" = Deney 1 v2'deki tanım (açı bandının geçerli kutusuna düşen etiketli kare oranı), her ölçüt için ayrı.

g. **Görsel örnek seçimi (tohum 0):** Görsel kontrol aracının geçici eşiği kullanılır (Adım 2b: test kişisi hariç 4 kişinin doğru tekrarlarındaki `SILUET` E'sinin %90'lık dilimi). Önce ortak kümede, aynı (video, kamera, yönelim) grubunda en az bir doğru ve bir silkme tekrarı olan gruplardan biri; sonra o gruptan bir doğru ve bir silkme tekrarı; üçüncüsü, bütün ortak kümedeki yanlış alarmlar (doğru, E > eşik) ve kaçırmalar (silkme, E ≤ eşik) birleşiminden biri. Hepsi `numpy.random.default_rng(0)` ile, bu sırayla.

h. **Önbellek (madde 8'den küçük sapma, önceden):** Sınır y'leri tekrarın gövde boyuna (`g0`) bağlıdır ve bir kare iki komşu tekrarın payına düşebilir; görsel örnekler de ancak değerlendirmeden sonra seçilebilir. Bu yüzden segmentasyon çalıştırması her işlenen karede **yalnızca omuz bölgesinin ikili maskesini** (eşik 0,5, yani tanımdaki "> 0,5" kuralının kendisi; kutu: x kulak–omuz aralığı ± 8 piksel, y kulak y − 0,5 · gövde_kare … omuz y + 0,6 · gövde_kare, gövde_kare o karenin gövde boyu) sıkıştırılmış olarak, 33 noktayla ve görünürlüklerle birlikte `veri/ara/siluet/` altına yazar. Tam maske saklanmaz. Sınır y'leri değerlendirmede bu kutulardan tanıma göre hesaplanır ve kare başına (5 sütun x'i, 5 sınır y'si) yine `veri/ara/siluet/` altına yazılır. Arama aralığı kutunun dışına taşarsa, taşan pikseller "bulunamadı" sayılır ve böyle sütunların sayısı raporlanır (beklenen: 0).

## Basit anlatım (kullanıcı için)
*(Sonuçlar gelince yazılacak.)*

## Yapılanlar (önceden kayıttan sonra; commit'ler: önceden kayıt `51a997c`, kod bunun ardından)
- `cekirdek/siluet.py`: `SILUET` ölçütünün tanımı (sütun seçimi, arama aralığı, sınır bulma, NaN kuralları, g0) ve aynı noktalardan `YENI_mp122`.
- `cekirdek/aci_bandi.py`: isteğe bağlı `nan_atla` (ayrıntı d). Varsayılan kapalı; eski yol birebir aynı. Uygulama bu seçeneği kullanmaz (Karar 49).
- `araclar/siluet_segment.py`: segmentasyon çalıştırması ve önbellek (ayrıntı a, h); yarıda kalırsa biten videolar atlanır.
- `deneyler/siluet.py`: değerlendirme (Deney 1 v2'nin v2 koşulu, ölçüt başına ayrı model, ortak küme, kişi AUC, bootstrap, betimsel tablolar, kare başına sınırların yazılması).
- `araclar/siluet_gorsel.py`: görsel kontrol aracı eki (açı bandı görünümü + omuz bölgesi: kutu, 5 sütun, siluet sınırı, büyütülmüş bölge) ve önceden kayıtlı örnek seçimi.
- `testler/test_siluet.py`: 15 test (yapay maskede sınır bulma, > 0,5 eşiği, kutu taşması, sütun seçimi, görünürlük ve en az 3 sütun kuralı, g0 ve NaN, `YENI_mp122` = kayıtlı YENI tanımı, önbellek paketleme, `nan_atla` sonlu veride aynı / NaN'ı yok sayar / en az 3 tekrar).

## Değişen / eklenen dosyalar
| Dosya | Ne işe yarıyor |
| --- | --- |
| `cekirdek/siluet.py` | SILUET ölçütü (tanım) |
| `cekirdek/aci_bandi.py` | `nan_atla` seçeneği (varsayılan kapalı) |
| `araclar/siluet_segment.py` | MediaPipe segmentasyon + önbellek (`veri/ara/siluet/`) |
| `deneyler/siluet.py` | değerlendirme → `sonuclar/siluet/` |
| `araclar/siluet_gorsel.py` | 3 görsel örnek → `sonuclar/siluet/gorsel/` |
| `testler/test_siluet.py` | testler |

## Kod sınaması (Güncelleme 11: yalnızca kodun çalıştığını görmek için; AUC hesaplanmadı)
- `python -m araclar.siluet_segment --sinama 500` → ayrı klasör `veri/ara/siluet_sinama/`. Ex1 Honza cam1'in ilk 500 gereken karesi: 0,2 dk (28,8 ms/kare, video çözme dahil), kişi bulunamayan kare 0, önbellek 356 008 bayt (~0,7 kB/kare).
- `python -m deneyler.siluet --onbellek veri/ara/siluet_sinama --sinama`: önbellekte tam olan 3 tekrar (hepsi doğru); geçerli kare %100, taşan sütun 0; SILUET medyanları 0,297 / 0,298 / 0,304 (YENI_mp122 0,400 / 0,385 / 0,413).
- Görsel aracı ve bant hesabının uçtan uca çalıştığını görmek için sınama 2500 kareye uzatıldı (1,2 dk, 28,4 ms/kare; 14 tekrar). Bir doğru tekrarın görsel videosu üretildi (~8 s). Etiketlerle E karşılaştırılmadı.
- **Gözlem (tanım değişmez):** Kulağa en yakın sütun (aralığın %75'i) bazı karelerde başa/saça değiyor; 5 sütunun medyanı bunu tek ya da iki sütunda tolere ediyor. Kol 90°'nin üstündeyken sütunlar kolun üst kenarına değiyor; bu Karar 48 madde 4'te öngörülen durum (bant bunu kişiye özel içerir).
- `pytest`: 203 geçti, 1 xfail (önceki 188 + 15 yeni). Deney 1 regresyonu değişmedi.

## Nasıl çalıştırılır
```powershell
.venv\Scripts\python -m araclar.siluet_segment          # segmentasyon (kullanıcı; ~1,5 saat)
.venv\Scripts\python -m araclar.siluet_segment --durum  # kaç video bitti
.venv\Scripts\python -m deneyler.siluet --gorsel        # değerlendirme + 3 görsel (birkaç dk)
```
İşlenecek: 15 video×kamera, **153 081 kare** (tekrarların ±10 pay dahil birleşimi; örtüşen paylar bir kez), çözülecek toplam 213 210 kare.

## Sonuçlar
*(Segmentasyon ve değerlendirme sonrası.)*

## Kararlar ve sapmalar
- Önbellek biçimi (ayrıntı h; madde 8'den küçük sapma, koddan önce kayıtlı): tam maske yerine her karede omuz bölgesi ikili maskesi saklanıyor; sınır y'leri değerlendirmede hesaplanıp `veri/ara/siluet/sinirlar.npz`'ye yazılıyor.
- `deneyler/hepsi.py`'ye 6b eklenmedi; dondurmada (Adım 9) karar verilir.
