# Güncelleme 11 — 7 Kasım 2026 akşam (danışmandan)

Claude Code: `/clear` sonrası yeni oturum. Sırayla oku:
1. `CLAUDE.md`
2. `PLAN.md` (Adım 6b bölümü dahil)
3. `ilerleme/KARARLAR.md`
4. `ilerleme/ADIM_08.md` (Güncelleme 10 ekleri dahil)
5. `ilerleme/ADIM_09.md` (Karar 45, süre tahmini)
6. bu dosya

Kararları (47–50) `KARARLAR.md`'ye işle. `PLAN.md`'deki durum işaretlerini güncelle (6b 🔄) ve Adım 6b'nin altına bu güncellemenin kısa notunu ekle.

**Öncelik değişmedi:** Kullanıcının Adım 7 videoları gelirse her şey bırakılır ve önce Adım 7 yapılır.

## Değerlendirme
- **Karar 42 (duyarlılık analizi):** Temiz yapıldı. İlk etiketlerin ayrı commit'lenmesi ve onlarla elde edilen sonucun da verilmesi doğruydu.
- **Gözden geçirme turu:** Önceden kayıtta yoktu. Ama analizden önce, yalnızca metne bakılarak yapıldı ve kararı kullanıcı verdi. İlk etiketlerle sonuç da raporlandığı ve yorum değişmediği için kabul ediyorum. Raporda tek cümleyle anılır.
- **6b süre tahmini:** İyi yapıldı. Ölçümü yarıda kesip daha kısa bir örneklemle tekrarlamak da doğru bir karardı.

## Kararlar

### Karar 47 — Deney 4'ün son yorumu (Karar 41'in güncellenmesi)
| İddia | Kanıt | Güç |
| --- | --- | --- |
| LLM'e yalnızca cümle yazdırmak (B), kararı korur ama üstünlük getirmez | Katı 61 / 61; insan düzeltmeli ilk iki 73 / 73, gereksiz uyarı 8 / 8 (B − A 0, GA 0–0); B'nin birincil tablodaki fazladan uyarısı tamamen çıkarıcı hatası | **Güçlü** (bu örneklem ve bu model için) |
| Hatayı LLM'e buldurmak (C), daha kötü sonuç verir | Katı −16 (GA −26 – −5), gereksiz uyarı +8 (GA 2–14), eklenen hata +33 (GA 27–39); insan düzeltmesinden sonra da **aynı** | **Orta-güçlü.** Çıkarıcı hatası değil; tek model, tek istem. |
| C fiziksel büyüklüğü çoğunlukla söylemez | Sayı içeren cümle: A 94, B 87, C 11 /100 | Betimsel |
| LLM sayı uydurur | B 1/150, C 0/150 | Tutmadı |
| Çıkarıcı, kural ve C cümlelerinde "az kaldırma"yı insan gibi okur; B'nin serbest anlatımında yanılır | Uyum A 119/119, C 90/91, B 119/132 | Betimsel; tek etiketleyici |
- Sunumdaki tek cümlelik özet: **"LLM'i hatayı bulmak için değil, en fazla cümle yazmak için kullanmak mantıklı. Ama o zaman da kurala bir üstünlüğü yok ve yasakladığımız ifadeleri kullanabiliyor."**

### Karar 48 — 6b (omuz silueti) yapılır; süre sınırlı, önceden kayıtlı
**Gerekçe:** Hocanın P2 önerilerinden biri "genel pose noktalarını lokal görüntü özellikleriyle birleştirmek". Şu ana kadarki bütün ölçütlerimiz pose noktalarından geliyor; siluet, görüntünün kendisinden gelen tek ölçüt olacak. Süre tahmini (~1,3 saat segmentasyon) makul. Olumsuz sonuç da raporlanır.

**Sert süre sınırı:** 10 Kasım akşamına kadar sonuç çıkmazsa durulur ve "denendi, tamamlanmadı" olarak yazılır. Adım 7 her zaman önce gelir.

**Önceden kayıt** (kod yazılmadan önce `ilerleme/ADIM_06b.md`'nin "Önceden belirlenenler" bölümüne yazılır ve commit'lenir):

1. **Kapsam:** Ex1, önden + çapraz görüş (|görüş| ≤ 60°), bütün tekrarlar (1363), tekrar kareleri ±10 pay. Profil dahil edilmez (ana senaryo, Karar 6).

2. **Kaynak:** Her videoda MediaPipe 1.2.2, `pose_landmarker_full`, VIDEO modu, `output_segmentation_masks=True` bir kez çalıştırılır. **Aynı çalıştırmanın** pose noktaları ROI'nin konumu, gövde boyu ve kol açısı için kullanılır; maske ile noktalar aynı karede olsun diye. Veri setinin 0.10.20 noktaları kullanılmaz.

