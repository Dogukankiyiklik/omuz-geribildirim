# Deney 1 galerisi (YENI, geçici eşik, yalnızca önden (0–20°))

Geçici karar: E > eşik ise "şüpheli". Eşik = test kişisi hariç diğer 4 kişinin doğru tekrarlarındaki E'nin %90'lık dilimi. Gerçek karar kuralı Adım 4'te gelecek.

Grup büyüklükleri (3 kamera dahil): yakalanan_silkme = 47, kacirilan_silkme = 8, yanlis_alarm = 30

## Doğru yakalanan silkmeler
Silkme etiketli, sistem şüpheli dedi.

| Dosya | Gerçek etiket | Ek hata | Görüş | E | Eşik |
| --- | --- | --- | --- | --- | --- |
| `yakalanan_silkme_1_ex1_Petra_cam2_o30_t5.mp4` | omuz silkme (omuz kulağa doğru kalkıyor) | – | 15° (önden (0–20°)) | 0.400 | 0.286 |
| `yakalanan_silkme_2_ex1_Petra_cam3_o90_t5.mp4` | omuz silkme (omuz kulağa doğru kalkıyor) | – | 0° (önden (0–20°)) | 0.371 | 0.286 |
| `yakalanan_silkme_3_ex1_Terka_cam3_o70_t5.mp4` | omuz silkme (omuz kulağa doğru kalkıyor) | – | 20° (önden (0–20°)) | 0.531 | 0.279 |

## Kaçırılan silkmeler
Silkme etiketli, sistem normal dedi.

| Dosya | Gerçek etiket | Ek hata | Görüş | E | Eşik |
| --- | --- | --- | --- | --- | --- |
| `kacirilan_silkme_1_ex1_Petra_cam1_o0_t5.mp4` | omuz silkme (omuz kulağa doğru kalkıyor) | – | 0° (önden (0–20°)) | 0.176 | 0.286 |
| `kacirilan_silkme_2_ex1_Vasil_cam3_o80_t6.mp4` | omuz silkme (omuz kulağa doğru kalkıyor) | – | 10° (önden (0–20°)) | 0.116 | 0.267 |
| `kacirilan_silkme_3_ex1_Vasil_cam3_o90_t5.mp4` | omuz silkme (omuz kulağa doğru kalkıyor) | – | 0° (önden (0–20°)) | 0.223 | 0.267 |

## Yanlış alarm verilen doğru tekrarlar
Doğru etiketli, sistem şüpheli dedi.

| Dosya | Gerçek etiket | Ek hata | Görüş | E | Eşik |
| --- | --- | --- | --- | --- | --- |
| `yanlis_alarm_1_ex1_Terka_cam1_o20_t10.mp4` | doğru | – | -20° (önden (0–20°)) | 0.353 | 0.279 |
| `yanlis_alarm_2_ex1_Terka_cam2_o60_t2.mp4` | doğru | – | -15° (önden (0–20°)) | 0.298 | 0.279 |
| `yanlis_alarm_3_ex1_Vasil_cam2_o60_t1.mp4` | doğru | – | -15° (önden (0–20°)) | 0.529 | 0.267 |

## Neye bakmalı?
- **İskelet oturuyor mu?** Yeşil noktalar kişinin kulak, omuz, dirsek, bilek ve kalçasına oturuyor mu? Oturmuyorsa ya MediaPipe yanılmış ya da video ile iskelet arasında kare kayması var.
- **Referans (turkuaz) mantıklı mı?** Kol hareketi zamanda yeşil ile birlikte mi ilerliyor (DTW)? Kalçalar üst üste mi? Silkmede turkuaz kulak–omuz çizgisi yeşilden uzun görünmeli (referansta omuz kulaktan daha uzak).
- **Kırmızı ne zaman yanıyor?** Kulak–omuz çizgisi kırmızıyken videoda omuz gerçekten kulağa doğru kalkıyor mu?
- **Kaçırılan silkmelerde:** Silkme gözle görülüyor mu? Görülmüyorsa etiket/performans belirsiz olabilir; görülüyorsa ölçüt neden kaçırdı (profil görüş mü, bant mı geniş)?
- **Yanlış alarmlarda:** Kişi gerçekten omzunu kaldırıyor mu (etiket hatası olabilir), yoksa başka bir şey mi (gövde eğilmesi, MediaPipe titremesi, referans tekrarın kendisi mi tuhaf)?
