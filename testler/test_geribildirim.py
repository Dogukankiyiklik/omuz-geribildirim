"""Adım 5 (Deney 3) testleri: sayı ekleri, faz/an seçimi, şiddet, şablonlar ve anahtar kelime çıkarıcı."""
import itertools

import numpy as np
import pandas as pd
import pytest

from cekirdek import geribildirim as gb
from cekirdek import hata_turu as ht
from cekirdek.metin_cozumleyici import cozumle
from testler.elle_cumleler import ELLE_CUMLELER


@pytest.mark.parametrize("n,iyelik,yonelme", [
    (32, "si", "ye"), (25, "i", "e"), (30, "u", "a"), (40, "ı", "a"), (6, "sı", "ya"), (100, "ü", "e"),
    (3, "ü", "e"), (4, "ü", "e"), (9, "u", "a"), (10, "u", "a"), (20, "si", "ye"), (50, "si", "ye"),
    (60, "ı", "a"), (70, "i", "e"), (80, "i", "e"), (90, "ı", "a"), (0, "ı", "a"), (1, "i", "e"),
    (7, "si", "ye"), (8, "i", "e"), (5, "i", "e"), (2, "si", "ye")])
def test_sayi_eki(n, iyelik, yonelme):
    assert gb.sayi_eki(n, "iyelik") == iyelik
    assert gb.sayi_eki(n, "yonelme") == yonelme


def test_yuvarla():
    assert gb.yuvarla(2.5) == 3 and gb.yuvarla(2.49) == 2 and gb.yuvarla(-2.5) == -2


def _kol():
    return np.concatenate([np.linspace(10, 150, 30), np.full(10, 150.0), np.linspace(150, 10, 30)])


def test_anlatim_fazlari():
    kol = _kol()
    faz = gb.anlatim_fazlari(kol)
    y = gb.yumusak_kol(kol)
    ust = y >= 0.85 * y.max()
    assert (faz[ust] == gb.USTTE).all()
    i0, i1 = np.flatnonzero(ust)[[0, -1]]
    assert (faz[:i0] == gb.KALDIRIRKEN).all() and (faz[i1 + 1:] == gb.INDIRIRKEN).all()


def test_an_sec_faz_ve_kare():
    kol = _kol()
    faz = gb.anlatim_fazlari(kol)
    n = len(kol)
    deger, mu = np.full(n, 0.30), np.full(n, 0.32)
    bd = np.zeros(n)
    i_kal = np.flatnonzero(faz == gb.KALDIRIRKEN)
    i_ind = np.flatnonzero(faz == gb.INDIRIRKEN)
    bd[i_kal[5]] = -0.05                      # tek büyük kare kaldırırken
    bd[i_ind[:10]] = -0.02                    # indirirken toplam daha büyük (0,20 > 0,05)
    bd[i_ind[3]] = -0.03
    bd[i_ind[4]] = +0.5                       # ters yön sayılmaz (yon = −1)
    p, j = gb.an_sec(kol, deger, mu, bd, yon=-1)
    assert p == gb.INDIRIRKEN and j == i_ind[3]
    # bant dışı yoksa yedek kural: beklenen yöndeki imzalı fark en büyük kare
    deger2 = deger.copy()
    deger2[7] = 0.20
    p, j = gb.an_sec(kol, deger2, mu, np.zeros(n), yon=-1)
    assert j == 7 and p == faz[7]


def test_model_ortalamasi_karar7():
    a1 = {"gecerli": np.array([True, True, False]), "mu": {"x": np.array([1.0, 2.0, 9.0])},
          "bant_disi": {"x": np.array([0.0, -1.0, np.nan])}}
    a2 = {"gecerli": np.array([True, False, False]), "mu": {"x": np.array([3.0, 9.0, 9.0])},
          "bant_disi": {"x": np.array([-2.0, np.nan, np.nan])}}
    mu, bd = gb.model_ortalamasi([a1, a2], "x")
    assert mu[0] == 2.0 and mu[1] == 2.0 and np.isnan(mu[2])
    assert bd[0] == -1.0 and bd[1] == -1.0 and np.isnan(bd[2])


