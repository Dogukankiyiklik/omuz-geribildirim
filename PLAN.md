# PLAN.md — Adım adım yol haritası

Her adımı sırayla yap. Her adımın sonunda `ilerleme/ADIM_XX.md` yazılır (bkz. `CLAUDE.md`).

**📤 Danışmana gönder** işaretli adımlardan sonra kullanıcı şu dosyaları danışman Claude sohbetine gönderir:
- `ilerleme/ADIM_XX.md`
- ilgili `sonuclar/.../ozet.csv`

Danışman sonuçları yorumlar; gerekirse bir sonraki adım için düzeltme verir.

| Adım | İş | Hedef tarih | Katman |
| --- | --- | --- | --- |
| 0 | Ortam ve veri: **orijinal Zenodo dosyalarından** doğrudan okuma | 6 Kas | Zorunlu ✅ |
| 1 | Çekirdek modül + Deney 1 regresyon testi | 6 Kas | Zorunlu ✅ |
| 2 | Deney 1'in kullanıcı tarafından çalıştırılması + şekiller | 6–7 Kas | Zorunlu ✅ |
| 2b | **Görsel kontrol aracı** (video + iskelet + bant eğrisi + karar) | 7 Kas | Zorunlu ✅ |
| 2c | **Deney 1 v2:** yöntem düzeltmeleri ablasyonu (pay hariç, çoklu referans, **açı bandı**) | 7 Kas | Zorunlu ✅ |
| 3 | Deney 1b (genel bant / kişiye özel bant) + **Deney 1c (zamansal yumuşatma)**; v1b ve v2 ile | 7–8 Kas | Zorunlu ✅ |
| 4 | Deney 2: hata türünü bulma (açı bandı + yönlü) | 6 Kas | Zorunlu ✅ |

**Yeni sıra (Güncelleme 05).** Tabloda yukarıdan aşağı yapılır:

| Sıra | Adım | İş | Hedef tarih | Katman | Durum |
| --- | --- | --- | --- | --- | --- |
| 1 | 4 (ek) | **Deney 2 revize** (Karar 13–14): yeni az kaldırma puanı + "ilk iki" metriği; `ADIM_04.md` sonuna "Ek: Güncelleme 05" | 7 Kas | Zorunlu 📤 | ✅ |
| 2 | 4b | **Ex7'de ayarsız doğrulama**: Deney 1 (silkme/doğru AUC; v1b ve v2) + Deney 2 kuralı Ex7 hata türleriyle. **Hiçbir sabit değiştirilmez** | 7 Kas | Zorunlu 📤 | ✅ |
| 3 | 5 | Deney 3: **ölçü içeren** kural tabanlı Türkçe geri bildirim; "ilk iki" metriği burada da | 7–8 Kas | Zorunlu 📤 | 🔄 |
| 4 | 6 | Uygulama: kalibrasyon, canlı/video değerlendirme, **referans iskelet bindirme (Problem 3)** | 8–10 Kas | **Zorunlu, öncelikli** 📤 | ⏳ |
| 5 | 7 | Kendi kayıtlarımızla deneme (kullanıcı çeker) | 10–11 Kas | Zorunlu 📤 | ⏳ |
| 6 | 8 | Deney 4: LLM ile kural tabanlı karşılaştırması (Gemini ücretsiz / Ollama); süre sınırı 1 gün | 11 Kas | Bildiri 📤 | ⏳ |
| 7 | 6b | Omuz bölgesi siluet ölçütü; süre sınırı 1 gün; segmentasyon saatler sürebilir, önce süre tahmini | 11–12 Kas | İsteğe bağlı 📤 | ⏳ |
| 8 | 10 | REHAB24-6 ile 10 yeni kişi; kullanıcı etiketler; önce veri biçimi, iş büyükse dur ve sor | 12–13 Kas | İsteğe bağlı | ⏳ |
| 9 | 9 | Sonuçları dondurma, şekiller, `sonuclar/OZET.md` | **13 Kas akşamı** | Zorunlu 📤 | ⏳ |
| — | — | 5 dk sunum (danışmanla, Claude Code dışında) | 13–15 Kas | Zorunlu | ⏳ |
| — | — | **1 sayfalık rapor** (hocanın şablonu; sunumdan sonra teslim) | 16 Kas sonrası | Zorunlu | ⏳ |
| — | 11 | ~~Ex7 genellemesi~~ → Adım 4b'ye taşındı | — | — | — |

Durum: ✅ tamamlandı · 🔄 devam ediyor · ⏳ başlanmadı (7 Kas 2026, Güncelleme 07 öncesi). Ana tablodaki Adım 0–4 de tamamlandı.

Sunum: **16 Kasım 2026.** **Kural (Güncelleme 05):** İsteğe bağlı adımlar (6, 7, 8 sıradaki) zorunlu adımları (4, 5 sıradaki) asla geciktiremez. Uygulama ve kendi kayıtlar bitmeden isteğe bağlılara geçilmez. 13 Kas akşamına kadar bitmeyen isteğe bağlı iş bırakılır.

### Hocanın ödev tanımıyla eşleşme (bkz. `docs/ODEV.md`)

| Hocanın problemi | Bizde karşılığı |
| --- | --- |
| **P1 — Doğal dil geri bildirimi:** referansa göre fiziksel fark, hatalı bölge ve **büyüklüğü**, düzeltme önerisi, doğru harekette olumlu geri bildirim | Adım 4–5: hata türü + faz + yön + **ölçü (°, gövde %)** + düzeltme cümlesi |
| **P2 — Omuz/skapula hassas ölçümü:** standart pose çıktısının sınırını göstermek + omuza özel en az bir iyileştirme + karşılaştırma | Deney 1, 1b, 1c: ham ölçütler (sınır) → kol açısına koşullu kişiye özel bant, kulak–omuz ölçütü, yumuşatma (iyileştirmeler) → AUC karşılaştırması. İsteğe bağlı 6b: siluet ölçütü |
| **P3 — Referans ve kullanıcı hareketini çakıştırma:** zamansal (DTW) + geometrik hizalama, aynı video üzerinde gösterim, hatalı bölgeleri görünür kılma | Adım 2b ve 6: DTW + gövde merkezine öteleme + gövde boyuna ölçekleme + gövde eksenine döndürme; referans iskelet kullanıcı videosuna yarı saydam bindirilir, banttan çıkan uzuvlar kırmızı |

---

## Adım 0 — Ortam ve veri: orijinal dosyalardan doğrudan okuma

Kullanıcı veri setini Zenodo'dan (https://zenodo.org/records/23018128) kendisi indirir ve `veri/rehab26/` klasörüne koyar:
- `Error_types.csv`
- `joint_names.txt`
- `jointSequences-mediapipe.zip` (açılmış hali de olur)
- `Segmentation.csv`
- `Segmentation.txt`
- `videos.zip` (8,4 GB): görsel kontrol (Adım 2b) için gerekli; açılmış hali de olur.

