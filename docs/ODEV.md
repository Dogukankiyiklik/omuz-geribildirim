# Ödev tanımı ve projedeki karşılıkları

Kaynak: hocanın verdiği Word dosyası, [`ODEV_asil.docx`](ODEV_asil.docx) ("Bilgisayarla Görü – Ara Sınav Projesi"; rapor şablonu, problem tanımları, kaynak rehberi). Bu belge onun özeti ve projedeki karşılıklarıdır; ikisi çelişirse Word dosyası geçerlidir. Sunum 16 Kasım 2026, 5 dakika. **Sunumdan sonra** 1 sayfalık rapor teslim edilir.

## Proje konusu
Videodan insan hareketlerinin ölçülmesi, karşılaştırılması ve kullanıcıya anlamlı geri bildirim üretilmesi. Üç problemden en az birini çözen **çalışan bir uygulama** isteniyor; birden fazlası seçilebilir. **Proje üçünü de kapsıyor.**

## Dikkat: ödev metni yoga diyor, proje omuz egzersizi yapıyor

Word dosyasında Problem 1'in başlığı "**Yoga** Hareketinin Doğruluğunun Ölçülmesi ve Doğal Dil Geri Bildirimi", Problem 3'ünki "Referans **Yoga** Hareketi ile Kullanıcı Hareketinin Aynı Video Üzerinde Çakıştırılması". İkisi de "doğru yoga hareketini gösteren bir referans video" ile kullanıcının videosunu karşılaştırmayı anlatıyor. Problem 2 ise doğrudan omuz/skapula ölçümü.

Projede iki fark var; sunumda sorulursa cevabı hazır olmalı:

