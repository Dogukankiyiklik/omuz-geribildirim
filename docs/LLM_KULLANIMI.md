# Üretken yapay zekâ kullanımı

Ödevin kuralı gereği projede üretken yapay zekânın nerede ve hangi amaçla kullanıldığı aşağıda. Rapor için kısa not en altta.

## Claude Code (Anthropic): kod ve belgeler
- `cekirdek/`, `deneyler/`, `uygulama/`, `araclar/` ve `testler/` altındaki kodun yazılması.
- Hata ayıklama, testler ve kısa sınamalar.
- Deneylerin bir kısmının, kullanıcının isteğiyle çalıştırılması. Son yeniden üretimi (10 Kasım 2026, `sonuclar/hepsi/`) Claude Code çalıştırdı.
- Geliştirme kayıtları (`arsiv/ilerleme/`), belgeler (`docs/`, klasörlerdeki README'ler) ve sunum şekilleri (`deneyler/sunum_sekilleri.py`; 10 Kasım 2026'da kaldırıldı, git geçmişinde `cc39d2a`). Belgelerdeki sayılar sonuç dosyalarından kopyalandı.
- Ödeve göre sadeleştirme (10 Kasım 2026): ödev dışı dosyaların `arsiv/` altına taşınması, kalıntıların temizlenmesi ve belgelerin yeniden yazılması. Aynı gün, kullanıcının isteğiyle Deney 1–3 uygulamanın kullandığı tek yönteme indirildi, sunum şekilleri betiği ve görsel kontrol aracı kaldırıldı, çekirdekte artık kullanılmayan kod silindi; her adımda bütün sonuçların birebir aynı yeniden üretildiği `deneyler/hepsi.py` ile denetlendi.

## Claude (ayrı sohbet): planlama ve yorum
- Literatür taraması (`arsiv/docs/ARKA_PLAN.md`).
- Planlama (`arsiv/PLAN.md`) ve güncellemeler (`arsiv/ilerleme/GUNCELLEME_XX.md`).
- Sonuçların yorumu ve karar önerileri (`arsiv/ilerleme/KARARLAR.md`). Deneylerin ölçütleri ve yöntem ayrıntıları çoğunlukla sonuçtan önce yazılıp commit'lendi ("önceden kayıt"); sonradan yapılan analizler kayıtlarda öyle işaretlendi.
- Çekim sırasında kullanılan suflör sayfası (`arsiv/docs/cekim_suflor.html`).

## Gemini (Google, ücretsiz katman): yalnızca arşivdeki bir yan deney
- LLM karşılaştırma deneyinde (Deney 4) karşılaştırma koşulu olarak: sapma kodundan cümle yazdırmak ve ham özetten hem hatayı hem cümleyi buldurmak.
- Model: `gemini-3.5-flash-lite`, temperature 0; istekler 7 Kasım 2026'da gönderildi. İstemler `arsiv/deneyler/istemler/` altında.
- **Ürünün yöntemi değildir.** Uygulamadaki geri bildirim tamamen kural tabanlıdır (`cekirdek/geribildirim.py`).

## Kullanıcının kendi yaptıkları
- Deneylerin çalıştırılması (bir kısmı) ve sonuçların okunması.
- Galeri ve görsel kontrol: videolarda iskelet ve bantların izlenmesi.
- Örnek cümlelerin okunup yorumlanması. İki katmanlı geri bildirim (hasta cümlesi ve uzman ayrıntısı) önerisi buradan çıktı.
- Uygulamanın canlı denemesi ve arayüz geri bildirimi.
- Kendi kayıtlarının çekimi, etiketlenmesi ve videodan kontrolü.
- LLM deneyindeki cümlelerin körlemesine elle etiketlenmesi.
- Sunum ve rapor.

## Rapor için not
> **Üretken yapay zekâ kullanımı.** Kodun yazılması, hata ayıklama, deneylerin bir kısmının çalıştırılması ve belgeler için Claude Code (Anthropic); literatür taraması, deney planlaması ve sonuçların yorumu için Claude kullanıldı. Raporda yer almayan bir yan deneyde Gemini (`gemini-3.5-flash-lite`, ücretsiz katman) yalnızca karşılaştırma koşulu olarak kullanıldı. Sistemin geri bildirimi kural tabanlıdır, LLM kullanmaz. Raporlanan bütün sayılar sonuç dosyalarından alındı ve `python -m deneyler.hepsi` ile yeniden üretilebilir.
