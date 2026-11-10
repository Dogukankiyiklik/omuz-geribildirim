# Güncelleme 09 — 7 Kasım 2026 öğleden sonra (danışmandan)

Claude Code: `/clear` sonrası yeni oturum. Sırayla oku:
1. `CLAUDE.md`
2. `PLAN.md`
3. `ilerleme/KARARLAR.md`
4. `ilerleme/ADIM_05.md` (Ek: Güncelleme 07 dahil)
5. `ilerleme/ADIM_07.md`
6. `ilerleme/ADIM_08.md`
7. bu dosya

Kararları (36–40) `KARARLAR.md`'ye işle. `PLAN.md`'deki durum işaretlerini güncelle (Adım 7 🔄 çekim bekleniyor; Adım 8 🔄) ve Adım 8 ile Adım 9'un altına bu güncellemenin kısa notunu ekle.

**Bağlam:** Kullanıcı Adım 7 videolarını bugün daha sonra çekecek. Bu güncelleme videoya bağlı **olmayan** işleri içerir. Video gelince Adım 7'nin hazır betiği aynen çalıştırılır; bu güncellemedeki hiçbir şey Adım 7'nin önceden belirlenenlerini değiştirmez.

Adım 7 ve Adım 8 hazırlığı temiz yapılmış. Örneklemde tabakaya kişiyi eklemek doğru bir karardı; LLM sonucu görülmeden yapıldığı için sorun yok.

## Kararlar

### Karar 36 — Deney 4 tasarımı (önceden kayıt; ilk API isteğinden önce commit'lenir)
**Örneklem:** `sonuclar/deney4/orneklem.csv` (150 tekrar, tabaka = sınıf × kişi, tohum 0) onaylandı. Aynı hareketin iki kamerası ayrı tekrar sayılabilir (Deney 3 ile aynı birim); raporda not edilir.

