# ADIM 08 — Deney 4: LLM ile kural tabanlı karşılaştırması

**Tarih:** 2026-11-07 (altyapı; Güncelleme 09 ile tasarım ve kod)
**Durum:** Kısmen. Tasarım "Önceden belirlenenler" bölümünde ve **ilk API isteğinden önce** commit'lendi. Kod, istemler ve ağsız testler hazır. **Bekleniyor:** kullanıcının `GEMINI_API_KEY`'i kurması → pilot → (gerekirse yalnızca biçim düzeltmesi) → 150'lik deney (kullanıcı çalıştırır) → 45 cümlelik elle etiketleme (kullanıcı).

## Önceden belirlenenler (Karar 36; ilk API isteğinden önce commit'lendi)
Kaynak: `ilerleme/GUNCELLEME_09.md`, Karar 36. Kod bu tanımlarla yazıldı. Pilottan sonra yalnızca **biçim** düzeltmesi yapılabilir; içerik kuralları, metrikler ve örneklem değişmez.

### 1. Örneklem ve birim
- `sonuclar/deney4/orneklem.csv`: 150 tekrar (50 doğru + her hata türünden 20), tabaka = sınıf × kişi, tohum 0, yalnızca önden + çapraz. Birim Deney 3'teki gibi (satır, kamera); aynı hareketin iki kamerası ayrı tekrar sayılabilir. Raporda not edilir.
- **Aynı girdi, aynı istek:** İki tekrarın B (ya da C) girdisi birebir aynıysa istek de aynıdır ve önbellekten tek yanıt kullanılır. Örneğin tepe açısı aynı 5°'lik dilime düşen iki doğru tekrarın B girdisi aynıdır. Sahte sağlayıcıyla yapılan kuru çalıştırmada 300 istek yerine 243 ağ isteği gitti. Bu, "koşul başına tek istek" kuralıyla tutarlıdır (sıcaklık 0'da aynı istem aynı cevabı vermeli). Her tekrar yine ayrı satır olarak sayılır.

