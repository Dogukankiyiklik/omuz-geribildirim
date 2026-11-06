# ADIM 02 — Deney 1'in kullanıcı tarafından çalıştırılması + şekiller

**Tarih:** 2026-11-06
**Durum:** Tamamlandı

## Basit anlatım (kullanıcı için, 3–6 cümle)
Deney 1'i kendi bilgisayarında çalıştırdın; çıkan tablo beklenen tabloyla (danışmanın sonuçları) en fazla 0,0042 farkla aynı. Deney şu soruyu soruyor: "Omuz silkmesini, doğru yapılan tekrarlardan hangi ölçüt en iyi ayırır, ve kişiye özel bant işe yarar mı?" Cevap: Bant kullanmadan ölçütler zayıf (AUC 0,60–0,70; 0,5 yazı-tura demek). Kişinin kendi doğru tekrarlarından çıkan bantla ölçünce hepsi belirgin şekilde iyileşiyor (0,82–0,91). En iyisi bizim önerdiğimiz kulak–omuz mesafesi (YENI, 0,909). Ama YENI'nin ikinci sıradaki ölçütlerden (M33, M39_F2) farkı küçük ve güven aralığı sıfırı içeriyor; yani 5 kişilik veriyle "YENI kesin daha iyi" diyemeyiz, ancak "en az onlar kadar iyi" diyebiliriz.

*Jargon:* **AUC:** Rastgele bir silkmeli ve rastgele bir doğru tekrar seçtiğimizde, ölçütün silkmeliye daha yüksek hata puanı verme olasılığı. **Güven aralığı (GA):** "Başka 5 kişi olsaydı sonuç büyük olasılıkla bu aralıkta olurdu." Kişileri yeniden örnekleyerek (bootstrap) hesaplandı.

## Yapılanlar
- Kullanıcı `python -m deneyler.deney1` komutunu çalıştırdı → `sonuclar/deney1/` oluştu.
- Regresyon testi kullanıcının dosyasıyla çalıştırıldı ve geçti.
- `deneyler/sekiller.py` yazıldı; iki şekil üretildi.

## Değişen / eklenen dosyalar
| Dosya | Ne işe yarıyor |
| --- | --- |
| `deneyler/sekiller.py` | `auc.png` ve `bant_ornegi.png` şekillerini üretir |
| `sonuclar/deney1/auc.png` | Ölçüt başına AUC, bantsız ve bantlı yan yana, bantlı için %95 GA |
| `sonuclar/deney1/bant_ornegi.png` | ex1_Honza, cam1, yönelim 0: YENI bandı, bir doğru ve bir silkmeli tekrar |
| `sonuclar/deney1/dagilim.png` | (Ek, kullanıcının isteğiyle sonradan) YENI puanlarının dağılımı: doğru / silkme / diğer hatalar, bantsız ve bantlı |
| `sonuclar/deney1/{tekrarlar,ozet,bootstrap,hata_turu_ortalama}.csv` | Kullanıcının çalıştırmasıyla üretildi |

## Nasıl çalıştırılır
```bash
python -m deneyler.deney1      # ~15 s
python -m deneyler.sekiller    # ~10 s
```

## Sonuçlar
`sonuclar/deney1/ozet.csv` (kullanıcının çalıştırması; 3 basamağa yuvarlanmış gösterim):

