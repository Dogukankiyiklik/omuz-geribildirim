# ADIM 07 — Kendi kayıtlarımızla deneme

**Tarih:** 2026-11-07 (hazırlık)
**Durum:** Hazırlık tamam: betik, şablon ve çekim listesi hazır. "Önceden belirlenenler" bölümü **çekimden önce** commit'lendi. **Bekleniyor:** kullanıcının çekimi (Karar 35: en geç 9 Kasım akşamı).

## Basit anlatım
- Şimdiye kadarki bütün sayılar başkalarının videolarından (REHAB26 veri seti) geldi. Bu adımda sistemi **kendi çektiğimiz** videolarla deniyoruz. Kalibrasyon videosunda 6 doğru tekrar var. Test videosunda ise sırası önceden yazılmış 21 tekrar var: bazıları doğru, bazıları bilerek hatalı.
- Sistemin her tekrar için söylediği cümle, bizim yazdığımız gerçek etiketle karşılaştırılıyor. Örneğin "omuz silktim, sistem de omuz dedi mi?"
- Bu adım hocanın "gerçek kullanımda çalışıyor mu?" sorusuna cevap verir. Canlı denemedeki iki şüpheyi de sınar: **"farklı yere bakınca baş hatası çıkıyor mu?"** ve **"hızlı yapınca hız notu çıkıyor mu?"**
- **Neden "önceden belirlenenler"?** Hangi sayıları nasıl hesaplayacağımızı videoyu çekmeden önce yazıp kaydettik (commit). Böylece sonuca bakıp ölçütü değiştirmediğimiz kanıtlanabilir. Buna "önceden kayıt" denir.

## Önceden belirlenenler (çekimden önce sabit; Karar 33)
1. **Yöntem ve parametreler:** Dondurulmuş yöntem (Karar 18), `modeller/kural_ex1.json` (Karar 24), `modeller/kamera_esigi.json` (Karar 26), `modeller/hiz_esigi.json` (Karar 31; 1.9000 s), yığın modu (`uygulama/toplu.py`), MediaPipe 1.2.2 + `pose_landmarker_full`. **Hiçbir eşik, sabit veya cümle şablonu bu kayıtlara göre değiştirilmez.** Sonuç kötü çıkarsa olduğu gibi yazılır.
2. **Kalibrasyon:** `kalibrasyon.mp4` içinde ayrılan tekrarlar sırayla kabul edilir, en fazla 6 (yığın modunun davranışı). Kalite kontrolü açık: omuz ya da kalça görünürlüğü medyanı < 0,5 olan tekrar alınmaz. 5'ten az tekrar kalırsa değerlendirme yapılmaz; çekim tekrarlanır.
3. **Eşleştirme:** Test videosunda ayrılan tekrarlar zaman sırasıyla `etiketler.csv` içindeki `tekrar_no` ile eşlenir. Sayılar tutmazsa betik durur ve ayrılan tekrarların yalnızca zamanlarını yazar (karar ve cümle yazmaz). Kullanıcı videoyu izleyerek bir eşleşme dosyası hazırlar (`--eslesme`). Eşlenemeyen etiketli tekrarlar metriklerin paydasına girmez ve "test videosunda ayrıldı: kaçta kaç" satırında ayrıca raporlanır.
4. **Hata listesi:** Kullanıcının gördüğü **hasta cümlesinden** `cekirdek/metin_cozumleyici.py` ile çıkarılır. Bu, Deney 3'teki çıkarıcının aynısıdır. Uzman ayrıntısından çıkarılan listeyle aynı olduğu ayrıca denetlenir.
5. **Metrikler** (kişi başına ve iki kişi birlikte; sayılar "kaçta kaç", güven aralığı verilmez):
   - Hatalı tekrarlar (12):
     - **katı:** cümledeki ilk hata = etiket;
     - **ilk iki:** etiket cümlede söylendi;
     - **olumlu cümle:** hiç hata söylenmedi.

     Hepsi için ayrıca hata türüne göre.
   - Doğru tekrarlarda **gereksiz uyarı** (cümlede en az bir hata), üç grupta ayrı: **normal** (5), **bakış** (3), **hızlı** (2).
   - **Hız notu:** hızlı tekrarlarda (2) ve normal doğru tekrarlarda (5) çıktı mı; bakış ve hatalılarda betimsel.
   - **Karışıklık tablosu:** gerçek etiket × cümledeki ilk hata.
   - **"Verilen cümle – gerçek etiket" tablosu**, tekrar başına.
   - **Betimsel:** kamera uyarısı ve sol kol notu sayısı.
