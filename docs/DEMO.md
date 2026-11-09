# Sunum demosu (Karar 56)

Üç yol var; sırayla denenir. Birincisi çalışmazsa beklemeden ikincisine geç. Komutlar proje kökünde, sanal ortam açıkken (`.venv\Scripts\activate`) çalıştırılır. **Sunumdan önce üçünü de bir kez dene** (aynı bilgisayarda, aynı ekran çözünürlüğünde).

## Hazırlık (sunumdan önce, bir kez)
- [ ] Bilgisayar prize takılı; pil tasarrufu kapalı (MediaPipe yavaşlamasın).
- [ ] Şu dosyalar yerinde (git'e girmezler, yalnızca bu bilgisayarda):
  - `profiller/kisi1.npz` (kişi 1 profili),
  - `veri/kendi_kayit/kisi1/test.MOV`,
  - `sonuclar/sunum/demo_kisi1.mp4`,
  - `sonuclar/sunum/demo_yedek_veriseti.mp4`,
  - `modeller/pose_landmarker_full.task` (MediaPipe modeli; yoksa ilk çalıştırma internetten indirir).
- [ ] Profil ya da demo videosu yoksa yeniden üret (MediaPipe noktaları önbellekte, ~2 dk):
  ```bash
  python -m deneyler.sunum_sekilleri --kendi-kayit     # profiller/kisi1.npz, demo_kisi1.mp4, 4b_, 5b_
  ```
- [ ] Videoları oynatmak için bir oynatıcı (Windows "Medya Oynatıcı" ya da VLC) açılıp denenmiş olsun.

## 1. Canlı: kişi 1 profiliyle `test.MOV` (birincil)
```bash
python -m uygulama.main --profil profiller/kisi1.npz --video veri/kendi_kayit/kisi1/test.MOV
```
- **Ne görülür:** Solda video ve iskelet, sağda panel. Her tekrar bitince o tekrarın oynatımı (turkuaz referans iskelet + kullanıcı iskeleti, banttan çıkan uzuv kırmızı), panelde karar (DOĞRU / HATA) ve Türkçe cümle; altında omuz eğrisi ve normal aralığı (gri).
- **Ne zaman ne olur** (test videosunda tekrarın başlangıcı, saniye; `sonuclar/kendi_kayit/kisi1/tekrarlar.csv`):
  - 26 s: tekrar 4, **doğru** → "Hareketi doğru yaptın. Kolun yaklaşık 140 dereceye çıktı, …"
  - 41 s: tekrar 6, **az kaldırma** → "Kolunu 105 dereceye kadar kaldırdın; normalde 140 dereceye çıkıyorsun. …"
  - 49 s: tekrar 7, **omuz silkmesi** → "Kolunu kaldırırken sağ omzunu kulağına doğru yaklaşık 5 derece kaldırdın. …"
  - 77 s: tekrar 11, **baş sola** → "Kolun yukarıdayken başını yaklaşık 30 derece yana eğdin. …"
  - Sunum 5 dakika: tekrar 7'den (omuz) sonra **Q** ile çıkmak yeterli (~1 dk).
- **Tuşlar:** Boşluk = duraklat (anlatırken), R = son tekrarı yeniden oynat, U = uzman ayrıntısı (ölçülü cümle), Q / Esc = çıkış. Tuşlar ancak pencere seçiliyken çalışır: önce pencereye bir kez tıkla.
- **Dikkat:** Doğru bir tekrarın oynatımında da bir uzuv kısa süre kırmızı görünebilir: o karede bant dışı, ama tekrarın toplam hatası eşiği geçmediği için karar "doğru". Sorulursa böyle anlat.

**Ne olursa ne yapılır**
| Sorun | Ne yap |
| --- | --- |
| Pencere açılmıyor / hata mesajı | Hemen **2. yola** geç. |
| Pencere ekrandan taşıyor ya da çok küçük | Pencereyi kenarından boyutlandır; olmazsa 2. yol. |
| Çok yavaş oynuyor (MediaPipe) | Bekleme; Q ile çık, 2. yol (video aynı sonucu gösterir). |
| `profiller/kisi1.npz` bulunamadı | Hazırlıktaki komutla üret; zaman yoksa 2. yol. |
| Tuşlar çalışmıyor | Pencereye bir kez tıkla; panelin altındaki düğmelere fareyle de basılabilir. |
| Cümle beklenenden farklı | Olmamalı (aynı kod, aynı video; `demo_kisi1.mp4` ile aynı cümleler doğrulandı). Olursa anlatmaya devam et, sonra not al. |

## 2. Yedek: `sonuclar/sunum/demo_kisi1.mp4`
- Video oynatıcıda aç (çift tıkla). 45 s: tekrar 4 (doğru), 7 (omuz), 11 (baş sola), 6 (az kaldırma); her birinin önünde kısa bir başlık ("Tekrar 7 · gerçek etiket: omuz silkmesi"), ardından tekrar ve oynatımı.
- Uygulamanın kendi çizim koduyla, aynı profil ve aynı videodan üretildi; dört tekrarın cümlesi Adım 7 sonuç dosyasıyla birebir aynı.
- Duraklatıp cümleyi okumak için oynatıcının duraklatma tuşunu kullan.

**Ne olursa ne yapılır**
| Sorun | Ne yap |
| --- | --- |
| Dosya açılmıyor (kodek) | VLC ile aç; olmazsa 3. yol. |
| Dosya yok | `python -m deneyler.sunum_sekilleri --kendi-kayit` (~2 dk); zaman yoksa 3. yol. |

## 3. İkinci yedek: veri seti demosu
- **Önce dosya:** `sonuclar/sunum/demo_yedek_veriseti.mp4` (25 s; Honza, veri seti, tekrar 5–7 ve oynatımları).
- **Canlı istenirse** (veri setinden video, `videos.zip` gerekir; ilk açılış ~1 dk):
  ```bash
  python -m uygulama.main --veri-seti ex1_Honza --kamera cam1 --yonelim 0
  ```
  Kalibrasyon aynı videonun ilk doğru tekrarlarından kurulur; o tekrarların kararı adil bir sınama değildir (Karar 40).
- Hiçbiri olmazsa: `sonuclar/sunum/4_geri_bildirim.png` ve `5_bindirme.png` (veri seti) ya da `4b_` / `5b_` (kişi 1) ekran görüntüleriyle anlat.

## Anlatım için tek cümleler
- "Sistem kişinin kendi doğru tekrarlarından, kolun her açısı için omzun normal yerini öğreniyor; yeni tekrarda omuz bu aralığın dışına çıkınca söylüyor."
- "Kendi videomda 11 hatalı tekrarın 11'inde doğru hata cümlede geçti, 9'unda ilk söylenen oydu; 5 normal doğru tekrarın hiçbirinde uyarı çıkmadı." (Karar 51; tek kişi, bir işaret.)
