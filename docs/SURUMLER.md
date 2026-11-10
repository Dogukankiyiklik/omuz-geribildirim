# Sürümler (Karar 37, 54)

Alındığı tarih: 9 Kasım 2026 (dondurma), `.venv`. 7 Kasım taslağıyla `pip freeze` birebir aynı.

## Python
`Python 3.11.9` (Windows 11).

## `pip freeze`
```text
absl-py==2.5.1
certifi==2026.10.23
cffi==2.1.1
colorama==0.4.6
contourpy==1.3.3
cycler==0.12.1
et_xmlfile==2.0.0
flatbuffers==25.12.19
fonttools==4.68.0
iniconfig==2.3.1
kiwisolver==1.5.1
llvmlite==0.50.0
matplotlib==3.11.2
mediapipe==1.2.2
numba==0.68.1
numpy==2.4.6
opencv-contrib-python==5.0.0.93
opencv-python==5.0.0.93
openpyxl==3.1.5
packaging==26.3
pandas==3.1.1
pillow==13.0.0
pluggy==1.7.0
pycparser==3.12
Pygments==2.21.0
pyparsing==3.3.3
pytest==9.2.0
python-dateutil==4.0.0
scipy==1.17.1
sounddevice==0.5.6
tzdata==2026.6
```

## MediaPipe sürüm notu
- **Veri seti:** REHAB26'nın iskeletleri MediaPipe **v0.10.20**, Full model ile üretildi (Zenodo sayfası).
- **Uygulama:** MediaPipe **1.2.2**, `pose_landmarker_full`, VIDEO modu. 0.10.20 kurulmadı: numpy'yi 2.4.6'dan 1.26.4'e indirip OpenCV'yi değiştirecekti, bu da raporlanmış deneylerin ortamını bozardı (Karar 27; `arsiv/ilerleme/ADIM_06.md`).
- **Ölçülen fark:** aynı Honza karelerinde (ex1_Honza, cam1, yönelim 0) kol açısı farkı medyan **0,92°**, %95 **3,09°** (`sonuclar/uygulama_saglik/ex1_Honza_cam1_o0_poz_farki.csv`). Sınırlılık olarak raporlanır.
- Deneyler MediaPipe'ı çalıştırmaz; veri setinin hazır iskeletlerini kullanır. Bu yüzden deney sonuçları MediaPipe sürümüne bağlı değildir.
- **Ölçütte etkisi (Karar 52):** arşivdeki siluet denemesinde (6b) aynı 1363 tekrarda YENI ölçütü 1.2.2 noktalarıyla AUC silkme/doğru 0,969, veri setinin 0.10.20 noktalarıyla 0,968 (`arsiv/sonuclar/siluet/ozet.csv`). Sürüm farkı bu ölçütü pratikte etkilemiyor; Karar 27'nin sınırlılık notu hafifler.
- Kendi kayıt (Adım 7) ve arşivdeki siluet denemesi MediaPipe 1.2.2 ile çalıştırıldı; noktaları önbellekte (`veri/ara/`).

## Yapay zekâ modelleri
- **Deney 4 (arşivde):** Google Gemini ücretsiz katmanı, `gemini-3.5-flash-lite`, temperature 0; 7 Kasım 2026. Ayrıntı: `arsiv/ilerleme/ADIM_08.md`. Uygulama LLM kullanmaz.
- **Claude Code / Claude:** kod ve planlama için (`docs/LLM_KULLANIMI.md`); sonuçları üreten kodun parçası değil.
