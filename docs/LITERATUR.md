# Literatür: projede kullanılan makaleler

Kodda ve belgelerde geçen `M39`, `M01` gibi adlar makale kodlarıdır. Bu belge yalnızca **yöntemde gerçekten kullanılan** sekiz makaleyi içerir: önce hangisinden ne alındığı, sonra her birinin özeti.

- Özetler, daha geniş bir literatür özetinden (16 makale) **değiştirilmeden** kopyalandı; o dosya ve makalelerin PDF'leri depoda değil.
- Özetler makalelerin metninden üretken yapay zekâ (Claude) ile çıkarıldı ([`LLM_KULLANIMI.md`](LLM_KULLANIMI.md)). Sayfa numaraları makaleye aittir; rapora ya da sunuma bir sayı alınmadan önce makalenin kendisinden doğrulanmalı.
- Her özetin sonundaki **Dikkat** bölümü, makalede tutarsız görünen noktaları listeler.

## Hangi makaleden ne alındı

| Kod | Makale | Projede ne için kullanıldı |
| --- | --- | --- |
| M39 | Jánošová ve ark., 2026 — Impact of Patient Orientation in Single- and Multi-View Camera Environments for AI-based Rehabilitation Monitoring | Veri seti (REHAB26-ViewAngles); kişiye özel tolerans bandı (μ, τ, τ alt sınırı, kare hatası); baş, dirsek, kol ölçülerinin tanımları (F1–F4) |
| M01 | Pavlikov ve ark., 2026 — Markerless On-Device Detection of Compensatory Movement Patterns in Upper-Limb Rehabilitation Exercises from Monocular RGB Video: A Validation Study in Healthy Adults | Kol açısı tanımı; omuz yükselmesinin tek kamerada en zor işaret olduğu; "normal hareket de omzu kaldırır" sorunu; faz fikri; en-boy düzeltmesi uyarısı |
| M33 | Cóias ve ark., 2022 — A low-cost virtual coach for 2D video-based compensation assessment of upper extremity rehabilitation exercises | Omzu boyna göre ölçme fikri; kural tabanlı telafi tespiti ve geri bildirim |
| M22 | Sarsfield ve ark., 2019 — Segmentation of Exercise Repetitions Enabling Real-Time Patient Analysis and Feedback Using a Single Exemplar | z-normalize DTW (yalnızca bindirmede) |
| M23 | Ye ve ark., 2026 — Perception, assessment, and coaching: a systematic review and taxonomy of computer vision-based physical rehabilitation techniques | Skor yerine performans bilgisi vermek: hangi eklem, hangi faz, nasıl düzelt |
| M45 | Delmas ve ark., 2024 — PoseScript: Linking 3D Human Poses and Natural Language | Pozdan kurallarla cümle üretme (sapma kodu fikri) |
| E2 | Delmas ve ark., Belirtilmemiş — PoseFix: Correcting 3D Human Poses with Natural Language | Poz farkından düzeltme cümlesi üretme (sapma kodu fikri) |
| E1 | Fieraru ve ark., 2021 — AIFit: Automatic 3D Human-Interpretable Feedback Models for Fitness Training | Referansa göre sapmayı doğal dilde söyleyen en yakın öncül |

Yöntemin anlatımı: [`SISTEM.md`](SISTEM.md). Makalelerin kodda geçtiği yerler: `cekirdek/aci_bandi.py` (M39), `cekirdek/ozellikler.py` (M01, M33, M39), `cekirdek/hizalama.py` (M22).

## Rapor için kaynak önerisi (şablon 3–5 kaynak istiyor)

1. Jánošová ve ark., 2026 (M39): veri seti ve tolerans bandı. arXiv:2609.35726; veri: Zenodo, DOI 10.5281/zenodo.23018128.
2. Pavlikov ve ark., 2026 (M01): kol açısı ve omuz yükselmesi sorunu. DOI 10.3390/s26165054.
3. Cóias ve ark., 2022 (M33): omzu boyna göre ölçme, kural tabanlı geri bildirim. DOI 10.1186/s12984-022-01053-z.
4. Sarsfield ve ark., 2019 (M22): z-normalize DTW. DOI 10.1109/TNSRE.2019.2907483.
5. Google MediaPipe Pose Landmarker, resmi dokümantasyon (poz çıkarımı; ödevin kaynak rehberinde).

DOI'ler makale listesinden (`makale_ozetleri.csv`) alındı; tam künyeler belgenin sonundaki tabloda.

## İncelenip yöntemde kullanılmayanlar

Geniş özette olup buraya alınmayan sekiz makale. Okundular, ama uygulamanın yöntemine bir şey girmedi:

| Makale | Konusu | Neden kullanılmadı |
| --- | --- | --- |
| Pereira ve ark., 2024 | Evde omuz egzersizi için akıllı telefon uygulaması, optoelektronik sistemle doğrulama | Benzer bir uygulama; yöntemimize aktarılan bir bileşen yok |
| Ullah ve ark., 2025 | Açı temelli hareket puanlama ve tekrar sayma | Tek bir puan veriyor; ödev puan yerine fiziksel ölçüm ve cümle istiyor |
| Francia ve ark., 2026 | MediaPipe'ın üst ekstremite açılarındaki doğruluğu (optoelektronik sisteme göre) | Yalnızca elenen "revize" az kaldırma puanının 10° alt sınırına gerekçeydi (kodda M42) |
| Mercadal-Baudart ve ark., 2024 | Tek kameradan 3B pozla egzersiz ölçütleri | Aynı elenen alt sınırın gerekçesi (kodda M41); 3B poz kullanmıyoruz |
| Gu ve ark., 2025 (ExeChecker) | Hataya yol açan eklemleri bulan derin ağ | Eğitilmiş model gerektiriyor; yöntemimiz kural tabanlı |
| Černek ve ark., 2025 | REHAB24-6 veri seti ve poz modellerinin karşılaştırması | Başka veri seti; poz modeli eğitmiyoruz |
| Tang ve ark., 2025 | Büyük dil modeliyle egzersiz değerlendirme ve geri bildirim | Cümleyi LLM'e yazdırmak denendi, üstünlük çıkmadı ([`DENEYLER.md`](DENEYLER.md), "Denenip işe yaramayanlar") |
| Unger ve ark., 2025 | İnme sonrası telafi hareketlerinin web kamerasıyla tespiti | Gerçek hasta verisi ve derin öğrenme; bizim verimiz sağlıklı kişilerin taklit hataları |

Kodda geçen `M20` (Carlos ve ark., 2025, MediaPipe ölçümlerinin tekrarlanabilirliği; DOI 10.1177/10554181251399001) da yalnızca aynı elenen alt sınırın gerekçesidir ve geniş özette yer almaz.

## Karşılaştırma tablosu

| Yazar, Yıl | Çalışma türü | Amaç (en fazla 10 kelime) | Veri / örneklem | Yöntem | Ana sonuç | Temel sınırlılık |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| Jánošová ve ark., 2026 | Deneysel | Kamera açısının rehabilitasyon egzersizi değerlendirmesine etkisini belirlemek | REHAB26-ViewAngles; 5 katılımcı, 3 egzersiz, 1.650 tekrar, 29 açı | MediaPipe Pose (2B/3B), YOLO26; ortogonal 2B, üçgenleme, ağırlıklı füzyon, RUMPL; ayırşabilirlik metriği Ψ | En uygun 2B açı önden görünüme göre \+%16,9; ortogonal iki kamera yaklaşık \+%13,1; 2B, 3B'den daha güvenilir | Çok kameralı düzenlerde kalibrasyon ve senkronizasyon güçlüğü |
| Pavlikov ve ark., 2026 | Deneysel doğrulama çalışması | Cihaz üzerinde belirteçsiz kompansasyon saptama sistemini doğrulamak | 37 sağlıklı gönüllü (9 kalibrasyon, 10 IMU, 18 saptama; 621 tekrar) | BlazePose, sabit eşikli beş geometrik metrik; IMU ve kör iki klinisyenle karşılaştırma | Açı medyan MAE 2.18° (0–62°); makro-F1 0.75/0.72; 22–30 FPS (s. 19, 21, 23\) | Sağlıklı gönüllüler, taklit kompansasyonlar, tek egzersiz |
| Cóias ve ark., 2022 | Deneysel (sistem geliştirme \+ pilot kullanıcı çalışması) | Web kamerasıyla 2B kompansasyon değerlendiren düşük maliyetli sanal koç | 15 inme sonrası hastanın 3 egzersiz videosu; 7 gönüllü | OpenPose 2B noktalar; kural tabanlı ve iki aşamalı NN sınıflandırma; LOSO/LOEO; Likert anketi | LOSO F1: E1 RB 0.76, E2 NN 0.73, E3 NN 0.80 (s. 12); hedonik 4.54, faydacı 4.86 (s. 12\) | Küçük kullanıcı örneklemi; RB yanlış tespitleri; uzak sunucuya bağlı gecikme |
| Sarsfield ve ark., 2019 | Deneysel (algoritma geliştirme) | Tek örnekle egzersiz tekrarlarını gerçek zamanlı bölütlemek | CMU (3 egzersiz, 10 denek); 4 inme hastası (Kinect, 3 GRASP egzersizi); sağlıklı katılımcılar (Qualisys, sayı belirtilmemiş) | Alt dizi DTW, kübik spline, sıfır hız geçişleri, z-normalizasyon, maliyet eşikli onay | Sağlıklı veride TE 0.5 s'de %100; hasta verisinde TE 0.3 s'de %86.4–89.3 TP; ≈5 ms işlem süresi (s. 1013–1016) | Egzersizin önceden bilindiği varsayımı; pencereyi aşan tekrarların kaçırılabilmesi |
| Ye ve ark., 2026 | Sistematik derleme ve taksonomi | Görü tabanlı rehabilitasyon tekniklerini PAC taksonomisiyle haritalamak | 147 yayın (2010–2026; 8 veri tabanı \+ Google Scholar) | PRISMA 2020, PICOS, özel kalite değerlendirmesi, betimsel kanıt haritası | Kanıt Algılama alanında yoğun; "Yüksek" düzey kayıt yok (s. 9\) | PROSPERO kaydı ve kappa yok; heterojenlik nedeniyle meta-analiz yok |
| Delmas ve ark., 2024 | Deneysel (veri seti ve yöntem önerisi) | 3B pozları doğal dil betimlemeleriyle eşleştirmek | AMASS'tan 100,000 poz; 6,283 insan betimlemesi; poz başına 3 otomatik betimleme | Kural tabanlı otomatik betimleme; ortak gömme ile erişim, koşullu VAE, otoregresif transformer | Otomatik betimlemelerle ön eğitim üç görevde performansı yaklaşık iki kat artırır (s. 12\) | Kendine temas eden ve baş aşağı pozlarda zayıf performans (s. 12\) |
| Delmas ve ark., Belirtilmemiş | Deneysel | Doğal dil geri bildirimiyle 3B insan pozlarını düzeltmek | AMASS'tan 135k otomatik ve 6157 insan açıklamalı poz çifti | Koşullu VAE (poz düzenleme); otoregresif transformer (metin üretimi) | En iyi düzenleme modelinde MPJE 196 mm; metin üretiminde R@2 %71.35 (s. 15023, 15026\) | Standart NLP ölçütleri tek referans metinle model kalitesini güvenilir yansıtmıyor |
| Fieraru ve ark., 2021 | Deneysel | Video ile 3B poz tabanlı otomatik fitness geri bildirim sistemi | Fit3D: 13 katılımcı, 37 egzersiz, 2,964,236 3B iskelet; CountixFitness (267 video) | MubyNet ile 3B poz; öz-ilinti ve eniyilemeyle tekrar bölütleme; aktif/pasif açı özellikleri; eşik tabanlı istatistiksel koç | Fit3D'de sayım OBO 0.140 (RepNet 0.520); δ \= 0.5'te geri bildirim doğruluğu yaklaşık %80 | Bölütleme ve geri bildirim doğruluğu poz kestirim kalitesine bağlı |