- **Hareket:** yoga pozu yerine kolu yana kaldırma (omuz rehabilitasyon egzersizi). Gerekçe: Problem 2 omuzu istiyor; üç problem aynı harekette, aynı uygulamada birlikte çözüldü. İstenen adımların hepsi (ölçüm, referansla karşılaştırma, hata büyüklüğü, doğal dil, zamansal + geometrik hizalama, bindirme) bu harekette yapılıyor.
- **Referans:** başka birinin "doğru" videosu yerine kişinin kendi 6 doğru tekrarı. Gerekçe ölçüldü: başkalarının tekrarlarından kurulan bant çok daha kötü çalışıyor (AUC 0,67'ye karşı 0,95; [`DENEYLER.md`](DENEYLER.md) Soru 1). Bindirme kodu iki farklı kişinin tekrarını da hizalayabiliyor ([`SISTEM.md`](SISTEM.md), sık sorulan sorular).

Bu sapmanın hocayla konuşulup konuşulmadığı bu depoda kayıtlı değil; sunumdan önce teyit etmek iyi olur.

## Problemler ve şartlar

### P1 — (Yoga) hareketinin doğruluğu ve doğal dil geri bildirimi
- Referans video ile kullanıcının aynı hareketi yaptığı video karşılaştırılır.
- Eklem açıları, doğrultular ve hizalama ölçüleri üretilir.
- **Hatalı bölge ve hata büyüklüğü** belirlenir; düzeltme doğal dilde söylenir.
  - Örnek: "Sağ kolunu yaklaşık 90° kaldırman gerekiyordu; sen 80° kaldırdın…"
- Doğru harekette olumlu geri bildirim verilir.
- **Yeterli değil:** Sadece iskelet çizmek veya "%85 doğru" demek. AUC ve accuracy deneysel değerlendirmede kullanılabilir, ama kullanıcıya verilen ana çıktı fiziksel ölçüm ve doğal dil olmalı.
- **Projede:** 5 ölçü (`cekirdek/ozellikler.py`), hata türü (`cekirdek/hata_turu.py`), Türkçe cümle (`cekirdek/geribildirim.py`). Hasta cümlesinde derece ve düzeltme önerisi, uzman ayrıntısında "normalde X, sende Y"; doğru tekrarda olumlu cümle. Ölçüm: [`DENEYLER.md`](DENEYLER.md) Soru 2 ve 3.

### P2 — Omuz/skapula hareketlerinin hassas ölçümü
- Standart pose çıktısının hangi durumda sınırlı kaldığı gösterilir.
- **Omuza özel en az bir iyileştirme** uygulanır.
- Yorumlanabilir ölçüm verilir: derece, normalize mesafe, asimetri, yörünge.
- Mümkünse standart yöntemle iyileştirilmiş yöntem karşılaştırılır.
- **Yeterli değil:** MediaPipe'ın omuz koordinatlarını doğrudan okuyup piksel farkını raporlamak.
- **Ödevde önerilen yöntemler:** shoulder ROI, optical flow, zamansal yumuşatma/Kalman, DeepLabCut ile özel noktalar, RGB-D, keypoint + lokal görüntü/özel geometrik ölçüm birleşimi. Ayrıca "kol elevasyonu ile omuz/skapula hareketi arasındaki ilişki" ölçülebilecekler arasında sayılmış.
- **Projede:**
  - **Sınırın gösterilmesi:** ham ölçüler silkmeyi zayıf ayırıyor (AUC 0,60–0,70); doğru harekette de omuz kalkıyor.
  - **İyileştirmeler:**
    1. kol açısına koşullu, kişiye özel bant (asıl katkı; AUC 0,70 → 0,95);
    2. kulak–omuz geometrik ölçüsü (omuzu kafaya göre ölçmek).
  - **Denenip elenenler:** zamansal yumuşatma ve görüntüden omuz silueti; ikisi de bantlı kulak–omuz ölçüsünden iyi değil (kodları `arsiv/`).
  - **Karşılaştırma:** [`DENEYLER.md`](DENEYLER.md) Soru 1.

### P3 — Referans (yoga) hareketi ile kullanıcı hareketini aynı videoda çakıştırma
- **Zamansal hizalama:** DTW veya başlangıç/bitiş eşleme.
- **Geometrik hizalama:** öteleme, ölçek, döndürme veya Procrustes.
- İki iskelet aynı video üzerinde farklı renklerle gösterilir; hatalı bölgeler görünür olur.
- **Yeterli değil:** Videoları yan yana oynatmak veya aynı kare numaralarını üst üste çizmek.
- **Projede:** uygulamada her tekrar sonrası oynatım: referans (kişinin kalibrasyon tekrarı) DTW ile zamanda, kalça ortasına öteleme + gövde boyu oranıyla ölçek + gövde ekseniyle döndürme ile geometride hizalanır; banttan çıkan uzuv kırmızı. Kod: `cekirdek/bindirme.py`, `uygulama/panel.py`. Ayrıntı: [`SISTEM.md`](SISTEM.md) §7.

## 1 sayfalık rapor şablonu
1. **Problem ve amaç:** 2–3 cümle.
2. **Teknolojiler ve veri** (tablo):
   - pose yöntemi
   - ek yöntemler
   - araçlar
   - girdi/referans
3. **Yeniden gerçekleştirme adımları (ana bölüm, 5–8 adım):**
   1. ortam
   2. girdi hazırlığı
   3. pose çıkarımı
   4. ölçüm/hizalama
   5. hata hesabı
   6. geri bildirim
   7. çıktı
4. **Çalışan çıktı, en önemli sınırlılık, 3–5 kaynak.**

## Kurallar
- Kullanılan her makale, GitHub deposu, doküman ve veri seti kaynak olarak yazılır.
- Python ve kritik paket sürümleri belirtilir.
- **Üretken yapay zekâ ile kod, hata ayıklama veya rapor desteği alındıysa, amacı kısa bir notla belirtilir.**
- Son kontrol sorusu: "Bir başka öğrenci bu raporla uygulamanın temel sürümünü yeniden kurabilir mi?"

## Ödevin kaynak rehberinde omuz için önerilenler
Raporun sınırlılık veya kaynak kısmında anılabilir:
- **Lefebvre vd. (2025):** DeepLabCut ile 20 anatomik omuz/üst ekstremite noktası.
- **Ceglia vd. (2026):** RGB-D ve akromial küme ile omuz/skapula kinematiği.
- **RGB-D omuz ROM sistematik derlemesi (2025).**

Projede gerçekten kullanılan makaleler ve rapor için kaynak önerisi: [`LITERATUR.md`](LITERATUR.md).
