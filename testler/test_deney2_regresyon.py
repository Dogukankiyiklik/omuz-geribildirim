"""
Karar 17–18 (Güncelleme 06): dondurulmuş Ex1 yöntemi (v2 yönlü + ilk sürüm kaldırma) Deney 2'nin
ilk sürüm kararlarını birebir üretmeli. Puanlar sonuclar/deney2/puanlar.csv'den okunur; karar kuralı
yeniden kurulur ve tahminler sonuclar/deney2_ilk/tahminler.csv ile karşılaştırılır.
Dosyalar yoksa (ör. temiz klon) test atlanır.
"""
import pandas as pd
import pytest

from cekirdek import veri

PUAN = veri.KOK / "sonuclar" / "deney2" / "puanlar.csv"
ILK = veri.KOK / "sonuclar" / "deney2_ilk" / "tahminler.csv"


@pytest.mark.skipif(not (PUAN.exists() and ILK.exists()), reason="Deney 2 çıktıları yok")
@pytest.mark.parametrize("bant,yonlu", [("v2", True)])
def test_dondurulmus_yontem_ilk_surumu_uretir(bant, yonlu):
    from deneyler import deney2
    puanlar = deney2.puanlari_oku(PUAN.parent)
    tah, _ = deney2.loso(puanlar[bant], yonlu)
    ilk = pd.read_csv(ILK, encoding="utf-8-sig", keep_default_na=False)
    ilk = ilk[ilk.sistem == deney2.sistem_adi(bant, yonlu)]
    anahtar = ["video", "kamera", "yonelim", "satir"]
    a = tah.set_index(anahtar).sort_index()
    b = ilk.set_index(anahtar).sort_index()
    assert len(a) == len(b) == 1668
    assert (a.tahmin == b.tahmin).all()
    assert (a.max_z - b.max_z).abs().max() < 1e-9
