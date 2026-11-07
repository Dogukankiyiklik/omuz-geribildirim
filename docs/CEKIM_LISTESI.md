# Çekim kontrol listesi (Adım 7, Karar 33)

Yazdır, çekim sırasında yanında dursun. Her kişi için iki video çekilir: `kalibrasyon.mp4` ve `test.mp4`.

## Kurulum (bir kez)
- [ ] Telefonu tripoda ya da sabit bir yüzeye koy. Göğüs hizasında, **2–2,5 m** uzakta olsun.
- [ ] Kameraya **önden** dur (en fazla 30° çapraz).
- [ ] Kadraj: baştan kalçaya bütün gövde ve **yukarı kalkan sağ kol** görünsün. Kolu tam kaldırıp elin kadraja girdiğini dene.
- [ ] Arka plan sade olsun, ışık önden gelsin (arkada pencere olmasın).
- [ ] Kameranın **yanında sabit bir nokta** seç (ör. bir etiket). Bütün çekim boyunca oraya bak; yalnızca "bakış" tekrarlarında bakma.
- [ ] İki video arasında telefonu **oynatma**. Çözünürlük ve yön (dikey/yatay) iki videoda aynı kalsın.
- [ ] Telefon 30 FPS'de çeksin (çoğu telefonda varsayılan).

## Her tekrarda
1. Kol aşağıda, dinlenmede başla.
2. Kolu yandan kaldır, sonra indir.
3. Kol aşağıda **1–2 saniye bekle**, sonra sıradaki tekrara geç. (Sistem tekrarın bittiğini kol aşağı inince anlar.)
- Kolu her zaman en az omuz hizasına yakın kaldır (az kaldırmada bile ~90°). 60°'nin altındaki hareket tekrar sayılmaz.
- Kaydı tekrarlar arasında **durdurma**. Videonun başında ve sonunda 3 saniye kıpırdamadan dur.

## Video 1: `kalibrasyon.mp4`
- [ ] **6 doğru tekrar.** Doğal ve rahat yap, kendini zorlama, "dümdüz" kasılma. Her tekrarda aynı noktaya bak.

## Video 2: `test.mp4`
21 tekrar, **aşağıdaki sırayla**. Her tekrardan sonra kutuyu işaretle. Bir tekrar yanlış olursa (sırayı karıştırdıysan, istemeden başka bir hata yaptıysan) **not sütununa yaz**; çekimi baştan almak gerekebilir.

Tekrar türleri:
- **doğru:** normal, doğru tekrar.
- **omuz:** kolu kaldırırken omzunu kulağına doğru kaldır (silk).
- **baş:** kolu kaldırırken başını yana eğ.
- **dirsek:** dirseğini bükerek kaldır.
- **az kaldırma:** kolu yalnızca omuz hizasına (~90°) kaldır.
- **öne kaçma:** kolu yandan değil, öne doğru (çapraz) kaldır.
- **doğru + bakış:** doğru yap, ama yere ya da yana bak.
- **doğru + hızlı:** doğru yap, ama yaklaşık **1 saniyede** kaldır-indir.

### Kişi 1 (tohum 0) → `veri/kendi_kayit/kisi1/`
| # | yapılacak | ✓ | not |
| --- | --- | --- | --- |
| 1 | dirsek | ☐ | |
| 2 | doğru + bakış | ☐ | |
| 3 | doğru + bakış | ☐ | |
| 4 | doğru | ☐ | |
| 5 | doğru | ☐ | |
| 6 | az kaldırma | ☐ | |
| 7 | omuz | ☐ | |
| 8 | doğru + hızlı | ☐ | |
| 9 | doğru | ☐ | |
| 10 | dirsek | ☐ | |
| 11 | baş | ☐ | |
| 12 | doğru | ☐ | |
| 13 | doğru + bakış | ☐ | |
| 14 | az kaldırma | ☐ | |
| 15 | omuz | ☐ | |
| 16 | doğru + hızlı | ☐ | |
| 17 | omuz | ☐ | |
| 18 | öne kaçma | ☐ | |
| 19 | baş | ☐ | |
| 20 | doğru | ☐ | |
| 21 | öne kaçma | ☐ | |

### Kişi 2 (tohum 1, isteğe bağlı) → `veri/kendi_kayit/kisi2/`
| # | yapılacak | ✓ | not |
| --- | --- | --- | --- |
| 1 | doğru | ☐ | |
| 2 | dirsek | ☐ | |
| 3 | doğru + hızlı | ☐ | |
| 4 | öne kaçma | ☐ | |
| 5 | omuz | ☐ | |
| 6 | az kaldırma | ☐ | |
| 7 | doğru + bakış | ☐ | |
| 8 | doğru + bakış | ☐ | |
| 9 | doğru + bakış | ☐ | |
| 10 | doğru | ☐ | |
| 11 | dirsek | ☐ | |
| 12 | doğru | ☐ | |
| 13 | doğru | ☐ | |
| 14 | omuz | ☐ | |
| 15 | baş | ☐ | |
| 16 | doğru | ☐ | |
| 17 | baş | ☐ | |
| 18 | öne kaçma | ☐ | |
| 19 | az kaldırma | ☐ | |
| 20 | omuz | ☐ | |
| 21 | doğru + hızlı | ☐ | |

## Çekimden sonra
- [ ] Videoları bilgisayara aktar: `veri/kendi_kayit/kisi1/kalibrasyon.mp4` ve `veri/kendi_kayit/kisi1/test.mp4`.
- [ ] `veri/kendi_kayit/kisi1/etiketler.csv` hazır (bu sırayla). Çekimde sıradan saptıysan dosyayı **gerçekte yaptığına** göre düzelt.
- [ ] Çalıştır:
  `python -m deneyler.kendi_kayit --kisi kisi1 --kalibrasyon veri/kendi_kayit/kisi1/kalibrasyon.mp4 --test veri/kendi_kayit/kisi1/test.mp4 --etiketler veri/kendi_kayit/kisi1/etiketler.csv`
- [ ] Betik "tekrar sayısı tutmuyor" derse: yazdığı zamanlara videoda bak, `ayrilan,tekrar_no` sütunlu bir eşleşme dosyası yaz ve `--eslesme` ile tekrar çalıştır.
