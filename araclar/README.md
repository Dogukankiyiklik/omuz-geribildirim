# araclar/

Deney sayılmayan, ama sistemin bir parçasını ya da sunumun bir şeklini üreten betikler.

| Betik | Ne yapar | Çıktı |
| --- | --- | --- |
| `kural_disa_aktar.py` | **Uygulamanın karar kuralı dosyasını üretir.** Deneyde kural her seferinde 4 kişiyle kurulup 5. kişide sınanır. Uygulamada test kişisi olmadığından kural beş kişinin hepsiyle, aynı prosedürle kurulur: ölçekleme, yönler, öne kaçma ölçüsünün seçimi, eşik T ve şiddet eşikleri. Bulunan değerler deneydeki beş kuralla yan yana yazılır; böylece uygulamanın kuralının deneydekilerden farklı olmadığı görülür. | `modeller/kural_ex1.json`, `sonuclar/kural_disa_aktar/loso_karsilastirma.csv` |
| `sunum_sekilleri.py` | **Sunumdaki açı bandı şeklini çizer.** Veri setindeki bir çekimin doğru tekrarlarını ve omuz silkmeli bir tekrarını çekirdek kodla çizer: solda zamana göre (doğru tekrarda da omuz kulağa yaklaşıyor), sağda kol açısına göre ve bantla. Sayı üretmez, yeni bir deney değildir. | `sonuclar/sunum/1_aci_bandi.png` |
| `hata_olcu_haritasi.py` | **Sunumdaki ısı haritasını çizer:** her gerçek hata türünde beş ölçünün sapma puanının (z) ortancası. `sonuclar/deney2/puanlar.csv` ile uygulamanın kuralını (`modeller/kural_ex1.json`) birleştirir; yeni sayı üretmez, veri seti gerekmez. | `sonuclar/sunum/2_hata_olcu_isi_haritasi.png` |

```bash
python -m araclar.sunum_sekilleri             # birkaç saniye; veri/rehab26/ gerekir
python -m araclar.kural_disa_aktar            # birkaç saniye; önce deney2 ve deney3 çalışmış olmalı
python -m araclar.hata_olcu_haritasi          # birkaç saniye; veri gerekmez
```

`veri/rehab26/` gerektirmez; `sonuclar/deney2/puanlar.csv`, `sonuclar/deney2/esikler.csv` ve `sonuclar/deney3/siddet_esikleri.csv` dosyalarını okur.
