# ADIM 09 — Sonuçları dondurma

**Tarih:** 2026-11-07 (hazırlık; Güncelleme 09, Karar 37–39), 2026-11-09 (Güncelleme 12, Karar 51–56)
**Durum:** Kısmen. Belgeler, önbellekli yeniden üretim ve sunum girdileri hazır (en sondaki Ek: Güncelleme 12). Tam yeniden üretim 119/120 aynı; tek fark Karar 57 ile giderildi ve Ex7 doğrulandı (24/24). Ardından `OZET.md`'ye yeniden üretim satırı, `v-sunum` etiketi ve push (Karar 55). Hedef 11 Kas.

## Basit anlatım
- **Yeniden üretim:** `deneyler/hepsi.py` projenin son kaydedilmiş (commit'lenmiş) hâlinin temiz bir kopyasını açıyor. Bu kopyada eski sonuç dosyaları yok. Bütün deneyleri sırayla baştan çalıştırıp çıkan her tabloyu bizim kayıtlı tablolarımızla karşılaştırıyor. Hepsi aynı çıkarsa "bu sonuçlar bu koddan, bu veriden çıkıyor" diyebiliriz. Hocanın istediği "yeniden kurulabilirlik" budur.
- **Taslak belgeler:** Başka bir öğrencinin sistemi kurabilmesi için adım adım bir kılavuz, yapay zekânın nerede kullanıldığını anlatan bir not ve paket sürümleri. Başlarında `TASLAK` yazıyor; sayılar dondurmada kesinleşecek.
- **Sunum şekilleri:** Kayıtlı sonuçlardan beş şekil adayı ve uygulamanın 25 saniyelik bir ekran kaydı. Hangilerinin slayta gireceğine danışmanla birlikte karar verilecek.

*Jargon:* **Git worktree:** aynı depodan, ayrı bir klasörde açılan ikinci bir çalışma kopyası. **Regresyon:** yeni çalıştırmanın eski sonuçla aynı çıkıp çıkmadığının denetimi.

## Yapılanlar
### Karar 37 — yeniden üretim ve taslak belgeler
- `deneyler/hepsi.py`:
  1. `git worktree add --detach <hedef> HEAD` ile temiz kopya açılır (varsayılan hedef: sistemin geçici klasöründe `omuz_hepsi_temiz`). Kopyada `sonuclar/` ve deneylerin ürettiği `modeller/*.json` silinir.
  2. Veri kopyalanmaz ve bağlanmaz. Kopyadaki kod `OMUZ_VERI` ortam değişkeniyle asıl `veri/` klasörünü yalnızca okur. Bunun için `cekirdek/veri.py`'ye `VERI_KOK` eklendi; değişken yoksa davranış aynı.
  3. Karar 37'deki sıra: Deney 1, 1 v2, 1b, 1c, 2, Ex7, 3, 3 (sağlam), tekrar ayırma, kamera açısı, hız eşiği, kural dışa aktarma.
  4. Her CSV ve `modeller/*.json` kayıtlı dosyayla karşılaştırılır: aynı sütunlar ve boyut, sayısal sütunlarda en büyük mutlak fark ≤ 1e-9, metin sütunları birebir. JSON'larda `tarih` ve `bilgi` (sürüm/commit) alanları yok sayılır.
  5. Çıktı: `sonuclar/hepsi/` altında `adimlar.csv`, `regresyon.csv`, `listelenen.csv`, `ozet.md`.
  6. Adım 7 ve 8 ile yeniden üretilmeyen diğer kayıtlı klasörler (ör. `deney2_revize`, `uygulama_saglik`) yalnızca listelenir.
  7. Galeri ve şekil üretimi kapalı (`--galeri-yok`, `--sekilsiz`): yalnızca tablolar karşılaştırılır.
- `testler/test_hepsi.py`: CSV ve JSON karşılaştırmasının farkı yakalaması, tarih/bilgi alanlarının yok sayılması, eksik/yeni dosya, adım sırası.
- Taslaklar: `docs/YENIDEN_KURULUM.md` (hocanın 7 başlığı), `docs/LLM_KULLANIMI.md`, `docs/SURUMLER.md` (Python 3.11.9, `pip freeze`, MediaPipe notu).

### Karar 38 — sunum şekil adayları
`python -m deneyler.sunum_sekilleri` (~75 s) → `sonuclar/sunum/`. 1 ve 3'teki sayılar yalnızca kayıtlı CSV'lerden okunur.

| dosya | ne gösteriyor | kaynak |
| --- | --- | --- |
| `1_problem.png` | Ham ölçü 0,70 → kişiye özel açı bandı 0,95 (silkme/doğru AUC, kişiler nokta) | `deney1b/ozet.csv`, `kisi_auc.csv` (v2, YENI, tüm görüşler) |
| `2_fikir_aci_bandi.png` | "Kol θ°'deyken omzun normal yeri": Petra cam1 o0, doğru tekrar 3 bandın içinde, silkmeli tekrar 5 dışında (kaldırma fazı) | Bant çekirdekteki `aci_bandi_modeli` ile o grubun 4 doğru tekrarından (gösterilen doğru tekrar hariç) |
| `3_kalibrasyon.png` | Genel bant 0,67 ve 0,62, kişiye özel 0,95 | `deney1b/ozet.csv`, `kisi_auc.csv` (v2, YENI) |
| `4_geri_bildirim.png` | Uygulama ekranı, Honza tekrar 5 oynatımında: hasta cümlesi, "omuz" etiketi, kırmızı uzuv, omuz eğrisi | Uygulamanın kendi çizim kodu, pencere açmadan |
| `5_bindirme.png` | Aynı tekrarın 3 karesi (kaldırırken 86°, tepede 151°, indirirken 63°): turkuaz referans + kullanıcı | `uygulama/panel.Oynatici` |
| `demo_yedek_veriseti.mp4` | 25 s, Honza tekrar 5–7 ve oynatımları (git'e girmez) | Aynı kod |

- 4, 5 ve video, uygulamanın video döngüsünü (`uygulama/main.calistir`) pencere açmadan izleyen bir fonksiyonla üretildi. Kullanılan panel, oturum ve oynatım kodu aynı. Profil Karar 40'taki veri seti profili (kalibrasyon: 1, 2, 3, 9, 10). Bu, gerçek bir ekran kaydı değil, aynı görüntünün dosyaya yazılmasıdır.
- Tekrar 5'in hasta cümlesi sağlık kontrolü tablosundakiyle aynı çıktı: "Kolunu kaldırırken sağ omzunu kulağına doğru yaklaşık 5 derece kaldırdın. Omzunu aşağıda ve gevşek tut. Ayrıca kolunu kaldırırken kolun öne kaçtı. Kolunu tam yana, vücudunla aynı hizada kaldır."
- Renkler: mavi = kişiye özel / doğru, turuncu = silkme, gri = karşılaştırma. Şekiller 16:9, Türkçe, büyük yazılı.

### Karar 39
- 6b (siluet) ve 10 (REHAB24-6) başlatılmadı. Adım 7 ve 8 bitince yalnızca 6b için 3 videoda süre ölçülecek.

## Nasıl çalıştırılır
```bash
python -m deneyler.hepsi            # tam yeniden üretim, kullanıcı çalıştırır
python -m deneyler.hepsi --temizle  # bittikten sonra temiz kopyayı kaldırır
python -m deneyler.sunum_sekilleri  # sunum şekilleri, ~75 s
```
- **Süre tahmini:** Deney 1c tek başına ~15–20 dk, Deney 2 ~5–10 dk, ötekiler birer-birkaç dakika: toplam kabaca **45–60 dk**.
- **Nasıl okunur:** Sonunda terminalde `aynı: N` satırı çıkar. "Aynı olmayanlar" tablosu boşsa her şey yeniden üretildi demektir. Bir dosya "farklı" ya da "üretilmedi" ise `sonuclar/hepsi/ozet.md` hangi dosya olduğunu ve en büyük farkı gösterir; adımın günlüğü temiz kopyada `hepsi_gunluk/<adım>.log` dosyasındadır.
- Çalıştırmadan önce her şey commit'lenmiş olmalı; betik commit'lenmemiş değişiklik görürse uyarır.

## Sonuçlar
**`--hizli` denemesi** (Claude Code; `sonuclar/hepsi/hizli/ozet.md`'den kopyalandı; commit `0c013a5`): Deney 1 (16.8 s), kamera açısı (3.1 s), hız eşiği (2.1 s), hepsi çıkış kodu 0. **Karşılaştırılan dosya: 11 · aynı: 11.** Temiz kopya kaldırıldı; `veri/` yerinde.

Tam çalıştırma: kullanıcı yapacak. **Kullanıcının kararı (7 Kas):** her şey bittikten sonra, dondurmadan hemen önce yapılacak; şimdi erken, çünkü düzeltmeler gelebilir.

## Kabul ölçütü kontrolü
- [ ] `OZET.md` var ve sayılar ADIM dosyalarıyla tutarlı (dondurmada).
- [x] `deneyler/hepsi.py` var ve `--hizli` ile denendi (11/11 aynı).
- [ ] Tam yeniden üretim (kullanıcı).
- [x] Taslak `YENIDEN_KURULUM.md`, `LLM_KULLANIMI.md`, `SURUMLER.md`.
- [x] Sunum şekil adayları ve demo yedeği.
- [ ] `v-sunum` etiketi.

## Kararlar ve sapmalar
- **Veriye bağlantı (junction/symlink) yerine ortam değişkeni.** Temiz kopyada `veri/` bağlantısı kullanılsaydı, kopya silinirken bağlantının arkasındaki verinin silinme riski olurdu (CLAUDE.md: veri asla silinmez). `OMUZ_VERI` ile kod veriyi yerinde, yalnızca okuyarak kullanıyor.
- **"Temiz" = son commit.** Commit'lenmemiş değişiklikler kopyaya girmez; bu bilerek böyle.
- **Deney 3 iki kez çalışır** (Karar 37'deki sıra: önce tek kare, sonra `--olcu-surumu saglam`). İkinci çalıştırma ana tabloları aynı değerlerle yeniden yazar ve `_saglam` dosyalarını ekler.
- **Demo videosu** ekran kaydı değil, aynı çizimin dosyaya yazılması (bu ortamda pencere açılamıyor). Gerçek bir ekran kaydı istenirse kullanıcı Karar 40 komutuyla pencereyi açıp Windows'un ekran kaydıyla (Win + Alt + R) alabilir.

## Açık sorular / danışmana notlar
- Sunum şekillerinin seçimi (13–15 Kasım).

## Ek: Güncelleme 10 — depo denetimi, şekil düzeltmesi, 6b süre tahmini (7 Kas)

### Basit anlatım
- **Güvenlik denetimi:** Gemini API anahtarının (şifre gibi bir şey) yanlışlıkla git geçmişine girip girmediğine baktık. Girmemiş. Kişisel videolar, profiller ve veri seti de depoda yok.
- **README:** Depoyu ilk açan birinin okuyacağı kısa tanıtım: proje ne yapıyor, nasıl kurulur, klasörler, veri setinin atfı ve lisansı.
- **Şekil düzeltmesi:** Sunum şeklinde bir sayı yazısı bir noktayı örtüyordu; yazı çubuğun üstüne taşındı. İki şeklin altyazısına önden + çapraz görüşteki sayılar eklendi.
- **6b süre tahmini:** "Siluet" fikri için MediaPipe'ın kişinin şeklini piksel piksel çıkaran **segmentasyon maskesi** gerekiyor. Bunun ne kadar süreceğini 3 videoda ölçtük ve bütün veri için tahmin ettik. Henüz hiçbir ölçüt yazılmadı; başlayıp başlamamaya danışman karar verecek.

*Jargon:* **Segmentasyon maskesi:** görüntüdeki her pikselin "kişi mi, arka plan mı" olduğunu söyleyen bir siyah-beyaz resim. **Git geçmişi:** projenin bütün eski kayıtları; bir dosya bir kez commit'lenirse silinse bile geçmişte kalır.

### Karar 43 — depo ve gizli bilgi denetimi
Komutlar ve bulgular (7 Kas, commit `21ddf9c` üzerinde):

| denetim | komut | bulgu |
| --- | --- | --- |
| `.env` git'te mi | `git ls-files`, `git log --all --name-only` | **Hiç commit'lenmemiş.** `.gitignore`'da (`.env`). Dosya yalnızca yerelde var. |
| Anahtar geçmişte mi | `git log --all -p \| grep -nE "GEMINI_API_KEY *=\|AIza[0-9A-Za-z_-]{10,}"` (29 commit) | Tek eşleşme: ADIM_08'deki örnek satır `#    GEMINI_API_KEY=...` (değer yok). `AIza…` biçiminde dizi **yok**. Ayrıca `api_key/token/secret = <16+ karakter>` araması: eşleşme yok. |
| Veri | `git ls-files` | `veri/` altında yalnızca `veri/README.md` izleniyor (`.gitignore`: `veri/*`, `kendi_kayit` dahil). Geçmişte de başka `veri/` dosyası yok. |
| Profiller, oturumlar | `.gitignore` | `profiller/`, `oturumlar/` yok sayılıyor; geçmişte yok. |
| Videolar | `git ls-files`, `git check-ignore` | Hiçbir `.mp4` izlenmiyor; `sonuclar/**/*.mp4` kuralı `sonuclar/sunum/demo_yedek_veriseti.mp4`'ü kapsıyor. Geçmişte `.mp4` yok. |
| LLM önbelleği | `.gitignore` | `sonuclar/deney4/onbellek.jsonl` yok sayılıyor (yanıtlar `yanitlar.csv`'de). |
| Poz modeli | `.gitignore` | `*.task` yok sayılıyor. |

- **Sonuç:** Anahtarı iptal etmeye ya da geçmişi temizlemeye gerek yok.
- **Not (lisans, gizlilik değil):** Bazı izlenen PNG'ler veri setinin video karelerinden üretildi (ör. `sonuclar/adim0/kare102_ham.png`, `sonuclar/sunum/4_geri_bildirim.png`, `5_bindirme.png`). Veri seti CC BY-NC 4.0; atıfla ve ticari olmayan amaçla paylaşılabilir. README'ye bu not yazıldı.
- **`README.md`** yeniden yazıldı: bir paragraf, hızlı başlangıç (kurulum, `pytest`, demo komutları), klasör tablosu, `docs/YENIDEN_KURULUM.md` bağlantısı, REHAB26-ViewAngles atfı (DOI 10.5281/zenodo.23018128, CC BY-NC 4.0; veri depoda yok), kişisel kayıtların depoya girmediği notu. **Kod lisansı:** kullanıcıya soruldu, "lisans belirtilmedi" seçildi.

### Karar 44 — sunum şekilleri (yalnızca görsel)
- `3_kalibrasyon.png`: değer yazısı çubuğun içinden, çubuğun ve en yüksek kişi noktasının **üstüne** taşındı (koyu renk); y ekseninin üst sınırı 1,08 → 1,16. Ortadaki "0,62" artık 0,37'deki noktayı örtmüyor.
- `1_problem.png` ve `3_kalibrasyon.png` altyazısına `deney1b/ozet.csv`'den (v2, YENI, "AUC silkme/doğru (önden+çapraz)") okunan cümle eklendi: **"Önden + çapraz: ham 0,76 → bant 0,97."** (0,761 ve 0,968). 1_problem'in altyazısı sığmadığı için iki satıra bölündü.
- 1_problem'deki değer yazısı yeri değişmedi (örtüşme yok). Sayılar, 2, 4, 5 numaralı şekiller ve demo videosu değişmedi (2, 4, 5 PNG'leri yeniden üretimde birebir aynı çıktı).
- `python -m deneyler.sunum_sekilleri` yeniden çalıştırıldı (~58 s).

### Karar 45 — 6b süre tahmini (ölçüt ya da deney yok)
- `python -m araclar.siluet_sure --kare 3000` (Claude Code çalıştırdı, ~6 dk) → `sonuclar/siluet_sure/` (`videolar.csv`, `ozet.csv`, `bilgi.csv`). MediaPipe 1.2.2, `pose_landmarker_full`, VIDEO modu, tek kişi; aynı kareler önce maskesiz, sonra `output_segmentation_masks=True` ile işlendi. Maskeler diske yazılmadı; her 30. karede bellekte sıkıştırılıp boyutu ölçüldü.
- Videolar: Ex1 Honza cam1, Petra cam2, Vasil cam1 (1080×1920); her birinin **ilk 3000 karesi**. İlk deneme bütün kareleri işliyordu (3 video ~49 600 kare × 2 geçiş ≈ 45 dk); kare başına süre videolar arasında sabit çıktığı için durduruldu ve 3000 kareyle yeniden çalıştırıldı.

Sonuçlar (terminal çıktısından):

| | maskesiz | maskeli |
| --- | --- | --- |
| ölçülen kare | 9000 | 9000 |
| model, ms/kare (ağırlıklı ort.) | 13.63 | 21.01 |
| video çözme dahil, ms/kare | 19.97 | 28.04 |
| maske bulunan kare | – | 9000 / 9000 |
| maske boyutu, kB/kare: ham float32 / 8 bit sıkıştırılmış / ikili sıkıştırılmış | – | 8100 / 37.03–45.24 / 2.99–3.21 |

Tahmin: önden + çapraz Ex1 = **1363 tekrar, 162 931 kare** (her tekrar ±10 kare pay dahil), 15 video×kamera.

| | maskesiz | maskeli |
| --- | --- | --- |
| tahmini toplam, yalnızca model | 37.03 dk | 57.06 dk |
| tahmini toplam, video çözme dahil | 54.22 dk | **76.14 dk** |
| tahmini disk (maskeli) | – | ham float32 1 288 810 MB (~1,2 TB; saklanamaz) · 8 bit sıkıştırılmış 6535 MB · **ikili sıkıştırılmış 499 MB** |

- **Okuma:** Maske, kare başına modele ~7,4 ms ekliyor (13,6 → 21,0). Bütün önden + çapraz tekrarlar için segmentasyon **yaklaşık 1,3 saat** sürer (tek çalıştırma, önbelleğe alınır). Disk için tam maske saklanamaz; ikili (eşik 0,5) sıkıştırılmış maske ~0,5 GB, yalnızca omuz ROI'si saklanırsa çok daha az.
- **Sınırlar:** (1) Tahmin yalnızca tekrar karelerini sayar; tekrarlara gitmek için videoyu baştan çözmek gerekirse (OpenCV'de kare atlama yavaş/güvenilmez olabilir) aradaki kareler de çözülür; bu durumda ek süre kabaca 15 videonun toplam kare sayısı × ~6 ms (yalnızca çözme). (2) Ölçüm bu dizüstü bilgisayarın CPU'sunda (20 çekirdek), GPU yok; başka işler aynı anda çalışmadı. (3) Uygulamanın kullandığı MediaPipe 1.2.2 ile ölçüldü; veri setinin iskeletleri 0.10.20 ile çıkarılmıştı (Karar 27 notu); siluet ölçütü kendi iskeletiyle değil maskeyle çalışacağından bu fark süreyi etkilemez.
- Ölçüt yazılmadı. Başlayıp başlamamaya danışman Adım 7 sonuçlarıyla birlikte karar verecek (Güncelleme 11).

### Karar 42 — duyarlılık analizi (durum)
- Önceden kayıt ve kod commit `21ddf9c`; ayrıntı ADIM_08 "Ek: Güncelleme 10". Etiketleme dosyası **ondan sonra** üretildi: `sonuclar/deney4/elle_kaldirma.xlsx`, **342 cümle** (A 119, B 132, C 91). Kullanıcı etiketleyince: `python -m deneyler.deney4 kaldirma-degerlendir`.

### Karar 45 — Adım 10
- ⛔ Yapılmaz; `docs/GELECEK_CALISMA.md` madde 11 ("başka bir veri setinde, görülmemiş kişilerde doğrulama"); PLAN'da işaretlendi.

## Ek: Güncelleme 12 — dondurma belgeleri ve önbellekli yeniden üretim (9 Kas; Karar 51–56)

### Basit anlatım
- **Neden önbellek?** Üç adım baştan çalıştırılamayacak kadar pahalı ya da dışa bağımlı: 6b'nin segmentasyonu ~1,5 saat, Deney 4 internet ve Gemini anahtarı ister, Adım 7 kişisel videodan MediaPipe çalıştırır. Bunların **ara çıktıları** (önbellek) saklı. `hepsi` artık bu üç adımın tablolarını önbellekten yeniden üretiyor: "bu tablolar bu koddan ve bu ara çıktılardan çıkıyor" diyebiliyoruz. Önbellekte eksik bir şey varsa adım durur ve "üretilmedi" der; ağa istek atmaz.
- **`OZET.md`:** Bütün projenin özeti. Her deneyin bir tablosu, iddiaların ne kadar güçlü olduğu, sınırlılıklar ve işe yaramayan denemeler. Her sayının yanında hangi dosyadan geldiği yazıyor.
- **Sunum girdileri:** Sunumda kullanılabilecek sayıların listesi (hocanın üç problemine göre), kendi videomuzdan 45 saniyelik bir demo yedeği ve sunumda adım adım ne yapılacağını anlatan demo talimatı.

*Jargon:* **Önbellek:** daha önce hesaplanmış bir sonucun diskte saklanan kopyası; aynı hesap tekrar gerekince yeniden yapılmaz, oradan okunur.

### Yapılanlar
- **Karar 51–56** `KARARLAR.md`'ye; PLAN durumları (Adım 7 ✅, 6b ✅ olumsuz sonuç, 10 ⛔, Adım 9 🔄, hedef 11 Kas).
- **ADIM_07:** "Önceden belirlenenler"in altına "Düzeltme: 11" notu (bölümün kendisi değişmedi).
- **Karar 52:** `GELECEK_CALISMA.md` madde 12.
- **Karar 53 — `deneyler/hepsi.py`:**
  - Adımlar artık bir `Adim` yapısı: yer tutuculu komut (`{VERI}`, `{PROJE}`, `{HEDEF}`), adım başına karşılaştırılacak dosya listesi, yok sayılan sütun, insan girdisi dosyalar, kaynak açıklaması. `adimlar.csv`'ye `kaynak` sütunu, `ozet.md`'ye "Yeniden üretim: N/N aynı" satırı.
  - Yeni adımlar (eski 12 adımdan sonra): `siluet` (önbellek `veri/ara/siluet/`), `deney4_orneklem`, `deney4` (`deney4 onbellekten`: `orneklem.csv`'den girdiler, yanıtlar yalnızca `onbellek.jsonl`'den, sonra `raporla`), `deney4_kaldirma` (`kaldirma-degerlendir`; kullanıcının `elle_kaldirma.xlsx` dosyası ve anahtarı girdi olarak kopyalanır), `kendi_kayit` (`--yalniz-onbellek`).
  - Boş CSV (`siluet/nan_nedenleri.csv`) karşılaştırmayı çökertiyordu; düzeltildi (iki taraf da boşsa "aynı").
  - `LISTELENEN`'den `kendi_kayit` çıktı; `deney4` ve `siluet`'in yeniden üretilmeyen kısımları ile `siluet_sure` listeleniyor.
- **Yardımcı değişiklikler (sonuçları değiştirmez):**
  - `cekirdek/llm.py`: `YalnizOnbellekSaglayici` (ağa gitmez; önbellekte olmayan istekte hata verir).
  - `deneyler/deney4.py`: `onbellekten` işlemi ve `--onbellek` seçeneği.
  - `deneyler/kendi_kayit.py`: önbellek yolu `VERI_KOK`'a bağlandı (`OMUZ_VERI` yoksa yine `veri/ara/kendi_kayit`); `--yalniz-onbellek`.
  - `deneyler/siluet.py`: `--sinirlar` (kare başına sınırların yazılacağı yer; yeniden üretim `veri/` içine yazmasın diye).
- **Testler:** `test_hepsi.py` (+5: yeni adımların sırası ve bağımlılıkları, yer tutucular, dosya seçimi ve yok sayılan sütun, girdi kopyalama, boş CSV), `test_llm.py` (+1: yalnızca önbellek sağlayıcısı ağa gitmez ve dosyaya yazmaz).
- **Karar 54 — belgeler:** `sonuclar/OZET.md` (yeni), `docs/YENIDEN_KURULUM.md` (TASLAK kalktı; önbellekli adımlar ve baştan üretim tablosu; kendi videoyla kullanım), `docs/LLM_KULLANIMI.md` (rapor notu), `docs/SURUMLER.md` (TASLAK kalktı; `pip freeze` 7 Kas ile aynı; MediaPipe ve Gemini notu), `docs/ARKA_PLAN.md` (v1 notu + güncel v2 satırı; eski tablo duruyor), `README.md` (sonuçlar paragrafı), `docs/cekim_suflor.html` (kullanıcının `docs/Çekim Suflörü.html` dosyası, içeriği değişmeden ASCII adla).
- **Karar 56 — sunum girdileri:** `docs/SUNUM_GIRDILERI.md`, `docs/DEMO.md`; `python -m deneyler.sunum_sekilleri --kendi-kayit` → `sonuclar/sunum/4b_geri_bildirim.png`, `5b_bindirme.png`, `demo_kisi1.mp4` ve `profiller/kisi1.npz`.

### Değişen / eklenen dosyalar
| Dosya | Ne işe yarıyor |
| --- | --- |
| `deneyler/hepsi.py`, `testler/test_hepsi.py` | Önbellekli adımlar (Karar 53) |
| `cekirdek/llm.py`, `deneyler/deney4.py`, `testler/test_llm.py` | Ağsız Deney 4 yeniden üretimi |
| `deneyler/kendi_kayit.py`, `deneyler/siluet.py` | Önbellek seçenekleri |
| `deneyler/sunum_sekilleri.py` | `--kendi-kayit` (Karar 56); 5_bindirme çizimi ortak `bindirme_sekli` fonksiyonuna taşındı |
| `sonuclar/OZET.md`, `docs/*.md`, `README.md` | Dondurma belgeleri |
| `.gitignore` | `sonuclar/sunum/4b_*.png`, `5b_*.png` (kişisel görüntü) |

### Nasıl çalıştırılır
```bash
python -m deneyler.hepsi                           # tam yeniden üretim, kullanıcı (~1–1,5 sa)
python -m deneyler.sunum_sekilleri --kendi-kayit   # 4b, 5b, demo_kisi1.mp4 (~2 dk)
```

### Sonuçlar
**Önbellekli adımların tek tek denemesi** (Claude Code, commit öncesi; çıktı geçici klasöre, kayıtlı dosyalarla `csv_karsilastir`):
- `deney4 onbellekten` (21 s; ağ isteği 0, 300/300 yanıt önbellekte): `girdiler`, `yanitlar` (`onbellekten` sütunu yok sayılarak), `cumleler`, `ozet`, `sinif`, `kisi`, `bootstrap` → 7/7 aynı (en büyük fark 0.0). `kaldirma-degerlendir`: 4/4 aynı.
- `kendi_kayit --yalniz-onbellek` (3 s): `kisi1/tekrarlar`, `cumle_etiket`, `karisiklik`, `ozet` ve birlikte `ozet`, `karisiklik` → 6/6 aynı.
- `siluet --sinirlar <geçici>` (28,5 s): `ozet`, `kisi_auc`, `bootstrap`, `betimsel`, `tekrarlar` 5/5 aynı; `nan_nedenleri` boş dosya, karşılaştırıcı çöktü; düzeltildi, sonra aynı.

**`hepsi` üzerinden deneme (temiz worktree):** `python -m deneyler.hepsi --adimlar deney1_v2 deney2 deney3 deney3_saglam kamera_acisi hiz_esigi kural_disa_aktar siluet deney4_orneklem deney4 deney4_kaldirma kendi_kayit` (Claude Code; commit `20f15b7`; çıktı geçici klasörde). 12 adımın hepsi çıkış kodu 0; süreler deney1_v2 99.8 s, deney2 98.9 s, deney3 35.1 s, deney3_saglam 36.2 s, siluet 31.5 s, deney4 21.7 s, deney4_kaldirma 8.2 s, kendi_kayit 3.1 s; toplam 5.7 dk. **Karşılaştırılan dosya: 74 · aynı: 74** ("Yeniden üretim: 74/74 aynı"). Ağ isteği yok. Temiz kopya kaldırıldı. Bu bir deneme; tam çalıştırma (Deney 1, 1b, 1c, Ex7, tekrar ayırma dahil) kullanıcıda.

### Tam yeniden üretim (9 Kas 16:28–17:01; Claude Code çalıştırdı, kullanıcının isteğiyle)
`python -m deneyler.hepsi`, commit `ecc6762`. Kaynak: `sonuclar/hepsi/ozet.md`, `adimlar.csv`, `regresyon.csv`.
- 17 adımın hepsi çıkış kodu 0; toplam süre **32.1 dk** (deney1c 1100.4 s, ex7 207.7 s, deney2 150.6 s, deney1b 114.2 s, deney1_v2 112.0 s; diğerleri < 1 dk). Ağ isteği yok.
- **Karşılaştırılan dosya: 120 · aynı: 119 · farklı: 1** ("Yeniden üretim: 119/120 aynı").
- Farklı olan: `ex7/d2_esikler.csv`, "boyut/sütun: (20, 22) / (20, 21)".

**Fark ne? (tanı; hiçbir dosya düzeltilmedi)**
- Yeniden üretilen dosyada fazladan bir sütun var: `kaldırma sürümü`; 20 satırın hepsinde değeri `ilk`.
- Bu sütun çıkarılınca dosya kayıtlı dosyayla **aynı** (`csv_karsilastir`: "aynı", en büyük fark 0.0). Yani hiçbir eşik, ölçek ya da sayı değişmedi.
- Sebep: Ex7 eşik tablosunu `deneyler/deney2.py`'deki ortak fonksiyonla yazıyor. Bu sütun o fonksiyona Güncelleme 06'da (Karar 17, commit `5752559`) eklendi. Kayıtlı `ex7/d2_esikler.csv` ise ondan önce, Adım 4b'de (commit `890fd15`) üretildi ve sonra yeniden üretilmedi. Ex7'de "az kaldırma" sınıfı yok; sütun yalnızca bir etiket ve `ilk`, Karar 17'deki varsayılan.
- Kanıt dosyası: `sonuclar/hepsi/ex7_d2_esikler_yeniden.csv` (yeniden üretilen hali).

**Karar 55 madde 4 gereği:** durdum. `OZET.md`'ye yeniden üretim satırı yazılmadı, `v-sunum` etiketi atılmadı, push yapılmadı. Kayıtlı sonuç dosyası elle düzeltilmedi. Danışmana soru: kayıtlı `ex7/d2_esikler.csv` yeniden üretilen haliyle değiştirilsin mi (yalnızca sütun eklenir, sayılar aynı), yoksa karşılaştırmada bu sütun mu yok sayılsın? İkisinden sonra da `v-sunum` atılabilir.

**Kişi 1 demo (`--kendi-kayit`):** kalibrasyon 6 tekrar, profil `profiller/kisi1.npz`; `demo_kisi1.mp4` 1350 kare, **45.0 s**. Seçilen dört tekrarın hasta cümlesi Adım 7 sonuç dosyasıyla (`kendi_kayit/kisi1/tekrarlar.csv`) **4/4 aynı**:
- 4 (doğru): "Hareketi doğru yaptın. Kolun yaklaşık 140 dereceye çıktı, omzun ve dirseğin yerindeydi."
- 7 (omuz): "Kolunu kaldırırken sağ omzunu kulağına doğru yaklaşık 5 derece kaldırdın. Omzunu aşağıda ve gevşek tut."
- 11 (baş): "Kolun yukarıdayken başını yaklaşık 30 derece yana eğdin. Başını dik tut, karşıya bak. Ayrıca kolun yukarıdayken dirseğini yaklaşık 5 derece büktün. Kolunu düz tut."
- 6 (az kaldırma): "Kolunu 105 dereceye kadar kaldırdın; normalde 140 dereceye çıkıyorsun. Kolunu yaklaşık 35 derece daha yukarı kaldır. Ayrıca kolun yukarıdayken başını yaklaşık 5 derece yana eğdin. Başını dik tut, karşıya bak."

**pytest:** 209 geçti, 1 xfail (68,48 s).

### Kabul ölçütü kontrolü
- [x] `OZET.md` var; sayılar kaynak CSV'lerden kopyalandı ve her sayının yanında kaynak yazılı.
- [x] Karar 53 eklemeleri ve testleri; önbellekli adımlar kayıtlı sonuçlarla aynı.
- [x] `YENIDEN_KURULUM.md`, `LLM_KULLANIMI.md`, `SURUMLER.md` son hali; `ARKA_PLAN.md` notu; README.
- [x] Sunum girdileri (Karar 56).
- [x] Tam yeniden üretim: 119/120 aynı; tek fark (etiket sütunu) Karar 57 ile giderildi, Ex7 yeniden çalıştırıldı: 24/24 aynı.
- [x] `v-sunum` etiketi ve push (aşağıda).

### Kararlar ve sapmalar
- **Deney 4'te `orneklem.csv` de yeniden üretiliyor.** Karar 53 yalnızca `raporla` ve `kaldirma-degerlendir` diyor. `raporla` girdi olarak `girdiler.csv` ve `yanitlar.csv` okuyor; bunları kopyalamak yerine zinciri baştan kurdum: örneklem (tohum 0, Deney 3 çıktısından) → girdiler → önbellekten yanıtlar → tablolar. Böylece önbellek anahtarları da sınanıyor: girdiler bir karakter bile farklı olsa yanıt bulunamaz ve adım "üretilmedi" olur. LLM'e hiç istek gitmez.
- **`yanitlar.csv`'de `onbellekten` sütunu karşılaştırmada yok sayılıyor.** Asıl çalıştırmada yanıtlar ağdan geldi (`False`), yeniden üretimde önbellekten (`True`). Bu sütun yanıtın içeriğini değil, nereden geldiğini söylüyor. Metin, bitiş nedeni, deneme ve model sütunları birebir karşılaştırılıyor.
- **İnsan girdisi kopyalanıyor:** `elle_kaldirma.xlsx` ve `elle_kaldirma_anahtar.csv` kullanıcının etiketi; yeniden üretilemez, temiz kopyaya kopyalanır ve karşılaştırılmaz.
- **Kişisel görüntü:** `4b_`, `5b_` PNG'leri ve `demo_kisi1.mp4` kişi 1'in yüzünü gösteriyor; depo GitHub'a gönderileceği için PNG'ler de `.gitignore`'a eklendi. Karar 56 yalnızca video için "git'e girmez" diyordu. Raporda ya da depoda kullanılacaksa kullanıcının kararı.
- **Demo süresi:** İlk üretim 36,6 s çıktı (Karar 56: ~45–60 s). Tekrar öncesi pay 1 → 2 s, oynatım sonrası 0,7 → 1,5 s, başlık 1,2 → 1,5 s yapıldı; 45,0 s. İçerik ve cümleler değişmedi. 5b'nin alt yazısı sığmadığı için kısaltıldı.
- **Suflör sayfası** `docs/Çekim Suflörü.html` → `docs/cekim_suflor.html` (Karar 54'teki ad; içerik aynı). Sayfa yalnızca Google Fonts'tan yazı tipi çekiyor.
- **5_bindirme çizimi** ortak bir fonksiyona taşındı (kod yolu aynı). Veri seti şekilleri yeniden üretilmedi (Karar 56: veri seti sürümleri kalır).

### Demo denemesi ve pencere düzeltmesi (9 Kas; etiketten önce)
- **Kullanıcı kontrolü:** `python -m uygulama.main --profil profiller/kisi1.npz --video veri/kendi_kayit/kisi1/test.MOV` Claude Code tarafından açıldı, kullanıcı izledi: cümleler, akış ve tuşlar sorunsuz.
- **Bulunan kozmetik sorun:** Pencere tam ekran yapılınca görüntü en-boy oranını korumadan yayılıyor, video ve yazılar bozuk görünüyordu. Sebep: Windows'taki OpenCV (Win32 arka ucu) görüntüyü pencereye esnetiyor; `WINDOW_KEEPRATIO` bu arka uçta çalışmıyor.
- **Düzeltme (yalnızca gösterim):** `uygulama/main.py`: `goster()` her kareyi pencerenin o anki boyutuna oranı koruyarak ölçekliyor, kenarları koyu dolduruyor (`sigdir`); fare tıklamaları `goruntu_koordinati` ile görüntü koordinatına geri çevriliyor. Ölçüm, karar ve cümle kodu değişmedi. Testler: `testler/test_pencere.py` (+2); uygulama = Deney 3 testi geçti; tam `pytest` 211 geçti, 1 xfail. Kullanıcı tam ekranda kontrol etti: sorun yok.

### Karar 57 — Ex7 eşik tablosu ve dondurma (9 Kas)
- Danışman kararı: kayıtlı `sonuclar/ex7/d2_esikler.csv` yeniden üretilen haliyle (`sonuclar/hepsi/ex7_d2_esikler_yeniden.csv`) değiştirildi; sütun karşılaştırmada yok sayılmadı. Ayrı commit: `b4a3fb5`.
- Doğrulama: `python -m deneyler.hepsi --adimlar ex7` (commit `b4a3fb5`, 2.4 dk): **Karşılaştırılan dosya: 24 · aynı: 24** ("Yeniden üretim: 24/24 aynı").
- **Sapma (küçük):** `--adimlar` çalıştırması özetini `sonuclar/hepsi/` altına yazıp tam çalıştırmanın özetinin üzerine yazdı. Tam çalıştırmanın dosyaları git'ten geri alındı; Ex7 doğrulaması `sonuclar/hepsi/ex7_dogrulama/` altına taşındı. Kod değiştirilmedi (dondurma).
- `OZET.md`'ye yeniden üretim satırı yazıldı (Karar 57'deki cümle).

