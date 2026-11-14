# Sunuma hazırlık: her şeyin açıklaması

Bu dosya, sunumu ve canlı demoyu yapacak kişi (sen) için yazıldı. Baştan sona bir kez okuyunca projenin ne yaptığını, her sayının nereden geldiğini, hangi makaleden ne alındığını ve gelebilecek sorulara ne cevap vereceğini bilmiş olursun. Jargon ilk geçtiği yerde açıklanıyor; ayrıca 4. bölümde küçük bir sözlük var.

- Sunum: 16 Kasım 2026, 5 dakika. Slaytlar: https://claude.ai/artifact/1upSPPq9oUYNJhikbSmk1q (sayfanın Paylaş › Dışa aktar menüsünden PowerPoint ya da PDF olarak indirilir).
- Rapor: [`RAPOR.docx`](RAPOR.docx) (hocanın şablonu doldurulmuş hâli, 1 sayfa) ve aynısının [`RAPOR.pdf`](RAPOR.pdf) kopyası.
- Bu dosyadaki her sayı bir sonuç dosyasından kopyalandı; yanında köşeli parantez içinde kaynağı yazıyor (`sonuclar/` altına göre yol).

## 1. Proje 30 saniyede

Tek bir kamerayla **kolu yana kaldırma** egzersizini izleyen bir uygulama yaptım. Kişi önce kolunu 6 kez doğru kaldırıyor; sistem bundan o kişinin "normalini" öğreniyor. Sonraki her tekrarda sistem üç şey yapıyor:

1. Tekrar doğru mu, değilse **hangi hata** var, onu buluyor. Odak omuz silkmesi (omzun kulağa doğru kalkması); ayrıca baş eğme, kolun öne kaçması, dirsek bükme ve az kaldırma.
2. Hatayı **derecesiyle, Türkçe bir cümleyle** söylüyor: *"Kolunu 110 dereceye kadar kaldırdın; normalde 140 dereceye çıkıyorsun. Kolunu yaklaşık 30 derece daha yukarı kaldır."*
3. Kişinin doğru tekrarını, yeni tekrarın **üstüne bindirip** oynatıyor; hatalı uzuv kırmızı görünüyor.

Yöntemin kalbi tek cümle: **"Kol şu açıdayken bu kişinin omzu normalde nerede?"** Buna *kişiye özel açı bandı* diyoruz.

## 2. Ödev ne istiyordu, biz ne yaptık?

Ödev üç problemden en az birini çözen çalışan bir uygulama istiyor. Üçünü de aynı uygulamada çözdük.

| Problem | Ödevin istediği | Bizdeki karşılığı | "Yeterli değil" dediği şeyi nasıl aştık |
| --- | --- | --- | --- |
| **P1** Doğruluk ve doğal dil | Ölçüm, hatalı bölge, hata büyüklüğü, düzeltme cümlesi, doğruda olumlu cümle | 5 ölçü, 5 hata türü, derece içeren Türkçe cümle, doğru tekrarda olumlu cümle | Yalnızca iskelet çizmiyoruz, "%85 doğru" demiyoruz; fiziksel ölçü (derece) ve ne yapılacağı söyleniyor |
| **P2** Omuzun hassas ölçümü | Standart pozun sınırını göster, omuza özel en az bir iyileştirme yap, yorumlanabilir ölçü ver, mümkünse karşılaştır | Sınır: ham ölçü AUC 0,70. İyileştirme: kulak–omuz ölçüsü ve kişiye özel açı bandı (0,95). Karşılaştırma tablosu var | MediaPipe'ın omuz noktasının piksel farkını raporlamıyoruz; omzu kulağa göre ve kişinin kendi normaline göre değerlendiriyoruz |
| **P3** Bindirme | Zamansal hizalama, geometrik hizalama, iki iskelet aynı videoda, hatalı bölge görünür | DTW (zaman) + öteleme, ölçek, döndürme (geometri); turkuaz referans, kırmızı hatalı uzuv | Videoları yan yana koymuyoruz, aynı kare numaralarını üst üste çizmiyoruz |

**Açıkça söyleyeceğin iki tercih** (hoca derste bunların sorun olmadığını söyledi; yine de gerekçeleriyle söyle):

- **Hareket yoga değil, omuz egzersizi.** Problem 2 zaten omuzu istiyor. Aynı hareketi seçince üç problem tek uygulamada birleşti.
- **Referans başkasının videosu değil, kişinin kendi 6 doğru tekrarı.** Bu bir kolaylık değil, ölçülmüş bir karar: bandı başka 4 kişinin tekrarlarından kurunca omuz silkmesini ayırma başarısı 0,67'de kalıyor, kişinin kendi tekrarlarından kurunca 0,95 oluyor [`deney1/ozet.csv`]. Çünkü herkesin omzu, boynu, duruşu farklı; "doğru"nun yeri kişiden kişiye değişiyor.

## 3. Sistem adım adım (ve her adımın nedeni)

Aşağıdaki sıra, raporun 7 adımıyla aynı. Her adımın kodu `cekirdek/` altında; uygulama da deneyler de **aynı kodu** kullanıyor. Bunun anlamı: deneyde ölçtüğümüz başarı, uygulamanın gerçekten verdiği kararın başarısı.

### 3.1 Ortam
Python 3.11.9, MediaPipe 1.2.2, OpenCV 5.0.0.93, NumPy 2.4.6, SciPy 1.17.1, pandas 3.1.1 [`docs/SURUMLER.md`]. Ekran kartı (GPU) gerekmiyor.