3. **Ölçüt `SILUET`** (piksel koordinatlarında; gerçek piksel olduğu için en-boy düzeltmesi gerekmez):
   - Her karede sağ kulak (8) ve sağ omuz (12) noktaları alınır. İkisinin görünürlüğü ≥ 0,5 değilse kare NaN olur.
   - Yatay aralık: kulağın x'i ile omzun x'i arası. Bu aralığın **ortadaki %50'sinde**, eşit aralıklı **5 sütun** seçilir. Kenarlar baş ve kola fazla yakın olduğu için atılır.
   - Dikey arama: her sütunda, y = (kulak y − 0,10 · gövde) noktasından aşağı, (omuz y + 0,20 · gövde) noktasına kadar inilir. Maske değeri ilk kez > 0,5 olan piksel **siluet sınırı**dır. Bulunamazsa o sütun NaN olur.
   - Kare değeri = (5 sütunun siluet sınırı y'lerinin medyanı − kulak y) / gövde boyu (piksel). En az 3 sütun geçerli olmalı; değilse NaN.
   - Yönü YENI ile aynıdır: omuz silkilince küçülür.
   - Gövde boyu, YENI ile aynı tanımla bu çalıştırmanın noktalarından hesaplanır.

4. **Kolun ROI'ye girmesi:** Kol yukarıdayken silüete karışabilir. Bunun için ayrı bir kural **konmaz**. Açı bandı kol açısına koşullu olduğundan, kişinin kendi doğru tekrarlarında da aynı karışma olur ve bant bunu kişiye özel olarak içerir. Bu varsayım raporda belirtilir.

5. **Değerlendirme (Deney 1 v2 biçimi):**
   - Açı bandı (v2), yönsüz bant (Deney 1 ile aynı), Karar 7 adil modeli, 5° kutu, en az 3 tekrar; bütün sabitler aynı.
   - Karşılaştırılan ölçütler: `SILUET` ve aynı çalıştırmanın noktalarından hesaplanan `YENI_mp122`. İkisi de **aynı tekrarlarda** değerlendirilir. Bilgi için, Deney 1 v2'deki kayıtlı YENI değeri yanına yazılır.
   - Metrikler: AUC silkme/doğru ve silkme/diğer; kişi bazlı AUC; kişi bazlı bootstrap ile `SILUET − YENI_mp122` farkı (2000 tekrar, tohum 1).
   - Ayrıca betimsel: geçerli kare oranı (NaN olmayan) ve açı bandı kapsamı.
   - **Birleşik ölçüt ve ağırlık yok.** İki ölçütü birleştirmek ayar gerektirir; gelecek çalışmaya yazılır.

6. **Görsel:** Görsel kontrol aracında 3 örnek video: aynı kişinin bir doğru ve bir silkmeli tekrarı ile bir yanlış alarm ya da kaçırma. Üzerine ROI, 5 sütun ve siluet sınırı çizilir. Seçim tohumla yapılır (tohum 0).

7. **Raporlama:** Sonuç ne olursa olsun yazılır. `SILUET` YENI'den kötü çıkarsa da bu bir bulgudur: "görüntüden omuz silueti denendi; bu tanımla anahtar noktalardan daha iyi değil". Hiçbir tanım sonuçlara bakılarak değiştirilmez.

8. **Önbellek:** Maskenin tamamı saklanmaz. Her kare için 5 sütunun sınır y'leri, kullanılan noktalar ve görünürlükler `veri/ara/siluet/` altına yazılır. Yalnızca görsel örneklerin tekrarları için ikili, sıkıştırılmış ROI maskesi saklanır.

**İş bölümü:**
- Claude Code önceden kaydı yazar ve commit'ler; sonra kodu yazar. Kodu tek bir videonun ilk ~500 karesinde sınar (yalnızca kodun çalıştığını görmek için; AUC hesaplanmaz).
- Uzun segmentasyon çalıştırmasını (tahmini 1,5–2 saat) **kullanıcı başlatır.** Komutu, süreyi ve yarıda kalırsa nasıl devam edileceğini (önbellekten) kısa ve net ver. Bilgisayar bu sürede başka ağır iş yapmasın.
- Değerlendirme (birkaç dakika) ardından çalıştırılır.

### Karar 49 — Uygulamaya ve geri bildirime etkisi
`SILUET` sonucu ne olursa olsun, **uygulama ve karar kuralı değişmez** (Karar 18). 6b bir P2 karşılaştırmasıdır, yeni bir yöntem değildir.

### Karar 50 — Sıra
1. Adım 7 (videolar gelince, her şeyden önce).
2. 6b: önceden kayıt → kod → kullanıcının segmentasyon çalıştırması → değerlendirme. Sert sınır 10 Kasım akşamı.
3. Bana gönderilecekler: ADIM_07 (sonuçlar) ve ADIM_06b (sonuçlar).
4. Ardından dondurma güncellemesi (Adım 9) gelecek. Orada `ARKA_PLAN.md`'nin eski Deney 1 tablosu da güncellenecek; şimdi dokunma.

## Yapılacaklar
1. `KARARLAR.md` ve `PLAN.md`.
2. `ilerleme/ADIM_06b.md`: "Önceden belirlenenler" (Karar 48, madde 1–8) ve commit.
3. Kod: segmentasyon ve önbellek betiği, `SILUET` ölçütü (`cekirdek/ozellikler.py` ya da ayrı bir modülde; çekirdek kuralına uygun), değerlendirme betiği (`deneyler/siluet.py`), görsel kontrol aracı eki, testler (yapay maske üzerinde sınır bulma, NaN kuralları, sütun seçimi). `pytest` geçmeli; Deney 1 regresyonu değişmemeli.
4. Kısa sınama (500 kare) ve ardından kullanıcıya uzun çalıştırma talimatı.
5. Sonuçlar gelince ADIM_06b'yi doldur. Basit anlatım bölümü olsun: siluet nedir, neden denendi, ne çıktı.
