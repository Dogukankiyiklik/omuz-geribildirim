# Güncelleme 05 — 6 Kasım 2026 gece (danışmandan)

Claude Code: `/clear` sonrası yeni oturum. Sırayla oku:
1. `CLAUDE.md`
2. `PLAN.md`
3. `ilerleme/KARARLAR.md`
4. `ilerleme/ADIM_04.md`
5. bu dosya

Kararları `KARARLAR.md`'ye işle, `PLAN.md`'yi aşağıdaki "Yeni sıra"ya göre güncelle, sonra sırayla ilerle.

Adım 4 çok iyiydi. Kullanıcının galeri gözlemi ("kol 180°'ye kalkıyor ama az kaldırma diyor") ile incelemen birleşince iki ayrı sorun net ortaya çıktı: etiketin yalnızca birincil olması ve 2B izdüşümü.

---

## Kararlar

### Karar 13 — "Az kaldırma" puanı diğer ölçütlerle aynı biçime getirilir (revizyon)
**Sorun bir tasarım hatası, ayar sorunu değil.** Duruş ölçütlerinin E'si 0–1 aralığında sınırlı, kaldırmanın d'si ise sınırsız. Ayrıca d'nin ölçeği kişinin tepe tutarlılığına (IQR ≈ birkaç derece) bağlı, bu yüzden fizyolojik olarak önemsiz eksiklikler büyük z'ye dönüşüyor. İki farklı birimdeki puanların argmax ile yarıştırılması bu yüzden adil değil.

**Yeni tanım** (`cekirdek/hata_turu.py`). Tepe açısı için tek kutulu bir "bant" kurulur:
- μ_k = kalibrasyon tepelerinin ortalaması.
- τ_k = max( t(0,975; n−1) · s / √n , **10°** ).
- eksik = μ_k − tekrarın tepesi.
- E_kaldirma = 0, eğer eksik ≤ τ_k; değilse min(1, (eksik − τ_k) / τ_k).
- Yönlü versiyonda yalnızca eksik (az kalkma) sayılır; yönsüzde |fark|.
- Sonra diğer ölçütlerle **aynı** z ölçeklemesi ve aynı karar kuralı uygulanır.

**10° alt sınırının gerekçesi** (sonuçlardan bağımsız, literatürden):
- MediaPipe ile gonyometre arasındaki uyum sınırları yaklaşık ±7° (M20).
- Tek kameralı omuz açılarında uç noktada 15°'ye varan hata bildirilmiş (M41, M42).
- 10°'nin altındaki bir eksiklik ölçüm belirsizliğinin içinde kalıyor; kişiye "kolunu kaldır" demek için yeterli kanıt değil.

**Dürüstlük:** Bu değişiklik Adım 4 sonuçları görüldükten sonra yapılıyor. Bu yüzden:
- mevcut sonuçlar `sonuclar/deney2_ilk/` altına kopyalanır ve raporda "ilk sürüm" olarak **korunur**;
- yeni sonuçlar `sonuclar/deney2/` altına "revize" olarak yazılır;
- eşik T ve diğer seçimler yine kişi bazlı birini-dışarıda-bırak ile yapılır;
- 10° değeri **değiştirilmez**, kötü sonuç çıksa bile;
- doğrulama: Ex7 (Adım 4b, ayarsız) ve kendi kayıtlarımız (Adım 7).

### Karar 14 — İlk iki tahmin metriği eklenir
Adım 5'te geri bildirim en fazla 2 hata söyleyecek (PLAN). Bu yüzden Deney 2 revizesine şu metrik eklenir:
- **"Gerçek birincil hata, en yüksek iki z içinde mi?"** Hatalı tekrarlarda, /100 biçiminde.
- Yanında ikinci z'nin de eşiği geçme oranı verilir; kural 2. hatayı ancak o da T'yi geçerse söyler.

