# Deney 1 galerisi (YENI, basit eşik)

Basit eşik (yalnızca bu galeri için): E > eşik ise "şüpheli". Eşik = test kişisi hariç diğer 4 kişinin doğru tekrarlarındaki E'nin %90'lık dilimi. Sistemin asıl karar kuralı Deney 2'dedir (cekirdek/hata_turu.py).

Grup büyüklükleri (3 kamera dahil): yakalanan_silkme = 124, kacirilan_silkme = 41, yanlis_alarm = 84

## Doğru yakalanan silkmeler
Silkme etiketli, sistem şüpheli dedi.

| Dosya | Gerçek etiket | Ek hata | Görüş | E | Eşik |
| --- | --- | --- | --- | --- | --- |
| `yakalanan_silkme_1_ex1_Petra_cam1_o50_t5.mp4` | omuz silkme (omuz kulağa doğru kalkıyor) | – | -50° (çapraz (30–60°)) | 0.459 | 0.286 |
| `yakalanan_silkme_2_ex1_Petra_cam3_o60_t5.mp4` | omuz silkme (omuz kulağa doğru kalkıyor) | – | 30° (çapraz (30–60°)) | 0.393 | 0.286 |
| `yakalanan_silkme_3_ex1_Terka_cam3_o45_t5.mp4` | omuz silkme (omuz kulağa doğru kalkıyor) | – | 45° (çapraz (30–60°)) | 0.499 | 0.279 |

## Kaçırılan silkmeler
Silkme etiketli, sistem normal dedi.

| Dosya | Gerçek etiket | Ek hata | Görüş | E | Eşik |
| --- | --- | --- | --- | --- | --- |
| `kacirilan_silkme_1_ex1_Honza_cam3_o0_t5.mp4` | omuz silkme (omuz kulağa doğru kalkıyor) | – | 90° (profil (70–90°)) | 0.094 | 0.288 |
| `kacirilan_silkme_2_ex1_Mima_cam1_o30_t5.mp4` | omuz silkme (omuz kulağa doğru kalkıyor) | dirsek bükük | -30° (çapraz (30–60°)) | 0.242 | 0.272 |
| `kacirilan_silkme_3_ex1_Mima_cam1_o60_t4.mp4` | omuz silkme (omuz kulağa doğru kalkıyor) | baş yana eğik | -60° (çapraz (30–60°)) | 0.102 | 0.272 |

## Yanlış alarm verilen doğru tekrarlar
Doğru etiketli, sistem şüpheli dedi.

| Dosya | Gerçek etiket | Ek hata | Görüş | E | Eşik |
| --- | --- | --- | --- | --- | --- |
| `yanlis_alarm_1_ex1_Terka_cam1_o20_t10.mp4` | doğru | – | -20° (önden (0–20°)) | 0.353 | 0.279 |
| `yanlis_alarm_2_ex1_Terka_cam2_o80_t10.mp4` | doğru | – | -35° (çapraz (30–60°)) | 0.368 | 0.279 |
| `yanlis_alarm_3_ex1_Vasil_cam3_o10_t9.mp4` | doğru | – | 80° (profil (70–90°)) | 0.322 | 0.267 |

## Neye bakmalı?
- **İskelet oturuyor mu?** Yeşil noktalar kişinin kulak, omuz, dirsek, bilek ve kalçasına oturuyor mu? Oturmuyorsa ya MediaPipe yanılmış ya da video ile iskelet arasında kare kayması var.
- **Referans (turkuaz) mantıklı mı?** Kol hareketi zamanda yeşil ile birlikte mi ilerliyor (DTW)? Kalçalar üst üste mi? Silkmede turkuaz kulak–omuz çizgisi yeşilden uzun görünmeli (referansta omuz kulaktan daha uzak).
- **Kırmızı ne zaman yanıyor?** Kulak–omuz çizgisi kırmızıyken videoda omuz gerçekten kulağa doğru kalkıyor mu?
- **Kaçırılan silkmelerde:** Silkme gözle görülüyor mu? Görülmüyorsa etiket/performans belirsiz olabilir; görülüyorsa ölçüt neden kaçırdı (profil görüş mü, bant mı geniş)?
- **Yanlış alarmlarda:** Kişi gerçekten omzunu kaldırıyor mu (etiket hatası olabilir), yoksa başka bir şey mi (gövde eğilmesi, MediaPipe titremesi, referans tekrarın kendisi mi tuhaf)?
