"""Çekirdek fonksiyonların birim testleri (veri gerektirmez)."""
import numpy as np
import pytest

from cekirdek.bant import bant_hatasi, bant_modeli, kare_hatasi
from cekirdek.degerlendirme import auc, guven_araligi
from cekirdek.geometri import aci, nokta
from cekirdek.hizalama import dtw_yol, hizala
from cekirdek.ozellikler import OLCUTLER, olcut, ozellikler


# ---------------------------------------------------------------- referans DTW (saf Python, referans koddan)
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


def test_hizala_ortalama():
    ref = np.array([0.0, 1.0, 2.0, 1.0, 0.0])
    tekrar = {"kol": np.array([0.0, 1.0, 1.0, 2.0, 1.0, 0.0]), "X": np.arange(6.0)}
    h = hizala(ref, tekrar, ["X"])
    assert h["X"].shape == (5,)
    assert h["X"][1] == pytest.approx(1.5)  # ref karesi 1'e tekrar kare 1 ve 2 düşer


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


def _yapay_tekrar(rng, n, silkme=0.0):
    t = np.linspace(0, np.pi, n)
    return {"kol": 90 * np.sin(t) + rng.normal(0, 1, n),
            "Y": 0.3 - silkme * np.sin(t) + rng.normal(0, 0.005, n)}


def test_bant_silkmeyi_ayirir():
    rng = np.random.default_rng(0)
    dogrular = [_yapay_tekrar(rng, rng.integers(50, 70)) for _ in range(5)]
    model = bant_modeli(dogrular, rng, ["Y"])
    e_dogru = bant_hatasi(model, _yapay_tekrar(rng, 60), ["Y"])["Y"]
    e_silkme = bant_hatasi(model, _yapay_tekrar(rng, 60, silkme=0.08), ["Y"])["Y"]
    e_yukari = bant_hatasi(model, _yapay_tekrar(rng, 60, silkme=0.08), ["Y"], yon={"Y": +1})["Y"]
    assert e_silkme > e_dogru
    assert e_yukari < e_silkme  # silkme Y'yi düşürür; yalnızca yukarı sapma sayılırsa hata küçük


def test_auc():
    assert auc([3, 4, 5], [0, 1, 2]) == 1.0
    assert auc([0, 1], [0, 1]) == 0.5
    assert np.isnan(auc([], [1]))
    assert guven_araligi(np.arange(101)) == (2.5, 97.5)


def test_olcut_kaydi():
    assert {"kol", "M01", "M01_tek", "M39_F2", "M33", "YENI"} <= set(OLCUTLER)

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
