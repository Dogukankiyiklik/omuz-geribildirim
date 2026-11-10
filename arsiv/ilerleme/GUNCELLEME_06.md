# Güncelleme 06 — 7 Kasım 2026 gece (danışmandan)

Claude Code: `/clear` sonrası yeni oturum. Sırayla oku:
1. `CLAUDE.md`
2. `PLAN.md`
3. `ilerleme/KARARLAR.md`
4. `ilerleme/ADIM_04.md` (sonundaki "Ek: Güncelleme 05" dahil)
5. `ilerleme/ADIM_04b.md`
6. bu dosya

Kararları `KARARLAR.md`'ye işle. Önce aşağıdaki "Yapılacaklar 1"i yap, sonra **Adım 5**'e geç.

## Önce bir sorumluluk notu
Karar 13'teki "aynı z ölçeklemesi" talimatı benim hatamdı. Yeni kaldırma puanının doğru tekrarlarda 0'da yığılacağını ve IQR'nin 0 çıkacağını öngörmedim. Senin uygulaman talimata birebir uydu ve sonucu dürüstçe raporladı. Ex7 raporunda "önceden belirlenenler" bölümünü sonuçlardan önce commit'lemen de çok iyi bir uygulamaydı.

## Kararlar

### Karar 17 — Ex1 "az kaldırma" puanında ilk sürüme dönülür
- Ana sonuç, **önceden belirlenmiş** ilk sürümdür: d = (kalibrasyon tepelerinin medyanı − tepe) / max(IQR, 5°). Gerekçe "daha iyi sonuç vermesi" değil; sonuçlardan önce tanımlanmış birincil yöntem olması.
- Revize (Karar 13), **başarısız bir deneme** olarak raporlanır. Raporda şunlar yer alır:
  - neden denendiği: birimler arası karşılaştırılamazlık;
  - neden başarısız olduğu: 0'da yığılan dağılımda IQR ölçeklemesi z = 100·E üretti;
  - sonucu: makro-F1 0,631 → 0,568, GA sıfırı içermiyor.
- (b) ve (c) seçenekleri denenmez; ikisi de sonuç gördükten sonra yeni bir dal açmak olur. Gelecek çalışmaya yazılır.

### Karar 18 — Yöntem donduruldu
- Puanlama ve karar kuralında bundan sonra **değişiklik yapılmaz.** Bundan sonraki bütün adımlar dondurulmuş yöntemi kullanır: Adım 5, uygulama, kendi kayıtlar, LLM, siluet, REHAB24-6.
- Dondurulan yöntem:
  - **Ex1:** v2 (açı bandı) + yönlü + ilk sürüm kaldırma; Karar 7 adil model; kişi bazlı birini-dışarıda-bırak ile T.
  - **Ex7:** Adım 4b'deki haliyle.
- Yeni fikirler `docs/GELECEK_CALISMA.md` dosyasına yazılır, uygulanmaz. Örnekler:
  - kol açısı + kol boyu ile öne kaçma ayrımı;
  - kaldırmanın sabit ölçeği;
  - Ex7 için yönsüz ya da zaman bandı tercihi;
  - dinlenme ayarlı genel bant.

### Karar 19 — Ex7 sonuçları ana sistemi değiştirmez
- Ex7 bir **doğrulama**dır. Doğrulama sonucuna göre ana sistemi değiştirmek, doğrulamayı ayar verisine çevirir.
- "Ex7'de en iyi sistem v1b yönsüz" bulgusu sınırlılık olarak raporlanır, şu gerekçeyle: açı bandının ön koşulu geniş kol açısı aralığıdır; yönlü bant da tek yönlü görünen hatalara uygundur.

### Karar 20 — İddia kapsamı (rapor ve sunum için)
| İddia | Kanıt | Güç |
| --- | --- | --- |
| Kişiye özel bant, omuz silkmesini sabit kuraldan çok daha iyi yakalar | Ex1: 0,70 → 0,95; Ex7 (ayarsız): 0,89–0,94 | **Güçlü**, iki harekette |
| Kalibrasyon kişiye özel olmalı | Deney 1b, 36/36 fark | **Güçlü** |
| Açı bandı silkmeyi diğer hatalardan daha iyi ayırır | Ex1 +0,108 (GA sıfırı içermiyor); Ex7'de tekrarlanmadı | **Yalnızca geniş açılı hareketler için** |
| Hata türü bulunabilir | Ex1 ö+ç makro-F1 0,63, 100 hatalının 57'sinde tür doğru; Ex7 0,40 | **Orta (Ex1), zayıf (Ex7)** |
| Titreme yumuşatması gerekmez | Deney 1c | Olumsuz sonuç |
| Profil görüş uygun değil | Ex1 ve Ex7 | Sınırlılık |

## Yapılacaklar
1. **İlk sürüm kaldırmayı geri getir.** Kodda `kaldirma_surumu = "ilk" | "revize"` seçeneği olsun; varsayılan `"ilk"`. Ardından:
   - `python -m deneyler.deney2` ile `sonuclar/deney2/` yeniden üretilsin. Revize çıktıları `sonuclar/deney2_revize/` altına taşınsın.
   - **Regresyon:** Yeni `sonuclar/deney2/ozet.csv`, `sonuclar/deney2_ilk/ozet.csv` ile birebir aynı olmalı. `ilk_iki.csv` ilk sürüm için de üretilsin; bu bir değerlendirme metriği, yöntem değişikliği değil.
   - ADIM_04'ün sonuna kısa bir "Ek: Güncelleme 06" yaz: ilk sürümün "ilk iki" sonuçları ve regresyon.
2. **`docs/GELECEK_CALISMA.md`** dosyasını oluştur ve yukarıdaki fikirleri yaz.
3. **Adım 5** (Deney 3):
   - Geri bildirim en fazla 2 hata söyler; 2. hata ancak z'si de T'yi geçerse söylenir (`ilk_iki`).
   - Ölçü içeren şablonlar (Güncelleme 01 / PLAN Adım 5).
   - Değerlendirme:
     - katı / esnek / ilk iki;
     - "cümle doğru hatayı adlandırdı mı" (anahtar kelime çıkarıcı ile);
     - doğru tekrarlarda gereksiz uyarı oranı.
   - Ana tablo önden + çapraz; tüm görüşler de verilir.
4. Ardından PLAN'daki sırayla: Adım 6 (uygulama) → Adım 7 → isteğe bağlılar.
