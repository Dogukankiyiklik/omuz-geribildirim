# Güncelleme 07 — 7 Kasım 2026 gece (danışmandan)

Claude Code: `/clear` sonrası yeni oturum. Sırayla oku:
1. `CLAUDE.md`
2. `PLAN.md`
3. `ilerleme/KARARLAR.md`
4. `ilerleme/ADIM_05.md` (kullanıcının yorumu dahil)
5. `docs/GELECEK_CALISMA.md`
6. bu dosya

Kararları (21–28) `KARARLAR.md`'ye işle. Önce "Yapılacaklar 1–4" ile Adım 5'i kapat, sonra **Adım 6**'ya geç.

## Önce kısa bir değerlendirme
Adım 5 temiz yapıldı:
- Önceden belirlenenler sonuçlardan önce commit'lendi.
- Kararlar Deney 2 ile 1668/1668 aynı çıktı.
- Tek kare ölçüsü sorunu sınamada görüldü ve kural değiştirilmeden raporlandı.

Doğru yaklaşım buydu. Kullanıcının yorumu (ADIM_05) da önemli bir düzeltme getiriyor; Karar 28'e bakın.

## Kararlar

### Karar 21 — Cümledeki ölçü için "sağlam ölçü" (tespit değişmez)
**Sorun:** Ölçü tek kareden alındığı için 2B iskeletin çöktüğü kareler cümleye giriyor. Örnekler: "kolun %112'si kadar görünürken %11'e kısaldı", "dirsek açın 6 dereceye indi". Uygulamada bu cümleler gösterilirse P1'in "fiziksel olarak yorumlanabilir ölçü" şartı zarar görür.

**Karar 18 ile ilişkisi:** Karar 18 puanlamayı ve karar kuralını dondurdu. Ölçü bunların ikisine de girmiyor. Deney 3'ün hiçbir metriği (katı, esnek, ilk iki, gereksiz uyarı) ölçüye bağlı değil. Bu yüzden değişiklik yalnızca **anlatım** katmanında. Bu kural Adım 5 sonuçları görüldükten sonra tanımlandı; raporda böyle yazılır.

**Tanım (bundan sonra değiştirilmez):**
- Hata türü, faz ve faz seçimi aynen kalır (ADIM_05 madde 0–1).
- K, seçilen fazdaki şu karelerden oluşur:
  - beklenen yöndeki fazlalığı > 0 olan;
  - ölçütün kullandığı bütün eklemlerin görünürlüğü ≥ 0,5 olan.
  - 0,5, MediaPipe'ın varsayılan görünürlük eşiğidir; veriye bakılarak seçilmedi.
