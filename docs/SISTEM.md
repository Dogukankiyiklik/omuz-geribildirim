# Sistem nasıl çalışıyor?

Bu belge, uygulamanın bir videoyu alıp Türkçe cümleye çevirene kadar ne yaptığını **koddan** anlatır. Başlıklar 1 sayfalık rapor şablonundaki 7 adımı izler. Sayılar ve sabitler koddaki değerlerdir; her adımın yanında hangi dosyada olduğu yazılı.

## Bir paragrafta

Kişi önce kolunu **6 kez doğru** kaldırır (kalibrasyon). Sistem bu tekrarlardan "kolun her açısında bu kişinin omzu, başı, dirseği normalde nerede?" sorusunun cevabını çıkarır: buna **açı bandı** diyoruz. Sonraki her tekrarda beş ölçü bu bandla karşılaştırılır; banttan en çok taşan ölçü hatanın türünü verir (omuz silkmesi, baş eğme, kolun öne kaçması, dirsek bükme, yetersiz kaldırma). Bulunan hata, derecesiyle birlikte kısa bir Türkçe cümleye çevrilir. Tekrar bitince kişinin iskeleti, kendi kalibrasyon tekrarından alınmış referans iskeletle zamanda ve geometride hizalanıp üst üste oynatılır; banttan çıkan uzuv kırmızı çizilir.

```
kamera / video
   │
   ▼
MediaPipe Pose (33 nokta, 2B)  ─►  kol açısı  ─►  tekrar ayırma
                                                     │
                     ┌───────────────────────────────┴────────────────────────────┐
             KALİBRASYON (ilk 6 doğru tekrar)                         DEĞERLENDİRME (sonraki her tekrar)
                     │                                                             │
             açı bandı: her ölçü için                              5 ölçü → banttan taşma puanı (E)
             kol açısı kutusu başına μ ± τ  ───────────────────►   → z → karar (doğru / hangi hata)
                                                                   → sapma kodu → Türkçe cümle
                                                                   → bindirmeli oynatım (DTW + öteleme/ölçek/döndürme)
                                                                   → panel + CSV
```

## 1. Ortam ve kütüphaneler

- Python 3.11 (sınandığı: 3.11.9, Windows 11). Tam paket listesi: [`SURUMLER.md`](SURUMLER.md).
- Kritik paketler: `mediapipe==1.2.2`, `opencv-python`, `numpy`, `scipy`, `pandas`, `matplotlib`, `pillow`. `numba` isteğe bağlı: yalnızca DTW'yi hızlandırır, sonucu değiştirmez.
- GPU gerekmez.

## 2. Video / kamera girdisi

`uygulama/main.py`