6. **Bilgi notları metrik değildir** (Karar 31): hız ve sol kol notu cümleye girmez, gereksiz uyarı sayılmaz.
7. **Yorum sınırı:** Kişi başına 21 tekrar var; tek kişide tek tekrarın değişmesi oranı 1/5 ile 1/2 arasında oynatır. Sonuçlar "kaçta kaç" olarak yazılır, veri setindeki yüzdelerle doğrudan kıyaslanmaz, yalnızca yan yana konur.
8. **Bakış sınaması (Karar 32):** "Bakış" grubunda gereksiz uyarı, normal doğru gruptan belirgin yüksekse (ör. 3/3'e 0/5), bu kullanıcının gözlemini destekler. Hangi hatanın söylendiği ayrıca yazılır (baş mı?). Sayılar küçük olduğu için bu bir kanıt değil, bir **işaret** olarak raporlanır.
9. **Çıktılar:** `sonuclar/kendi_kayit/<kisi>/` altına `tekrarlar.csv` (ham), `cumle_etiket.csv`, `karisiklik.csv`, `ozet.csv` ve `bilgi.json` (sürümler, kalibrasyon tepeleri, eşleşme biçimi). İki kişi birlikte: `sonuclar/kendi_kayit/ozet.csv`, `karisiklik.csv`.
10. **Sunum yedeği (Karar 27):** Bu iki video ve yığın modu çıktısı sunumdaki yedektir.

## Yapılanlar (hazırlık)
- `deneyler/kendi_kayit.py`:
  - `--sablon`: tohumlu karışık sıra ve `etiketler.csv` şablonu yazar; var olan dosyanın üzerine yazmaz.
  - Değerlendirme: yığın modu, MediaPipe noktaları `veri/ara/kendi_kayit/` altına önbelleklenir.
  - Eşleştirme, metrikler ve çıktılar yukarıdaki maddelere göre.
- `uygulama/toplu.py`: `kalibre_et` ve `degerlendir_video` artık önceden çıkarılmış noktaları da alabiliyor (`lm=`). Davranış aynı.
- Sıralar üretildi: `veri/kendi_kayit/kisi1/etiketler.csv` (tohum 0) ve `veri/kendi_kayit/kisi2/etiketler.csv` (tohum 1). Kopyası `docs/etiketler_sablon.csv`, tohum 0. Sıralar `docs/CEKIM_LISTESI.md` içinde.
- `testler/test_kendi_kayit.py`: sıranın protokole uyması, etiket denetimleri, eşleştirme ve metrik tanımları (yapay tabloyla).
- **Duman testi (yalnızca betiğin çalıştığını görmek için, sonuç değildir):** Veri setinden `ex1_Honza` cam1 yönelim 0 videosu kesildi ve hem kalibrasyon hem test olarak verildi; 10 etiket de veri setinden alındı. Sonuç: 10/10 tekrar ayrıldı ve eşlendi, tablolar yazıldı. Hasta ve uzman metinlerinden çıkan hata listeleri 10/10 aynıydı. Kalibrasyon videosunda 5'ten az tekrar olunca betik doğru şekilde durdu. Bu çalıştırmada kalibrasyona hatalı tekrarlar da girdiği için sayılar anlamsızdır ve raporlanmaz. Çıktı proje dışında (geçici klasör).

## Değişen / eklenen dosyalar
| Dosya | Ne işe yarıyor |
| --- | --- |
| `deneyler/kendi_kayit.py` | Adım 7 değerlendirmesi ve sıra şablonu |
| `testler/test_kendi_kayit.py` | Betiğin testleri |
| `docs/CEKIM_LISTESI.md` | Yazdırılabilir çekim kontrol listesi ve iki kişinin sırası |
| `docs/etiketler_sablon.csv` | `etiketler.csv` örneği (tohum 0 sırası) |
| `uygulama/toplu.py` | `lm=` seçeneği |

## Nasıl çalıştırılır
```bash
# Çekimden sonra (videolar veri/kendi_kayit/kisi1/ altına konur):
python -m deneyler.kendi_kayit --kisi kisi1 --kalibrasyon veri/kendi_kayit/kisi1/kalibrasyon.mp4 --test veri/kendi_kayit/kisi1/test.mp4 --etiketler veri/kendi_kayit/kisi1/etiketler.csv
```
Beklenen süre: MediaPipe ilk çalıştırmada videonun süresinin kabaca 1–2 katı (2 dakikalık test videosu için birkaç dakika). Sonraki çalıştırmalar önbellekten birkaç saniye sürer. Çıktı: `sonuclar/kendi_kayit/kisi1/`.

## Sonuçlar
Çekimden sonra doldurulacak.

## Kabul ölçütü kontrolü
- [x] Testler geçti (hazırlık): tam pytest `145 passed, 1 xfailed in 96.53s`.
- [ ] Tablo var (karışıklık + cümle–etiket).
- [ ] Sistemin yanıldığı tekrarlar için kısa gözlem yazıldı.
- [x] Önceden belirlenenler çekimden önce commit'lendi.

## Kararlar ve sapmalar
- PLAN'daki eski protokol (5 kalibrasyon, 14 test tekrarı) yerine Karar 33 geçerli: 6 kalibrasyon ve 21 test tekrarı (öne kaçma, bakış ve hızlı tekrarlar eklendi).
- Karışık sıra, kâğıda elle yazmak yerine tohumlu bir betikle üretildi. Böylece hem tekrarlanabilir hem de çekimden önce sabit.

## Açık sorular / danışmana notlar
- Hızlı tekrarlar (~1 s), tekrar ayırıcının "30°'den 20°'ye en az 0,8 s" şartı yüzünden ayrılamayabilir. Bu durumda eşleşme dosyasıyla devam edilir ve ayrılamama "test videosunda ayrıldı" satırında raporlanır. Bu da bir bulgudur, eşik değiştirilmez.
