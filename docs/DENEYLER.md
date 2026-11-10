# Deneyler: neyi test ettik, ne bulduk?

Ödev açısından cevaplanan **üç soru** var. Her sayı köşeli parantezdeki dosyadan kopyalandı (`sonuclar/` altına göre yol). Sistemin nasıl çalıştığı: [`SISTEM.md`](SISTEM.md).

## Ortak kurulum (bir kez okunur)

- **Veri:** REHAB26-ViewAngles, Ex1 (kolu yana kaldırma, sağ kol). 5 sağlıklı kişi × 11 yönelim × 3 kamera. Her tekrarın doğru mu, yanlışsa hangi hata olduğu etiketli; hatalar kişilerin bilerek yaptığı taklitler.
- **Görüş grupları:** kişinin kameraya göre açısı. **Önden + çapraz** (0–60°) uygulamanın önerilen kurulumu; **profil** (70–90°) ayrı raporlanır, çünkü orada yana kaldırma kameraya doğru bir harekete dönüşüyor.
- **Dürüstlük kuralları:**
  - Eşikler **kişi bazlı birini-dışarıda-bırak** ile ayarlandı: 4 kişide ayarla, 5. kişide sına, her kişi için tekrarla.
  - Değerlendirilen tekrar hiçbir zaman kendi bandının içinde değil.
- **AUC:** rastgele bir silkmeli tekrarın rastgele bir doğru tekrardan daha yüksek hata puanı alma olasılığı. 0,5 yazı tura, 1 kusursuz.

## Soru 1 (Problem 2): Kişiye özel açı bandı, ham ölçüye göre omuz silkmesini daha iyi buluyor mu?

**Cevap: evet, belirgin biçimde.** Ham ölçü silkmeyi zayıf ayırıyor. Kişinin kendi doğru tekrarlarından kurulan açı bandıyla AUC 0,70'ten 0,95'e çıkıyor. Başkalarının tekrarlarından kurulan "genel" bant ham ölçüyle aynı düzeyde kalıyor; yani kalibrasyon kişiye özel olmalı.

**Nasıl ölçüldü** (`deneyler/deney1.py`): Dört omuz ölçüsünün her biri üç yolla puanlandı.

- **Ham:** tekrar kendi başlangıcıyla (kol aşağıdayken) karşılaştırılır; omuz başlangıca göre ne kadar uzaklaştı?
- **Genel bant:** açı bandı, ama aynı kamera ve yönelimdeki diğer 4 kişinin bütün doğru tekrarlarından kurulur.
- **Kişiye özel açı bandı:** kişinin kendi doğru tekrarlarından kurulur. Değerlendirilen tekrar banda girmez.

Kulak–omuz ölçüsü (`YENI`), silkmeli tekrar ile doğru tekrar [`deney1/ozet.csv`]:

| Değerlendirme | Bütün görüşler | Önden + çapraz | Silkme / diğer hatalar |
| --- | --- | --- | --- |
| Ham ölçü (bant yok) | 0,704 | 0,761 | 0,699 |
| Genel bant (diğer 4 kişinin doğru tekrarları) | 0,666 | 0,683 | 0,649 |
| **Kişiye özel açı bandı** | **0,947** | **0,968** | **0,829** |

**Hangi omuz ölçüsü?** Literatürden üç ölçü ile kendi önerimiz (kulak–omuz) aynı veride karşılaştırıldı (bütün görüşler, silkme / doğru) [`deney1/ozet.csv`]:

