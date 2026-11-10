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

**Cevap: evet, belirgin biçimde.** Ham ölçü (sabit kural) silkmeyi zayıf ayırıyor. Kişinin kendi doğru tekrarlarından kurulan açı bandıyla AUC 0,70'ten 0,95'e çıkıyor. Başkalarının tekrarlarından kurulan "genel" bant işe yaramıyor; yani kalibrasyon kişiye özel olmalı.

Kulak–omuz ölçüsü (`YENI`), silkmeli tekrar ile doğru tekrar [`deney1b/ozet.csv`]:

| Değerlendirme | Bütün görüşler | Önden + çapraz | Silkme / diğer hatalar |
| --- | --- | --- | --- |
| Bant yok (ham ölçü) | 0,704 | 0,761 | 0,699 |
| Genel bant: diğer 4 kişinin bütün doğru tekrarları | 0,666 | 0,683 | 0,649 |
| Genel bant: başka tek bir kişinin kalibrasyonu | 0,618 | 0,634 | 0,603 |
| **Kişiye özel açı bandı** | **0,947** | **0,968** | **0,829** |

**Hangi omuz ölçüsü?** Literatürden dört ölçü ile kendi önerimiz (kulak–omuz) aynı veride karşılaştırıldı (bütün görüşler) [`deney1b/ozet.csv`]:

| Ölçü | Ham | Kişiye özel bant |
| --- | --- | --- |
| Kulak–omuz dikey mesafesi (bizim önerimiz) | 0,704 | 0,947 |
| Sağ omzun iki omuz ortasına göre yüksekliği (Cóias ve ark. 2022'den uyarlama) | 0,638 | 0,924 |
| Sol omuz – sağ omuz – sağ kalça açısı (Jánošová ve ark. 2026, F2) | 0,600 | 0,909 |
| Yalnızca sağ omzun kalkışı (Pavlikov ve ark. 2026'nın tek omuz hâli) | 0,658 | 0,889 |
| İki omzun ortalama kalkışı (Pavlikov ve ark. 2026) | 0,650 | 0,858 |

- **En büyük kazanç ölçünün seçiminden değil, kişiye özel banttan geliyor.** Bütün ölçüler bantla 0,86–0,95'e çıkıyor.
- Kulak–omuz en yüksek çıkıyor, ama farkı küçük. İlk sürüm bantta yapılan kişi bazlı bootstrap'te kulak–omuz ile F2 açısı arasındaki fark anlamlı değildi: +0,021, %95 GA −0,017 – +0,060 [`deney1/bootstrap.csv`]. Son sürümde ölçüler arası bu sınama ayrıca yapılmadı. Sunumda "en iyi ölçü bu" deme; "en yüksek çıkan ve iki omzun birlikte kalkmasını da yakalayabilen ölçüyü seçtik" de.
- İki omzun ortalaması en kötüsü: tek taraflı silkmeyi yarı yarıya seyreltiyor.
- Profil görüşte bant da zayıflıyor (kulak–omuz 0,842) [`deney1b/ozet.csv`].

Şekil: `sonuclar/sunum/1_problem.png` (ham → bant, kişi başına nokta) ve `2_fikir_aci_bandi.png` (bir doğru ve bir silkmeli tekrar bandla birlikte).

## Soru 2 (Problem 1): Sistem hatanın türünü doğru söylüyor mu?

**Cevap: kısmen.** Önden + çapraz görüşte hatalı tekrarların yarısından biraz fazlasında ilk söylenen hata doğru; üçte ikisinde doğru hata cümlede geçiyor. Doğru tekrarların çoğuna "doğru" deniyor. Beş hata türü arasında rastgele tahmin %20 tutturur; sonuç bunun çok üstünde, ama kusursuz değil.

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
- Örnek cümleler: `sonuclar/deney3/ornek_cumleler_saglam.md`.

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

Kodları ve sonuçları `arsiv/` altında ([`../arsiv/README.md`](../arsiv/README.md)). Sunumda birer cümleyle anılır; özellikle ilk ikisi hocanın Problem 2 için önerdiği yöntemlerdi.

| Deneme | Sonuç |
| --- | --- |
| **Zamansal yumuşatma** (One Euro, Savitzky–Golay; hocanın önerisi) | MediaPipe titremesi %38–87 azaldı, ama silkme tespiti değişmedi: AUC 0,947 → 0,943 ve 0,947. Kullanılmadı. |
| **Görüntüden omuz silueti** (omuz bölgesinde segmentasyon maskesi; hocanın "pose + lokal görüntü" önerisi) | Önden çekimde silkmeyi ayırıyor (0,94), çapraz çekimde arama bölgesi başın üstüne düşüyor (0,55). Toplamda 0,72; kulak–omuz ölçüsü aynı tekrarlarda 0,97. |
| Yetersiz kaldırma puanının "revize" hâli | Hata türü doğruluğunu düşürdü (makro-F1 0,631 → 0,568); ilk hâline dönüldü. |
| Cümleyi bir LLM'e yazdırmak (Gemini, ücretsiz katman; 150 tekrar) | Karar kuraldan gelip LLM yalnızca cümleyi yazınca sonuç kural cümlesiyle aynı düzeyde (ilk söylenen doğru 61'e 61), üstünlük yok. Hatayı da LLM'e buldurunca 61'den 45'e düştü. Ürün kural tabanlı kaldı. |
| Aynı sistemi başka bir harekette denemek (omuz ekstansiyonu, Ex7) | Silkme tespiti taşınıyor (AUC 0,89–0,94), ama hata türü zayıf (makro-F1 0,40). Ödevin kapsamı dışında. |

## Sınırlılıklar (raporda en önemli üçü seçilir)

1. **Veri:** 5 sağlıklı kişi; hatalar taklit, gerçek hasta yok.
2. **Dar bant:** τ, ortalamanın güven aralığıdır, yeni bir tekrarın düşebileceği aralık değil. 6 tekrarla bant, yeni tekrar için gereken aralıktan yaklaşık 2,6 kat dar; küçük sapmalar da uyarıya dönüşebiliyor.
3. **Tek kamera, 2B:** derinlik yok; dereceler yaklaşık. Öne kaçma ile dirsek, baş eğme ile omuz silkmesi karışabiliyor. Profil görüş uygun değil.
4. **Kalibrasyon şart:** kişi her kurulumda 6 doğru tekrar yapmalı ve kamera aynı yerde durmalı.
5. **Bakış ve hız:** başka yere bakmak ya da çok hızlı yapmak gereksiz uyarı üretebiliyor (kendi kayıt).

## Sunumda söylenmemesi gerekenler

- "Kulak–omuz ölçüsü en iyisi": fark anlamlı değil (yukarıya bak).
- "Cümleler %100 doğru": eski belgelerdeki "çıkarıcı uyumu 100/100", cümleyi kendi şablonlarıyla geri okuyan bir kontroldü, doğruluk ölçüsü değil. Cümlenin doğruluğu Soru 2'deki 56,6 / 67,4.
- "Sistem her harekette çalışır": yalnızca kolu yana kaldırmada ölçüldü.
