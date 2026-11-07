# Güncelleme 10 — 7 Kasım 2026 akşamüstü (danışmandan)

Claude Code: `/clear` sonrası yeni oturum. Sırayla oku:
1. `CLAUDE.md`
2. `PLAN.md`
3. `ilerleme/KARARLAR.md`
4. `ilerleme/ADIM_06.md` (Ek: Güncelleme 09 dahil)
5. `ilerleme/ADIM_08.md`
6. `ilerleme/ADIM_09.md`
7. `docs/GELECEK_CALISMA.md`
8. bu dosya

Kararları (41–46) `KARARLAR.md`'ye işle. `PLAN.md`'deki durum işaretlerini güncelle (Adım 8 ✅; Adım 7 çekim bekleniyor; Adım 9 hazırlık tamam). Adım 8, 9, 6b ve 10'un altına bu güncellemenin kısa notunu ekle.

**Bağlam:** Kullanıcı bilerek iki işi bekletiyor: Adım 7 çekimi (bugün) ve Adım 9'un tam yeniden üretimi (dondurmada). Bu güncelleme ikisine de dokunmaz. Video gelince önce Adım 7 yapılır.

## Değerlendirme
- **Adım 8 çok iyi yapıldı.** Önceden kayıt, pilotta istemi değiştirmemek, 2.5 Flash yanıtlarını raporlamamak, üslup metriğindeki "bu yüzden" hatasını açıkça yazmak ve çıkarıcının hatalarını kendinden saklamamak tam istenen şeydi.
- **Model değişikliği kabul:** Lite olmayan bütün Flash modellerinde günlük sınır 20; Karar 36'nın yedek kuralı doğru uygulandı. Raporda şöyle yazılır: "Ücretsiz katmanın günlük sınırı nedeniyle gemini-3.5-flash-lite; düşünme ayarı varsayılan." ADIM_08'deki açık soru da kapandı: düşünme varsayılan kalır.
- **Adım 6'daki iki bulgu** (öne kaçma–dirsek karışması, baş eğmesinin omuz ölçütünü etkilemesi) kullanıcının gözleminden çıktı ve doğru biçimde gelecek çalışmaya yazıldı. Sunumda "sınırlılık" olarak anılacak.

## Kararlar

### Karar 41 — Deney 4'ün yorumu ve iddia kapsamı (Karar 20 ve 23'e ek)
| İddia | Kanıt | Güç |
| --- | --- | --- |
| LLM'e yalnızca cümle yazdırmak (B), kural tabanlı kararı korur ama üstünlük getirmez | Katı 61 / 61 (GA 0–0), ilk iki 73 / 74; B 17/150 cümlede yasaklanan "gövde boyu"nu kullandı; yer yer anlamsız talimat ("dirseğini daha fazla aç") | **Orta.** Kural tabanlı ana yöntem kararını (5 Kas) destekler. |
| Hatayı LLM'e buldurmak (C), doğru hatayı daha az söyler ve doğru tekrarda daha çok uyarır | Katı −16 (GA −26 – −5), gereksiz uyarı +8 (GA 2 – 14) | **Orta.** M21'deki bulguyla tutarlı; tek model, tek istem. |
| C, P1'in "fiziksel büyüklük" şartını çoğunlukla karşılamaz | Sayı içeren cümle: A 94, B 87, C 11 /100 | **Betimsel, ama sunum için güçlü bir örnek.** |
| LLM sayı uydurur (beklenti 3) | B 1/150, C 0/150 | **Tutmadı.** C sayıyı az kullandığı için uydurma da az. Olduğu gibi raporlanır. |
| Çıkarıcı LLM cümlelerini de okuyabilir | Körlemesine 45/45; ama B'nin tam okumasında 150'de 13 hata, hepsi "kaldır" kalıbında | **Makul ama kusursuz değil.** Karar 42'deki duyarlılık analizi bu sınırı ölçer. |
- Kullanıcının "hasta gözüyle" notları (çelişkili övgü, anlamsız derece, "gövde boyu" kafa karışıklığı) betimseldir ve sunumda örnek olarak kullanılabilir. "Derece bana anlam ifade etmiyor" notu Karar 28 ile çelişmez, ama sınırlılık olarak yazılır: hasta için derecenin anlamı belirsiz olabilir; hocanın P1 şartı derece istiyor.

