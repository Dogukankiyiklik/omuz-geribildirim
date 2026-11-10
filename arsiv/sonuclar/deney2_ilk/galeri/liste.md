# Deney 2 galerisi (ana sistem: açı bandı, yönlü · önden + çapraz · katı)

Her video: solda video + iskelet (kırmızı: grafikteki ölçütün banttan çıktığı uzuv), sağ üstte KARARI VEREN ölçütün açı bandı (kaçırmada gerçek hatanın ölçütü), sağ altta z tablosu ve karar.

En sık karışan hata çiftleri (önden + çapraz): omuz → az kaldırma = 37, öne kaçma → az kaldırma = 23, dirsek → öne kaçma = 23, baş → omuz = 20, dirsek → omuz = 16

## omuz silkme (omuz kulağa doğru kalkıyor) → sistem "kol yeterince kalkmıyor" dedi (37 tekrar)

| Dosya | Gerçek | Ek hata | Karar | Görüş | Grafikteki ölçüt | max z | T |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `karisma_omuz_az_kaldirma_1_ex1_Petra_cam2_o40_t5.mp4` | omuz | – | az kaldırma | 5° | kaldirma | 18.98 | 4.28 |
| `karisma_omuz_az_kaldirma_2_ex1_Petra_cam2_o70_t5.mp4` | omuz | – | az kaldırma | -25° | kaldirma | 16.62 | 4.28 |
| `karisma_omuz_az_kaldirma_3_ex1_Petra_cam3_o60_t5.mp4` | omuz | – | az kaldırma | 30° | kaldirma | 17.95 | 4.28 |

## kol öne kaçıyor → sistem "kol yeterince kalkmıyor" dedi (23 tekrar)

| Dosya | Gerçek | Ek hata | Karar | Görüş | Grafikteki ölçüt | max z | T |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `karisma_one_kacma_az_kaldirma_1_ex1_Honza_cam1_o20_t4.mp4` | öne kaçma | – | az kaldırma | -20° | kaldirma | 5.61 | 4.03 |
| `karisma_one_kacma_az_kaldirma_2_ex1_Honza_cam1_o30_t4.mp4` | öne kaçma | – | az kaldırma | -30° | kaldirma | 7.31 | 4.03 |
| `karisma_one_kacma_az_kaldirma_3_ex1_Terka_cam2_o80_t4.mp4` | öne kaçma | – | az kaldırma | -35° | kaldirma | 3.86 | 3.77 |

## Kaçırılan hatalar: hatalı tekrar, sistem "doğru" dedi (106 tekrar)

| Dosya | Gerçek | Ek hata | Karar | Görüş | Grafikteki ölçüt | max z | T |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `kacirilan_1_ex1_Vasil_cam1_o40_t4.mp4` | öne kaçma | – | doğru | -40° | kol_boyu | 0.06 | 5.00 |
| `kacirilan_2_ex1_Vasil_cam1_o60_t5.mp4` | omuz | – | doğru | -60° | YENI | 3.78 | 5.00 |
| `kacirilan_3_ex1_Vasil_cam3_o40_t6.mp4` | baş | – | doğru | 50° | bas | 2.91 | 5.00 |

## Neye bakmalı?
- **Karışmalarda:** Videoda gerçekten etiketteki hata mı görülüyor, yoksa sistemin söylediği hata da var mı? (Örneğin baş eğerken omuz da kalkıyor olabilir; etiket yalnızca birincil hatayı veriyor.)
- **Grafikteki ölçüt** gerçekten banttan çıkıyor mu, ve çıktığı an videoda o uzvun hareketiyle tutarlı mı?
- **Kaçırılanlarda:** Hata gözle görülüyor mu? Görülüyorsa ölçüt neden yakalamadı (bant geniş mi, kapsam düşük mü, hata kalibrasyon aralığının dışındaki açılarda mı)?
