# Üretken yapay zekâ kullanımı

Ödevin kuralı gereği projede üretken yapay zekânın nerede ve hangi amaçla kullanıldığı aşağıda. Rapor için kısa not en altta.

## Claude Code (Anthropic): kod ve belgeler
- `cekirdek/`, `deneyler/`, `uygulama/`, `araclar/` ve `testler/` altındaki kodun yazılması.
- Hata ayıklama, testler ve kısa sınamalar.
- Deneylerin bir kısmının, kullanıcının isteğiyle çalıştırılması. Son yeniden üretimi (10 Kasım 2026, `sonuclar/hepsi/`) Claude Code çalıştırdı.
- Geliştirme kayıtları (artık depoda değil; git geçmişinde `v-sunum` etiketi), belgeler (`docs/`, klasörlerdeki README'ler) ve sunum şekilleri (`deneyler/sunum_sekilleri.py`; 10 Kasım 2026'da kaldırıldı, git geçmişinde `cc39d2a`). Belgelerdeki sayılar sonuç dosyalarından kopyalandı.
- Ödeve göre sadeleştirme (10 Kasım 2026): ödev dışı dosyaların ayrı bir klasöre taşınması (14 Kasım 2026'da bu klasör depodan silindi), kalıntıların temizlenmesi ve belgelerin yeniden yazılması. Aynı gün, kullanıcının isteğiyle Deney 1–3 uygulamanın kullandığı tek yönteme indirildi, sunum şekilleri betiği ve görsel kontrol aracı kaldırıldı, çekirdekte artık kullanılmayan kod silindi; her adımda bütün sonuçların birebir aynı yeniden üretildiği `deneyler/hepsi.py` ile denetlendi.

- Rapor, sunum ve hazırlık belgesi (11 Kasım 2026): 1 sayfalık rapor (`docs/RAPOR.docx`), sunum slaytları ve konuşmacı notları, `docs/SUNUM_HAZIRLIK.md` ve sunumdaki açı bandı şekli (`araclar/sunum_sekilleri.py`) Claude Code ile hazırlandı; kullanıcı okuyup düzeltir ve sunar. Aynı gün, kullanılan on iki makaledeki iddia ve sayılar makalelerin PDF'lerinden doğrulandı ([`LITERATUR.md`](LITERATUR.md)). Rapor 14 Kasım 2026'da, kullanıcının isteğiyle daha okunur bir dille yeniden yazıldı.

## Claude (ayrı sohbet): planlama ve yorum
- Literatür taraması ve makale özetleri: her makale, sabit bir istemle tek tek özetletildi; projede işe yarayan on iki makalenin özeti [`LITERATUR.md`](LITERATUR.md)'de.
- Planlama ve güncellemeler.
- Sonuçların yorumu ve karar önerileri. Deneylerin ölçütleri ve yöntem ayrıntıları çoğunlukla sonuçtan önce yazılıp commit'lendi ("önceden kayıt"); sonradan yapılan analizler kayıtlarda öyle işaretlendi.
- Çekim sırasında kullanılan suflör sayfası.

## Kullanıcının kendi yaptıkları
- Deneylerin çalıştırılması (bir kısmı) ve sonuçların okunması.
- Galeri ve görsel kontrol: videolarda iskelet ve bantların izlenmesi.
- Örnek cümlelerin okunup yorumlanması. İki katmanlı geri bildirim (hasta cümlesi ve uzman ayrıntısı) önerisi buradan çıktı.
- Uygulamanın canlı denemesi ve arayüz geri bildirimi.
- Kendi kayıtlarının çekimi, etiketlenmesi ve videodan kontrolü.
- Sunumun yapılması; raporun ve slaytların okunup onaylanması.

## Rapor için not
> **Yapay zekâ kullanımı:** Kod yazımı, hata ayıklama ve belgeler (bu rapor dahil) için Claude Code (Anthropic) kullanılmıştır; uygulamanın kendisi dil modeli kullanmaz.
