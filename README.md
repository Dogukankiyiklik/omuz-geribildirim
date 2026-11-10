# Omuz Silkmesi Tespiti ve Türkçe Geri Bildirim

Bilgisayarlı Görü dersi ara sınav projesi (sunum: 16 Kasım 2026).

Tek bir RGB kamerayla **kolu yana kaldırma** egzersizini izleyen bir uygulama. MediaPipe ile çıkarılan iskeletten hatalı tekrarları bulur. Odak, omzun kulağa doğru kalkması, yani **omuz silkmesi**. Hatanın türünü belirler (omuz, baş eğme, kolun öne kaçması, dirsek bükme, yetersiz kaldırma) ve kişiye derecesiyle **ne yapacağını söyleyen Türkçe bir cümle** verir: *"Kolunu 110 dereceye kadar kaldırdın; normalde 140 dereceye çıkıyorsun. Kolunu yaklaşık 30 derece daha yukarı kaldır."*

Yöntemin temeli **kişiye özel açı bandı**: kişinin 6 doğru tekrarından, kolun her açısı için "omzun normal yeri" çıkarılır ve yeni tekrar bu banda göre değerlendirilir.

## Ödevin üç problemi ve karşılıkları

| Problem | Uygulamada | Ayrıntı |
| --- | --- | --- |
| **P1** Hareket doğruluğu ve doğal dil geri bildirimi | 5 ölçü, hata türü, derece içeren Türkçe düzeltme cümlesi; doğru tekrarda olumlu cümle | [`docs/SISTEM.md`](docs/SISTEM.md) §5–6 |
| **P2** Omuzun hassas ölçümü | Ham omuz ölçüsünün yetersizliği gösterildi (AUC 0,70); kişiye özel, kol açısına koşullu bantla 0,95 | [`docs/DENEYLER.md`](docs/DENEYLER.md) Soru 1 |
| **P3** Referans ile kullanıcıyı çakıştırma | Her tekrar sonrası DTW (zaman) + öteleme/ölçek/döndürme (geometri) ile hizalanmış referans iskelet; banttan çıkan uzuv kırmızı | [`docs/SISTEM.md`](docs/SISTEM.md) §7 |

## Nereden başlamalı?

1. **[`docs/SISTEM.md`](docs/SISTEM.md)**: sistem adım adım nasıl çalışıyor (raporun 7 başlığı), hocanın sorabileceği sorular, literatürden ne alındı.
2. **[`docs/DENEYLER.md`](docs/DENEYLER.md)**: üç soru, üç cevap; denenip işe yaramayanlar; sınırlılıklar.
3. **[`docs/DEMO.md`](docs/DEMO.md)**: sunumda demo nasıl yapılır, sorun çıkarsa ne yapılır.
4. **[`docs/ODEV.md`](docs/ODEV.md)**: hocanın ödev şartları ve bizdeki karşılıkları.

## Hızlı başlangıç

```bash
python -m venv .venv
.venv\Scripts\activate             # Git Bash: source .venv/Scripts/activate · macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
pytest -q                          # testler (veri seti yoksa veri gerektirenler atlanır)
```

```bash
# Kendi kameranla: önce 6 doğru tekrarla kalibrasyon, sonra değerlendirme
python -m uygulama.main --isim adin

# Kayıtlı profille bir video dosyası
python -m uygulama.main --profil profiller/adin.npz --video test.mp4

# Veri setinden bir video (veri seti veri/rehab26/ altında olmalı)
python -m uygulama.main --veri-seti ex1_Honza --kamera cam1 --yonelim 0
```

Sıfırdan kurulum, veri seti ve deneylerin yeniden üretimi: [`docs/YENIDEN_KURULUM.md`](docs/YENIDEN_KURULUM.md).

## Klasörler

| Klasör | İçerik |
| --- | --- |
| `uygulama/` | Uygulama: kamera/video, kalibrasyon, panel, bindirmeli oynatım (`main.py`), pencere açmadan CSV (`toplu.py`) |
| `cekirdek/` | Ortak kod: ölçüler, açı bandı, hata türü, Türkçe cümle, DTW, bindirme. Uygulama ve deneyler aynı kodu kullanır |
| `deneyler/` | Deney betikleri (Deney 1, 1b, 2, 3, tekrar ayırma, kendi kayıt, sunum şekilleri) ve hepsini yeniden üreten `hepsi.py` |
| `araclar/` | Uygulamanın kural dosyasını üreten `kural_disa_aktar.py`, görsel kontrol aracı |
| `modeller/` | Uygulamanın kullandığı kural ve eşik dosyaları (JSON) |
| `sonuclar/` | Deney çıktıları (CSV, `ozet.csv`, sunum şekilleri) |
| `testler/` | pytest testleri |
| `referans/` | İlk Deney 1 kodu ve beklenen sonuçlar (regresyon testi) |
| `docs/` | Belgeler (yukarıdaki liste) |
| `arsiv/` | Ödevin parçası olmayan her şey: bildiri deneyleri, geliştirme kayıtları. Neden orada olduklarını [`arsiv/README.md`](arsiv/README.md) anlatır |
| `veri/` | Veri setleri (git'e **girmez**) |

## Veri seti ve lisans

- **Veri:** REHAB26-ViewAngles, Zenodo, DOI [10.5281/zenodo.23018128](https://doi.org/10.5281/zenodo.23018128), lisans **CC BY-NC 4.0** (ticari olmayan kullanım, atıf zorunlu). Veri bu depoda **yoktur**; Zenodo'dan indirilir (`veri/README.md`). `sonuclar/` altındaki bazı şekiller veri setinin video karelerinden üretildi ve aynı lisansa tabidir.
- Kişisel kayıtlar (`profiller/`, `oturumlar/`, `veri/kendi_kayit/`) ve bütün `.mp4` dosyaları depoya girmez.
- **Kod:** lisans belirtilmedi.
- Üretken yapay zekânın nerede kullanıldığı: [`docs/LLM_KULLANIMI.md`](docs/LLM_KULLANIMI.md).