### 2. Koşullar (üçü de Karar 28'deki hasta cümlesi üslubunda)
- **A — Kural tabanlı:** Deney 3'ün hasta cümlesi, sağlam ölçüyle. Yeni üretim yok. Kod A metnini Deney 3'ün kodundan yeniden üretir ve `sonuclar/deney3/cumleler_saglam.csv` ile **birebir aynı** olduğunu `assert` ile denetler (150/150 geçti).
- **B — LLM + sapma kodu.** Girdi JSON'u:
  - `karar`: "doğru" ya da "hatalı";
  - hatalıda `hatalar` (en fazla 2, önem sırasıyla): `hata` (Türkçe ad), `taraf`, `faz`, `yon` (ne olduğunun kısa tarifi);
  - `sayilar`: yalnızca A'nın hasta cümlesinin de sayı söylediği durumda verilir. İçinde `olcu_adi`, 5°'ye yuvarlanmış `olcu` ve `beklenen`, `fark` (yuvarlanmış iki değerin farkı) ve `birim` = "derece" vardır. Öne kaçmada sayı yok. Fark 0 ise ya da cümlenin yönüyle çelişiyorsa sayı verilmez (A ile aynı kural).
  - doğruda `tepe_kol_acisi` (5°'ye yuvarlanmış).
  - Denetim: A metnindeki sayılar her zaman B girdisindeki sayıların içinde. A için "sayı uydurdu" 0,00 ve sadakat 100,00 çıktı (madde 9).
- **C — LLM + ham özet (M21 tarzı).** Karar ve sapma kodu **verilmez**. Girdi JSON'u:
  - 5 ölçüt: `kulak_omuz` (YENI), `bas_govde_acisi` (bas), `kol_govde_acisi` (on_kacma), `kol_boyu`, `dirsek_acisi`. Her biri için `hasta` (en küçük, en büyük, ortalama) ve `normal_aralik` (μ−τ'nun en küçüğü, μ+τ'nun en büyüğü, μ'nün ortalaması);
  - hepsi tekrarın **geçerli karelerinden**, yani μ ve τ'nun tanımlı olduğu karelerden. Hatalı tekrarda μ ve τ, Karar 7'deki n modelin kare başına ortalamasıdır (NaN'lar atlanır; τ için `cekirdek/geribildirim.tau_ortalamasi` eklendi). Doğru tekrarda kendisinin dışarıda bırakıldığı tek model kullanılır;
  - `tepe_kol_acisi` ve `kalibrasyon_tepe_medyani` (Deney 3'ün `beklenen_tepe`'si);
  - birimler: açılar derece, 1 ondalık. `kulak_omuz` ve `kol_boyu` "gövde boyuna oran", 3 ondalık; istemde kısaca tanımlı.
- **Sıfır atış:** İstemde örnek cümle yok.

### 3. İstemler
Dosyalar `deneyler/istemler/` altında. `{ortak_uslup}` yerine `ortak_uslup.txt`, `{girdi}` yerine girintili girdi JSON'u konur. Pilottan önceki hâlleri:

**`deneyler/istemler/ortak_uslup.txt`**
```text
Sen bir fizyoterapi uygulamasının geri bildirim yazarısın. Bir hasta, sağ kolunu yana kaldırma egzersizini (omuz abdüksiyonu: kol yandan, vücutla aynı hizada yukarı kaldırılır ve indirilir) kamera karşısında yaptı. Bir tekrarın ardından hastanın ekranında gösterilecek geri bildirimi yazacaksın.

Üslup kuralları:
- Türkçe yaz ve hastaya "sen" diye hitap et.
- En fazla 2 hatadan söz et.
- Her hata için önce ne olduğunu, sonra ne yapması gerektiğini söyle. Hata başına yaklaşık 20 kelime yeter.
- Yüzde kullanma, "gövde boyu" ifadesini kullanma. Sayı kullanırsan yalnızca derece olarak kullan.
- Tekrar doğruysa kısa, somut ve olumlu bir cümle yaz.
- Çıktı yalnızca hastaya söylenecek metindir: başlık, madde işareti, tırnak işareti ya da açıklama ekleme.
```

**`deneyler/istemler/B_sistem.txt`**
```text
{ortak_uslup}

Sana bu tekrarın değerlendirmesi JSON olarak verilecek. Değerlendirmeyi bir ölçüm sistemi yaptı; senin işin yalnızca bunu hastaya söylenecek metne çevirmek.

Alanlar:
- "karar": "doğru" ya da "hatalı".
- "hatalar": en fazla 2 hata, önem sırasıyla. Her hatada:
  - "hata": hatanın adı;
  - "taraf": hangi taraf;
  - "faz": hatanın hareketin hangi anında görüldüğü ("kaldırırken", "en üstteyken", "indirirken");
  - "yon": ne olduğunun kısa tarifi;
  - "sayilar" (varsa): "olcu" (bu tekrardaki değer), "beklenen" (hastanın normal değeri), "fark" ve "birim". Sayıların neyi ölçtüğü "olcu_adi" alanında yazar. "sayilar" yoksa sayı kullanma.
- Doğru tekrarda "tepe_kol_acisi": kolun çıktığı en yüksek açı (derece).

Yalnızca verilen hataları söyle, yeni hata ekleme. Yalnızca verilen sayıları kullan.
```

**`deneyler/istemler/B_kullanici.txt`**
```text
Tekrarın değerlendirmesi:
{girdi}

Hastaya söylenecek metni yaz.
```

**`deneyler/istemler/C_sistem.txt`**
```text
{ortak_uslup}

Sana bu tekrarın ham ölçüm özeti JSON olarak verilecek. Tekrarın doğru olup olmadığına ve varsa en fazla iki hataya kendin karar ver; sonra yalnızca hastaya söylenecek metni yaz.

Olası hata türleri:
- omuz kalkması: sağ omzun kulağa doğru kalkması (omuz silkme);
- baş eğme: başın yana eğilmesi;
- kolun öne kaçması: kolun yandan değil, öne doğru kalkması;
- dirsek bükme: kolun dirsekten bükülmesi;
- yetersiz kaldırma: kolun hastanın normalinden daha az kaldırılması.

Ölçütler (hepsi sağ kol ve sağ omuz için, tekrar boyunca):
- "kulak_omuz": sağ kulak ile sağ omuz arasındaki dikey mesafe, gövde boyuna oran olarak (gövde boyu: omuzların ortası ile kalçaların ortası arasındaki uzaklık). Omuz kalkmasıyla ilgilidir; omuz kulağa yaklaştıkça küçülür.
- "bas_govde_acisi": baş ile gövde ekseni arasındaki açı (derece). Baş eğmeyle ilgilidir.
- "kol_govde_acisi": sağ bilek, sağ omuz ve sağ kalça arasındaki açı (derece). Kolun öne kaçmasıyla ilgilidir.
- "kol_boyu": kolun kamerada görünen boyu (sağ omuz ile sağ bilek arası), gövde boyuna oran olarak. Kolun öne kaçmasıyla ilgilidir; kol kameraya doğru gittikçe kısa görünür.
- "dirsek_acisi": sağ omuz, sağ dirsek ve sağ bilek arasındaki açı (derece; 180 düz kol). Dirsek bükmeyle ilgilidir.

Her ölçütte "hasta" alanı, bu tekrardaki değerlerin en küçüğü, en büyüğü ve ortalamasıdır. "normal_aralik" alanı, hastanın kendi doğru (kalibrasyon) tekrarlarından kolun açısına göre her an için hesaplanmış normal aralığın özetidir: alt sınırın en küçüğü, üst sınırın en büyüğü ve ortanın ortalaması. Hepsi bu tekrarın aynı anlarından hesaplanmıştır.

Ayrıca "tepe_kol_acisi" bu tekrarda kolun çıktığı en yüksek açıdır (derece; kol aşağıdayken 0, tam yukarıdayken yaklaşık 180). "kalibrasyon_tepe_medyani", hastanın doğru tekrarlarındaki en yüksek açıların ortancasıdır. Yetersiz kaldırmayla ilgilidir.
```

**`deneyler/istemler/C_kullanici.txt`**
```text
Tekrarın değerlendirmesi:
{girdi}

Hastaya söylenecek metni yaz.
```

### 4. Model ve ayarlar
- **Resmi sayfa kontrolü (7 Kasım 2026).** `ai.google.dev/gemini-api/docs/...` adresleri `aistudio.google.com/docs/...` adresine yönleniyor. Bulunanlar:
  - **Rate limits sayfası** ücretsiz katman sayılarını vermiyor: "Rate limits depend on a variety of factors (such as your usage tier) and can be viewed in Google AI Studio." Sınırlar `https://aistudio.google.com/rate-limit` adresinde, giriş yapınca görünüyor. **Kullanıcı bu sayfadaki dakikalık ve günlük sınırları "Sonuçlar"a yazdıracak.**
  - **Deprecations sayfası:** "gemini-2.5-flash is deprecated and is no longer available to select in Google AI Studio." · "Effective December 1, 2026, all API requests to gemini-2.5-flash will automatically route to gemini-3.5-flash-lite." Models sayfası: "API access to the 2.5 models is limited to existing users."
  - `gemini-2.5-flash-lite`: "not deprecated and remains available through the API until further notice."
  - Düşünme sayfası yalnızca yeni Interactions API'sini (`thinking_level`) anlatıyor. `generateContent` için `thinkingBudget = 0`'ı doğrulayan bir cümle bulunamadı.
- **Seçim kuralı (Karar 36'ya göre):**
  1. Kullanıcının anahtarı `gemini-2.5-flash`'a erişebiliyorsa o kullanılır. Kontrol: `python -m deneyler.deney4 modeller`. Bu komut erişilebilen modelleri listeler ve kota harcamaz.
  2. Erişemiyorsa (yeni kullanıcılar için büyük olasılık), listedeki güncel ücretsiz **Flash** modeli kullanılır. Öncelik: kullanımdan kaldırılmamış en yeni "flash" (lite olmayan); yoksa "flash-lite". Modelin tam adı ve sınırlar "Sonuçlar"a yazılır.
- `temperature = 0`. Düşünme: 2.5 modellerinde `generationConfig.thinkingConfig.thinkingBudget = 0`. Diğer modellerde varsayılan bırakılır ve not edilir; gerekirse `--dusunme` ile bir düzey verilir. Ayar pilotta denenir; API reddederse varsayılan bırakılır ve not edilir.
- Her tekrar için koşul başına **tek istek**. Yalnızca ağ ya da kota hatasında yeniden denenir (`cekirdek/llm.py`). Cevap beğenilmediği için yeniden istek atılmaz.
- Toplam 300 istek (150 × B, C); aynı girdiler önbellekten gelir (madde 1). Varsayılan aralık 6 s (`--rpm 10`). Günlük sınıra takılırsa betik durur; önbellek sayesinde aynı komut ertesi gün kaldığı yerden devam eder.
- Ollama yalnızca yedek; kurulmadı.

### 5. Pilot (yalnızca biçim denetimi; raporlanmaz)
- Örneklem dışından 5 tekrar: önden + çapraz görüşte örneklemde olmayan tekrarlar arasından, 30 tabakadan (sınıf × kişi) tohum 1 ile 5 tabaka, her birinden 1 tekrar (`sonuclar/deney4/pilot/girdiler.csv`).
- B ve C ile çalıştırılır (10 istek). Yalnızca **biçim** sorunları düzeltilebilir: markdown, başlık, tırnak, İngilizce cevap vb. İçerik kuralları değişmez. Sonra istemler commit'lenir; ancak bundan sonra 150'lik deney çalıştırılır.

### 6. Metrikler (`deneyler/deney4.py`; çıkarıcı `cekirdek/metin_cozumleyici.py`, Deney 3 ile aynı)
- L = metinden çıkarılan hata listesi; S = sistemin (Deney 3) hata listesi, yani B'nin girdisi.
- Deney 3 ile aynı: **katı** (L'nin ilki = birincil), **ilk iki** (birincil ∈ L), **hatalılarda olumlu cümle** (L boş), **doğrularda gereksiz uyarı** (L boş değil).
- **Sadakat** (150 tekrarın hepsinde): L = S (sıra dahil) /100, ayrıca küme eşitliği. **Eklenen hata** (L'de olup S'de olmayan bir tür) /100 ve **atlanan hata** (S'de olup L'de olmayan bir tür) /100 ayrı ayrı. Bunlar B'nin sadakatidir; C'de aynı sütunlar yalnızca "kural sistemiyle uyum" olarak betimseldir.
- **Sayı uydurma:** Metindeki rakamla yazılmış bütün sayılar çıkarılır (Türkçe ondalık virgülü dahil). En az bir sayı izinli kümede yoksa metin "sayı uydurdu" sayılır.
  - A ve B: izinli küme = B girdisindeki sayılar, tam eşleşme.
  - C: girdideki bütün sayılar, bunların 1'e ve 5'e yuvarlanmışları, aynı ölçüt içindeki ikili farklar ve onların 1'e ve 5'e yuvarlanmışları. Tepe ile kalibrasyon medyanı bir grup sayılır. Tolerans ±1.
  - Yazıyla yazılmış sayılar ("yirmi") yakalanmaz; sınırlılık.
- **Üslup ihlali:** "%", "yüzde" ya da "gövde boy" geçen metin /100; 2'den fazla hata söyleyen metin /100. **Uzunluk:** ortalama kelime sayısı. Ayrıca sayı içeren metin /100 (betimsel).
- Tablolar: koşul başına özet, kişi bazlı, gerçek sınıfa göre. Her koşuldan aynı 5 tekrarın örnek cümlesi (`ornek_cumleler.md`, tohum 0; 1 doğru + 4 hata türü).
- **Belirsizlik:** Kişi bazlı bootstrap (2000 tekrar, tohum 1). B − A ve C − A eşleştirilmiş farklar: katı, ilk iki, gereksiz uyarı.

### 7. Çıkarıcının bağımsız sınaması
- Çıkarıcı yalnızca şablonlarla ve elle yazılmış cümlelerle geliştirildi (Karar 23). LLM cümleleri onun ilk bağımsız sınavıdır.
- 450 cümleden 45'i seçilir: her koşuldan 15, tohum 2. Koşul başına her sınıftan 2 cümle, tohumla seçilen 3 sınıftan birer fazla. Bir tekrar en fazla bir koşuldan seçilir; böylece aynı tekrarın iki cümlesi listede yan yana gelmez.
- `sonuclar/deney4/elle_etiket.csv`: yalnızca sıra, cümle ve boş işaret sütunları (`omuz`, `bas`, `one_kacma`, `dirsek`, `az_kaldirma`, `not`). Koşul ve gerçek etiket **gizli**, sıra karışık. Anahtar `elle_etiket_anahtar.csv` dosyasında; kullanıcı onu açmaz.
- **Kullanıcı** her cümle için "hangi hatalardan söz ediyor?" sorusunu kendisi işaretler.
- Rapor: tam eşleşme (küme olarak) /45, koşul başına, ve uyuşmayan cümlelerin listesi. Bu sonuca bakılarak sözlük **değiştirilmez**.

### 8. Önceden belirlenen beklentiler (sonuç ne olursa olsun raporlanır)
1. B'nin katı ve ilk iki değerleri A'ya yakın çıkar. Karar aynı; fark yalnızca LLM'in hata eklemesinden ya da atlamasından gelir.
2. C, A'dan daha düşük katı ve daha yüksek gereksiz uyarı verir (M21'deki "eşik uydurma, aşırı özgüven" bulgusu).
3. Sayı uydurma C'de B'den yüksek çıkar.

### 9. A koşulu (LLM'siz; `python -m deneyler.deney4 hazirla` çıktısından kopyalandı)
A, Deney 3'ün cümlesi olduğu için LLM isteğinden önce hesaplanabilir. Bu sayılar örneklemin Deney 3'teki değeridir; tasarımı etkilemedi.

| metrik | A |
| --- | --- |
| tekrar | 150 (100 hatalı, 50 doğru) |
| katı /100 | 61.00 |
| ilk iki /100 | 73.00 |
| hatalılarda olumlu cümle /100 | 15.00 |
| doğrularda gereksiz uyarı /100 | 8.00 |
| sadakat: liste = girdi /100 | 100.00 (denetim) |
| eklenen / atlanan hata /100 | 0.00 / 0.00 (denetim) |
| sayı uydurdu /100 | 0.00 (denetim) |
| sayı içeren /100 | 94.00 |
| üslup: %, yüzde, gövde boy /100 | 0.00 |
| üslup: 2'den fazla hata /100 | 0.00 |
| ortalama kelime | 17.37 |

## Basit anlatım (Güncelleme 09)
- Üç tür cümleyi karşılaştıracağız:
  - **A:** bizim kurallarla yazdığımız cümle;
  - **B:** sistemimizin bulduğu hatayı ve sayıları yapay zekâya (LLM) verip "bunu hastaya söyle" dediğimiz cümle;
  - **C:** yapay zekâya yalnızca ham ölçümleri verip "hatayı da sen bul" dediğimiz cümle.
- B, "yapay zekâ cümleyi daha iyi kurar mı, yoksa olmayan bir hata ya da sayı mı uydurur?" sorusunu sınar. C, makalelerde (M21) görülen "yapay zekâ eşik uyduruyor ve fazla emin konuşuyor" bulgusunu bizim veride sınar.
- **Sıfır atış:** Yapay zekâya örnek cümle vermiyoruz. Verseydik bizim şablonlarımızı kopyalardı ve karşılaştırma anlamsızlaşırdı.
- **Önceden kayıt:** Ne ölçeceğimizi, hangi sayıyı "uydurma" sayacağımızı ve ne beklediğimizi ilk isteği atmadan yazıp kaydettik.
- **Pilot:** Önce 5 tekrarla küçük bir deneme yapılacak. Bu denemede yalnızca yazım biçimi düzeltilebilir (ör. model başlık ya da madde işareti eklerse). Ne söyleneceğine dair kurallar değişmez.
- **Çıkarıcının sınavı:** Cümleden "hangi hata söylendi"yi bulan kodumuz şimdiye kadar yalnızca kendi şablonlarımızla sınandı. Yapay zekâ cümleleri onun ilk gerçek sınavı. Bunu ölçmek için 45 cümleyi, hangi koşuldan geldiğini bilmeden sen etiketleyeceksin.

*Jargon:* **Sadakat:** yapay zekânın kendisine verilen hataları eksiksiz ve fazlasız söylemesi. **Sayı uydurma:** cümlede girdide olmayan bir sayı geçmesi. **Eşleştirilmiş fark:** aynı 150 tekrar üzerinde iki koşulun farkı. **Bootstrap:** kişileri yeniden örnekleyerek farkın ne kadar oynak olduğunu ölçme.

## Yapılanlar (Güncelleme 09)
- `deneyler/istemler/`: `ortak_uslup.txt`, `B_sistem.txt`, `B_kullanici.txt`, `C_sistem.txt`, `C_kullanici.txt` (madde 3).
- `deneyler/deney4.py`: `hazirla` (ağ yok; girdiler + pilot girdileri + A denetimi), `modeller`, `pilot`, `calistir`, `elle-uret`, `elle-degerlendir`. Kararlar ve A metni Deney 3'ün koduyla (`deney3.kararlar`, `deney3.ayrintilar`, `cekirdek/degerlendirici.kod_uret`); kopya kod yok.
- `cekirdek/llm.py`: `Istek.dusunme` (int → `thinkingBudget`, str → `thinkingLevel`, None → varsayılan; None olunca önbellek anahtarı eskisiyle aynı) ve `GeminiSaglayici.modeller()`.
- `cekirdek/geribildirim.py`: `tau_ortalamasi` (Karar 7 ortalaması, τ için). `deneyler/deney3.ayrintilar` artık `tau` da döndürüyor. Deney 3'ün kendi çıktısında kullanılmıyor; A metni 150/150 aynı.
- `testler/test_deney4.py` (ağsız, 23 test): B sayılarının hasta cümlesiyle aynı olması (13 sapma kodu dalı), sayı çıkarma, C'nin izinli kümesi ve toleransı, istem dosyaları, düşünme ayarı ve Gemini gövdesi, sahte sağlayıcıyla çalıştırma ve önbellek, kalıcı hatada durma, sadakat / uydurma / üslup metrikleri, 45 cümlelik seçimin dengesi ve tekrarlanabilirliği, etiketleme dosyasının gizliliği ve üzerine yazmaması, uyum hesabı.
- **Kuru çalıştırma:** `python -m deneyler.deney4 calistir --saglayici sahte --rpm 0` bütün boru hattını (300 yanıt, tablolar, örnekler) ağ olmadan çalıştırdı. Çıktı geçici klasöre yazıldı ve silindi; sonuç değildir.

## Değişen / eklenen dosyalar (Güncelleme 09)
| Dosya | Ne işe yarıyor |
| --- | --- |
| `deneyler/istemler/*.txt` | Beş istem dosyası |
| `deneyler/deney4.py` | Girdiler, LLM çalıştırma, metrikler, elle etiketleme |
| `testler/test_deney4.py` | Ağsız testler |
| `cekirdek/llm.py` | Düşünme ayarı, model listesi |
| `cekirdek/geribildirim.py`, `deneyler/deney3.py` | τ'nun Karar 7 ortalaması (yalnızca C girdisi için) |
| `sonuclar/deney4/girdiler.csv`, `pilot/girdiler.csv` | 150 + 5 tekrarın A metni, B ve C girdileri |

## Nasıl çalıştırılır
```bash
# 0) Bir kez: Google AI Studio'dan ücretsiz anahtar al, proje kökünde .env dosyasına yaz (git'e girmez):
#    GEMINI_API_KEY=...
# 1) Erişilebilen modeller (kota harcamaz):
python -m deneyler.deney4 modeller
# 2) Pilot, 10 istek, ~1 dk (Claude Code çalıştırır ve biçimi kontrol eder):
python -m deneyler.deney4 pilot --model <model>
# 3) Asıl deney, 150 × B, C (kullanıcı çalıştırır):
python -m deneyler.deney4 calistir --model <model>
# 4) Elle etiketleme dosyası, sonra kullanıcının etiketleriyle uyum:
python -m deneyler.deney4 elle-uret
python -m deneyler.deney4 elle-degerlendir
```
- `hazirla` zaten çalıştırıldı (~30 s). Girdiler değişmediği sürece yeniden çalıştırmak gerekmez.
- 3. adımın süresi: istekler arası 6 s ile en az ~25–30 dk (243 ağ isteği; yanıt süresi ekstra). Günlük sınır 300'ün altındaysa betik durur; ertesi gün aynı komut kaldığı yerden devam eder.

## Sonuçlar
### Model ve pilot (7 Kasım 2026, 14:24; Claude Code çalıştırdı)
- **Model:** `gemini-2.5-flash`. `python -m deneyler.deney4 modeller` listesinde var ve kullanıcının anahtarı ona erişebiliyor. Karar 36'nın ilk tercihi kullanıldı; yedek kurala gerek kalmadı.
- **Ayarlar:** temperature 0; `thinkingBudget = 0` API tarafından kabul edildi (bitiş nedeni `STOP`, yanıt süresi ~1 s).
- **Sınırlar:** AI Studio'daki sayılar okunamadı. Kullanıcının bulduğu ikinci el bilgi (eski 1.5/2.0 Flash için 15 istek/dk, 1.500 istek/gün) doğrulanmadı. Deney `--rpm 10` ile (istekler arası 6 s) çalıştırılır; günlük sınıra takılırsa önbellekten devam edilir.
- **Tekrarlanabilirlik notu:** 2.5 Flash'a gelen istekler 1 Aralık 2026'dan sonra `gemini-3.5-flash-lite`'a yönlendirilecek (Deprecations sayfası). Bu deneyin yanıtları `onbellek.jsonl`'de saklı. Aynı modelle yeniden istek atmak o tarihten sonra mümkün olmayabilir; sınırlılık olarak yazılır.
- **Pilot:** 5 tekrar × B, C = 10 yanıt, 11 ağ isteği (1 istek geçici hatadan sonra 2. denemede geçti), 101,6 s (`sonuclar/deney4/pilot/bilgi.json`).
- **Biçim denetimi:** 10 yanıtın hiçbirinde markdown, başlık, madde işareti, tırnak ya da İngilizce yok; hepsi düz Türkçe metin. **İstemlerde değişiklik yapılmadı**; pilottan önceki hâlleri (madde 3) geçerli.
- İçerik pilotta raporlanmaz (Karar 36). Pilotun yanıtları ve tabloları `sonuclar/deney4/pilot/` altında, yalnızca kayıt için.

## Kabul ölçütü kontrolü
- [x] Önceden belirlenenler ilk API isteğinden önce commit'lendi.
- [x] Testler geçti: tam pytest `179 passed, 1 xfailed in 82.71s`.
- [x] Pilot (biçim): düzeltme gerekmedi; istemler değişmeden commit'li.
- [ ] Üç koşulun tablosu ve her koşuldan 5 örnek cümle.
- [ ] Çıkarıcının bağımsız sınaması (45 cümle).

## Kararlar ve sapmalar (Güncelleme 09)
- **Model sorunu:** Karar 36'nın tercih ettiği `gemini-2.5-flash` resmi sayfaya göre kullanımdan kaldırılmış ve yeni kullanıcılara kapalı. Karar 36'nın yedek kuralı ("güncel ücretsiz Flash modeli") uygulanacak; seçim `modeller` komutunun çıktısına göre yapılır ve buraya yazılır. Model kodda sabit değil, `--model` ile verilir.
- **Aynı girdi → aynı yanıt** (madde 1): kural dışı bir yeniden kullanım değil; önbellek anahtarı istemin tamamı.
- **B'deki `yon` alanı** kodlardaki ±1 yerine kısa bir Türkçe tarifle verildi (ör. "sağ omuz kulağa doğru kalktı"). ±1 tek başına modele bir şey anlatmaz. Tarifler hasta cümlesi şablonlarının yön dallarıyla aynı anlamda; düzeltme önerisi içermez.
- **B'de az kaldırmanın fazı** "en üstteyken" (Deney 3'teki gibi).
- **C'deki sadakat sütunları** yalnızca betimsel ("kural sistemiyle uyum"); C'nin girdisinde hata listesi yok.
- **A için de sayı uydurma ve sadakat hesaplandı.** Bu bir denetimdir: B'nin izinli kümesinin A'nın gerçekten kullandığı sayıları kapsadığını gösterir (0,00 ve 100,00).

## Açık sorular / danışmana notlar (Güncelleme 09)
- Yeni bir Flash modeli (ör. 3.x) "düşünme"yi tamamen kapatmaya izin vermeyebilir. Bu durumda en düşük düzey mi, yoksa varsayılan mı kullanılsın? Karar 36 "varsayılan bırakılır ve not edilir" diyor; ben varsayılanı bırakacağım.

---

## Basit anlatım (altyapı, Güncelleme 08)
- Deney 4'te aynı bilgiyi bir yapay zekâ dil modeline (LLM) verip, onun yazdığı cümlenin bizim kurallarla ürettiğimiz cümleden iyi mi kötü mü olduğunu ölçeceğiz.
- Şimdilik yalnızca **altyapıyı** hazırladık. Hangi yazılı talimatın (istemin) kullanılacağı danışmanın kararı.
- Altyapının üç parçası var:
  - **Ortak arayüz:** Kod hangi modelle konuştuğunu bilmek zorunda değil. Model Gemini (Google'ın ücretsiz katmanı) ya da kendi bilgisayarımızda çalışan Ollama olabilir.
  - **Önbellek:** Her cevap bir dosyaya yazılıyor. Deneyi tekrar çalıştırınca aynı soru için internete tekrar gidilmiyor. Bu, ücretsiz kotayı korur ve sonuçları tekrarlanabilir yapar.
  - **Örneklem:** Ücretsiz kotalar yüzünden bütün tekrarlar yerine seçilmiş 150 tekrar kullanılacak. Seçim her kişiden ve her hata türünden eşit sayıda tekrar alacak şekilde yapıldı.

*Jargon:* **LLM:** büyük dil modeli. **İstem (prompt):** modele verilen yazılı talimat. **Tabakalı örneklem:** gruplara (tabakalara) ayırıp her gruptan belirli sayıda seçmek. **Sıcaklık (temperature) = 0:** modelin her seferinde aynı cevabı vermeye en yakın ayarı.

## Yapılanlar (altyapı, Güncelleme 08)
- `cekirdek/llm.py`:
  - `Istek` / `Yanit`; sıcaklık varsayılanı 0.
  - `GeminiSaglayici` (REST `generateContent`; anahtar `GEMINI_API_KEY` ortam değişkeninden ya da git'e girmeyen `.env` dosyasından), `OllamaSaglayici` (yerel, `localhost:11434`), `SahteSaglayici` (testler, ağ yok).
  - `Onbellek`: `sonuclar/deney4/onbellek.jsonl`, `.gitignore`'da. Anahtar, isteğin bütün parçalarının SHA-256'sı.
  - `LLMIstemcisi`:
    - önbellek;
    - istekler arası en kısa bekleme (dakikalık sınır için);
    - 429/5xx/bağlantı hatasında yeniden deneme: sağlayıcının önerdiği süre (`Retry-After` ya da Gemini `retryDelay`), yoksa üstel bekleme;
    - boş yanıt ve kalıcı hata önbelleğe yazılmaz.
  - Model adı kodda sabit değil; güncel ücretsiz model ve sınırlar Adım 8'de resmi sayfadan kontrol edilecek.
  - Yeni paket yok (standart kütüphane `urllib`); `requirements.txt` notu güncellendi.
- `deneyler/deney4_orneklem.py`: Deney 3 tablosundan (`sonuclar/deney3/cumleler.csv`) yalnızca önden + çapraz tekrarlar alınır. 50 doğru + her hata türünden 20 = 150 tekrar seçilir, tohum 0. Tabaka = **sınıf × kişi**: her kişiden 10 doğru ve hata türü başına 4 tekrar. Çıktı: `sonuclar/deney4/orneklem.csv`, `orneklem_ozet.csv`.
- `testler/test_llm.py` (ağ kullanmaz):
  - önbellek: ikinci istekte ve dosyadan yeni istemcide ağa gidilmiyor;
  - anahtarın isteğin her parçasına bağlı olması;
  - yeniden deneme ve bekleme süreleri, deneme hakkının bitmesi;
  - kalıcı hatanın ve boş yanıtın önbelleğe girmemesi;
  - en kısa aralık;
  - Gemini ve Ollama istek gövdeleri ve Gemini yanıt çözümlemesi ("düşünce" parçaları atılır);
  - eksik anahtar uyarısı, `.env` okuma;
  - örneklemin tabakalı ve tekrarlanabilir olması.

## Sonuçlar (altyapı, Güncelleme 08)
Örneklem (`python -m deneyler.deney4_orneklem` çıktısından):

| tabaka | Honza | Mima | Petra | Terka | Vasil | toplam |
| --- | --- | --- | --- | --- | --- | --- |
| az kaldırma | 4 | 4 | 4 | 4 | 4 | 20 |
| baş | 4 | 4 | 4 | 4 | 4 | 20 |
| dirsek | 4 | 4 | 4 | 4 | 4 | 20 |
| doğru | 10 | 10 | 10 | 10 | 10 | 50 |
| omuz | 4 | 4 | 4 | 4 | 4 | 20 |
| öne kaçma | 4 | 4 | 4 | 4 | 4 | 20 |
| toplam | 30 | 30 | 30 | 30 | 30 | 150 |

## Kararlar ve sapmalar (altyapı, Güncelleme 08)
- **Tabaka = sınıf × kişi** (PLAN yalnızca "tabakalı" diyor). İlk denemede yalnızca sınıfa göre tabakalandırdım; öne kaçmanın 20 tekrarından 10'u Vasil'den, 1'i Petra'dan geldi. Kişi dengesi için tabakaya kişiyi de ekledim. Bu seçim yalnızca örneklemin bileşimine bakılarak yapıldı; hiçbir LLM sonucu yoktu. Danışman farklı bir tabaka isterse tek satırla değişir.
- Örneklem birimi Deney 3'teki gibi (satır, kamera) tekrarıdır. Aynı hareketin iki kamerası ayrı tekrar sayılır. Danışmana soru: aynı hareketin iki görüşü birlikte seçilebilsin mi?

## Açık sorular / danışmana notlar (altyapı, Güncelleme 08)
- ~~İstem metinleri, girdi biçimi ve model~~ → Karar 36 (yukarıda).
- Ollama için yerel model seçimi ve Türkçe kalitesi henüz denenmedi.
- Kullanıcı Google AI Studio'dan ücretsiz bir `GEMINI_API_KEY` alacak (Karar 35).
