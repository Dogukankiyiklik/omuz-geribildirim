"""Bilgi notları: hız, sol kol, kamera. Hata türü değildir."""
import json

import numpy as np
import pytest

from cekirdek import bilgi_notlari as bn
from cekirdek import veri


def _iskelet(sag: np.ndarray, sol: np.ndarray, omuz_genislik: float = 0.2) -> np.ndarray:
    """Kare başına sağ ve sol kol açısından (aşağı yönle, derece) yapay iskelet; en-boy 1 varsayılır."""
    n = len(sag)
    d = np.full((n, 33, 4), 0.5)
    d[..., 3] = 1.0
    x12, x11 = 0.5 - omuz_genislik / 2, 0.5 + omuz_genislik / 2
    d[:, 12, :2], d[:, 11, :2] = (x12, 0.3), (x11, 0.3)
    d[:, 24, :2], d[:, 23, :2] = (x12, 0.6), (x11, 0.6)
    d[:, [7, 8, 0, 2, 5], 1] = 0.2
    L = 0.15
    a, b = np.radians(sag), np.radians(sol)
    d[:, 14, 0], d[:, 14, 1] = x12 - L * np.sin(a), 0.3 + L * np.cos(a)
    d[:, 13, 0], d[:, 13, 1] = x11 + L * np.sin(b), 0.3 + L * np.cos(b)
    d[:, 16, :2], d[:, 15, :2] = d[:, 14, :2], d[:, 13, :2]
    return d


def test_sure_ve_hiz():
    assert bn.tekrar_suresi(0, 29, 30) == pytest.approx(1.0)
    assert bn.hiz_notu_gerekli(1.5, 1.9)
    assert not bn.hiz_notu_gerekli(1.9, 1.9)          # eşitlikte not yok (kesin küçük)
    assert not bn.hiz_notu_gerekli(1.0, None)          # eşik dosyası yoksa not yok
    assert not bn.hiz_notu_gerekli(np.nan, 1.9)


def test_sol_kol_acisi_sag_kolla_ayni_tanim():
    from cekirdek.ozellikler import OLCUTLER, Iskelet
    aci = np.array([0, 30, 60, 90, 120, 150.0])
    d = _iskelet(aci, aci)
    np.testing.assert_allclose(bn.sol_kol_acisi(d, 1.0), aci, atol=0.01)
    np.testing.assert_allclose(OLCUTLER["kol"](Iskelet(d, 1.0)), aci, atol=0.01)   # sağ kol ile aynı


def test_sol_kol_notu_60_derece():
    sag = np.full(30, 120.0)
    assert bn.SOL_KOL_ESIGI == 60.0
    assert not bn.sol_kol_notu_gerekli(bn.sol_kol_tepesi(_iskelet(sag, np.full(30, 55.0)), 1.0))
    assert bn.sol_kol_notu_gerekli(bn.sol_kol_tepesi(_iskelet(sag, np.full(30, 65.0)), 1.0))
    tek_kare = np.zeros(30)
    tek_kare[10] = 120.0                                 # tek karelik sıçrama (5 karelik medyan bastırır)
    assert not bn.sol_kol_notu_gerekli(bn.sol_kol_tepesi(_iskelet(sag, tek_kare), 1.0))


def test_notlar_satiri():
    d = _iskelet(np.full(30, 120.0), np.full(30, 90.0))
    n = bn.notlar(d, 1.0, 0.30, 1.0, 1.9, 0.3887)
    assert n.hiz and n.sol_kol and n.kamera
    assert n.metinler == [bn.HIZ_NOTU, bn.SOL_KOL_NOTU]
    s = n.satir()
    assert (s["hiz_notu"], s["sol_kol_notu"], s["kamera_uyarisi"]) == (1, 1, 1)
    n = bn.notlar(d * 1, 3.0, 0.60, 1.0, 1.9, 0.3887)
    assert not n.hiz and not n.kamera


def _hareket(tepe: float, kalkis: int, sol: float = 0.0, dinlenme: int = 45) -> tuple[np.ndarray, np.ndarray]:
    yukari = np.linspace(5, tepe, kalkis)
    sag = np.concatenate([np.full(dinlenme, 5.0), yukari, yukari[::-1], np.full(dinlenme, 5.0)])
    sol_a = np.where(sag > 30, sol, 5.0)
    return sag, sol_a


def test_oturum_csv_sutunlari():
    from uygulama.oturum import Oturum
    s1, l1 = _hareket(150, 15, sol=90)                   # hızlı ve iki kol
    s2, l2 = _hareket(150, 60)                           # yavaş, tek kol
    lm = _iskelet(np.concatenate([s1, s2]), np.concatenate([l1, l2]))
    o = Oturum(1.0, 30.0)
    for k in lm:
        o.kare_ekle(k)
    o.bitir()
    assert len(o.tekrarlar) == 2
    r1, r2 = o.oturum_satirlari()
    for a in ("kamera_orani", "kamera_uyarisi", "hiz_notu", "sol_kol_notu", "sol_kol_tepe", "bilgi_notu"):
        assert a in r1
    assert r1["sol_kol_notu"] == 1 and r2["sol_kol_notu"] == 0
    if o.hiz_esigi is not None:
        assert r1["hiz_notu"] == int(r1["sure_s"] < o.hiz_esigi) and r1["hiz_notu"] == 1
        assert r2["hiz_notu"] == 0
    assert r1["kamera_uyarisi"] == 0                     # omuz/gövde = 0.2 / 0.3 > eşik


@pytest.mark.skipif(not (bn.HIZ_ESIGI_DOSYASI.exists() and veri.SEGMENTASYON.exists()),
                    reason="hız eşiği ya da Segmentation.csv yok")
def test_hiz_esigi_dosyasi_yeniden_uretilir():
    from deneyler.hiz_esigi import esik_hesapla, sure_tablosu
    kayitli = json.loads(bn.HIZ_ESIGI_DOSYASI.read_text(encoding="utf-8"))["esik_s"]
    assert esik_hesapla(sure_tablosu()) == pytest.approx(kayitli)