- K'de 3 kareden az varsa görünürlük koşulu kaldırılır. Yine 3 kareden azsa ADIM_05'teki tek kare kuralı kullanılır. Hangi yolun kullanıldığı `cumleler.csv`'ye yazılır.
- `olcu` = K'deki ham değerlerin medyanı; `beklenen` = K'deki μ'lerin medyanı. Yuvarlama ve fark ADIM_05 madde 6'daki gibi (hasta cümlesi için Karar 28'e bakın).
- `omuz_egim` aynı K ile hesaplanır.
- Az kaldırma değişmez; tepe zaten 5 karelik medyanla yumuşatılmış.
- Hatalı tekrarda Karar 7 ortalaması aynen (ADIM_05 madde 3).

**Uygulama:**
- `cekirdek/geribildirim.py` içinde `olcu_surumu = "tek_kare" | "saglam"` seçeneği olur. **Uygulamanın varsayılanı `"saglam"`.**
- Deney 3 `--olcu-surumu saglam` ile çalıştırıldığında şu ek çıktılar yazılır: `olcu_saglam.csv`, `cumleler_saglam.csv`, `ornek_cumleler_saglam.md` (aynı 20 tekrar).
- Ana `ozet.csv`, `bootstrap.csv` vb. tek kare sürümüyle aynı kalır; kod bunu `assert` ile denetler.
- Tek kare sürümü birincil sonuç olarak kalır; sağlam sürüm betimsel karşılaştırmadır.
- **Tek deneme yapılır.** Sağlam sürüm de inandırıcı olmayan değerler üretirse olduğu gibi raporlanır ve yeni bir sürüm denenmez.

### Karar 22 — Şiddet tanımı değişmez
- Baş ve öne kaçmada "hafif" sınıfının hiç çıkmaması sınırlılık olarak raporlanır. Sebep ADIM_05'te doğru açıklanmış.
- Şiddet yalnızca uzman ayrıntısında kullanılır; hasta cümlesinde kullanılmaz (Karar 28).
- Alternatif (eşikleri yalnızca sistemin yakaladığı tekrarlardan almak) `GELECEK_CALISMA.md`'ye 7. madde olarak yazılır.

### Karar 23 — Deney 3'ün yorumu ve iddia kapsamı (Karar 20'ye ek)
| İddia | Kanıt | Güç |
| --- | --- | --- |
| Kural tabanlı cümleler hatayı açıkça adlandırır | Çıkarıcı uyumu %100 | **Zayıf kanıt.** Çıkarıcı aynı şablonlarla ve 24 elle yazılmış cümleyle geliştirildi. Bağımsız sınav Deney 4'teki LLM cümleleri. |
| İki hata söylemek, gerçek hatayı söyleme oranını artırır | ö+ç 56,6 → 67,4; silkmede 41,5 → 73,3; bedeli doğrularda iki uyarı 1,6 /100 | **Orta.** "İlk iki" tanımı gereği katıdan küçük olamaz; asıl bilgi, kazancın bedelinin küçük olması. |
| Doğru tekrarda gereksiz uyarı azdır | 7,5 /100 (GA 3,9–10,4) | **Orta** |
| Geri bildirim fiziksel ölçü içerir | Bütün cümlelerde ölçü var; omuz medyan fark 8 puan, baş 14° | Omuz ve başta makul. Dirsek ve öne kaçmada tek kare sorunu var (Karar 21). |

### Karar 24 — Uygulamanın kural parametreleri
- Uygulama yeni bir kişiyle çalışır ve test kişisi yoktur. Bu yüzden kural **beş kişinin hepsinin önden + çapraz tekrarlarıyla** kurulur.
- Prosedür, LOSO'daki eğitim adımıyla birebir aynıdır: ölçekleme (medyan, IQR), yönler, `on_kacma`/`kol_boyu` seçimi, T ve şiddet eşikleri.
- Bunları tek bir betik üretir: `python -m araclar.kural_disa_aktar` → `modeller/kural_ex1.json`. Dosyaya sürüm bilgisi yazılır: kaldırma sürümü, ölçü sürümü, commit, tarih.
- ADIM_06'da bu değerler LOSO'daki beş değerle yan yana verilir. Örneğin T'nin LOSO aralığı 3,68–5,00 idi; beş kişiyle seçilen T'nin bu aralıkta ya da yakınında çıkması beklenir. Çıkmazsa durulmaz, yalnızca yazılır.
- Kalibrasyonda tam model kullanılır, yani kalibrasyondaki bütün doğru tekrarlar (ADIM_05 madde 3).

### Karar 25 — Canlı tekrar ayırma (önceden sabit) ve veri setinde sınanması
**Kural:**
- Kol açısı 5 karelik hareketli medyanla yumuşatılır.
- Tekrar adayı, yumuşatılmış açı 30°'nin üstüne çıkınca başlar ve ardından 20°'nin altına inince biter. Tepe en az 60°, süre en az 0,8 s olmalıdır.
- **Sınırlar dinlenmeden dinlenmeye uzatılır**, çünkü veri setindeki `first_frame`/`last_frame` hareketin başından sonuna kadardır:
  - dinlenme açısı = başlangıç geçişinden önceki 1 s'nin medyanı;
  - başlangıç = 30° geçişinden geriye doğru, açının (dinlenme + 5°) ya da altında olduğu son kare; en fazla 2 s geri;
  - bitiş = 20° geçişinden sonra, açının (dinlenme + 5°) ya da altına indiği ilk kare; en fazla 1 s ileri.
- Kod `cekirdek/tekrar_ayirici.py` içindedir; uygulama ve sınama aynı kodu kullanır.

**Veri setinde sınama** (`python -m deneyler.tekrar_ayirma`, kısa):
- Ayırıcı, Ex1'in bütün sürekli iskelet dizilerinde çalıştırılır ve `Segmentation.csv` ile karşılaştırılır. Sonuçlar önden + çapraz ve tüm görüşler için ayrı verilir.
- Eşleşme: bulunan ve etiketli tekrar arasında zaman örtüşmesi (IoU) ≥ 0,5.
- Raporlanacaklar:
  - bulunan / kaçırılan / fazladan tekrar sayıları;
  - başlangıç ve bitiş farkının medyanı ve çeyrekleri (kare);
  - hata türüne göre kaçırma.
- **Eşikler bu sonuca göre değiştirilmez.** Etiketli tekrarların %90'ından azı bulunursa durum ADIM_06'ya yazılır ve kullanıcıya söylenir; uygulama işine devam edilir.

### Karar 26 — Kamera açısı uyarısının eşiği (Karar 9'un ayrıntısı)
- Oran = dinlenmede (tekrar öncesi ilk 8 kare) omuz genişliği / gövde boyu, en-boy düzeltmeli.
- Veri setinin doğru tekrarlarında bu oranın dağılımı, görüş grubuna göre (önden / çapraz / profil) ADIM_06'da tablo olarak verilir.
- **Eşik = çapraz (30–60°) grubundaki oranın 10. yüzdeliği.** Kalibrasyonun ilk saniyelerinde oran bu eşiğin altındaysa şu uyarı gösterilir: "Kameraya daha önden durun." Uyarı kalibrasyonu engellemez.
- Gerekçe: Ana sonuçlar |görüş| ≤ 60° için geçerli (Karar 6); profil (70–90°) sınırlılıktır.

### Karar 27 — Demo güvenliği ve sürüm
- **Video dosyası modu birincil demo yoludur;** canlı kamera artıdır.
- Sunumda internet, ışık ya da kamera sorununa karşı önceden kaydedilmiş bir kalibrasyon + test videosu ve bunun yığın modu çıktısı hazır tutulur. Adım 7'nin kayıtları bu iş için de kullanılır.
- MediaPipe sürümü: Veri seti MediaPipe v0.10.20, Full model ile üretildi. Uygulamada mümkünse aynı sürüm ve `pose_landmarker_full` kullanılır. Kurulamazsa kullanılan sürüm `requirements.txt` ve ADIM_06'ya yazılır, fark sınırlılık olarak not edilir.
- Uygulamanın ilk sürümü yalnızca Ex1 içindir. Menü yapısı ileride egzersiz eklemeye uygun kurulur, ama Ex7 uygulamaya **eklenmez**.

### Karar 28 — İki katmanlı geri bildirim: hasta cümlesi + uzman ayrıntısı
**Kullanıcının yorumu:** "Hasta olarak okusam hiçbir şey anlamam." Haklı. "Kolun kamerada gövde boyunun %84'ü kadar görünürken %67'ye kısaldı" gibi ifadeler geri bildirim gibi değil, ölçüm raporu gibi okunuyor.

Öte yandan hocanın P1 şartı, hatanın **büyüklüğünün fiziksel olarak** söylenmesini istiyor; yalnızca "yanlış yaptın, sebebi şu" yetmez. Hocanın kendi örneği iki isteği birden karşılıyor: kısa, derece içeriyor ve ne yapılacağını söylüyor ("…sen 80° kaldırdın. Kolunu yaklaşık 10° daha yukarı kaldırmalısın."). Hedef bu üslup.

Karar kuralı, faz, an ve ölçü değişmez (Karar 18, 21). Değişen yalnızca cümlenin yazılışı. Aynı `SapmaKodu`'ndan iki metin üretilir.

**1. Hasta cümlesi** (`hasta_cumlesi`). Uygulamada büyük harfle gösterilen ana çıktıdır.
- Her hata için en fazla iki kısa cümle yazılır: **ne oldu** (fazıyla) ve **ne yapmalı**. Hata başına yaklaşık 20 kelimeyi geçmez.
- **Yüzde ve "gövde boyu" hiç kullanılmaz.** Sayı yalnızca **derece** olarak ve yalnızca şu durumlarda söylenir:
  - az kaldırma: tepe açısı, normali ve eksik (hocanın örneği);
  - baş: eğilme farkı;
  - dirsek: bükülme farkı;
  - omuz: omuz çizgisi eğimi farkı (`omuz_egim`, sağlam ölçüyle), yalnızca o karede geçerliyse;
  - öne kaçma: sayı yok. Kol boyundan derece tahmini gelecek çalışmanın 5. maddesidir.
- **Hasta cümlesinde dereceler 5°'ye yuvarlanır.** Söylenen fark, yuvarlanmış iki değerin farkıdır. Yuvarlanmış fark 0 ise sayı söylenmez ve cümle sayısız kurulur.
  - Gerekçe: Tek kameralı 2B açı ölçümünün hatası birkaç derecedir (M20: ±7° uyum sınırı; M41/M42). 1°'lik hassasiyet iddia etmek abartı olur. Bu seçim sonuçlara bakılarak değil, ölçüm belirsizliğine göre yapıldı.
- **Şiddet kelimesi** ("biraz", "belirgin şekilde", "çok") hasta cümlesinde kullanılmaz; büyüklüğü derece taşır.
- İki hata söylenirken biçim şudur: 1. hata cümlesi + " Ayrıca " + 2. hata cümlesi.
- Doğru tekrarda kısa ve somut 4 varyasyon kullanılır; seçim kuralı ADIM_05'teki gibidir. Örnek: "Hareketi doğru yaptın. Kolun yaklaşık 170 dereceye çıktı, omzun ve dirseğin yerindeydi."

**Örnek üslup** (son sözcükleri Claude Code seçer; bağlayıcı olan yukarıdaki kurallardır):
- omuz: "Kolunu kaldırırken sağ omzunu kulağına doğru yaklaşık 10 derece kaldırdın. Omzunu aşağıda ve gevşek tut."
- baş: "Kolun yukarıdayken başını yaklaşık 20 derece yana eğdin. Başını dik tut, karşıya bak."
- dirsek: "Kolun yukarıdayken dirseğini yaklaşık 25 derece büktün. Kolunu düz tut."
- öne kaçma: "Kolunu kaldırırken kolun öne kaçtı. Kolunu tam yana, vücudunla aynı hizada kaldır."
- az kaldırma: "Kolunu 150 dereceye kadar kaldırdın; normalde 170 dereceye çıkıyorsun. Yaklaşık 20 derece daha yukarı kaldır."

**2. Uzman ayrıntısı** (`uzman_ayrintisi`). Fizyoterapist, hoca ve rapor içindir.
- Bugünkü ölçülü cümlelerdir, sağlam ölçüyle. Şiddet, gövde yüzdesi ve 1°'lik yuvarlama burada kalır.
- Uygulamada panelin alt kısmında küçük yazıyla ya da bir tuşla açılıp kapanan bir alanda gösterilir.

**Deney 3'te değerlendirme:**
- `cumleler.csv`'ye iki metin de yazılır ve çıkarıcı **ikisinde de** çalıştırılır.
- Kararlar aynı olduğu için iki metnin metrikleri birbirine ve mevcut `ozet.csv`'ye eşit olmalıdır; bu `assert` ile denetlenir. `ozet.csv`'ye "metin = hasta / uzman" sütunu eklenir.
- Ek betimsel tablo: iki metnin ortalama kelime sayısı ve hasta cümlelerinde sayı içeren cümle oranı (hata türüne göre).
- `ornek_cumleler.md`'de aynı 20 tekrar yer alır; her birinde önce hasta cümlesi, altında uzman ayrıntısı.
- **Çıkarıcı:** Yeni şablonların bütün birleşimleri testlere eklenir ve %100 doğru çıkarılmalıdır. Sözlük yalnızca şablonlar ve elle yazılmış cümlelerle geliştirilir (ADIM_05 madde 8), veri setindeki sonuçlara bakılarak değil. Olumlu cümlelerdeki "yerindeydi" gibi yeni kalıplar olumlu parça listesine eklenir.

**Deney 4 için not:** LLM'den istenen cümle de hasta cümlesi üslubunda olacak; aynı kurallar istem metnine yazılacak. Ayrıntılar Adım 8'de verilecek.

**Rapor ve sunum:** "Geri bildirim iki katmanlı: hasta kısa bir cümle ve derece duyar; uzman ölçülü ayrıntıyı görür." Bu, P1'in hem "anlaşılır doğal dil" hem "fiziksel büyüklük" şartını karşılar.

## Yapılacaklar
1. **Karar 21 ve 28'i uygula:** `cekirdek/geribildirim.py`, testler, `deneyler/deney3.py`. Testlere şunlar eklenir:
   - sağlam ölçünün özel durumları: K boş, K'de 3 kareden az, görünürlük yolu;
   - hasta cümlesinde 5°'lik yuvarlama ve yuvarlanmış fark 0 olunca sayısız cümle;
   - hasta şablonlarının çıkarıcıyla %100 doğru okunması.
2. `python -m deneyler.deney3 --olcu-surumu saglam` komutunu çalıştır (kısa; sen çalıştırabilirsin). Ana metriklerin değişmediği `assert` ile denetlenir. `GELECEK_CALISMA.md`'ye madde 7'yi ekle (Karar 22).
3. **ADIM_05'in sonuna "Ek: Güncelleme 07" yaz.** Sayılar CSV'den kopyalanır. İçerik:
   - sağlam ölçü tablosu, tek kare sürümüyle yan yana: |fark| medyanı ve çeyrekleri; K'nin hangi yoldan geldiği, sayılarla;
   - iki metnin kelime sayısı ve sayı içerme tablosu;
   - aynı 20 örnekten **en az 8**'inin hasta cümlesi ve uzman ayrıntısı yan yana. Örnek 4, 5, 7, 10, 12, 13, 15 ve 17 mutlaka bulunsun.
4. **Dur ve kullanıcıya göster.** Kullanıcı yeni hasta cümlelerini okuyup tek satırlık bir onay ya da düzeltme verir. Onay gelince ADIM_05'e yazılır ve Adım 5 kapanır.
   - Kullanıcı yalnızca **sözcük düzeltmesi** isterse (ör. "bu ifade garip") düzeltilebilir; bu metrikleri etkilemez.
   - Yapısal bir değişiklik isterse danışmana sorulur.
5. **Karar 24 betiği:** `araclar/kural_disa_aktar.py` ve `modeller/kural_ex1.json`. Değerler ADIM_06'da LOSO değerleriyle yan yana verilir.
6. **Adım 6 — uygulama** (PLAN Adım 6 + Karar 8, 9, 21, 24–28):
   - Önce Karar 25'teki tekrar ayırıcıyı yaz ve veri setinde sına (kısa deney; sen çalıştırabilirsin).
   - Sonra uygulamanın kendisini yaz:
     - kalibrasyon: varsayılan 6 tekrar, en az 5; kamera açısı uyarısı; her tekrar için onay/ret;
     - değerlendirme: video dosyası ve canlı kamera;
     - panel: tekrar no, karar, **hasta cümlesi büyük**, uzman ayrıntısı küçük ya da tuşla açılır, son 5 tekrar, omuz eğrisi ve bandı;
     - tekrar sonrası bindirme oynatımı (P3; `cekirdek/bindirme.py`);
     - PIL ile Türkçe metin;
     - oturum CSV'si;
     - yığın modu: `python -m uygulama.toplu`.
   - **Yumuşatma yok** (Karar 10). İskelet çizimi çok titrerse yalnızca çizim için hafif One Euro kullanılabilir.
   - Uygulamada karar ve cümle yalnızca `cekirdek/` içinden içe aktarılır.
   - **Hızlı uçtan uca sınama:** Veri setinden bir kişinin bir videosu (ör. `ex1_Honza cam1`, önden yönelim) yığın moduyla, MediaPipe video dosyasından yeniden çalıştırılarak işlenir. İlk 6 doğru tekrar kalibrasyon, kalan tekrarlar değerlendirme olur. Çıkan kararlar ve cümleler gerçek etiketlerle bir tabloda verilir. Bu bir sağlık kontrolüdür, değerlendirme sonucu değildir.
   - Kabul ölçütü PLAN'daki gibi: kullanıcı kendi kamerasıyla kalibrasyon yapıp en az 5 tekrar değerlendirir, video modu çalışır, kopya kod yoktur.
   - ADIM_06'ya kullanıcı için **demo talimatı** adım adım yazılır: hangi komut çalıştırılacak, kamera nereye konacak, kalibrasyonda ne yapılacak.
7. Ardından PLAN'daki sırayla Adım 7 (kendi kayıtlar). Adım 7 bitmeden isteğe bağlı adımlara geçilmez.