`rehab26_kucuk.npz` artık zorunlu değil. Yalnızca karşılaştırma için tutulur, çünkü danışmanın Deney 1 sonuçları bu dosyadan üretildi.

**Yapılacaklar**
- `.venv` oluştur, `requirements.txt` kur.
- `araclar/veri_tanit.py`: kullanıcıya veri setini tanıtan betik. Şunları yazdırır:
  - `Segmentation.txt` içeriği
  - `joint_names.txt` (33 eklem, indeksleriyle)
  - zip içindeki dosya listesi
  - bir dosyanın biçimi, `(kare, 33, 4)`
  - her sütunun en küçük ve en büyük değeri
  - egzersiz ve hata türü başına tekrar sayıları
- **Koordinat kontrolü:** Zenodo sayfası "2B'de x, y piksel koordinatı" diyor. Danışmanın incelediği veride x, y 0–1 aralığındaydı, yani görüntü boyutuna bölünmüş görünüyor. Gerçek değer aralığını yazdır, video çözünürlüğünü `videos.zip` içindeki bir videodan oku ve hangisinin doğru olduğunu ADIM dosyasına yaz. En-boy düzeltmesi buna bağlı: normalize ise `x *= W/H`, piksel ise düzeltme gerekmez.
- `cekirdek/veri.py`: zip'ten **doğrudan** okuma. Ex1 (ve istenirse Ex7) için `_2d.npy` dosyaları açılır. Her tekrar `first_frame − 10 … last_frame + 10` aralığında kesilir ve bellekte (video, kamera, yönelim) gruplarına ayrılır. Eklem seçimi kodun içinde yapılır; 33 eklemin hepsi de tutulabilir.
- **Eşdeğerlik testi:** Aynı tekrarlar için orijinal veriden okunan 13 eklem ile `rehab26_kucuk.npz` karşılaştırılır. En büyük mutlak fark ≤ 1e-3 olmalı (float16 yuvarlaması).

**Kabul ölçütü:**
- Veri tanıtım çıktısı ADIM_00'da var.
- Ex1 tekrar sayıları `Segmentation.csv` ile tutuyor.
- Eşdeğerlik testi geçti.
- Koordinat biçimi (piksel mi, normalize mi) netleşti.

---

## Adım 1 — Çekirdek modül ve regresyon testi

**Amaç:** `referans/deney1_omuz_olcutleri.py` içindeki mantığı yeniden kullanılabilir bir pakete taşımak, **davranışı değiştirmeden.**

