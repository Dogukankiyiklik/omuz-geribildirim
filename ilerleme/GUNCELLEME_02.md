# Güncelleme 02 — 6 Kasım 2026 akşamı (danışmandan)

Claude Code: `/clear` sonrası yeni bir oturumdasın. Sırayla şunları oku: `CLAUDE.md`, `PLAN.md`, `ilerleme/KARARLAR.md`, `ilerleme/ADIM_02b.md`, ardından bu dosya. Bu dosyadaki kararları `KARARLAR.md`'ye işle: "AÇIK" satırlarını kapat, yeni karar satırları ekle. Ardından `PLAN.md`'ye **Adım 2c**'yi ekle; Adım 3, 4 ve 11'i aşağıya göre güncelle. Sonra Adım 2c'ye başla.

Adım 0–2b'deki iş çok iyiydi. Kullanıcının galeri gözlemleri, özellikle Petra ve "sondaki sapma", gerçek yöntem sorunlarını ortaya çıkardı.

---

## Açık soruların kararları

### Karar 1 — Tek rastgele referans yerine: hiç referans gerektirmeyen "açı bandı" + zaman bandında çoklu referans
Tek bir rastgele referans tekrarına bağlı olmak keyfi bir seçim ve tek tekrar kararını oynak yapıyor. İki çözüm uygulanacak:
- **Zaman bandında (M39 tipi):** Modeldeki her doğru tekrar sırayla referans yapılır, bant kurulur ve E hesaplanır. Bu E'lerin ortalaması alınır. Rastgelelik ortadan kalkar.
- **Açı bandında (Karar 2):** Referans tekrar zaten yok, bu yüzden sorun da yok.

### Karar 2 — Yeni bant türü: "açı bandı" (kol açısına koşullu bant)
Petra bulgusu, şekle göre DTW'nin omzu farklı kol açılarında karşılaştırdığını gösterdi. Fizyolojik olarak doğru soru şu: **"Kol θ derecedeyken bu kişinin omzu normalde nerede?"** Bu yüzden zamana göre değil, kol açısına göre bir bant kurulur. Bu, projenin başındaki "kol açısına koşullu ölçüt" fikrinin doğrudan uygulaması ve M39'un zaman bandından ayrışan **özgün bir katkı**.

`cekirdek/aci_bandi.py` tanımı:
1. Yalnızca etiketli tekrar kareleri kullanılır (Karar 3).
2. **Faz:** Her tekrarda kol açısının en büyük olduğu kareye kadar olan kısım "kaldırma", sonrası "indirme". Tepe karesi, 5 karelik hareketli medyanla yumuşatılmış kol açısından bulunur. Kalkarken ve inerken omuz farklı davranabileceği için iki faz ayrı tutulur.
3. **Kutular:** Kol açısı 0–180°, 5° genişliğinde kutular, faz başına ayrı.
4. Her kalibrasyon tekrarı her kutuya **bir değer** verir: o kutuya düşen karelerin ortalaması. Böylece n = katkı veren tekrar sayısı olur ve M39'un güven aralığı formülü aynen kullanılabilir:
   - μ = tekrar değerlerinin ortalaması
   - τ = t(0,975; n−1) · s / √n
   - alt sınır: geçerli kutulardaki τ'ların birinci çeyreği (M39 ile aynı)
5. **Geçerlilik:** En az 3 tekrarın katkı verdiği kutu geçerlidir. Geçerli kutular arasındaki boşluklar μ ve τ için doğrusal ara değerle doldurulur. Kalibrasyon aralığının dışı **geçersizdir**.
6. **Bir tekrarın değerlendirmesi:**
   - Her kare kendi fazına ve kol açısı kutusuna göre (μ, τ) ile karşılaştırılır. Kare hatası M39 ile aynıdır: sapma ≤ τ ise 0; değilse min(1, (sapma − τ)/τ). Yönsüz ve yönlü seçenek olsun.
   - E = geçerli karelerin ortalaması.
   - Ayrıca `kapsam` (geçerli kare oranı) ve `aralik_disi` bayrağı raporlanır. Bayrak, karelerin %20'sinden fazlası kalibrasyonun en yüksek açısının 5°'den fazla üstündeyse kalkar.
