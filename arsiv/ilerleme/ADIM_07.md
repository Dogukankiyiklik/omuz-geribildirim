# ADIM 07 — Kendi kayıtlarımızla deneme

**Tarih:** 2026-11-07 (hazırlık), 2026-11-09 (çekim ve video kontrolü)
**Durum:** ✅ Tamamlandı (9 Kas). Tek kişi (kişi 1) çekildi ve değerlendirildi; kabul ölçütü sağlandı. 2. kişi çekilmeyecek (kullanıcı kararı).

## Basit anlatım
- Şimdiye kadarki bütün sayılar başkalarının videolarından (REHAB26 veri seti) geldi. Bu adımda sistemi **kendi çektiğimiz** videolarla deniyoruz. Kalibrasyon videosunda 6 doğru tekrar var. Test videosunda ise sırası önceden yazılmış 21 tekrar var: bazıları doğru, bazıları bilerek hatalı.
- Sistemin her tekrar için söylediği cümle, bizim yazdığımız gerçek etiketle karşılaştırılıyor. Örneğin "omuz silktim, sistem de omuz dedi mi?"
- Bu adım hocanın "gerçek kullanımda çalışıyor mu?" sorusuna cevap verir. Canlı denemedeki iki şüpheyi de sınar: **"farklı yere bakınca baş hatası çıkıyor mu?"** ve **"hızlı yapınca hız notu çıkıyor mu?"**
- **Neden "önceden belirlenenler"?** Hangi sayıları nasıl hesaplayacağımızı videoyu çekmeden önce yazıp kaydettik (commit). Böylece sonuca bakıp ölçütü değiştirmediğimiz kanıtlanabilir. Buna "önceden kayıt" denir.

## Önceden belirlenenler (çekimden önce sabit; Karar 33)
1. **Yöntem ve parametreler:** Dondurulmuş yöntem (Karar 18), `modeller/kural_ex1.json` (Karar 24), `modeller/kamera_esigi.json` (Karar 26), `modeller/hiz_esigi.json` (Karar 31; 1.9000 s), yığın modu (`uygulama/toplu.py`), MediaPipe 1.2.2 + `pose_landmarker_full`. **Hiçbir eşik, sabit veya cümle şablonu bu kayıtlara göre değiştirilmez.** Sonuç kötü çıkarsa olduğu gibi yazılır.
2. **Kalibrasyon:** `kalibrasyon.mp4` içinde ayrılan tekrarlar sırayla kabul edilir, en fazla 6 (yığın modunun davranışı). Kalite kontrolü açık: omuz ya da kalça görünürlüğü medyanı < 0,5 olan tekrar alınmaz. 5'ten az tekrar kalırsa değerlendirme yapılmaz; çekim tekrarlanır.
3. **Eşleştirme:** Test videosunda ayrılan tekrarlar zaman sırasıyla `etiketler.csv` içindeki `tekrar_no` ile eşlenir. Sayılar tutmazsa betik durur ve ayrılan tekrarların yalnızca zamanlarını yazar (karar ve cümle yazmaz). Kullanıcı videoyu izleyerek bir eşleşme dosyası hazırlar (`--eslesme`). Eşlenemeyen etiketli tekrarlar metriklerin paydasına girmez ve "test videosunda ayrıldı: kaçta kaç" satırında ayrıca raporlanır.
4. **Hata listesi:** Kullanıcının gördüğü **hasta cümlesinden** `cekirdek/metin_cozumleyici.py` ile çıkarılır. Bu, Deney 3'teki çıkarıcının aynısıdır. Uzman ayrıntısından çıkarılan listeyle aynı olduğu ayrıca denetlenir.
5. **Metrikler** (kişi başına ve iki kişi birlikte; sayılar "kaçta kaç", güven aralığı verilmez):
   - Hatalı tekrarlar (12):
     - **katı:** cümledeki ilk hata = etiket;
     - **ilk iki:** etiket cümlede söylendi;
     - **olumlu cümle:** hiç hata söylenmedi.

     Hepsi için ayrıca hata türüne göre.
   - Doğru tekrarlarda **gereksiz uyarı** (cümlede en az bir hata), üç grupta ayrı: **normal** (5), **bakış** (3), **hızlı** (2).
   - **Hız notu:** hızlı tekrarlarda (2) ve normal doğru tekrarlarda (5) çıktı mı; bakış ve hatalılarda betimsel.
   - **Karışıklık tablosu:** gerçek etiket × cümledeki ilk hata.
   - **"Verilen cümle – gerçek etiket" tablosu**, tekrar başına.
   - **Betimsel:** kamera uyarısı ve sol kol notu sayısı.
