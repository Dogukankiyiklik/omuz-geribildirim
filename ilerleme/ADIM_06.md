# ADIM 06 — Uygulama

**Tarih:** 2026-11-07
**Durum:** Kabul ölçütleri sağlandı. Kullanıcı canlı kamerayla iki oturum yaptı. Açık kalan: pencere modunda video dosyasının (`--video`) kullanıcı tarafından bir kez denenmesi. Canlı denemeden çıkan gözlemler ve öneriler danışmanda (Sonuçlar 6, Açık sorular).

## Basit anlatım
- Sunumda gösterilecek uygulama hazır. Solda görüntü ve iskelet var, sağda geri bildirim paneli. Panelin üstünde büyük harflerle **hasta cümlesi** yer alıyor. Uzman ayrıntısı U tuşuyla açılıp kapanıyor. Altta omuz eğrisi (kişinin normal aralığıyla) ve son 5 tekrar görünüyor.
- **Kalibrasyon:** Kişi 6 doğru tekrar yapar (en az 5). Her tekrardan sonra E (evet) ya da H (hayır) ile onaylar. Sistem bu tekrarlardan kişinin "normal aralığını" kurar.
- **Değerlendirme:** Her tekrar bitince karar ve cümle panele gelir. Ardından tekrar, üzerine kişinin kendi doğru tekrarının iskeleti (turkuaz) bindirilerek yeniden oynatılır. Normal aralığın dışına çıkan uzuvlar kırmızı görünür. Bu, hocanın Problem 3'üdür.
- **Uygulama, deneylerle aynı kodu kullanıyor.** Bunu bir testle gösterdik: uygulamanın değerlendirme fonksiyonu, Deney 3'ün kararını ve iki cümlesini 8 rastgele tekrarda birebir üretti.
- **Hızlı sağlık kontrolü:** Veri setinden Honza'nın bir videosunda MediaPipe'ı yeniden çalıştırdık. 10 tekrarın 10'u ayrıldı. 5 hatalı tekrarın 4'ünde birincil hata doğru söylendi; öne kaçma kaçtı.

*Jargon:* **Tekrar ayırıcı:** Sürekli görüntüde "bir tekrar nerede başlıyor, nerede bitiyor" sorusunu kol açısına bakarak cevaplayan kod. **IoU:** İki zaman aralığının örtüşme oranı (kesişim / birleşim); 1 = tam üst üste. **LOSO:** Birini-dışarıda-bırak; 4 kişide ayarla, 5. kişide test et.

