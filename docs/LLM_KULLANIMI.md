# Üretken yapay zekâ kullanımı

Hocanın kuralı gereği projede üretken yapay zekânın nerede ve hangi amaçla kullanıldığı aşağıda. Rapor için kısa not en altta.

## Claude Code (Anthropic) — kod
- `cekirdek/`, `deneyler/`, `uygulama/`, `araclar/` ve `testler/` altındaki kodun yazılması.
- Hata ayıklama ve deney betikleri; kısa sınamalar (pytest ve hızlı kontroller).
- Her adımın ilerleme kaydı (`ilerleme/ADIM_XX.md`) ve sonuç özeti (`sonuclar/OZET.md`). Bu kayıtlardaki sayılar terminal çıktısından ve sonuç dosyalarından kopyalandı; uzun deneyleri kullanıcı çalıştırdı.
- Belgeler (`docs/YENIDEN_KURULUM.md`, `docs/SURUMLER.md`, `docs/DEMO.md`, `docs/SUNUM_GIRDILERI.md`) ve sunum şekil adayları (`deneyler/sunum_sekilleri.py`).

## Claude (danışman sohbeti) — planlama ve yorum
- Literatür taraması (`docs/ARKA_PLAN.md`).
- Planlama (`PLAN.md`) ve güncellemeler (`ilerleme/GUNCELLEME_XX.md`).
- Sonuçların yorumu ve karar önerileri (`ilerleme/KARARLAR.md`). Deneylerin ölçütleri ve yöntem ayrıntıları çoğunlukla sonuçtan önce yazılıp commit'lendi ("önceden kayıt"); sonradan yapılan analizler belgelerde öyle işaretlendi.
- Çekim suflör sayfası (`docs/cekim_suflor.html`).

## Gemini (Google, ücretsiz katman) — yalnızca Deney 4
- Deney 4'te karşılaştırma koşulu (B: sapma kodundan cümle; C: ham özetten hata ve cümle).
- Model: `gemini-3.5-flash-lite` (ücretsiz katmanın günlük sınırı nedeniyle; düşünme ayarı varsayılan; temperature 0). İstekler 7 Kasım 2026'da atıldı. Ayrıntı: `ilerleme/ADIM_08.md`, `docs/SURUMLER.md`, istemler `deneyler/istemler/`.
- **Ürünün yöntemi değildir.** Uygulamadaki geri bildirim tamamen kural tabanlıdır (`cekirdek/geribildirim.py`).

## Kullanıcının kendi yaptıkları
- Bütün uzun deneylerin çalıştırılması ve sonuçların okunması.
- Galeri ve görsel kontrol (videolarda iskelet ve bantların izlenmesi; Adım 2b).
- Örnek cümlelerin okunup yorumlanması (iki katmanlı geri bildirim önerisi buradan çıktı; Karar 28).
- Uygulamanın canlı denemesi ve arayüz geri bildirimi (Adım 6).
- Kendi kayıtlarının çekimi, etiketlenmesi ve videodan kontrolü (Adım 7).
- Deney 4'te cümlelerin körlemesine elle etiketlenmesi (45 cümle ve Karar 42'de 342 cümle).
- Sunum ve rapor.

## Rapor için not (doğrudan konabilir)
> **Üretken yapay zekâ kullanımı.** Üretken yapay zekâ şu amaçlarla kullanıldı: kodun yazılması, hata ayıklama ve ilerleme kayıtları için Claude Code (Anthropic); literatür taraması, deney planlaması ve sonuçların yorumu için Claude (danışman sohbeti); Deney 4'te yalnızca karşılaştırma koşulu olarak Gemini (`gemini-3.5-flash-lite`, ücretsiz katman). Sistemin geri bildirimi kural tabanlıdır, LLM kullanmaz. Deneyleri yazar çalıştırdı; raporlanan bütün sayılar sonuç dosyalarından alındı ve `python -m deneyler.hepsi` ile yeniden üretilebilir.