| yöntem | ölçüt | AUC silkme/doğru | AUC silkme/diğer hatalar | AUC önden (0–20°) | AUC çapraz (30–60°) | AUC profil (70–90°) | Ψ (M39) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ham | M01 | 0.650 | 0.683 | 0.751 | 0.673 | 0.544 | |
| ham | M01_tek | 0.658 | 0.712 | 0.763 | 0.690 | 0.579 | |
| ham | M39_F2 | 0.600 | 0.644 | 0.684 | 0.599 | 0.559 | |
| ham | M33 | 0.638 | 0.695 | 0.746 | 0.664 | 0.593 | |
| ham | YENI | 0.704 | 0.699 | 0.767 | 0.759 | 0.554 | |
| bant | M01 | 0.822 | 0.642 | 0.885 | 0.830 | 0.670 | 0.221 |
| bant | M01_tek | 0.866 | 0.662 | 0.898 | 0.889 | 0.743 | 0.275 |
| bant | M39_F2 | 0.888 | 0.637 | 0.888 | 0.924 | 0.794 | 0.281 |
| bant | M33 | 0.904 | 0.646 | 0.918 | 0.914 | 0.849 | 0.300 |
| bant | YENI | 0.909 | 0.705 | 0.942 | 0.933 | 0.779 | 0.330 |

`sonuclar/deney1/bootstrap.csv` (bant, AUC silkme/doğru, kişi bazlı bootstrap, 2000 tekrar):

| ölçüt | ortalama | GA %2,5 | GA %97,5 |
| --- | --- | --- | --- |
| M01 | 0.8225 | 0.7761 | 0.8843 |
| M01_tek | 0.8656 | 0.8152 | 0.9188 |
| M39_F2 | 0.8877 | 0.8114 | 0.9553 |
| M33 | 0.9028 | 0.8231 | 0.9677 |
| YENI | 0.9087 | 0.8491 | 0.9606 |
| YENI − M39_F2 | 0.0210 | -0.0171 | 0.0602 |

Bant örneği (terminal çıktısı): `doğru = satır 0 (tekrar 1), E = 0.054; silkme = satır 4 (tekrar 5), E = 0.657; bant 4 doğru tekrardan, referans indeksi 3`.

Regresyon testi (kullanıcının `ozet.csv` dosyası): `En büyük mutlak fark: 0.00424837 (('bant', 'M39_F2', 'AUC profil (70–90°)'))` → `1 passed`.

### Şekiller nasıl okunur
**`auc.png`:** Her ölçüt için iki çubuk var: gri = bantsız, mavi = kişiye özel bant. Çubuk ne kadar yüksekse ölçüt silkmeli tekrarı doğru tekrardan o kadar iyi ayırıyor; eksen 0,5'ten (yazı-tura) başlıyor. Her ölçütte mavi çubuk griden belirgin şekilde yüksek: **bant her ölçütü iyileştiriyor.** Mavi çubukların üstündeki siyah çizgiler güven aralığı; birbirine çok binmeleri, bantlı ölçütler arasındaki farkların (ör. YENI 0,91 ile M33 0,90) 5 kişiyle kesin olmadığını gösteriyor.

**`bant_ornegi.png`:** Üstteki eğri kolun açısı: 0'dan ~150°'ye çıkıp iniyor. Alttaki gri alan Honza'nın "normal" kulak–omuz mesafesi; kolu kaldırırken doğal olarak azalıyor, çünkü kol kalkınca omuz da biraz kalkar. Bu yüzden sabit bir eşik işe yaramaz, bant ise kol açısına göre değişiyor. Mavi (doğru tekrar) bandın içinde kalıyor (E = 0,05). Turuncu (silkmeli tekrar) kol daha yeni kalkarken banttan aşağı kopuyor ve tepe noktasında belirgin şekilde altında kalıyor (E = 0,66), yani omuz kulağa normalden çok yaklaşıyor. Noktalar bandın dışına çıkılan anları gösteriyor.

**`dagilim.png` (ek):** Bantsız puanda mavi (doğru) ve turuncu (silkme) tepeler iç içe; bantlı puanda doğrular 0'a yığılıyor, silkmeler sağa yayılıyor. Kesikli çizgi doğruların %90'ının altında kaldığı değer; bu çizginin sağında silkmelerin bantsızda %41'i (eşik 0.184), bantlıda %75'i (eşik 0.278) kalıyor. Aynı çizgiyi diğer hataların bantsızda %13'ü, bantlıda %42'si geçiyor; yani bant "bir şey ters" sinyalini diğer hatalarda da veriyor. Bu eşik test verisinden seçildiği için **yalnızca açıklama amaçlı**; bir değerlendirme sonucu değil.

