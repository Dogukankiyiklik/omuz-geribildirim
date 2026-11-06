# Arka plan — neden bu proje, neye dayanıyor

Bu dosya Claude Code'un ve kullanıcının projenin bilimsel arka planını hızlıca hatırlaması içindir. Ayrıntılı literatür raporu ayrı bir dokümanda; kullanıcıda link var. Makale kimlikleri (M01, M39…) o rapordaki numaralardır.

## Problem

Fizyoterapide kolu yana kaldırırken (omuz abdüksiyonu) sık görülen bir hata, omzu kulağa doğru silkmektir: kişi kolu kaldıramadığı yerde omzuyla telafi eder. Bu hatayı tek RGB kamerayla tespit etmek iki sebeple zor:

1. **Biyolojik:** Doğru harekette de kürek kemiği döner ve omuz kuşağı bir miktar yükselir (skapulohumeral ritim). Hata, bu yükselmenin normalden fazla olmasıdır.
2. **Ölçüm:** MediaPipe gibi seyrek noktalı modeller omzu tek bir nokta olarak verir; kol kalktıkça bu nokta da kayar.

Bu yüzden sabit eşikli kurallar başarısız olur. M01 (Sensors 2026) bunu açıkça gösteriyor: omuz yükselmesinde F1 yaklaşık 0,55, doğru tekrarların %14'ünde yanlış alarm. Ayrıca mevcut sistemler geri bildirimi ya sayı olarak veriyor (M09) ya da LLM'e serbest bıraktırıyor (M21). İkincisinde LLM kendi eşiğini uyduruyor ve aşırı özgüvenli davranıyor; üstelik cümlelerin doğruluğu hiç sayıyla ölçülmemiş.

## Yaklaşım

- **Kişiye özel tolerans bandı (M39):** Kişinin doğru tekrarları kol açısına göre DTW ile hizalanır. Her an ve her ölçüt için ortalama μ ile tolerans τ hesaplanır (%95 güven aralığı, t dağılımı, alt sınır olarak τ'ların birinci çeyreği). Yeni tekrarın bant dışına çıkma miktarı 0–1 aralığına ölçeklenir ve tekrar boyunca ortalanır: bu E'dir. **Bu yöntem bizim katkımız değil, M39'dan alındı.**
- **Katkılarımız:**
  1. Omuz silkme ölçütlerinin aynı veri üzerinde, bantlı ve bantsız, farklı kamera açılarında karşılaştırılması (Deney 1, 1b).
  2. Hata türünü bulma ve bunu kural tabanlı Türkçe "performans bilgisi" (KP) cümlesine çevirme; cümlenin doğru hatayı adlandırıp adlandırmadığının veri setinin hata türü etiketleriyle **nicel** ölçülmesi (Deney 2, 3).
  3. Kural tabanlı ve LLM tabanlı geri bildirimin karşılaştırılması (Deney 4, bildiri katmanı).

## Deney 1 sonuçları (referans kod, tohum 0, en-boy 9/16)

AUC = rastgele bir silkme tekrarının rastgele bir doğru tekrardan yüksek skor alma olasılığı.

| Ölçüt | Bantsız | Bantlı | Bantlı, %95 GA (kişi bootstrap) | Önden | Çapraz | Profil | Silkme / diğer hatalar |
| --- | --- | --- | --- | --- | --- | --- | --- |
| YENI (kulak–omuz) | 0,70 | 0,91 | 0,85–0,96 | 0,94 | 0,93 | 0,78 | 0,71 |
| M33 (omuz ortasına göre) | 0,64 | 0,90 | 0,82–0,97 | 0,92 | 0,91 | 0,85 | 0,64 |
| M39_F2 (omuz–omuz–kalça) | 0,60 | 0,89 | 0,81–0,96 | 0,89 | 0,92 | 0,80 | 0,64 |
| M01_tek | 0,66 | 0,87 | 0,82–0,92 | 0,90 | 0,89 | 0,75 | 0,66 |
| M01 (iki omuz ort.) | 0,65 | 0,82 | 0,78–0,88 | 0,88 | 0,83 | 0,67 | 0,64 |

**Öne çıkanlar**
- **Kişiye özel bant en büyük kazanç.** Bantsız 0,60–0,70, bantlı 0,82–0,91.
- **YENI en iyi**, ama M33 ve M39_F2'den farkı anlamlı değil: YENI − F2 = 0,022, %95 GA −0,018 ile 0,061 arası.
- **M01'in iki omuz ortalaması** tek taraflı silkmeyi seyreltiyor.
- **Profil görünüm kötü.**
- **Yanlış en-boy oranı** (1:1) açı tabanlı F2'yi 0,89'dan 0,83'e düşürüyor.
- **Ana zayıflık:** silkmeyi diğer hatalardan ayırmak (AUC 0,64–0,71). Tek bir ölçüt "bir şey yanlış" diyor, "yanlış olan omuz" diyemiyor. En çok karışan hata baş eğme. Deney 2 bu sorun için var.

## Veri seti

**REHAB26-ViewAngles** (M39; Zenodo 10.5281/zenodo.23018128; lisans CC BY-NC 4.0).
- 5 sağlıklı kişi (Honza, Mima, Petra, Terka, Vasil), 3 egzersiz.
- 11 yönelim (0–90°, 10° aralıklarla, artı 45°) × 3 telefon kamerası.
- Her yönelimde yaklaşık 5 doğru ve 5 hatalı tekrar; her hatalı tekrarda tek bir **etiketli birincil hata** var.
- Ex1'de (kol abdüksiyonu, sağ kol): 278 doğru, 55 omuz yükselmesi (birincil), 19 tekrarda omuz yükselmesi ek hata olarak işaretli.
- Hatalar sağlıklı kişilerin taklidi; bu bir sınırlama.

**REHAB24-6** (M34): 10 kişi, 6 egzersiz, 2 kamera + mocap. Yalnızca doğru/yanlış etiketi var. İsteğe bağlı dış doğrulama için.

## Önemli makaleler (rapordaki kimliklerle)

| ID | Kısaca | Projede nerede |
| --- | --- | --- |
| M01 | Cihaz üzerinde telafi tespiti; omuz yükselmesi en zayıf işaret; izotropik normalizasyon uyarısı; 4 durumlu faz makinesi | Temel çizgi ölçütü, uygulamada tekrar ayırma |
| M39 | Kişiye özel tolerans bandı; kamera açısı; REHAB26 | Bant yöntemi, veri, F1–F5 ölçütleri |
| M33 | Düşük maliyetli sanal koç; omuz yükselmesi boyna göre; durum makineli geri bildirim | Ölçüt, uygulama geri bildirim tasarımı |
| M21 | LLM ile rehabilitasyon geri bildirimi; eşik uydurma, aşırı özgüven; Ex1'de omuz özelliği yok | Deney 4 karşılaştırması |
| M45 / E2 | PoseScript / PoseFix: pozdan ve poz farkından kural tabanlı metin | Sapma kodu → cümle fikri |
| E1 | AIFit: eğitmen referansına göre istatistiksel koç, doğal dil geri bildirim | En yakın öncül, farkımız |
| M23 | PAC taksonomisi: KR (sonuç bilgisi) → KP (performans bilgisi) boşluğu | Motivasyon |
| M22 | Tek örnekle alt dizi DTW ile tekrar ayırma | Canlı tekrar ayırma (alternatif) |
| M12 | Kişi içi model %83–95, kişiler arası %50–70 | Kişiye özel referans gerekçesi |
| M34 | REHAB24-6; 2B tercih edilmeli | İsteğe bağlı doğrulama |