| Ölçü | Ham | Genel bant | Kişiye özel bant |
| --- | --- | --- | --- |
| Kulak–omuz dikey mesafesi (bizim önerimiz) | 0,704 | 0,666 | 0,947 |
| Sağ omzun iki omuz ortasına göre yüksekliği (Cóias ve ark. 2022'den uyarlama) | 0,638 | 0,709 | 0,924 |
| Sol omuz – sağ omuz – sağ kalça açısı (Jánošová ve ark. 2026, F2) | 0,600 | 0,663 | 0,909 |
| İki omzun ortalama kalkışı (Pavlikov ve ark. 2026) | 0,650 | 0,700 | 0,858 |

- **En büyük kazanç ölçünün seçiminden değil, kişiye özel banttan geliyor.** Bütün ölçüler kişiye özel bantla 0,86–0,95'e çıkıyor; genel bantla 0,66–0,71'de kalıyor.
- Kulak–omuz en yüksek çıkan ölçü, ama ölçüler arasındaki farklar küçük. Yalnızca 5 kişiyle bir ölçünün diğerlerinden üstün olduğunu iddia etmiyoruz. Kulak–omuz, en yüksek çıktığı ve iki omzun birlikte kalkmasını da yakalayabildiği için seçildi.
- Profil görüşte bant da zayıflıyor (kulak–omuz 0,842) [`deney1/ozet.csv`].
- Kişi başına bakıldığında kişiye özel bant her kişide 0,84 ile 0,98 arasında [`deney1/ozet.csv`, "kişi özeti"; kişi kişi değerler `deney1/kisi_auc.csv`].

## Soru 2 (Problem 1): Sistem hatanın türünü doğru söylüyor mu?

**Cevap: kısmen.** Önden + çapraz görüşte hatalı tekrarların yarısından biraz fazlasında ilk söylenen hata doğru; üçte ikisinde doğru hata cümlede geçiyor. Doğru tekrarların çoğuna "doğru" deniyor. Beş hata türü arasında rastgele tahmin %20 tutturur; sonuç bunun çok üstünde, ama kusursuz değil.

**Nasıl karar veriliyor** (`deneyler/deney2.py`, kural `cekirdek/hata_turu.py`):

1. Her hata türünün bir ölçüsü var: omuz silkmesi → kulak–omuz, baş eğme → baş eğikliği, kolun öne kaçması → iki adaydan eğitimde seçilen, dirsek bükme → dirsek açısı. Bunlar kişiye özel açı bandıyla puanlanır. Bant yönlüdür: yalnızca hatanın yönündeki taşma sayılır. Yetersiz kaldırmanın puanı, kolun en yüksek açısının kalibrasyondaki tepe açılarının ortancasından ne kadar eksik kaldığıdır.
2. Puanlar ortak bir ölçeğe çevrilir: z = (puan − doğru tekrarlardaki ortanca) / (doğru tekrarlardaki yayılım).
3. En büyük z, eşik T'den küçükse "doğru"; değilse en büyük z'yi veren hata söylenir.
4. T, yönler ve öne kaçma ölçüsü 4 kişide seçilir, 5. kişide sınanır (her kişi için tekrarlanır).

Cümleye çevirme kayıpsız: cümlenin söylediği hata, karar kuralının bulduğu hatayla her tekrarda aynı. Bu yüzden "hata türü doğruluğu" ile "cümle doğruluğu" aynı sayı [`deney2/ozet.csv`, `deney3/ozet.csv`]:

| Ölçü (önden + çapraz; 682 hatalı, 681 doğru tekrar) | Değer |
| --- | --- |
| Hatalılarda ilk söylenen hata = gerçek hata | 56,6 / 100 |
| Hatalılarda gerçek hata söylenen iki hatadan biri | 67,4 / 100 |
| Hatalılara yanlışlıkla "doğru tekrar" dendi | 15,5 / 100 |
| Doğrulara gereksiz uyarı verildi | 7,5 / 100 |
| Altı sınıf için makro-F1 (doğru + 5 hata) | 0,631 |
| Bütün görüşlerde ilk söylenen hata doğru | 49,3 / 100 |
| Profil görüşte ilk söylenen hata doğru | 16,4 / 100 |

- **En çok karışan çiftler:** kolun öne kaçması ile dirsek bükme (ikisinde de kol kamerada kısa görünüyor) ve baş eğme ile omuz silkmesi (ikisinde de kulak ile omuz arası kısalıyor).
- Örnek cümleler: `sonuclar/deney3/ornek_cumleler.md`.
- Hasta cümlesinde sayı: kolun öne kaçması cümlelerinin hiçbirinde sayı yok (189'da 0), omuz cümlelerinin %66,7'sinde, diğer hatalarda %95–100'ünde var; uzman ayrıntısının hepsinde sayı var [`deney3/metin.csv`]. Nedeni cümle kuralında: hasta cümlesinde yüzde kullanılmıyor, yalnızca 5°'ye yuvarlanmış derece veriliyor; öne kaçma cümlesi hiç sayı içermiyor, omuz cümlesine derece yalnızca omuz çizgisinin eğimi yeterince değiştiyse giriyor (`cekirdek/geribildirim.py`, `hasta_cumlesi`).

## Soru 3: Hiç görmediği bir kişide, ev ortamında çalışıyor mu?

**Cevap: bir işaret var (tek kişi).** Kendi çektiğimiz videoda: 6 kalibrasyon tekrarı ve sırası önceden belirlenmiş 21 test tekrarı. Eşiklerin hiçbiri bu videoya bakılarak değiştirilmedi [`kendi_kayit/kisi1/ozet.csv`]:

| Ölçü | Kaçta kaç |
| --- | --- |
| Tekrar otomatik ayrıldı | 21/21 |
| Hatalılarda ilk söylenen hata doğru | 9/11 |
| Hatalılarda doğru hata cümlede geçti | 11/11 |
| Omuz silkmesi bulundu (ilk sırada) | 3/3 |
| Normal doğru tekrarda gereksiz uyarı | 0/5 |
| Başka yere bakarak yapılan doğru tekrarda gereksiz uyarı | 3/3 |
| Hızlı yapılan doğru tekrarda gereksiz uyarı | 2/2 |

- Kaçırılan iki tekrarın ikisi de öne kaçma–dirsek karışmasından; bu, veri setindeki karışmayla tutarlı.
- Kullanım talimatı buradan çıktı: kalibrasyonda ve değerlendirmede **aynı yere bak, doğal hızda yap**.
- Tek kişi, tek oturum, değerlendiren aynı zamanda geliştirici: güven aralığı verilmez, yalnızca "kaçta kaç" olarak söylenir.

## Altyapı kontrolleri

| Kontrol | Sonuç | Kaynak |
| --- | --- | --- |
| Otomatik tekrar ayırma, veri setinin etiketli tekrarlarına karşı (önden + çapraz) | 1363 tekrarın 1295'i bulundu (95,0/100); sınır örtüşmesi medyan 0,85; 34 fazladan tekrar. Profil görüşte 53,1/100 | [`tekrar_ayirma/ozet.csv`] |
| Uygulamanın MediaPipe sürümü (1.2.2) ile veri setininki (0.10.20) arasındaki fark | Aynı karelerde kol açısı farkı medyan 0,92°, %95'i 3,09° altında | [`uygulama_saglik/ex1_Honza_cam1_o0_poz_farki.csv`] |
| Uygulamanın kural dosyası deneydekiyle aynı yöntemle mi kuruldu? | Evet; aynı prosedür 5 kişinin hepsiyle. Uygulamanın eşiği T = 3,80, deneydeki beş "4 kişilik" ayarın aralığında (3,68–5,00) | [`kural_disa_aktar/loso_karsilastirma.csv`], `modeller/kural_ex1.json` |

## Denenip işe yaramayanlar

Kodları ve sonuçları `arsiv/` altında ([`../arsiv/README.md`](../arsiv/README.md)); kaynak yolları `arsiv/sonuclar/` altına göre. İlk ikisi ödevin Problem 2 için önerdiği yöntemlerdi.

| Deneme | Sonuç | Kaynak |
| --- | --- | --- |
| **Zamansal yumuşatma** (One Euro, Savitzky–Golay; ödevde önerilen) | MediaPipe titremesi %38–87 azaldı, ama silkme tespiti değişmedi: AUC 0,947 → 0,943 ve 0,947. Kullanılmadı. | `deney1c/ozet.csv`, `deney1c/titreme.csv` |
| **Görüntüden omuz silueti** (omuz bölgesinde segmentasyon maskesi; ödevdeki "pose + lokal görüntü" önerisi) | Önden çekimde silkmeyi ayırıyor (0,94), çapraz çekimde arama bölgesi başın üstüne düşüyor (0,55). Toplamda 0,72; kulak–omuz ölçüsü aynı tekrarlarda 0,97. | `siluet/ozet.csv` |
| **Zaman bandı** (literatürdeki yöntem: tekrarlar DTW ile zamanda hizalanır, bant zamana göre kurulur). Açı bandından önce bunu kullandık. | Kulak–omuz silkme / doğru 0,909 (açı bandında 0,947); asıl fark silkmeyi diğer hatalardan ayırmada: 0,705 (açı bandında 0,829). Kol az kaldırılınca omuz yanlış kol açısıyla karşılaştırılıyordu. Açı bandına geçildi. | `sonuclar/deney1_v2/ozet.csv` (`v1` ve `v2` satırları, `YENI`); dosya `ecd69a9` commit'inde, Deney 1 sadeleştirilince depodan çıkarıldı |
| Deney 2'de zaman bandı ve yönsüz bant | Hata türü kararında açı bandı (yönlü) ile fark anlamlı değil: önden + çapraz makro-F1 farkı zaman bandına göre +0,004 (%95 GA −0,027 – +0,019), yönsüz banda göre +0,004 (%95 GA −0,032 – +0,043). Uygulamanın yöntemi (açı bandı, yönlü) kaldı. | `sonuclar/deney2/bootstrap.csv` (`a18101a` commit'inde; Deney 2 sadeleştirilince depodan çıkarıldı) |
| Yetersiz kaldırma puanının "revize" hâli | Hata türü doğruluğunu düşürdü (makro-F1 0,631 → 0,568); ilk hâline dönüldü. | `deney2_revize/ozet.csv` |
| Cümleyi bir LLM'e yazdırmak (Gemini, ücretsiz katman; 150 tekrar) | Karar kuraldan gelip LLM yalnızca cümleyi yazınca sonuç kural cümlesiyle aynı düzeyde (ilk söylenen doğru 61'e 61), üstünlük yok. Hatayı da LLM'e buldurunca 61'den 45'e düştü. Ürün kural tabanlı kaldı. | `deney4/ozet.csv` |
| Aynı sistemi başka bir harekette denemek (omuz ekstansiyonu, Ex7) | Silkme tespiti taşınıyor (AUC 0,89–0,94), ama hata türü zayıf (makro-F1 0,40). Ödevin kapsamı dışında. | `ex7/ozet.csv` |

