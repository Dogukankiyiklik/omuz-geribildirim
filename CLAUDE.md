# CLAUDE.md — Claude Code için proje kuralları

Bu dosyayı her oturumun başında oku. Sonra `PLAN.md`'de sıradaki adımı bul ve yalnızca o adım üzerinde çalış. Hocanın ödev şartları `docs/ODEV.md` dosyasında; her adımda bunlara uyduğunu kontrol et. `ilerleme/` altında okunmamış bir `GUNCELLEME_XX.md` varsa önce onu oku.

## Proje bir paragrafta

Tek bir RGB kamerayla **kolu yana kaldırma (omuz abdüksiyonu)** egzersizini izleyen bir sistem. Sistemin dört işi var:

1. Hatalı tekrarları bulmak; odak **omuz silkmesi** (omzun kulağa doğru kalkması).
2. Hatanın türünü belirlemek: omuz, baş eğme, kolun öne kaçması, dirsek bükme veya yetersiz kaldırma.
3. Kişiye **Türkçe, ne yapacağını söyleyen bir cümle** vermek.
4. Bütün bunları açık bir veri setinde (REHAB26-ViewAngles) sayılarla ölçmek.

Yöntemin temeli **kişiye özel tolerans bandı**: kişinin birkaç doğru tekrarı DTW ile hizalanır ve her an için bir "normal aralık" çıkarılır. Yöntem M39'dan alınmıştır. Ayrıntılı arka plan: `docs/ARKA_PLAN.md`.

Bu bir ders projesi; sunum 16 Kasım 2026'da. Proje ayrıca bildiriye dönüştürülebilir olmalı, bu yüzden deneylerin dürüst ve tekrarlanabilir olması önemli.

## Kullanıcı hakkında

- Kullanıcı konuya yeni ve sistemi hocasına **kendisi anlatacak**. Her adımın sonunda yaptığını **basit Türkçe** ile, jargonu açıklayarak anlat.
- Kullanıcı deneyleri **kendisi çalıştırıp sonuçları görmek** istiyor. Uzun deney çalıştırmalarının son halini kullanıcıya bırak: komutu ver, ne kadar süreceğini ve çıktının nasıl okunacağını söyle. Kısa testleri (pytest, hızlı kontroller) sen çalıştırabilirsin.
- Kullanıcı her adımın özetini ayrı bir Claude sohbetine (proje danışmanı) götürüyor. Bu yüzden ilerleme kaydı zorunlu; aşağıya bak.

## İlerleme kaydı (zorunlu)

Her adım bittiğinde `ilerleme/ADIM_XX.md` dosyasını `ilerleme/_SABLON.md`'deki şablona göre yaz. XX, PLAN.md'deki adım numarasıdır.

- **Sonuçlar:** Sayılar terminal çıktısından veya sonuç dosyasından **kopyalanır**, asla tahmin edilmez ya da yuvarlanarak uydurulmaz.
- **Sapmalar:** PLAN.md'den sapma, belirsizlik veya kendi verdiğin kararlar "Kararlar ve sapmalar" bölümüne yazılır.
- **Ortak kararlar:** Birden fazla adımı etkileyen kararları ayrıca `ilerleme/KARARLAR.md` dosyasına tek satır olarak ekle.

Adım bitmeden sonraki adıma geçme. Bir adımın kabul ölçütü sağlanamıyorsa dur, sebebi ADIM dosyasına yaz ve kullanıcıya söyle.

## Kod kuralları

