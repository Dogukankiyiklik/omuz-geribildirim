# ADIM 06b — Omuz bölgesi siluet ölçütü (`SILUET`)

**Tarih:** 2026-11-07 (önceden kayıt ve sonuçlar aynı gün)
**Durum:** Tamamlandı (sonuç olumsuz; olduğu gibi raporlanıyor). Danışmana gönderilecek.

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
- **Siluet nedir?** MediaPipe isteğe bağlı olarak bir "segmentasyon maskesi" de veriyor: görüntüdeki her pikselin kişiye mi arka plana mı ait olduğunu gösteren bir harita. Bu haritada kişinin dış çizgisi, yani silueti görünür. Omuz silkilince boyundan omuza inen çizgi (trapez kası hattı) kulağa doğru kalkar.
- **Neden denendi?** Şimdiye kadarki bütün ölçütlerimiz MediaPipe'ın verdiği noktalardan geliyordu. Hoca, noktaların yanında görüntünün kendisinden gelen bir özellik de önermişti. `SILUET` bu projedeki görüntüden gelen tek ölçüt.
- **Nasıl ölçtük?** Kulak ile omuz arasına 5 dikey çizgi koyduk. Her çizgide yukarıdan aşağı inip kişinin başladığı ilk pikseli bulduk. Bu "omuz çizgisi"nin kulağa uzaklığını gövde boyuna böldük. Değerlendirme, kulak–omuz ölçütümüz YENI ile tamamen aynı yöntemle (kişiye özel açı bandı) yapıldı.
- **Ne çıktı?** Önden çekimde siluet iyi çalışıyor (AUC 0,94; 1'e ne kadar yakınsa silkmeyi o kadar iyi ayırıyor demek). Ama YENI'den yine biraz geride (0,99). Çapraz çekimde ise neredeyse yazı-tura (0,55). Hepsi birlikte 0,72'de kalıyor; YENI 0,97. Farkın güven aralığı sıfırı içermiyor, yani YENI'nin üstünlüğü tesadüf değil.
- **Neden çaprazda bozuldu?** Kişi kameraya yan durunca kulak ve omuz görüntüde neredeyse üst üste geliyor. Bu yüzden 5 çizgi boyun–omuz hattına değil, başın (yüz, saç) üstüne düşüyor. Çizgiler kulağın biraz üstünden başladığı için ilk pikselden itibaren "kişi" buluyor ve ölçüt hep aynı sayıyı veriyor. −50° ve −60°'de karelerin %100'ünde böyle.
- **Sonuç cümlesi:** "Görüntüden omuz silueti denendi; bu tanımla anahtar noktalardan daha iyi değil. Önden çekimde işe yarıyor, çapraz çekimde tanım başa takılıyor." Uygulama ve karar kuralı değişmiyor (Karar 49).

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

### Segmentasyon çalıştırması (kullanıcı, 7 Kas akşamı)
- `python -m araclar.siluet_segment`: 15/15 video×kamera, 153 081 kare, toplam **90,0 dk** (35,3 ms/kare; atlanan karelerin çözülmesi dahil). MediaPipe 1.2.2. Kişi bulunamayan kare **0**, maskesiz kare **0**. Önbellek `veri/ara/siluet/` 100 MB.
- `python -m deneyler.siluet --gorsel` → `sonuclar/siluet/` (`ozet.csv`, `kisi_auc.csv`, `bootstrap.csv`, `betimsel.csv`, `tekrarlar.csv`, `sonuclar.xlsx`), `sonuclar/siluet/gorsel/` (3 video + `liste.md`), `veri/ara/siluet/sinirlar.npz`.

### 1) AUC (`ozet.csv`; ortak küme = 1363 tekrarın hepsi; silkme 135, doğru 681, diğer hatalar 501)
| Ölçüt | AUC silkme/doğru | AUC silkme/diğer | önden (0–20°) silkme/doğru | çapraz (30–60°) silkme/doğru | kişi AUC ort. (en düşük–en yüksek) |
| --- | --- | --- | --- | --- | --- |
| `SILUET` | 0.7160602599662805 | 0.6248983514452576 | 0.9376716808371485 | 0.5486352357320099 | 0,72 (0,53–0,79) |
| `YENI_mp122` | 0.9686300103333877 | 0.8622754491017964 | 0.986592544146501 | 0.9569478908188586 | 0,97 (0,91–1,00) |
| YENI (Deney 1 v2, kayıtlı; 0.10.20 noktaları; bilgi için) | 0.9676293033121227 | 0.8624233015450581 | 0.9789404839764552 | 0.9602667493796526 | – |

E boş (NaN) tekrar: SILUET 0, YENI_mp122 0 (1363 değerlendirilen tekrarın hepsi ortak kümede).

### 2) Kişi bazlı AUC (`kisi_auc.csv`)
| Kişi | SILUET silkme/doğru | YENI_mp122 silkme/doğru | SILUET silkme/diğer | YENI_mp122 silkme/diğer | silkme / doğru |
| --- | --- | --- | --- | --- | --- |
| Honza | 0.7632373113854596 | 0.9994513031550069 | 0.6430041152263375 | 0.9650205761316872 | 27 / 135 |
| Mima | 0.5255474452554745 | 0.9599891862665585 | 0.456980056980057 | 0.7407407407407407 | 27 / 137 |
| Petra | 0.7599451303155007 | 0.9865569272976681 | 0.692929292929293 | 0.907070707070707 | 27 / 135 |
| Terka | 0.7407407407407407 | 0.9851851851851852 | 0.6306584362139918 | 0.9636488340192044 | 27 / 135 |
| Vasil | 0.7934985345057287 | 0.9094058086863842 | 0.7286195286195286 | 0.8255892255892255 | 27 / 139 |

### 3) Fark, kişi bazlı bootstrap (2000, tohum 1; `bootstrap.csv`)
| Fark | Nokta tahmini | %95 GA |
| --- | --- | --- |
| silkme/doğru · SILUET − YENI_mp122 | -0.25256975036710716 | -0.35603415456572574 – -0.1658202598522832 |
| silkme/diğer · SILUET − YENI_mp122 | -0.2373770976565388 | -0.3238542365302929 – -0.14384802297327148 |

### 4) Betimsel (`betimsel.csv`)
- Geçerli kare oranı (SILUET NaN olmayan): bütün hata türlerinde ortalama ve medyan **1.0**. Görünürlük kuralı hiç devreye girmedi: bu çalıştırmada kulak ve omuz görünürlüğünün en küçük değeri videolara göre 0,968–0,999. Her sütunda bir sınır bulundu (`nan_nedenleri.csv` boş).
- Kapsam (açı bandı): iki ölçütte aynı, HEPSİ 0.9467598215171945 (DOGRU 0.9481742085900806, silkme 0.940789495942286). Kişi bulunamayan kare 0, taşan sütun 0.

### 5) Tanı: siluet sınırının arama başlangıcına yapışması (sonuçlardan SONRA yapılan betimsel analiz; önceden kayıtta yoktu)
Çapraz görüşteki düşük AUC'yi anlamak için yapıldı (CLAUDE.md: önce hata ara). Görsel örneklerde sütunların başa düştüğü görüldü. Sayısı `sinirlar.npz`'den çıkarıldı: etiketli karelerde sütunun sınırı tam arama başlangıcında (kulak y − 0,10·g0) mı, yani sütun en baştan kişinin içinde mi? Çıktı: `sonuclar/siluet/tani_bas_takilma.txt`.

| Görüş grubu | sütun başta oranı | kare değeri başta oranı |
| --- | --- | --- |
| önden (0–20°) | 0.339 | 0.181 |
| çapraz (30–60°) | 0.770 | 0.801 |

Görüş açısına göre kare değerinin başta olma oranı: 0° 0.130; −10° 0.143, 10° 0.179; −30° 0.931, 30° 0.534; −50° 1.000, 50° 0.834; −60° 1.000, 60° 0.971. "Başta" olan karede SILUET tam −0,10 olur ve omzun hareketinden bağımsızdır. Kod hatası bulunmadı: kutu taşması 0, kişi kaybı 0. Görsel örneklerde sınır sütunun ilk pikselinde ve o piksel başın/saçın üstünde.
- **Okuma:** Tanım, kulak ile omuz arasındaki yatay aralıkta boynun yanındaki boşluğu varsayıyor. Kişi döndükçe bu aralık başın üstüne düşüyor. Önden bile karelerin %18'inde değer başa takılıyor; önden AUC'nin YENI'den düşük olmasının bir nedeni bu olabilir (test edilmedi). **Tanım değiştirilmedi** (Karar 48 madde 7); başka bir tanım (ör. aramayı kulağın altından başlatmak) gelecek çalışma önerisi.

### 6) Görsel örnekler (`sonuclar/siluet/gorsel/liste.md`; seçim önceden kayıtlı, tohum 0)
| Dosya | Rol | Gerçek etiket | Görüş | SILUET E | Eşik | YENI_mp122 E |
| --- | --- | --- | --- | --- | --- | --- |
| `dogru_ex1_Vasil_cam1_o50_t9.mp4` | dogru | doğru | -50° | 0.160 | 0.204 | 0.085 |
| `silkme_ex1_Vasil_cam1_o50_t5.mp4` | silkme | omuz silkme | -50° | 0.037 | 0.204 | 0.129 |
| `kacirma_ex1_Petra_cam2_o10_t5.mp4` | kacirma | omuz silkme | 35° | 0.124 | 0.226 | 0.648 |

Üç örnek de çapraz görüşten geldi (seçim rastgele). Üçünde de sütunlar başın üstünde. Grafikte SILUET −0,10 civarında yatay bir çizgi; silkmeli tekrarın E'si (0.037) doğru tekrarınkinden (0.160) düşük. Petra'daki kaçırmayı YENI_mp122 güçlü biçimde yakalıyor (E 0.648).

## Kabul ölçütü kontrolü
- [x] YENI ile siluet ölçütünün AUC karşılaştırması (aynı tekrarlar, bootstrap GA): yukarıda.
- [x] Görsel kontrol aracında siluet sınırının çizildiği 3 örnek video: `sonuclar/siluet/gorsel/`.
- [x] Olumsuz sonuç raporlandı; tanım sonuca göre değiştirilmedi.
- [x] Testler: `pytest` 203 geçti, 1 xfail (değerlendirmeden önce). Deney 1 regresyonu değişmedi.
- [x] Sert süre sınırı (10 Kas akşamı) içinde: 7 Kas.

## Kararlar ve sapmalar
- Önbellek biçimi (ayrıntı h; madde 8'den küçük sapma, koddan önce kayıtlı): tam maske yerine her karede omuz bölgesi ikili maskesi saklanıyor; sınır y'leri değerlendirmede hesaplanıp `veri/ara/siluet/sinirlar.npz`'ye yazılıyor.
- `deneyler/hepsi.py`'ye 6b eklenmedi; dondurmada (Adım 9) karar verilir.
- Segmentasyonun gerçek süresi 90,0 dk; Karar 45 tahmini 76 dk idi (atlanan karelerin çözülmesi ve kutu kesme ek süre getirdi).
- Bölüm 5'teki "başa takılma" analizi önceden kayıtta yoktu. Sonuçlardan sonra, yalnızca betimsel olarak ve hata aramak için yapıldı. Hiçbir sayı ya da tanım ona göre değişmedi.
- YENI_mp122 (1.2.2 noktaları) ile kayıtlı YENI (0.10.20) neredeyse aynı: silkme/doğru 0,969 ve 0,968 (aynı tekrarlar). Karar 27'deki sürüm farkının bu ölçüte etkisi küçük (betimsel).

## Açık sorular / danışmana notlar
- Sonuç: SILUET bu tanımla YENI'den kötü (silkme/doğru −0,25, GA −0,36 – −0,17; silkme/diğer −0,24, GA −0,32 – −0,14). Önden 0,94'e karşı çapraz 0,55. Raporda önerilen cümle: "Görüntüden omuz silueti denendi; bu tanımla anahtar noktalardan daha iyi değil: önden çekimde silkmeyi ayırıyor (AUC 0,94), çapraz çekimde arama bölgesi başın üstüne düşüyor (0,55)."
- GELECEK_CALISMA için öneri (eklenmedi, onayınızı bekliyor): görüş açısına dayanıklı bir ROI (ör. aramayı kulak yerine kulak–omuz çizgisinin ortasından başlatmak ya da boynun yanını başka noktalardan seçmek) ve SILUET + YENI birleşimi (ayar gerektirir, kişi bazlı birini-dışarıda-bırak ile).
- Karar 48 madde 4 varsayımı (kolun ROI'ye girmesini bant içerir) önden görüşte çalışmış görünüyor (önden 0,94), ama ayrıca sınanmadı.
