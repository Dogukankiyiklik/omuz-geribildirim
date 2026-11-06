# ADIM 02b — Görsel kontrol aracı

**Tarih:** 2026-11-06
**Durum:** Tamamlandı (kullanıcı iki galeriden 13 videoyu yorumladı ve kalanları izledi; gözlemler ve onlardan çıkan ölçümler aşağıda)

## Basit anlatım (kullanıcı için, 3–6 cümle)
Şimdiye kadar sistem bize sadece sayılar veriyordu. Bu adımda herhangi bir tekrarı videoda izleyip sistemin ne gördüğünü kendi gözünle kontrol edebileceğin bir araç yaptık. Solda video ve üstünde iki iskelet var. **Yeşil** iskelet, veri setinin MediaPipe iskeleti; bandın dışına çıkan bölge **kırmızı** oluyor. **Turkuaz** iskelet, kişinin kendi doğru tekrarlarından biri (referans). Bu iskelet zamanda (DTW) ve konumda (kalça, gövde boyu, gövde ekseni) kişinin üstüne oturtulmuş, böylece "doğrusu böyle olmalıydı" görülebiliyor. Sağ üstte bant grafiği ve hareket eden bir imleç, sağ altta gerçek etiket, puanlar ve sistemin geçici kararı var. Bu, hocanın Problem 3'ünün (referans ve kullanıcı hareketini çakıştırma) ilk sürümü.

## Yapılanlar
- `cekirdek/bindirme.py`: referans iskeleti kullanıcıya çakıştıran ortak kod. Zamansal hizalama DTW ile, geometrik hizalama öteleme + ölçek + döndürme ile yapılıyor. Adım 6'daki uygulama da bunu kullanacak.
- `araclar/gorsel_kontrol.py`: tek tekrar videosu ve galeri üretir; `--goster` ile pencerede oynatır.
- `deneyler/deney1.py`: `tekrar_degerlendirmeleri()` adlı bir üretece ayrıldı. Böylece araçta gösterilen bant ve E, Deney 1 tablosundakiyle **aynı hesap** (fark 0.0; `tekrarlar.csv` ile karşılaştırıldı). Deney sonunda galeri kendiliğinden üretiliyor (`--galeri-yok` ile kapatılabilir).
- `araclar/senkron_kontrol.py`: Adım 0'da açık kalan "video ile iskelet kare kare hizalı mı?" sorusu bütün Ex1 videolarında ölçüldü (aşağıda).
- Galeri: `sonuclar/deney1/galeri/`, 3 grup × 3 video ve `liste.md`.

## Değişen / eklenen dosyalar
| Dosya | Ne işe yarıyor |
| --- | --- |
| `cekirdek/bindirme.py` | `Bindirici` (DTW kare eşlemesi + geometrik çakıştırma), `KEMIKLER`, `OLCUT_UZUVLARI`, `banttan_cikan_kemikler` |
| `cekirdek/etiketler.py` | Hata kodlarının ve ölçütlerin Türkçe adları |
| `cekirdek/veri.py` | `video_adi`, `video_cikar` eklendi (videoyu zip'ten geçici klasöre çıkarır; zip'e dokunmaz) |
| `araclar/gorsel_kontrol.py` | Görsel kontrol aracı ve galeri |
| `araclar/senkron_kontrol.py` | Video–iskelet kare hizası ölçümü |
| `deneyler/deney1.py` | `tekrar_degerlendirmeleri` üreteci; sonunda galeri |
| `testler/test_bindirme.py` | Çakıştırma testleri (7 test) |
| `.gitignore` | `sonuclar/**/*.mp4` (videolar yeniden üretilebilir ve büyük) |
| `sonuclar/deney1/galeri/` | 9 MP4 + `liste.md` |
| `sonuclar/adim2b/senkron.csv` | Kare hizası ölçümü |

