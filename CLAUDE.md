# CLAUDE.md — Claude Code için proje kuralları

Bu bir **ders ödevi** (Bilgisayarlı Görü ara sınav projesi; sunum 16 Kasım 2026, ardından 1 sayfalık rapor). Bildiri hedefi bırakıldı. Yöntem **donduruldu**; geliştirme adımları (eski `PLAN.md`) bitti.

Her oturumun başında oku:
- `docs/ODEV.md`: hocanın şartları ve bizdeki karşılıkları,
- `docs/SISTEM.md`: sistem nasıl çalışıyor,
- `docs/DENEYLER.md`: neyi test ettik, ne bulduk.

## Proje bir paragrafta

Tek bir RGB kamerayla **kolu yana kaldırma** egzersizini izleyen bir uygulama. Hatalı tekrarları bulur (odak: **omuz silkmesi**), hatanın türünü belirler (omuz, baş eğme, kolun öne kaçması, dirsek bükme, yetersiz kaldırma) ve kişiye **Türkçe, derece içeren, ne yapacağını söyleyen bir cümle** verir. Yöntemin temeli **kişiye özel açı bandı**: kişinin 6 doğru tekrarından, kol açısının her 5°'lik kutusu için ölçülerin normal aralığı (μ ± τ) çıkarılır. Puanlamada DTW **yoktur**; DTW yalnızca bindirmede (referans iskeletin zamanda hizalanması) kullanılır.

## Kullanıcı hakkında

- Kullanıcı konuya yeni ve sistemi hocasına **kendisi anlatacak**. Yaptığını **basit Türkçe** ile, jargonu açıklayarak anlat.
- Uzun deney çalıştırmalarını kullanıcıya bırak: komutu, süresini ve çıktının nasıl okunacağını söyle. Kısa kontrolleri (pytest, içe aktarma) sen çalıştırabilirsin.
- Kullanıcı yaptığın işin özetini ayrı bir Claude sohbetine götürebilir. Bir iş bitince ne değiştiğini, hangi dosyalara dokunduğunu ve sayıların kaynağını kısa bir özetle söyle.

## Kapsam

- Yöntem donduruldu. Puanlamayı, eşikleri veya karar kuralını değiştirme. Değişiklik gerekiyorsa önce öner, kullanıcı onaylasın.
- `arsiv/` altındakiler ödevin parçası değil. Buraya dokunma; buradan kod içe aktarma. Gerekirse eski çalışır hâl `v-sunum` etiketinde.
- Yeni deney ekleme. Sunum ve rapor için yalnızca mevcut sonuç dosyalarından sayı ve şekil üret.

## Kod kuralları

- Python 3.11, sanal ortam `.venv`. Bağımlılıklar `requirements.txt` dosyasında.
- **Ortak çekirdek:** ölçüler, bant, hata türü, geri bildirim ve bindirme kodu yalnızca `cekirdek/` altında yaşar. `uygulama/` ve `deneyler/` bu kodu **içe aktarır, kopyalamaz**. Böylece uygulamanın kararı, deneyde ölçülen kararla aynı koddan gelir.
- **Regresyon:** çekirdekte bir değişiklikten sonra `pytest -q` çalışmalı. `referans/beklenen_deney1_ozet.csv` sonuçları ±0,01 içinde yeniden üretilmeli (`testler/test_deney1_regresyon.py`).
- **İsimlendirme:** Türkçe, ASCII karakterli isimler (`ozellikler`, `aci_bandi`). Yorumlar ve kullanıcıya dönük metinler Türkçe.
- **Sayılar:** belgeye yazılan her sayı bir sonuç dosyasından **kopyalanır** ve yanına kaynağı yazılır. Tahmin edilmez, uydurulmaz.
- **Veri:** `veri/` git'e girmez. Veri dosyalarını asla silme veya üzerine yazma.

## Veri hakkında hızlı bilgiler

- **REHAB26-ViewAngles** (`veri/rehab26/`): `jointSequences-mediapipe.zip` içinde `mediapipe/<ex>/<ex>_<kişi>_cam<1|2|3>_2d.npy`, `(kare, 33, 4)`. Son eksen: x, y (görüntüye göre 0–1), z, görünürlük. MediaPipe v0.10.20, Full model. Videolar `videos.zip` içinde, 30 FPS.
- `Segmentation.csv`: tekrar başına başlangıç ve bitiş karesi, yönelim, `correctness_score` (1 doğru, 5 yanlış), `error_description` (birincil hata), `additional_errors` (ek hatalar).
- `ex1` = kolu yana kaldırma (**sağ kol** egzersiz yapıyor). Kullanılan tek egzersiz bu.
- **En-boy:** videolar dikey, açı veya mesafeden önce `x *= 9/16`. Uygulamada gerçek kare oranı kullanılır.
- **Görüş açısı** = `kamera_konumu − yonelim` (cam1 = 0, cam2 = 45, cam3 = 90). Üç grup: önden 0–20°, çapraz 30–60°, profil 70–90°. Ana sonuçlar önden + çapraz için.

## Yapılmayacaklar

- Sonuç uydurmak, tahmini sayı yazmak.
- Test kişisinin verisiyle eşik ayarlamak.
- Çekirdeği deney veya uygulama içine kopyalamak.
- Ücretli API kullanmak.
