# uygulama/

Kamerayla ya da video dosyasıyla çalışan uygulama. Kişi önce 6 doğru tekrar yapar (**kalibrasyon**); sistem bu tekrarlardan kişinin normal hareketini öğrenir. Sonraki her tekrar bu normale göre değerlendirilir: ekranda doğru/hata kararı, Türkçe düzeltme cümlesi ve tekrarın referansla üst üste bindirilmiş oynatımı görünür.

Bu klasör yalnızca **arayüz ve akıştır**. Ölçüler, bant, hata türü, cümle ve bindirme hesabı `cekirdek/` içindedir; uygulama onları içe aktarır. Böylece uygulamanın kararı, deneylerde ölçülen kararla aynı koddan gelir.

## Çalıştırma

Proje kökünden:

```bash
# Canlı kamera: önce kalibrasyon, sonra değerlendirme; profil profiller/adin.npz olarak kaydedilir
python -m uygulama.main --isim adin

# Kayıtlı profille doğrudan değerlendirme (kalibrasyon atlanır)
python -m uygulama.main --profil profiller/adin.npz

# Video dosyalarıyla: kalibrasyon videosu + değerlendirilecek video
python -m uygulama.main --isim adin --kalibrasyon-video kalibrasyon.mp4 --video test.mp4

# Veri setinden bir video (veri/rehab26/ gerekir); profil aynı videonun etiketi doğru tekrarlarından kurulur
python -m uygulama.main --veri-seti ex1_Honza --kamera cam1 --yonelim 0

# Pencere açmadan aynı değerlendirme; sonuç CSV ve terminalde tablo
python -m uygulama.toplu --profil profiller/adin.npz --video test.mp4
```

Bütün seçenekler: `python -m uygulama.main --help`. Sık kullanılanlar:

| Seçenek | Ne yapar |
| --- | --- |
| `--kamera 1` | Başka bir kamera kullan (varsayılan 0) |
| `--cozunurluk 1920x1080` | Canlı kamera çözünürlüğü (varsayılan 1280x720) |
| `--hazirlik 5` | Başlangıçta yerine geçme süresi, saniye (varsayılan 10) |
| `--onay-suresi 8` | Kalibrasyonda biten tekrar bu kadar saniye içinde reddedilmezse kendiliğinden kabul edilir |
| `--elle-onay` | Kendiliğinden kabul yok; her tekrar için Kabul/Reddet beklenir |
| `--aynasiz` | Canlı görüntüyü ayna gibi çevirme (yalnızca görüntü; ölçümü etkilemez) |

## Akış

1. **Hazırlık** (yalnızca canlı kamerada, 10 sn): kişi yerine geçer. Ekran omuzların ve kalçaların kadrajda olup olmadığını söyler. Hiçbir şey kaydedilmez; bu sürede yalnızca bilgisayarın saniyede kaç kare işlediği ölçülür. Boşluk tuşuyla atlanır.
2. **Kalibrasyon:** kişi kolunu yandan rahatça çıkabildiği en yükseğe kaldırıp indirir. Biten her tekrar onay bekler: kişi kabul ya da ret eder, ya da tekrar 8 sn sonra kendiliğinden kabul edilir. Omuzları veya kalçaları kadrajda olmayan tekrar hiç alınmaz. 6 tekrar kabul edilince (en az 5 ile elle bitirilebilir) bu tekrarlardan kişiye özel **profil** kurulur.
3. **Değerlendirme:** her yeni tekrar profile göre değerlendirilir. Panelde karar (DOĞRU ya da hata türü), hasta cümlesi, istenirse uzman ayrıntısı ve omuz ölçüsünün normal aralıkla grafiği görünür.
4. **Oynatım:** değerlendirilen her tekrarın ardından kişinin iskeleti, referans tekrarla (kalibrasyondaki tipik tekrar, turkuaz) zamanda ve geometride hizalanmış olarak oynatılır. Normal aralığın dışına çıkan uzuv kırmızı çizilir.

## Klavye ve fare

Panelin altındaki düğmelere fareyle tıklanabilir; kısayol düğmede parantez içinde yazar. Klavye için pencerenin seçili olması gerekir (bir kez tıklamak yeter).

| Tuş | Eylem |
| --- | --- |
| E / H | Bekleyen kalibrasyon tekrarını kabul et / reddet |
| Z | Son kabulü geri al |
| K | Kalibrasyonu bitir (en az 5 tekrarla) |
| B | Kalibrasyona baştan başla |
| R | Son tekrarı yeniden oynat |
| U | Uzman ayrıntısını aç/kapat |
| Boşluk | Duraklat (yalnızca video dosyasında); hazırlıkta bekleme süresini atlar |
| Q / Esc | Çıkış |

## Dosyalar

| Dosya | Görevi |
| --- | --- |
| `main.py` | Pencereli uygulama. Görüntü kaynağını açar (kamera ya da video), hazırlık ekranını gösterir, her kareyi MediaPipe'a ve oturuma verir, paneli çizdirir, klavye ve fare olaylarını işler. Ana döngü `calistir()` fonksiyonudur. |
| `oturum.py` | Pencereden bağımsız akış (`Oturum` sınıfı). `kare_ekle()` her karenin kol açısını tekrar ayırıcıya verir ve biten tekrarı döndürür. Kalibrasyonda tekrar onay bekler; `kalibrasyonu_bitir()` profili kurar. Değerlendirmede karar `cekirdek/degerlendirici.py` içindeki `degerlendir()` fonksiyonundan gelir. Profili (`profil_kaydet` / `profil_yukle`) ve oturum CSV'sini (`oturum_kaydet`) de yazar. |
| `panel.py` | Ekrandaki her çizim: canlı iskelet, bindirmeli oynatım (`Oynatici`), sağdaki geri bildirim paneli (`panel()`), düğmeler, kol açısı çubuğu ve omuz grafiği. Türkçe karakterler için metin PIL ile yazılır. |
| `poz.py` | MediaPipe PoseLandmarker'ı saran küçük sınıf (`PozCikarici`). Bir kare alır, 33 eklem noktası döndürür (x, y, z, görünürlük); biçim veri setindekiyle aynıdır. Model dosyası yoksa ilk çalıştırmada `modeller/` altına indirir. |
| `toplu.py` | Pencere açmadan aynı değerlendirme (video → CSV). Kendi kayıt deneyi ve sunum şekilleri bunu kullanır. `--veri-seti` ile **sağlık kontrolü** yapar: veri setinden bir videoda MediaPipe'ı yeniden çalıştırır, sonucu veri setindeki iskeletle ve etiketlerle karşılaştırır (`sonuclar/uygulama_saglik/`). |

## Kullandığı dosyalar ve çıktılar

- **Okur:** `modeller/kural_ex1.json` (hata türü kuralı ve eşikler), `modeller/kamera_esigi.json` ve `modeller/hiz_esigi.json` (bilgi notları için eşikler), `modeller/pose_landmarker_full.task` (MediaPipe modeli; yoksa indirilir).
- **Yazar:** `profiller/<isim>.npz` (kalibrasyon tekrarları) ve `oturumlar/<tarih>.csv` (her tekrarın kararı, cümlesi ve ölçüleri). Bu iki klasör kişisel kayıt olduğu için depoya girmez; uygulama ilk çalıştırmada oluşturur.