## Nasıl çalıştırılır
```bash
python -m araclar.gorsel_kontrol --video ex1_Honza --kamera cam1 --yonelim 0 --tekrar 5            # ~15 s
python -m araclar.gorsel_kontrol --video ex1_Honza --kamera cam1 --yonelim 0 --tekrar 5 --goster   # ayrıca pencerede oynatır (boşluk: duraklat, q: çık)
python -m araclar.gorsel_kontrol --video ex1_Honza --kamera cam1 --yonelim 0 --tekrar 5 --fps 15   # yarı hızda
python -m araclar.gorsel_kontrol --galeri          # ~40 s
python -m araclar.senkron_kontrol                  # ~2,5 dk
```
`--tekrar`, Segmentation.csv'deki `repetition_number` (o kişinin o yönelimdeki kaçıncı tekrarı). `--olcut` ile YENI yerine başka bir Deney 1 ölçütü gösterilebilir.
Çıktı: `sonuclar/gorsel_kontrol/<video>_<kamera>_o<yönelim>_t<tekrar>_<ölçüt>.mp4` (1300×960, 30 FPS, mp4v).

## Sonuçlar

**Tutarlılık:** Honza cam1, yönelim 0, tekrar 5 için araç `YENI E = 0.646 · eşik 0.288 · karar: şüpheli` verdi; `tekrarlar.csv`'deki bant_YENI = 0.646 ile aynı. Araçtaki her tekrar E'si bir doğrulama (`assert`) ile tablodakine eşit tutuluyor.

