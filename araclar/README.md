# araclar/

Deney sayılmayan, ama sistemin bir parçasını üreten betik.

| Betik | Ne yapar | Çıktı |
| --- | --- | --- |
| `kural_disa_aktar.py` | **Uygulamanın karar kuralı dosyasını üretir.** Deneyde kural her seferinde 4 kişiyle kurulup 5. kişide sınanır. Uygulamada test kişisi olmadığından kural beş kişinin hepsiyle, aynı prosedürle kurulur: ölçekleme, yönler, öne kaçma ölçüsünün seçimi, eşik T ve şiddet eşikleri. Bulunan değerler deneydeki beş kuralla yan yana yazılır; böylece uygulamanın kuralının deneydekilerden farklı olmadığı görülür. | `modeller/kural_ex1.json`, `sonuclar/kural_disa_aktar/loso_karsilastirma.csv` |

```bash
python -m araclar.kural_disa_aktar            # birkaç saniye; önce deney2 ve deney3 çalışmış olmalı
```

`veri/rehab26/` gerektirmez; `sonuclar/deney2/puanlar.csv`, `sonuclar/deney2/esikler.csv` ve `sonuclar/deney3/siddet_esikleri.csv` dosyalarını okur.
