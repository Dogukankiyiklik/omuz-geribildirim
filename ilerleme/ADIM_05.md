# ADIM 05 — Deney 3: kural tabanlı Türkçe geri bildirim

**Tarih:** 2026-11-07
**Durum:** Hazırlık. Önceden belirlenenler yazıldı ve commit'lendi. Kod henüz yok, sonuç yok.

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
