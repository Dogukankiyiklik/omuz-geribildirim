# TASLAK — Üretken yapay zekâ kullanımı (Karar 37)

Hocanın kuralı gereği projede üretken yapay zekânın nerede ve hangi amaçla kullanıldığı aşağıda. Raporda kısa bir notla belirtilecek.

## Claude Code (Anthropic) — kod
- `cekirdek/`, `deneyler/`, `uygulama/`, `araclar/` ve `testler/` altındaki kodun yazılması.
- Hata ayıklama ve deney betikleri.
- Her adımın ilerleme kaydı (`ilerleme/ADIM_XX.md`). Bu kayıtlardaki sayılar terminal çıktısından ve sonuç dosyalarından kopyalandı.
- Kısa sınamalar: pytest ve hızlı kontroller.

## Claude (danışman sohbeti) — planlama ve yorum
- Literatür taraması (`docs/ARKA_PLAN.md`).
- Planlama (`PLAN.md`) ve güncellemeler (`ilerleme/GUNCELLEME_XX.md`).
- Sonuçların yorumu ve karar önerileri (`ilerleme/KARARLAR.md`). Kararlar önce yazıldı, sonuç ondan sonra görüldü ("önceden kayıt").

## Gemini (Google, ücretsiz katman) — yalnızca Deney 4
- Deney 4'te karşılaştırma koşulu (B: sapma kodundan cümle; C: ham özetten hata ve cümle).
- **Ürünün yöntemi değildir.** Uygulamadaki geri bildirim tamamen kural tabanlıdır (`cekirdek/geribildirim.py`).
- Kullanılan model, ayarlar ve istemler: `ilerleme/ADIM_08.md`, `deneyler/istemler/`.

## Kullanıcının kendi yaptıkları
- Bütün uzun deneylerin çalıştırılması ve sonuçların okunması.
- Galeri ve görsel kontrol (videolarda iskelet ve bantların izlenmesi; Adım 2b).
- Örnek cümlelerin okunup yorumlanması (iki katmanlı geri bildirim önerisi buradan çıktı; Karar 28).
- Uygulamanın canlı denemesi ve arayüz geri bildirimi (Adım 6).
- Kendi kayıtlarının çekimi ve etiketlenmesi (Adım 7).
- Deney 4'te 45 cümlenin körlemesine elle etiketlenmesi.
- Sunum ve rapor.