- Canlı kamera 1280×720 istenir (OpenCV'nin varsayılanı 640×480 görüntüyü kırpıyor) ya da bir video dosyası açılır.
- **En-boy düzeltmesi:** MediaPipe x'i görüntü genişliğine, y'yi yüksekliğe böler. Açı ve mesafe doğru çıksın diye x, genişlik/yükseklik oranıyla çarpılır (`cekirdek/geometri.py`, `nokta`). Veri setinin dikey videolarında bu oran 9/16'dır.
- **Kadraj kontrolü:** omuzlar ve kalçalar görünmüyorsa (MediaPipe görünürlüğü < 0,5) tekrar kalibrasyona alınmaz (`uygulama/oturum.py`, `kalite_sorunu`).
- **Kamera açısı uyarısı:** dinlenmedeki omuz genişliği / gövde boyu oranı 0,389'un altındaysa (kişi kameraya fazla yan duruyor) "Kameraya daha önden durun" uyarısı çıkar; karar yine verilir (`cekirdek/kamera_acisi.py`, eşik `modeller/kamera_esigi.json`).

## 3. Pose / landmark çıkarımı

`uygulama/poz.py`

- MediaPipe Tasks `PoseLandmarker`, model `pose_landmarker_full.task` (ilk çalıştırmada `modeller/` altına indirilir), VIDEO modu, tek kişi.
- Kare başına 33 nokta × (x, y, z, görünürlük). **Yalnızca 2B (x, y) kullanılır**; z derinlik tahmini güvenilir değil.
- Kullanılan noktalar: 0 burun, 2/5 gözler, 7/8 kulaklar, 11/12 omuzlar, 13/14 dirsekler, 15/16 bilekler, 23/24 kalçalar. Egzersizi **sağ kol** yapar.
- Zamansal yumuşatma **yok**: denendi, titremeyi azalttı ama tespiti iyileştirmedi ([`DENEYLER.md`](DENEYLER.md), "Denenip işe yaramayanlar").

## 4. Ölçüm, tekrar ayırma, kalibrasyon ve açı bandı

### 4a. Kol açısı
Sağ üst kol (omuz → dirsek) ile aşağı dikey arasındaki açı: kol yanda 0°, yatayda 90°, başın üstünde 180° (`cekirdek/ozellikler.py`, `kol_acisi`). Sistemdeki her şey bu açıya göre düzenlenir.

### 4b. Tekrar ayırma
`cekirdek/tekrar_ayirici.py`. Kol açısı 5 karelik hareketli medyanla yumuşatılır. Açı **30°'yi geçince** tekrar başlar, **20°'nin altına inince** biter. Geçerli sayılması için tepe ≥ 60° ve süre ≥ 0,8 s olmalı. Sınırlar dinlenme hâline kadar uzatılır.

### 4c. Beş ölçü (her hata türü için bir tane)
`cekirdek/ozellikler.py`. Uzunluklar kişinin **dinlenmedeki gövde boyuna** (omuz ortası – kalça ortası, tekrarın ilk 8 karesinin medyanı) bölünür; böylece kameraya uzaklık ve boy farkı ölçüyü etkilemez. (Omuz genişliğine bölünmez: yan görünümde omuz genişliği sıfıra iner.)

| Hata | Ölçü (koddaki adı) | Nasıl hesaplanır | Hata hangi yönde |
| --- | --- | --- | --- |
| Omuz silkmesi | `YENI` | sağ omuz ile sağ kulak arasındaki **dikey** mesafe / gövde boyu | küçülür (omuz kulağa yaklaşır) |
| Baş yana eğme | `bas` | (omuz ortası → kulak ortası) ile (kalça ortası → omuz ortası) arasındaki açı | büyür |
| Kolun öne kaçması | `kol_boyu` | sağ omuz – sağ bilek mesafesi / gövde boyu (öne giden kol kamerada kısa görünür) | küçülür |
| Dirsek bükme | `dirsek` | omuz – dirsek – bilek açısı (180° = düz kol) | küçülür |
| Yetersiz kaldırma | `kaldirma` | tekrarın en yüksek kol açısının, kalibrasyon tepelerinin medyanından eksiği | eksik büyür |

"Hata hangi yönde" sütunu elle yazılmadı; veri setinde hatalı ve doğru tekrarların ortalama farkından öğrenildi (`cekirdek/hata_turu.py`, `beklenen_yonler`; değerler `modeller/kural_ex1.json` içinde `yonler`).

### 4d. Kalibrasyon
`uygulama/oturum.py`. Kişi 6 doğru tekrar yapar (en az 5). Biten tekrar 8 saniye içinde reddedilmezse kendiliğinden kabul edilir. Tekrarlar `profiller/<isim>.npz` dosyasına kaydedilir; bir sonraki sefer `--profil` ile doğrudan değerlendirmeye geçilir.

### 4e. Açı bandı (yöntemin kalbi)
`cekirdek/aci_bandi.py`

**Fikir:** Doğru yapılan harekette de omuz bir miktar kalkar (kürek kemiği döner). Bu yüzden "omuz şu kadar kalkarsa hata" diyen sabit bir eşik işe yaramaz. Doğru soru şudur: *Kol θ derecedeyken bu kişinin omzu normalde nerede?*

**Nasıl kurulur:**
1. Her kalibrasyon tekrarı iki faza ayrılır: tepeye kadar **kaldırma**, sonrası **indirme**.
2. Kol açısı 0–180° arası **5°'lik kutulara** bölünür (faz başına 36 kutu).
3. Her tekrar her kutuya bir değer verir (o kutuya düşen karelerin ortalaması).
4. Her kutu için ortalama **μ** ve tolerans **τ = t(0,975; n−1) · s / √n** (n: o kutuya katkı veren tekrar sayısı, s: standart sapma). τ, çok dar olmasın diye bütün kutulardaki τ'ların birinci çeyreğinden küçük olamaz.
5. En az 3 tekrarın katkı verdiği kutular geçerlidir; aradaki boşluklar doğrusal ara değerle doldurulur. Kalibrasyonda hiç görülmemiş kol açıları değerlendirilmez (o açıda kişinin normalini bilmiyoruz).

Bant fikri, μ ve τ'nun tanımı ve τ'ya alt sınır **Jánošová ve ark. (2026)**'dan alındı. Onlar tekrarları **zamanda** (DTW ile) hizalıyordu; bizim değişikliğimiz karşılaştırmayı **kol açısına** göre yapmak. Böylece kol farklı yüksekliğe kalksa da omuz aynı kol açısında karşılaştırılır. **Puanlamada DTW kullanılmaz**; DTW yalnızca bindirmede (7. adım) var.

## 5. Hata / farkın hesaplanması

`cekirdek/aci_bandi.py`, `cekirdek/hata_turu.py`, `cekirdek/degerlendirici.py`

1. **Kare hatası:** her karede ölçü kendi kutusunun bandıyla karşılaştırılır. Bant içindeyse 0; dışındaysa (sapma − τ)/τ, en fazla 1. Yalnızca hatanın beklenen yönündeki taşma sayılır (örneğin omuzda yalnızca kulağa yaklaşma).
2. **Tekrar puanı E:** kare hatalarının ortalaması (0 = hep bant içinde, 1 = hep çok dışında). Yetersiz kaldırmada puan d = (kalibrasyon tepelerinin medyanı − tekrarın tepesi) / max(tepelerin çeyrekler arası açıklığı, 5°).
3. **Ortak ölçeğe çevirme:** beş puan farklı birimde olduğu için z = (puan − medyan) / (çeyrekler arası açıklık + 0,01). Medyan ve açıklık, veri setindeki **doğru** tekrarların puanlarından gelir.
4. **Karar:** en büyük z, **T = 3,80** eşiğinin altındaysa → "doğru". Değilse en büyük z'li hata söylenir; ikinci en büyük z de T'yi geçerse ikinci hata da söylenir (en fazla 2).

**Bu sistem iki katmanlıdır; bunu açıkça söylemek önemli:**
- **Kişiye özel katman:** açı bandı (μ, τ) yalnızca o kişinin kalibrasyonundan gelir.
- **Ortak katman:** z ölçeği (medyan, açıklık), hata yönleri ve T eşiği veri setindeki 5 kişiden öğrenildi. T, hata türü doğruluğunu (makro-F1) en yükseğe çıkaran değer olarak seçildi.
- Deneylerde bu ortak katman **4 kişide öğrenilip 5. kişide sınandı** (kişi bazlı birini-dışarıda-bırak). Uygulamada ise 5 kişinin hepsiyle aynı yöntemle bir kez kuruldu: `python -m araclar.kural_disa_aktar` → `modeller/kural_ex1.json`.

**Şiddet** (hafif / belirgin / çok belirgin) puanın eşiklerle karşılaştırılmasından gelir (`kural_ex1.json`, `siddet_esikleri`) ve yalnızca uzman ayrıntısında kullanılır.

## 6. Doğal dil geri bildirimi

`cekirdek/geribildirim.py`

- Bulunan her hata önce bir **sapma kodu**na çevrilir: hata türü, taraf (sağ), faz (kaldırırken / yukarıdayken / indirirken), yön, şiddet, ölçü (derece) ve kişinin normal değeri.
- Kod, kurallarla iki katmanlı Türkçe metne dönüşür:
  - **Hasta cümlesi** (uygulamada büyük yazı): ne oldu + ne yapmalı; sayı yalnızca 5°'ye yuvarlanmış derece.
  - **Uzman ayrıntısı** (`U` tuşu): "normalde X, sende Y" biçiminde ölçülü.
- **LLM kullanılmaz;** cümleler tamamen kural tabanlıdır.
- Kendi kaydımızdan gerçek çıktılar (`sonuclar/kendi_kayit/kisi1/tekrarlar.csv`):
  - Az kaldırma: *"Kolunu 110 dereceye kadar kaldırdın; normalde 140 dereceye çıkıyorsun. Kolunu yaklaşık 30 derece daha yukarı kaldır."*
  - Omuz silkmesi: *"Kolunu kaldırırken sağ omzunu kulağına doğru yaklaşık 10 derece kaldırdın. Omzunu aşağıda ve gevşek tut."*
  - Baş eğme: *"Kolun yukarıdayken başını yaklaşık 30 derece yana eğdin. Başını dik tut, karşıya bak."*
  - Doğru tekrar: *"Hareketi doğru yaptın. Kolun yaklaşık 145 dereceye çıktı, omzun ve dirseğin yerindeydi."*
- Silkme cümlesindeki "derece", omuz çizgisinin gövde eksenine göre eğiminin kişinin normaline göre farkıdır (`omuz_egim` ölçüsü; yalnızca anlatım için, karara girmez).
- **Bilgi notları** (hata değil, karara girmez): tekrar çok hızlıysa hız notu, sol kol da kalktıysa "yalnızca sağ kolunu kaldır", kamera açısı uyarısı (`cekirdek/bilgi_notlari.py`).

## 7. Çıktının gösterilmesi ve kaydı

`uygulama/panel.py`, `cekirdek/bindirme.py`

- **Ekran:** solda video ve canlı iskelet, sağda panel (karar, hasta cümlesi, omuz eğrisi ve normal aralığı).
- **Bindirmeli oynatım (Problem 3):** her tekrar bitince o tekrar yeniden oynatılır; kişinin iskeletinin üstüne yarı saydam bir referans iskelet çizilir.
  - **Referans:** kalibrasyon tekrarlarından, tepe açısı kalibrasyon medyanına en yakın olanı (`uygulama/oturum.py`, `referans`).
  - **Zamansal hizalama:** iki tekrarın kol açısı eğrileri DTW ile eşlenir (z-normalize; `cekirdek/hizalama.py`). Kullanıcının her karesine referansın "aynı andaki" karesi bulunur. Örneğin kullanıcı yavaş kaldırdıysa referansın bir karesi kullanıcının birkaç karesine eşlenir.
  - **Geometrik hizalama:** referans iskelet (a) kalça ortası kullanıcının o karedeki kalça ortasına **ötelenir**, (b) dinlenme gövde boylarının oranıyla **ölçeklenir**, (c) dinlenme gövde eksenlerinin açı farkı kadar **döndürülür**. Ölçek ve döndürme kare kare değil, tekrar başında bir kez hesaplanır: kare kare gövde boyuna ölçekleseydik omuz kalkınca gövde de "uzayacağı" için silkme referansa da taşınır ve görünmez olurdu.
  - **Renk:** o karede bandın dışında kalan ölçünün uzvu kırmızı (ör. omuzda kulak–omuz çizgisi).
- **Kayıt:** her tekrarın kararı, cümleleri ve z'leri `oturumlar/<tarih>.csv` dosyasına, kalibrasyon `profiller/<isim>.npz` dosyasına yazılır (ikisi de git'e girmez). Pencere açmadan CSV üretmek için `python -m uygulama.toplu`.