7. **Kalibrasyon aralığı dışındaki kareler omuz için değerlendirilmez.** O açıda bu kişinin normal omuz yerini bilmiyoruz; tahmin etmek uydurmak olur. Bu önceden verilmiş bir karardır; test verisine bakarak değiştirme.

Açı bandı yalnızca **duruş** ölçütleri içindir: omuz ölçütleri, baş, dirsek, öne kaçma. Kolun kendi açısı için anlamsızdır, çünkü kendisine koşullanmış olur. "Yetersiz kaldırma" Adım 4'te ayrı ele alınır: tekrarın en yüksek kol açısı, kalibrasyon tekrarlarının en yüksek açılarıyla karşılaştırılır.

### Karar 3 — Bant hatası yalnızca etiketli tekrar karelerinde
Pay kareleri tanım gereği tekrarın parçası değil. Kullanımları:
- Dinlenme taban değeri için kullanılmaya devam eder (ilk 8 kare; pay dahil, eskisi gibi).
- DTW, bant ve E yalnızca `first_frame … last_frame` aralığında hesaplanır.
- Uygulamada da tekrar sınırını tekrar ayırıcı belirleyecek; davranış tutarlı olur.

### Karar 4 — Bindirmede ölçek ve döndürme tekrar başından bir kez: **onaylandı**
Gerekçe doğru: kare kare gövde ölçeği silkmeyi gizlerdi. `test_silkme_gizlenmez` testi kalsın. Kişi tekrar sırasında kameraya yaklaşıp uzaklaşırsa küçük bir ölçek hatası olur; bu sınırlama olarak not edilir.

### Karar 5 — Kişiler arası fark nasıl raporlanır
- Her ana sonuç tablosunun yanında **kişi bazlı AUC tablosu** (5 satır) ve "ortalama (en düşük–en yüksek)" biçiminde özet verilir. Örnek: "0,91 (0,80–0,99)".
- Şekillerde kişi değerleri çubuğun üzerinde nokta olarak gösterilir.
- Vasil'in etiketleri hakkında yorum yapılmaz; yalnızca ayrımın bu kişide düşük olduğu raporlanır.

---

## Yeni Adım 2c — Deney 1 v2: yöntem düzeltmeleri (ablasyon) 📤