## Kabul ölçütü kontrolü
- [x] Kullanıcı aynı sayıları kendi bilgisayarında gördü: kullanıcının `ozet.csv` dosyası Adım 1'deki zip çalıştırmasıyla aynı en büyük farkı (0.00424837) veriyor; regresyon testi geçti.
- [x] İki şekil oluştu: `sonuclar/deney1/auc.png`, `sonuclar/deney1/bant_ornegi.png` (ayrıca ek: `dagilim.png`).

## Kararlar ve sapmalar
- **Bant örneğinde adil model:** Gösterilen doğru tekrar banda dahil edilmedi (birini-dışarıda-bırak). Bant kalan 4 doğru tekrardan kuruldu ve silkmeli tekrar da aynı modelle ölçüldü. Seçim: gruptaki ilk doğru tekrar (tekrar 1) ve ilk silkmeli tekrar (tekrar 5); tohum 0. Bu yüzden E değerleri `tekrarlar.csv`'dekilerden biraz farklı olabilir; orada her tekrarın modeli ayrı rastgele çekimle kuruluyor.
- **Şekle eklenenler:** PLAN'daki AUC çubuk grafiğine bantlı çubuklar için bootstrap güven aralığı eklendi. Bant örneğine üstte referans tekrarın kol açısı paneli eklendi; hizalamanın neye göre yapıldığını görmek için.
- **Renkler:** Erişilebilir referans paletinden mavi ve turuncu; bantsız çubuklar nötr gri.
- **Excel'de okunabilirlik (kullanıcı geri bildirimi):** Kullanıcı `tekrarlar.csv`'yi Excel'de açınca `ham_M39_F2` sütununda `####` ve `gorus_grubu`'nda bozuk karakterler gördü. Dosya bozuk değildi (değişmemiş, `#` içermiyor, regresyon testi geçiyor). Sebep: Excel UTF-8'i BOM olmadan tanımıyor, Türkçe Excel de ondalık noktayı binlik ayırıcı sanıyor (13.33… → çok büyük sayı → `####`). Çözüm: CSV'ler artık UTF-8 BOM ile yazılıyor ve ayrıca `sonuclar/deney1/sonuclar.xlsx` (her tablo ayrı sayfa) üretiliyor (`cekirdek/konsol.py: sonuclari_yaz`; `openpyxl` requirements'a eklendi). Kullanıcının mevcut dosyaları yeniden hesaplanmadan bu biçimde yeniden kaydedildi; içerik `assert_frame_equal` ile birebir aynı. Excel'de bakmak için `.xlsx` kullanılmalı.

## Açık sorular / danışmana notlar
- **AUC silkme/diğer hatalar düşük (0,64–0,71) ve bant onu iyileştirmiyor** (ham YENI 0.699 → bant YENI 0.705; diğer ölçütlerde düşüyor). `hata_turu_ortalama.csv`'ye göre diğer hatalar da omuz ölçütlerinde bant dışına çıkıyor (ör. bant_YENI: silkme 0.436, baş eğme 0.320, yetersiz kaldırma 0.322, öne kaçma 0.266, dirsek 0.243, doğru 0.106). Bant "bir şeyler normal değil" sinyalini iyi veriyor, ama hatanın **türünü** tek omuz ölçütüyle ayırmak zor. Bu, Adım 4'ün (hata türü başına ayrı ölçüt) neden gerekli olduğunu destekliyor.
- **Profil görünümde (70–90°) bütün ölçütler zayıflıyor** (bant YENI 0.779). Bu bir sınırlılık olarak raporlanabilir. Önden ve çapraz görüş 0,93–0,94.
- Adım 1'deki "tek tekrarın E'si tohuma duyarlı" notu hâlâ açık (bkz. ADIM_01, KARARLAR.md).