Bu, "omuz → az kaldırma" gibi gerçekten iki hata içeren tekrarları (Petra: kol da 108°'de kalıyor) daha adil ölçer. Raporda **etiket sınırlılığı** olarak açıklanır: veri seti yalnızca birincil hatayı etiketliyor; silkmeli tekrarların bir kısmında kol da belirgin az kalkıyor (eksik medyanı 41,7°).

### Karar 15 — Ana sistem: v2 yönlü
- Sonuçlardan önce seçilmişti; değişmiyor.
- Geri bildirim uygulamasında gereksiz uyarının az olması tercih edilir (doğru tekrarlarda "doğru" deme oranı 0,925).
- Yönsüz ve v1b karşılaştırma olarak raporlanmaya devam eder.

### Karar 16 — `aralik_disi` bayrağı karar kuralına eklenmez
- Betimsel olarak raporlanır.
- "Öne kaçma, 2B'de kolu kısa ve alçak gösteriyor" bulgusu bir **sınırlılık** ve gelecek çalışma olarak yazılır (örnek öneri: kol açısı ile kol boyunu birlikte kullanan bir kural).
- Yeni bir kural eklenmez; sonuç gördükten sonra kural eklemek aşırı uyum riski taşır.

---

## Yeni sıra (PLAN.md'ye işle)

| Sıra | İş | Hedef | Not |
| --- | --- | --- | --- |
| 1 | **Deney 2 revize** (Karar 13–14) | 7 Kas | Kısa. ADIM_04'ün sonuna "Ek: Güncelleme 05" olarak yaz |
| 2 | **Adım 4b — Ex7'de ayarsız doğrulama** | 7 Kas | Deney 1 (silkme/doğru AUC; v1b ve v2) + Deney 2 kuralı Ex7 hata türleriyle. **Hiçbir sabit değiştirilmez.** Ex7'nin ölçüt–hata eşlemesi önceden yazılır (aşağıda) |
| 3 | Adım 5 — Türkçe geri bildirim (Deney 3) | 7–8 Kas | İlk iki metriği (Karar 14) Deney 3'te de raporla |
| 4 | Adım 6 — Uygulama | 8–10 Kas | **Zorunlu, öncelikli** |
| 5 | Adım 7 — Kendi kayıtlar | 10–11 Kas | Kullanıcı çeker |
| 6 | Adım 8 — LLM karşılaştırması (Gemini ücretsiz / Ollama) | 11 Kas | Süre sınırı 1 gün |
| 7 | Adım 6b — Omuz siluet ölçütü | 11–12 Kas | Süre sınırı 1 gün; MediaPipe segmentasyonu arka planda saatler sürebilir, önce süre tahmini ver |
| 8 | Adım 10 — REHAB24-6 ile 10 yeni kişi | 12–13 Kas | Kullanıcı birkaç saat etiketleme yapacak; önce veri biçimini kontrol et, iş büyükse dur ve sor |
| 9 | Adım 9 — Sonuçları dondurma | **13 Kas akşamı** | Bu saate kadar bitmeyen isteğe bağlı iş bırakılır |

**Kural:** İsteğe bağlı adımlar (6, 7, 8) zorunlu adımları (4, 5) asla geciktiremez. Uygulama ve kendi kayıtlar bitmeden isteğe bağlılara geçilmez.

### Ex7 için ölçüt–hata eşlemesi (önceden belirlenmiştir)
| Ex7 hata kodu | ölçüt |
| --- | --- |
| `ERR_ELEVATED_SHOULDER` | YENI (aynı) |
| `ERR_BENT_ARM` | `dirsek` (aynı) |
| `ERR_TORSO_FORWARD` | gövde öne eğimi: (kalça ortası → omuz ortası) vektörünün dikeyle açısı |
| `ERR_TORSO_ROTATION` | omuz genişliği / kalça genişliği oranı (dönme 2B'de omuz çizgisini kısaltır) |
| `ERR_ARM_TO_SIDE` | `kol_boyu` (Ex1'deki öne kaçmanın simetriği; kol yana kaçınca yandan görüşte kısalır) |

- Ex7'de "az kaldırma" sınıfı yoktur; Ex7'nin kendi 5 hatası kullanılır.
- Kol açısı tanımı aynıdır.
- Yeni ölçütler (gövde eğimi, gövde dönmesi) açı bandıyla değerlendirilir.
- Eşik T ve ölçekleme Ex7'nin içinde yine kişi bazlı birini-dışarıda-bırak ile seçilir. Bu, yöntemin aynısının yeni bir harekette çalışıp çalışmadığını gösterir. **Ex1'de bulunan hiçbir sabit değiştirilmez:** 5° kutu, en az 3 tekrar, %20 bayrağı, 10° alt sınır.
- Ex7'de yana ve geriye kaldırma farklı görüşlerde görülür. Sonuçlar görüş gruplarına göre verilir; hangi grubun "uygulama senaryosu" olduğunu **önceden** yaz: Ex7 için yan veya çapraz (|görüş| ≥ 30°) önerilir, çünkü ekstansiyon sagital düzlemdedir.
