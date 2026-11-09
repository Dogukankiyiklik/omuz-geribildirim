# Yeniden üretim özeti

- Tarih: 2026-11-09 17:01 · commit: `ecc6762` · Python 3.11.9
- Adım: 17 · başarısız: 0 · toplam süre: 32.1 dk
- Karşılaştırılan dosya: 120 · aynı: 119 · farklı: 1
- Yeniden üretim: 119/120 aynı

## Adımlar

| adım | komut | çıkış kodu | süre (s) | kaynak |
| --- | --- | --- | --- | --- |
| deney1 | python -m deneyler.deney1 --galeri-yok | 0 | 15.1 | baştan |
| deney1_v2 | python -m deneyler.deney1_v2 --sekilsiz | 0 | 112.0 | baştan |
| deney1b | python -m deneyler.deney1b | 0 | 114.2 | baştan |
| deney1c | python -m deneyler.deney1c | 0 | 1100.4 | baştan |
| deney2 | python -m deneyler.deney2 | 0 | 150.6 | baştan |
| ex7 | python -m deneyler.ex7 | 0 | 207.7 | baştan |
| deney3 | python -m deneyler.deney3 | 0 | 55.2 | baştan |
| deney3_saglam | python -m deneyler.deney3 --olcu-surumu saglam | 0 | 54.5 | baştan |
| tekrar_ayirma | python -m deneyler.tekrar_ayirma | 0 | 9.6 | baştan |
| kamera_acisi | python -m deneyler.kamera_acisi | 0 | 3.3 | baştan |
| hiz_esigi | python -m deneyler.hiz_esigi | 0 | 2.1 | baştan |
| kural_disa_aktar | python -m araclar.kural_disa_aktar | 0 | 4.1 | baştan |
| siluet | python -m deneyler.siluet --sinirlar C:/Users/dogukan/AppData/Local/Temp/omuz_hepsi_temiz/hepsi_ara/siluet_sinirlar.npz | 0 | 48.8 | önbellekten: veri/ara/siluet/ (segmentasyon yeniden çalıştırılmadı) |
| deney4_orneklem | python -m deneyler.deney4_orneklem | 0 | 2.0 | baştan |
| deney4 | python -m deneyler.deney4 onbellekten --model gemini-3.5-flash-lite --onbellek C:/Users/dogukan/Desktop/omuz-geribildirim/sonuclar/deney4/onbellek.jsonl | 0 | 32.4 | önbellekten: sonuclar/deney4/onbellek.jsonl (LLM'e istek gitmez) |
| deney4_kaldirma | python -m deneyler.deney4 kaldirma-degerlendir | 0 | 11.7 | kayıtlı yanıtlar + kullanıcı etiketleri (elle_kaldirma.xlsx girdi olarak kopyalanır) |
| kendi_kayit | python -m deneyler.kendi_kayit --kisi kisi1 --kalibrasyon C:/Users/dogukan/Desktop/omuz-geribildirim/veri/kendi_kayit/kisi1/kalibrasyon.MOV --test C:/Users/dogukan/Desktop/omuz-geribildirim/veri/kendi_kayit/kisi1/test.MOV --etiketler C:/Users/dogukan/Desktop/omuz-geribildirim/veri/kendi_kayit/kisi1/etiketler.csv --yalniz-onbellek | 0 | 3.0 | önbellekten: veri/ara/kendi_kayit/ (MediaPipe noktaları) |

## Aynı olmayan dosyalar

| klasör | dosya | durum | ayrıntı | en büyük fark |
| --- | --- | --- | --- | --- |
| ex7 | d2_esikler.csv | farklı | boyut/sütun: (20, 22) / (20, 21) |  |

## Yeniden üretilmeyen kayıtlı çıktılar

| klasör | neden yeniden üretilmedi | var mı | dosya sayısı |
| --- | --- | --- | --- |
| deney4 | Adım 8: pilot, API çalıştırması (onbellek.jsonl), elle_etiket/elle_uyum ve kullanıcı etiket dosyaları yeniden üretilmez (tablolar önbellekten üretilir) | True | 40 |
| siluet | 6b: segmentasyon (veri/ara/siluet/, ~1,5 sa) ve görsel örnekler yeniden üretilmez | True | 12 |
| siluet_sure | Karar 45: süre ölçümü (makineye bağlı) | True | 4 |
| deney2_revize | Karar 17: başarısız deneme, kayıtlı | True | 42 |
| deney2_ilk | Karar 13 öncesi ilk sürüm, kayıtlı | True | 39 |
| deney1_v2_atla_rastgele | Karar 7 öncesi, kayıtlı | True | 11 |
| adim0 | Adım 0 veri tanıtımı | True | 3 |
| adim2b | Adım 2b senkron kontrolü | True | 1 |
| gorsel_kontrol | görsel kontrol aracı çıktıları | True | 5 |
| bant_genisligi | Güncelleme 08 tanısı | True | 2 |
| uygulama_saglik | uygulama sağlık kontrolü (MediaPipe) | True | 3 |
| sunum | sunum şekil adayları (Karar 38, 56) | True | 9 |