**Amaç:** Yukarıdaki kararların her birinin etkisini ayrı ayrı göstermek. Deney 1 v1 (M39'a sadık hali) temel çizgi olarak **korunur ve silinmez**.

**Koşullar** (birikimli). Tüm koşullarda 5 omuz ölçütü, yönsüz bant:
| Kod | Bant | Pay | Referans |
| --- | --- | --- | --- |
| v1 | zaman (M39) | dahil | tek rastgele (Deney 1 aynen) |
| v1a | zaman | **hariç** | tek rastgele |
| v1b | zaman | hariç | **çoklu (sırayla hepsi, ortalama)** |
| v2 | **açı bandı** | hariç | yok |

Adillik kuralları aynen geçerli: doğru tekrar birini-dışarıda-bırak, hatalı tekrar aynı sayıda (n−1) doğru tekrarla. v2'de "atla" seçimi rastgele olduğu için tohum yine kullanılır.

**Çıktılar** (`sonuclar/deney1_v2/`):
- Koşul × ölçüt AUC tablosu: silkme/doğru, silkme/diğer, görüş grupları.
- Kişi bazlı AUC.
- YENI için "v2 − v1" farkının kişi bazlı bootstrap güven aralığı.
- v2'de tekrarların ortalama `kapsam`ı ve `aralik_disi` oranı, hata türüne göre.
- **Tohum duyarlılığı:** v1, v1b ve v2'de tohum 0 ile 1 arasında tekrar E'sinin değişimi (medyan ve > 0,05 oranı). Karar 1'in işe yarayıp yaramadığını gösterir.
- **Görsel:**
  - Görsel kontrol aracına açı bandı görünümü ekle: x ekseni kol açısı, y ekseni ölçüt, kalkış ve iniş ayrı renk, bant ve tekrarın noktaları.
  - Şu üç tekrar için v1 ve v2 görüntülerini yan yana üret: Petra cam1 o0 t5, Honza cam1 o0 t5, Terka cam1 o20 t10.
  - Bu şekil sunum için de aday: "kol 90°'deyken omzun normal yeri".

**Dürüstlük notu (ADIM dosyasına yazılacak):** Bu düzeltmeler aynı veriye bakılarak bulundu, yani v1→v2 kazancı iyimser olabilir. Doğrulama için:
- son yöntem Ex7'de **hiç ayar yapılmadan** çalıştırılacak (Adım 4b);
- ayrıca kendi kayıtlarımızda denenecek (Adım 7).

Deneyde v2'nin parametreleri (5° kutu, en az 3 tekrar, %20 bayrağı) **değiştirilmez**. Kötü sonuç çıkarsa da olduğu gibi raporlanır.

**Kabul ölçütü:** Ablasyon tablosu, kişi tablosu, tohum duyarlılığı, üç örnek görsel. Kullanıcı Petra örneğini v1 ve v2'de izledi ve yorumunu ADIM dosyasına not etti.

---

## Diğer adımlarda değişiklik

**Adım 3 (Deney 1b genel bant + 1c yumuşatma):**
- Hem v1b (zaman bandı) hem v2 (açı bandı) ile çalıştır.
- "Genel bant" açı bandında doğal olarak tanımlıdır: diğer 4 kişinin doğru tekrarları, aynı kamera ve yönelim.

**Adım 4 (Deney 2):**
- **Duruş ölçütleri** (omuz = YENI, baş, dirsek, öne kaçma / kol boyu): açı bandı + **yönlü** seçenek.
- **Yetersiz kaldırma:** tekrarın en yüksek kol açısı ile kalibrasyon tekrarlarının en yüksek açıları karşılaştırılır. Sapma = (kalibrasyon medyanı − tekrarın tepesi); kalibrasyon tepelerinin yayılımına (çeyrekler arası açıklık, alt sınır 5°) bölünerek z'ye çevrilir.
- `aralik_disi` bayrağı da karar kuralına bir girdi olabilir ("kol normalden yüksek"). Eğitim kişilerinde gerekli olup olmadığını gör.
- Adım 2c'de açı bandı zaman bandından belirgin şekilde kötü çıkarsa Adım 4'e geçmeden danışmana sor.

**Yeni Adım 4b (eski Adım 11'in önceliği yükseldi) — Ex7'de ayarsız doğrulama:**
- Adım 4 bittikten sonra, son yöntem (açı bandı + Deney 2 kuralı) Ex7 omuz ekstansiyonunda **hiçbir parametre değiştirilmeden** çalıştırılır.
- Kol açısı tanımı aynıdır: üst kolun aşağı dikeyle yaptığı açı.
- Ex7'nin hata türleri farklıdır; omuz silkmesi (`ERR_ELEVATED_SHOULDER`) ortaktır. En azından Deney 1 (silkme/doğru AUC) raporlanır.
- Ekstansiyon önden zor görülür; görüş gruplarına göre ayrı raporla. Bu, yöntemin "başka bir harekette de çalışıyor mu" kanıtıdır.

**Zaman:** 6 Kasım akşamı itibarıyla plandan yaklaşık yarım gün öndeyiz. Adım 2c'nin 7 Kasım'da bitmesi hedefleniyor.