### Karar 42 — Deney 4 duyarlılık analizi: "az kaldırma" için körlemesine insan etiketi (önceden kayıt)
**Neden:** Çıkarıcının bilinen hatalarının hepsi "kaldır" kalıbında. Bu kalıp, C'nin düşük katı değerini ve B'nin fazladan uyarısını etkiliyor olabilir. Birincil sonuç değişmez; yanına bir duyarlılık analizi eklenir.

**Seçim:** A, B ve C'nin 450 cümlesinden, şu düzenli ifadeye (büyük/küçük harf duyarsız) uyan **bütün** cümleler: `kald|kalk|yüks|yukarı`. Seçim yalnızca metne dayanır; koşula ya da sonuca dayanmaz.

**Etiketleme:**
- Cümleler karışık sırayla, koşul ve gerçek etiket gizli olarak `sonuclar/deney4/elle_kaldirma.xlsx` dosyasına yazılır (tohum 3).
- Tek soru: "Bu cümle, kolun **yeterince kaldırılmadığını / daha yukarı kaldırılması gerektiğini** bir hata olarak söylüyor mu? (1 = evet, boş = hayır)."
- Etiketleme talimatına şu not eklenir: "Doğru tekrarı öven 'kolunu 145 dereceye kaldırdın' gibi cümleler hayır. Başka bir hatanın düzeltmesi içinde geçen 'kolunu yana kaldır' gibi ifadeler de, kolun az kalktığını söylemiyorsa hayır."
- Anahtar ayrı dosyada; kullanıcı açmaz.

**Analiz:**
- Her cümlede, çıkarıcının listesindeki "az kaldırma" varlığı insan etiketiyle değiştirilir; diğer hata türleri çıkarıcıdan kalır. Seçilmeyen cümlelerde çıkarıcının listesi aynen kullanılır.
- Bu düzeltilmiş listelerle **sıradan bağımsız** metrikler yeniden hesaplanır: ilk iki, hatalılarda olumlu cümle, doğrularda gereksiz uyarı, sadakat (küme), eklenen ve atlanan hata.
- **Katı yeniden hesaplanmaz**, çünkü sıra insan etiketinden çıkmaz. Yalnızca insanın "hayır" dediği ve çıkarıcının ilk sırada "az kaldırma" bulduğu cümlelerin sayısı koşul başına raporlanır.
- Ayrıca çıkarıcı ile insanın "az kaldırma" uyumu koşul başına verilir (evet/evet, evet/hayır, hayır/evet, hayır/hayır).
- Bootstrap: Deney 4 ile aynı (2000 tekrar, tohum 1), B − A ve C − A için.

**Raporlama:** Birincil tablo (ADIM_08) değişmez. Duyarlılık tablosu yanına konur. Sonuç ne olursa olsun yazılır; sözlük yine **değiştirilmez**.

**Zamanlama:** Bu iş Adım 7'den sonra gelir. Kullanıcı etiketlemeyi dondurmadan önce istediği zaman yapar (tahmini 20–30 dakika). Dondurmaya kadar yapılmazsa yapılmamış olarak not edilir.

### Karar 43 — Depo temizliği ve güvenlik denetimi
- **Gizli bilgi denetimi:** `.env` dosyası `.gitignore`'da mı ve hiç commit'lenmiş mi? `git log --all -p` içinde `GEMINI_API_KEY=`, `AIza` ya da anahtara benzeyen bir dizi var mı? Varsa kullanıcıya hemen söyle, anahtarın Google AI Studio'dan iptal edilip yenisinin alınmasını öner ve geçmişin nasıl temizleneceğini anlat. Kendi başına geçmişi yeniden yazma.
- **Veri:** `veri/`, `profiller/`, `oturumlar/`, `veri/kendi_kayit/` ve videoların git'te olmadığını doğrula. Kullanıcının yüzünün göründüğü videolar ve canlı oturum dosyaları depoya girmez. `sonuclar/sunum/demo_yedek_veriseti.mp4` de girmez (veri seti CC BY-NC; ayrıca boyut).
- **`README.md`** (kök dizinde, kısa): projenin bir paragrafı, hızlı başlangıç (kurulum + demo komutu), klasör yapısı, `docs/YENIDEN_KURULUM.md`'ye bağlantı, veri seti atıfı ve lisans notu (REHAB26-ViewAngles, Zenodo 10.5281/zenodo.23018128, CC BY-NC 4.0; veri depoda yok). Kod için lisans seçimi kullanıcıya sorulur; seçilmezse "lisans belirtilmedi" yazılır.
- Bulunanlar ADIM_09'a yazılır.