**Yapılacaklar** — `cekirdek/` altında:
- `veri.py` (Adım 0'da başlandı): orijinal zip'ten okuma, segmentasyon ile eşleştirme, (video, kamera, yönelim) gruplaması, görüş açısı hesabı. İsteğe bağlı olarak `rehab26_kucuk.npz`'den okuma seçeneği; regresyon testi her iki kaynakla da çalıştırılabilsin. Orijinal veri float64, npz float16 olduğu için çok küçük farklar beklenir; ±0,01 toleransı ikisi için de geçerli.
- `geometri.py`: en-boy düzeltmesi, açı fonksiyonu.
- `ozellikler.py`: kol açısı ve omuz ölçütleri (M01, M01_tek, M39_F2, M33, YENI). Ölçüt eklemeyi kolaylaştıran bir kayıt sistemi (sözlük) kur; Adım 4'te yeni ölçütler eklenecek.
- `hizalama.py`: DTW yolu ve hizalama. Referans koddaki saf Python döngüsü yavaş; hızlandırabilirsin (numba veya vektörize), ama sonuç aynı kalmalı.
- `bant.py`: bant modeli (μ, τ, Q1 alt sınırı) ve bant hatası. Hem **yönsüz** (M39, referans) hem **yönlü** (yalnızca belirtilen yöndeki sapma) hata seçeneği olsun; yönlü olan Adım 4'te kullanılacak.
- `degerlendirme.py`: AUC, Ψ ve kişi bazlı bootstrap.
- `deneyler/deney1.py`: çekirdeği kullanarak referans deneyi yeniden üret ve `sonuclar/deney1/` altına yaz.
- `testler/test_deney1_regresyon.py`: `sonuclar/deney1/ozet.csv` ile `referans/beklenen_deney1_ozet.csv`'yi karşılaştıran test.

**Kabul ölçütü:** Tohum 0 ve en-boy 9/16 ile bant ve ham AUC değerleri beklenen tablodan en fazla **±0,01** sapıyor. Sapma varsa sebebini bul. Hızlandırma sonrası değişen kayan nokta sırası küçük farklar yaratabilir; 0,01'in altındaysa kabul et ve not et.

---

## Adım 2 — Deney 1'in kullanıcı tarafından çalıştırılması + şekiller 📤

**Yapılacaklar**
- Kullanıcıya `python -m deneyler.deney1` komutunu ver; kullanıcı çalıştırır.
- `deneyler/sekiller.py` ile iki şekil üret:
  1. Ölçütlere göre AUC çubuk grafiği, bantlı ve bantsız yan yana (`sonuclar/deney1/auc.png`).
  2. Bant örneği: bir kişi, önden kamera; bant (gri alan), bir doğru tekrar ve bir silkmeli tekrar. Örnek: `ex1_Honza`, `cam1`, yönelim 0 (`sonuclar/deney1/bant_ornegi.png`).
- ADIM_02'de kullanıcıya şekilleri nasıl okuyacağını 3–5 cümleyle anlat.

**Kabul ölçütü:** Kullanıcı aynı sayıları kendi bilgisayarında gördü; iki şekil oluştu.

---

## Adım 2b — Görsel kontrol aracı 📤

**Amaç:** Sistem kapalı bir kutu olmasın. Kullanıcı herhangi bir tekrarı videoda izleyip sistemin ne gördüğünü ve neden o kararı verdiğini kendi gözüyle kontrol edebilsin. Bu araç aynı zamanda hocanın Problem 3'ünün (referans ve kullanıcı hareketini çakıştırma) ilk sürümüdür.

**Yapılacaklar** — `araclar/gorsel_kontrol.py`:
```bash
python -m araclar.gorsel_kontrol --video ex1_Honza --kamera cam1 --yonelim 0 --tekrar 3
```
Çıktı bir MP4 dosyasıdır ve istenirse pencerede oynatılır. Ekran üç parçadan oluşur:
1. **Sol: orijinal video** (`videos.zip`) ve üzerinde:
   - veri setinin MediaPipe iskeleti, böylece kullanıcı noktaların doğru oturup oturmadığını görür;
   - referans iskelet: kişinin kendi doğru tekrarlarından biri, DTW ile zamanda, gövde merkezi, gövde boyu ve gövde ekseniyle geometride hizalanmış, yarı saydam ve farklı renkte;
   - banttan çıkan uzuvlar kırmızı.
2. **Sağ üst:** Seçilen ölçütün eğrisi, bant ve hareketli bir zaman imleci (dokümandaki bant grafiğinin canlı hali).
3. **Sağ alt:**
   - gerçek etiket (veri setinden);
   - sistemin kararı ve E değerleri;
   - Adım 5'ten sonra Türkçe cümle.

`videos.zip` yoksa iskeletler boş bir tuvale çizilir.

**Galeri:** Her deney betiği sonunda `sonuclar/<deney>/galeri/` klasörüne otomatik örnekler üretir. Her grup için 3'er MP4, tohum sabit:
- doğru yakalanan silkmeler
- kaçırılan silkmeler
- yanlış alarm verilen doğru tekrarlar
- (Deney 2'den sonra) karıştırılan hata türleri

ADIM dosyasında bu örneklerin listesi ve "neye bakmalı" notu yer alır.

**Kabul ölçütü:**
- Kullanıcı en az 5 tekrarı izledi.
- İskeletin videoya oturduğunu ve kararların görüntüyle tutarlı olup olmadığını ADIM dosyasına not etti.

---

## Adım 2c — Deney 1 v2: yöntem düzeltmeleri (ablasyon) 📤

Kaynak: `ilerleme/GUNCELLEME_02.md` (danışman, 6 Kasım akşamı). Adım 2b'deki kullanıcı gözlemlerinden (Petra, "sondaki sapma") çıkan yöntem sorunlarının düzeltilmesi.

**Amaç:** Her düzeltmenin etkisini ayrı ayrı göstermek. Deney 1 v1 (M39'a sadık hali) temel çizgi olarak **korunur ve silinmez**.

**Düzeltmeler (kararlar, bkz. `KARARLAR.md`):**
1. **Çoklu referans (zaman bandı):** Modeldeki her doğru tekrar sırayla referans yapılır, bant kurulur, E hesaplanır; E'lerin ortalaması alınır.
2. **Açı bandı** (`cekirdek/aci_bandi.py`): kol açısına koşullu bant. "Kol θ°'deyken bu kişinin omzu normalde nerede?"
   - Yalnızca etiketli tekrar kareleri. Faz: 5 karelik hareketli medyanla yumuşatılmış kol açısının tepesine kadar "kaldırma", sonrası "indirme".
   - 0–180°, 5° kutular, faz başına ayrı. Her kalibrasyon tekrarı her kutuya bir değer (o kutudaki karelerin ortalaması) verir.
   - μ = tekrar değerlerinin ortalaması; τ = t(0,975; n−1)·s/√n; alt sınır: geçerli kutulardaki τ'ların Q1'i.
   - Geçerli kutu: en az 3 tekrar katkı verir. Geçerli kutular arası boşluklar μ ve τ için doğrusal ara değerle doldurulur; kalibrasyon aralığının dışı geçersiz.
   - Değerlendirme: her kare kendi fazı ve kutusuna göre M39 kare hatası (yönsüz ve yönlü). E = geçerli karelerin ortalaması. Ayrıca `kapsam` (geçerli kare oranı) ve `aralik_disi` bayrağı (karelerin > %20'si kalibrasyonun en yüksek açısının 5°'den fazla üstünde).
   - Kalibrasyon aralığı dışındaki kareler değerlendirilmez (önceden verilmiş karar; test verisine bakarak değiştirilmez).
   - Yalnızca duruş ölçütleri için; yetersiz kaldırma Adım 4'te tepe açısıyla ayrı ele alınır.
3. **Pay hariç:** DTW, bant ve E yalnızca `first_frame … last_frame` aralığında. Dinlenme tabanı yine ilk 8 kare (pay dahil).

**Koşullar** (birikimli; hepsinde 5 omuz ölçütü, yönsüz bant):
| Kod | Bant | Pay | Referans |
| --- | --- | --- | --- |
| v1 | zaman (M39) | dahil | tek rastgele (Deney 1 aynen) |
| v1a | zaman | **hariç** | tek rastgele |
| v1b | zaman | hariç | **çoklu (sırayla hepsi, ortalama)** |
| v2 | **açı bandı** | hariç | yok |

Adillik kuralları aynen: doğru tekrar birini-dışarıda-bırak, hatalı tekrar aynı sayıda (n−1) doğru tekrarla. v2'de "atla" seçimi rastgele, tohum kullanılır.

**Çıktılar** (`sonuclar/deney1_v2/`):
- Koşul × ölçüt AUC tablosu: silkme/doğru, silkme/diğer, görüş grupları.
- Kişi bazlı AUC; "ortalama (en düşük–en yüksek)".
- YENI için "v2 − v1" farkının kişi bazlı bootstrap güven aralığı.
- v2'de tekrarların ortalama `kapsam`ı ve `aralik_disi` oranı, hata türüne göre.
- **Tohum duyarlılığı:** v1, v1b ve v2'de tohum 0 ile 1 arasında tekrar E'sinin değişimi (medyan ve > 0,05 oranı).
- **Görsel:** görsel kontrol aracına açı bandı görünümü (x: kol açısı, y: ölçüt, kalkış/iniş ayrı renk, bant + tekrarın noktaları). Petra cam1 o0 t5, Honza cam1 o0 t5, Terka cam1 o20 t10 için v1 ve v2 yan yana. Sunum adayı: "kol 90°'deyken omzun normal yeri".

**Dürüstlük notu (ADIM dosyasına):** Düzeltmeler aynı veriye bakılarak bulundu; v1→v2 kazancı iyimser olabilir. Doğrulama: Ex7'de ayarsız (Adım 4b) ve kendi kayıtlarımızda (Adım 7). v2 parametreleri (5° kutu, en az 3 tekrar, %20 bayrağı) **değiştirilmez**; kötü sonuç da olduğu gibi raporlanır.

**Kabul ölçütü:** Ablasyon tablosu, kişi tablosu, tohum duyarlılığı, üç örnek görsel. Kullanıcı Petra örneğini v1 ve v2'de izledi ve yorumunu ADIM dosyasına not etti.

**Ek — Güncelleme 03** (ADIM_02c'nin sonuna "Ek" olarak yazılır, yeni ADIM dosyası açılmaz):
- **Karar 7:** v1b ve v2'de hatalı tekrar, her doğru tekrar sırayla dışarıda bırakılarak kurulan n modelin E ortalamasıyla değerlendirilir (`cekirdek/adil_model.py`). v1 ve v1a Deney 1'e sadık kalır (tek rastgele "atla").
- Eski çıktı `sonuclar/deney1_v2_atla_rastgele/` olarak saklanır; yeni çıktı `sonuclar/deney1_v2/`.
- `bootstrap.csv`'ye silkme/diğer farkları (v2 − v1b, v2 − v1; YENI ve M33); ablasyon tablosuna "önden + çapraz" sütunları.
- **Kabul ölçütü:** tohum 0 ile 1 arasında |ΔE| hatalı tekrarlarda da 0 (v1b, v2).

---

## Adım 3 — Deney 1b: genel bant ile kişiye özel bant 📤

**Soru:** Kalibrasyon kişiye özel olmak zorunda mı? Başkalarının doğru tekrarlarından kurulan bir bant yeterli olur mu?

**Yöntem:** Her (kişi, kamera, yönelim) dizisi için üç koşul:
1. **Bant yok:** Deney 1'deki "ham" yöntem.
2. **Genel bant:** Aynı kamera ve yönelimde **diğer 4 kişinin** doğru tekrarlarından kurulan bant. Test kişisinin hiçbir tekrarı modele girmez. Referans tekrar diğer kişilerden rastgele seçilir; adil olmak için kişiye özel bantla aynı sayıda tekrar kullanılabilir (örneğin 4) — bu seçimi ADIM dosyasına yaz.
3. **Kişiye özel bant:** Deney 1'deki yöntem.

**Çıktı:** Her koşul için AUC (silkme/doğru, silkme/diğer), görüş grubuna göre AUC ve kişi bazlı bootstrap güven aralıkları. Ölçüt olarak en az YENI, M33 ve M39_F2. Sonuçlar `sonuclar/deney1b/` altına.

**Güncelleme 02:** Hem **v1b** (zaman bandı, çoklu referans, pay hariç) hem **v2** (açı bandı) ile çalıştırılır. Açı bandında genel bant doğal olarak tanımlıdır: diğer 4 kişinin doğru tekrarları, aynı kamera ve yönelim. Kişi bazlı AUC tablosu da verilir (Karar 5).

**Güncelleme 03:** Her ana sonuç iki biçimde: "uygulama senaryosu: önden + çapraz (|görüş| ≤ 60°)" ve "tüm görüşler" (Karar 6); profil ayrıca sınırlılık olarak. Hatalı tekrarlar Karar 7 ile (tüm (n−1)'li modellerin ortalaması) değerlendirilir.

**Deney 1c — zamansal yumuşatma** (aynı adımda): Hocanın Problem 2 için önerdiği iyileştirmelerden biri. MediaPipe noktaları kareden kareye titrer (jitter).
- `cekirdek/yumusatma.py`: One Euro filtresi ve Savitzky–Golay. Parametreler eğitim kişilerinde seçilir.
- Deney 1, yumuşatmalı ve yumuşatmasız tekrarlanır: YENI, M33 ve M39_F2 ölçütleri, kişiye özel bant (v1b ve v2).
- Ayrıca bir doğru tekrarda ham ve yumuşatılmış omuz noktası yörüngesi tek bir şekilde gösterilir (`sonuclar/deney1c/titreme.png`).

**Kabul ölçütü:**
- Üç koşulun tablosu ve "genel bant – kişiye özel bant" farkı için güven aralığı var.
- Yumuşatmalı ve yumuşatmasız karşılaştırma tablosu ve titreme şekli var.

---

## Adım 4 — Deney 2: hata türünü bulma 📤

**Soru:** Sistem, bir tekrarın doğru mu olduğunu, yanlışsa **hangi hatayı** içerdiğini bulabiliyor mu?

**Hata türü başına ölçütler** (Ex1, sağ kol; M39 Tablo 1'den uyarlama; hepsi en-boy düzeltmeli 2B):

| Hata kodu | Ölçüt | Tanım |
| --- | --- | --- |
| `ERR_ELEVATED_SHOULDER` | `omuz` = YENI | (y sağ omuz − y sağ kulak) / gövde uzunluğu |
| `ERR_HEAD_TO_SIDE` | `bas` (M39 F3) | (omuz ortası → kulak ortası) vektörü ile (kalça ortası → omuz ortası) vektörü arasındaki açı |
| `ERR_ARM_FORWARD` | `on_kacma` (M39 F1) | sağ bilek – sağ omuz – sağ kalça açısı; ayrıca aday: `kol_boyu` = sağ omuz–bilek mesafesi / gövde (öne giden kol önden kamerada kısa görünür) |
| `ERR_BENT_ARM` | `dirsek` (M39 F4) | sağ omuz – sağ dirsek – sağ bilek açısı |
| `ERR_LOW_ABDUCTION` | `kaldirma` (M39 F5) | sağ bilek – sağ omuz – sol omuz açısı |

**Karar kuralı** (basit ve açıklanabilir kalmalı):
1. Her tekrar için her ölçütün bant hatası E_k hesaplanır. Doğru tekrarlar birini-dışarıda-bırak ile, hatalılar adil modelle değerlendirilir (Deney 1'deki gibi).
2. Her ölçüt, **eğitim kişilerinin** doğru tekrarlarındaki dağılımına göre ölçeklenir: z_k = (E_k − medyan) / (çeyrekler arası açıklık + ε).
3. max z_k < T ise "doğru" denir; değilse hata türü = argmax z_k.
4. T, **kişi bazlı birini-dışarıda-bırak** ile eğitim kişilerinde makro-F1'i en yükseğe çıkaracak şekilde seçilir.
5. Yönsüz ve yönlü bant ayrı ayrı raporlanır. Yönlü bantta yön, hatanın beklenen yönüdür; örneğin `omuz` için mesafe bandın **altına** iniyorsa. Her ölçüt için beklenen yönü doğru tekrarlar ile ilgili hatalı tekrarların ortalama farkından eğitim kişilerinde belirle; elle yazma.
6. Hem `on_kacma` hem `kol_boyu` denenir; hangisinin kullanılacağına eğitim kişilerinde karar verilir.

**Çıktılar** (`sonuclar/deney2/`):
- 6 sınıflı (DOGRU + 5 hata) karışıklık matrisi: CSV + PNG.
- Sınıf başına duyarlılık/kesinlik/F1, makro-F1, doğruluk.
- Görüş grubuna göre makro-F1.
- **Katı** değerlendirme (yalnızca birincil hata) ve **esnek** değerlendirme (ek hatalardan birini söylemek de doğru sayılır).
- Karşılaştırma için basit bir temel çizgi: tek bir toplam hata (E'lerin ortalaması) ile yalnızca doğru/yanlış ayrımı.

**Güncelleme 02 değişiklikleri:**
- **Duruş ölçütleri** (omuz = YENI, baş, dirsek, öne kaçma / kol boyu): **açı bandı** + **yönlü** seçenek.
- **Yetersiz kaldırma:** bant yerine tepe açısı. Sapma = (kalibrasyon tekrarlarının tepe açılarının medyanı − tekrarın tepe açısı); kalibrasyon tepelerinin çeyrekler arası açıklığına (alt sınır 5°) bölünerek z'ye çevrilir.
- `aralik_disi` bayrağı ("kol normalden yüksek") karar kuralına bir girdi olabilir; eğitim kişilerinde gerekli olup olmadığına bakılır.
- Adım 2c'de açı bandı zaman bandından belirgin şekilde kötü çıkarsa Adım 4'e geçmeden danışmana sorulur.

**Güncelleme 03 değişiklikleri:**
- **Karar 6:** Duruş ölçütleri için **yalnızca açı bandı**; görüşe göre yöntem değiştiren karma çözüm yok. Her ana sonuç iki biçimde: "uygulama senaryosu: önden + çapraz (|görüş| ≤ 60°)" ve "tüm görüşler". Profil (70–90°) gerekçesiyle sınırlılık olarak ayrıca raporlanır. **v1b** (zaman bandı, çoklu referans) karşılaştırma temel çizgisi olarak raporlanır, karar kuralına girmez.
- **Karar 7:** Hatalı tekrarlar tüm (n−1)'li modellerin E ortalamasıyla değerlendirilir (`cekirdek/adil_model.py`).

**Güncelleme 04 değişiklikleri:**
- Açı bandı ayrıntı çıktısı kare bazında imzalı sapma, faz, kol açısı, ölçütün ham değeri ve μ'yü verir (Adım 5'teki "normalde X, sende Y" için); davranış değişmez.
- Galeri `sonuclar/deney2/galeri/` (önden + çapraz): en sık karışan iki hata çifti + kaçırılan hatalar, her gruptan 3 video; görsel kararı veren ölçütün eğrisini ve bandını gösterir.
- Temel çizgi (tek toplam hata, doğru/yanlış) ve 6 sınıflı kural aynı tabloda.
- Basit anlatım: "100 hatalı tekrarın kaçında hatanın türünü doğru söyledi?"
- Karar 10–12: yumuşatma kullanılmaz; kişiye özel kalibrasyon zorunlu; Karar 7 pürüzsüzleştirme notu.

**Güncelleme 05 değişiklikleri (Deney 2 revize):**
- **Karar 13 — az kaldırma puanı 0–1 biçiminde.** Kalibrasyon tepeleri için tek kutulu bant: μ = tepelerin ortalaması, τ = max(t(0,975; n−1)·s/√n, **10°**), eksik = μ − tekrarın tepesi; E = 0 (eksik ≤ τ), değilse min(1, (eksik − τ)/τ). Yönlüde yalnızca eksik, yönsüzde |fark|. Sonra diğer ölçütlerle aynı z ölçeklemesi ve karar kuralı. 10° literatürden (M20, M41, M42) ve **değiştirilmez**.
- İlk sürüm sonuçları `sonuclar/deney2_ilk/` altında korunur ("ilk sürüm"); revize `sonuclar/deney2/`. T ve diğer seçimler yine kişi bazlı birini-dışarıda-bırak.
- **Karar 14 — "ilk iki" metriği:** hatalılarda gerçek birincil hata en yüksek iki z içinde mi (/100) ve ikinci z'nin de T'yi geçme oranı.
- **Karar 15:** Ana sistem v2 yönlü. **Karar 16:** `aralik_disi` karar kuralına eklenmez; betimsel + sınırlılık.
- Doğrulama: Ex7 (Adım 4b, ayarsız) ve kendi kayıtlar (Adım 7).

**Güncelleme 06 değişiklikleri:**
- **Karar 17:** Az kaldırmada **ilk sürüme** dönülür (d = (tepe medyanı − tepe) / max(IQR, 5°)); kodda `kaldirma_surumu = "ilk" | "revize"`, varsayılan `"ilk"`. Revize `sonuclar/deney2_revize/` altında, başarısız deneme olarak raporlanır. (b) ve (c) denenmez → `docs/GELECEK_CALISMA.md`.
- **Karar 18:** Yöntem donduruldu (Ex1: v2 + yönlü + ilk sürüm kaldırma + Karar 7 + LOSO ile T; Ex7: Adım 4b). Sonraki bütün adımlar bunu kullanır.
- **Karar 19:** Ex7 sonuçları ana sistemi değiştirmez. **Karar 20:** iddia kapsamı (KARARLAR.md).

**Kabul ölçütü:** Tüm tablolar var; T seçiminin her kişide hangi değere düştüğü yazılmış.

---

## Adım 4b — Ex7'de ayarsız doğrulama 📤 (Güncelleme 02; eski Adım 11)

- Adım 4 bittikten sonra son yöntem (açı bandı + Deney 2 kuralı) Ex7 omuz ekstansiyonunda **hiçbir parametre değiştirilmeden** çalıştırılır.
- Kol açısı tanımı aynı: üst kolun aşağı dikeyle yaptığı açı.
- Ex7'nin hata türleri farklı; omuz silkmesi (`ERR_ELEVATED_SHOULDER`) ortak. En azından Deney 1 (silkme/doğru AUC) raporlanır.
- Ekstansiyon önden zor görülür; görüş gruplarına göre ayrı raporlanır. Bu, "yöntem başka bir harekette de çalışıyor mu" kanıtıdır ve Adım 2c'deki iyimserlik riskine karşı doğrulamadır.

**Güncelleme 05 — Ex7 ölçüt–hata eşlemesi (önceden belirlenmiştir):**

| Ex7 hata kodu | ölçüt |
| --- | --- |
| `ERR_ELEVATED_SHOULDER` | YENI (aynı) |
| `ERR_BENT_ARM` | `dirsek` (aynı) |
| `ERR_TORSO_FORWARD` | gövde öne eğimi: (kalça ortası → omuz ortası) vektörünün dikeyle açısı |
| `ERR_TORSO_ROTATION` | omuz genişliği / kalça genişliği oranı (dönme 2B'de omuz çizgisini kısaltır) |
| `ERR_ARM_TO_SIDE` | `kol_boyu` (Ex1'deki öne kaçmanın simetriği) |

- Ex7'de "az kaldırma" sınıfı yoktur; Ex7'nin kendi 5 hatası kullanılır. Kol açısı tanımı aynı.
- Yeni ölçütler (gövde eğimi, gövde dönmesi) açı bandıyla değerlendirilir.
- Deney 1 (silkme/doğru AUC; v1b ve v2) + Deney 2 kuralı Ex7 hata türleriyle.
- Eşik T ve ölçekleme Ex7'nin içinde yine kişi bazlı birini-dışarıda-bırak. **Ex1'de bulunan hiçbir sabit değiştirilmez:** 5° kutu, en az 3 tekrar, %20 bayrağı, 10° alt sınır.
- Sonuçlar görüş gruplarına göre. **Uygulama senaryosu (önceden):** yan veya çapraz (|görüş| ≥ 30°), çünkü ekstansiyon sagital düzlemdedir.

**Kabul ölçütü:** Ex7 silkme/doğru AUC tablosu (görüş grubu ve kişi bazlı); hiçbir parametrenin değiştirilmediği ADIM dosyasında belirtilmiş.

---

## Adım 5 — Deney 3: kural tabanlı Türkçe geri bildirim 📤

**Amaç:** Deney 2'nin kararını kişinin anlayacağı bir cümleye çevirmek ve cümlenin doğru hatayı söyleyip söylemediğini ölçmek.

**Sapma kodu** (`cekirdek/geribildirim.py`). Her hatalı tekrar için en yüksek z'li 1, en fazla 2 hata alınır ve her biri için bir kod üretilir:
- `hata`: hata türü
- `taraf`: "sağ" (Ex1'de sağ kol)
- `faz`: kaldırırken / kol en üstteyken / indirirken. Referans tekrarın kol açısı eğrisine göre belirlenir: tepe = kol açısının en büyük değerinin %85'inin üstü; öncesi kaldırma, sonrası indirme. Bant dışı fazlalığın en çok toplandığı faz seçilir.
- `yon`: bandın üstü mü altı mı
- `siddet`: hafif / belirgin / çok belirgin. Eşikler eğitim kişilerinin hatalı tekrarlarındaki E dağılımının üçte birlik dilimlerinden alınır.
- `olcu` ve `beklenen` (**hocanın şartı: hatanın büyüklüğü fiziksel olarak söylenmeli**): Bant dışı sapmanın en büyük olduğu anda kişinin ölçülen değeri ile bandın ortası (μ), birimiyle. Kullanıcıya gösterilecek birimler:
  - açı ölçütleri (dirsek, baş, öne kaçma, kaldırma): derece;
  - omuz için **omuz çizgisinin gövde eksenine göre açısı** (derece; hocanın P2 listesindeki "omuz çizgisinin gövde eksenine göre açısı") ve kulak–omuz mesafesi "gövde boyunun %'si". Tespit yine YENI ile yapılır; derece yalnızca anlatım içindir.
  - Santimetre kullanma; tek kameradan güvenilir ölçek yok.

Hocanın örnek çıktısı: *"Sağ kolunu yaklaşık 90° kaldırman gerekiyordu; sen 80° kaldırdın. Kolunu yaklaşık 10° daha yukarı kaldırmalısın."* Bizim cümlelerimiz bu ayrıntıda olmalı.

**Şablonlar.** Her hata ve yön için 1–2 şablon, sade Türkçe, **ölçü + düzeltme** içeren. Örnekler (geliştirilebilir):
- omuz, yukarı: "{Faz} sağ omzunu kulağına doğru {siddet} kaldırıyorsun: omuz çizgin normalde yaklaşık {beklenen}° iken {olcu}°'ye çıktı. Omzunu aşağıda ve gevşek tut; kolu omuzdan değil, koldan kaldır."
- bas: "{Faz} başını yaklaşık {fark}° yana eğiyorsun. Başını dik tut, karşıya bak."
- dirsek: "{Faz} dirseğin yaklaşık {fark}° bükülüyor (normalde {beklenen}°, sende {olcu}°). Kolunu düz tut."
- on_kacma: "{Faz} kolun yaklaşık {fark}° öne kaçıyor. Kolunu vücudunla aynı hizada, tam yana kaldır."
- kaldirma: "Kolunu en fazla {olcu}° kaldırdın; normalde {beklenen}° civarına çıkıyordun. Yaklaşık {fark}° daha yukarı uzan."
- doğru (hocanın şartı: olumlu ve **somut**): "Hareketi doğru yaptın. Kolun {olcu_kol}°'ye kadar çıktı; omzun ve dirseğin normal aralıkta kaldı." Aynı cümle sürekli tekrarlanmasın diye 3–4 varyasyon olabilir.

**Değerlendirme** (`deneyler/deney3.py`):
- Bir **anahtar kelime çıkarıcı** yaz (`cekirdek/metin_cozumleyici.py`). Bir cümleden hangi hata türlerinin söz edildiğini bulur; sözlük tabanlı, örneğin omuz + kulak/kaldır → omuz. Deney 4'te LLM cümleleri de aynı çıkarıcıyla ölçülecek, bu yüzden şablonlara özel değil, genel yazılmalı. Kendi şablonlarında %100 doğru çalıştığını test et; ayrıca 15–20 elle yazılmış farklı cümleyle de test et.
- Metrikler:
  - hatalı tekrarlarda "cümle doğru hatayı adlandırdı" oranı (katı ve esnek)
  - doğru tekrarlarda gereksiz uyarı oranı
  - görüş grubuna göre aynı metrikler
- Kullanıcı okusun diye 20 rastgele örnek cümle (tohum sabit) `sonuclar/deney3/ornek_cumleler.md` dosyasına; yanında gerçek etiket yazılı olsun.

**Güncelleme 05:** "İlk iki" metriği (Karar 14) Deney 3'te de raporlanır: birincil hata söylenen ilk iki hata içinde mi; 2. hata yalnızca o da T'yi geçerse söylenir.

**Güncelleme 06:** Dondurulmuş yöntem (Karar 18) kullanılır; kaldırma ilk sürüm. Değerlendirme katı / esnek / ilk iki + "cümle doğru hatayı adlandırdı mı" (çıkarıcı ile) + doğrularda gereksiz uyarı. Ana tablo önden + çapraz; tüm görüşler de verilir. Sonuçlardan bağımsız seçimler (faz sınırları, şiddet eşikleri, ölçünün anı, hatalıda μ, az kaldırmanın şiddeti) kod yazılmadan önce `ADIM_05.md` "Önceden belirlenenler" bölümüne yazılıp commit'lenir.

**Güncelleme 07** (ayrıntı: `ilerleme/GUNCELLEME_07.md`, `KARARLAR.md`):
- **Karar 21 — sağlam ölçü:** cümledeki ölçü tek kare yerine seçilen fazın güvenilir karelerinin medyanından; `olcu_surumu = "tek_kare" | "saglam"`, uygulamada varsayılan `"saglam"`. Tespit ve metrikler değişmez (`assert`); tek deneme.
- **Karar 22–23:** şiddet tanımı değişmez ("hafif"in çıkmaması sınırlılık); Deney 3 iddialarının gücü tablo halinde (çıkarıcı uyumu zayıf kanıt).
- **Karar 28 — iki katmanlı geri bildirim:** aynı `SapmaKodu`'ndan `hasta_cumlesi` (kısa, yüzde yok, yalnızca 5°'ye yuvarlanmış derece, şiddet kelimesi yok) ve `uzman_ayrintisi` (bugünkü ölçülü cümle). Çıkarıcı ikisinde de çalışır; metrikler eşit olmalı.
- Adım 5, ADIM_05'e "Ek: Güncelleme 07" yazılıp kullanıcı yeni hasta cümlelerini onaylayınca kapanır.

**Kabul ölçütü:** Metrik tablosu ve örnek cümleler var. Kullanıcı örnekleri okuyup anlaşılır bulduğunu veya düzeltme önerilerini ADIM dosyasına not etti.

---

## Adım 6 — Uygulama 📤

**Amaç:** Ders sunumundaki demo. Derste gösterilen yoga uygulamasına benzer: görüntü ve iskelet bir tarafta, geri bildirim paneli diğer tarafta.

**Teknik tercih:** OpenCV penceresi + MediaPipe Tasks `PoseLandmarker` (model: `pose_landmarker_full.task`, ilk çalıştırmada indirilir). Streamlit'te canlı kamera zahmetli olduğu için tercih edilmedi. Daha iyi bir fikrin varsa öner, kullanıcı onaylasın.

**Akış** (`uygulama/main.py`):
1. **Egzersiz seçimi:** Şimdilik tek egzersiz: "Kolu yana kaldırma (sağ kol)". Menü yapısı ileride yenisi eklenebilecek şekilde kurulsun.
2. **Kalibrasyon modu:** Kişi fizyoterapist eşliğinde doğru tekrarlar yapar: **varsayılan 6, en az 5** (Güncelleme 03, Karar 8; açı bandındaki "en az 3 tekrar" kuralı 4 tekrarlık modelde sınırda kalıyordu). Arayüz bunu söyler.
   - **Kamera açısı kontrolü (Karar 9):** Kalibrasyonun başında dinlenme duruşundaki omuz genişliği / gövde uzunluğu oranından kişinin kameraya ne kadar dönük olduğu kabaca tahmin edilir. Oran, veri setinin önden (0–20°) doğru tekrarlarındaki tipik değerin belirgin altındaysa uyarı: "Kameraya daha önden durun." Eşik ve gerekçesi ADIM_06'ya yazılır.
   - Tekrar ayırma ve onay: Tekrarlar otomatik ayrılır; kullanıcı her tekrarı onaylar veya reddeder. Ölçüt dizileri `profiller/<isim>.npz` dosyasına kaydedilir.
3. **Değerlendirme modu:** Canlı kamera **veya** video dosyası (`--video yol.mp4`). Her tekrar bitince:
   - çekirdekteki bant modeli ve Deney 2 kararı uygulanır,
   - panelde tekrar numarası, karar (doğru/hata) ve Deney 3'ün Türkçe cümlesi gösterilir.
   - Son 5 tekrarın geçmişi panelde kalır.
4. **Tekrar ayırma:** Canlıda kol açısına dayalı durum makinesi: dinlenme → kaldırma → tepe → indirme (M01). Örnek eşikler: kol açısı 30°'yi geçince başlangıç, 20°'nin altına dönünce bitiş; en kısa süre 0,8 s. Eşikleri ve gerekçesini ADIM dosyasına yaz.
5. **En-boy:** Uygulamada gerçek kare boyutu bilinir; x, W/H ile çarpılır. 9/16 sabiti yalnızca REHAB26 içindir (Adım 0'da netleşen biçime göre).
5b. **Referans iskelet bindirme (hocanın Problem 3'ü):** Her tekrar bittiğinde o tekrarın kısa tekrar oynatımı gösterilir. Üzerinde:
   - kullanıcının iskeleti;
   - kalibrasyondaki referans tekrarın iskeleti, yarı saydam ve farklı renkte;
   - banttan çıkan uzuvlar kırmızı, diğerleri yeşil;
   - hatanın en büyük olduğu anda kısa bir etiket, örneğin "omuz +7°".

   Hizalama:
   - **Zamansal:** DTW, kol açısına göre (Adım 1'deki çekirdek).
   - **Geometrik:**
     1. referans iskelet kullanıcının gövde merkezine (iki omuz ve iki kalça ortalaması) ötelenir;
     2. gövde uzunluğu oranında ölçeklenir;
     3. gövde ekseni açısı kadar döndürülür.
     Alternatif: gövde noktaları üzerinde Procrustes (`scipy.linalg.orthogonal_procrustes`).

   Bu kod Adım 2b'deki görsel kontrol aracıyla **ortak** olmalı (`cekirdek/bindirme.py`).
5c. **Omuz yörüngesi:** Panelde son tekrarın omuz ölçütü eğrisi ve bandı küçük bir grafikle gösterilir (hocanın P2 çıktısı: "hareket yörüngesi").
6. **Türkçe karakter:** `cv2.putText` Türkçe karakter çizemez. Panel metni PIL (`ImageDraw` + TTF font) ile çizilmeli.
7. **Kayıt:** Her oturumun tekrar sonuçları `oturumlar/<tarih>.csv` dosyasına yazılır.
8. **Yığın modu:** `python -m uygulama.toplu --profil X --video Y` aynı değerlendirmeyi pencere açmadan yapar ve CSV üretir. Adım 7 bunu kullanır.

**Kabul ölçütü:**
- Kullanıcı kendi kamerasıyla kalibrasyon yapıp en az 5 tekrar değerlendirdi.
- Video dosyası modu çalışıyor.
- Uygulama kararları çekirdek kodu içe aktarıyor; kopya kod yok.

**Güncelleme 07** (ayrıntı: `ilerleme/GUNCELLEME_07.md`, `KARARLAR.md`):
- **Karar 24 — kural parametreleri:** beş kişinin önden + çapraz tekrarlarıyla, LOSO eğitim adımıyla aynı prosedür; `python -m araclar.kural_disa_aktar` → `modeller/kural_ex1.json` (sürüm bilgisiyle). Değerler ADIM_06'da LOSO değerleriyle yan yana.
- **Karar 25 — tekrar ayırma:** önceden sabit kural (`cekirdek/tekrar_ayirici.py`; 30°/20°, tepe ≥ 60°, ≥ 0,8 s, sınırlar dinlenmeye uzatılır); `python -m deneyler.tekrar_ayirma` ile `Segmentation.csv`'ye karşı sınanır (IoU ≥ 0,5). Eşikler sonuca göre değiştirilmez.
- **Karar 26 — kamera açısı uyarısı:** eşik, çapraz (30–60°) doğru tekrarlardaki omuz genişliği / gövde boyu oranının 10. yüzdeliği (yukarıdaki "önden" ifadesinin yerini alır); uyarı kalibrasyonu engellemez.
- **Karar 27 — demo güvenliği:** video dosyası modu birincil demo yolu, yedek kayıt hazır; mümkünse MediaPipe v0.10.20 + `pose_landmarker_full`; yalnızca Ex1. Panelde hasta cümlesi büyük, uzman ayrıntısı küçük (Karar 28).

---

## Adım 7 — Kendi kayıtlarımızla deneme 📤

**Çekim protokolü** (kullanıcı çeker):
- Telefon tripodda, göğüs hizasında, 2–2,5 m uzakta; kişiye önden veya en fazla 30° çapraz. Dikey çekim olabilir. Arka plan sade, ışık önden.
- `kalibrasyon.mp4`: 5 doğru tekrar.
- `test.mp4`: 5 doğru, 3 omuz silkmeli, 2 baş eğik, 2 dirsek bükük, 2 yetersiz kaldırma tekrarı; sıra karışık.
- Çekim sırasında hangi tekrarın ne olduğu `etiketler.csv` dosyasına yazılır: `tekrar_no, etiket`.
- İstenirse ikinci bir kişiyle tekrar edilir (arkadaş veya aile).

**Yapılacaklar:** Yığın moduyla değerlendir; etiketlerle karşılaştır. Karışıklık matrisi ve tekrar başına "verilen cümle – gerçek etiket" tablosunu `sonuclar/kendi_kayit/` altına yaz.

**Kabul ölçütü:** Tablo var; sistemin yanıldığı tekrarlar için kısa bir gözlem yazıldı (örneğin "baş eğme omuz olarak algılandı").

---

## Adım 6b — (Yetişirse) Omuz bölgesi siluet ölçütü 📤

**Fikir:** MediaPipe omzu tek bir nokta olarak veriyor. Oysa omuz silkilince boyun ile omuz arasındaki **siluet çizgisi** (trapez kası hattı) görünür şekilde yükselir. Hocanın P2 önerileriyle örtüşüyor: "shoulder ROI", "genel pose keypointlerini lokal görüntü özellikleriyle birleştirme". MediaPipe Pose Landmarker isteğe bağlı bir segmentasyon maskesi verebiliyor.

**Yöntem (taslak):**
1. Kulak ile omuz arasında, egzersiz yapan tarafta bir ilgi bölgesi (ROI) tanımlanır.
2. ROI içinde segmentasyon maskesinin üst sınırı (siluetin en üst pikseli) birkaç dikey sütunda bulunur.
3. "Siluet omuz yüksekliği" = bu sınırın kulağa göre dikey konumu / gövde uzunluğu.
4. Bu yeni ölçüt, YENI ile aynı bant çerçevesinde değerlendirilir.

**Veri:** `videos.zip` içinden yalnızca Ex1, önden ve çapraz görüş açıları, tekrar kareleri ±10. MediaPipe segmentasyonu bir kez çalıştırılıp `veri/ara/` altına önbelleğe alınır. Süreyi önceden tahmin et ve kullanıcıya söyle.

**Kabul ölçütü:** YENI ile siluet ölçütünün AUC karşılaştırması ve görsel kontrol aracında siluet sınırının çizildiği 3 örnek video. Sonuç olumsuz çıksa da raporlanır.

---

## Adım 8 — Deney 4: LLM ile kural tabanlı karşılaştırması 📤 (bildiri katmanı)

**Soru:** Aynı bilgi bir LLM'e verilirse, kurallardan daha iyi ya da daha kötü bir cümle mi çıkar?

**Koşullar:**
- **A — Kural tabanlı:** Deney 3.
- **B — LLM + sapma kodları:** Sapma kodları JSON olarak verilir; LLM yalnızca cümleye çevirir.
- **C — LLM + ham özet:** M21 tarzı. Her ölçüt için kişinin değeri ve bant sınırları (en büyük, en küçük, ortalama) verilir, sapma kodu verilmez; LLM hatayı da kendisi bulur.

**Sağlayıcı:**
- **Gemini ücretsiz katmanı.** Google AI Studio'dan alınan API anahtarı, `GEMINI_API_KEY` ortam değişkeninde tutulur. Güncel ücretsiz modelleri ve limitleri resmi sayfadan kontrol et: https://ai.google.dev/gemini-api/docs/rate-limits — limitler sık değişiyor.
- **Ollama yedeği.** Yerel küçük bir model; Türkçe kalitesini ADIM dosyasında belirt.
- `cekirdek/llm.py` sağlayıcıdan bağımsız bir arayüz olsun. `temperature = 0`.
- **Her yanıt `sonuclar/deney4/onbellek.jsonl` dosyasına kaydedilir;** tekrar çalıştırmada yeniden istek atılmaz.
- Hız sınırı için bekleme ve yeniden deneme eklenir.

**Örneklem:** Ücretsiz limitler yüzünden tabakalı bir alt küme kullanılır. Örnek: önden ve çapraz görüşten 50 doğru + her hata türünden 20 tekrar = 150 tekrar, tohum sabit. Koşul başına 150 istek atılır.

**Metrikler:** Aynı anahtar kelime çıkarıcıyla:
- hata adlandırma doğruluğu
- gereksiz uyarı oranı
- **uydurma oranı**: girdide olmayan bir sayı ya da derece içeren cümleler; B koşulunda girdide olmayan bir vücut bölgesinden söz eden cümleler
- ortalama cümle uzunluğu

İstem metinleri `deneyler/istemler/` altında dosya olarak saklanır; ADIM dosyasına da kopyalanır.

**Kabul ölçütü:** Üç koşulun tablosu ve her koşuldan 5 örnek cümle.

---

## Adım 9 — Sonuçları dondurma 📤

- Tüm deneyleri temiz bir çalıştırmayla yeniden üret: `python -m deneyler.hepsi`.
- `sonuclar/OZET.md` dosyasını yaz: her deneyin tek tablosu, en önemli 3 şekil ve 5 maddelik "ne öğrendik".
- Sürümleri yaz: Python ve tüm kritik paketler (`pip freeze` çıktısından). Hocanın raporu "yeniden kurulabilirlik" istiyor.
- `docs/YENIDEN_KURULUM.md`: başka bir öğrencinin sistemi sıfırdan kurabilmesi için 5–8 adım. Hocanın rapor şablonundaki 7 başlığa göre yazılır: ortam, girdi hazırlığı, pose çıkarımı, hizalama, hata hesabı, geri bildirim, çıktı. 1 sayfalık rapor buradan yazılacak.
- `docs/LLM_KULLANIMI.md`: projede üretken yapay zekânın nerede ve hangi amaçla kullanıldığı (Claude Code: kod; Claude: literatür, planlama, analiz). Hocanın kuralı gereği raporda kısa bir notla belirtilecek.
- Git etiketi: `v-sunum`.

**Kabul ölçütü:** `OZET.md` var ve sayılar ADIM dosyalarındaki sayılarla tutarlı.

---

## Adım 10 — (Yetişirse) REHAB24-6 doğrulaması

REHAB24-6 (M34): 10 kişi, Ex1 kol abdüksiyonu, yalnızca doğru/yanlış etiketi var. Adımlar:
1. Kullanıcı Zenodo'dan MediaPipe çıktılarını veya videoları indirir.
2. Yanlış Ex1 tekrarlarını izleyip omuz silkmesi olanları **elle etiketler**. Bunun için bir etiketleme betiği yazılır: tekrarı oynatır, kullanıcı tuşla etiket girer.
3. Deney 1 ve Deney 2 burada, ayar yapılmadan çalıştırılır: "Hiç görmediği 10 kişide de çalışıyor mu?"

## Adım 11 — Ex7 genellemesi → Adım 4b'ye taşındı

Güncelleme 02 ile önceliği yükseldi ve zorunlu **Adım 4b** oldu (yukarıya bakın). Kol açısı tanımı Adım 1'dekiyle aynı (üst kolun aşağı dikeyle açısı); ayrı bir "geriye açı" tanımlanmaz.
