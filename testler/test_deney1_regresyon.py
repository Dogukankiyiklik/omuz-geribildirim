"""
Deney 1 regresyon testi: kod değiştikten sonra Deney 1'in AUC tablosu (referans/beklenen_deney1_ozet.csv)
±0,01 içinde yeniden üretilmeli.

Beklenen dosya, Deney 1 tek deneye indirildiğinde (ham / genel bant / kişiye özel açı bandı) üretildi.
Sayıları, eski deney1b betiğinin açı bandı (v2) satırlarıyla birebir aynıydı (en büyük fark 0).

  * test_sonuc_dosyasi : sonuclar/deney1/ozet.csv varsa onu karşılaştırır.
  * test_yeniden_uret  : deneyi orijinal veriyle (zip) geçici klasörde yeniden çalıştırıp
                         karşılaştırır (~20 s).
"""
import numpy as np
import pandas as pd
import pytest

from cekirdek import veri

BEKLENEN = veri.KOK / "referans" / "beklenen_deney1_ozet.csv"
SONUC = veri.KOK / "sonuclar" / "deney1" / "ozet.csv"
TOLERANS = 0.01


def karsilastir(gercek: pd.DataFrame, beklenen: pd.DataFrame) -> float:
    """Aynı (koşul, ölçüt) satırlarındaki tüm sayısal sütunların en büyük mutlak farkı."""
    anahtar = ["kosul", "ölçüt"]
    g = gercek.astype({"kosul": str}).set_index(anahtar).sort_index()
    b = beklenen.set_index(anahtar).sort_index()
    assert list(g.index) == list(b.index), "satırlar farklı"
    assert set(b.columns) <= set(g.columns), f"eksik sütun: {set(b.columns) - set(g.columns)}"
    sayisal = [c for c in b.columns if pd.api.types.is_numeric_dtype(b[c])]
    assert (g[sayisal].isna() == b[sayisal].isna()).all().all(), "boş hücreler farklı"
    fark = (g[sayisal] - b[sayisal]).abs()
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
    tablo = deney1.calistir(cikti=tmp_path, yazdir=False)["ozet"]
    assert karsilastir(tablo, pd.read_csv(BEKLENEN)) <= TOLERANS
