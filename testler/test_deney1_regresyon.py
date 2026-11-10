"""
Deney 1 regresyon testi: çekirdek, referans kodun sonuçlarını (referans/beklenen_deney1_ozet.csv)
±0,01 içinde yeniden üretmeli. Tohum 0, en-boy 9/16.

  * test_sonuc_dosyasi : sonuclar/deney1/ozet.csv (kullanıcının çalıştırdığı) varsa onu karşılaştırır.
  * test_yeniden_uret  : deneyi orijinal veriyle (zip) geçici klasörde yeniden çalıştırıp
                         karşılaştırır (~15 s).
"""
import numpy as np
import pandas as pd
import pytest

from cekirdek import veri

BEKLENEN = veri.KOK / "referans" / "beklenen_deney1_ozet.csv"
SONUC = veri.KOK / "sonuclar" / "deney1" / "ozet.csv"
TOLERANS = 0.01


def karsilastir(gercek: pd.DataFrame, beklenen: pd.DataFrame) -> float:
    """Aynı (yöntem, ölçüt) satırlarındaki tüm sayısal sütunların en büyük mutlak farkı."""
    anahtar = ["yöntem", "ölçüt"]
    g = gercek.set_index(anahtar).sort_index()
    b = beklenen.set_index(anahtar).sort_index()
    assert list(g.index) == list(b.index), "satırlar farklı"
    assert set(b.columns) <= set(g.columns), f"eksik sütun: {set(b.columns) - set(g.columns)}"
    fark = (g[b.columns] - b).abs()
    # Ψ ham satırlarında boş: iki tarafta da boş olmalı
    assert (g[b.columns].isna() == b.isna()).all().all(), "boş hücreler farklı"
    en_buyuk = float(np.nanmax(fark.values))
    print(f"\nEn büyük mutlak fark: {en_buyuk:.6g}  ({fark.stack().idxmax()})")
    return en_buyuk


@pytest.mark.skipif(not SONUC.exists(), reason="sonuclar/deney1/ozet.csv yok (python -m deneyler.deney1)")
def test_sonuc_dosyasi():
    assert karsilastir(pd.read_csv(SONUC), pd.read_csv(BEKLENEN)) <= TOLERANS


def test_yeniden_uret(tmp_path):
    if not veri.ISKELET_ZIP.exists():
        pytest.skip("orijinal zip yok")
    from deneyler import deney1
    tablo = deney1.calistir(tohum=0, cikti=tmp_path, bootstrap_n=0, yazdir=False)
    assert karsilastir(tablo, pd.read_csv(BEKLENEN)) <= TOLERANS
