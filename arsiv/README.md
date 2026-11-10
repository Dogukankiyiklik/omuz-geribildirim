# arsiv/ — ödevin parçası olmayanlar

Proje başta hem ders ödevi hem de konferans bildirisi olarak planlanmıştı. Ödeve odaklanmak için (10 Kasım 2026, `odev-sade` dalı) ödevi doğrudan ilgilendirmeyen her şey buraya taşındı. **Hiçbir şey silinmedi.** Klasör yapısı projeninkini aynen izler: `arsiv/deneyler/ex7.py` eskiden `deneyler/ex7.py` idi.

## Bu klasördeki kodlar çalıştırılmak için değil

Taşınan kodlar artık içe aktarılamaz (yolları değişti) ve `pytest` bu klasörü taramaz (`pytest.ini`). Bir arşiv deneyini çalıştırmak gerekirse, her şeyin taşınmadan önceki çalışır hâli `v-sunum` etiketindedir:

```bash
git worktree add ../omuz-v-sunum v-sunum     # ayrı bir klasörde eski hâli açar; bu klasöre dokunmaz
cd ../omuz-v-sunum                            # orada python -m deneyler.ex7 vb. çalışır
```

## Ne var, neden burada?

| Ne | Eski yeri | Neden ödevin dışında |
| --- | --- | --- |
| Planlama ve kayıtlar: `PLAN.md`, `ilerleme/` (14 adım özeti, 12 güncelleme, `KARARLAR.md`'deki kararlar günlüğü) | kök, `ilerleme/` | Geliştirme sürecinin günlüğü. Bir kararın nedenini bulmak için faydalı; sistemi anlamak için `docs/SISTEM.md` yeter. |
| Eski sonuç özeti `sonuclar/OZET.md` | `sonuclar/` | Bildiri için yazıldı (bootstrap, iddia kapsamı tabloları). Ödev özeti: `docs/DENEYLER.md`. |
| Eski belgeler: `ARKA_PLAN.md`, `GELECEK_CALISMA.md`, `SUNUM_GIRDILERI.md`, `CEKIM_LISTESI.md`, `cekim_suflor.html`, `etiketler_sablon.csv` | `docs/` | `ARKA_PLAN.md`'de puanlamanın DTW ile yapıldığı yazıyordu; bu ilk sürüme aitti, son sürümde geçerli değil. Diğerleri bildiri planı ve kendi kaydın çekim hazırlığı (çekim bitti). |
| **Deney 1c**: zamansal yumuşatma (`deneyler/deney1c.py`, `cekirdek/yumusatma.py`, `sonuclar/deney1c/`) | | Olumsuz sonuç: titreme azaldı, tespit değişmedi. Sonucu `docs/DENEYLER.md`'de tek satır. |
| **6b**: omuz silueti (`deneyler/siluet.py`, `cekirdek/siluet.py`, `araclar/siluet_*.py`, `sonuclar/siluet/`, `sonuclar/siluet_sure/`) | | Olumsuz sonuç: kulak–omuz ölçüsünden kötü. Tek satır özeti `docs/DENEYLER.md`'de. |
| **Deney 4**: LLM karşılaştırması (`deneyler/deney4*.py`, `deneyler/istemler/`, `cekirdek/llm.py`, `sonuclar/deney4/`) | | Bildiri katmanı; ödev LLM istemiyor. Ürün kural tabanlı. |
| **Ex7**: omuz ekstansiyonunda doğrulama (`deneyler/ex7.py`, `sonuclar/ex7/`) | | Ödevin hareketi kolu yana kaldırma. |
| Ara sürümler ve tanılar: `sonuclar/deney2_ilk/`, `deney2_revize/`, `deney1_v2_atla_rastgele/`, `bant_genisligi/`, `adim0/`, `adim2b/`, `araclar/bant_genisligi_tani.py`, `senkron_kontrol.py`, `veri_tanit.py`, `rehab26_kucult.py` | | Geliştirme sırasında yapılan kontroller ve geri dönülen denemeler. |
| Yeniden üretim raporu `sonuclar/hepsi/` | | `python -m deneyler.hepsi` çalıştırılınca yeniden oluşur. |
| Testler: `testler/test_deney4.py`, `test_llm.py`, `test_siluet.py`, `test_yumusatma.py` | `testler/` | Arşivlenen kodun testleri. |
