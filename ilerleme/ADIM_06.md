# ADIM 06 — Uygulama

**Tarih:** 2026-11-07
**Durum:** Kısmen. Uygulama, yığın modu ve sınamalar hazır. Sağlık kontrolü geçti. **Kabul ölçütü bekleniyor:** kullanıcının kendi kamerasıyla kalibrasyon yapıp en az 5 tekrar değerlendirmesi (aşağıdaki demo talimatı).

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
2. İlk 3 saniye "Hazırlanın" yazar; bu sırada yerine geç. Uygulama bu sürede bilgisayarın hızını ölçer.
3. **Kalibrasyon:** Kolu yana, doğru şekilde, yavaşça kaldırıp indir. Her tekrar arasında kolunu 1–2 saniye aşağıda dinlendir; ayırıcı tekrarın bittiğini kol aşağı inince anlar. Her tekrardan sonra panelde "Kalibrasyona alınsın mı?" çıkar: **E** evet, **H** hayır. 6 tekrar kabul edilince değerlendirme kendiliğinden başlar. 5 tekrardan sonra **K** ile erken bitirebilirsin.
4. **Değerlendirme:** En az 5 tekrar yap: birkaç doğru, birkaç bilerek hatalı (omuz silkme, başı yana eğme, dirseği bükme, kolu az kaldırma). Her tekrardan sonra panelde karar ve cümle çıkar, solda tekrar bindirmeli olarak oynatılır.
5. **U** uzman ayrıntısını açar, **R** son tekrarı yeniden oynatır, **Q** çıkar.
6. Çıkınca terminalde oturum CSV'sinin yolu yazar (`oturumlar/<tarih>.csv`). Profil `profiller/dogukan.npz` olarak kaydedilir.
7. Kayıtlı profille doğrudan değerlendirmek için: `python -m uygulama.main --profil profiller/dogukan.npz`.

**B) Video dosyası (birincil demo yolu, Karar 27):**
- `python -m uygulama.main --isim dogukan --kalibrasyon-video kalibrasyon.mp4 --video test.mp4`
  - Kalibrasyon videosundaki tekrarlar otomatik kabul edilir; videoda yalnızca doğru tekrarlar olmalı.
- Ya da `python -m uygulama.main --profil profiller/dogukan.npz --video test.mp4`. **Boşluk** tuşu duraklatır.
- Pencere açmadan aynı değerlendirme: `python -m uygulama.toplu --profil profiller/dogukan.npz --video test.mp4`.

**Sunum yedeği (Karar 27):** Adım 7'deki kalibrasyon + test videosu ve onların yığın modu çıktısı (CSV) sunumdan önce hazır tutulacak.

**Bize göndermen gereken:** Canlı denemeden sonra terminalde yazan oturum CSV yolunu ve kısa bir gözlem (ör. "omuz silkmesini yakaladı, baş eğmeyi kaçırdı", "kalibrasyon sırasında uyarı çıktı / çıkmadı"). Bunlar ADIM_06'nın kabul bölümüne yazılacak.

## Kabul ölçütü kontrolü
- [ ] Kullanıcı kendi kamerasıyla kalibrasyon yapıp en az 5 tekrar değerlendirdi (**bekleniyor**).
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

## Açık sorular / danışmana notlar
- Tüm görüşlerde tekrar ayırma 87.35 (< %90); önden + çapraz 95.01. Karar 25 gereği eşikler değişmedi. Uygulama senaryosu |görüş| ≤ 60° olduğu için sorun görmüyoruz; onay?
- MediaPipe 1.2.2 farkı (kol açısında medyan 0.92°) sınırlılık notu olarak yeterli mi?