### 3.2 Girdi
- Canlı kamera (1280×720) ya da video dosyası.
- **En-boy düzeltmesi:** MediaPipe bir noktanın x'ini görüntünün genişliğine, y'sini yüksekliğine bölerek 0–1 arası verir. Görüntü kare değilse x ve y farklı ölçekte olur ve açılar bozulur. Bu yüzden her şeyden önce x'i genişlik/yükseklik oranıyla çarpıyoruz. (Bu uyarı Pavlikov ve ark.'ta da var: düzeltilmezse ölçüler en-boy oranına göre 24–36° oynuyor, s. 9.)
- **Kamera nerede durmalı:** önden ya da hafif çapraz (en fazla ~60°). Tam yandan bakınca kolu yana kaldırmak kameraya doğru bir harekete dönüşüyor ve 2B'de görünmüyor. Kişi fazla yan durursa uygulama "Kameraya daha önden durun" uyarısı veriyor (dinlenmede omuz genişliği / gövde boyu < 0,389 ise) [`modeller/kamera_esigi.json`].

### 3.3 Poz çıkarımı
MediaPipe Pose Landmarker, "full" model, her karede 33 nokta. Yalnızca **2B (x, y)** kullanıyoruz; z (derinlik) tek kameradan tahmin edildiği için güvenilir değil. Kullandığımız noktalar: kulaklar, omuzlar, sağ dirsek, sağ bilek, kalçalar. Egzersizi **sağ kol** yapıyor.

