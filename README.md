# Omuz Silkmesi Tespiti ve Türkçe Geri Bildirim

Tek bir RGB kamerayla **kolu yana kaldırma (omuz abdüksiyonu)** egzersizini izleyen bir sistem. MediaPipe ile çıkarılan iskeletten hatalı tekrarları bulur (odak: omzun kulağa doğru kalkması, "omuz silkmesi"), hatanın türünü belirler (omuz, baş eğme, kolun öne kaçması, dirsek bükme, yetersiz kaldırma) ve kişiye **ne yapacağını söyleyen Türkçe bir cümle** verir. Yöntemin temeli **kişiye özel açı bandı**: kişinin birkaç doğru tekrarından, kolun her açısı için "omzun normal yeri" çıkarılır ve yeni tekrar bu banda göre değerlendirilir. Bütün sonuçlar açık REHAB26-ViewAngles veri setinde, kişi bazlı (birini dışarıda bırak) ölçülür. Bilgisayarlı Görü dersi projesi (sunum: 16 Kasım 2026).

## Sonuçlar (kısaca)

REHAB26-ViewAngles'ın 5 kişisinde, kişi bazlı birini-dışarıda-bırak ile: ham MediaPipe ölçüsü omuz silkmesini zayıf ayırıyor (AUC 0,70); kişinin kendi doğru tekrarlarından kurulan açı bandıyla 0,95'e çıkıyor (önden + çapraz 0,97), başkalarının tekrarlarından kurulan genel bant ise 0,62–0,67'de kalıyor. Önden + çapraz görüşte hata türü hatalı tekrarların 56,6/100'ünde ilk sırada, 67,4/100'ünde ilk iki içinde doğru söyleniyor; doğru tekrarların 7,5/100'ünde gereksiz uyarı çıkıyor. Cümleyi bir LLM'e yazdırmak kurala üstünlük getirmiyor, hatayı LLM'e buldurmak sonucu kötüleştiriyor. Kendi çektiğimiz videoda (tek kişi) 11 hatalı tekrarın 11'inde doğru hata cümlede geçti. Bütün tablolar, sınırlılıklar ve olumsuz sonuçlar: [`sonuclar/OZET.md`](sonuclar/OZET.md).

## Hızlı başlangıç

```bash
python -m venv .venv
.venv\Scripts\activate             # Git Bash: source .venv/Scripts/activate · macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
pytest -q                          # hepsi geçmeli (Deney 1 regresyonu dahil)
```

Veri setini `veri/rehab26/` altına koy (`veri/README.md`). Sonra demo:

```bash
# Veri setinden bir video, veri setinden üretilmiş kalibrasyonla (pencere açılır)
python -m uygulama.main --veri-seti ex1_Honza --kamera cam1 --yonelim 0

# Kendi kameranla: önce 6 doğru tekrarla kalibrasyon, sonra değerlendirme
python -m uygulama.main --isim adin
```

Sıfırdan kurulum ve deneylerin yeniden üretimi: [`docs/YENIDEN_KURULUM.md`](docs/YENIDEN_KURULUM.md) (bütün deneyler: `python -m deneyler.hepsi`).

## Klasörler

| Klasör | İçerik |
| --- | --- |
| `cekirdek/` | Ortak kod: ölçütler, DTW, açı bandı, hata türü, geri bildirim, LLM istemcisi. Deneyler ve uygulama bunu içe aktarır |
| `deneyler/` | Deney betikleri (Deney 1–4, Ex7, sunum şekilleri, `hepsi.py`) |
| `uygulama/` | Demo uygulaması (kalibrasyon, canlı kamera / video, referans iskelet bindirme) |
| `araclar/` | Yardımcı betikler (veri tanıtma, görsel kontrol, kural dışa aktarma) |
| `modeller/` | Uygulamanın kullandığı kural ve eşik dosyaları (JSON) |
| `sonuclar/` | Deney çıktıları (CSV, `ozet.csv`, şekiller) |
| `testler/` | pytest testleri |
| `referans/` | Danışmanın Deney 1 kodu ve beklenen sonuçlar (regresyon testi) |
| `docs/` | Arka plan, ödev tanımı, yeniden kurulum, LLM kullanımı, gelecek çalışma |
| `ilerleme/` | Her adımın özeti (`ADIM_XX.md`) ve kararlar günlüğü (`KARARLAR.md`) |
| `veri/` | Veri setleri (git'e **girmez**) |

`PLAN.md` adım adım yol haritası, `CLAUDE.md` Claude Code ile çalışma kurallarıdır.

## Veri seti ve lisans

- **Veri:** REHAB26-ViewAngles, Zenodo, DOI [10.5281/zenodo.23018128](https://doi.org/10.5281/zenodo.23018128), lisans **CC BY-NC 4.0** (ticari olmayan kullanım, atıf zorunlu). Veri bu depoda **yoktur**; Zenodo'dan indirilir. `sonuclar/` altındaki bazı şekiller veri setinin video karelerinden üretilmiştir ve aynı lisansa tabidir.
- Kişisel kayıtlar (kalibrasyon profilleri `profiller/`, canlı oturumlar `oturumlar/`, kendi videolarımız `veri/kendi_kayit/`) ve bütün `.mp4` dosyaları depoya girmez.
- **Kod:** lisans belirtilmedi.
- Projede üretken yapay zekânın nerede kullanıldığı: [`docs/LLM_KULLANIMI.md`](docs/LLM_KULLANIMI.md).
