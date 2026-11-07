# ADIM 09 — Sonuçları dondurma

**Tarih:** 2026-11-07 (hazırlık; Güncelleme 09, Karar 37–39)
**Durum:** Kısmen: yalnızca hazırlık. Dondurma 13 Kasım akşamı yapılacak. Bekleyenler: Adım 7 ve 8'in sonuçları, `deneyler/hepsi.py`'nin tam çalıştırması (kullanıcı), `sonuclar/OZET.md`, `v-sunum` etiketi.

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
