# Sürümler

Ortam: `.venv`, Python **3.11.9**, Windows 11. Aşağıdaki liste 10 Kasım 2026'da `pip freeze` ile yeniden alındı ve 9 Kasım'daki dondurma listesiyle birebir aynı. `requirements.txt` kritik paketleri bu sürümlere sabitler.

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

## MediaPipe sürüm farkı
- **Veri seti:** REHAB26'nın iskeletleri MediaPipe **v0.10.20**, Full modeliyle üretildi (Zenodo sayfası).
- **Uygulama:** MediaPipe **1.2.2**, `pose_landmarker_full`, VIDEO modu. 0.10.20 kurulmadı, çünkü numpy'yi 2.4.6'dan 1.26.4'e indirip OpenCV'yi değiştirecekti; bu da deneylerin ortamını bozardı.
- **Deneyler etkilenmez:** deneyler MediaPipe'ı çalıştırmaz, veri setinin hazır iskeletlerini kullanır.
- **Ölçülen fark:** aynı Honza karelerinde (ex1_Honza, cam1, yönelim 0) kol açısı farkı medyan **0,92°**, %95 **3,09°** (`sonuclar/uygulama_saglik/ex1_Honza_cam1_o0_poz_farki.csv`).
- **Silkme ölçüsüne etkisi:** aynı 1363 tekrarda kulak–omuz ölçüsünün AUC'si (silkme / doğru) 1.2.2 noktalarıyla 0,969, veri setinin 0.10.20 noktalarıyla 0,968 (`sonuclar/siluet/ozet.csv`, `v-sunum` etiketinde). Sürüm farkı bu ölçüyü pratikte etkilemiyor; yine de sınırlılık olarak raporlanır.
- Kendi kayıt deneyi MediaPipe 1.2.2 ile çalıştırıldı; noktaları `veri/ara/kendi_kayit/` önbelleğinde.

## Yapay zekâ araçları
Uygulama LLM kullanmaz. Geliştirmede kullanılan araçlar: [`LLM_KULLANIMI.md`](LLM_KULLANIMI.md).
