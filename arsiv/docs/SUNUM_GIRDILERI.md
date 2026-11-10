# Sunum girdileri (Karar 56)

Sunumun kendisi değil; sunumda kullanılabilecek sayıların listesi. Her satır: bir cümle + kaynak dosya (`sonuclar/` altına göre). Sayılar kaynak dosyalardan kopyalandı; ayrıntı ve tablolar [`sonuclar/OZET.md`](../sonuclar/OZET.md). "ö+ç" = önden + çapraz görüş (|görüş| ≤ 60°, uygulama senaryosu).

## Tek cümleler (danışmanın kararları)
- **Karar 51 (kendi videomuz):** "Kendi videomda 11 hatalı tekrarın 11'inde doğru hata cümlede geçti, 9'unda ilk söylenen oydu; 5 normal doğru tekrarın hiçbirinde uyarı çıkmadı." [`kendi_kayit/kisi1/ozet.csv`]
- **Karar 47 (LLM; Karar 41'in güncellenmiş hali):** "LLM'i hatayı bulmak için değil, en fazla cümle yazmak için kullanmak mantıklı. Ama o zaman da kurala bir üstünlüğü yok ve yasakladığımız ifadeleri kullanabiliyor." [`deney4/ozet.csv`, `deney4/kaldirma_ozet.csv`]
- **Karar 41 (model notu, rapor için):** "Ücretsiz katmanın günlük sınırı nedeniyle gemini-3.5-flash-lite; düşünme ayarı varsayılan." [`deney4/bilgi.json`]
- **Karar 52 (siluet):** "Görüntüden omuz silueti denendi; bu tanımla anahtar noktalardan daha iyi değil: önden çekimde silkmeyi ayırıyor (AUC 0,94), çapraz çekimde arama bölgesi başın üstüne düşüyor (0,55)." [`siluet/ozet.csv`]

## P1 — Hareket doğruluğu ve doğal dil geri bildirimi
| Sayı | Cümle | Kaynak |
| --- | --- | --- |
| 56,6 / 100 | ö+ç hatalı tekrarlarda cümlenin ilk söylediği hata gerçek hata (katı; GA 42,3–70,4). | `deney3/ozet.csv`, `deney3/bootstrap.csv` |
| 67,4 / 100 | ö+ç hatalı tekrarlarda gerçek hata cümlede söylenen ilk iki hata içinde (GA 50,6–80,1). | `deney3/ozet.csv`, `deney3/bootstrap.csv` |
| 7,5 / 100 | ö+ç doğru tekrarlarda gereksiz uyarı (GA 3,9–10,4); geri kalanında somut olumlu cümle. | `deney3/ozet.csv`, `deney3/bootstrap.csv` |
| 0,631 | Hata türü (6 sınıf: doğru + 5 hata) makro-F1, ö+ç; tüm görüşlerde 0,581, profilde 0,296. | `deney2/ozet.csv` |
| 1,6 / 100 | İkinci hatayı da söylemenin bedeli: doğru tekrarlarda iki uyarı oranı (ö+ç). | `deney2/ilk_iki.csv` |
| 100 / 100 | Cümleden geri okunan hata listesi kararla aynı (cümleye çevirme kayıpsız). | `deney3/ozet.csv` |
| 61 / 61 / 45 | Katı doğru hata (/100): kural (A), LLM yalnızca cümle (B), LLM hatayı da buluyor (C). C − A −16 (GA −26 – −5). | `deney4/ozet.csv`, `deney4/bootstrap.csv` |
| 8 / 8 / 16 | Doğru tekrarda gereksiz uyarı (/100), insan düzeltmeli, A / B / C. C − A +8 (GA 2 – 14). | `deney4/kaldirma_ozet.csv`, `deney4/kaldirma_bootstrap.csv` |
| 94 / 87,33 / 11,33 | Fiziksel büyüklük (sayı) içeren cümle (/100), A / B / C: hatayı LLM'e buldurunca ölçü kayboluyor. | `deney4/ozet.csv` |
| 11,33 / 100 | B'de yasakladığımız ifadeler (%, yüzde, gövde boyu) geçen cümle; A'da 0. | `deney4/ozet.csv` |
| 0,67 / 100 | "LLM sayı uydurur" beklentisi tutmadı: B'de 1/150, C'de 0. | `deney4/ozet.csv` |
| 9/11 · 11/11 · 0/11 | Kendi videomuz, hatalı tekrarlar: katı · ilk iki · olumlu cümle (yanlışlıkla "doğru" deme). | `kendi_kayit/kisi1/ozet.csv` |
| 0/5 · 3/3 · 2/2 | Kendi videomuz, doğru tekrarlarda gereksiz uyarı: normal · başka yere bakış · hızlı. | `kendi_kayit/kisi1/ozet.csv` |
| 2/2 | Hızlı tekrarlarda "Hareketi biraz daha yavaş yap." notu çıktı (normal doğrularda 0/5). | `kendi_kayit/kisi1/ozet.csv` |

Örnek cümleler (kendi videomuz, `kendi_kayit/kisi1/tekrarlar.csv`):
- Tekrar 7 (omuz): "Kolunu kaldırırken sağ omzunu kulağına doğru yaklaşık 5 derece kaldırdın. Omzunu aşağıda ve gevşek tut."
- Tekrar 6 (az kaldırma): "Kolunu 105 dereceye kadar kaldırdın; normalde 140 dereceye çıkıyorsun. Kolunu yaklaşık 35 derece daha yukarı kaldır. …"
- Tekrar 4 (doğru): "Hareketi doğru yaptın. Kolun yaklaşık 140 dereceye çıktı, omzun ve dirseğin yerindeydi."

## P2 — Omuz/skapula hareketlerinin hassas ölçümü
| Sayı | Cümle | Kaynak |
| --- | --- | --- |
| 0,704 → 0,947 | Omuz silkmesini doğru tekrardan ayırma (AUC): ham kulak–omuz ölçüsü → kişiye özel açı bandı (tüm görüşler). Standart pose çıktısının sınırı ve iyileştirme. | `deney1b/ozet.csv` |
| 0,761 → 0,968 | Aynısı, ö+ç. | `deney1b/ozet.csv` |
| 0,666 / 0,618 | Genel bant (başkalarının tekrarlarından) AUC: kalibrasyon kişiye özel olmalı. Genel − kişiye özel −0,280 (GA −0,406 – −0,141). | `deney1b/ozet.csv`, `deney1b/bootstrap.csv` |
| +0,108 | Açı bandının asıl kazancı: silkmeyi diğer hatalardan ayırma, v2 − v1b (GA +0,053 – +0,190); 0,721 → 0,829. | `deney1_v2/bootstrap.csv`, `deney1_v2/ozet.csv` |
| 0,95 (0,84–0,98) | Kişi bazlı AUC ortalaması (en düşük–en yüksek kişi), v2 YENI. | `deney1_v2/ozet.csv` |
| 0,888 – 0,939 | Ex7'de (omuz ekstansiyonu), hiçbir sabit değiştirilmeden silkme AUC'si (v2 / v1b, çapraz + profil). | `ex7/d1_auc.csv` |
| %38–87 | Zamansal yumuşatma titremeyi azaltıyor, ama AUC değişmiyor (0,947 → 0,943 / 0,947): denendi, etkisiz. | `deney1c/titreme.csv`, `deney1c/ozet.csv` |
| 0,716 vs 0,969 | Siluet (görüntüden omuz çizgisi) ile anahtar nokta ölçütü, aynı 1363 tekrar; önden 0,938, çapraz 0,549. | `siluet/ozet.csv` |
| 0,968 / 0,969 | Aynı ölçüt, MediaPipe 0.10.20 ve 1.2.2 noktalarıyla: sürüm farkı pratikte etkisiz. | `siluet/ozet.csv` |

Yorumlanabilir ölçüm (hocanın şartı): "kol 90°'deyken bu kişinin omzu normalde nerede?" (`sunum/2_fikir_aci_bandi.png`); cümlelerde omuz için derece, kol için derece.

## P3 — Referans ve kullanıcı hareketini çakıştırma
| Sayı / öğe | Cümle | Kaynak |
| --- | --- | --- |
| DTW + öteleme, ölçek, döndürme | Kalibrasyondaki referans tekrar, kullanıcının tekrarına zamanda (DTW, kol açısına göre) ve geometride hizalanıp yarı saydam turkuaz olarak bindirilir; banttan çıkan uzuv kırmızı. | `sunum/5_bindirme.png`, `sunum/5b_bindirme.png` (kişi 1, yerelde), `cekirdek/bindirme.py` |
| 95,01 / 100 | Uygulamanın otomatik tekrar ayırıcısı ö+ç tekrarların 95,01'ini buluyor, IoU medyan 0,85 (tüm görüşler 87,35, profil 53,11). | `tekrar_ayirma/ozet.csv` |
| 21/21 | Kendi videomuzda bütün tekrarlar ayrıldı (hızlı tekrarlar dahil). | `kendi_kayit/kisi1/ozet.csv` |
| ±4 kare | Veri setinde video ile iskelet kare kare hizalı (bindirmenin ön koşulu). | `adim2b/senkron.csv` (KARARLAR, 6 Kas) |

## Sınırlılıklar (sunumda bir slayt)
- 5 sağlıklı kişi, taklit hatalar; kendi videomuz tek kişi ve kişi geliştirici.
- Profil görüş uygun değil (makro-F1 0,296) → kullanım talimatı: kameraya önden ya da en fazla çapraz dur.
- Karışmalar: öne kaçma ↔ dirsek; baş eğme → omuz.
- Bakış ve hız: başka yere bakmak ve hızlı tekrar gereksiz uyarı üretebilir → kalibrasyonda ve değerlendirmede aynı yere bak, doğal hızda yap.

## Şekiller ve videolar (`sonuclar/sunum/`)
| Dosya | Ne | Git |
| --- | --- | --- |
| `1_problem.png` | Ham 0,70 → bant 0,95 | var |
| `2_fikir_aci_bandi.png` | Açı bandı fikri | var |
| `3_kalibrasyon.png` | Genel bant ile kişiye özel bant | var |
| `4_geri_bildirim.png`, `5_bindirme.png` | Uygulama ekranı ve bindirme, veri seti (Honza, tekrar 5) | var |
| `4b_geri_bildirim.png`, `5b_bindirme.png` | Aynısı, kişi 1 tekrar 7 (omuz) | **yok** (kişisel görüntü) |
| `demo_yedek_veriseti.mp4` | 25 s, veri seti demosu | yok |
| `demo_kisi1.mp4` | 45 s, kişi 1: tekrar 4, 7, 11, 6 ve oynatımları | yok (kişisel görüntü) |
