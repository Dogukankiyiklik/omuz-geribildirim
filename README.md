# Omuz Silkmesi Tespiti ve Türkçe Geri Bildirim

Tek kamerayla kolu yana kaldırma egzersizini izleyen bir sistem. Omuz silkmesi başta olmak üzere hataları bulur ve kişiye Türkçe, ne yapacağını söyleyen bir geri bildirim verir. Bilgisayarlı Görü dersi projesi.

## Klasörler

| Klasör | İçerik |
| --- | --- |
| `CLAUDE.md` | Claude Code'un kuralları (her oturumda okunur) |
| `PLAN.md` | Adım adım yol haritası ve tarihler |
| `docs/ARKA_PLAN.md` | Problem, yöntem, literatür, Deney 1 sonuçları |
| `docs/ODEV.md` | Hocanın ödev tanımı ve bizim karşılığımız |
| `ilerleme/` | Her adımın özeti (`ADIM_XX.md`) ve kararlar günlüğü |
| `cekirdek/` | Ortak kod: ölçütler, DTW, bant, hata türü, geri bildirim |
| `deneyler/` | Deney betikleri |
| `uygulama/` | Demo uygulaması |
| `araclar/` | Yardımcı betikler (veri küçültme vb.) |
| `referans/` | Danışmanın yazdığı Deney 1 kodu ve beklenen sonuçlar |
| `veri/` | Veri dosyaları (git'e girmez) |
| `sonuclar/` | Deney çıktıları |
| `testler/` | Otomatik testler |

## İlk kurulum

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

Sonra `veri/README.md` dosyasındaki dosyaları `veri/` klasörüne koy.

## Claude Code ile çalışma

1. Proje klasöründe Claude Code'u başlat.
2. İlk mesaj: **"CLAUDE.md ve PLAN.md'yi oku, Adım 0'dan başla."**
3. Her adım bitince Claude Code `ilerleme/ADIM_XX.md` dosyasını yazar.
4. 📤 işaretli adımlardan sonra o dosyayı ve ilgili `ozet.csv` dosyasını danışman Claude sohbetine gönder.
5. Danışmanın düzeltmeleri varsa Claude Code'a ilet: "Danışman şunu söyledi: …".
