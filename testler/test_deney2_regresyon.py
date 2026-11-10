"""
Dondurulmuş yöntem (açı bandı, yönlü) kayıtlı Deney 2 kararlarını birebir üretmeli.
Puanlar sonuclar/deney2/puanlar.csv'den okunur; karar kuralı kişi bazlı birini-dışarıda-bırak ile yeniden
kurulur ve tahminler sonuclar/deney2/tahminler.csv ile karşılaştırılır.
Dosyalar yoksa (ör. temiz klon) test atlanır.
"""
import pandas as pd
import pytest

from cekirdek import veri

PUAN = veri.KOK / "sonuclar" / "deney2" / "puanlar.csv"
ILK = veri.KOK / "sonuclar" / "deney2" / "tahminler.csv"


@pytest.mark.skipif(not (PUAN.exists() and ILK.exists()), reason="Deney 2 çıktıları yok")
def test_dondurulmus_yontem_ilk_surumu_uretir():
    from deneyler import deney2
    tah, _ = deney2.loso(deney2.puanlari_oku(PUAN.parent))
    ilk = pd.read_csv(ILK, encoding="utf-8-sig", keep_default_na=False)
    anahtar = ["video", "kamera", "yonelim", "satir"]
    a = tah.set_index(anahtar).sort_index()
    b = ilk.set_index(anahtar).sort_index()
    assert len(a) == len(b) == 1668
    assert (a.tahmin == b.tahmin).all()
    assert (a.max_z - b.max_z).abs().max() < 1e-9
