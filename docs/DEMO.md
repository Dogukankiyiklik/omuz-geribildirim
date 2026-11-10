# Sunum demosu

Üç yol var; sırayla denenir. Birincisi çalışmazsa ikincisine geçilir. Komutlar proje kökünde, sanal ortam açıkken (`.venv\Scripts\activate`) çalıştırılır. Üç yol da sunumdan önce aynı bilgisayarda ve aynı ekran çözünürlüğünde bir kez denenmeli.

## Hazırlık (sunumdan önce, bir kez)
- [ ] Bilgisayar prize takılı, pil tasarrufu kapalı (MediaPipe yavaşlamasın).
- [ ] Şu dosyalar yerinde (git'e girmezler, yalnızca bu bilgisayarda):
  - `profiller/kisi1.npz` (kişi 1 profili),
  - `veri/kendi_kayit/kisi1/test.MOV`,
  - `sonuclar/sunum/demo_kisi1.mp4`,
  - `sonuclar/sunum/demo_yedek_veriseti.mp4`,
  - `modeller/pose_landmarker_full.task` (MediaPipe modeli; yoksa ilk çalıştırmada internetten indirilir).
- [ ] Eksik olan varsa yeniden üretilir:
  ```bash
  python -m deneyler.sunum_sekilleri --kendi-kayit   # profiller/kisi1.npz, demo_kisi1.mp4, 4b_, 5b_ (~3–5 dk)
  python -m deneyler.sunum_sekilleri                 # demo_yedek_veriseti.mp4 ve 1–5 numaralı şekiller (~2 dk)
  ```
- [ ] Videoları oynatacak bir oynatıcı (Windows Medya Oynatıcı ya da VLC) açılıp denenmiş olsun.

## 1. Canlı: kişi 1 profiliyle `test.MOV` (birincil)
```bash
python -m uygulama.main --profil profiller/kisi1.npz --video veri/kendi_kayit/kisi1/test.MOV
```
- **Ne görülür:** solda video ve iskelet, sağda panel. Her tekrar bitince o tekrar yeniden oynatılır: turkuaz referans iskelet ile kullanıcı iskeleti üst üste, banttan çıkan uzuv kırmızı. Panelde karar (DOĞRU / HATA), Türkçe cümle ve altında omuz eğrisi ile normal aralığı (gri) görünür.
- **Ne zaman ne olur** (test videosunda tekrarın başlangıcı, saniye; `sonuclar/kendi_kayit/kisi1/tekrarlar.csv`, `bas_kare / 30`):
  - 26 s: tekrar 4, **doğru** → "Hareketi doğru yaptın. Kolun yaklaşık 140 dereceye çıktı, …"
  - 41 s: tekrar 6, **az kaldırma** → "Kolunu 105 dereceye kadar kaldırdın; normalde 140 dereceye çıkıyorsun. …"
  - 49 s: tekrar 7, **omuz silkmesi** → "Kolunu kaldırırken sağ omzunu kulağına doğru yaklaşık 5 derece kaldırdın. …"
  - 77 s: tekrar 11, **baş sola** → "Kolun yukarıdayken başını yaklaşık 30 derece yana eğdin. …"
  - Sunum 5 dakika olduğu için tekrar 7'den (omuz) sonra **Q** ile çıkmak yeterli (~1 dk).
- **Tuşlar:**
  - Boşluk: duraklat.
  - R: son tekrarı yeniden oynat.
  - U: uzman ayrıntısı.
  - Q / Esc: çıkış.

  Tuşlar yalnızca pencere seçiliyken çalışır; önce pencereye bir kez tıklayın.
- **Not:** doğru bir tekrarın oynatımında da bir uzuv kısa süre kırmızı görünebilir. O kare bandın dışındadır, ama tekrarın toplam hatası eşiği geçmediği için karar "doğru" çıkar.

**Sorun çıkarsa**

| Sorun | Ne yapılır |
| --- | --- |
| Pencere açılmıyor / hata mesajı | Hemen 2. yola geçilir. |
| Pencere ekrandan taşıyor ya da çok küçük | Pencere kenarından boyutlandırılır; olmazsa 2. yol. |
| Çok yavaş oynuyor (MediaPipe) | Q ile çıkılır, 2. yola geçilir (video aynı sonucu gösterir). |
| `profiller/kisi1.npz` bulunamadı | Hazırlıktaki komutla üretilir; zaman yoksa 2. yol. |
| Tuşlar çalışmıyor | Pencereye bir kez tıklanır; panelin altındaki düğmelere fareyle de basılabilir. |

## 2. Yedek: `sonuclar/sunum/demo_kisi1.mp4`
- Video oynatıcıda açılır. Sırayla tekrar 4 (doğru), 7 (omuz), 11 (baş sola) ve 6 (az kaldırma) oynar. Her birinin önünde kısa bir başlık var ("Tekrar 7 · gerçek etiket: omuz silkmesi"); ardından tekrar ve oynatımı gelir.
- Uygulamanın kendi çizim koduyla, aynı profil ve aynı videodan üretildi. Dört tekrarın cümlesi kendi kayıt sonuç dosyasıyla (`sonuclar/kendi_kayit/kisi1/tekrarlar.csv`) birebir aynı.

| Sorun | Ne yapılır |
| --- | --- |
| Dosya açılmıyor (kodek) | VLC ile açılır; olmazsa 3. yol. |
| Dosya yok | `python -m deneyler.sunum_sekilleri --kendi-kayit` (~3–5 dk); zaman yoksa 3. yol. |

## 3. İkinci yedek: veri seti demosu
- **Önce dosya:** `sonuclar/sunum/demo_yedek_veriseti.mp4`. Yaklaşık 25 s; veri setinden Honza, tekrar 5–7 ve oynatımları.
- **Canlı istenirse** (`videos.zip` gerekir; ilk açılış ~1 dk):
  ```bash
  python -m uygulama.main --veri-seti ex1_Honza --kamera cam1 --yonelim 0
  ```
  Kalibrasyon aynı videonun ilk doğru tekrarlarından kurulur; o tekrarların kararı adil bir sınama değildir.
- Hiçbiri çalışmazsa ekran görüntüleri kullanılır: `sonuclar/sunum/4_geri_bildirim.png` ve `5_bindirme.png` (veri seti) ya da `4b_*` / `5b_*` (kişi 1).