6. **Bilgi notları metrik değildir** (Karar 31): hız ve sol kol notu cümleye girmez, gereksiz uyarı sayılmaz.
7. **Yorum sınırı:** Kişi başına 21 tekrar var; tek kişide tek tekrarın değişmesi oranı 1/5 ile 1/2 arasında oynatır. Sonuçlar "kaçta kaç" olarak yazılır, veri setindeki yüzdelerle doğrudan kıyaslanmaz, yalnızca yan yana konur.
8. **Bakış sınaması (Karar 32):** "Bakış" grubunda gereksiz uyarı, normal doğru gruptan belirgin yüksekse (ör. 3/3'e 0/5), bu kullanıcının gözlemini destekler. Hangi hatanın söylendiği ayrıca yazılır (baş mı?). Sayılar küçük olduğu için bu bir kanıt değil, bir **işaret** olarak raporlanır.
9. **Çıktılar:** `sonuclar/kendi_kayit/<kisi>/` altına `tekrarlar.csv` (ham), `cumle_etiket.csv`, `karisiklik.csv`, `ozet.csv` ve `bilgi.json` (sürümler, kalibrasyon tepeleri, eşleşme biçimi). İki kişi birlikte: `sonuclar/kendi_kayit/ozet.csv`, `karisiklik.csv`.
10. **Sunum yedeği (Karar 27):** Bu iki video ve yığın modu çıktısı sunumdaki yedektir.

> **Düzeltme: 11** (9 Kas, Güncelleme 12): Madde 5'teki "Hatalı tekrarlar (12)" bir yazım hatasıdır. Protokole göre hatalı tekrar sayısı **11**'dir (3 omuz + 2 baş + 2 dirsek + 2 az kaldırma + 2 öne kaçma). Önceden kayıt korunsun diye bölümün kendisi değiştirilmedi; sonuçlar zaten 11 üzerinden hesaplandı.

## Yapılanlar (hazırlık)
- `deneyler/kendi_kayit.py`:
  - `--sablon`: tohumlu karışık sıra ve `etiketler.csv` şablonu yazar; var olan dosyanın üzerine yazmaz.
  - Değerlendirme: yığın modu, MediaPipe noktaları `veri/ara/kendi_kayit/` altına önbelleklenir.
  - Eşleştirme, metrikler ve çıktılar yukarıdaki maddelere göre.
- `uygulama/toplu.py`: `kalibre_et` ve `degerlendir_video` artık önceden çıkarılmış noktaları da alabiliyor (`lm=`). Davranış aynı.
- Sıralar üretildi: `veri/kendi_kayit/kisi1/etiketler.csv` (tohum 0) ve `veri/kendi_kayit/kisi2/etiketler.csv` (tohum 1). Kopyası `docs/etiketler_sablon.csv`, tohum 0. Sıralar `docs/CEKIM_LISTESI.md` içinde.
- `testler/test_kendi_kayit.py`: sıranın protokole uyması, etiket denetimleri, eşleştirme ve metrik tanımları (yapay tabloyla).
- **Duman testi (yalnızca betiğin çalıştığını görmek için, sonuç değildir):** Veri setinden `ex1_Honza` cam1 yönelim 0 videosu kesildi ve hem kalibrasyon hem test olarak verildi; 10 etiket de veri setinden alındı. Sonuç: 10/10 tekrar ayrıldı ve eşlendi, tablolar yazıldı. Hasta ve uzman metinlerinden çıkan hata listeleri 10/10 aynıydı. Kalibrasyon videosunda 5'ten az tekrar olunca betik doğru şekilde durdu. Bu çalıştırmada kalibrasyona hatalı tekrarlar da girdiği için sayılar anlamsızdır ve raporlanmaz. Çıktı proje dışında (geçici klasör).

## Çekim (kişi 1, 9 Kasım 2026)
- **Cihaz ve ayar:** iPhone, "En Uyumlu" biçim (H.264), 1080p 30 fps, dikey. Kişi önden, ayakta.
- **Kurulum:** İki video aynı kurulumda çekildi. Kişi ekrandaki suflör sayfasına baktı; bakış noktası dizüstü bilgisayarın ekranıydı. Her tekrardan önce sayfa tekrar numarasını ve hareketi sesli okudu, kaldırma ve indirme anlarında bip çaldı.
- **Kalibrasyon ve test suflör sayfasına bakılarak çekildi; ilk kalibrasyon videosu (suflörsüz) kullanılmadı.**
- **Dosyalar:** `veri/kendi_kayit/kisi1/kalibrasyon.MOV` (6 doğru tekrar) ve `test.MOV` (21 tekrar, `docs/CEKIM_LISTESI.md` sırasıyla).
- **Etiket açıklamaları:** `etiketler.csv`'ye serbest metinli bir `aciklama` sütunu eklendi: 11 "baş sola", 19 "baş sağa"; 2, 3 ve 13 "bakış sağ-aşağıdaki işarete". Eklemeden önceki dosya `etiketler_aciklamasiz.csv` adıyla saklandı. Etiketler ve `not` sütunu değişmedi.

### Video kontrolü (OpenCV 5.0.0, FFMPEG arka ucu)
| | kalibrasyon.MOV | test.MOV |
| --- | --- | --- |
| Kodek | h264 | h264 |
| Çözünürlük (döndürme sonrası) | 1080 × 1920 (dikey) | 1080 × 1920 (dikey) |
| Döndürme bilgisi | 90° (OpenCV otomatik uyguluyor) | 90° (OpenCV otomatik uyguluyor) |
| Başlıktaki fps | 29.988458579122852 | 29.982057786302047 |
| Başlıktaki kare sayısı | 1559 | 4846 |
| Okunan kare sayısı | 1549 | 4824 |
| Süre (son karenin zamanı) | 51.64 s | 160.89 s |
| Kareler arası süre (en az / medyan / en çok) | 33.33 / 33.33 / 35.00 ms | 33.33 / 33.33 / 35.00 ms |
| 40 ms'den uzun aralık | 0 | 0 |

- **Sabit 30 fps:** Kareler arası süre medyanı 33,33 ms, hiç kare atlaması yok; video pratikte sabit 30 fps. Başlıktaki 29,98 değeri ortalama hesabından geliyor (muhtemelen ses izi videodan biraz uzun). Betik zaman damgasını başlıktaki fps ile hesaplıyor; fark %0,06, sonuca etkisi yok.
- **Kare sayısı farkı:** Başlıktaki sayı bir tahmin; okunan kare sayısı gerçek değer. Değerlendirme betiği kareleri okuyarak işler, başlıktaki sayıyı kullanmaz.
- **Dik görünüm:** İki videonun ilk karesi OpenCV ile okundu ve gözle bakıldı: kişi dik, önden, baştan ayağa kadrajda; arka plan sade beyaz duvar.
- **Dönüştürme yapılmadı:** Bilgisayarda ffmpeg kurulu değil. Gerek de yok: OpenCV `.MOV` dosyasını doğrudan okuyor ve döndürmeyi kendisi uyguluyor (ilk kare 1080 × 1920, dik). En-boy oranı 1080/1920 = 0,5625; bu, projede kullanılan 9/16 ile aynı. Bu yüzden `kalibrasyon.mp4` / `test.mp4` oluşturulmadı; değerlendirme orijinal `.MOV` dosyalarıyla yapılır. Orijinaller değiştirilmedi.

## Değişen / eklenen dosyalar
| Dosya | Ne işe yarıyor |
| --- | --- |
| `deneyler/kendi_kayit.py` | Adım 7 değerlendirmesi ve sıra şablonu |
| `testler/test_kendi_kayit.py` | Betiğin testleri |
| `docs/CEKIM_LISTESI.md` | Yazdırılabilir çekim kontrol listesi ve iki kişinin sırası |
| `docs/etiketler_sablon.csv` | `etiketler.csv` örneği (tohum 0 sırası) |
| `uygulama/toplu.py` | `lm=` seçeneği |

## Nasıl çalıştırılır
```bash
# Çekimden sonra (videolar veri/kendi_kayit/kisi1/ altına konur):
python -m deneyler.kendi_kayit --kisi kisi1 --kalibrasyon veri/kendi_kayit/kisi1/kalibrasyon.mp4 --test veri/kendi_kayit/kisi1/test.mp4 --etiketler veri/kendi_kayit/kisi1/etiketler.csv
# Kişi 1'in gerçek videoları .MOV (dönüştürme yapılmadı, yukarıya bakın):
python -m deneyler.kendi_kayit --kisi kisi1 --kalibrasyon veri/kendi_kayit/kisi1/kalibrasyon.MOV --test veri/kendi_kayit/kisi1/test.MOV --etiketler veri/kendi_kayit/kisi1/etiketler.csv
```
Beklenen süre: MediaPipe ilk çalıştırmada videonun süresinin kabaca 1–2 katı (2 dakikalık test videosu için birkaç dakika). Sonraki çalıştırmalar önbellekten birkaç saniye sürer. Çıktı: `sonuclar/kendi_kayit/kisi1/`.

## Sonuçlar (kişi 1; çalıştırma 2026-11-09T15:45:01, kullanıcı çalıştırdı)
Kaynak: `sonuclar/kendi_kayit/kisi1/` (`bilgi.json`, `ozet.csv`, `karisiklik.csv`, `cumle_etiket.csv`, `tekrarlar.csv`). Sayılar bu dosyalardan kopyalandı.

**Kalibrasyon:** 6 tekrar ayrıldı, 6'sı kabul edildi, kalite reddi 0. Tepe açıları: 142.7, 144.7, 139.7, 139.5, 140.8, 138.3. MediaPipe 1.2.2, en-boy 0.5625.

**Ayrılma ve eşleştirme:** Test videosunda 21/21 tekrar ayrıldı (hızlı tekrarlar 2/2 dahil). Eşleşme dosyası gerekmedi, eşleştirme sırayla yapıldı. Hasta ve uzman metinlerinden aynı hata listesi çıkma denetimi 21/21.

| Metrik | Grup | Kaçta kaç |
| --- | --- | --- |
| Katı: cümledeki ilk hata = etiket | hatalı (hepsi) | 9/11 |
| İlk iki: etiket cümlede söylendi | hatalı (hepsi) | 11/11 |
| Olumlu cümle (hiç hata söylenmedi) | hatalı (hepsi) | 0/11 |
| Katı / ilk iki | omuz | 3/3 / 3/3 |
| Katı / ilk iki | baş | 2/2 / 2/2 |
| Katı / ilk iki | öne kaçma | 1/2 / 2/2 |
| Katı / ilk iki | dirsek | 1/2 / 2/2 |
| Katı / ilk iki | az kaldırma | 2/2 / 2/2 |
| Gereksiz uyarı | doğru (normal) | 0/5 |
| Gereksiz uyarı | doğru, bakış | 3/3 |
| Gereksiz uyarı | doğru, hızlı | 2/2 |
| Hız notu | doğru, hızlı | 2/2 |
| Hız notu | doğru (normal) / bakış / hatalı | 0/5 / 0/3 / 0/11 |
| Kamera uyarısı (betimsel) | bütün tekrarlar | 0/21 |
| Sol kol notu (betimsel) | bütün tekrarlar | 0/21 |

**Karışıklık tablosu** (satır: gerçek etiket; sütun: cümledeki ilk hata, "doğru" = hata söylenmedi):

| gerçek \ ilk söylenen | doğru | omuz | baş | öne kaçma | dirsek | az kaldırma |
| --- | --- | --- | --- | --- | --- | --- |
| doğru (normal+bakış+hızlı) | 5 | 3 | 0 | 0 | 2 | 0 |
| omuz | 0 | 3 | 0 | 0 | 0 | 0 |
| baş | 0 | 0 | 2 | 0 | 0 | 0 |
| öne kaçma | 0 | 0 | 0 | 1 | 1 | 0 |
| dirsek | 0 | 0 | 0 | 1 | 1 | 0 |
| az kaldırma | 0 | 0 | 0 | 0 | 0 | 2 |

### Sistemin yanıldığı tekrarlar: gözlemler
Bunlar tablolardaki ölçüm değerlerine dayanıyor. 18, 21 ve 13. tekrarları kullanıcı videodan izleyip doğruladı (9 Kas); diğerlerine videodan bakılmadı.
- **Dirsek ile öne kaçma karıştı (1 ve 21; katı ölçütteki 2 kaçırmanın ikisi):** Tekrar 1 (dirsek) için ilk söylenen "öne kaçma" oldu, dirsek ikinci sırada geldi. Tekrar 21'de (öne kaçma) tersi oldu. Tekrar 18'de (öne kaçma) de ikinci hata olarak 117° dirsek bükülmesi söylendi. Olası sebep: bükülü dirsek kolun kamerada kısa görünmesine yol açıyor (tekrar 1'de kol boyu %92'den %70'e indi). Öne kaçma da kolu kısa gösterdiği için önden bakan tek kamerada bu iki hata birbirine benziyor. **Videodan doğrulama (kullanıcı):** 18 ve 21. tekrarlarda kol hem öne götürülmüş hem de dirsek bükülmüş. Yani bu iki tekrarda dirsek uyarısı (18: 179°→117°, 21: 173°→117°) bir yanılgı değil, **gerçekten yapılan ikinci bir hata**. Tekrar 21'in katı ölçütte kaçırma sayılmasının sebebi: iki gerçek hatadan etiketteki değil, öbürü önce söylendi. Tekrar 1'e (dirsek → ilk söylenen öne kaçma) videodan bakılmadı.
- **Bakış tekrarlarında 3/3 gereksiz uyarı (2, 3, 13; bakış sağ-aşağıdaki işarete):** Baş, 3 tekrarın 2'sinde söylendi: tekrar 3'te ikinci hata olarak (2°→3°), tekrar 13'te ikinci hata olarak (1°→9°). Diğer söylenenler: tekrar 2'de dirsek (178°→174°), tekrar 3'te ilk hata olarak dirsek (178°→168°), tekrar 13'te ilk hata olarak omuz (kulak–omuz %28→%24). Normal doğru grupta oran 0/5. Madde 8'e göre bu, kullanıcının "başka yere bakınca hata çıkıyor" gözlemini **destekleyen bir işaret**; sayılar küçük olduğu için kanıt değil. Bazı sapmalar çok küçük (4°, 1°) ama bant kişiye özel ve dar olduğu için uyarıya dönüşüyor. **Videodan doğrulama (kullanıcı):** Tekrar 13'te kişi yalnızca gözlerini kaydırmak yerine başını belirgin şekilde eğmiş. Yani 13'teki baş uyarısı (1°→9°) **doğru bir tespit**; bu tekrar "başka yere bakış" sınamasına uygun değil. Bu durumda işaret zayıflıyor: yalnızca gözle bakılan 2 ve 3. tekrarlarda da uyarı çıktı (2: dirsek 4°; 3: dirsek 10° + baş 2°→3°), ama baş yalnızca 3'te ve çok küçük bir sapmayla söylendi. Ön kayıt gereği etiketler ve metrikler değiştirilmedi; tablo yukarıdaki gibi kalır.
- **Hızlı tekrarlarda 2/2 gereksiz omuz uyarısı (8, 16; süre 1.23 s ve 1.37 s):** İkisinde de "indirirken omuz" söylendi, sapma küçük (kulak–omuz %29→%27 ve %30→%28, omuz çizgisi yaklaşık 3°). Hız notu ikisinde de doğru şekilde çıktı. Olası sebep: hızlı tekrar, normal hızdaki kalibrasyon tekrarlarıyla zaman ekseninde iyi hizalanmıyor olabilir. Bu bir varsayım, doğrulanmadı.
- **Hatalı tekrarlarda ek (ikinci) hatalar:** 6 (az kaldırma) + baş 1°→4°; 10 (dirsek) + az kaldırma 117° (bükülü kol tepe açısını da düşürüyor); 11 (baş sola) + dirsek 179°→175°; **19 (baş sağa) + omuz** (sağ kulak–omuz mesafesi %28→%23). Tekrar 19 PLAN'daki örnekle ilgili: başı sağa eğmek sağ kulağı sağ omza yaklaştırıyor, bu yüzden omuz ölçütü de tetikleniyor. Ancak burada baş yine ilk hata olarak doğru söylendi; omuz ikinci sırada kaldı. Başı sola eğilen tekrar 11'de omuz söylenmedi.
- **Omuz silkmesi (projenin odağı):** 3/3 katı ölçütle doğru, normal doğru tekrarlarda omuz uyarısı 0/5.

## Kabul ölçütü kontrolü
- [x] Testler geçti (hazırlık): tam pytest `145 passed, 1 xfailed in 96.53s`.
- [x] Tablo var (karışıklık + cümle–etiket): `sonuclar/kendi_kayit/kisi1/karisiklik.csv`, `cumle_etiket.csv`.
- [x] Sistemin yanıldığı tekrarlar için kısa gözlem yazıldı (yukarıda; videoya bakarak doğrulama bekliyor).
- [x] Önceden belirlenenler çekimden önce commit'lendi.

## Kararlar ve sapmalar
- **Tek kişi** (9 Kas): PLAN'da isteğe bağlı olan 2. kişi çekilmedi; Adım 7 kişi 1 ile kapandı.
- **Etiketler değiştirilmedi** (9 Kas): Videodan izlenince 18 ve 21'de ek dirsek hatası, 13'te gerçek baş eğme görüldü. Ön kayıt gereği etiketler ve metrikler aynı bırakıldı; bu bilgi yalnızca gözlemlere yazıldı.
- **Videolar `.mp4`'e dönüştürülmedi** (9 Kas): OpenCV `.MOV`'u doğrudan ve doğru yönde okuyor; ffmpeg kurulu değil. Komutlarda `.mp4` yerine `.MOV` kullanılır. PLAN'daki dosya adlarından tek fark budur.
- **Serbest açıklamalar ayrı sütunda** (9 Kas): Kullanıcı açıklamaların `not` sütununa yazılmasını istedi. Ancak betik `not` sütununu makine için okuyor: yalnızca boş/`bakis`/`hizli` kabul ediyor ve hatalı tekrarlarda dolu `not`'u reddediyor (Karar 33). Önceden kaydedilmiş betiği değiştirmemek için açıklamalar yeni bir `aciklama` sütununa yazıldı; betik bu sütunu kullanmıyor.
- PLAN'daki eski protokol (5 kalibrasyon, 14 test tekrarı) yerine Karar 33 geçerli: 6 kalibrasyon ve 21 test tekrarı (öne kaçma, bakış ve hızlı tekrarlar eklendi).
- Karışık sıra, kâğıda elle yazmak yerine tohumlu bir betikle üretildi. Böylece hem tekrarlanabilir hem de çekimden önce sabit.

## Açık sorular / danışmana notlar
- Hızlı tekrarlar (~1 s), tekrar ayırıcının "30°'den 20°'ye en az 0,8 s" şartı yüzünden ayrılamayabilir. Bu durumda eşleşme dosyasıyla devam edilir ve ayrılamama "test videosunda ayrıldı" satırında raporlanır. Bu da bir bulgudur, eşik değiştirilmez. **Kişi 1 sonucu:** Bu endişe gerçekleşmedi; hızlı tekrarlar (1.23 s ve 1.37 s) 2/2 ayrıldı.
- 2. kişi: **çekilmeyecek** (kullanıcı, 9 Kas). Sonuçlar tek kişiye ait; "iki kişi birlikte" tabloları yalnızca kişi 1'i içerir.
