# ADIM 05 — Deney 3: kural tabanlı Türkçe geri bildirim

**Tarih:** 2026-11-07
**Durum:** Kısmen. Önceden belirlenenler commit'lendi (`23f9129`). Kod yazıldı ve sınandı. **Tam çalıştırma kullanıcıda**; sonuçlar ve kullanıcının örnek cümle yorumu bekleniyor.

## Önceden belirlenenler (kod ve sonuçlardan önce)
Kaynaklar: PLAN Adım 5, Güncelleme 01, 05 ve 06. Kod bu tanımlarla yazılacak. Sınama ve tam çalıştırmadan sonra hiçbiri değiştirilmeyecek. Sınama sırasında bir **kod hatası** bulunursa düzeltilir ve "Kararlar ve sapmalar" bölümüne yazılır. Tanımın kendisi değişmez.

### 0. Hangi sistem, hangi karar?
- **Yalnızca ana sistem:** v2 (açı bandı) + yönlü + ilk sürüm kaldırma (Karar 15, 17, 18).
- v1b ve yönsüz sistemler Deney 3'e girmez. Gerekçe: Cümledeki "normalde X, sende Y" ölçüsü açı bandının kare bazındaki μ'sünden gelir. Zaman bandında bu yok.
- **Karar değişmez.** Hangi hatanın söyleneceğini Deney 2'nin kuralı verir: aynı puanlar, aynı LOSO, aynı T, aynı `ht.ilk_iki`. Deney 3 yalnızca bu kararı cümleye çevirir.
- Deney 3'ün kararları `sonuclar/deney2/tahminler.csv` (v2_yonlu) ile **birebir aynı** olmalı. Kod bunu `assert` ile denetler.
- **En fazla 2 hata söylenir.**
  - 1. hata: max z ≥ T ise argmax z.
  - 2. hata: yalnızca ikinci z de T'yi geçerse (`soylenen2`).
  - max z < T ise olumlu cümle verilir.

### 1. Faz sınırları
- **Tanım:** Fazlar, değerlendirilen tekrarın **kendi** kol açısı eğrisinden bulunur. Eğri, açı bandının faz tanımında kullanılan 5 karelik hareketli medyanla yumuşatılmıştır.
  - A = yumuşatılmış eğrinin en büyük değeri (tepe açısı).
  - "Kol en üstteyken" fazı: yumuşatılmış kol açısının **0,85·A** veya üstünde olduğu **ilk kareden son kareye** kadar olan kesintisiz aralık.
  - Bu aralıktan önceki kareler "kaldırırken", sonraki kareler "indirirken".
- **Gerekçe:**
  - PLAN "referans tekrarın eğrisi" diyor. Açı bandında referans tekrar yok, kareler kendi kol açılarıyla karşılaştırılıyor.
  - Kişinin kendi tepe açısını kullanmanın bir nedeni daha var: Kalibrasyon tepesi kullanılsaydı, az kalkan bir tekrar "en üstte" fazına hiç girmezdi.
- **Hangi faz söylenir:** Bant dışı fazlalığın en çok toplandığı faz.
  - Fazlalık: kare başına, **beklenen yöndeki** imzalı bant dışı büyüklük, yani max(yön · `bant_disi`, 0). `bant_disi` = h − μ ∓ τ, ölçütün kendi biriminde.
  - Faz puanı: bu fazlalığın o fazdaki karelerde **toplamı**.
  - Eşitlikte sıra: kaldırırken → en üstte → indirirken.
- **Az kaldırma:** Faz her zaman "kol en üstteyken" (tepe açısıyla ilgili bir hata).

### 2. Ölçünün alındığı an
- An: **seçilen faz içinde** fazlalığın en büyük olduğu kare. Böylece cümledeki faz ile ölçü aynı ana ait olur.
- **Ölçü (`olcu`):** Kişinin o karedeki ham değeri.
- **Beklenen (`beklenen`):** O karede bandın ortası (μ). Fark = olcu − beklenen.
- **Yedek kural:** Seçilen ölçütte hiç bant dışı kare yoksa (beklenmiyor, çünkü z ≥ T için E > 0 olmalı), an şöyle seçilir: geçerli kareler içinde beklenen yöndeki imzalı farkın, yön · (h − μ), en büyük olduğu kare. Faz da o karenin fazı olur.
- **Az kaldırma:**
  - olcu = tekrarın tepe açısı (yumuşatılmış eğrinin en büyüğü; Deney 2 ile aynı).
  - beklenen = kalibrasyon tepelerinin **medyanı** (ilk sürümün referansı).
  - fark = beklenen − olcu.

