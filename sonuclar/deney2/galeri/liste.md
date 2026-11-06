# Deney 2 galerisi (ana sistem: açı bandı, yönlü · önden + çapraz · katı)

Her video: solda video + iskelet (kırmızı: grafikteki ölçütün banttan çıktığı uzuv), sağ üstte KARARI VEREN ölçütün açı bandı (kaçırmada gerçek hatanın ölçütü), sağ altta z tablosu ve karar.

En sık karışan hata çiftleri (önden + çapraz): omuz → az kaldırma = 61, baş → az kaldırma = 54, dirsek → az kaldırma = 38, öne kaçma → az kaldırma = 32, omuz → öne kaçma = 13

## omuz silkme (omuz kulağa doğru kalkıyor) → sistem "kol yeterince kalkmıyor" dedi (61 tekrar)

| Dosya | Gerçek | Ek hata | Karar | Görüş | Grafikteki ölçüt | max z | T |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `karisma_omuz_az_kaldirma_1_ex1_Petra_cam2_o45_t5.mp4` | omuz | – | az kaldırma | 0° | kaldirma | 100.00 | 3.69 |
| `karisma_omuz_az_kaldirma_2_ex1_Petra_cam3_o40_t5.mp4` | omuz | – | az kaldırma | 50° | kaldirma | 100.00 | 3.69 |
| `karisma_omuz_az_kaldirma_3_ex1_Terka_cam2_o40_t5.mp4` | omuz | – | az kaldırma | 5° | kaldirma | 100.00 | 3.75 |

## baş yana eğik → sistem "kol yeterince kalkmıyor" dedi (54 tekrar)

| Dosya | Gerçek | Ek hata | Karar | Görüş | Grafikteki ölçüt | max z | T |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `karisma_bas_az_kaldirma_1_ex1_Mima_cam1_o0_t7.mp4` | baş | omuz silkme (omuz kulağa doğru kalkıyor) | az kaldırma | 0° | kaldirma | 52.22 | 3.68 |
| `karisma_bas_az_kaldirma_2_ex1_Mima_cam1_o30_t6.mp4` | baş | omuz silkme (omuz kulağa doğru kalkıyor), dirsek bükük | az kaldırma | -30° | kaldirma | 100.00 | 3.68 |
| `karisma_bas_az_kaldirma_3_ex1_Mima_cam1_o40_t6.mp4` | baş | omuz silkme (omuz kulağa doğru kalkıyor), dirsek bükük | az kaldırma | -40° | kaldirma | 100.00 | 3.68 |

## Kaçırılan hatalar: hatalı tekrar, sistem "doğru" dedi (69 tekrar)

| Dosya | Gerçek | Ek hata | Karar | Görüş | Grafikteki ölçüt | max z | T |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `kacirilan_1_ex1_Terka_cam3_o80_t4.mp4` | öne kaçma | – | doğru | 10° | kol_boyu | 3.65 | 3.75 |
| `kacirilan_2_ex1_Vasil_cam1_o40_t6.mp4` | baş | – | doğru | -40° | bas | 2.68 | 3.46 |
| `kacirilan_3_ex1_Vasil_cam2_o70_t4.mp4` | öne kaçma | – | doğru | -25° | kol_boyu | 0.60 | 3.46 |

## Neye bakmalı?
- **Karışmalarda:** Videoda gerçekten etiketteki hata mı görülüyor, yoksa sistemin söylediği hata da var mı? (Örneğin baş eğerken omuz da kalkıyor olabilir; etiket yalnızca birincil hatayı veriyor.)
- **Grafikteki ölçüt** gerçekten banttan çıkıyor mu, ve çıktığı an videoda o uzvun hareketiyle tutarlı mı?
- **Kaçırılanlarda:** Hata gözle görülüyor mu? Görülüyorsa ölçüt neden yakalamadı (bant geniş mi, kapsam düşük mü, hata kalibrasyon aralığının dışındaki açılarda mı)?
