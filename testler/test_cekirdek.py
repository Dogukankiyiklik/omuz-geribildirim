"""Çekirdek fonksiyonların birim testleri (veri gerektirmez)."""
import numpy as np
import pytest

from cekirdek.aci_bandi import kare_hatasi
from cekirdek.degerlendirme import auc, guven_araligi
from cekirdek.geometri import aci, nokta
from cekirdek.hizalama import dtw_yol
from cekirdek.ozellikler import OLCUTLER, olcut, ozellikler


# ---------------------------------------------------------------- referans DTW (saf Python, ilk Deney 1 kodundan)
def dtw_yol_referans(a, b):
    a = (a - a.mean()) / (a.std() + 1e-9)
    b = (b - b.mean()) / (b.std() + 1e-9)
    n, m = len(a), len(b)
    D = np.full((n + 1, m + 1), np.inf)
    D[0, 0] = 0
    maliyet = np.abs(a[:, None] - b[None, :])
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            D[i, j] = maliyet[i - 1, j - 1] + min(D[i - 1, j], D[i, j - 1], D[i - 1, j - 1])
    i, j, yol = n, m, []
    while i > 0 and j > 0:
        yol.append((i - 1, j - 1))
        k = np.argmin([D[i - 1, j - 1], D[i - 1, j], D[i, j - 1]])
        i, j = (i - 1, j - 1) if k == 0 else (i - 1, j) if k == 1 else (i, j - 1)
    return yol[::-1]


@pytest.mark.parametrize("tohum", range(5))
def test_dtw_referansla_ayni(tohum):
    rng = np.random.default_rng(tohum)
    a = np.sin(np.linspace(0, np.pi, rng.integers(40, 90))) * 90 + rng.normal(0, 2, 1).item()
    b = np.sin(np.linspace(0, np.pi, rng.integers(40, 90)) ** 1.3) * 85
    b = b + rng.normal(0, 1, len(b))
    assert [tuple(x) for x in dtw_yol(a, b)] == dtw_yol_referans(a, b)


def test_dtw_esitlikte_ayni():
    # Sabit diziler: tüm maliyetler eşit, eşitlik kırma kuralı belirleyici
    a, b = np.zeros(7), np.zeros(5)
    assert [tuple(x) for x in dtw_yol(a, b)] == dtw_yol_referans(a, b)


def test_aci_ve_nokta():
    u = np.array([[1.0, 0.0], [1.0, 1.0]])
    v = np.array([[0.0, 1.0], [1.0, 0.0]])
    assert aci(u, v) == pytest.approx([90.0, 45.0], abs=1e-6)
    d = np.zeros((2, 33, 4))
    d[:, 12, 0], d[:, 12, 1] = 1.0, 0.5
    assert nokta(d, 12, 0.5).tolist() == [[0.5, 0.5], [0.5, 0.5]]


def test_kare_hatasi_yonsuz_ve_yonlu():
    mu, tau = np.zeros(4), np.ones(4)
    h = np.array([0.5, 1.5, -1.5, 5.0])
    assert kare_hatasi(h, mu, tau, 0).tolist() == [0, 0.5, 0.5, 1]
    assert kare_hatasi(h, mu, tau, +1).tolist() == [0, 0.5, 0, 1]
    assert kare_hatasi(h, mu, tau, -1).tolist() == [0, 0, 0.5, 0]


def test_auc():
    assert auc([3, 4, 5], [0, 1, 2]) == 1.0
    assert auc([0, 1], [0, 1]) == 0.5
    assert np.isnan(auc([], [1]))
    assert guven_araligi(np.arange(101)) == (2.5, 97.5)


def test_olcut_kaydi():
    assert {"kol", "M01", "M39_F2", "M33", "YENI"} <= set(OLCUTLER)

    @olcut("_deneme_olcutu")
    def _d(s):
        return s.p(0)[:, 1]
    try:
        d = np.random.default_rng(0).random((12, 33, 4))
        f = ozellikler(d, ["_deneme_olcutu"])
        assert set(f) == {"kol", "_deneme_olcutu"}
        with pytest.raises(ValueError):
            olcut("_deneme_olcutu")(_d)
    finally:
        OLCUTLER.pop("_deneme_olcutu")