### 3. Hatalı tekrarda hangi modelin μ'sü?
- **Karar 7 ile aynı:** Hatalı tekrar, n tane (n−1)'li modelin her biriyle ayrı ayrı değerlendirilir.
  - Kare başına μ ve `bant_disi`, bu modellerin **ortalamasıdır** (NaN'lar atlanır). Bir karede hiçbir model geçerli değilse o kare NaN olur.
  - Faz, an ve ölçü bu ortalama eğrilerden bulunur.
- **Doğru tekrar:** Kendisinin dışarıda bırakıldığı tek (n−1)'li model.
- **Gerekçe:** "Adil model" kuralı. Doğru ve hatalı tekrar aynı sayıda kalibrasyon tekrarından kurulmuş modellerle anlatılır. Ayrıca deterministiktir.
- Tüm n doğru tekrardan kurulan "tam model" kullanılmaz. Hatalı tekrara bir tekrar fazla bilgiyle bakmak olurdu. Uygulamada (Adım 6) ise tam model kullanılır, çünkü orada değerlendirilen tekrar kalibrasyona hiç girmez.
- **Az kaldırma:** beklenen = n modelin kalibrasyon tepesi medyanlarının ortalaması. Doğru tekrarda tek modelin medyanı.

### 4. Şiddet eşikleri (hafif / belirgin / çok belirgin)
- **Kişi bazlı birini-dışarıda-bırak.** Test kişisinin eşikleri, diğer 4 kişinin **önden + çapraz** tekrarlarından alınır (Deney 2'nin ayar görüşüyle aynı).
- Her hata türü için: eğitim kişilerinde **birincil etiketi o hata olan** bütün tekrarlar alınır (sistem yakalamış olsun ya da olmasın). Bunların kural puanının üçte birlik dilimleri bulunur: q₁ (%33,33) ve q₂ (%66,67).
- **Kural puanı:** Karar kuralının z'den önce kullandığı puan.
  - Duruş ölçütleri: yönlü E (0–1).
  - Az kaldırma: max(d, 0) (bkz. madde 5).
- **Sınıflar:**
  - puan < q₁ → hafif;
  - q₁ ≤ puan < q₂ → belirgin;
  - puan ≥ q₂ → çok belirgin.
- 2. hata da kendi hata türünün eşikleriyle derecelendirilir.
- **Cümledeki karşılığı:** hafif → "biraz", belirgin → "belirgin şekilde", çok belirgin → "çok".

### 5. Az kaldırmanın şiddeti
- Diğer hatalarla **aynı kural** (madde 4). Kural puanı ilk sürümün yönlü puanı max(d, 0); d = (tepe medyanı − tepe) / max(IQR, 5°).
- Eşikler, eğitim kişilerinin "az kaldırma" etiketli önden + çapraz tekrarlarındaki bu puanın üçte birlik dilimleri.
- Yeni bir sabit (ör. "20° altı hafif") **tanımlanmaz**.
- Cümlede derece olarak ölçü + fark söylenir. Şiddet kelimesi yalnızca puan dilimine dayanır.

### 6. Birimler ve yuvarlama
| hata | tespit ölçütü (değişmez) | cümledeki ölçü | birim |
| --- | --- | --- | --- |
| omuz | `YENI` | kulak–omuz dikey mesafesi = 100·YENI; ayrıca omuz çizgisi eğimi | gövde boyunun %'si; derece |
| baş | `bas` | baş–gövde açısı | derece |
| öne kaçma | `kol_boyu` (Deney 2'de 20/20 seçildi; kural her kişide yeniden seçer) | kolun kamerada görünen boyu = 100·kol_boyu; `on_kacma` seçilirse açı | gövde boyunun %'si; derece |
| dirsek | `dirsek` | dirsek açısı (180° = düz) | derece |
| az kaldırma | tepe açısı (ilk sürüm d) | kol açısı (üst kolun aşağı dikeyle açısı) | derece |

- **Omuz çizgisi eğimi (`omuz_egim`)** yalnızca anlatım içindir; tespite girmez. Hocanın P2 listesindeki "omuz çizgisinin gövde eksenine göre açısı" budur.
  - Tanım: 90° − açı(sağ omuz − sol omuz, omuz ortası − kalça ortası). Pozitif değer, sağ omzun gövde eksenine dik çizgiden yukarıda olduğunu gösterir.
  - Ayrı bir açı bandı modeliyle kurulur. Aynı kalibrasyon tekrarları ve aynı Karar 7 ortalaması kullanılır. Ayrı model, Deney 2 puanlarına hiç dokunmaz.
  - O karede `omuz_egim` bandı geçersizse cümle derece kısmı olmadan kurulur.
- **Yuvarlama:** Açılar en yakın 1°'ye, yüzdeler en yakın 1 puana yuvarlanır. Söylenen fark, yuvarlanmış iki değerin farkıdır. Böylece "normalde 32, sende 25, yani 7" tutarlı olur.
- Santimetre kullanılmaz.

### 7. Şablonlar
- Her hata ve her yön için şablon vardır. Bu, beklenen yön eğitimde ters çıksa bile cümle kurulabilsin diye. Ana sistemin yönleri ADIM_04'te: YENI −1, baş +1, kol_boyu −1, dirsek −1, kaldırma +1.
- Her şablon üç parça içerir: faz, şiddet, ölçü (normalde X, sende Y) ve bir **düzeltme** cümlesi.
- **2 hata:** "1. cümle" + " Ayrıca " + "2. cümle (kısa biçim)".
- **Doğru tekrar:** 4 varyasyon; somut (kolun tepe açısı + "omzun ve dirseğin normal aralıkta kaldı"). Seçim: (Segmentation.csv satır numarası + tohum) mod 4, tohum = 0.
- **Türkçe ek uyumu:** "dereceye" yazılarak derece ekinden kaçınılır. Yüzdelerin eki (%30'u, %25'i) sayının okunuşuna göre küçük bir fonksiyonla seçilir ve test edilir.

### 8. Anahtar kelime çıkarıcı (`cekirdek/metin_cozumleyici.py`)
- Sözlük tabanlıdır ve şablonlara özel değildir. Deney 4'te LLM cümleleri de aynı çıkarıcıyla ölçülecek.
- Metin cümle/yan cümle parçalarına ayrılır. Her parçada hata türüne ait kök kelime + eylem/yön kelimesi aranır.
- Olumlu parçalar ("normal aralıkta", "doğru yaptın" vb.) hata saymaz.
- Dönüş: söz edilen hata türlerinin **metindeki ilk geçiş sırasına göre** listesi.
- **Sözlük yalnızca şunlarla geliştirilir:** şablonlardan üretilen bütün birleşimler ve elle yazılmış en az 20 farklı cümle. Elle yazılan cümleler beklenen etiketleriyle birlikte `testler/` altına, **Deney 3 çalıştırılmadan önce** yazılır. Veri setindeki sonuçlara bakarak sözlük değiştirilmez.
- **Kabul:** Şablon birleşimlerinin %100'ü doğru çıkarılır. Elle yazılmış cümlelerin sonucu olduğu gibi raporlanır.

### 9. Metrikler (`deneyler/deney3.py`)
Cümleden çıkarılan hata listesi L olsun (en fazla 2 eleman beklenir).

| metrik | tanım |
| --- | --- |
| **katı** /100 | hatalı tekrarlarda L'nin ilk elemanı = birincil hata |
| **esnek** /100 | hatalı tekrarlarda L'nin ilk elemanı ∈ {birincil} ∪ ek hatalar |
| **ilk iki** /100 | hatalı tekrarlarda birincil hata ∈ L |
| **ilk iki (esnek)** /100 | hatalı tekrarlarda L ∩ ({birincil} ∪ ek hatalar) boş değil |
| hatalılarda olumlu cümle /100 | hatalı tekrarda L boş (kaçırma) |
| **doğrularda gereksiz uyarı** /100 | doğru tekrarda L boş değil |
| doğrularda iki uyarı /100 | doğru tekrarda \|L\| = 2 |
| çıkarıcı uyumu /100 | L = sistemin söylemek istediği hata listesi (bütün tekrarlarda) |

- **Görüş:**
  - **Ana tablo önden + çapraz** (|görüş| ≤ 60°).
  - Ayrıca tüm görüşler, profil ve üç görüş grubu.
  - Kişi bazlı tablo (5 kişi).
- **Belirsizlik:** Katı, esnek, ilk iki ve gereksiz uyarı için kişi bazlı bootstrap %95 GA. 2000 tekrar, tohum 1 (Deney 2 ile aynı). Önden + çapraz ve tüm görüşler için.
- **Tutarlılık denetimi:** Çıkarıcı uyumu %100 ise katı = Deney 2 "tür doğru (katı)" ve ilk iki = Deney 2 "birincil söylenen ilk iki içinde" olur. Bu eşitlik raporda gösterilir.
- **Betimsel ölçü tablosu:** Her hata türü için, o hata söylendiğinde |fark| medyanı ve çeyrekleri. Ayrıca şiddet sınıflarının dağılımı ve faz dağılımı.
- **Örnek cümleler** (`sonuclar/deney3/ornek_cumleler.md`): önden + çapraz, tohum 0.
  - Her gerçek sınıftan 3 tekrar (6 × 3 = 18) ve sistemin iki hata söylediği tekrarlardan 2 tane, toplam 20.
  - Yanlarında gerçek etiket, ek hatalar, sistemin kararı ve görüş yazılır.
- **Çıktılar** `sonuclar/deney3/` altında:
  - `cumleler.csv`: her tekrar için kod alanları (`hata`, `taraf`, `faz`, `yon`, `siddet`, `olcu`, `beklenen`, `fark`, `birim`), cümle ve L;
  - `ozet.csv`, `gorus_grubu.csv`, `kisi.csv`, `bootstrap.csv`, `olcu.csv`, `siddet_esikleri.csv`;
  - `ornek_cumleler.md`.

## Basit anlatım
- Deney 2, bir tekrarın hangi hatayı içerdiğine karar veriyordu. Deney 3 bu kararı kişinin anlayacağı **Türkçe bir cümleye** çeviriyor.
- Cümlede üç şey var:
  - **ne zaman** oldu: kolu kaldırırken / kol en üstteyken / indirirken;
  - **ne kadar**: "normalde X, sende Y", derece ya da gövde boyunun yüzdesi;
  - **ne yapmalı**: düzeltme cümlesi.
- Doğru tekrarda somut, olumlu bir cümle veriliyor.
- Ölçme yöntemi: Bir "anahtar kelime çıkarıcı" cümleyi okuyor ve hangi hatadan söz ettiğini buluyor. Örneğin cümlede "omuz" ve "kulak" geçiyorsa, cümle omuz silkmesinden söz ediyor demektir. Sonra bu, videonun gerçek etiketiyle karşılaştırılıyor.
- Yöntemin hiçbir parçası değişmedi (Karar 18). Karar, Deney 2'deki kararla birebir aynı. Değişen tek şey, kararın cümleye çevrilmesi.

## Yapılanlar
- `cekirdek/geribildirim.py` (uygulama da bunu kullanacak):
  - faz (`anlatim_fazlari`) ve an seçimi (`an_sec`);
  - Karar 7 ortalaması (`model_ortalamasi`);
  - sapma kodu (`SapmaKodu`, `durus_kodu`, `kaldirma_kodu`);
  - şiddet (`siddet_esikleri`, `siddet_sinifi`);
  - şablonlar (`hata_cumlesi`, `olumlu_cumle`, `geri_bildirim`);
  - Türkçe sayı ekleri (`sayi_eki`: %30'u, %25'e).
- `cekirdek/metin_cozumleyici.py`: Sözlük tabanlı çıkarıcı (`cozumle`). Metni parçalara ayırır, olumlu parçaları atlar, her hata türü için kök + eylem kuralı uygular. Bulduğu hataları metindeki sıralarıyla döndürür.
- `cekirdek/ozellikler.py`: Yeni ölçüt `omuz_egim` (omuz çizgisinin gövde eksenine göre eğimi). Yalnızca anlatım içindir, tespite girmez. Deney 1 ve 2 ölçütleri değişmedi; Deney 1 regresyon testi geçiyor.
- `deneyler/deney3.py`:
  - Deney 2 puanlarından aynı LOSO kuralı yeniden kuruluyor. Kararların `sonuclar/deney2/tahminler.csv` ile aynı olduğu `assert` ile denetleniyor.
  - Her tekrar için kare bazında ayrıntı hesaplanıyor (hatalı tekrarda n modelin ortalaması), sonra cümle kuruluyor ve çıkarıcı çalıştırılıyor.
  - Metrikler, kişi bazlı bootstrap ve 20 örnek cümle üretiliyor.
- Testler:
  - `testler/test_geribildirim.py`:
    - sayı ekleri (22 sayı);
    - faz ve an seçimi;
    - Karar 7 ortalaması;
    - şiddet dilimleri;
    - **şablon birleşimleri**: her hata, yön, şiddet, faz, ölçülü/ölçüsüz (tek hata ve iki hata), 4 olumlu varyasyon;
    - elle yazılmış 24 cümle.
  - `testler/elle_cumleler.py`: 24 cümle, Deney 3 çalıştırılmadan önce yazıldı.
- `docs/GELECEK_CALISMA.md` madde 6 eklendi (aşağıdaki sınama gözlemi).

## Değişen / eklenen dosyalar
| Dosya | Ne işe yarıyor |
| --- | --- |
| `cekirdek/geribildirim.py` | Sapma kodu ve Türkçe cümle (deney + uygulama ortak) |
| `cekirdek/metin_cozumleyici.py` | Cümleden hata türlerini çıkaran sözlük (Deney 3 ve 4) |
| `cekirdek/ozellikler.py` | `omuz_egim` (yalnızca anlatım) |
| `deneyler/deney3.py` | Deney 3 |
| `testler/test_geribildirim.py`, `testler/elle_cumleler.py` | Testler |

## Nasıl çalıştırılır
```bash
python -m deneyler.deney3
```
- **Beklenen süre:** yaklaşık 1–3 dakika. Sınamada bootstrap'sız 13,4 s sürdü; bootstrap (2000 tekrar) ek süre getirir.
- **Ön koşul:** `sonuclar/deney2/puanlar.csv` dosyası, Güncelleme 06 sonrası haliyle.
- **Çıktı:** `sonuclar/deney3/`.

## Sınama (kod denetimi; sonuçlar raporlanmadı)
Kod bir kez, geçici klasörde ve bootstrap'sız çalıştırıldı. Amaç yalnızca kod hatalarını bulmaktı. Sonuç sayıları burada raporlanmıyor; tam çalıştırmadan alınacak. Sınamadan sonra hiçbir tanım değişmedi.
- Kararlar Deney 2 ile **1668/1668 aynı**. Çıkarıcı uyumu bütün görüşlerde 100,0.
- Hiçbir cümlede "nan" yok. Söylenen her hatanın bir ölçüsü ve fazı var.
- **Gözlem (kod hatası değil):** Söylenen dirsek hatalarının 56'sında ölçü 90°'nin altında. En küçükleri 2–6°.
  - Ham veride bu değerler gerçekten var. Örnek: `ex1_Honza cam3 o10`; kare medyanı 169,0°, en küçük kare 6,5°, 183 karenin 16'sında açı 90°'nin altında.
  - İncelenen örnekler çapraz ya da profil görüşten. Sebep, 2B dirsek açısının bazı karelerde çökmesi: kol kameraya dönük oluyor ya da görünürlük düşüyor (bir örnekte 0,06).
  - Önceden belirlenen kural ölçüyü sapmanın en büyük olduğu **tek kareden** aldığı için, bu uç kareler cümleye girebiliyor.
  - Kural değiştirilmedi. Bu bir sınırlılık olarak raporlanacak; sağlam alternatif `docs/GELECEK_CALISMA.md` madde 6'da.

## Sonuçlar
*Kullanıcının tam çalıştırmasından sonra `sonuclar/deney3/ozet.csv`, `bootstrap.csv`, `kisi.csv`, `gorus_grubu.csv`, `olcu.csv` dosyalarından kopyalanacak.*

## Kabul ölçütü kontrolü
- [ ] Metrik tablosu var (tam çalıştırmadan sonra)
- [ ] 20 örnek cümle var (`sonuclar/deney3/ornek_cumleler.md`)
- [ ] Kullanıcı örnekleri okudu; yorumu buraya not edildi
- [x] Çıkarıcı, şablon birleşimlerinin %100'ünde doğru (`test_cikarici_*_sablonlari`)
- [x] Elle yazılmış 24 cümlenin 23'ü doğru. Biri bilinen sınırlılık: "Omzun kalkmadı, kolun düzdü, güzel tekrar." cümlesinde omuz bulunuyor, çünkü olumsuz geçmiş zaman ayırt edilmiyor. Not: Sözlük bu 24 cümleyle geliştirildi, bu yüzden bu oran iyimser. Asıl bağımsız sınav Deney 4'teki LLM cümleleri olacak.
- [x] `pytest`: `112 passed, 1 xfailed`

## Kararlar ve sapmalar
- **Deney 3 yalnızca ana sistemle** (madde 0): v1b ve yönsüz sistemlerde kare bazındaki μ yok.
- **Çıkarıcıda geliştirme sırasında iki düzeltme yapıldı.** İkisi de yalnızca testler ve elle yazılmış cümleler kullanılarak yapıldı; veri setinin sonuçlarına bakılmadı:
  - "kulağına" kelimesindeki k → ğ yumuşaması eklendi;
  - "biraz kaldırıyorsun" içindeki "az kald"ın kaldırma sayılmaması için kelime sınırı eklendi.
- **Yuvarlama:** "en yakın 1" kuralında yarımlar yukarı yuvarlanır (2,5 → 3).
- **`omuz_egim` bandı ayrı modelle** kuruldu (madde 6). Deney 2 puanları değişmedi; denetim bunu doğruluyor.

## Açık sorular / danışmana notlar
- Dirsek ölçüsündeki tek kare uç değerleri (yukarıdaki gözlem). Raporda bir "sınırlılık" cümlesi yeterli mi?
