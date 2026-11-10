# araclar/

Deney sayılmayan, ama sistemin bir parçasını üreten ya da gözle kontrol etmeye yarayan iki betik.

| Betik | Ne yapar | Çıktı |
| --- | --- | --- |
| `kural_disa_aktar.py` | **Uygulamanın karar kuralı dosyasını üretir.** Deneyde kural her seferinde 4 kişiyle kurulup 5. kişide sınanır. Uygulamada test kişisi olmadığından kural beş kişinin hepsiyle, aynı prosedürle kurulur: ölçekleme, yönler, öne kaçma ölçüsünün seçimi, eşik T ve şiddet eşikleri. Bulunan değerler deneydeki beş kuralla yan yana yazılır; böylece uygulamanın kuralının deneydekilerden farklı olmadığı görülür. | `modeller/kural_ex1.json`, `sonuclar/kural_disa_aktar/loso_karsilastirma.csv` |
| `gorsel_kontrol.py` | **Bir tekrarı videoda izleyip sistemin ne gördüğünü kontrol eder.** Solda video, MediaPipe iskeleti ve hizalanmış referans iskelet; sağda kol açısına göre ölçü ve kişiye özel açı bandı görünür. Banttan çıkan uzuv kırmızı çizilir. Deney 1'in galerisini de üretir. | `sonuclar/gorsel_kontrol/<tekrar>.mp4`, `sonuclar/deney1/galeri/` |

```bash
python -m araclar.kural_disa_aktar            # birkaç saniye; önce deney2 ve deney3 çalışmış olmalı
python -m araclar.gorsel_kontrol --video ex1_Honza --kamera cam1 --yonelim 0 --tekrar 5   # tek tekrar (~20 sn)
python -m araclar.gorsel_kontrol --galeri      # Deney 1 galerisi (videos.zip gerekir)
```

İkisi de `veri/rehab26/` gerektirir. Video gösteren kısım için ayrıca `videos.zip` gerekir.

**Not:** `gorsel_kontrol.py` ekranında "basit eşik kararı" yazar: E, diğer 4 kişinin doğru tekrarlarının %90'lık diliminden büyükse "şüpheli" denir. Bu yalnızca bu aracın ve Deney 1 galerisinin gruplaması içindir. Sistemin asıl kararı `cekirdek/hata_turu.py`'den gelir (Deney 2).
