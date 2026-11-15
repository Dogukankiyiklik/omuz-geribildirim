# Sunum demosu

Demo, slaytlar bittikten sonra **veri setindeki bir videoyla** yapılır. Üç yol var; sırayla denenir, birincisi çalışmazsa ikincisine geçilir. Komutlar proje kökünde, sanal ortam açıkken (`.venv\Scripts\activate`) çalıştırılır. Hepsi sunumdan önce aynı bilgisayarda ve aynı ekran çözünürlüğünde bir kez denenmeli.

## Hazırlık (sunumdan önce, bir kez)
- [ ] Bilgisayar prize takılı, pil tasarrufu kapalı (MediaPipe yavaşlamasın).
- [ ] Şu dosyalar yerinde (git'e girmezler, yalnızca bu bilgisayarda):
  - `veri/rehab26/videos.zip` (veri setinin videoları),
  - `sonuclar/sunum/demo_yedek_veriseti.mp4` (yedek video),
  - `modeller/pose_landmarker_full.task` (MediaPipe modeli; yoksa ilk çalıştırmada internetten indirilir).
- [ ] 1. yolu bir kez baştan sona çalıştır. İlk açılışta kalibrasyon hazırlanırken yaklaşık 1 dakika beklenir; profil `profiller/veriseti_ex1_Honza_cam1_o0.npz` olarak kaydedilir ve sunumdaki açılış hızlı olur.
- [ ] Yedek videoyu oynatacak bir oynatıcı (Windows Medya Oynatıcı ya da VLC) açılıp denenmiş olsun.

## 1. Veri setindeki video (birincil)
```bash
python -m uygulama.main --veri-seti ex1_Honza --kamera cam1 --yonelim 0
```
- **Ne görülür:** solda video ve iskelet, sağda panel. Her tekrar bitince o tekrar yeniden oynatılır: turkuaz referans iskelet ile kişinin iskeleti üst üste, normal aralığın dışına çıkan uzuv kırmızı. Panelde karar (DOĞRU / HATA), Türkçe cümle ve altında omuz eğrisi ile normal aralık (gri) görünür.
- **Kalibrasyon:** videodaki doğru etiketli tekrarlardan (1, 2, 3, 9, 10) otomatik kurulur. Bu tekrarların kararı adil bir sınama olmadığı için onların üzerinde durulmaz.
- **Gösterilecek tekrarlar** (uygulamanın bu videodaki çıktısı: `sonuclar/uygulama_saglik/ex1_Honza_cam1_o0_tekrarlar.csv`):
  - 5. tekrar, **omuz silkmesi** → "Kolunu kaldırırken sağ omzunu kulağına doğru yaklaşık 5 derece kaldırdın. Omzunu aşağıda ve gevşek tut. …"
  - 6. tekrar, **baş eğme** → "Kolun yukarıdayken başını yaklaşık 20 derece yana eğdin. Başını dik tut, karşıya bak. …"
  - 7. tekrar, **kolu az kaldırma** → "Kolunu 115 dereceye kadar kaldırdın; normalde 150 dereceye çıkıyorsun. Kolunu yaklaşık 35 derece daha yukarı kaldır. …"
  - 8. tekrar, **dirsek bükme** → "Kolun yukarıdayken dirseğini yaklaşık 30 derece büktün. Kolunu düz tut. …"
  - Süre kısıtlıysa 5. tekrarın oynatımından sonra **Q** ile çıkmak yeterli.
- **Dikkat:** 4. tekrar veri setinde "kolun öne kaçması" etiketli, uygulama "doğru" diyor. Üzerinde durulmaz; sorulursa tek kamerada derinlik olmadığı için öne kaçmanın her zaman görülemediği söylenir (sınırlılık).
- Hatalı tekrarlarda ikinci bir hata da söylenebilir ("Ayrıca kolun öne kaçtı…"); en büyük hata önce söylenir.
- **Tuşlar:** Boşluk duraklat, R son tekrarı yeniden oynat, U uzman ayrıntısı, Q / Esc çıkış. Tuşlar yalnızca pencere seçiliyken çalışır; önce pencereye bir kez tıklanır.

**Sorun çıkarsa**

| Sorun | Ne yapılır |
| --- | --- |
| Pencere açılmıyor / hata mesajı | Hemen 2. yola geçilir. |
| `videos.zip` bulunamadı | 2. yol. |
| Pencere ekrandan taşıyor ya da çok küçük | Pencere kenarından boyutlandırılır; olmazsa 2. yol. |
| Çok yavaş oynuyor (MediaPipe) | Q ile çıkılır, 2. yola geçilir. |
| Tuşlar çalışmıyor | Pencereye bir kez tıklanır; panelin altındaki düğmelere fareyle de basılabilir. |

## 2. Yedek: `sonuclar/sunum/demo_yedek_veriseti.mp4`
- Video oynatıcıda açılır. Yaklaşık 25 saniye; aynı videodan 5–7. tekrarlar ve oynatımları. Uygulamanın kendi çizim koduyla üretildi.
- Açılmazsa VLC ile denenir; olmazsa 3. yol.

## 3. Son yedek: ekran görüntüleri
Slaytlardaki iki görüntü zaten veri setinden: `sonuclar/sunum/4_geri_bildirim.png` (uygulama ekranı) ve `5_bindirme.png` (bindirme). Demo hiç çalışmazsa bunlar üzerinden anlatılır.

## Kendi kaydınla (isteğe bağlı)
Kendi videonla denemek istersen: `python -m uygulama.main --profil profiller/kisi1.npz --video veri/kendi_kayit/kisi1/test.MOV` (profil yoksa [`YENIDEN_KURULUM.md`](YENIDEN_KURULUM.md), 5. bölüm). Sunumda veri setindeki video kullanılıyor.