## Yapılanlar
- **Ortak çekirdek** (`cekirdek/degerlendirici.py`):
  - tek tekrarın puanı (`tekrar_puanlari`; `deneyler/deney2.py`'deki v2 puanlama buraya taşındı);
  - sapma kodu (`kod_uret`; `deneyler/deney3.py`'den taşındı);
  - uygulamanın tek tekrarlık değerlendirmesi (`Profil`, `degerlendir`).
  - Deney 2 ve Deney 3 artık bunu içe aktarıyor. Taşımadan sonra Deney 2 puanları (v2 ve v1b) kayıtlı `puanlar.csv` ile aynı: en büyük fark 0,0, NaN deseni aynı. Deney 3'ün `cumleler.csv` ve `cumleler_saglam.csv` dosyaları da birebir aynı.
- **Karar 24:** `cekirdek/kural_dosyasi.py` ve `araclar/kural_disa_aktar.py` → `modeller/kural_ex1.json`.
- **Karar 25:** `cekirdek/tekrar_ayirici.py`. Kareleri tek tek alan bir akış sınıfı. Veri setinde sınama (`deneyler/tekrar_ayirma.py`) bütün diziyi bu sınıfa kare kare veriyor, yani uygulamayla aynı kod.
- **Karar 26:** `cekirdek/kamera_acisi.py`, `deneyler/kamera_acisi.py` → `modeller/kamera_esigi.json`.
- **Uygulama** (`uygulama/`):
  - `poz.py`: MediaPipe Tasks PoseLandmarker, `pose_landmarker_full`, VIDEO modu. Model ilk çalıştırmada `modeller/` altına indirilir.
  - `oturum.py`: arayüzden bağımsız oturum. Tekrar ayırma, kalibrasyon (onay/ret, varsayılan 6, en az 5), kamera açısı uyarısı, değerlendirme, profil kaydı (`profiller/<isim>.npz`), oturum CSV'si (`oturumlar/<tarih>.csv`).
  - `panel.py`: PIL ile Türkçe metin. Panel, omuz eğrisi ve bandı, bindirmeli oynatım (`cekirdek/bindirme.py`).
  - `main.py`: pencere; canlı kamera ya da video dosyası.
  - `toplu.py`: yığın modu ve veri setinden sağlık kontrolü.
- **Testler:** `testler/test_tekrar_ayirici.py` (ayırıcı 7 test, kural dosyası 1 test) ve `testler/test_degerlendirici.py` (uygulama = Deney 3). Toplam `134 passed, 1 xfailed`.

## Değişen / eklenen dosyalar
| Dosya | Ne işe yarıyor |
| --- | --- |
| `cekirdek/degerlendirici.py` | Puan → karar → sapma kodu → iki cümle (deney + uygulama ortak) |
| `cekirdek/tekrar_ayirici.py` | Canlı tekrar ayırma (Karar 25) |
| `cekirdek/kural_dosyasi.py` | Kural dosyası yaz/oku (Karar 24) |
| `cekirdek/kamera_acisi.py` | Kamera açısı oranı ve uyarı (Karar 26) |
| `araclar/kural_disa_aktar.py` | `modeller/kural_ex1.json` üretir |
| `araclar/bant_genisligi_tani.py` | Tanı: uygulama profilinin bant genişliği / veri seti (canlı deneme sonrası) |
| `deneyler/tekrar_ayirma.py` | Ayırıcının veri setinde sınanması |
| `deneyler/kamera_acisi.py` | Kamera açısı eşiği |
| `deneyler/deney2.py`, `deneyler/deney3.py` | Taşınan fonksiyonları çekirdekten içe aktarıyor (davranış aynı) |
| `uygulama/*.py` | Uygulama |
| `modeller/kural_ex1.json`, `modeller/kamera_esigi.json` | Uygulamanın sabitleri (git'te) |
| `requirements.txt` | `mediapipe==1.2.2` (Karar 27 notu) |

## Nasıl çalıştırılır
```bash
python -m araclar.kural_disa_aktar          # birkaç saniye → modeller/kural_ex1.json
python -m deneyler.tekrar_ayirma            # ~5 s → sonuclar/tekrar_ayirma/
python -m deneyler.kamera_acisi             # ~30 s → sonuclar/kamera_acisi/, modeller/kamera_esigi.json
python -m uygulama.toplu --veri-seti ex1_Honza --kamera cam1 --yonelim 0   # ~1 dk sağlık kontrolü
python -m uygulama.main ...                 # demo (aşağıda)
```

## Sonuçlar
Sayılar terminal çıktısından ve `sonuclar/` CSV'lerinden kopyalandı.

### 1. Uygulamanın kural parametreleri (Karar 24)
Beş kişinin önden + çapraz tekrarları: 1363 tekrar, eğitim makro-F1 0.6337. Yanında LOSO'daki beş değerin aralığı (`sonuclar/kural_disa_aktar/loso_karsilastirma.csv`).

| parametre | beş kişi (uygulama) | LOSO en küçük | LOSO en büyük |
| --- | --- | --- | --- |
| **T** | **3.8043** | 3.6756 | 5.0034 |
| öne kaçma ölçütü | kol_boyu | kol_boyu (5/5) | |
| yönler (YENI, bas, kol_boyu, dirsek, kaldırma) | −1, +1, −1, −1, +1 | aynı | aynı |
| medyan / ölçek YENI | 0.0156 / 0.0798 | 0.0147 / 0.0771 | 0.0179 / 0.0847 |
| medyan / ölçek bas | 0.0099 / 0.0808 | 0.0085 / 0.0687 | 0.0112 / 0.0876 |
| medyan / ölçek kol_boyu | 0.0261 / 0.0810 | 0.0239 / 0.0783 | 0.0303 / 0.0897 |
| medyan / ölçek dirsek | 0.0306 / 0.0890 | 0.0239 / 0.0851 | 0.0359 / 0.0934 |
| medyan / ölçek kaldırma | 0.0000 / 0.5649 | 0.0000 / 0.5470 | 0.0017 / 0.6505 |
| şiddet q1 / q2 omuz | 0.4818 / 0.6724 | 0.4434 / 0.6098 | 0.5783 / 0.7202 |
| şiddet q1 / q2 baş | 0.2808 / 0.6172 | 0.2640 / 0.5685 | 0.4139 / 0.6643 |
| şiddet q1 / q2 öne kaçma | 0.0433 / 0.5260 | 0.0323 / 0.4761 | 0.0440 / 0.5734 |
| şiddet q1 / q2 dirsek | 0.5447 / 0.7518 | 0.4190 / 0.7087 | 0.6394 / 0.7795 |
| şiddet q1 / q2 az kaldırma | 5.3643 / 9.1424 | 5.0855 / 7.2091 | 6.2219 / 11.1466 |

Bütün değerler LOSO aralığının içinde. T = 3,80, beklenen 3,68–5,00 aralığında.

### 2. Tekrar ayırıcının veri setinde sınanması (Karar 25)
Ex1'in 15 dizisi (5 kişi × 3 kamera), IoU ≥ 0,5, bire bir eşleşme (`sonuclar/tekrar_ayirma/`). Fark = bulunan − etiket (kare; 30 kare = 1 s).

| | önden + çapraz | tüm görüşler | profil (70–90°) |
| --- | --- | --- | --- |
| etiketli | 1363 | 1668 | 305 |
| bulunan | 1295 | 1457 | 162 |
| kaçırılan | 68 | 211 | 143 |
| fazladan | 34 | 63 | 29 |
| **bulunan /100** | **95.01** | **87.35** | **53.11** |
| IoU medyan | 0.85 | 0.85 | 0.72 |
| başlangıç farkı medyan (Ç1–Ç3) | 4 (2–6) | 4 (2–7) | 9 (5–16) |
| bitiş farkı medyan (Ç1–Ç3) | −10 (−13 – −7) | −10 (−14 – −8) | −17,5 (−26 – −12) |

**Hata türüne göre kaçırılan /100:**

| gerçek sınıf | önden + çapraz | tüm görüşler |
| --- | --- | --- |
| doğru | 6.02 (41/681) | 14.15 (118/834) |
| omuz | 2.22 (3/135) | 9.70 (16/165) |
| baş | 3.62 (5/138) | 10.71 (18/168) |
| öne kaçma | 9.49 (13/137) | 12.50 (21/168) |
| dirsek | 2.92 (4/137) | 10.71 (18/168) |
| az kaldırma | 1.48 (2/135) | 12.12 (20/165) |

**Kişi, bulunan /100 (önden + çapraz):** Honza 98.52, Mima 96.00, Petra 97.79, Terka 93.33, Vasil 89.49.

- **Karar 25 durumu:** Önden + çapraz görüş, yani uygulama senaryosu, %90 hedefini geçiyor (95.01). **Tüm görüşler (87.35) ve profil (53.11) %90'ın altında.** Kullanıcıya söylendi. Eşikler değiştirilmedi. Profilde kol kameraya doğru kalktığı için 2B kol açısı küçük görünüyor, 30° geçişi ve 60° tepe şartı tutmuyor. Bu, Karar 6 ve 20'deki profil sınırlılığıyla tutarlı.
- **Bitiş yaklaşık 10 kare (0,33 s) erken.** Ayırıcı, kol dinlenmeye 5° yaklaşınca bitiriyor. Etiketlerde ise son kare biraz daha geç. Başlangıç yaklaşık 4 kare geç. Bu sınırlar karar için sorun değil: puanlar yalnızca bant içindeki karelerden hesaplanıyor ve dinlenme kareleri banda zaten girmiyor. Yine de etiketli aralıkla aynı değil; not edildi.

### 3. Kamera açısı eşiği (Karar 26)
Oran = dinlenmede (ilk 8 kare) omuz genişliği / gövde boyu, doğru tekrarlar (`sonuclar/kamera_acisi/dagilim.csv`):

| görüş grubu | doğru tekrar | %10 | Ç1 | medyan | Ç3 | %90 | eşiğin altında /100 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| önden (0–20°) | 278 | 0.642 | 0.665 | 0.693 | 0.719 | 0.742 | 0.0 |
| çapraz (30–60°) | 403 | 0.389 | 0.463 | 0.536 | 0.601 | 0.650 | 10.174 |
| profil (70–90°) | 153 | 0.046 | 0.080 | 0.158 | 0.223 | 0.292 | 99.346 |

**Eşik = 0.3887.** Görüş açısına göre eşiğin altında kalan tekrar /100 (`gorus.csv`): −45° ile +45° arasında 0; −50°'de 16, +50°'de 0; −60°'de 100, +60°'de 48; |görüş| ≥ 70°'de 96–100. Yani uyarı yaklaşık 50–60°'den sonra devreye giriyor. İki yön simetrik değil; bunun sebebi, egzersiz yapan sağ kolun bir yönde gövdeyi kapatması olabilir (doğrulanmadı). Sonuç, ana sonuçların geçerli olduğu |görüş| ≤ 60° sınırıyla uyumlu.

### 4. Hızlı uçtan uca sağlık kontrolü (Güncelleme 07, madde 6)
`ex1_Honza`, cam1, yönelim 0 (önden). MediaPipe 1.2.2 video dosyasından yeniden çalıştırıldı (kare 0–2014, 42,1 s). Bu bir sağlık kontrolüdür, değerlendirme sonucu değildir.

**Yeni MediaPipe çıktısı ile veri setindeki iskelet (aynı kareler):** kişi bulunamayan kare 0/2015. |Δx| medyanı 0.0023, |Δy| medyanı 0.0013 (görüntü boyuna oran). |Δ kol açısı| medyanı 0.92°, %95'lik dilimi 3.09°.

| ayrılan | kare | etiket no | gerçek etiket | rol | karar | söylenen | hasta cümlesi |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 17–153 | 1 | doğru | kalibrasyon | | | |
| 2 | 180–300 | 2 | doğru | kalibrasyon | | | |
| 3 | 334–458 | 3 | doğru | kalibrasyon | | | |
| 4 | 571–715 | 4 | öne kaçma | değerlendirme | doğru | – | Hareketi doğru yaptın. Kolun yaklaşık 145 dereceye çıktı, omzun ve dirseğin yerindeydi. |
| 5 | 759–933 | 5 | omuz | değerlendirme | omuz | omuz + öne kaçma | Kolunu kaldırırken sağ omzunu kulağına doğru yaklaşık 5 derece kaldırdın. Omzunu aşağıda ve gevşek tut. Ayrıca kolunu kaldırırken kolun öne kaçtı. Kolunu tam yana, vücudunla aynı hizada kaldır. |
| 6 | 993–1183 | 6 | baş | değerlendirme | baş | baş + omuz | Kolun yukarıdayken başını yaklaşık 20 derece yana eğdin. Başını dik tut, karşıya bak. Ayrıca kolun yukarıdayken sağ omzunu kulağına doğru kaldırdın. Omzunu aşağıda ve gevşek tut. |
| 7 | 1242–1363 | 7 | az kaldırma | değerlendirme | az kaldırma | az kaldırma + öne kaçma | Kolunu 115 dereceye kadar kaldırdın; normalde 150 dereceye çıkıyorsun. Kolunu yaklaşık 35 derece daha yukarı kaldır. Ayrıca kolunu indirirken kolun öne kaçtı. Kolunu tam yana, vücudunla aynı hizada kaldır. |
| 8 | 1422–1596 | 8 | dirsek | değerlendirme | dirsek | dirsek + öne kaçma | Kolun yukarıdayken dirseğini yaklaşık 30 derece büktün. Kolunu düz tut. Ayrıca kolunu indirirken kolun öne kaçtı. Kolunu tam yana, vücudunla aynı hizada kaldır. |
| 9 | 1658–1787 | 9 | doğru | kalibrasyon | | | |
| 10 | 1828–1949 | 10 | doğru | kalibrasyon | | | |

- 10 etiketli tekrarın 10'u ayrıldı.
- 5 hatalı tekrarın 4'ünde birincil hata doğru söylendi. Öne kaçma (tekrar 4) "doğru" diye kaçırıldı. Bu, Deney 2'deki bilinen zayıflıkla tutarlı: öne kaçma en çok kaçırılan hata.
- 4 hatalı tekrarda ikinci hata olarak "öne kaçma" da söylendi. Bu tekrarların etiketinde ek hata yok. Deney 3'te de görülen bir durum: iki hata söylemek gerçek hatayı söyleme oranını artırıyor, ama bazen fazladan bir hata da ekliyor.
- Kalibrasyon 3 adet ilk doğru tekrar + 2 adet sondaki doğru tekrarla yapıldı. Yığın modunda kalibrasyon tekrarları sonradan seçilebiliyor; canlı akışta kalibrasyon her zaman önce gelir.

### 5. Görsel kontrol
Panel ve oynatım karesi PNG'ye basılıp kontrol edildi. Tekrar 6 (baş): hasta cümlesi büyük, uzman ayrıntısı küçük; omuz eğrisi bandın altına iniyor; oynatımda turkuaz referansın başı dik, kullanıcının başı eğik ve baş kemikleri kırmızı. İlk denemede hata etiketi başın üstünü örtüyordu ve turkuaz referans yeşil iskeletin altında kalıyordu; ikisi de düzeltildi.

### 6. Kullanıcının canlı denemesi (7 Kas)
Kendi dizüstü kamerası, 1280×720, önden. Sayılar `oturumlar/*.csv` dosyalarından kopyalandı. **Tekrarların gerçek etiketi yok.** Kullanıcı tekrar başına ne yaptığını yazmadı. Bu yüzden bu bölümdeki sayılar doğruluk ölçümü değildir; doğruluk Adım 7'de etiketli videoyla ölçülecek.

| oturum | kalibrasyon | reddedilen | değerlendirilen | birincil karar |
| --- | --- | --- | --- | --- |
| `2026-11-07_123525.csv` | 6 (tepe 143.7–156.9°) | 2 (tepe 110.0, 109.2°) | 41 | omuz 10, baş 10, az kaldırma 9, doğru 5, öne kaçma 4, dirsek 3 |
| `2026-11-07_123930.csv` | 6 (tepe 146.5–154.8°) | 0 | 15 | omuz 6, öne kaçma 4, doğru 2, dirsek 1, baş 1, az kaldırma 1 |

- Söylenen hatalar (1. + 2.), ilk oturum: baş 22, omuz 13, az kaldırma 12, öne kaçma 10, dirsek 10, doğru 5. İkinci oturum: omuz 10, öne kaçma 6, baş 6, doğru 2, dirsek 1, az kaldırma 1.
- Kalite sorunu olan tekrar: 0 / 56.
- `profiller/dogukan.npz` ikinci oturumun kalibrasyonudur; ilkinin profili üzerine yazıldı.
- Daha önceki iki oturum (`120254`, `121530`) arayüz sorunlarının bulunduğu denemelerdi (bkz. Kararlar ve sapmalar).

**Kullanıcının gözlemleri** (kendi sözleriyle özetlendi):
1. En çok öne kaçma ve baş hatası veriyor gibi; baş hafif eğilse bile hata algılanıyor.
2. Tanımlı olmayan "absürt" hareketlerde (örneğin iki kolu birden kaldırmak) sistem tanımlı hatalardan birini söylüyor.
3. Kameraya farklı açıdan durunca "açı hatası" yerine omuz ya da baş hatası çıkıyor.
4. Hız kontrolü yok: hareket çok hızlı yapılınca bunu söyleyen bir şey yok.
5. Dirseği bükmediği halde sık sık "dirsek" diyor. Kullanıcı, kalibrasyonda kendini çok sıkıp "dümdüz" yaptığını ve sistemin "en ufak hatayı affetmediğini" düşünüyor.

6. **Baş (ek yorum):** Başını belirgin eğdiği birkaç tekrarı sistem doğru yakaladı. Ama belirgin eğmediği tekrarlarda da baş hatası çıktı. Kalibrasyonu tam karşıya bakarak, değerlendirmeyi ise bilgisayar ekranına bakarak yaptı. Bakış yönünün değişmesinin baş hatasını tetiklediğini düşünüyor.

**Gözlemlerin verideki karşılığı:**
- **(5) Dar bant: doğrulandı.** Tanı aracı (`python -m araclar.bant_genisligi_tani --profil profiller/dogukan.npz` → `sonuclar/bant_genisligi/`) kullanıcının profilindeki τ medyanını, veri setinde aynı yöntemle (önden, her grubun ilk 6 doğru tekrarı, 55 grup) kurulan profillerle karşılaştırdı:

| ölçüt | veri seti τ medyanı (en küçük–en büyük) | kullanıcı τ | oran | kullanıcıdan dar grup /55 |
| --- | --- | --- | --- | --- |
| omuz (YENI) | 0.0131 (0.0065–0.0247) | 0.0126 | 0.9629 | 24 |
| baş | 1.1944 (0.5983–3.2745) | 0.9457 | 0.7917 | 10 |
| öne kaçma | 2.7368 (0.9203–4.3832) | 1.5527 | 0.5673 | 9 |
| kol boyu | 0.0295 (0.0187–0.0494) | 0.0242 | 0.8217 | 12 |
| dirsek | 3.4525 (1.3552–8.3441) | 1.7061 | 0.4942 | 2 |

  Kullanıcının dirsek bandı veri setindeki tipik bandın yaklaşık yarısı; 55 grubun yalnızca 2'si daha dar. Baş ve öne kaçma bantları da dar. τ = t·s/√n olduğu için tekdüze kalibrasyon dar bant, dar bant da küçük sapmalarda büyük z demek. Dikkat: kamera düzeni farklı (yatay dizüstü kamerası, yakın mesafe ve MediaPipe 1.2.2; veri seti ise dikey telefon). Fark kısmen buradan da gelebilir.
- **(3) Kamera açısı:** İlk oturumda tekrar 20 ve 22'nin kamera oranı 0.31 ve 0.23, yani eşiğin (0.3887) altında. Bu tekrarlarda baş, öne kaçma ve omuz z'leri 11–12'ye çıkmış. **Uygulama kamera açısı uyarısını yalnızca kalibrasyonda veriyor, değerlendirmede vermiyor.** Bu bir eksik.
- **(4) Hız:** 1,5 s'den kısa tekrar ilk oturumda 2, ikincide 1. Hata türleri veri setindeki 5 etiketle sınırlı; "çok hızlı" bir etiket değil, bu yüzden sistemde yok. Tekrar ayırıcı yalnızca 0,8 s'den kısa hareketi saymıyor.
- **(2) Tanımsız hareket:** Sistem yalnızca 5 hata türünü biliyor; bilinmeyen bir hareketi en yakın türe atıyor. Sınırlılık.
- **(1, 6) Baş:** İlk oturumda baş, söylenen hatalar arasında en sık olanı (22). Gerçek etiket olmadığı için yanlış alarm mı, gerçek eğme mi sayıyla ayırt edilemez. Kullanıcının açıklaması ölçütün tanımıyla tutarlı: `bas` = (omuz ortası → kulak ortası) ile (kalça ortası → omuz ortası) arasındaki açı (M39 F3). Gözleri kullanmaz, kulakları kullanır. Bakış tek başına etkilemez, ama ekrana bakmak için başı hafifçe çevirmek ya da öne eğmek 2B görüntüde kulak ortasını kaydırır. Kullanıcının baş bandı τ medyanı 0.9457°. Bu yüzden kalibrasyon ile değerlendirme arasında baş duruşunun 1–2° değişmesi bile bant dışına çıkabilir. Sonuç: baş ölçütü, kalibrasyon ve değerlendirme arasında **baş duruşunun (bakılan yerin) değişmesine** duyarlı. Bu, sistematik bir yanlış alarm kaynağı olabilir. Doğrulanmadı; Adım 7 çekiminde sınanabilir.

**Önemli:** Bu gözlemlere bakarak hiçbir eşik veya sabit değiştirilmedi. Kullanıcının verisi test verisidir (CLAUDE.md, deney dürüstlüğü). Öneriler aşağıda, danışmana.

## Demo talimatı (kullanıcı için, adım adım)
**Hazırlık (bir kez):**
1. Sanal ortamı aç: `.venv\Scripts\activate`.
2. Kurallar ve eşik dosyaları git'te hazır (`modeller/kural_ex1.json`, `modeller/kamera_esigi.json`). Yeniden üretmek istersen yukarıdaki iki komutu çalıştır.

**Kamera yerleşimi (Adım 7 çekim protokolüyle aynı):**
- Telefon ya da web kamerası göğüs hizasında, 2–2,5 m uzakta olsun. Tam karşıdan bak; en fazla 30° çapraz olabilir.
- Baştan kalçaya kadar bütün gövde ve yukarı kalkan sağ kol kadrajda olmalı.
- Arka plan sade olsun, ışık önden gelsin.
- Kamera açısı uyarısı ("Kameraya daha önden durun.") çıkarsa biraz kameraya dön. Uyarı kalibrasyonu durdurmaz.

**A) Canlı kamera (kabul ölçütü için gereken):**
1. `python -m uygulama.main --isim dogukan`
2. Pencere açılınca **bir kez pencereye tıkla.** Klavye kısayolları yalnızca pencere seçiliyken çalışır. Kısayollar zorunlu da değil: panelin altındaki düğmelere fareyle tıklanabilir.
3. İlk 10 saniye **HAZIRLIK** ekranıdır: yerine geçmen için bekleme süresi, hiçbir şey kaydedilmez (Boşluk ile atlanır). Ekranda "kalçaların kadrajda" yazısı yeşilse hazırsın. Görüntü ayna gibidir.
4. **Kalibrasyon:** Kolu yana, doğru şekilde, yavaşça kaldır, indir, 1–2 saniye bekle. Paneldeki **"Şimdi" kutusu** ne yapman gerektiğini ve anlık kol açını gösterir. Bir hareket sayılmazsa sebebini de söyler, örneğin "kol en fazla 45°'ye çıktı; en az 60° gerekli". Biten tekrar **8 saniye içinde reddedilmezse kendiliğinden kabul edilir**; bu yüzden klavyeye gitmen gerekmez. Kötü bir tekrarı **Reddet** düğmesi ya da **H** ile atarsın. 6 tekrar kabul edilince değerlendirme kendiliğinden başlar. 5 tekrardan sonra **Kalibrasyonu bitir (K)**, her şeyi baştan almak için **Baştan (B)**.
5. **Değerlendirme:** En az 5 tekrar yap: birkaç doğru, birkaç bilerek hatalı (omuz silkme, başı yana eğme, dirseği bükme, kolu az kaldırma). Ne yaptığını bir kağıda not et. Her tekrardan sonra panelde karar ve cümle çıkar; solda tekrar, bindirmeli olarak oynatılır.
6. Düğmeler / kısayollar: **Uzman ayrıntısı (U)**, **Son tekrarı oynat (R)**, **Çıkış (Q / Esc)**. Büyük/küçük harf fark etmez.
7. Çıkınca terminalde oturum CSV'sinin yolu yazar (`oturumlar/<tarih>.csv`). Profil `profiller/dogukan.npz` olarak kaydedilir.
8. Kayıtlı profille doğrudan değerlendirmek için: `python -m uygulama.main --profil profiller/dogukan.npz`.
9. Her tekrarı elle onaylamak istersen `--elle-onay` ekle; bekleme süresini değiştirmek için `--onay-suresi 6`.

**B) Video dosyası (birincil demo yolu, Karar 27):**
- `python -m uygulama.main --isim dogukan --kalibrasyon-video kalibrasyon.mp4 --video test.mp4`
  - Kalibrasyon videosundaki tekrarlar otomatik kabul edilir; videoda yalnızca doğru tekrarlar olmalı.
- Ya da `python -m uygulama.main --profil profiller/dogukan.npz --video test.mp4`. **Duraklat** düğmesi ya da **Boşluk** tuşu duraklatır.
- Pencere açmadan aynı değerlendirme: `python -m uygulama.toplu --profil profiller/dogukan.npz --video test.mp4`.

**Sunum yedeği (Karar 27):** Adım 7'deki kalibrasyon + test videosu ve onların yığın modu çıktısı (CSV) sunumdan önce hazır tutulacak.

**Bize göndermen gereken:** Canlı denemeden sonra terminalde yazan oturum CSV yolunu ve kısa bir gözlem (ör. "omuz silkmesini yakaladı, baş eğmeyi kaçırdı", "kalibrasyon sırasında uyarı çıktı / çıkmadı"). Bunlar ADIM_06'nın kabul bölümüne yazılacak.

## Kabul ölçütü kontrolü
- [x] Kullanıcı kendi kamerasıyla kalibrasyon yapıp en az 5 tekrar değerlendirdi: iki oturum, 6 + 6 kalibrasyon, 41 + 15 değerlendirme (Sonuçlar 6).
- [x] Video dosyası modu çalışıyor: yığın modu Honza videosunda uçtan uca çalıştı (sağlık kontrolü). Pencere modu (`--video`) aynı oturum kodunu kullanıyor; panel ve oynatım çizimi PNG'ye basılarak kontrol edildi. Pencerenin kendisi bu ortamda açılamadığı için **kullanıcının bir kez denemesi gerekiyor**.
- [x] Kopya kod yok: karar ve cümle yalnızca `cekirdek/` içinden (`degerlendirici.degerlendir`). Uygulama = Deney 3 testi geçiyor.

## Kararlar ve sapmalar
- **MediaPipe 1.2.2 kullanıldı, 0.10.20 değil (Karar 27).** 0.10.20'yi kurmak numpy'yi 2.4.6'dan 1.26.4'e indirip OpenCV'yi değiştirecekti (pip kuru çalıştırma). Bu, raporlanmış deneylerin ortamını bozardı. Fark ölçüldü: aynı Honza karelerinde kol açısı farkı medyan 0.92°, %95 3.09°. Sınırlılık olarak raporlanır.
- **MediaPipe VIDEO modu** kendi içinde kareler arası takip yapar. Bu, MediaPipe'ın bir parçası; bizim eklediğimiz bir yumuşatma değil. Karar 10 gereği biz yumuşatma eklemedik.
- **Sağlık kontrolünde kalibrasyon 5 tekrarla yapıldı.** Güncelleme 07 "ilk 6 doğru tekrar" diyor, ama Honza cam1 yönelim 0'da yalnızca 5 doğru tekrar var (1, 2, 3, 9, 10). En az sayı (5, Karar 8) kullanıldı.
- **Fonksiyon taşıma:** `deney2._model_puani`'nin v2 dalı ve `deney3.kod_uret` çekirdeğe taşındı. Sonuç dosyaları birebir aynı kaldı (yukarıda).
- **Tekrar ayırıcı ayrıntıları** (Karar 25'te açık bırakılanlar):
  - süre şartı 30° geçişi ile 20° geçişi arasında ölçülüyor;
  - bitiş araması 20° geçişinin kendisinden başlıyor;
  - başlangıç bir önceki tekrarın bitişinden geriye gidemez;
  - NaN kareler medyanda atlanıyor.
  - Not: dinlenme son 1 s'nin medyanı olduğu için "en fazla 2 s geri" sınırı NaN olmadıkça hiç bağlayıcı olmuyor; o 1 s'nin en az yarısı zaten sınırın altında.
- **Uygulamada tekrarın dinlenme payı:** Ayrılan tekrarın başına en fazla 10 kare (veri setindeki pay gibi) eklenir. Ölçütlerin dinlenme tabanı (ilk 8 kare) buradan gelir. Bant ve puan yalnızca ayrılan tekrar karelerinden hesaplanır.
- **Bindirme referansı:** Tepe açısı kalibrasyon medyanına en yakın kalibrasyon tekrarı. Zamansal hizalama DTW, geometrik hizalama `cekirdek/bindirme.py` (öteleme + ölçek + döndürme).
- **Canlı kamerada FPS:** Zaman eşikleri (0,8 s, 1 s, 2 s) ilk 3 saniyede ölçülen gerçek işleme hızına göre kare sayısına çevrilir.

- **Kullanılabilirlik düzeltmesi (kullanıcı geri bildirimi, 7 Kas):** Kullanıcı tuşların "çalışmadığını" bildirdi. Bulunan sebepler: (1) yalnızca küçük harf tanınıyordu (Caps Lock/Shift ile basılan E/H yok sayılıyordu); (2) tuşlar yalnızca pencere seçiliyken gelir, terminal seçiliyse gitmez; (3) E/H yalnızca bir tekrar ayrıldıktan sonra işe yarıyordu ve tekrar sayılmadığında (tepe < 60° ya da < 0,8 s) ekranda hiçbir açıklama yoktu; (4) kamerada 2 m uzaktaki kişinin her tekrarda klavyeye gitmesi pratik değil. Yapılanlar:
  - büyük/küçük harf fark etmiyor; Esc de çıkış;
  - panelde tıklanabilir düğmeler (Kabul, Reddet, Kalibrasyonu bitir, Baştan, Son tekrarı oynat, Uzman ayrıntısı, Duraklat, Çıkış);
  - pencere açılınca öne getiriliyor; terminale kısa kullanım yazısı basılıyor;
  - panelde **"Şimdi" kutusu**: anlık kol açısı göstergesi (30° ve 60° çizgili) ve yönerge ("Hazır: kolunu yana kaldır", "Tekrar sürüyor…", "Kolunu indir ve 1–2 saniye bekle", "Seni göremiyorum", "Bu hareket tekrar sayılmadı: …");
  - uygulanamayan bir tuş ya da düğme artık açıklayıcı bir mesaj veriyor (örneğin "Şu an onay bekleyen tekrar yok…");
  - **kalibrasyonda otomatik kabul:** biten tekrar 4 saniye içinde reddedilmezse kabul ediliyor (`--onay-suresi`, `--elle-onay` ile eski davranış). PLAN "kullanıcı her tekrarı onaylar veya reddeder" diyor. Ret hakkı duruyor, kabul örtük oluyor. Küçük bir arayüz sapması; danışmana not.
  - **Baştan** düğmesi: kalibrasyonu sıfırlar. Kalibrasyon bittiği anda hâlâ onay bekleyen tekrar `kullanilmadi` olarak işaretleniyor (önceden sonsuza kadar "onay bekliyor" kalıp panelde soruyu göstermeye devam ediyordu).
  - `cekirdek/tekrar_ayirici.py`'ye yalnızca okunur bilgi eklendi (`durum`, `anlik_tepe`, `son_gecersiz`). Ayırma kararı değişmedi; ayırıcı ve regresyon testleri geçiyor (tam pytest: 134 passed, 1 xfailed).
  - Panel, veri setindeki Honza dizisi kare kare verilerek dört durumda PNG'ye basılıp kontrol edildi. Bu sırada hasta cümlesi satırındaki bir çizim hatası bulunup düzeltildi.

- **Kamera görüş alanı (kullanıcı geri bildirimi, 7 Kas):** Kullanıcı görüntünün "zoomlu" olduğunu ve gövdenin altının kadraja girmediğini bildirdi. Sebep: OpenCV kamerayı varsayılan 640×480 (4:3) açıyor; 16:9 sensörlü kameralar bu modda görüntüyü kırpıyor. Canlı kamera artık 1280×720 isteniyor (`--cozunurluk`, örneğin `1920x1080`); istenen ve alınan çözünürlük terminale yazılıyor. Video alanı en fazla 1400 piksel genişliğe çıkarıldı (16:9'da 1351×760); pencere ilk açılışta ekrana sığacak şekilde boyutlandırılıyor. En-boy oranı her zaman gerçek kareden alındığı için (W/H) ölçümler etkilenmiyor. Not: kalibrasyon profili ile değerlendirme aynı çözünürlükte olmalı; farklıysa uygulama zaten uyarı veriyor.

- **İlk canlı deneme ve düzeltmeler (kullanıcı geri bildirimi, 7 Kas):** `oturumlar/2026-11-07_121530.csv` ve `profiller/dogukan.npz` incelendi (bu deneme kabul ölçütüne sayılmaz; değerlendirme tekrarı yok). 7 tekrar ayrıldı: 1. tekrar reddedildi, 6 tekrar kabul edildi. Kalibrasyon tekrarlarının tepe açısı 93.3, 89.5, 86.8, 95.3, 94.5 ve 6.'da NaN. Kullanıcı çubuktaki 30°/60° çizgilerini hedef aralık sandığı için kolu ~90°'de bırakmış (veri setinde doğru tekrar ~150°). 6. tekrarda kalçalar kadraj dışındaydı (kalça görünürlüğü medyanı 0.13 ve 0.12, y ≈ 1.23). Bu tekrar 4 s sonra kendiliğinden kabul edildi ve kalibrasyonu bitirdi. Yapılanlar:
  - **Kalite kontrolü** (`uygulama/oturum.py`, `kalite_sorunu`): tekrar boyunca omuz veya kalça görünürlüğünün medyanı < 0,5 ise tekrar kalibrasyona alınmaz ve sebebi panelde yazılır. Değerlendirmede tekrar yine değerlendirilir ama "sonuç güvenilir değil" uyarısı gösterilir. Sebep: kol açısı omuz–kalça çizgisine göre ölçülüyor ve ölçütler gövde boyuyla ölçekleniyor. Bu kontrol kullanıcının profilindeki 6. tekrarı yakalıyor, diğer 5 tekrarı geçiriyor. Sağlık kontrolünde (`toplu.saglik_kontrolu`) kapalı; raporlanmış sonuçlar değişmesin diye.
  - **Otomatik kabul süresi 4 s → 8 s.** "Son kabulü geri al (Z)" eklendi; değerlendirme tekrarı yokken kalibrasyon bittikten sonra da çalışır ("Kalibrasyona geri dön").
  - **Kol açısı çubuğu:** 30° çizgisi kaldırıldı. Yalnızca "en az 60° (sayılması için)" çizgisi var; değerlendirmede ayrıca "senin normalin X°" (kalibrasyon tepe medyanı). Kalibrasyonda tepe < 120° ise "kol genelde ~150°'ye kalkar; tam kaldırmadıysan Reddet" hatırlatması çıkıyor. 120° yalnızca arayüz hatırlatmasıdır; karar kuralına girmez.
  - **Hazırlık ekranı:** 3 s → 10 s (`--hazirlik`, Boşluk ile atlanır). Ekranda bunun kalibrasyon olmadığı, hiçbir şeyin kaydedilmediği yazıyor. Canlı "kalçaların görünüyor / görünmüyor" kontrolü var. FPS ölçümü bu sürede yapılıyor.
  - **Ayna görüntü:** canlı kamera varsayılan olarak ayna gibi gösteriliyor (`--aynasiz` ile kapanır). Yalnızca gösterim; MediaPipe ve ölçümler aynasız kareyi kullanıyor (sağ kol = MediaPipe 12/14/16 değişmedi). Video dosyası modunda ayna yok.
  - Oturum CSV'sine `tepe_aci` ve `kalite` sütunları eklendi.
  - Tam pytest: 134 passed, 1 xfailed.

## Açık sorular / danışmana notlar
- Tüm görüşlerde tekrar ayırma 87.35 (< %90); önden + çapraz 95.01. Karar 25 gereği eşikler değişmedi. Uygulama senaryosu |görüş| ≤ 60° olduğu için sorun görmüyoruz; onay?
- MediaPipe 1.2.2 farkı (kol açısında medyan 0.92°) sınırlılık notu olarak yeterli mi?
- **Canlı denemeden çıkan öneriler (karar danışmanın; hiçbiri uygulanmadı):**
  1. **Bant için en az genişlik.** Örneğin τ ≥ veri setindeki τ dağılımının bir yüzdeliği. Bu bir yöntem değişikliği; Deney 2 üzerinde birini-dışarıda-bırak ile sınanmadan uygulamaya girmemeli (alt sınır 4 kişiden, 5. kişide test).
  2. **Değerlendirmede kamera açısı uyarısı.** Karar 26 eşiği (0.3887) her değerlendirme tekrarının kamera oranına da uygulanır: "Kameraya göre açın değişti; bu sonuç güvenilir değil." Yeni eşik yok, yalnızca arayüz.
  3. **Hız (tempo) bilgisi.** Örneğin "çok hızlı yaptın, yavaşla". Veri setinde etiketi yok, ölçülemez. Eşik, veri setindeki doğru tekrarların süre dağılımından (örneğin %5'lik dilim) alınabilir ve yalnızca bilgi olarak gösterilir.
  4. **Tanınmayan hareket.** Örneğin sol kolun da kalkması ya da birçok ölçütün aynı anda çok yüksek olması: "Hareket tanınmadı" denir. Etiketi yok, ölçülemez.
  5. **Kalibrasyon yönergesi.** "Doğal, rahat tekrarlar yap; kendini zorlama." Dar bandı biraz azaltabilir ama çözmez.
  6. **Bakış yönü yönergesi** (eşik değil, yalnızca talimat): "Kalibrasyonda da değerlendirmede de aynı yere bak (ekrana)." Adım 7 çekim protokolüne de eklenebilir: kalibrasyon ve test videosunda kişi aynı noktaya baksın. İstenirse Adım 7'de bilerek "farklı yere bakma" tekrarları çekilir ve etkisi ölçülür.
- Kalibrasyonda 8 saniyelik otomatik kabul (ret hakkı saklı) PLAN'daki "her tekrarı onaylar" ifadesine uygun sayılır mı?