**Video–iskelet kare hizası** (`sonuclar/adim2b/senkron.csv`; 15 video × 2 pencere = 30 pencere):
- Örtüşmenin güvenilir olduğu (korelasyon ≥ 0,4) 16 pencerede en iyi kayma: −4: 1, −3: 1, −2: 1, −1: 6, 0: 6, +1: 1. Hepsi **en fazla ±4 kare (< 0,14 s)**.
- Büyük kaymalar (−294, −378, +218, +291) yalnızca korelasyonu 0,19–0,23 olan, yani ölçümün güvenilmediği pencerelerde çıktı.
- Video ile iskelet arasında en büyük kare farkı olan ex1_Mima cam1 (14027 / 13724): son pencerede en iyi kayma −5 (r = 0,205, güvenilmez); Adım 0'daki görsel kontrolde de kayma 0 oturuyordu, 303 kare kaydırınca oturmuyordu.
- **Sonuç:** Video ve iskelet pratikte kare kare hizalı; fazla video kareleri sonda. En çok birkaç karelik kaymalar olabilir (ör. ex1_Terka cam1 başta −3, r = 0,783 / kayma 0'da 0,165), görsel araç için önemsiz. Deneyler videoyu kullanmadığı için onları hiç etkilemiyor.

**Galeri** (`sonuclar/deney1/galeri/liste.md`; YENI, geçici eşik, tohum 0). Grup büyüklükleri (3 kamera dahil): yakalanan silkme = 124, kaçırılan silkme = 41, yanlış alarm = 84.

| Dosya | Gerçek etiket | Ek hata | Görüş | E | Eşik |
| --- | --- | --- | --- | --- | --- |
| `yakalanan_silkme_1_ex1_Petra_cam1_o50_t5.mp4` | omuz silkme | – | -50° (çapraz) | 0.459 | 0.286 |
| `yakalanan_silkme_2_ex1_Petra_cam3_o60_t5.mp4` | omuz silkme | – | 30° (çapraz) | 0.393 | 0.286 |
| `yakalanan_silkme_3_ex1_Terka_cam3_o45_t5.mp4` | omuz silkme | – | 45° (çapraz) | 0.499 | 0.279 |
| `kacirilan_silkme_1_ex1_Honza_cam3_o0_t5.mp4` | omuz silkme | – | 90° (profil) | 0.094 | 0.288 |
| `kacirilan_silkme_2_ex1_Mima_cam1_o30_t5.mp4` | omuz silkme | dirsek bükük | -30° (çapraz) | 0.242 | 0.272 |
| `kacirilan_silkme_3_ex1_Mima_cam1_o60_t4.mp4` | omuz silkme | baş yana eğik | -60° (çapraz) | 0.102 | 0.272 |
| `yanlis_alarm_1_ex1_Terka_cam1_o20_t10.mp4` | doğru | – | -20° (önden) | 0.353 | 0.279 |
| `yanlis_alarm_2_ex1_Terka_cam2_o80_t10.mp4` | doğru | – | -35° (çapraz) | 0.368 | 0.279 |
| `yanlis_alarm_3_ex1_Vasil_cam3_o10_t9.mp4` | doğru | – | 80° (profil) | 0.322 | 0.267 |

Not: İki yanlış alarm Terka'nın 10. tekrarları, ama yönelimleri farklı (20° ve 80°), yani iki ayrı tekrar. İkisi de grubunun **son** tekrarı; tekrar sonunda E'nin yükselmesi gözlemiyle birlikte (aşağıda) dikkat çekici.

**İlk gözlemler (Claude Code; videoların birkaç karesine bakılarak, kullanıcı gözleminin yerine geçmez):**
- Önden (Honza cam1 t5), profilden (Honza cam3 t5) ve önden-çapraz (Terka cam1 t10) örneklerde yeşil iskelet kişiye oturuyor.
- Honza'nın 5. tekrarı (silkme) **önden yakalanıyor** (E = 0.646), **profilden kaçırılıyor** (E = 0.094). Aynı hareket, iki farklı kamera. Deney 1'deki "profil zayıf" sonucunun somut örneği.
- Silkmede turkuaz (referans) kulak–omuz çizgisi, yeşil/kırmızı (kullanıcı) çizgiden belirgin şekilde uzun: silkme görüntüde seçilebiliyor.
- Terka t10 (yanlış alarm): YENI, kol inerken ve tekrarın sonunda bandın altında kalıyor (0.35 civarı; bant ~0.50). Bu, kişinin tekrar bitiminde omzunu aşağı bırakmaması ya da tekrarın kısa kesilmesi olabilir (91 kare, diğer tekrarlardan kısa). Videoda bakılmalı.

## Kabul ölçütü kontrolü
- [x] Kullanıcı en az 5 tekrarı izledi: 13 videoyu tek tek yorumladı, kalanları da izledi.
- [x] İskeletin videoya oturduğu ve kararların görüntüyle tutarlı olup olmadığı not edildi (aşağıda).
- [x] Araç ve galeri çalışıyor; testler: `26 passed`.

## Kullanıcı gözlemleri (kullanıcının sözleri, kısaltılmış)
`galeri/` (tüm görüşler) ve `galeri_onden/` (yalnızca önden):

| # | Video | Kullanıcının gözlemi |
| --- | --- | --- |
| 1 | `galeri/kacirilan_silkme_1_ex1_Honza_cam3_o0_t5` (profil) | Mantıklı görünüyor ama yandan çekim olduğu için iskeletler birbirine girmiş, tam seçilmiyor. "Tam yandan bir görüntüde insan olsan bile yana açışı değerlendirebilir misin, muamma." |
| 2 | `galeri/kacirilan_silkme_2_ex1_Mima_cam1_o30_t5` (çapraz) | Açı nedeniyle yanlış etiketlenmiş (kaçırılmış) gibi. |
| 3 | `galeri/kacirilan_silkme_3_ex1_Mima_cam1_o60_t4` (çapraz) | İskeletler arada titriyor, açı nedeniyle olabilir. |
| 4 | `galeri/yakalanan_silkme_1_ex1_Petra_cam1_o50_t5` | Turkuaz iskelet daha yukarıda. |
| 5 | `galeri/yakalanan_silkme_2_ex1_Petra_cam3_o60_t5` | Turkuaz iskelet aşırı yukarıda (kullanıcı ~90°, referans ~180°). |
| 6 | `galeri/yakalanan_silkme_3_ex1_Terka_cam3_o45_t5` | Güzel yakalanmış, iskeletler güzel. |
| 7 | `galeri/yanlis_alarm_1_ex1_Terka_cam1_o20_t10` | Sonlarda kolunu çok hızlı indiriyor; yanlış alarm sırf sondaki sapmadan (bandın altında kalmasından). |
| 8 | `galeri/yanlis_alarm_2_ex1_Terka_cam2_o80_t10` | Yine hızlı indirme / sondaki sapma kaynaklı yanlış alarm gibi. |
| 9 | `galeri/yanlis_alarm_3_ex1_Vasil_cam3_o10_t9` | Hızlı indirmeye kurban gitmiş gibi. |
| 10 | `galeri_onden/kacirilan_silkme_1_ex1_Petra_cam1_o0_t5` | Turkuaz çok yukarıda; **bariz omuz silkmesi var, neden normal dediğini anlamadım.** |
| 11 | `galeri_onden/kacirilan_silkme_2_ex1_Vasil_cam3_o80_t6` | Kişi elini neredeyse 180° kaldırmış; yanlış karar bundan mı? |
| 12 | `galeri_onden/kacirilan_silkme_3_ex1_Vasil_cam3_o90_t5` | Yine Vasil; Vasil'in videolarında saptamak zor olsa gerek. |
| 13 | `galeri_onden/yakalanan_silkme_1_ex1_Petra_cam2_o30_t5` | Turkuaz yine yukarıda, ama doğru tespit edilmiş. |

Genel yorum: "Bazılarında kişi kolunu 180° kaldırıyor ya da çok hızlı indiriyor; turuncu çizgide şaşmalar oluyor. Vasil her tekrarda elini ~180° kaldırıyor ama bazıları silkme, bazıları doğru etiketlenmiş; garip geldi. Genel olarak bir gariplik var ama ifade edemiyorum."

İskeletin videoya oturması hakkında kullanıcı bir sorun bildirmedi. Bildirilen: profil görüşte iskeletlerin üst üste binmesi (#1) ve çapraz görüşte titreme (#3).

## Gözlemlerden çıkan ölçümler (Claude Code)
Kullanıcının "ifade edemediği gariplik" üç ayrı soruna ayrıldı. Hepsi sayılarla doğrulandı.

**Bulgu A — Yanlış alarmlar tekrarın SONUNDAN geliyor (#7, #8, #9).**
- ex1_Terka cam1 yönelim 20 tekrar 10 (91 kare): kol 77. karede inmiş (2°). Sonraki karelerde kol aşağıdayken YENI 0.428 → 0.397 (kare 84) → 0.346 (kare 90) düşmeye devam ediyor; başlangıçta 0.520'ydi. Yani sapma hareketin kendisinde değil, kol indikten **sonra**. Son 10 kare, Adım 0'da eklenen **pay**; bu karelerde kişi muhtemelen bir sonraki duruşa hazırlanıyor ya da gevşiyor. Tekrar 10, o yönelimin son tekrarı.
- Tüm veride: Yanlış alarm veren doğru tekrarlarda E'nin inişten sonraki bölümden gelen payı medyan **0.31**; diğer doğru tekrarlarda **0.14**, silkmelerde **0.13**.
- Kullanıcının "hızlı indirme" açıklaması kısmen tutmuyor: İniş süresinin referansa oranı yanlış alarmlarda da diğer doğru tekrarlarda da medyan **1.0**. Sorun hız değil, iniş sonrasındaki karelerde omuz/başın yerinin değişmesi.
- **Keşif amaçlı deneme** (Deney 1 değiştirilmedi): E, referansın baştaki ve sondaki 10 pay karesi hariç tutularak hesaplanınca:

  | | AUC silkme/doğru | AUC silkme/diğer | %90 eşikte yakalanan silkme | %90 eşikte yanlış alarm |
  | --- | --- | --- | --- | --- |
  | E (Deney 1, pay dahil) | 0.909 | 0.705 | 124/165 | 84/834 |
  | E (pay hariç) | 0.932 | 0.714 | 130/165 | 81/834 |

  Pay kareleri yalnızca dinlenme başlangıcı (ilk 8 kare) için gerekli; bant hatasına katılmaları referans koddan gelen bir davranış. Öneri: E'yi yalnızca etiketli tekrar karelerinde hesaplamak. Bu, test verisinde görülüp yapılan bir değişiklik olduğu için Deney 1'e dokunulmadı; karar danışmanın.

**Bulgu B — Petra'nın bariz silkmesi kolun az kalkması yüzünden kaçırılıyor (#10, ayrıca #4, #5, #13).**
- ex1_Petra cam1 yönelim 0 tekrar 5 (önden): E = 0.176 (eşik 0.286) → kaçırıldı. Ama **aynı kol açısında** karşılaştırınca silkme apaçık:

  | Kol bu açıyı geçerken | Silkmeli tekrar 5'in YENI'si | 5 doğru tekrarın YENI'si |
  | --- | --- | --- |
  | 60° | 0.422 | 0.491 – 0.516 |
  | 90° | 0.380 | 0.448 – 0.473 |
  | 110° | 0.338 | 0.396 – 0.428 |

  Silkmeli tekrarın değeri, her açıda **bütün** doğru tekrarlardan belirgin şekilde düşük.
- Sebep, "İnceleme 1"de bulunan kol yüksekliği karışması. Petra silkerken kolu medyan 121° kaldırıyor, doğruda 169°. DTW eğrinin şeklini eşlediği için 121°'lik tepe 169°'lik tepeyle eşleniyor ve omuz, "kol 169°'deyken normal" olan omuz yüksekliğiyle karşılaştırılıyor. Turkuazın hep yukarıda olması da bundan.
- Kolu ≥ 30° az kalkan silkmelerin E medyanı 0.358 (n = 30); diğer silkmelerinki 0.425 (n = 135).
- Bu, **hizalamayı gerçek kol açısına göre yapma** önerisini güçlü şekilde destekliyor.

**Bulgu C — Kişiler arası fark: Vasil'de ayrım en zayıf (#11, #12).** Kişi bazlı AUC (silkme/doğru, bant YENI):

| Kişi | AUC | Silkmede kol (medyan) | Doğruda kol (medyan) | Silkme E (medyan) | Doğru E (medyan) |
| --- | --- | --- | --- | --- | --- |
| Honza | 0.985 | 158° | 148° | 0.713 | 0.050 |
| Mima | 0.947 | 114° | 135° | 0.481 | 0.072 |
| Petra | 0.884 | 121° | 169° | 0.371 | 0.068 |
| Terka | 0.926 | 157° | 171° | 0.458 | 0.067 |
| Vasil | **0.800** | 162° | 153° | **0.224** | 0.044 |

Vasil'in silkmelerinin E medyanı (0.224) geçici eşiğin (~0.27) altında, bu yüzden çoğu kaçırılıyor. Vasil silkerken kolu doğru tekrarlarından **daha yükseğe** kaldırıyor. Silkmesi bu ölçütle zayıf görünüyor. Etiketlerin yanlış olup olmadığını söyleyemeyiz; ama 5 kişiden birinde ayrımın belirgin şekilde düşük olması raporlanmalı.

**Diğer gözlemler:**
- Profil görüş (#1): Kullanıcı da insan gözüyle değerlendirmenin zor olduğunu söylüyor. Bu, Deney 1'deki profil AUC'sinin düşüklüğüyle (0.779) uyumlu ve bir sınırlılık olarak raporlanabilir.
- Titreme (#3): MediaPipe noktalarının kareden kareye titremesi. Adım 3'teki Deney 1c (yumuşatma) bunu ele alacak.
- Turuncu çizgideki "şaşmalar": Tekrar ile referansın temposu ya da kol yüksekliği farklı olunca DTW birçok kareyi aynı referans karesine eşliyor. Hizalanmış eğri bu yüzden basamaklı ya da düzlüklü görünüyor (ör. Petra'da tepedeki düz kısım).

## Kararlar ve sapmalar
- **Geometrik hizalama, PLAN'dan küçük bir sapma:** PLAN, "gövde merkezine öteleme, gövde uzunluğu oranında ölçekleme, gövde ekseni açısı kadar döndürme" diyor. Uygulanan:
  - öteleme: **kalça ortası** (kare kare);
  - ölçek ve döndürme: **tekrar başındaki dinlenme karelerinden bir kez**.

  Gerekçe: Gövde merkezi ve gövde uzunluğu omuzları içeriyor. Kare kare bunlara göre hizalanırsa, kullanıcının omzu kalkınca referans da onunla birlikte büyür ve kalkar, yani **silkme gizlenir**. Bunu `test_silkme_gizlenmez` testi doğruluyor. Kalçalar silkmeden etkilenmiyor. Adım 6'daki bindirme de aynı kodu kullanacak.
- **Referans iskelet = bandın referans tekrarı.** Bu, Deney 1'de o tekrarın bandı kurulurken rastgele seçilen doğru tekrar; böylece videoda görülen referans, bandın zaman eksenini belirleyen tekrarla aynı.
- **Geçici karar ve eşik:** Adım 4'ten önce bir karar kuralı yok. Araçta ve galeride "E > eşik → şüpheli" kullanıldı. Eşik = **test kişisi hariç** diğer 4 kişinin doğru tekrarlarındaki E'nin %90'lık dilimi. Test kişisinin verisi eşiğe girmiyor (CLAUDE.md, eşik ayarı kuralı). Bu yalnızca görselleştirme için; bir değerlendirme sonucu olarak raporlanmamalı.
- **Kırmızı kemikler:** Yalnızca seçilen ölçütün (varsayılan YENI) kemikleri: YENI → kulak–omuz; M01, M33 → omuz çizgisi; M01_tek, M39_F2 → omuz çizgisi + sağ gövde kenarı.
- **Renkler:** Referans önce maviydi; Honza'nın mavi kolunun üstünde seçilmediği için siyah kenarlı turkuaza çevrildi.
- **Video biçimi:** mp4v kodlu MP4. Windows'un varsayılan oynatıcısı açamazsa `--goster` ya da VLC kullanılabilir.
- **Videolar** her çalıştırmada `videos.zip`'ten geçici bir klasöre çıkarılıp sonra siliniyor; `veri/` altına hiçbir şey yazılmıyor.
- **Galeri** "karıştırılan hata türleri" grubunu henüz içermiyor (PLAN: Deney 2'den sonra).

## Kullanıcı geri bildirimi sonrası (aynı gün)
Kullanıcının ilk iki gözlemi:
1. `yakalanan_silkme_2_ex1_Petra_cam3_o60_t5.mp4`: kullanıcı kolu ~90° kaldırıyor, turkuaz referans ~180°'ye kalkıyor.
2. Videolar tam karşıdan değil; bant grafiğinde "inip çıkıp tekrar inen" eğriler var; açı yanılgıya sebep olmuyor mu?

**İnceleme 1: Petra, yazılım hatası değil, veride bir özellik.** Bu tekrarda Petra kolunu en fazla **111.1°** kaldırmış. Bandın referansı (tekrar 9, doğru) **169.8°**'ye çıkıyor. Aynı gruptaki doğru tekrarlar 165–174°. Çakıştırma doğru çalışıyor (ölçek 1.023, döndürme 0.98°). Turkuaz iskelet, "doğru tekrarda kol nereye çıkmalıydı"yı gösteriyor.

Tüm veride kolun en yüksek açısı (medyan, kişi × hata):

| kişi | DOGRU | ARM_FORWARD | BENT_ARM | ELEVATED_SHOULDER | HEAD_TO_SIDE | LOW_ABDUCTION |
| --- | --- | --- | --- | --- | --- | --- |
| Honza | 148 | 156 | 152 | 158 | 156 | 121 |
| Mima | 135 | 137 | 120 | 114 | 115 | 103 |
| Petra | 169 | 151 | 170 | 121 | 154 | 103 |
| Terka | 171 | 169 | 167 | 157 | 165 | 119 |
| Vasil | 153 | 165 | 141 | 162 | 167 | 121 |

Silkmeli tekrarların **%18,2'si** kendi referansından en az 30° daha az kalkmış. Petra ve Mima silkerken kolu belirgin şekilde daha az kaldırıyor.

**Sonuç ve olası etkisi (danışmana):**
- DTW z-normalize edildiği için eğrinin **şeklini** eşliyor, açının **değerini** değil. Kullanıcının 111°'lik tepesi, referansın 170°'lik tepesiyle eşleniyor. Yani omuz, "kol 170°'deyken normal olan" omuz yüksekliğiyle karşılaştırılıyor.
- Bu iki yöne etki edebilir:
  - (a) Silkme + düşük kol: referans anında omuz zaten doğal olarak yüksek, silkme daha zor görünür.
  - (b) Yetersiz kaldırma tekrarlarında omuz bandın **üstünde** (kulaktan uzak) kalır ve yönsüz bant bunu da "omuz anormal" sayar. Bu gruptaki yetersiz kaldırma tekrarı (tekrar 7, kol 102.3°) YENI E = 0.705 aldı, silkmeden (0.393) yüksek.
- Bu, Deney 1'deki "silkme/diğer hatalar" ayrımının zayıf olmasının (AUC 0,70) bir açıklaması olabilir. Adım 4'teki **yönlü bant** (yalnızca omzun kulağa yaklaşması) (b)'yi azaltmalı.
- Ek öneri (karar danışmanın): hizalamayı z-normalize şekil yerine **gerçek kol açısına** göre yapmak ("kol açısı X°'deyken normal omuz"). Bu referans koddan bir sapma olur; Deney 1 sayılarını değiştirir. Bu yüzden yapılmadı.

**İnceleme 2: görüş açısı.** Bant, aynı kişinin **aynı kamera ve aynı yönelimdeki** doğru tekrarlarından kuruluyor. Yani çapraz görüşteki bir tekrar, çapraz görüşteki bir bantla karşılaştırılıyor; açının yarattığı bozulma iki tarafta da var. Etkisi Deney 1'de ölçülmüştü: bant YENI AUC önden 0.942, çapraz 0.933, profil 0.779. Çapraz neredeyse önden kadar iyi, profil belirgin şekilde kötü. İlk galerideki 9 videonun 7'si çapraz ya da profildi. Rastgele seçimin sonucu: tekrar parçalarının 556'sı önden, 807'si çapraz, 305'i profil.

**Önden galerisi:** Kullanıcı isteğiyle `--gorus onden` seçeneği eklendi → `sonuclar/deney1/galeri_onden/` (9 MP4 + `liste.md`). Önden görüşte grup büyüklükleri: yakalanan silkme = 47, kaçırılan silkme = 8, yanlış alarm = 30. Tüm görüşlerde ise 124 / 41 / 84.

## Açık sorular / danışmana notlar
- **Pay kareleri E'ye katılıyor** (Bulgu A): Tekrar sonrasındaki 10 pay karesi yanlış alarmların önemli bir kaynağı. Keşif denemesinde pay hariç E ile AUC 0.909 → 0.932. E yalnızca etiketli tekrar karelerinde mi hesaplansın? (Referans koddan sapma; Deney 1 sayılarını değiştirir.)
- **Hizalama açıya göre mi?** (Bulgu B): Petra'da aynı kol açısında silkme her açıda bütün doğru tekrarlardan ayrılıyor, ama şekle göre DTW onu kaçırıyor.
- **Kişiler arası fark** (Bulgu C): Kişi bazlı AUC 0.800 (Vasil) – 0.985 (Honza). Sunumda/raporda ortalamanın yanında kişi aralığı da verilmeli.
- **Kol yüksekliği karışması** (yukarıda, "İnceleme 1"): silkmeli tekrarların %18,2'sinde kol referanstan ≥ 30° az kalkıyor; DTW şekil eşlediği için omuz farklı kol açılarında karşılaştırılıyor. Yönlü bant (Adım 4) ve/veya açıya göre hizalama önerisi.
- Kaçırılan silkmelerin 2'si **çapraz** görüşte ve **ek hatalı** (dirsek bükük, baş eğik). Ek hata, kişinin kendi bandında da bir şeyleri değiştirmiş olabilir. Kullanıcının gözlemine göre Adım 4'te incelenebilir.
- Yanlış alarmlarda E'nin tekrarın **sonunda** yükseldiği bir örnek var (Terka t10). Tekrar sınırlarının (Segmentation.csv) bazı tekrarlarda kısa kesilmesi E'yi şişiriyor olabilir; gözlem bekleniyor.
