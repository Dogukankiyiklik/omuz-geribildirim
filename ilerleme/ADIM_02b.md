# ADIM 02b — Görsel kontrol aracı

**Tarih:** 2026-11-06
**Durum:** Kısmen — araç ve galeri hazır; **kullanıcının en az 5 tekrarı izleyip gözlemlerini yazması bekleniyor** (aşağıda "Kullanıcı gözlemleri").

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
- [ ] Kullanıcı en az 5 tekrarı izledi — **bekleniyor**.
- [ ] İskeletin videoya oturduğu ve kararların görüntüyle tutarlı olup olmadığı ADIM dosyasına not edildi — **bekleniyor** (aşağıdaki bölüm).
- [x] Araç ve galeri çalışıyor; testler: `26 passed in 9.86s`.

## Kullanıcı gözlemleri (kullanıcı dolduracak)
| Video | İskelet oturuyor mu? | Referans (turkuaz) mantıklı mı? | Karar görüntüyle tutarlı mı? | Not |
| --- | --- | --- | --- | --- |
| | | | | |
| | | | | |
| | | | | |
| | | | | |
| | | | | |

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
- **Kol yüksekliği karışması** (yukarıda, "İnceleme 1"): silkmeli tekrarların %18,2'sinde kol referanstan ≥ 30° az kalkıyor; DTW şekil eşlediği için omuz farklı kol açılarında karşılaştırılıyor. Yönlü bant (Adım 4) ve/veya açıya göre hizalama önerisi.
- Kaçırılan silkmelerin 2'si **çapraz** görüşte ve **ek hatalı** (dirsek bükük, baş eğik). Ek hata, kişinin kendi bandında da bir şeyleri değiştirmiş olabilir. Kullanıcının gözlemine göre Adım 4'te incelenebilir.
- Yanlış alarmlarda E'nin tekrarın **sonunda** yükseldiği bir örnek var (Terka t10). Tekrar sınırlarının (Segmentation.csv) bazı tekrarlarda kısa kesilmesi E'yi şişiriyor olabilir; gözlem bekleniyor.