---

## Sık sorulan sorular

**Neden MediaPipe'ın omuz noktası tek başına yetmiyor?** Doğru harekette de omuz noktası yukarı kayıyor. Sabit eşikli ham ölçü silkmeyi zayıf ayırıyor (AUC 0,70); kişinin kendi normaline göre değerlendirince 0,95 oluyor ([`DENEYLER.md`](DENEYLER.md), Soru 1).

**Omuza özel iyileştirme ne?** İki şey: (1) omzu kulağa göre ölçmek (omuz noktasını tek başına değil, kafaya göre); (2) asıl katkı olarak bu ölçüyü **kol açısına koşullu, kişiye özel** bir bantla değerlendirmek. Ödevde sayılan "kol elevasyonu ile omuz/skapula hareketi arasındaki ilişki" tam olarak bu. Ödevde önerilen yumuşatma ve omuz bölgesi (siluet) de denendi, ikisi de bu yöntemden iyi çıkmadı.

**Referans video kimin?** Kişinin kendi kalibrasyon tekrarları. Başkasının tekrarlarından kurulan "genel" bant çok daha kötü çalıştı (0,62–0,67'ye karşı 0,95). Yani referans bilerek kişiye özel.

**DTW nerede kullanılıyor?** Yalnızca bindirmede (iki tekrarı zamanda eşlemek için). Hata puanı kol açısına göre hesaplandığı için puanlamada zaman hizalamasına gerek kalmıyor.

**Eşikler nereden geliyor?** Bant kişinin kendisinden. Ortak eşik T ve z ölçeği veri setinden; deneylerde test kişisi bu ayara hiç girmedi (4 kişide ayarla, 5. kişide sına).

**Bindirmede referans aynı kişiyse geometrik hizalama ne işe yarıyor?** Kişi kalibrasyonda ve testte farklı yerde durabilir, kameraya yaklaşabilir; öteleme ve ölçek bunu düzeltir. Kod (`Bindirici`) iki farklı kişinin tekrarını da alacak şekilde yazıldı; arayüzde yalnızca kişinin kendi referansı seçiliyor.

**Neden profil (tam yan) kamera yok?** Yana kaldırma, yandan bakan kamerada kameraya doğru bir harekete dönüşüyor; 2B kol açısı bozuluyor. Önerilen kurulum: önden ya da hafif çapraz (en fazla ~60°).

## Literatürden alınanlar

Kodda makaleler M numarasıyla anılır (ör. `M39`). Bu tablo yalnızca yöntemde gerçekten kullanılanları verir.

| Kodda | Makale | Ne alındı |
| --- | --- | --- |
| M39 | Jánošová ve ark., 2026 — Impact of Patient Orientation… (REHAB26-ViewAngles) | Veri seti; kişiye özel tolerans bandı (μ, τ, τ alt sınırı, kare hatası); baş, dirsek, kol ölçülerinin tanımları (F1–F4) |
| M01 | Pavlikov ve ark., 2026 — Markerless On-Device Detection of Compensatory Movement Patterns… | Kol açısı tanımı; omuz yükselmesinin tek kamerada en zor işaret olduğu; "normal hareket de omzu kaldırır" sorunu; faz fikri; en-boy düzeltmesi uyarısı |
| M33 | Cóias ve ark., 2022 — A low-cost virtual coach… | Omzu boyna göre ölçme fikri; kural tabanlı telafi tespiti ve geri bildirim |
| M22 | Sarsfield ve ark., 2019 — Segmentation of Exercise Repetitions… | z-normalize DTW |
| M45 / E2 | Delmas ve ark., 2024 (PoseScript) ve PoseFix | Pozdan / poz farkından kurallarla cümle üretme (sapma kodu fikri) |
| M23 | Ye ve ark., 2026 — Perception, assessment, and coaching… | Sonuç bilgisi (skor) yerine performans bilgisi (hangi eklem, hangi faz, nasıl düzelt) vermek |
| E1 | Fieraru ve ark., 2021 — AIFit | Referansa göre sapmayı doğal dilde söyleyen en yakın öncül |