### Karar 44 — Sunum şekillerinde küçük düzeltmeler (yalnızca görsel)
- `3_kalibrasyon.png`: Ortadaki çubuğun "0,62" yazısı en alttaki kişi noktasını (~0,37) örtüyor. Değer yazısı çubuğun üstüne taşınır ya da noktalar yazının önüne çizilir.
- `1_problem.png` ve `3_kalibrasyon.png` "tüm görüşler" sayılarını kullanıyor; bu tutarlı ve temkinli bir seçim, değişmez. Altyazıya "önden + çapraz: ham 0,xx → bant 0,97" eklenir; sayılar `deney1b` ya da `deney1_v2` CSV'lerinden okunur.
- Başka değişiklik yapılmaz. Hangi şeklin slayta gireceğine sunum hazırlığında karar verilecek.

### Karar 45 — İsteğe bağlı adımlar
- **6b (siluet):** Yalnızca **süre tahmini** yapılır (Karar 39). MediaPipe'ın segmentasyon maskesi (`output_segmentation_masks=True`), Ex1'in 3 videosunda çalıştırılır ve süresi ölçülür. Ardından önden + çapraz için gereken toplam süre ve disk alanı tahmin edilir. Hiçbir ölçüt ya da deney yazılmaz. Sonuç ADIM_09'un sonuna (ya da kısa bir `ADIM_06b.md`'ye) yazılır. Başlayıp başlamamaya danışman Adım 7 sonuçlarıyla birlikte karar verecek.
- **10 (REHAB24-6): yapılmaz.** Gerekçe: Veri setinde yalnızca doğru/yanlış etiketi var; omuz silkmesi için kullanıcının saatlerce elle etiketleme yapması gerekiyor. Takvime sığmaz. `GELECEK_CALISMA.md`'ye "başka bir veri setinde, görülmemiş kişilerde doğrulama" maddesi olarak yazılır. PLAN'da ⛔ ile işaretlenir.

### Karar 46 — Sıra
1. Bu güncellemedeki küçük işler: Karar 43, 44 ve 45'in süre tahmini; Karar 42'nin etiketleme dosyası ve analiz kodu (`--sahte` testleriyle).
2. Kullanıcının videoları gelince Adım 7 (her şeyden önce).
3. Kullanıcı istediği zaman Karar 42 etiketlemesini yapar; analiz çalıştırılır.
4. Danışman Adım 7 ve 6b süre tahminine bakar: 6b'ye girilip girilmeyeceğine karar verir (Güncelleme 11).
5. 13 Kasım: dondurma (Adım 9). Sunum ve rapor ondan sonra.

## Yapılacaklar
1. Karar 43: denetim, `README.md`. Bulguları ADIM_09'a yaz.
2. Karar 44: şekil düzeltmesi; `python -m deneyler.sunum_sekilleri` yeniden çalıştır.
3. Karar 42: `deneyler/deney4.py`'ye `kaldirma-uret` ve `kaldirma-degerlendir` alt komutları, testler. Önceden belirlenenleri ADIM_08'in sonuna "Ek: Güncelleme 10 — duyarlılık analizi (önceden kayıt)" başlığıyla yaz ve **etiketleme dosyasını üretmeden önce** commit'le. Ardından dosyayı üret ve kullanıcıya kısa bir talimatla ver: kaç cümle olduğu, tahmini süre ve tek sorunun ne olduğu.
4. Karar 45: 6b süre tahmini (3 video); REHAB24-6 için GELECEK_CALISMA maddesi ve PLAN işareti.
5. `pytest` geçmeli. Bitince kısa bir özet ver: ne yapıldı, kullanıcının yapacakları (çekim, Karar 42 etiketlemesi), bana gönderilecekler (ADIM_09'un yeni bölümü, 6b süre tahmini, Adım 7 sonuçları geldiğinde ADIM_07).
