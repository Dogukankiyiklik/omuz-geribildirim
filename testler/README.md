# testler/

Kodun doğru çalıştığını ve bir değişiklikten sonra sonuçların bozulmadığını denetleyen `pytest` testleri. Proje kökünden çalıştırılır:

```bash
pytest -q          # ~1 dk
```

Beklenen çıktı: **hepsi geçer, 1 tane `xfailed`**. `xfailed`, "bilerek başarısız olması beklenen test" demek. Anahtar kelime çıkarıcı "Omzun kalkmadı, kolun düzdü" gibi olumsuz geçmiş zamanlı olumlu cümleleri ayırt edemiyor (`cekirdek/metin_cozumleyici.py`'deki bilinen sınırlılık). Test bu sınırlılığı belgelemek için duruyor. Bir gün düzelirse test "beklenmedik şekilde geçti" diye uyarır.

`pytest.ini`, yalnızca bu klasörün taranmasını sağlar.

## İki tür test

**Birim testleri** küçük, yapay girdilerle tek bir fonksiyonu sınar ve veri gerektirmez.

**Veri testleri** gerçek veri setini ya da kayıtlı sonuçları kullanır. Gerekli dosya yoksa (örneğin repoyu yeni indiren birinde) hata vermez, **atlanır** (`skipped`). Bunların en önemlileri **regresyon testleri**: kod değişince sonuçların değişmediğini, kayıtlı sonuçları yeniden üreterek denetlerler.

| Dosya | Neyi sınar | Veri gerekir mi? |
| --- | --- | --- |
| `test_deney1_regresyon.py` | **Regresyon:** Deney 1 yeniden çalıştırılınca sonuç `referans/beklenen_deney1_ozet.csv` ile ±0,01 içinde aynı mı? | Evet |
| `test_deney2_regresyon.py` | **Regresyon:** karar kuralı yeniden kurulunca kayıtlı Deney 2 kararları (`sonuclar/deney2/tahminler.csv`) birebir çıkıyor mu? | Kayıtlı sonuçlar |
| `test_degerlendirici.py` | Uygulamanın değerlendiricisi Deney 3 ile aynı kararı ve cümleyi veriyor mu? (Uygulama ile deneyin aynı koddan geldiğinin kanıtı) | Evet |
| `test_cekirdek.py` | Geometri, ölçüler, DTW (numba'lı ve saf Python aynı sonucu veriyor mu), kare hatası, AUC | Hayır |
| `test_aci_bandi.py` | Açı bandı: kutular, fazlar, μ ve τ, adil model; Deney 1'in genel bandına test kişisinin tekrarı giriyor mu | Kısmen |
| `test_hata_turu.py` | Hata ölçüleri, puanlar, karar kuralı (z, T, "ilk iki"), az kaldırmanın iki sürümü | Hayır |
| `test_geribildirim.py` | Türkçe sayı ekleri (%30'u, %30'a), faz ve an seçimi, şiddet, cümle şablonları, anahtar kelime çıkarıcı (`elle_cumleler.py`) | Hayır |
| `test_bindirme.py` | Referans iskelet kullanıcının üstüne doğru çakıştırılıyor mu (öteleme, ölçek, döndürme) | Hayır |
| `test_tekrar_ayirici.py` | Canlı tekrar ayırıcı (başlangıç, bitiş, geçersiz adaylar) ve kural dosyasının yazılıp okunması | Hayır |
| `test_bilgi_notlari.py` | Hız, sol kol ve kamera notları | Kısmen |
| `test_veri.py` | Veri okuma: görüş açısı, en-boy, tekrar sayıları | Kısmen |
| `test_kendi_kayit.py` | Kendi kayıt betiği: tekrar sırası, etiket okuma, eşleştirme, metrikler | Hayır |
| `test_hepsi.py` | `deneyler/hepsi.py`'nin karşılaştırma fonksiyonları (deney çalıştırmaz) | Hayır |
| `test_pencere.py` | Uygulama penceresi büyütülünce görüntü oranının korunması ve fare tıklamasının doğru yere düşmesi | Hayır |

`elle_cumleler.py` bir test değil; anahtar kelime çıkarıcıyı sınamak için Deney 3'ten önce elle yazılmış cümleler ve beklenen hatalar.