**Koşullar.** Üçünde de hedef üslup, Karar 28'deki **hasta cümlesi** üslubudur.
- **A — Kural tabanlı:** Deney 3'ün hasta cümlesi, sağlam ölçüyle (`cumleler_saglam.csv`). Yeni üretim yapılmaz.
- **B — LLM + sapma kodu:** Girdi, Deney 3'ün sapma kodlarıdır (JSON):
  - karar ("doğru" ya da en fazla 2 hata);
  - her hata için `hata`, `taraf`, `faz`, `yon`; ayrıca hasta cümlesinde söylenecek sayılar, yani 5°'ye yuvarlanmış `olcu`, `beklenen`, `fark` ve birimi (yalnızca derece; öne kaçmada sayı yok);
  - doğru tekrarda tepe kol açısı (5°'ye yuvarlanmış).
  - LLM yalnızca bunu hasta cümlesine çevirir.
- **C — LLM + ham özet (M21 tarzı):** Sapma kodu ve karar **verilmez**.
  - Girdi, 5 ölçütün her biri için kişinin tekrar boyunca değerinin en küçük, en büyük ve ortalamasıdır; yanında kişinin normal aralığının özeti verilir (μ−τ'nun en küçüğü, μ+τ'nun en büyüğü, μ'nün ortalaması). Hepsi tekrarın geçerli karelerinden hesaplanır, hatalı tekrarda Karar 7 ortalamasıyla.
  - Ayrıca tekrarın tepe kol açısı ve kalibrasyon tepelerinin medyanı verilir.
  - Birimler: açılar derece. `YENI` ve `kol_boyu` "gövde boyuna oran" olarak verilir ve istemde kısaca tanımlanır.
  - LLM, tekrarın doğru olup olmadığına ve en fazla iki hataya kendisi karar verir, sonra hasta cümlesini yazar.

**İstem metinleri** `deneyler/istemler/` altında dosya olarak durur: `ortak_uslup.txt`, `B_sistem.txt`, `B_kullanici.txt`, `C_sistem.txt`, `C_kullanici.txt`. Hepsi ADIM_08'e de kopyalanır.
- **Ortak üslup kuralları** Karar 28'den alınır:
  - Türkçe; en fazla 2 hata; hata başına "ne oldu" + "ne yapmalı", yaklaşık 20 kelime.
  - Yüzde ve "gövde boyu" yok; sayı yalnızca derece olarak.
  - Doğru tekrarda kısa, somut ve olumlu bir cümle.
  - **Çıktı yalnızca hastaya söylenecek metindir:** başlık, madde işareti ya da açıklama yok.
- B'ye ek: "Yalnızca verilen hataları söyle, yeni hata ekleme. Yalnızca verilen sayıları kullan."
- C'ye ek: Hata türlerinin listesi ve her ölçütün hangi hatayı gösterdiği, kısa ve tarafsız bir tanımla. **Eşik verilmez.** M21'deki gibi LLM'in kendi yargısı ölçülür.
- **Örnek cümle verilmez (sıfır atış).** Örnek verilseydi LLM A'nın şablonlarını kopyalardı ve karşılaştırma anlamsızlaşırdı.

**Model ve ayarlar:**
- Gemini ücretsiz katmanı. Önce resmi sayfa (https://ai.google.dev/gemini-api/docs/rate-limits ve modeller sayfası) kontrol edilir. Tercih `gemini-2.5-flash`; ücretsiz katmanda yoksa güncel ücretsiz Flash modeli kullanılır.
- Modelin tam adı, kontrol tarihi ve günlük/dakikalık sınırlar ADIM_08'e yazılır.
- `temperature = 0`. Model destekliyorsa "düşünme" bütçesi 0'a çekilir; desteklemiyorsa varsayılan bırakılır ve not edilir.
- Her tekrar için koşul başına **tek istek** atılır. Cevap beğenilmediği için yeniden istek atılmaz. Yalnızca ağ ya da kota hatasında yeniden denenir (mevcut altyapı).
- Toplam 300 istek (150 × B, C). Günlük sınıra takılırsa önbellek sayesinde ertesi gün kaldığı yerden devam edilir.
- Ollama yalnızca Gemini kullanılamazsa yedektir; bu güncellemede kurulmaz.

**Pilot (yalnızca biçim denetimi):**
- Örneklem **dışından** 5 tekrar seçilir (tohum 1, aynı tabakalardan). B ve C ile çalıştırılır. Bunlar raporlanmaz.
- Pilottan sonra istemde yalnızca **biçim** sorunları düzeltilebilir: markdown, başlık, tırnak, İngilizce cevap vb. İçerik kuralları değişmez.
- Pilottan sonra istemler commit'lenir; ancak bundan sonra 150'lik deney çalıştırılır.

**Metrikler** (`deneyler/deney4.py`; aynı çıkarıcı, `cekirdek/metin_cozumleyici.py`):
- Deney 3 ile aynı olanlar: katı, ilk iki, hatalılarda olumlu cümle, doğrularda gereksiz uyarı.
- **B'de sadakat:** Çıkarıcının bulduğu hata listesi, girdideki hata listesine eşit mi (/100)? Ayrıca **eklenen hata** (girdide olmayan bir hata türünden söz etme) ve **atlanan hata** oranları ayrı ayrı.
- **Sayı uydurma:** Metindeki bütün sayılar (rakamla yazılanlar) çıkarılır.
  - B'de izinli küme, girdideki sayılardır.
  - C'de izinli küme: girdideki bütün sayılar, bunların 1'e ve 5'e yuvarlanmış halleri, aynı ölçüt içindeki girdi değerlerinin ikili farkları (onlar da 1'e ve 5'e yuvarlanmış), artı ya da eksi 1 toleransla.
  - İzinli kümede olmayan en az bir sayı içeren cümle "sayı uydurdu" sayılır. Yazıyla yazılmış sayılar ("yirmi") yakalanmaz; sınırlılık.
- **Üslup ihlali:** "%", "yüzde" ya da "gövde boy" geçen cümle oranı; 2'den fazla hata söyleyen cümle oranı.
- **Uzunluk:** ortalama kelime sayısı.
- **Belirsizlik:** Kişi bazlı bootstrap (2000 tekrar, tohum 1). B − A ve C − A eşleştirilmiş farklar (katı, ilk iki, gereksiz uyarı).

**Çıkarıcının bağımsız sınanması (önemli):**
- Çıkarıcı yalnızca şablonlarla ve elle yazılmış cümlelerle geliştirildi (Karar 23). LLM cümleleri onun ilk bağımsız sınavıdır.
- 150 × 3 cümleden 45'i seçilir: her koşuldan 15, tohum 2, sınıflara dengeli.
- Bu cümleler **koşul ve gerçek etiket gizlenerek** karışık sırayla `sonuclar/deney4/elle_etiket.csv` dosyasına yazılır. **Kullanıcı** her cümle için "hangi hatalardan söz ediyor" sorusunu kendisi işaretler.
- Raporlanacaklar: çıkarıcı ile kullanıcının uyumu (tam eşleşme /45; koşul başına), uyuşmayan cümlelerin listesi. Bu sonuca bakılarak sözlük **değiştirilmez**; uyuşmazlık olduğu gibi raporlanır.

**Önceden belirlenen beklentiler** (sonuç ne olursa olsun raporlanır):
1. B'nin katı ve ilk iki değerleri A'ya yakın çıkar. B'de karar aynı; fark yalnızca LLM'in hata eklemesinden ya da atlamasından gelir.
2. C, A'dan daha düşük katı ve daha yüksek gereksiz uyarı verir (M21'deki "eşik uydurma, aşırı özgüven" bulgusu).
3. Sayı uydurma C'de B'den yüksek çıkar.

### Karar 37 — Adım 9 hazırlığı (dondurma 13 Kasım akşamı; şimdi taslak)
- `deneyler/hepsi.py`: Bütün deneyleri doğru sırayla temiz bir klasörde yeniden üretir ve sonuçları `sonuclar/` altındaki kayıtlı dosyalarla karşılaştırır (regresyon özeti).
  - Sıra: Deney 1, 1 v2, 1b, 1c, 2, Ex7, 3, 3 (sağlam), tekrar ayırma, kamera açısı, hız eşiği, kural dışa aktarma.
  - Adım 7 ve 8 dahil değildir (video ve API gerektirir); onların kayıtlı çıktıları yalnızca listelenir.
  - Uzun sürecek; **tam çalıştırmayı kullanıcı yapar.** Sen yalnızca küçük bir alt kümede (`--hizli`) denersin.
- Taslak belgeler (sayılar dondurmada kesinleşir; şimdi `TASLAK` başlığıyla):
  - `docs/YENIDEN_KURULUM.md`: Hocanın şablonundaki 7 başlık (ortam, girdi hazırlığı, pose çıkarımı, ölçüm/hizalama, hata hesabı, geri bildirim, çıktı). Başka bir öğrencinin kurabileceği netlikte, komutlarla.
  - `docs/LLM_KULLANIMI.md`: Üretken yapay zekânın nerede ve hangi amaçla kullanıldığı. Claude Code: kod yazma, hata ayıklama, deney betikleri. Claude (danışman sohbeti): literatür taraması, planlama, sonuç yorumu, karar önerileri. Gemini: yalnızca Deney 4'te karşılaştırma koşulu, ürün yöntemi değil. Kullanıcının kendi yaptıkları: deneyleri çalıştırma, galeri ve görsel kontrol, örnek cümle yorumları, canlı deneme, video çekimi ve etiketleme.
  - `docs/SURUMLER.md`: Python sürümü, `pip freeze` çıktısı, MediaPipe sürüm notu (veri seti 0.10.20, uygulama 1.2.2, ölçülen fark).

### Karar 38 — Sunum için şekil adayları
- `deneyler/sunum_sekilleri.py` → `sonuclar/sunum/`. Kayıtlı sonuç dosyalarından üretilir; hiçbir deney yeniden çalıştırılmaz. PNG, 16:9 slayta uygun, Türkçe etiketli, büyük yazı.
  1. **Problem:** Bantsız ve bantlı omuz silkme tespiti (Ex1; ham YENI 0,70 → v2). Tek çubuk çifti ya da sade bir çubuk grafik.
  2. **Fikir:** Açı bandı görseli, "kol 90°'deyken omzun normal yeri" (Adım 2c'deki Petra örneği). Doğru tekrar bandın içinde, silkmeli tekrar dışında.
  3. **Kişiye özel kalibrasyon:** Genel bant ile kişiye özel bant (Deney 1b).
  4. **Geri bildirim:** Bir silkme tekrarında uygulamanın ekran görüntüsü: hasta cümlesi, bindirme ve kırmızı uzuv. Veri setinden Honza'nın sağlık kontrolü tekrarı 5 ya da 6.
  5. **Bindirme (P3):** Aynı tekrarın 3 karesi yan yana (kaldırırken, tepede, indirirken), turkuaz referans ve kullanıcı iskeleti.
- Ayrıca Honza sağlık kontrolünün pencere modundan 20–30 saniyelik bir ekran kaydı (`sonuclar/sunum/demo_yedek_veriseti.mp4`). Bu, Adım 7 videoları gelmeden önce de elde bulunan ikinci bir yedektir.
- Şekiller **aday**dır. Hangilerinin slayta gireceğine 13–15 Kasım'da danışmanla karar verilir.

### Karar 39 — İsteğe bağlı adımların durumu
- 6b (siluet) ve 10 (REHAB24-6) bu güncellemede başlatılmaz.
- Adım 7 ve 8 bittikten sonra 6b için yalnızca bir **süre tahmini** yapılır: segmentasyonun Ex1 önden + çapraz videolarında kaç saat süreceği, 3 video üzerinde ölçülerek. Karar ondan sonra verilir.
- REHAB24-6 büyük olasılıkla yapılmayacak; gelecek çalışma olarak yazılır.

### Karar 40 — Pencere modunda video denemesi (Adım 6'nın son açığı)
Kullanıcı aşağıdaki komutla, veri setindeki bir videoyla pencere modunu bir kez dener. Komutu ADIM_06'nın sonunda kullanıcıya hazır ver: profil, veri setinden üretilmiş bir kalibrasyonla. Gerekirse küçük bir yardımcı betik ya da `--veri-seti` seçeneği ekle; yeni yöntem kodu yazılmaz.
```bash
python -m uygulama.main --veri-seti ex1_Honza --kamera cam1 --yonelim 0
```
Kullanıcının gözlemi ADIM_06'nın kabul bölümüne yazılır.

## Yapılacaklar
1. **Karar 40:** Pencere modunda video denemesi için komutu hazırla ve kullanıcıya ver. Kullanıcı denedikten sonra gözlemini ADIM_06'ya yaz.
2. **Karar 36:** İstem dosyaları, `deneyler/deney4.py`, metrikler (sayı uydurma ve sadakat dahil), elle etiketleme dosyası üretimi ve bunların testleri (ağ yok, `SahteSaglayici`).
   - ADIM_08'e "Önceden belirlenenler" bölümünü yaz ve commit'le.
   - Kullanıcı `GEMINI_API_KEY`'i kurunca:
     1. pilot (5 tekrar, raporlanmaz);
     2. gerekirse yalnızca biçim düzeltmesi; istemleri commit'le;
     3. 150'lik deney. Bunu kullanıcı çalıştırır; komutu, süresini ve kota durumunu söyle.
   - Ardından kullanıcıya 45 cümlelik elle etiketleme dosyasını ver; talimat kısa ve açık olsun.
3. **Karar 37:** `deneyler/hepsi.py` (`--hizli` ile dene) ve üç taslak belge.
4. **Karar 38:** Sunum şekil adayları ve veri setinden demo yedeği.
5. Adım 7 videoları geldiğinde: ADIM_07'deki komut aynen çalıştırılır ve sonuçlar ADIM_07'ye yazılır. Bu güncellemedeki işlerin yarım kalması Adım 7'yi bekletmez; video gelince önce Adım 7 yapılır.
6. Her iş bitince ilgili ADIM dosyasını güncelle. Bana dönerken gönderilecekler: ADIM_07 (sonuçlar), ADIM_08 (sonuçlar), `sonuclar/sunum/` içindeki PNG'lerin listesi.
