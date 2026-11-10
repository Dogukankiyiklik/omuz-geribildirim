# Güncelleme 01 — 6 Kasım 2026 (danışmandan)

Claude Code: Bu dosyayı oku ve `PLAN.md`, `CLAUDE.md`, `docs/ODEV.md` dosyalarının yeni hallerine göre devam et. Daha önce tamamladığın adımlar varsa, aşağıdaki değişikliklerin onları nasıl etkilediğini `ilerleme/KARARLAR.md`'ye yaz.

## Neden
Hocanın resmi ödev tanımı geldi (`docs/ODEV.md`). Projemiz üç problemin üçünü de kapsıyor, ama bazı şartlar planda eksikti. Ayrıca kullanıcı sistemin kapalı bir kutu olmamasını ve her sonucu videoda kendi gözüyle kontrol edebilmeyi istiyor.

## Değişiklikler
1. **Adım 0:** Veri artık orijinal Zenodo dosyalarından (`veri/rehab26/`) doğrudan okunuyor. `rehab26_kucuk.npz` yalnızca regresyon karşılaştırması için var. Koordinat biçimini (piksel mi, 0–1 mi) netleştir.
2. **Yeni Adım 2b:** Görsel kontrol aracı ve deney galerileri. Video + iskelet + DTW ile hizalanmış referans iskelet + bant eğrisi + karar. Bu aynı zamanda hocanın Problem 3'ünün ilk sürümü.
3. **Adım 3:** Deney 1c (zamansal yumuşatma) eklendi; hocanın Problem 2 için önerdiği iyileştirmelerden biri.
4. **Adım 5:** Cümleler **ölçü** içermeli (derece veya gövde %'si, "normalde X, sende Y"). Doğru tekrarda **somut** olumlu cümle verilmeli. Hocanın şartı.
5. **Adım 6:** Tekrar sonunda referans iskelet bindirmeli oynatım (zamansal + geometrik hizalama; hatalı uzuvlar kırmızı) ve omuz yörüngesi grafiği. Ortak kod `cekirdek/bindirme.py`.
6. **Yeni Adım 6b (isteğe bağlı):** Segmentasyon maskesiyle omuz siluet ölçütü.
7. **Adım 8 (LLM)** isteğe bağlı oldu. Öncelik sırası: 6b → 8 → 11 → 10.
8. **Adım 9:** `docs/YENIDEN_KURULUM.md` ve `docs/LLM_KULLANIMI.md` eklendi (hocanın rapor kuralları).