### 3.4 Kol açısı ve tekrar ayırma
- **Kol açısı:** sağ üst kol (omuz → dirsek) ile aşağı doğru dikey arasındaki açı. Kol yandayken 0°, yataydayken 90°, başın üstünde 180°. (Tanım Pavlikov ve ark.'tan, Denklem 5.)
- **Tekrar ayırma:** kol açısı 30°'yi geçince tekrar başlıyor, 20°'nin altına inince bitiyor. Sayılması için tepe en az 60°, süre en az 0,8 s olmalı. İki ayrı eşik (30 ve 20) kullanmamızın nedeni, açı eşiğin etrafında titrerken tekrarın bir başlayıp bir bitmemesi.

### 3.5 Beş ölçü
Her hata türünün bir ölçüsü var. Uzunlukları kişinin dinlenmedeki **gövde boyuna** (omuz ortası – kalça ortası) bölüyoruz; böylece kameraya yakın ya da uzak durmak ölçüyü değiştirmiyor.

| Hata | Ölçü | Hata olunca ne olur |
| --- | --- | --- |
| Omuz silkmesi | Sağ kulak ile sağ omuz arasındaki **dikey** mesafe / gövde boyu | Küçülür (omuz kulağa yaklaşır) |
| Baş yana eğme | Baş ekseni ile gövde ekseni arasındaki açı | Büyür |
| Kolun öne kaçması | Omuz – bilek mesafesi / gövde boyu | Küçülür (öne giden kol kamerada kısa görünür) |
| Dirsek bükme | Omuz – dirsek – bilek açısı (180° = düz kol) | Küçülür |
| Az kaldırma | Tekrarın en yüksek kol açısı | Kalibrasyondaki tepeden eksik kalır |

**Neden kulak–omuz?** MediaPipe'ın omuz noktasına tek başına bakmak yerine omzu **kafaya göre** ölçüyoruz. Omzu boyna göre ölçme fikri Cóias ve ark.'tan (omuz yükselmesini boyun eklemine göre yer değiştirmeyle değerlendiriyorlar, s. 9).

### 3.6 Açı bandı (yöntemin kalbi)

**Sorun:** Kolunu doğru kaldırdığında da omzun bir miktar kalkar; kürek kemiği kolla birlikte döner. Sunumdaki grafikte bunu görüyorsun: doğru tekrarlarda da kulak–omuz mesafesi 0,45'ten 0,27'ye iniyor. Dolayısıyla "omuz şu kadar kalkarsa hata" diyen sabit bir eşik çalışmaz. Aynı sorunu Pavlikov ve ark. da yazıyor: normal abdüksiyonda omuz önden görünümde kolla birlikte yükselir ve tek bir dinlenme değerine göre ölçen bir ölçü bunu gerçek silkmeden ayıramaz (s. 12); onların sisteminde omuz yükselmesi en zayıf işaret (F1 0,55 ve 0,50; s. 23).

**Çözüm:** Kişinin 6 doğru tekrarından, kolun her açısı için "omzun normal yeri"ni çıkar.

1. Her tekrarı ikiye ayır: tepeye kadar **kaldırma**, sonrası **indirme**.
2. Kol açısını 0–180° arasında **5°'lik kutulara** böl.
3. Her kutu için, kalibrasyon tekrarlarının o kutudaki değerlerinin ortalamasını (**μ**) ve toleransını (**τ**) hesapla. τ = t(0,975; n−1) · s / √n. Burada s standart sapma, n o kutuya katkı veren tekrar sayısı; yani τ, ortalamanın %95 güven aralığının yarı genişliği.
4. τ çok dar çıkmasın diye bütün kutulardaki τ'ların birinci çeyreğinden küçük olamaz.
5. Bant = μ ± τ. Kalibrasyonda hiç görülmemiş kol açıları değerlendirilmez.

**Bu fikrin kaynağı:** μ, τ, τ'nun alt sınırı ve kare hatası formülü Jánošová ve ark. (2026)'dan (s. 10–11). **Bizim değişikliğimiz:** onlar tekrarları DTW ile *zamanda* hizalayıp bandı zamana göre kuruyor; biz bandı *kol açısına* göre kuruyoruz. Neden önemli: kişi kolunu az kaldırdığında, zamana göre hizalanmış bantta omuz yanlış kol açısındaki değerle karşılaştırılıyordu. Kol açısına göre kurunca omuz hep aynı kol açısında karşılaştırılıyor. (Önce zaman bandını kullandık, sonra açı bandına geçtik; 7. bölümde sayıları var.)

### 3.7 Hata puanı ve karar
1. **Kare hatası:** ölçü bandın içindeyse 0; dışındaysa (sapma − τ)/τ, en fazla 1. Yalnızca hatanın yönündeki taşma sayılıyor (omuzda yalnızca kulağa yaklaşma).
2. **Tekrar puanı E:** kare hatalarının ortalaması. 0 = hep bandın içinde, 1 = hep çok dışında.
3. **Az kaldırma puanı:** (kalibrasyon tepe açılarının medyanı − bu tekrarın tepe açısı) / max(tepelerin çeyrekler arası açıklığı, 5°).
4. **Ortak ölçek (z):** beş puan farklı büyüklükte olduğu için hepsi z = (puan − medyan) / (çeyrekler arası açıklık + 0,01) ile aynı ölçeğe çevriliyor. Medyan ve açıklık, veri setindeki **doğru** tekrarların puanlarından geliyor. Yani z, "bu puan doğru tekrarlardaki olağan değerden kaç kat uzakta?" demek.
5. **Karar:** en büyük z, **T = 3,80**'den küçükse "doğru". Değilse en büyük z'yi veren hata söyleniyor; ikinci en büyük z de T'yi geçiyorsa ikinci hata da söyleniyor (en fazla iki).

**Dürüstçe söylenecek nokta: sistem iki katmanlı.**
- *Kişiye özel katman:* bant (μ, τ) yalnızca o kişinin kalibrasyonundan gelir.
- *Ortak katman:* z ölçeği, hatanın yönleri ve T eşiği veri setindeki 5 kişiden öğrenildi. T, hata türü başarısını (makro-F1) en yükseğe çıkaran değer olarak seçildi.
- Deneylerde bu ortak katman **4 kişide öğrenilip 5. kişide sınandı** ve bu her kişi için tekrarlandı. Uygulamada test kişisi olmadığı için aynı yöntemle 5 kişinin hepsiyle bir kez kuruldu. Uygulamanın T'si 3,80; deneydeki beş ayrı ayarda T 3,68 ile 5,00 arasında çıkmıştı [`kural_disa_aktar/loso_karsilastirma.csv`].

### 3.8 Türkçe cümle
- Bulunan hata önce bir **sapma kodu**na çevriliyor: hata türü, taraf, faz (kaldırırken / yukarıdayken / indirirken), yön, şiddet, ölçü (derece) ve kişinin normal değeri.
- Kod, kurallarla iki katmanlı metne dönüşüyor: büyük yazıyla **hasta cümlesi** (ne oldu + ne yapmalı; sayılar 5°'ye yuvarlı) ve `U` tuşuyla açılan **uzman ayrıntısı** ("dirsek açın normalde 177 derece iken 120 dereceye indi").
- **Dil modeli (LLM) yok.** Cümleler tamamen kural tabanlı.
- Omuz cümlesindeki "derece", omuz çizgisinin gövde eksenine göre eğiminin kişinin normalinden farkı. Bu yalnızca anlatım için; karara girmiyor.
- Fikrin kaynakları: pozdan kurallarla metin üretme PoseScript ve PoseFix'ten ("posecode" ve "paircode" kavramları); skor yerine "hangi eklem, hangi fazda, nasıl düzelt" bilgisini verme ilkesi Ye ve ark. derlemesinden (sonuç bilgisi yerine performans bilgisi).

### 3.9 Bindirme (Problem 3)
Her tekrar bitince o tekrar yeniden oynatılıyor ve üstüne yarı saydam turkuaz bir referans iskelet çiziliyor.

- **Referans kim?** Kişinin kalibrasyon tekrarlarından, tepe açısı kalibrasyon medyanına en yakın olanı.
- **Zamanda hizalama:** iki tekrarın kol açısı eğrileri DTW ile eşleniyor. Eğriler önce z-normalize ediliyor (ortalaması çıkarılıp standart sapmasına bölünüyor; Sarsfield ve ark., s. 1006). Sonuç: kullanıcının her karesine, referansın "hareketin aynı anındaki" karesi karşılık geliyor.
- **Geometride hizalama:** referans iskelet (a) kullanıcının o karedeki kalça ortasına **öteleniyor**, (b) iki tekrarın dinlenme gövde boylarının oranıyla **ölçekleniyor**, (c) dinlenme gövde eksenlerinin açı farkı kadar **döndürülüyor**.
- **İnce nokta (soru gelirse):** ölçek ve döndürme kare kare değil, tekrar başında **bir kez** hesaplanıyor. Kare kare gövde boyuna ölçekleseydik, omuz kalkınca gövde de "uzamış" görünür, silkme referansa da taşınır ve farkı göremezdik.
- **Renk:** o karede bandın dışına çıkan ölçünün uzvu kırmızı (omuzda kulak–omuz çizgisi).

### 3.10 Çıktı ve kayıt
Solda video ve iskelet, sağda panel: karar, cümle, omuz eğrisi ve gri normal aralığı. Her tekrar `oturumlar/<tarih>.csv` dosyasına, kalibrasyon `profiller/<isim>.npz` dosyasına yazılıyor.

## 4. Küçük sözlük

- **AUC:** rastgele seçilen bir silkmeli tekrarın, rastgele seçilen bir doğru tekrardan daha yüksek hata puanı alma olasılığı. 0,5 yazı tura, 1 kusursuz ayırma. Eşik seçmeye gerek bırakmadan "puan iki grubu ne kadar iyi ayırıyor?" sorusunu cevaplar.
- **Bant:** kişinin doğru tekrarlarından çıkan normal aralık, μ ± τ.
- **τ (tolerans):** ortalamanın %95 güven aralığının yarı genişliği.
- **DTW (dinamik zaman bükme):** farklı hızda yapılmış iki hareketi, zaman eksenini esneterek kare kare eşleyen algoritma. **Bizde yalnızca bindirmede var; puanlamada yok.**
- **z:** bir puanın, doğru tekrarlardaki olağan değerden ne kadar uzak olduğu.
- **T:** "doğru" ile "hatalı" arasındaki karar eşiği (3,80).
- **Makro-F1:** her sınıfın (doğru + 5 hata) başarısının eşit ağırlıklı ortalaması. 1 kusursuz.
- **Kişi bazlı birini-dışarıda-bırak:** eşikleri 4 kişide ayarla, 5. kişide sına; bunu her kişi için tekrarla. Böylece sistem, sınandığı kişiyi ayar sırasında hiç görmemiş olur.
- **Görüş açısı:** kameranın kişiyi gördüğü açı. Önden 0–20°, çapraz 30–60°, profil 70–90°.

## 5. Sonuçlar: ne bulduk, nasıl bulduk?

**Veri:** REHAB26-ViewAngles veri setinin 1. egzersizi (kolu yana kaldırma). 5 sağlıklı kişi, 11 duruş yönü, 3 kamera; her tekrar doğru mu, yanlışsa hangi hata, etiketli. Hatalar kişilerin bilerek yaptığı taklitler. Üç kamerayla birlikte 1668 tekrar görüntüsü var; bunların 1363'ü önden + çapraz görüşte (682 hatalı, 681 doğru), 305'i profilde [`deney2/ozet.csv`]. Deneyler MediaPipe çalıştırmıyor; veri setinin hazır iskeletlerini kullanıyor.

### 5.1 Soru 1 (Problem 2): Kişiye özel bant omuz silkmesini daha iyi buluyor mu?

**Evet.** Kulak–omuz ölçüsü, silkmeli tekrar / doğru tekrar, AUC [`deney1/ozet.csv`]:

| Puanlama | Bütün görüşler | Önden + çapraz | Silkme / diğer hatalar |
| --- | --- | --- | --- |
| Ham ölçü (bant yok) | 0,704 | 0,761 | 0,699 |
| Genel bant (diğer 4 kişiden) | 0,666 | 0,683 | 0,649 |
| **Kişiye özel açı bandı** | **0,947** | **0,968** | **0,829** |

Üç puanlamanın farkı:
- **Ham:** tekrar kendi başlangıcıyla karşılaştırılır; "omuz, kol aşağıdayken durduğu yerden ne kadar uzaklaştı?" Standart yaklaşımın karşılığı bu.
- **Genel bant:** açı bandı kurulur ama aynı kamera ve yönelimdeki *diğer 4 kişinin* doğru tekrarlarından.
- **Kişiye özel:** bant kişinin kendi doğru tekrarlarından kurulur. Değerlendirilen doğru tekrar kendi bandına girmez (yoksa kendini ölçmüş olurdu).

Dört omuz ölçüsünü aynı veride karşılaştırdık (bütün görüşler) [`deney1/ozet.csv`]:

| Ölçü | Ham | Genel bant | Kişiye özel bant |
| --- | --- | --- | --- |
| Kulak–omuz dikey mesafesi (bizimki) | 0,704 | 0,666 | 0,947 |
| Sağ omzun iki omuz ortasına göre yüksekliği (Cóias'tan uyarlama) | 0,638 | 0,709 | 0,924 |
| Sol omuz – sağ omuz – sağ kalça açısı (Jánošová, F2) | 0,600 | 0,663 | 0,909 |
| İki omzun ortalama kalkışı (Pavlikov) | 0,650 | 0,700 | 0,858 |

**Nasıl yorumlanır:**
- Asıl kazanç ölçünün seçiminden değil, **kişiye özel banttan** geliyor: bütün ölçüler bantla 0,86–0,95'e çıkıyor.
- Kulak–omuz en yüksek çıkıyor, ama farklar küçük ve yalnızca 5 kişi var. **Kulak–omuzun diğerlerinden üstün olduğunu iddia etmiyoruz.**
- Kişi kişi bakınca kişiye özel bant 0,84 ile 0,98 arasında: Honza 0,975, Mima 0,954, Petra 0,981, Terka 0,982, Vasil 0,844 [`deney1/kisi_auc.csv`].
- Profil görüşte bant da zayıflıyor: 0,842 [`deney1/ozet.csv`].

### 5.2 Soru 2 (Problem 1): Hatanın türünü doğru söylüyor mu?

**Kısmen.** Önden + çapraz görüş, 682 hatalı ve 681 doğru tekrar [`deney2/ozet.csv`]:

| Ölçü | Değer |
| --- | --- |
| Hatalılarda ilk söylenen hata = gerçek hata | 56,6 / 100 |
| Hatalılarda gerçek hata, söylenen iki hatadan biri | 67,4 / 100 [`deney2/ilk_iki.csv`] |
| Hatalıya yanlışlıkla "doğru" dendi | 15,5 / 100 |
| Doğruya gereksiz uyarı verildi | 7,5 / 100 |
| Altı sınıf için makro-F1 | 0,631 |
| Bütün görüşlerde ilk söylenen hata doğru | 49,3 / 100 |
| Profil görüşte ilk söylenen hata doğru | 16,4 / 100 |

Beş hata arasında rastgele tahmin 100'de 20 tutturur; sonuç bunun çok üstünde ama kusursuz değil. Cümleye çevirme kayıpsız: cümlenin söylediği hata, karar kuralının bulduğuyla her tekrarda aynı [`deney3/ozet.csv`].

**Hangi hata neyle karışıyor?** Karışıklık tablosu, önden + çapraz; satır gerçek hata, sütun sistemin söylediği [`deney2/karisiklik_oc_kati.csv`]:

| Gerçek ↓ / söylenen → | doğru | omuz | baş | öne kaçma | dirsek | az kaldırma |
| --- | --- | --- | --- | --- | --- | --- |
| doğru (681) | **630** | 6 | 12 | 10 | 7 | 16 |
| omuz (135) | 20 | **56** | 12 | 10 | 0 | 37 |
| baş (138) | 25 | 20 | **71** | 5 | 1 | 16 |
| öne kaçma (137) | 48 | 2 | 1 | **55** | 8 | 23 |
| dirsek (137) | 9 | 16 | 0 | 23 | **77** | 12 |
| az kaldırma (135) | 4 | 3 | 0 | 1 | 0 | **127** |

Bu tablodan çıkanlar:
- En iyi bulunan hata **az kaldırma** (135'te 127). Ama sistem "az kaldırma"yı gereğinden sık söylüyor: omuz silkmelilerin 37'sine, öne kaçmaların 23'üne de az kaldırma demiş. Muhtemel neden (benim yorumum, ölçülmedi): kişi başka bir hatayı taklit ederken kolunu da daha az kaldırıyor, ve az kaldırmanın puanı diğerlerinden büyük çıkınca ilk sıraya o geçiyor.
- **Öne kaçma** en çok kaçırılan hata: 48'ine "doğru" denmiş. Tek kamerada derinlik olmadığı için kolun öne gitmesi yalnızca "kol kısaldı" diye görülebiliyor.
- **Dirsek ↔ öne kaçma** karışıyor (ikisinde de kol kamerada kısa görünür); **baş ↔ omuz** karışıyor (ikisinde de kulak ile omuz arası kısalır).
- Sınıf başına F1: doğru 0,89; az kaldırma 0,69; dirsek 0,67; baş 0,61; omuz 0,47; öne kaçma 0,46 [`deney2/siniflar.csv`].

**Olası soru: "Silkmeyi 0,95 ile buluyorsun, ama omuz türünde 135'te 56 mı?"** İkisi farklı soru. 0,95, silkmeli tekrarı *doğru tekrardan* ayırma başarısı (iki sınıf, eşik yok). Tür kararında ise beş hata birbiriyle yarışıyor ve tek bir eşik var; silkmeyi *diğer hatalardan* ayırma zaten daha zor (AUC 0,83). Omuz silkmelilerin 135'te yalnızca 20'sine "doğru" denmiş; yani sistem çoğunda bir sorun olduğunu görüyor, ama bir kısmında yanlış ad koyuyor.

### 5.3 Soru 3: Hiç görmediği birinde, ev ortamında çalışıyor mu?

**Bir işaret var (tek kişi).** Kendi çektiğimiz video: 6 kalibrasyon tekrarı, sonra sırası önceden rastgele belirlenmiş 21 test tekrarı. Eşiklerin hiçbiri bu videoya bakılarak değiştirilmedi [`kendi_kayit/kisi1/ozet.csv`]:

| Ölçü | Kaçta kaç |
| --- | --- |
| Tekrar otomatik ayrıldı | 21/21 |
| Hatalılarda ilk söylenen hata doğru | 9/11 |
| Hatalılarda doğru hata cümlede geçti | 11/11 |
| Omuz silkmesi bulundu (ilk sırada) | 3/3 |
| Normal doğru tekrarda gereksiz uyarı | 0/5 |
| Başka yere bakarak yapılan doğru tekrarda gereksiz uyarı | 3/3 |
| Hızlı yapılan doğru tekrarda gereksiz uyarı | 2/2 |

- Kaçırılan iki tekrar öne kaçma–dirsek karışması; veri setindeki karışmayla aynı.
- Başka yere bakınca ya da hızlı yapınca gereksiz uyarı çıktı. Bundan kullanım talimatı çıktı: **kalibrasyonda ve değerlendirmede aynı yere bak, doğal hızda yap.**
- Tek kişi, tek oturum, değerlendiren aynı zamanda geliştirici. Bu yüzden yüzde ya da güven aralığı vermiyoruz, yalnızca "kaçta kaç" diyoruz.

### 5.4 Altyapı kontrolleri

| Kontrol | Sonuç | Kaynak |
| --- | --- | --- |
| Otomatik tekrar ayırma (önden + çapraz) | 1363 tekrarın 1295'i bulundu (95,0/100); 34 fazladan tekrar | [`tekrar_ayirma/ozet.csv`] |
| Uygulamanın MediaPipe sürümü (1.2.2) ile veri setininki (0.10.20) | Aynı karelerde kol açısı farkı medyan 0,92°, %95'i 3,09° altında | [`uygulama_saglik/ex1_Honza_cam1_o0_poz_farki.csv`] |
| Bütün sonuçlar bugünkü koddan yeniden üretiliyor mu? | 40 dosyanın 40'ı aynı (10 Kasım 2026) | [`hepsi/ozet.md`] |

## 6. Hangi makaleden ne alındı?

Aşağıdaki her satırı 11 Kasım 2026'da **makalenin kendi PDF'inden** doğruladım (sayfa numaraları makaleye ait). Sunumda yalnızca ilk dördünü ve MediaPipe'ı anman yeter; diğerleri soru gelirse.

### Yönteme bir parçası giren makaleler

| Makale | Ne alındı | Makalede nerede |
| --- | --- | --- |
| **Jánošová, Lang, Budikova, Sedmidubsky (2026)**, *Impact of Patient Orientation in Single- and Multi-View Camera Environments for AI-based Rehabilitation Monitoring*, arXiv:2609.35726 | (1) **Veri seti** REHAB26-ViewAngles: 3 egzersiz, 5 kişi, 11 yönelim, 1.650 etiketli tekrar, 29 görüş açısı. (2) **Tolerans bandı:** doğru tekrarlardan ortalama μ ve %95 güven aralığı (Student t) toleransı τ; τ'ya birinci çeyrek alt sınırı; kare hatası min(1, (sapma − τ)/τ); tekrar hatası = ortalama. (3) Baş, dirsek, kol ölçülerinin tanımları (Tablo 1, F1–F4). | Veri: s. 8–9. Bant ve hata: s. 10–11. Tablo 1: s. 7 |
| **Pavlikov ve ark. (2026)**, *Markerless On-Device Detection of Compensatory Movement Patterns…*, Sensors 26, 5054 | (1) **Kol açısı tanımı:** üst kol ile aşağı dikey arasındaki açı. (2) **Sorunun kendisi:** normal harekette de omuz yükselir, tek bir dinlenme değerine göre ölçen ölçü bunu ayıramaz; omuz yükselmesi en zayıf işaret (F1 0,55 / 0,50). (3) Hareketi fazlara ayırma fikri (kaldırma / tutma / indirme). (4) En-boy düzeltmesi uyarısı. | Kol açısı: s. 10. Omuz sorunu: s. 12, 22–23. Faz: s. 10–11. En-boy: s. 9 |
| **Cóias, Lee, Bernardino (2022)**, *A low-cost virtual coach for 2D video-based compensation assessment…*, J. NeuroEng. Rehabil. 19:83 | Omzu **boyna göre** ölçme fikri (kulak–omuz ölçümüzün esin kaynağı); kural tabanlı telafi tespiti ve geri bildirim. Onların kural tabanlı yöntemi bir egzersizde sinir ağından iyi çıkmış (F1 0,76'ya 0,70). | Omuz–boyun: s. 9. Sonuç: s. 12 |
| **Sarsfield ve ark. (2019)**, *Segmentation of Exercise Repetitions… Using a Single Exemplar*, IEEE TNSRE 27(5), 1004–1019 | DTW'den önce özelliği **sıfır ortalama, birim varyansa** getirme (z-normalizasyon). Bizde yalnızca bindirmede. | s. 1006 |
| **Ye ve ark. (2026)**, *Perception, assessment, and coaching…* (147 yayınlık sistematik derleme), Front. Rehabil. Sci. 7 | **Skor yerine performans bilgisi:** sistemler çoğunlukla özet "sonuç bilgisi" veriyor, oysa kişiye gereken "performans bilgisi" (ne yanlış, nasıl düzelir). Geri bildirim tasarımımızın ilkesi. | s. 1, 3 |
| **Delmas ve ark. (2024)**, *PoseScript*, ve **Delmas ve ark.**, *PoseFix* (ICCV) | Pozdan ve iki poz arasındaki farktan **kurallarla** kısa kodlar ("posecode", "paircode") çıkarıp şablon cümleye çevirme. Bizim "sapma kodu → cümle" yapımız bunun küçük bir benzeri. | PoseScript s. 1–2; PoseFix s. 15021 |
| **Fieraru ve ark. (2021)**, *AIFit*, CVPR | Referansa (eğitmene) göre sapmayı bulup doğal dilde söyleyen en yakın öncül sistem. Onlar 3B poz ve eğitmen referansı kullanıyor; biz 2B ve kişinin kendi referansını. | s. 9919–9921 |

### Bir tasarım kararının gerekçesi olan makaleler

| Makale | Hangi kararın gerekçesi | Makaledeki dayanak |
| --- | --- | --- |
| **Unger ve ark. (2025)**, Front. Med. 12 | **Kişiye özel referans.** İnmeli bireylerde omuz telafisini web kamerasıyla bulmada kişi içi modeller 0,92–0,95 doğruluk verirken kişiler arası modeller en fazla 0,70'te kalmış. Bizim 0,95'e karşı 0,67 bulgumuzla aynı yönde. | s. 6–8 |
| **Černek, Sedmidubsky, Budikova (2025)**, Information Systems 134 | **3B yerine 2B.** Derinlik tahmini poz kestiriminin asıl zorluğu; mümkünse 2B tercih edilmeli. Jánošová ve ark. da 2B'nin 3B'den ortalama %9,2 daha iyi ayırdığını buluyor. | Černek s. 11; Jánošová s. 20 |
| **Tang ve ark. (2025)**, arXiv:2505.18412 | **Cümleyi LLM'e değil kurala yazdırma.** GPT-4o ile egzersiz değerlendirme doğruluğu en iyi 0,76 ve 0,70; çıktılar çalıştırmadan çalıştırmaya değişebiliyor, geri bildirim yalnızca nitel değerlendirilebilmiş. | s. 11, 13 |
| **Ullah ve ark. (2025)**, Sci. Rep. 15 | **Motivasyon.** MediaPipe + DTW ile çalışan benzer bir sistem, ama çıktısı tek bir "eylem puanı". Ödev tam da bunun yeterli olmadığını söylüyor. | s. 9 |

**Poz çıkarımı:** Google MediaPipe Pose Landmarker (resmi belgeler; ödevin kaynak rehberinde de var).

**Kendi katkımız ne?** Hiçbir makaleden alınmayan iki şey: (1) bandı zamana değil **kol açısına** göre kurmak, (2) omuz için **kulak–omuz dikey mesafesi** ölçüsü. Ayrıca bütün parçaları (ölçüm, tür kararı, Türkçe cümle, bindirme) tek bir çalışan uygulamada birleştirmek.

## 7. Denenip elenenler (soru gelirse)

Kodları ve sonuçları depoda değil, git geçmişinde (`v-sunum` etiketi); ödevin parçası değiller ama "bunu denediniz mi?" sorusunun cevabıdırlar. Kaynak yolları o etiketteki `sonuclar/` klasörüne göre.

| Ne denendi | Ne oldu | Kaynak |
| --- | --- | --- |
| **Zamansal yumuşatma** (ödevin P2 için önerdiği) | MediaPipe titremesi %38–87 azaldı, ama silkme tespiti değişmedi (AUC 0,947 → 0,943 ve 0,947). Kullanılmadı. | `deney1c/ozet.csv` |
| **Görüntüden omuz silueti** (ödevdeki "pose + lokal görüntü" önerisi) | Önden çekimde ayırıyor (0,94), çaprazda bozuluyor (0,55); toplamda 0,72. Kulak–omuz aynı tekrarlarda 0,97. | `siluet/ozet.csv` |
| **Zaman bandı** (literatürdeki hâli: DTW ile zamanda hizala) | Silkme / doğru 0,909 (açı bandında 0,947); silkme / diğer hatalar 0,705 (açı bandında 0,829). Açı bandına geçildi. | DENEYLER.md, "Denenip işe yaramayanlar" |

## 8. Sınırlılıklar (kendin söyle, sorulmasını bekleme)

1. **Veri:** 5 sağlıklı kişi; hatalar taklit, gerçek hasta yok.
2. **Tek kamera, 2B:** derinlik yok, dereceler yaklaşık. Öne kaçma ile dirsek, baş eğme ile omuz karışabiliyor. Profil çekim uygun değil.
3. **Kalibrasyon şart:** her kurulumda 6 doğru tekrar gerekiyor ve kamera yerinden oynamamalı. Kalibrasyonu yanlış yapan kişinin bandı da yanlış olur.
4. **Bakış ve hız:** başka yere bakmak ya da çok hızlı yapmak gereksiz uyarı üretebiliyor.
5. **Dar bant:** τ, ortalamanın güven aralığı; yeni bir tekrarın düşebileceği aralık bundan daha geniş olurdu (6 tekrarla yaklaşık 2,6 kat; hesap, ölçüm değil). Bu yüzden küçük sapmalar da uyarıya dönüşebiliyor.
6. **Tek hareket:** sistem yalnızca kolu yana kaldırmada ölçüldü.

## 9. Beş dakikanın akışı

| # | Slayt | Süre | Söylenecek tek cümle |
| --- | --- | --- | --- |
| 1 | Kapak | 15 sn | Tek kamerayla egzersizi izleyen, hatayı Türkçe söyleyen ve doğru tekrarı üstüne bindiren bir uygulama. |
| 2 | Ödevin üç problemi | 30 sn | Üç problem tek uygulamada; hareket omuz egzersizi, referans kişinin kendi 6 doğru tekrarı. |
| 3 | Beş adım | 35 sn | MediaPipe → kol açısı → açı bandı → hata türü → cümle ve bindirme. |
| 4 | Doğru harekette de omuz kalkıyor | 45 sn | Sabit eşik çalışmaz; kol açısına göre kişinin normaline bakıyoruz. |
| 5 | 0,70'ten 0,95'e | 40 sn | Kazanç ölçüden değil, kişiye özel banttan geliyor. |
| 6 | Cümle | 30 sn | Puan değil; ne oldu, kaç derece, ne yapmalı. |
| 7 | Bindirme | 35 sn | DTW ile zamanda; öteleme, ölçek, döndürme ile geometride. |
| 8 | Tür doğruluğu | 45 sn | Hatalıların 56,6/100'ünde ilk söylenen doğru; kendi videomda 9/11. |
| 9 | Canlı demo | 60 sn | Bir doğru, bir az kaldırma, bir omuz silkmesi. |
| 10 | Sınırlılıklar ve kaynaklar | 30 sn | 5 sağlıklı kişi, 2B, kalibrasyon şart. |

Toplam yaklaşık 6 dakika ediyor. Süre sıkışırsa 3. slaytı 15 saniyeye indir ve 8. slayttaki sol tabloyu yalnızca tek cümleyle geç. Her slaytın konuşmacı notunda söylenecek metin yazılı.

## 10. Canlı demo

Ayrıntılı kontrol listesi ve yedek yollar: [`DEMO.md`](DEMO.md). Özet:

```bash
.venv\Scripts\activate
python -m uygulama.main --profil profiller/kisi1.npz --video veri/kendi_kayit/kisi1/test.MOV
```

- **26. sn**, tekrar 4, doğru → "Hareketi doğru yaptın. Kolun yaklaşık 140 dereceye çıktı, omzun ve dirseğin yerindeydi."
- **41. sn**, tekrar 6, az kaldırma → "Kolunu 105 dereceye kadar kaldırdın; normalde 140 dereceye çıkıyorsun…"
- **49. sn**, tekrar 7, omuz silkmesi → "Kolunu kaldırırken sağ omzunu kulağına doğru yaklaşık 5 derece kaldırdın. Omzunu aşağıda ve gevşek tut."
- Tekrar 7'nin oynatımından sonra **Q** ile çık.
- Tuşlar: Boşluk duraklat, R son tekrarı yeniden oynat, U uzman ayrıntısı. Önce pencereye bir kez tıkla.
- Pencere açılmazsa: `sonuclar/sunum/demo_kisi1.mp4` dosyasını video oynatıcıda aç.

**Demoda dürüst kalınacak iki nokta:**
- Tekrar 6'da sistem az kaldırmanın yanında ikinci hata olarak hafif bir baş eğme de söylüyor ("…başını yaklaşık 5 derece yana eğdin"). Etiket yalnızca az kaldırma. Sorulursa: bant dar olduğu için küçük sapmalar da uyarıya dönüşebiliyor (8. bölüm, madde 5).
- Doğru bir tekrarın oynatımında da bir uzuv kısa süre kırmızı görünebilir. O kare bandın dışındadır, ama tekrarın toplam puanı eşiği geçmediği için karar "doğru" çıkar.

**Sunumdan önce bir kez dene:** aynı bilgisayar, aynı ekran çözünürlüğü, priz takılı.

## 11. Gelebilecek sorular ve cevapları

**Neden yoga değil?** Derste hareketin yoga olmasının şart olmadığı söylendi. Problem 2 omuzu istiyor; omuz egzersizi seçince üç problem aynı uygulamada birleşti.

**Referans video nerede? Neden başka birinin videosu yok?** Referans, kişinin kendi kalibrasyon tekrarları. Bunu ölçtük: başkalarından kurulan bantla 0,67, kişinin kendisinden 0,95. Literatür de aynı yönde (Unger ve ark.: kişi içi 0,92–0,95, kişiler arası en fazla 0,70). Bindirme kodu iki farklı kişinin tekrarını da hizalayabilecek şekilde yazıldı; arayüzde kişinin kendi referansı seçiliyor.

**Referans aynı kişiyse geometrik hizalama ne işe yarıyor?** Kişi kalibrasyonda ve testte farklı yerde durabilir, kameraya yaklaşıp uzaklaşabilir. Öteleme ve ölçek bunu düzeltiyor.

**MediaPipe'ın omuz noktası neden yetmiyor?** Doğru harekette de omuz noktası yukarı kayıyor. Ham ölçü silkmeyi 0,70 ile ayırıyor; kişinin kendi normaline göre bakınca 0,95.

**Omuza özel iyileştirmeniz tam olarak ne?** İki şey: omzu kulağa göre ölçmek ve bu ölçüyü kol açısına koşullu, kişiye özel bantla değerlendirmek. Ödevde sayılan "kol elevasyonu ile omuz/skapula hareketi arasındaki ilişki" tam olarak bu. Ödevin önerdiği yumuşatmayı ve omuz bölgesi siluetini de denedik; ikisi de bundan iyi çıkmadı.

**Skapulayı (kürek kemiğini) gerçekten ölçüyor musunuz?** Hayır, doğrudan değil. MediaPipe kürek kemiğini vermez. Biz omuz kuşağının yükselmesini, omuz noktasının kulağa göre konumundan dolaylı olarak ölçüyoruz. Kürek kemiğinin kendisini ölçmek için ödevin kaynak rehberindeki yöntemler (özel noktalar eğitmek, derinlik kamerası) gerekirdi.

**DTW'yi nerede kullanıyorsunuz?** Yalnızca bindirmede, iki tekrarı zamanda eşlemek için. Puanlama kol açısına göre yapıldığı için orada zaman hizalamasına gerek kalmıyor.

**Neden Procrustes kullanmadınız?** Procrustes iki nokta kümesini *bütün* noktalara göre en iyi çakıştırır; hatalı uzuv da bu hesaba girer ve fark küçültülür. Biz hatanın görünür kalmasını istediğimiz için yalnızca gövdeye göre (kalça ortası, gövde boyu, gövde ekseni) hizalıyoruz; kol ve omuz serbest kalıyor. (Bu bir tasarım gerekçesi; iki yöntemi sayıyla karşılaştırmadık.)

**Eşikleri nasıl seçtiniz? Test verisine bakmadınız mı?** Bant kişinin kendisinden geliyor. Ortak eşik T ve z ölçeği veri setinden; deneylerde 4 kişide ayarlanıp 5. kişide sınandı, test kişisi ayara hiç girmedi. Bandın parametreleri (5° kutu, en az 3 tekrar) deneyden önce sabitlendi.

**AUC nedir, neden doğruluk (accuracy) değil?** AUC eşik seçmeden iki grubun puanlarının ne kadar ayrıştığını ölçer. Doğruluk bir eşiğe bağlıdır; AUC ölçünün kendisinin kalitesini gösterir. Ödev de AUC'nin deneysel değerlendirmede kullanılabileceğini söylüyor; kullanıcıya verdiğimiz çıktı AUC değil, cümle.

**Sonuçlar neden kusursuz değil?** Tek kamerada derinlik yok. Kolun öne gitmesi ile dirseğin bükülmesi kameradan bakınca aynı görünüyor: kol kısalıyor. Bunu ayırmak için ikinci kamera ya da derinlik gerekir.

**5 kişi az değil mi?** Az. Bu yüzden ölçüler arasında üstünlük iddia etmiyoruz ve kendi kaydımızı yalnızca "kaçta kaç" olarak veriyoruz. Asıl bulgumuz (kişiye özel bant ham ölçüden iyi) beş kişinin beşinde de geçerli: en düşük kişi 0,84.

**Hatalar taklit; gerçek hastada çalışır mı?** Bilmiyoruz, ölçmedik. Bu en önemli sınırlılıklardan biri.

**Neden LLM kullanmadınız?** Denedik; kural cümlesinden iyi çıkmadı, hatayı da LLM'e buldurunca kötüleşti. Kural tabanlı cümle her çalıştırmada aynı, ücretsiz ve internet gerektirmiyor.

**Gerçek zamanlı mı?** Uygulama canlı kamerayla çalışıyor ve karar tekrar bitince veriliyor (tekrarın tamamına bakıldığı için). Kare hızını ayrıca ölçüp raporlamadık.

**Veri setinin makalesindeki kamera adları sizinkinden farklı görünüyor?** Makalenin şemasında önden kamera "Cam3" olarak geçiyor; indirilen veride ise önden bakan kamera `cam1`. Bunu veriden doğruladık: omuz genişliği / gövde boyu oranı bizim hesapladığımız görüş açısı 0° civarındayken en büyük (≈0,70), ±90°'de en küçük (≈0,06) [`kamera_acisi/gorus.csv`].

**Yapay zekâ kullandınız mı?** Evet, ödevin kuralı gereği raporda yazıyor: kodun yazılması, hata ayıklama ve belgelerde Claude Code; literatür taraması ve planlamada Claude. Uygulamanın kendisi dil modeli kullanmıyor. Ayrıntı: [`LLM_KULLANIMI.md`](LLM_KULLANIMI.md).

**Bir başkası bunu yeniden kurabilir mi?** Evet. `pip install -r requirements.txt`, sonra `python -m uygulama.main --isim adin`. Deneylerin hepsi `python -m deneyler.hepsi` ile yaklaşık 1,5 dakikada yeniden üretiliyor ve kayıtlı sonuçlarla karşılaştırılıyor (son çalıştırmada 40 dosyanın 40'ı aynı).

## 12. Akılda tutulacak sayılar

| Sayı | Ne |
| --- | --- |
| **6** | Kalibrasyon tekrarı |
| **5°** | Bandın kol açısı kutusu |
| **5** | Ölçü ve hata türü |
| **0,70 → 0,95** | Omuz silkmesini ayırma (AUC): ham ölçü → kişiye özel bant |
| **0,67** | Aynı şey, bant başkalarından kurulunca |
| **56,6 / 67,4** | 100 hatalı tekrarda: ilk söylenen hata doğru / doğru hata cümlede |
| **7,5** | 100 doğru tekrarda gereksiz uyarı |
| **9/11, 3/3, 0/5** | Kendi video: ilk hata doğru, silkme bulundu, normal doğruda gereksiz uyarı |
| **3,80** | Karar eşiği T |
| **30° / 20°** | Tekrarın başlama / bitme açısı |
| **5 kişi, 1363 tekrar** | Veri seti (önden + çapraz görüş) |

## 13. Makale doğrulaması hakkında not

`LITERATUR.md`'deki özetler yapay zekâyla çıkarılmıştı ve "rapora girecek sayılar makalenin kendisinden doğrulanmalı" notu vardı. 11 Kasım 2026'da projede kullanılan 12 makalenin PDF'leri açılıp, bu dosyada ve raporda geçen her iddia ve sayı makalenin metninde arandı. Hepsi tuttu; düzeltilmesi gereken bir sayı çıkmadı. Doğrulananların listesi `LITERATUR.md`'nin başında. Kullanılmayan makaleler incelenmedi.