## Künye

| Yazar(lar) | Yıl | Başlık | Dergi / Konferans | Cilt (Sayı) | Sayfa | DOI | Yayın türü | APA 7 |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| Jánošová, M., Lang, A., Budikova, P., & Sedmidubsky, J. | 2026 | Impact of Patient Orientation in Single- and Multi-View Camera Environments for AI-based Rehabilitation Monitoring | Belirtilmemiş (arXiv, cs.CV; hakeme gönderilmiş taslak) | Belirtilmemiş | Belirtilmemiş (ön baskı, 25 sayfa) | Belirtilmemiş (yalnızca veri setinin DOI'si var: 10.5281/zenodo.23018128) | Ön baskı (arXiv:2609.35726v2) | Jánošová, M., Lang, A., Budikova, P., & Sedmidubsky, J. (2026). *Impact of patient orientation in single- and multi-view camera environments for AI-based rehabilitation monitoring* (arXiv:2609.35726v2) \[Preprint\]. arXiv. |
| Artem Pavlikov, Vera Petrosyan, Vladislav Agapov, Mikhail Gorodnichev, Danila Lobunko, Dmitry Skvortsov | 2026 | Markerless On-Device Detection of Compensatory Movement Patterns in Upper-Limb Rehabilitation Exercises from Monocular RGB Video: A Validation Study in Healthy Adults | Sensors | 26 (Belirtilmemiş) | Makale no. 5054 (35 s.) | 10.3390/s26165054 | Dergi makalesi (açık erişim, CC BY) | Pavlikov, A., Petrosyan, V., Agapov, V., Gorodnichev, M., Lobunko, D., & Skvortsov, D. (2026). Markerless on-device detection of compensatory movement patterns in upper-limb rehabilitation exercises from monocular RGB video: A validation study in healthy adults. *Sensors, 26*, Article 5054\. https\://doi.org/10.3390/s26165054 |
| Cóias, A. R., Lee, M. H., & Bernardino, A. | 2022 | A low-cost virtual coach for 2D video-based compensation assessment of upper extremity rehabilitation exercises | Journal of NeuroEngineering and Rehabilitation | 19 (Belirtilmemiş) | Makale no. 83 (16 sayfa) | 10.1186/s12984-022-01053-z | Dergi makalesi (Research, açık erişim) | Cóias, A. R., Lee, M. H., & Bernardino, A. (2022). A low-cost virtual coach for 2D video-based compensation assessment of upper extremity rehabilitation exercises. *Journal of NeuroEngineering and Rehabilitation, 19*, Article 83\. https\://doi.org/10.1186/s12984-022-01053-z |
| Sarsfield, J., Brown, D., Sherkat, N., Langensiepen, C., Lewis, J., Taheri, M., Selwood, L., Standen, P., Logan, P. | 2019 | Segmentation of Exercise Repetitions Enabling Real-Time Patient Analysis and Feedback Using a Single Exemplar | IEEE Transactions on Neural Systems and Rehabilitation Engineering | 27 (5) | 1004–1019 | 10.1109/TNSRE.2019.2907483 | Dergi makalesi | Sarsfield, J., Brown, D., Sherkat, N., Langensiepen, C., Lewis, J., Taheri, M., Selwood, L., Standen, P., & Logan, P. (2019). Segmentation of exercise repetitions enabling real-time patient analysis and feedback using a single exemplar. *IEEE Transactions on Neural Systems and Rehabilitation Engineering, 27*(5), 1004–1019. https\://doi.org/10.1109/TNSRE.2019.2907483 |
| Ye P., Li Y., Qu M., Liu J., Lu X., Cao W., Wang R., Wan Y., Zhu T., Zhou J. | 2026 | Perception, assessment, and coaching: a systematic review and taxonomy of computer vision-based physical rehabilitation techniques | Frontiers in Rehabilitation Sciences | 7 (Sayı: Belirtilmemiş) | Makale no. 1906327 (33 s.) | 10.3389/fresc.2026.1906327 | Dergi makalesi (Systematic Review), açık erişim | Ye, P., Li, Y., Qu, M., Liu, J., Lu, X., Cao, W., Wang, R., Wan, Y., Zhu, T., & Zhou, J. (2026). Perception, assessment, and coaching: A systematic review and taxonomy of computer vision-based physical rehabilitation techniques. *Frontiers in Rehabilitation Sciences, 7*, Article 1906327\. https\://doi.org/10.3389/fresc.2026.1906327 |
| Ginger Delmas, Philippe Weinzaepfel, Thomas Lucas, Francesc Moreno-Noguer, Grégory Rogez | 2024 | PoseScript: Linking 3D Human Poses and Natural Language | Belirtilmemiş (yalnızca DOI'de "TPAMI" kısaltması geçiyor) | Belirtilmemiş | Belirtilmemiş (ön baskı 25 sayfa) | 10.1109/TPAMI.2024.3407570 | arXiv ön baskısı (arXiv:2210.11795v3, 10 Eylül 2024), IEEE telif notuyla | Delmas, G., Weinzaepfel, P., Lucas, T., Moreno-Noguer, F., & Rogez, G. (2024). *PoseScript: Linking 3D human poses and natural language* (arXiv:2210.11795v3) \[Preprint\]. arXiv. https\://doi.org/10.1109/TPAMI.2024.3407570 |
| Ginger Delmas, Philippe Weinzaepfel, Francesc Moreno-Noguer, Grégory Rogez | Belirtilmemiş | PoseFix: Correcting 3D Human Poses with Natural Language | ICCV (Computer Vision Foundation açık erişim sürümü) | Belirtilmemiş | 15018–15028 | Belirtilmemiş | Konferans bildirisi | Delmas, G., Weinzaepfel, P., Moreno-Noguer, F. ve Rogez, G. (t.y.). PoseFix: Correcting 3D human poses with natural language. *ICCV* içinde (ss. 15018–15028). Computer Vision Foundation. |
| Mihai Fieraru, Mihai Zanfir, Silviu Cristian Pirlea, Vlad Olaru, Cristian Sminchisescu | 2021 | AIFit: Automatic 3D Human-Interpretable Feedback Models for Fitness Training | CVPR 2021 (Computer Vision Foundation Open Access sürümü) | Belirtilmemiş | 9919–9928 | Belirtilmemiş | Konferans bildirisi | Fieraru, M., Zanfir, M., Pirlea, S. C., Olaru, V., & Sminchisescu, C. (2021). AIFit: Automatic 3D human-interpretable feedback models for fitness training. In *CVPR 2021* (pp. 9919–9928). |

---

# Özetler

## M39 — Jánošová ve ark., 2026 — Impact of Patient Orientation in Single- and Multi-View Camera Environments for AI-based Rehabilitation Monitoring

**Çalışma türü:** Deneysel (veri seti geliştirme ve karşılaştırmalı değerlendirme).

**Amaç:** Kamera açısının ve poz kestirim stratejisinin, rehabilitasyon egzersizlerinde doğru ve hatalı tekrarların ayırt edilmesine etkisini incelemek. Altı araştırma sorusu; özellik düzeyinde açı etkisini, egzersize göre en iyi açıyı, yönelim sapmalarına dayanıklılığı, 2B–3B karşılaştırmasını, iki kamerada en uygun 3B füzyon stratejisini ve iki kameranın tek kameraya göre kazancını kapsıyor (s. 12).

**Yöntem:**

* Veri: Yazarların oluşturduğu REHAB26-ViewAngles veri seti; 5 katılımcı (2 erkek, 3 kadın), 3 egzersiz (kol abdüksiyonu, omuz ekstansiyonu, squat), 11 nominal vücut yönelimi; her koşulda 5 doğru ve 5 hatalı tekrar, toplam 1.650 tekrar (s. 8). Üç senkron iPhone 16e ile 29 benzersiz açı, 6 saatten fazla video ve yaklaşık 650.000 kare kaydedilmiş (s. 8–9).  
* Değerlendirme çerçevesi: Fizyoterapistlerle tanımlanan 15 eklem açısı özelliği (F1–F15); doğru tekrarlardan DTW hizalaması ve kare bazında %95 güven aralığı (Student t) ile kişiselleştirilmiş model kuruluyor (s. 7, 10).  
* Yöntemler: Tek kamerada MediaPipe Pose (2B ve 3B) ve 2B doğrulama için YOLO26; iki ortogonal kamerada ortogonal 2B birleşim, OpenCV DLT ile üçgenleme, görünürlük ağırlıklı 3B füzyon ve RUMPL dönüştürücü modeli (s. 13–14).  
* Ölçüt: Önerilen ayırşabilirlik metriği Ψ (hatalı tekrarın hatası eksi doğru tekrarların ortalama hatası; −1 ile 1 arası), −90° ile 90° arasındaki açılarda hesaplanıyor (s. 11, 15).

**Ana bulgular:**

* En uygun tek kamera açıları (2B MediaPipe ve YOLO26 uzlaşısı) Egzersiz 1 için 15°, Egzersiz 2 için 20°, Egzersiz 3 için 30°; bu açıya yerleştirilen 2B kamera, ayırşabilirliği yaygın 0° önden görünüme göre %16,9 artırdı (s. 16).  
* En iyi açı egzersizin hareket düzleminden çok sık görülen hataların yönüne bağlı; evrensel bir en iyi açı bulunmadı (s. 16).  
* Yönelim sapmasında özellikler en iyi açıdan yaklaşık 5°–10° içinde büyük ölçüde kararlı kaldı, 15°'yi aşan kaymalarda hızla bozuldu (s. 17).  
* 2B temsil 3B'ye göre ortalama %9,2 daha iyi ayırşabilirlik sağladı (s. 20); fark en belirgin squat egzersizindeydi, Egzersiz 2'de 3B biraz daha iyiydi (s. 18).  
* İki kamerada 3B stratejiler arasında en kararlısı üçgenleme oldu (s. 18). Tek kamera 2B MediaPipe'a göre ortogonal 2B kazançları %0 (Egz. 1), %26,6 (Egz. 2), %12,7 (Egz. 3); üçgenleme kazançları %1,5, %23,3 ve −%1,8 (s. 18); genel iyileşme ortogonal için yaklaşık %13,1, üçgenleme için yaklaşık %7,6 (s. 20).

**Yazarların sonucu:** Kamera açısı egzersiz değerlendirmesinde belirleyicidir; hafif yanal ve yarı profil açılar üç egzersiz için en uygunudur ve hastaların doğru konuma yönlendirilmesi gerekir (s. 20). Uygulama kolaylığı nedeniyle tek kameralı 2B poz kestirimi birincil yaklaşım olarak öneriliyor; iki kamera kullanılacaksa ortogonal 2B yaklaşım en avantajlı seçenek (s. 18, 20).

**Katkı:**

* Doğru ve hatalı tekrarları çok sayıda görüş açısından içeren REHAB26-ViewAngles veri seti.  
* Kişiselleştirilmiş modellere dayalı, doğru ve hatalı tekrarların ayrılabilirliğini ölçen yeni bir metrikle otomatik değerlendirme yöntemi.

**Sınırlılıklar ve gelecek çalışma:**

* Çok kameralı düzenler daha fazla alan, kalibrasyon ve zamansal senkronizasyon gerektiriyor; standart akıllı telefonlarla ev ortamında senkronizasyon pratikte zor (s. 18, 20).  
* Ayırşabilirlik skoru hatanın süresinden etkileniyor; yalnızca hareketin tepe noktasında kısa süren hatalar düşük skor alıyor (s. 15–16).  
* Gelecekte skor çerçevesinin hata süresini hesaba katması ve hareketin kritik noktasındaki hataları öne çıkaran dinamik zamansal ağırlıklandırma planlanıyor (s. 20).

**Kısa özet:** Jánošová ve ark. (2026), kamera açısının yapay zekâ tabanlı rehabilitasyon izlemesine etkisini incelemek için üç egzersiz, beş katılımcı ve 29 görüş açısını kapsayan REHAB26-ViewAngles veri setini oluşturmuş ve doğru ile hatalı tekrarların ayrılabilirliğini ölçen bir metrik önermiştir. Tek kamerada egzersize özgü 15°–30° arası açıların ayırşabilirliği önden görünüme göre %16,9 artırdığı, yaklaşık 10°'lik yönelim sapmasının tolere edilebildiği ve 2B poz kestiriminin 3B'den daha güvenilir olduğu rapor edilmiştir (s. 16–17, 20). İki kameralı stratejiler arasında en büyük kazancı ortogonal 2B birleşim (yaklaşık %13,1) sağlamış, 3B üçgenlemenin kazancı daha sınırlı kalmıştır (s. 20). Yazarlar, uygulama kolaylığı nedeniyle tek kameralı 2B yaklaşımı birincil yöntem olarak önermektedir (s. 18).

**Dikkat:**

* Özette iki kameranın kazancı "en fazla %13,1" olarak veriliyor (s. 1); oysa s. 18'de Egzersiz 2 için %26,6 kazanç bildiriliyor ve s. 20'de %13,1 genel iyileşme olarak sunuluyor. Değerin ortalama mı üst sınır mı olduğu tutarsız.  
* 2B–3B karşılaştırmasında Egzersiz 1 için önce farkların küçük olduğu, birkaç cümle sonra 3B'nin belirgin biçimde daha kötü olduğu söyleniyor (s. 17–18).  
* RQ5 "kalibre edilmemiş" iki kameradan söz ediyor (s. 12); ancak üçgenleme ve RUMPL, kayıt düzeneğinin bilinen geometrisinden türetilmiş kalibrasyon parametreleriyle çalıştırılmış (s. 13–14).


## M01 — Pavlikov ve ark., 2026 — Markerless On-Device Detection of Compensatory Movement Patterns in Upper-Limb Rehabilitation Exercises from Monocular RGB Video: A Validation Study in Healthy Adults

**Çalışma türü:** Deneysel doğrulama çalışması (sistem geliştirme ve ölçüm geçerliliği).

**Amaç:** Tek bir RGB kameradan alınan görüntüyü tamamen tarayıcıda, cihaz üzerinde işleyen belirteçsiz bir sistemin üst ekstremite rehabilitasyonunda kol elevasyon açısını ölçme ve kompansatuvar hareketleri saptama başarısını sağlıklı yetişkinlerde değerlendirmek. Açık bir hipotez belirtilmemiş.

**Yöntem:**

* Desen ve örneklem: Ayrık üç sağlıklı gönüllü örneklemi (toplam 37): eşik kalibrasyonu (n \= 9, 292 tekrar), IMU ile açı doğrulaması (n \= 10, 50 döngü), saptama değerlendirmesi (n \= 18, 621 tekrar); görev oturarak frontal düzlemde omuz abdüksiyonu (s. 16–17).  
* Sistem: BlazePose'un 33 noktasından beş normalize geometrik metrik (eksik dirsek ekstansiyonu, ekstremiteler arası asimetri, omuz elevasyonu, lateral gövde eğilmesi, baş eğimi) türetilmiş, sabit eşiklerle karşılaştırılmış; tekrarlar sonlu durum makinesiyle bölütlenmiş.  
* Referanslar: 200 Hz iki birimli IMU sistemi ve talimat verilen koşula, sistem çıktısına ve birbirine kör iki bağımsız klinisyen; kompansasyonlar gönüllülerce taklit edilmiş.  
* Ölçütler: Açı için MAE, RMSE, Bland–Altman ve Lin CCC, önceden belirlenmiş sınırlar MAE ≤ 5°, \|sapma\| ≤ 2°, LoA genişliği ≤ 10° (s. 18); saptama için F1, Cohen κ ve katılımcıları yeniden örnekleyen küme bootstrap (10,000 yineleme) ile %95 güven aralıkları (s. 14).

**Ana bulgular:**

* IMU referansına göre, kayıtların kapsadığı 0–62° aralığında görüntü düzlemi açısı tüm önceden belirlenmiş ölçütleri karşıladı: medyan MAE 2.18° \[Ç1–Ç3: 1.62–2.83\], RMSE 2.61°, sapma 0.92°, kişi başına LoA genişliği 7.35°, Lin CCC 0.956 \[0.942–0.967\] (s. 18–19).  
* Fark açıyla orantılı büyüdü: farkın ortalama açı üzerindeki regresyon eğimi yaklaşık 0.044 derece/derece (R² ≈ 0.89), kaydedilen aralığın üst ucunda yaklaşık \+2.7° (s. 19).  
* Birincil analizde (621 tekrarın tamamı, her klinisyene ayrı ayrı) makro-F1 0.75 \[0.69, 0.80\] ve 0.72 \[0.66, 0.78\]; iki klinisyenin uzlaştığı 477 tekrarlık alt kümede üst sınır olarak 0.78 \[0.72, 0.83\] bulundu; klinisyenler arası ortalama κ 0.84 (s. 21).  
* Metrik bazında bireysel değerlendiricilere karşı F1: gövde eğilmesi 0.92/0.92, baş eğimi 0.90/0.87, eksik dirsek ekstansiyonu 0.72/0.73, asimetri 0.66/0.60, omuz elevasyonu 0.55/0.50 (s. 23). Dirsek eşiği %20 sıkılaştırıldığında uzlaşı alt kümesindeki F1 0.72'den 0.23'e düştü (s. 24).  
* Altı dizüstü bilgisayarda ayrık GPU olmadan uçtan uca 22–30 FPS ve %9–20 CPU yükü; hesaplama gecikmesi 120 ms'nin altında, toplam geri bildirim gecikmesi yaklaşık 350–400 ms (s. 23–24).

**Yazarların sonucu:** Sistem, evde telerehabilitasyon için mahremiyeti koruyan bir kavram kanıtı temeli sunuyor, bitmiş bir klinik araç değil; başka egzersizlere genellenebilirliği ve gerçek inme sonrası kompansasyonlardaki etkinliği henüz gösterilmemiş (s. 1, 30).

**Katkı:**

* Ham videonun cihazdan çıkmadığı, tarayıcıda tamamen yerel çalışan bir "kare → poz → metrik → geri bildirim" döngüsü ile sabit eşikli, tekrarlanabilir beş metrikten oluşan bir set (s. 3–4).  
* Açının IMU'ya, beş bayrağın kör iki klinisyene karşı ayrı ayrı doğrulandığı iki parçalı değerlendirme; yazarlar yeniliği yeni bir poz tahmin yöntemi değil, sistem entegrasyonu ve doğrulama olarak tanımlıyor (s. 3).

**Sınırlılıklar ve gelecek çalışma:**

* Tek egzersiz, tek kamera düzeni ve genç, çoğunluğu erkek sağlıklı gönüllülerin taklit ettiği kompansasyonlar; açı doğrulaması yalnızca 0–62° aralığında ve gerçek zamanlı yol yerine çevrimdışı işlenmiş sinyalde yapılmış (s. 27–29).  
* Omuz elevasyonu tek frontal görünümde abdüksiyon hareketinden tam ayrıştırılamıyor; Q skoru ve tekrar bölütlemesi doğrulanmamış; her iki kolun görüntüde kalması gerektiğinden tek taraflı hemiparetik kullanım kapsam dışı (s. 28).  
* Gelecek çalışma: ataletsel veya 3B füzyon, hastaya özgü uyarlanabilir eşikler ve gerçek inme sonrası hastalarda kinematiği fonksiyonel iyileşmeyle ilişkilendiren daha büyük klinik çalışma (s. 30).

**Kısa özet:** Pavlikov ve ark. (2026), tek RGB kameradan beş geometrik kompansasyon metriği türeten ve tamamen tarayıcıda çalışan bir üst ekstremite telerehabilitasyon sistemi geliştirmiştir. Sağlıklı gönüllülerde omuz abdüksiyon açısı 0–62° aralığında IMU'ya göre 2.18° medyan MAE ile ölçütleri karşılamış, ancak fark açıyla orantılı artmıştır (s. 19). Kör iki klinisyene karşı saptamada makro-F1 0.75 ve 0.72 elde edilmiş; en yüksek başarı gövde eğilmesi ve baş eğiminde, en düşük omuz elevasyonunda görülmüştür (s. 21, 23). Sistem ayrık GPU olmadan 22–30 FPS hızında çalışmış, ancak bulgular tek egzersiz ve taklit kompansasyonlarla sınırlıdır (s. 23, 27).

**Dikkat:**

* Sapma farklı biçimlerde raporlanmış: kişi başı medyan sapma 0.92° (s. 19), ortalama yörüngeye dayalı Bland–Altman grafiğinde ortalama fark 1.40° (s. 20); orantılı hata nedeniyle aralığın üst ucunda sistematik bileşen ±2° sınırına yaklaşıp aşıyor (s. 20).  
* Lin CCC aralığı %95 güven aralığı olarak verilmiş, ancak nasıl hesaplandığı belgelenmemiş; aynı tablodaki diğer aralıklar çeyrekler arası aralık (s. 19).  
* Tablo 12 başlığı yalnızca dirsek metriğinin eşiğe duyarlı olduğunu belirtirken, aynı tabloda gövde eğilmesi F1 değeri −%20'de 0.92'den 0.75'e düşüyor (s. 24–25).


## M33 — Cóias ve ark., 2022 — A low-cost virtual coach for 2D video-based compensation assessment of upper extremity rehabilitation exercises

**Çalışma türü:** Deneysel (sistem geliştirme ve doğrulama ile keşifsel pilot kullanıcı çalışması).

**Amaç:** Yalnızca dahili web kameralı bir dizüstü bilgisayarla üç üst ekstremite rehabilitasyon egzersizini izleyen, kompansatuvar hareketleri 2B konum verisinden değerlendirip gerçek zamanlı görsel ve işitsel geri bildirim veren düşük maliyetli bir sanal koç (VC) geliştirmek ve kullanılabilirliğini değerlendirmek. Hipotezler: hedonik değer algısı, VC performansı algısı ve etkileşim özelliklerinden etkilenir (H1); VC algısı inme geçirmiş ile geçirmemiş gönüllüler (H2a) ve yaşlı ile genç yetişkinler arasında, özellikle faydacı değerde (H2b), farklılaşır (s. 11).

**Yöntem:**

* Veri: Lee ve ark. veri setindeki 15 inme sonrası hastanın (yaş 63 ± 11.43) üç egzersizi (E1 bardağı ağza götürme, E2 ışık düğmesine basma, E3 bastonu ileri itme), egzersiz başına ortalama 10 deneme; kareler terapist görüşüyle dört kompansasyon türü (gövde öne, gövde rotasyonu, omuz elevasyonu, diğer) ve normal hareket olarak etiketlendi.  
* Model: OpenPose ile 2B vücut noktaları çıkarıldı, MidHip merkezli koordinata dönüştürülüp omurga uzunluğuna normalize edildi; kinematik değişkenlere eşik kuralları uygulayan kural tabanlı (RB) sınıflandırıcı ile ikili (C1) ve çok etiketli (C2) aşamalı sinir ağı (NN) yaklaşımı karşılaştırıldı.  
* Değerlendirme: Mikro-ortalamalı Precision, Recall, F1 ve Hamming Loss; LOSO çapraz doğrulama, NN için ayrıca E1 ve E2 ile LOEO.  
* Kullanıcı çalışması: Biri inme geçirmiş 7 gönüllü, ev ortamında dizüstü bilgisayar ve RB yöntemiyle en fazla 30 dakikalık oturumlar; hedonik değer, faydacı değer, kullanım niyeti ve sistem performansı 5'li Likert ile ölçüldü.

**Ana bulgular:**

* E1'de RB, LOSO ile F1 \= 0.76 ± 0.12 ve Hamming Loss \= 0.11 ± 0.07 elde ederek NN'den (F1 \= 0.70 ± 0.24) daha iyi sonuç verdi (s. 12).  
* E2 ve E3'te NN, LOSO ile sırasıyla F1 \= 0.73 ± 0.19 ve 0.80 ± 0.22 elde etti; RB'nin değerleri 0.59 ± 0.16 ve 0.70 ± 0.26 idi (s. 12).  
* NN, E1 ve E2 ile LOEO çapraz doğrulamasında F1 \= 0.80 ± 0.02 elde etti (s. 12); yazarlar bunu, veri toplama düzeni aynı kaldıkça farklı egzersizlere genellenebilirlik olarak yorumladı (s. 14).  
* Pilot çalışmada 5'li Likert ortalamaları hedonik değer 4.54 ± 0.51, faydacı değer 4.86 ± 0.38, kullanım niyeti 4.75 ± 0.50 ve sistem performansı 4.36 idi (s. 12–13); hedonik değer ile sistem performansı arasında Pearson ρ \= 0.53 bulundu (s. 13).  
* İnme geçirmiş gönüllü faydacı değere 4.0, sistem performansına 3.0 ve kullanım niyetine 4.0 puan verirken diğer gönüllülerin ortalamaları 5.0 ± 0.0, 4.58 ± 0.58 ve 5.0 ± 0.0 idi; 55 yaş ve üstü grup faydacı değere 5.0 ± 0.0, 55 yaş altı grup 4.67 ± 0.58 verdi ve fark anlamlı değildi (s. 13, 15).

**Yazarların sonucu:** Önerilen yöntemler 15 hastalık veri setinde motor kompansasyonu 2B konum verisinden doğru biçimde değerlendirmekte ve 3B poz verisi kullanan yaklaşımlarla karşılaştırılabilir performans göstermektedir (s. 15). Pilot çalışma, VC'nin yararlı geri bildirim verdiğini ve uygulanabilirliğine ilişkin kanıt sunduğunu göstermiştir (s. 15).

**Katkı:**

* Yalnızca dahili web kameralı bir dizüstü bilgisayar gerektiren ve kompansatuvar hareketlere gerçek zamanlı geri bildirim veren düşük maliyetli bir sanal koç (s. 2).  
* 2B video analiziyle gerçek zamanlı nicel kompansasyon değerlendirme yöntemleri ve bunun için kare kare etiketlenmiş veri; LOSO sonuçları (%72–79) 3B poz verili modellerle (%74–82) karşılaştırılabilir (s. 2, 13).

**Sınırlılıklar ve gelecek çalışma:**

* RB yöntemi gövde eğimini omuz elevasyonu olarak yanlış algılayabildi; kurallarda gövde yer değiştirmesine öncelik verilmesi, hareket açıklığı ve düzgünlük gibi bileşenlerin ve klinik anlamlı bir performans skorunun eklenmesi öneriliyor (s. 14–15).  
* Başlangıç pozisyonunda esneklik eksikliği ve WiFi üzerinden uzak sunucuya bağlı yavaş yanıt; TensorFlow Lite ve yapay zekâ donanım hızlandırıcıları ile hızlandırma hedefleniyor (s. 14–15).  
* Nadir kompansasyon örüntüleri veri setinde zayıf temsil ediliyor ve kullanıcı örneklemi küçük ve dengesiz; daha büyük örneklemle ve rehabilitasyondaki inme hastaları ile terapistlerle değerlendirme planlanıyor (s. 13, 15).

**Kısa özet:** Cóias ve ark. (2022), yalnızca dahili web kameralı bir dizüstü bilgisayarla çalışan ve inme sonrası üst ekstremite egzersizlerindeki kompansatuvar hareketleri OpenPose ile elde edilen 2B vücut noktalarından değerlendiren düşük maliyetli bir sanal koç geliştirmiştir. 15 inme sonrası hastanın verisiyle kural tabanlı ve sinir ağı tabanlı sınıflandırıcılar karşılaştırılmış; LOSO doğrulamasında en iyi F1 değerleri E1 için 0.76 (kural tabanlı), E2 ve E3 için 0.73 ve 0.80 (sinir ağı) olmuştur (s. 12). Yedi gönüllüyle yapılan pilot çalışmada sistem yüksek hedonik (4.54) ve faydacı (4.86) değer almış, ancak yanıt süresi, pozisyon esnekliği ve bazı yanlış tespitler geliştirilmesi gereken noktalar olarak belirtilmiştir (s. 12, 14). Yazarlar, 2B veriyle elde edilen performansın 3B poz verisi kullanan yaklaşımlarla karşılaştırılabilir olduğunu bildirmektedir (s. 13).

**Dikkat:**

* F1 değerleri farklı yerlerde farklı hassasiyetle ve kısmen farklı verilmiş: özette %76.69, %72.56 ve %79.87 (s. 1), Tablo 9'da 0.76, 0.73 ve 0.80 (s. 12); LOEO F1 değeri s. 12'de 0.80 ± 0.02, s. 14'te %79.59 ± %1.86.  
* Tablo 11'de kullanım niyetinin diğer tüm boyutlarla korelasyonu 1.00 olarak raporlanmış (s. 13); Şekil 14 notuna göre kullanım niyeti maddelerini yalnızca daha önce rehabilitasyon sürecini izlemiş gönüllüler yanıtlamış (s. 14), bu nedenle bu boyutun örneklem sayısı belirsiz.  
* Tablo 9 başlığında doğrulama yöntemi "LOES" olarak geçerken metinde "LOEO" kullanılıyor; Tablo 13 dipnotu ise sınıflandırıcı performansından söz ediyor (s. 12–13).


## M22 — Sarsfield ve ark., 2019 — Segmentation of Exercise Repetitions Enabling Real-Time Patient Analysis and Feedback Using a Single Exemplar

**Çalışma türü:** Deneysel (algoritma geliştirme ve değerlendirme).

**Amaç:** Hareket kısıtlılığı olan bireyler dahil, egzersiz tekrarlarını yalnızca tek bir örnek (exemplar) tekrar kullanarak gerçek zamanlı bölütleyen bir algoritma geliştirmek. Hipotez: herhangi bir sağlıklı bireyden alınan tek bir örnek tekrar, sınırlı hareketliliği olanlar dahil başka bireylerin tekrarlarını bölütlemek için kullanılabilir (s. 1004).

**Yöntem:**

* Desen: Algoritma önerisi ve gerçek zamanlı simülasyonla (veri kare kare verilir, gelecek veri görülmez) üç veri kümesinde değerlendirme.  
* Veri: CMU Motion Capture Database'den 3 egzersiz (yan dönüş, çömelme, jumping jack) ve 10 denek; evde rehabilitasyon gören 4 inme hastasının Kinect ile kaydedilen 3 GRASP egzersizi (kolu yana, kolu öne, dönüş; her biri 3 tekrar); aynı egzersizleri yapan sağlıklı katılımcıların Qualisys verisi (katılımcı sayısı belirtilmemiş).  
* Model: Yerel koordinat sistemine döndürülmüş, eklemler arası birim yön vektörlerinin tek boyutlu bileşenleri; değişim miktarına göre özellik sıralama; kübik spline ve sıfır hız geçişleriyle özellik çıkarımı; sıfır ortalama/birim varyans normalizasyonu; alt dizi DTW (SDTW); diğer özelliklerin toplam maliyet eşikleriyle onay/ret.  
* Değerlendirme: Zaman hatası (TE) 0–0.5 s aralığında TP/FP/FN yüzdeleri ve MAE; parametreler (ST, DM, DB) CMU üzerinde 0–1 aralığında 0.1 adımlı ızgara aramasıyla F1 ölçütüne göre incelendi; yürütme süresi Intel Core i7 4790K üzerinde tek iş parçacıklı Python ile ölçüldü.

**Ana bulgular:**

* CMU veri kümesinde jumping jack 21/26, çömelme 13/19, yan dönüş 2/4 tekrar doğru bölütlendi (sırasıyla 4, 5 ve 1 aday denek); FP yalnızca çömelmede (4 segment, deneme 86\_02) görüldü ve hataların çoğu algoritmadan değil eklem izleme kaybı veya hatalı egzersiz icrasından kaynaklandı (s. 1011–1012).  
* Kinect inme hastası verisinde TP oranı TE \= 0.3 s'de egzersiz 1, 2 ve 3 için sırasıyla %87.5, %89.3 ve %86.4; TE \= 0.5 s'de %95.8, %89.3 ve %90.9 oldu (s. 1014–1015).  
* Aynı 0.3 s TE eşiğinde bu yaklaşım %86.4–89.3 doğruluk elde ederken Lin ve Kulic'in alt ekstremite rehabilitasyonundaki 4 total eklem protezi hastasıyla test edilen yöntemi %79 bildirmişti (s. 1016).  
* Qualisys ile kaydedilen sağlıklı katılımcı verisinde tüm egzersizlerde TE \= 0.5 s'de %100 TP elde edildi ve MAE ihmal edilebilir düzeydeydi (s. 1014–1015).  
* 30 Hz'de 600 karelik 20 s'lik pencerede en son tekrarın bölütlenmesi ≈5 ms sürdü (gerçek zamanlı sınır 33 ms); en iyi parametre kombinasyonları F1 \= 0.77 (ST 0.1 veya 0.2, DM 0.1, DB 0.3) verdi (s. 1013, 1018).

**Yazarların sonucu:** Algoritma tek bir örnek tekrarla gerçek zamanlı bölütleme yapabilmekte; sağlıklı popülasyondaki tüm tekrarları 0.5 s içinde, inme hastalarının tekrarlarını ise 0.3–0.4 s içinde %90 TP ile doğru bölütlemiştir (s. 1018).

**Katkı:**

* Yalnızca tek bir bireyden tek bir örnek tekrar gerektiren ve düşük hareket açıklığı, hareket istikrarsızlığı ile sensör gürültüsüne dayanıklı gerçek zamanlı bölütleme algoritması (s. 1004, 1018).  
* Önceki çalışmaların çoğunun aksine gerçek inme hastası verisiyle test edilmiş ve DTW'nin çevrim içi kullanım için fazla maliyetli olduğu görüşüne karşın gerçek zamanlı çalışan bir DTW yaklaşımı (s. 1016).

**Sınırlılıklar ve gelecek çalışma:**

* Yapılan egzersizin önceden bilindiği varsayılır; egzersiz tanıma yapılmaz (s. 1004, 1006).  
* Pencere boyutunu aşan tekrarlar kaçırılabilir veya geç bölütlenebilir; Kinect eklem konumları örtüşme ve titreme nedeniyle güvenilmez olabilir ve benzer kol hareketleri kolu yana/öne egzersizlerinde daha fazla FP'ye yol açmıştır (s. 1013–1014).  
* Gelecekte klinik kullanıma yönelik bir poz kestirim algoritması geliştirilip bu bölütleme algoritmasıyla birleştirilmesi planlanmaktadır (s. 1018).

**Kısa özet:** Sarsfield ve ark. (2019), teknoloji destekli fiziksel rehabilitasyon sistemlerinde anlık geri bildirim sağlamak için egzersiz tekrarlarını tek bir örnek tekrar üzerinden gerçek zamanlı bölütleyen, alt dizi DTW tabanlı bir algoritma önermiştir. Yöntem, eklemler arası birim yön vektörlerinden türetilen hareket özelliklerini kübik spline ve sıfır hız geçişleriyle seyrelterek normalize eder ve en bilgilendirici özellik üzerinde hizalama yaptıktan sonra diğer özelliklerle bölütlemeyi onaylar ya da reddeder. CMU veri kümesi, sağlıklı katılımcıların Qualisys verisi ve 4 inme hastasının Kinect verisiyle yapılan değerlendirmede sağlıklı verilerde 0.5 s içinde %100, hasta verisinde 0.3–0.4 s içinde yaklaşık %90 doğru bölütleme bildirilmiştir (s. 1014–1015, 1018). Yazarlar yaklaşımın tek iş parçacıklı Python uygulamasında bile gerçek zamanlı çalışabildiğini göstermiştir (s. 1013).

**Dikkat:**

* Metinde Kinect verisinde ≈0.3 s TE ile %90 doğru bölütleme elde edildiği belirtilirken Tablo IV–VI'da TE \= 0.3 s için TP oranları %87.5, %89.3 ve %86.4'tür; sonuç bölümü bu eşiği 0.3–0.4 s olarak verir (s. 1014–1015, 1018).  
* Şekil 6 (çömelme) ve Şekil 7 (jumping jack, sorgu denek 86\) içindeki grafik başlıkları "yan dönüş, sorgu denek 13 deneme 29" olarak görünmekte, alt yazılarla uyuşmamaktadır (s. 1010–1011).  
* Parametre bölümünde DM ve DB'nin toplam maliyet eşiklerini Denklem 8'e göre ayarladığı yazılmıştır; eşik tanımı ise Denklem 2'dedir (s. 1006, 1016).


## M23 — Ye ve ark., 2026 — Perception, assessment, and coaching: a systematic review and taxonomy of computer vision-based physical rehabilitation techniques

**Çalışma türü:** Sistematik derleme (PRISMA 2020\) ve taksonomi önerisi.

**Amaç:** Bilgisayarlı görü tabanlı tekniklerin fiziksel rehabilitasyonun Algılama, Değerlendirme ve Koçluk aşamalarında nasıl geliştirildiğini, doğrulandığını ve aktarıldığını incelemek; rutin klinik kullanım önünde kalan yöntemsel, klinik ve uygulama boşluklarını belirlemek (s. 5). Literatürü düzenlemek için Algılama, Değerlendirme ve Koçluk (PAC) taksonomisi önerilmektedir.

**Yöntem:**

* PRISMA 2020 raporlama çerçevesi ve PICOS temelli uygunluk ölçütleri; protokol PROSPERO'ya önceden kaydedilmemiş (s. 4–5).  
* Ocak 2010–Ocak 2026 aralığında IEEE Xplore, ACM Digital Library, arXiv, PubMed/MEDLINE, Cochrane Library, JMIR, Web of Science ve Scopus taranmış; Google Scholar ile atıf takibi yapılmış (s. 5).  
* 427 veri tabanı kaydı ve 31 ek kayıt (toplam 458); 130 yinelenen çıkarıldıktan sonra 328 başlık/özet ve 228 tam metin incelenmiş, 147 yayın dahil edilmiş (s. 7).  
* Sekiz boyutlu özel kalite değerlendirme listesi ve PAC temelli betimsel kanıt haritası kullanılmış; heterojenlik nedeniyle meta-analiz yapılmamış (s. 6–7).

**Ana bulgular:**

* 147 kaydın 56'sı (38.1%) yalnızca Algılama, 20'si (13.6%) yalnızca Değerlendirme, 16'sı (10.9%) yalnızca Koçluk, 19'u (12.9%) alanlar arası; kanıt Algılama alanında yoğunlaşıyor (s. 9).  
* Genel kalite değerlendirmesinde "Yüksek" düzeyde kayıt yok (0; 0.0%), "Orta-yüksek" 10 kayıt (6.8%); 88 kayıt (59.9%) genel, kıyaslama odaklı veya belirli bir hasta grubuna özgü değil (s. 9).  
* Algılama alt kümesinde optik hareket yakalama ile doğrulama yalnızca 2 kayıtta kodlanmış; 54 kayıtta açıkça kodlanmış klinik karşılaştırıcı yok (s. 18–19).  
* Standart yürüyüş analizi koşullarında güncel 3D poz modellerinin MPJPE değeri yaklaşık 30–50 mm; HGcnMLP, kas-iskelet hastalarında diz açısı için Vicon'a göre ICC 0.84–0.98 ve yaklaşık 5–10° açısal hata bildirmiş; yazarlar bunu klinik geçerlik için yeterli saymıyor (s. 17).  
* Hareket kalitesi değerlendirmesinde düşük düzey sinyal regresyonu Spearman r 0.41, ince taneli zamansal ayrıştırma 0.89–0.92 (cerrahi bağlamı); inme bağlamında hiyerarşik füzyon ile kare doğruluğu 85.08% (s. 22).

**Yazarların sonucu:** Algılamada biyomekanik dijital ikizlere, Değerlendirmede yorumlanabilir patolojik atfa, Koçlukta motor öğrenme ilkelerine dayalı uyarlanabilir çok modlu duyu-motor döngüye doğru bir dönüşüm saptanmıştır (s. 29). Yazarlara göre üretken YZ ve MLLM'ler bu alanları yeniden yapılandırmakta, ancak patolojik veri ve klinik doğrulama sorunları sürmektedir (s. 29).

**Katkı:**

* Rehabilitasyon görüsünü genel görüden ayırarak temel sorunun eylem sınıflamasından patolojik hareket kalitesinin ölçülmesine kaydığını ortaya koyma (s. 4).  
* Dağınık literatür için üç alanlı PAC taksonomisini kurma ve bunu sistemleri sınıflayıp klinik olgunluğunu değerlendiren bir araç olarak işlevselleştirme (s. 4, 14).

**Sınırlılıklar ve gelecek çalışma:**

* PROSPERO kaydı yapılmamış; tarama aşamasında Cohen kappa gibi değerlendiriciler arası güvenirlik istatistikleri kaydedilmemiş (s. 28).  
* Yayın yanlılığı olasılığı, tasarım ve sonuç ölçütlerindeki heterojenlik nedeniyle meta-analiz yapılamaması ve İngilizce dışı literatürün eksik temsili (s. 28–29).  
* Gelecekte koçluk stratejilerinin randomize veya kontrollü denemelerle sınanması, hasta bildirimli sonuçların eklenmesi, pediatrik ve bilişsel bozukluğu olan gruplarda doğrulama gerekiyor (s. 24, 29).

**Kısa özet:** Ye ve ark. (2026), bilgisayarlı görü tabanlı fiziksel rehabilitasyon tekniklerini PRISMA 2020'ye göre derleyerek 147 yayını Algılama, Değerlendirme ve Koçluk (PAC) taksonomisiyle haritalamıştır. Kanıtın büyük bölümü poz kestirimi ve yeniden yapılandırmaya odaklanırken değerlendirme ve özellikle kapalı döngü koçluk çalışmaları daha az temsil edilmektedir (s. 9). Hiçbir kayıt yüksek düzey klinik kanıt sunmamakta, Algılama çalışmalarının çoğunda da altın standart karşılaştırıcı bulunmamaktadır (s. 9, 18–19). Yazarlar, biyomekanik kısıtlı dijital ikizleri, yorumlanabilir patolojik atfı ve motor öğrenmeye dayalı geri bildirimi klinik aktarım için temel yönler olarak sunmaktadır.

**Dikkat:**

* Tablo 10 ve metin 21 veri kümesinden söz ediyor, tabloda ise 22 veri kümesi listeleniyor; gerçek patolojik veri kümelerinin genellikle n \< 50 olduğu belirtilirken aynı grupta 80 ve 414 katılımcılı kümeler yer alıyor (s. 27–28).  
* Bazı atıflar iddiayla uyuşmuyor: I3D eylem tanıma modeli için bir konuşma tanıma makalesine (kaynak 61), Geri Bildirim Öncelik Piramidi için görsel soru yanıtlama derlemesine (kaynak 28), Motor Öğrenme Kuramı için görüntü kalitesi derlemesine (kaynak 86\) atıf yapılmış (s. 4, 8, 14, 30–32).  
* Sonuç bölümü büyük modellerin sistemleri klinik mantığa sahip özerk ajanlara dönüştürdüğünü kesin dille ifade ederken (s. 29), Bölüm 8.1 bunu doğrulanmamış bir hipotez olarak çerçeveliyor (s. 24); Tablo 6'daki klinik metrikler de pilot çalışmalardan öngörülmüş, derlemelerden sentezlenmiş değerler (s. 19).


## M45 — Delmas ve ark., 2024 — PoseScript: Linking 3D Human Poses and Natural Language

**Çalışma türü:** Deneysel (veri seti geliştirme ve yöntem önerisi).

**Amaç:** 3B insan pozlarını vücut bölümlerini ve aralarındaki uzamsal ilişkileri anlatan doğal dil betimlemeleriyle eşleştiren bir veri seti oluşturmak ve bu veriyi üç çok kipli öğrenme görevinde sınamak.

**Yöntem:**

* Veri: AMASS'taki 14,096 diziden en uzak nokta örneklemesiyle seçilen 100,000 statik poz (s. 3); Amazon Mechanical Turk'te iki aşamalı arayüzle toplanan 6,283 insan betimlemesi, PoseScript-H (s. 4, 6).  
* Otomatik betimleme hattı: 3B eklem koordinatlarından kural tabanlı "posecode"lar çıkarılıp seçilir, birleştirilir ve şablon cümlelere dönüştürülür; poz başına 3 otomatik betimleme, PoseScript-A (s. 5–6).  
* Modeller: metin–poz erişimi için ortak gömme uzayı (BBC kaybı), metne koşullu poz üretimi için koşullu VAE, poz betimleme üretimi için çapraz dikkatli otoregresif transformer; metin kodlayıcı GloVe+biGRU veya DistilBERT tabanlı transformer.  
* Değerlendirme: erişimde R@K ve mRecall; poz üretiminde FID benzeri ölçüt, mRecall ve ELBO; betimleme üretiminde R-Precision, BLEU-4, ROUGE-L, METEOR ve yeniden yapılandırma hataları; veri yaklaşık %70/10/20 eğitim/doğrulama/test olarak bölünmüş (s. 6).

**Ana bulgular:**

* Metin–poz erişiminde PoseScript-H testinde yalnızca insan betimlemeleriyle eğitilen model mRecall 23.0, PoseScript-A ön eğitimi \+ PoseScript-H ince ayarı 40.9, buna transformer metin kodlayıcı ve ayna artırımı eklenince 45.3 elde etmiştir; PoseScript-A'da eğitilip test edilen model 72.8'e ulaşmıştır (s. 8).  
* Metne koşullu poz üretiminde (PoseScript-H testi, L\_reg'li model) ön eğitim FID'i 0.29'dan 0.04'e düşürmüş, mRecall R/G'yi 5.2'den 19.5'e, G/R'yi 20.5'ten 35.1'e çıkarmıştır; transformer ve ayna artırımıyla FID 0.03, R/G 37.5, G/R 45.2 olmuştur (s. 9).  
* Poz betimleme üretiminde ön eğitim R@1'i 24.39'dan 88.09'a, BLEU-4'ü 11.35'ten 13.07'ye çıkarmış, MPJE'yi 324'ten 203'e düşürmüştür (MPJE birimi belirtilmemiş); ayna artırımıyla R@1 88.98'dir (s. 11).  
* Ön eğitimde tekil otomatik betimleme sürümleri arasında en yüksek mRecall'ı örtüklük (posecode birleştirme) içeren N3 sürümü (39.8), en iyi sonucu ise farklı sürümlerden oluşan PoseScript-A havuzu (40.9) vermiştir; ön eğitimde kullanılan otomatik betimleme sayısı arttıkça sonuçlar iyileşmiştir (s. 11).  
* Pozların farklı açılardan görüntülenmesiyle sınanan CLIP mRecall 1.6 elde ederken önerilen en iyi model 45.3 elde etmiştir (s. 18).

**Yazarların sonucu:** PoseScript, 3B insan pozlarını doğal dil betimlemeleriyle eşleyen ilk veri seti olarak sunulmuştur. Otomatik betimlemelerle ön eğitimin incelenen üç görevin hepsinde performansı sistematik olarak yaklaşık iki kat artırdığı belirtilmiştir (s. 12).

**Katkı:**

* İnsan yazımı ve otomatik betimlemeler içeren PoseScript veri seti ile binlerce pozu dakikalar içinde betimleyebilen modüler otomatik betimleme hattı (s. 2, 6).  
* Metin–poz erişimi, metne koşullu poz üretimi ve poz betimleme üretimi görevleri için temel modeller (s. 2).

**Sınırlılıklar ve gelecek çalışma:**

* Modeller, eğitim verisinde az bulunan kendine temas eden ve baş aşağı pozlarda zorlanmakta; zengin ve karmaşık betimlemelerdeki tüm koşulları karşılamaya çalışmaktadır (s. 12).  
* Otomatik hat eklem koordinatlarını kullandığından uzuv yönelimi ve burulmasını betimlememekte; fiziksel çevre kısıtları kapsam dışıdır (s. 18).  
* Veri setinin çok kişili etkileşimlere genişletilmesi, büyük çok kipli modellerden yararlanılması ve metin tabanlı poz önselinin eylem tanıma gibi alanlarda denenmesi önerilmiştir (s. 12).

**Kısa özet:** Delmas ve ark. (2024), 3B insan pozlarını ayrıntılı doğal dil betimlemeleriyle eşleştiren PoseScript veri setini tanıtmıştır. Veri seti, AMASS'tan seçilen 100,000 poz, 6,283 insan betimlemesi ve kural tabanlı bir "posecode" hattıyla üretilen otomatik betimlemelerden oluşmaktadır (s. 3, 6). Yazarlar veriyi metin–poz erişimi, metne koşullu poz üretimi ve poz betimleme üretiminde kullanmış; otomatik betimlemelerle ön eğitimin üç görevde de performansı yaklaşık iki kat artırdığını bildirmiştir (s. 12). Örneğin insan betimlemelerinde erişim mRecall değeri ön eğitimle 23.0'dan 40.9'a yükselmiştir (s. 8).

**Dikkat:**

* Tablo VIII'de "at the left of", "above" ve "in front of" kategorilerinin eşiği "\> −0.15" olarak verilmiştir; bu aralık "ignored" kategorisinin aralığıyla çakışmaktadır (s. 16).  
* Pitch & roll tanımı tutarsızdır: ana metinde dikeylik y-hiperdüzlemine dik olmak olarak tanımlanırken (s. 5), ekte y-ekseniyle kosinüs benzerliği 0'a yakınsa dikey, 1'e yakınsa yatay denmektedir (s. 14).  
* Ek metinde EXP-2'nin R@50'de daha iyi olduğu söylenmektedir, ancak Tablo X'te R@50 değil R@10 raporlanmıştır (s. 19).


## E2 — Delmas ve ark., Belirtilmemiş — PoseFix: Correcting 3D Human Poses with Natural Language

**Çalışma türü:** Deneysel (veri seti geliştirme ve temel model değerlendirmesi).

**Amaç:** Çalışma, 3B insan pozlarının doğal dil geri bildirimiyle düzeltilmesini ele alır ve kaynak pozun hedef poza nasıl dönüştürüleceğini betimleyen metinlerden oluşan PoseFix veri setini tanıtır. Veri setinin potansiyeli iki görevde sınanır: metne dayalı poz düzenleme ve iki poz arasındaki farka dayalı düzeltici metin üretimi.

**Yöntem:**

* AMASS pozlarından 135k {poz A, poz B, metin değiştirici} üçlüsü otomatik olarak açıklandı; 6157 çift ayrıca Amazon Mechanical Turk'te insanlarca açıklandı ve %70-%10-%20 oranında bölündü (s. 15020–15021). Çiftler aynı diziden (IS, en çok 0.5 saniye arayla) veya farklı dizilerden (OOS) seçildi; poz A, PoseScript özellik benzerliğinde ilk 100 içinden ve en az 15 (IS) / 20 (OOS) farklı düşük düzeyli özellik koşuluyla belirlendi (s. 15020).  
* Otomatik değiştiriciler, "paircode" ve "super-paircode"lardan şablon cümleler üreten kural tabanlı bir hatla oluşturuldu; 135k açıklama 15 dakikadan kısa sürede üretildi ve yalnızca ön eğitimde kullanıldı (s. 15021).  
* Poz düzenleme için VPoser tabanlı poz kodlayıcı (d \= 32), metin kodlayıcı (GloVe \+ bi-GRU veya DistilBERT \+ transformer) ve TIRG füzyon modülünden oluşan koşullu VAE kullanıldı; sol/sağ çevirme, InstructGPT parafrazları, PoseMix ve PoseCopy denendi (s. 15022–15023). Metin üretimi için poz bilgisini istem (prompt) veya çapraz dikkatle alan, açgözlü kod çözmeli otoregresif transformer kullanıldı (s. 15025).  
* Poz düzenleme ELBO, FID ve 30 örnekten en iyisi için MPJE (mm), MPVE (mm) ve geodezik uzaklıkla (derece); metin üretimi BLEU-4, ROUGE-L, METEOR, 32 poz çifti içinde top-k R-precision ve üretilen metinle yeniden yapılandırma ölçütleriyle değerlendirildi (s. 15022, 15025).

**Ana bulgular:**

* Poz düzenlemede otomatik değiştiricilerle ön eğitim, herhangi bir veri artırımından daha büyük etki gösterdi (ELBO'da \+%84); ön eğitimli ortamda artırımların katkısı \+%1'de kaldı (s. 15023).  
* En iyi poz düzenleme modeli (ön eğitim \+ sol/sağ çevirme \+ parafraz) FID 0.13, ELBO 1.44 (jts) / 1.92 (v2v) / 0.97 (rot), MPJE 196 mm, MPVE 162 mm ve geodezik 8.62 değerlerine ulaştı (s. 15023).  
* Tam test setinde (1239 çift) yalnız poz A ile MPJE 219 mm ve FID 0.17, yalnız değiştirici ile MPJE 378 mm ve FID 1.05, ikisi birlikte MPJE 196 mm ve FID 0.13 elde edildi; ELBO (jts) IS alt kümesinde 1.33, OOS'ta 1.53'tür (s. 15024).  
* Metin üretiminde çapraz dikkat istemden iyi sonuç verdi ve ön eğitim R@2'yi %12.27'den %71.35'e çıkardı (s. 15026). Sol/sağ çevirmeyle R@1/R@2/R@3 60.69/71.51/78.85 ve MPJE 189 mm elde edildi; özgün metinlerde bu değerler 62.71/74.01/79.26 ve 196 mm'dir (s. 15026).  
* Düzenleme modeli beden parçalarını ve eylemleri görece iyi kavradı, ancak temas gerektiren talimatlarda ve çömelme ile uzanma pozlarında zorlandı (s. 15024); metin üretim modeli poz A ile B'yi karıştırabildi ve farkların yalnızca bir kısmını betimleyebildi (s. 15026).

**Yazarların sonucu:** Yazarlar, çalışmanın 3B insan pozlarını doğal dil talimatlarıyla düzeltme sorununa temel attığını ve poz çiftleri arasındaki ince farkları yakalamanın yeni bir anlamsal kavrayış düzeyi gerektirdiğini belirtir. PoseFix veri setiyle birlikte iki görev için sunulan temel modellerin umut verici sonuçlar verdiği sonucuna varırlar (s. 15026).

**Katkı:**

* İki 3B pozu, aralarındaki farkı anlatan insan yazımı metinlerle ilişkilendiren PoseFix veri seti; yazarlara göre daha önce bu türde bir veri seti bulunmuyordu (s. 15019).  
* Metne dayalı poz düzenleme görevinin cVAE temel modeliyle tanıtılması ve düzeltici metin üretiminin koşullu otoregresif modelle incelenmesi (s. 15019).

**Sınırlılıklar ve gelecek çalışma:**

* İnsan açıklamalarında poz A'nın bağlamı veri kabul edildiğinden bazı ayrıntılar atlanabiliyor; yazarlar bu zorlukların göreve içkin olduğunu belirtir (s. 15022).  
* Tek referans metin bulunduğu ve farklı talimatlar aynı sonuca götürebildiği için standart NLP ölçütleri model kalitesini güvenilir yansıtmıyor; eklenen ölçütler de kendi sınırlılıkları olan kusurlu modellere dayanıyor (s. 15025–15026).  
* Ayrı bir gelecek çalışma bölümü yok; yazarlar iki yönlü çiftlerin döngü tutarlılığı için, hem betimleme hem değiştirici içeren pozların çoklu görev ortamında kullanılabileceğini belirtir (s. 15020–15021).

**Kısa özet:** Delmas ve ark., 3B insan pozlarının doğal dil geri bildirimiyle düzeltilmesi için AMASS pozlarından oluşturulan, 6157 insan ve 135k otomatik açıklamalı çift içeren PoseFix veri setini sunmuştur. Veri seti, koşullu VAE tabanlı metne dayalı poz düzenleme ve otoregresif transformer tabanlı düzeltici metin üretimi görevlerinde sınanmıştır. Otomatik açıklamalarla ön eğitim her iki görevde belirleyici olmuş, düzenlemede kaynak poz ile metnin birlikte kullanımı en iyi sonucu vermiş ve üretilen metinlerin R-precision değerleri özgün metinlere yaklaşmıştır. Modeller yine de temas talimatlarında, çömelme ve uzanma pozlarında ve kaynak ile hedef pozu ayırt etmede zorlanmıştır.

**Dikkat:**

* Yayın yılı, cilt ve DOI makale metninde yer almıyor; yalnızca ICCV açık erişim sürümü olduğu belirtiliyor (s. 15018).  
* Metinde sonraki deneylerde GloVe \+ bi-GRU kodlayıcının kullanıldığı belirtilirken Şekil 4'teki genel bakışta metin kodlayıcı DistilBERT \+ transformer olarak gösteriliyor (s. 15022–15023).  
* Çıkarım aşamasında sonraki sözcüğün negatif log olabilirliği en büyükleyen sözcük olarak seçildiği yazıyor; açgözlü kod çözme tanımıyla bu ifade tutarsız görünüyor (s. 15025).


## E1 — Fieraru ve ark., 2021 — AIFit: Automatic 3D Human-Interpretable Feedback Models for Fitness Training

**Çalışma türü:** Deneysel (sistem geliştirme ve veri seti tanıtımı).

**Amaç:** Egzersiz yapan kişinin videosundan 3B poz ve hareketi yeniden oluşturan, tekrarları ayıran, eğitmen standartlarından sapmaları belirleyip doğal dilde geri bildirim veren otomatik bir sistem (AIFit) geliştirmek. Ayrıca bu alandaki araştırmayı desteklemek için büyük ölçekli bir veri seti (Fit3D) sunmak.

**Yöntem:**

* **Veri:** Fit3D; 13 katılımcı (1 lisanslı eğitmen, diğerleri farklı düzeyde kursiyer), 37 egzersiz, egzersiz başına en az 5 tekrar; 12 kameralı VICON hareket yakalama ve 4 RGB kamera (s. 9919–9920). 2,964,236 MOCAP 3B iskelet; eğitim/doğrulama 10 katılımcı (2,278,572 görüntü), test 3 katılımcı (685,664 görüntü); elle işaretlenmiş 2,964 tekrar zaman damgası (s. 9921).  
* **3B poz kestirimi:** Human3.6M ile ön eğitimli MubyNet, tek görüş (SV) ve çok görüş (MV) olarak kullanılmış ve Fit3D'de 5 epok ince ayarlanmış (FT); SPIN ile karşılaştırılmış (s. 9924).  
* **Sistem:** Tekrarlar, MPJPE tabanlı poz benzerliğiyle öz-ilintiden bulunan başlangıç periyodu ve kısıtlı doğrusal olmayan eniyilemeyle bölütlenmiş (s. 9921–9922). Eklem açıları, eğitmen hareketindeki enerjiye göre aktif ve pasif kümelere ayrılmış; aktiflere max, min ve korelasyon, pasiflere ortalama ve standart sapma uygulanarak egzersiz imzası çıkarılmış (s. 9923–9924). İstatistiksel koç, imzayı 0–1 arası küresel δ parametresiyle ölçeklenen eşiklerle eğitmen imzasına kıyaslamış; geri bildirim aktif ve pasif dilbilgisiyle üretilmiş (s. 9924).  
* **Değerlendirme:** Poz için MPJPE (mm), bölütleme için IoU, tekrar sayımı için RepNet'e karşı OBO ve MAE (Fit3D testi 444 video, CountixFitness doğrulama 267 video), geri bildirim için gerçek pozlarla üretilen geri bildirime göre doğruluk (s. 9925–9926).

**Ana bulgular:**

* Test kümesinde Procrustes hizalaması olmadan MPJPE, ince ayarlı çok görüşlü MubyNet ile 45.4 mm, ince ayarlı tek görüşlü sürümle 52.4 mm; ince ayarsız MubyNet SV ile 90.4 mm, SPIN SV ile 89.5 mm (s. 9925).  
* Tekrar bölütleme doğruluğu (IoU) gerçek 3B eklemlerle 0.731, MubyNet-MV-FT tahminleriyle 0.730, MubyNet SV ile 0.661 (s. 9925).  
* Fit3D test setinde tekrar sayımında AIFit OBO 0.140 ve MAE 0.253, RepNet OBO 0.520 ve MAE 0.740 elde etmiş (s. 9925).  
* CountixFitness'ta OBO her iki yöntemde 0.292; MAE AIFit için 0.604, RepNet için 0.468 (s. 9925).  
* δ \= 0.5 eşiğinde tahmin edilen 3B pozlarla üretilen geri bildirim, gerçek pozlara dayalı geri bildirime göre aktif ve pasif politikalarda yaklaşık %80 doğruluğa ulaşmış; eşik gevşedikçe doğruluk artmış (s. 9926).

**Yazarların sonucu:** Yazarlara göre AIFit 3B poz ve hareketi yeniden oluşturabilmekte, tekrarları güvenilir biçimde bölütleyip eğitmen modellerinden sapmaları belirleyebilmekte ve yerelleştirilmiş, nicel, görsel olarak temellendirilmiş doğal dil geri bildirimi verebilmektedir (s. 9926). Sistem, insan eğitmenlerin her zaman bulunamadığı salon, açık hava ve ev ortamları için tamamlayıcı bir araç olarak konumlandırılmıştır (s. 9926).

**Katkı:**

* 3B insan algılamaya dayalı ilk otomatik fitness eğitim sistemi olarak AIFit (s. 9919, 9926).  
* 3B hareket yakalama gerçek verisi ve elle işaretlenmiş tekrar sınırları içeren ilk büyük ölçekli fitness veri seti olarak Fit3D (s. 9919, 9921).

**Sınırlılıklar ve gelecek çalışma:**

* Tekrar bölütleme doğruluğu girdi 3B pozların kalitesine bağlıdır; poz hatası arttıkça doğruluk düşer (s. 9925).  
* Yöntem tekrarın bir insan tarafından yapılmasını gerektirir; CountixFitness'ta hatalı olduğunda RepNet'ten daha fazla sapmıştır (s. 9925).  
* Daha katı eşiklerde poz kestirim hataları geri bildirimi daha çok etkiler (s. 9926). Gelecek çalışma: Belirtilmemiş (yalnızca modellerin araştırma için paylaşılacağı söylenmiştir).

**Kısa özet:** Fieraru ve ark. (2021), video tabanlı 3B poz kestirimine dayanan ve fitness egzersizlerinde eğitmen standartlarından sapmaları doğal dilde bildiren AIFit sistemini, 13 katılımcı ve 37 egzersiz içeren Fit3D veri setiyle birlikte sunmuştur. Sistem tekrarları eğitim gerektirmeyen bir öz-ilinti ve eniyileme yöntemiyle bölütlemekte, eklem açılarını aktif ve pasif olarak ayırıp egzersiz imzası çıkarmakta ve bunu ayarlanabilir bir eşikle eğitmen imzasıyla karşılaştırmaktadır. Fit3D'de tekrar sayımında RepNet'ten düşük hata elde edilmiş (OBO 0.140'a karşı 0.520) ve ince ayarlı çok görüşlü poz tahminleriyle bölütleme doğruluğu gerçek pozlarla elde edilene yaklaşmıştır (s. 9925). δ \= 0.5 eşiğinde tahmin edilen pozlarla üretilen geri bildirim, gerçek pozlara dayalı geri bildirimle yaklaşık %80 doğruluk göstermiştir (s. 9926).

**Dikkat:**

* Özet ve girişte 3 milyonu aşan görüntüden söz edilir (s. 9919); ancak veri seti 2,964,236 iskelet olarak verilir ve eğitim/doğrulama ile test görüntü sayılarının toplamı da bu sayıya eşittir (s. 9921).  
* 2B ile 3B poz karşılaştırmasında OBO değerleri 3B, 2B sırasıyla (0.140 ve 0.920), MAE değerleri ise ters sırayla (2.250 ve 0.253) yazılmıştır; 3B'nin her iki ölçütte üstün olduğu iddiasıyla bu sıralama çelişir (s. 9925).  
* δ simgesi hem tekrar bölütlemede ardışık zaman damgaları arasındaki alt sınır (s. 9922\) hem de istatistiksel koçun küresel eşik parametresi (s. 9924\) için kullanılmıştır.