def test_siddet_esikleri_ucte_bir():
    rng = np.random.default_rng(0)
    df = pd.DataFrame({"hata": ["ERR_BENT_ARM"] * 300, ht.puan_sutunu("dirsek", -1): rng.uniform(0, 1, 300)})
    kural = ht.KararKurali({"ERR_BENT_ARM": "dirsek"}, True, {"dirsek": -1}, {"dirsek": 0.0}, {"dirsek": 1.0})
    q = gb.siddet_esikleri(df, kural)["ERR_BENT_ARM"]
    p = df[ht.puan_sutunu("dirsek", -1)]
    assert q == pytest.approx(tuple(np.percentile(p, [100 / 3, 200 / 3])))
    siniflar = [gb.siddet_sinifi(x, q) for x in p]
    assert abs(siniflar.count("hafif") - 100) <= 1 and abs(siniflar.count("çok belirgin") - 100) <= 1


def test_sapma_kodu_birim_ve_fark():
    k = gb.SapmaKodu("ERR_ELEVATED_SHOULDER", "YENI", -1, "belirgin", 0.2549, 0.3150, gb.KALDIRIRKEN, 5, 7.6, 1.4)
    assert (k.birim, k.olcu_g, k.beklenen_g, k.fark, k.ek_fark) == ("%", 25, 32, -7, 7)
    c = gb.hata_cumlesi(k)
    assert "%32'si iken %25'e indi" in c and "6 derece yukarı" not in c and "7 derece yukarı" in c
    kk = gb.kaldirma_kodu(1, "çok belirgin", 118.4, 151.6)
    assert (kk.olcu_g, kk.beklenen_g, kk.fark) == (118, 152, 34)
    assert gb.hata_cumlesi(kk) == ("Kolunu çok az kaldırdın: en fazla 118 dereceye çıktı, normalde 152 dereceye "
                                   "kadar çıkıyordun. Kolunu yaklaşık 34 derece daha yukarı kaldır.")


# ---------------------------------------------------------------- çıkarıcı: şablonların %100'ü
OLCUT_SECENEKLERI = {"ERR_ELEVATED_SHOULDER": ["YENI"], "ERR_HEAD_TO_SIDE": ["bas"],
                     "ERR_ARM_FORWARD": ["kol_boyu", "on_kacma"], "ERR_BENT_ARM": ["dirsek"],
                     "ERR_LOW_ABDUCTION": [ht.KALDIRMA]}


def _tum_kodlar():
    for h in ht.HATALAR:
        for o, yon, s, faz, olculu, ek in itertools.product(OLCUT_SECENEKLERI[h], (1, -1), gb.SIDDETLER,
                                                           (0, 1, 2, None), (True, False), (True, False)):
            v = (0.25, 0.32) if o in gb.YUZDE_OLCUTLERI else (118.0, 152.0)
            yield gb.SapmaKodu(h, o, yon, s, v[0] if olculu else None, v[1] if olculu else None, faz, 3,
                               9.0 if ek else None, 1.0 if ek else None)


def test_cikarici_tek_hata_sablonlari():
    kodlar = list(_tum_kodlar())
    assert len(kodlar) > 400
    for k in kodlar:
        for kisa in (False, True):
            c = gb.hata_cumlesi(k, kisa)
            assert cozumle(c) == [k.hata], c


def test_cikarici_iki_hata_sablonlari():
    tekler = {}
    for k in _tum_kodlar():
        tekler.setdefault((k.hata, k.yon), k)
    for (a, b) in itertools.permutations(tekler, 2):
        if a[0] == b[0]:
            continue
        c = gb.geri_bildirim([tekler[a], tekler[b]], 150, 0)
        assert cozumle(c) == [a[0], b[0]], c


def test_cikarici_olumlu_sablonlar():
    for i in range(len(gb.OLUMLU)):
        for t in (90.0, 151.4, 176.0):
            c = gb.olumlu_cumle(t, i)
            assert cozumle(c) == [], c
    assert gb.olumlu_cumle(151.4, 0) == gb.OLUMLU[0].format(t=151)
    assert gb.olumlu_cumle(151.4, 1, tohum=3) == gb.OLUMLU[0].format(t=151)


BILINEN_HATALAR = {"Omzun kalkmadı, kolun düzdü, güzel tekrar."}   # olumsuz geçmiş zaman (modül belgesi)


@pytest.mark.parametrize("cumle,beklenen", [
    pytest.param(c, b, marks=pytest.mark.xfail(strict=True, reason="bilinen sınırlılık")) if c in BILINEN_HATALAR
    else (c, b) for c, b in ELLE_CUMLELER])
def test_cikarici_elle_cumleler(cumle, beklenen):
    assert cozumle(cumle) == beklenen