## Sınırlılıklar

1. **Veri:** 5 sağlıklı kişi; hatalar taklit, gerçek hasta yok.
2. **Dar bant:** τ, ortalamanın güven aralığıdır, yeni bir tekrarın düşebileceği aralık değil. 6 tekrarla bant, yeni tekrar için gereken aralıktan yaklaşık 2,6 kat dar; küçük sapmalar da uyarıya dönüşebiliyor.
3. **Tek kamera, 2B:** derinlik yok; dereceler yaklaşık. Öne kaçma ile dirsek, baş eğme ile omuz silkmesi karışabiliyor. Profil görüş uygun değil.
4. **Kalibrasyon şart:** kişi her kurulumda 6 doğru tekrar yapmalı ve kamera aynı yerde durmalı.
5. **Bakış ve hız:** başka yere bakmak ya da çok hızlı yapmak gereksiz uyarı üretebiliyor (kendi kayıt).

## Sonuçları yorumlarken dikkat

- Kulak–omuz ölçüsünün diğer omuz ölçülerinden üstün olduğu iddia edilmiyor: en yüksek çıkıyor, ama farklar küçük ve yalnızca 5 kişi var (Soru 1).
- Deney 3'teki "çıkarıcı uyumu", cümleyi kendi şablonlarıyla geri okuyan bir kontroldür, doğruluk ölçüsü değildir. Cümlenin doğruluğu Soru 2'deki 56,6 / 67,4'tür.
- Sistem yalnızca kolu yana kaldırma hareketinde ölçüldü.