- Python 3.11, sanal ortam `.venv`. Bağımlılıklar `requirements.txt` dosyasında; yeni paket eklersen oraya da yaz.
- **Ortak çekirdek:** Ölçütler, hizalama, bant, hata türü ve geri bildirim kodu yalnızca `cekirdek/` altında yaşar. Deneyler (`deneyler/`) ve uygulama (`uygulama/`) bu kodu **içe aktarır, kopyalamaz.** Uygulamanın verdiği karar, deneyde ölçtüğümüz karar ile aynı kod olmalı.
- **Davranış koruma:** `referans/deney1_omuz_olcutleri.py` çalışan ve sonuçları doğrulanmış referans koddur. Çekirdek bu koddan türetilir ve `referans/beklenen_deney1_ozet.csv` sonuçlarını **±0,01 içinde** yeniden üretmek zorundadır (Adım 1'deki test). Çekirdekte yapılan her değişiklikten sonra bu test tekrar çalışmalı.
- **İsimlendirme:** Türkçe, ASCII karakterli isimler (`ozellikler`, `bant_modeli`, `kol_acisi`). Bu, mevcut kodla uyumlu. Yorumlar ve kullanıcıya dönük metinler Türkçe.
- **Tekrarlanabilirlik:** Rastgelelik içeren her yerde tohum (`seed`) parametre olarak alınır, varsayılan 0'dır.
- **Sonuç dosyaları:** Sonuçlar `sonuclar/<deney_adi>/` altına yazılır: CSV (ham sonuçlar), `ozet.csv` (tablo) ve gerekirse PNG.
- **Testler:** `testler/` altında pytest. En azından çekirdek fonksiyonları ve Deney 1 regresyonu için birer test olmalı.
- **Veri:** `veri/` klasörü git'e girmez (`.gitignore`). Veri dosyalarını asla silme veya üzerine yazma.

## Deney dürüstlüğü (önemli)

- **Eşik ayarı:** Bir eşik, ağırlık veya parametre ayarlanacaksa **birini-dışarıda-bırak (kişi bazlı)** yapılır: 4 kişide ayarla, 5. kişide test et, her kişi için tekrarla. Test kişisinin verisi ayarlamaya asla girmez.
- **Adil model:** Bant modeli bir tekrarı değerlendirirken o tekrar modele dahil edilmez. Doğru ve hatalı tekrarlar **aynı sayıda** doğru tekrardan kurulan modelle değerlendirilir (referans kodda yapıldığı gibi).
- **Raporlama:** Kötü veya beklenmedik sonuçları gizleme; olduğu gibi raporla. Sonuç beklentiye uymuyorsa önce hata ara, bulamazsan sonucu yaz.
- **Belirsizlik:** Sadece 5 kişi var. Önemli farklar için kişi bazlı bootstrap güven aralığı ver (referans koddaki gibi).

## Veri hakkında hızlı bilgiler

- **Ana kaynak:** `veri/rehab26/` altındaki orijinal Zenodo dosyaları. `jointSequences-mediapipe.zip` içinde dosyalar `mediapipe/<ex>/<ex>_<kişi>_cam<1|2|3>_<2d|3d>.npy` biçiminde, her biri `(kare, 33, 4)` float64. Videolar `videos.zip` içinde, `videos/<ex>/<ex>_<kişi>_cam<1|2|3>.mp4`, 30 FPS. Segmentasyon kare numaraları bu videolara göredir. MediaPipe v0.10.20, Full model.
- **2B / 3B:** `_2d`: x, y görüntü koordinatı (Zenodo "piksel" diyor; danışmanın gördüğü değerler 0–1, Adım 0'da netleştir); z, MediaPipe'ın göreli derinlik tahmini; son sütun görünürlük. `_3d`: kalça ortası merkezli, metre cinsinden "world landmarks". Biz 2B kullanıyoruz.
- **Yardımcı dosya:** `veri/rehab26_kucuk.npz`, danışmanın kullandığı küçültülmüş kopya. Yalnızca regresyon karşılaştırması için. Anahtar biçimi `"{video_id}|{kamera}|2d|veri|satir{N}|rep{R}|o{yonelim}"`. N, `Segmentation.csv` içindeki **satır indeksi** (0'dan başlar, başlık hariç); etiketlerle eşleştirme bu numarayla yapılır.
  - Her değer `(kare, 13, 4)` float16 dizisidir. Son eksen: x, y (görüntüye göre 0–1), z, görünürlük.
  - 13 eklem sırası, MediaPipe indeksleriyle: `[0 burun, 2 sol göz, 5 sağ göz, 7 sol kulak, 8 sağ kulak, 11 sol omuz, 12 sağ omuz, 13 sol dirsek, 14 sağ dirsek, 15 sol bilek, 16 sağ bilek, 23 sol kalça, 24 sağ kalça]`.
  - Her tekrarın başında ve sonunda 10 kare pay vardır, yani ilk kareler dinlenme halidir.
  - `__meta__` anahtarı JSON meta veridir.
- **Egzersizler:** `ex1` = kol abdüksiyonu (**sağ kol** egzersiz yapıyor), `ex7` = omuz ekstansiyonu. Squat dosyada yok.
- **En-boy:** x ve y ayrı ayrı normalize edilmiş. Açı veya mesafe hesaplamadan önce `x *= 9/16` yapılır; videolar dikey telefon videosu (tahmin: 0,62, kullanılan: 0,5625).
- **Görüş açısı:** `kamera_konumu - yonelim`, kamera konumları `cam1=0`, `cam2=45`, `cam3=90`. Mutlak değere göre üç grup: önden 0–20°, çapraz 30–60°, profil 70–90°.
- **Etiketler:** `correctness_score` 1 = doğru, 5 = yanlış. `error_description` birincil hatayı, `additional_errors` ek hataları verir. Hata kodları `veri/Error_types.csv` dosyasında.

## Yapılmayacaklar

- Sonuç uydurmak, tahmini sayı yazmak.
- Test kişisinin verisiyle eşik ayarlamak.
- Çekirdeği deney veya uygulama içine kopyalamak.
- Kullanıcıya sormadan PLAN.md'deki kapsamı değiştirmek. Değişiklik gerekiyorsa öner ve ADIM dosyasına yaz.
- Ücretli API kullanmak (LLM için yalnızca Gemini ücretsiz katmanı veya yerel Ollama).
