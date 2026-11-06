"""Karar 25 tekrar ayırıcı ve Karar 24 kural dosyası testleri."""
import numpy as np
import pandas as pd

from cekirdek import hata_turu as ht
from cekirdek import kural_dosyasi
from cekirdek import tekrar_ayirici as ta
from cekirdek.aci_bandi import yumusak_kol


def _tekrar(dinlenme=10.0, tepe=170.0, kalkis=30, ust=15, inis=30):
    return np.concatenate([np.linspace(dinlenme, tepe, kalkis), np.full(ust, tepe), np.linspace(tepe, dinlenme, inis)])


def _dizi(*parcalar, ara=40, dinlenme=10.0):
    d = [np.full(ara, dinlenme)]
    for p in parcalar:
        d += [p, np.full(ara, dinlenme)]
    return np.concatenate(d)


def test_uc_tekrar_ve_sinirlar():
    kol = _dizi(_tekrar(), _tekrar(), _tekrar())
    t = ta.tekrarlari_bul(kol)
    assert len(t) == 3
    y = yumusak_kol(kol)
    for r in t:
        assert r.dinlenme == 10.0 and r.tepe == 170.0
        assert y[r.bas] <= 15.0 and y[r.bas + 1] > 15.0     # dinlenme + 5°'nin üstüne çıkmadan önceki son kare
        assert y[r.son] <= 15.0 and y[r.son - 1] > 15.0     # ilk dinlenme karesi
        assert y[r.s] > 30 and y[r.s - 1] <= 30 and y[r.e] < 20 and y[r.e - 1] >= 20
    assert t[0].son < t[1].bas


def test_yumusatma_scipy_ile_ayni():
    rng = np.random.default_rng(0)
    kol = _dizi(_tekrar())
    kol = kol + rng.normal(0, 3, len(kol))
    a = ta.TekrarAyirici()
    for v in kol:
        a.ekle(v)
    a.bitir()
    assert np.allclose(a.y, yumusak_kol(kol))


def test_kisa_ve_alcak_hareket_sayilmaz():
    kisa = _tekrar(kalkis=8, ust=2, inis=8)              # 30°→20° arası 0,8 s'den kısa
    alcak = _tekrar(tepe=55.0)                           # tepe < 60°
    assert ta.tekrarlari_bul(_dizi(kisa, alcak)) == []
    assert len(ta.tekrarlari_bul(_dizi(kisa, _tekrar(), alcak))) == 1


def test_bitis_en_fazla_bir_saniye_ve_dizi_sonu():
    # iniş 18°'de kalıyor: dinlenme + 5 = 15'e hiç inmiyor → bitiş = e + 30 kare
    p = np.concatenate([np.linspace(10, 170, 30), np.full(10, 170.0), np.linspace(170, 18, 30), np.full(60, 18.0)])
    kol = np.concatenate([np.full(40, 10.0), p])
    r, = ta.tekrarlari_bul(kol)
    assert r.son == r.e + 30
    # dizi bitişi aranırken biterse son kareyle kapanır
    r, = ta.tekrarlari_bul(kol[:r.e + 10])
    assert r.son == r.e + 9


def test_geri_en_fazla_iki_saniye():
    # 90 kare boyunca 20°'de bekleyip kalkıyor; dinlenme 20 → sınır 25; 30 kare öncesine kadar ≤ 25 → bulunur
    kol = np.concatenate([np.full(100, 20.0), np.linspace(20, 170, 30), np.full(10, 170.0), np.linspace(170, 10, 30),
                          np.full(40, 10.0)])
    r, = ta.tekrarlari_bul(kol)
    assert r.s - r.bas <= 60
    # Not: dinlenme son 1 s'nin medyanı olduğundan o 1 s'nin en az yarısı ≤ dinlenme + 5°; 2 s sınırı ancak
    # NaN'larla bağlayıcı olur. Önceki tekrarın bitişinden geriye gidilmediğini denetle:
    t = ta.tekrarlari_bul(_dizi(_tekrar(), _tekrar(), ara=3))
    assert len(t) == 2 and t[1].bas > t[0].son


def test_canli_ile_toplu_ayni():
    kol = _dizi(_tekrar(), _tekrar(tepe=120.0), _tekrar())
    a = ta.TekrarAyirici()
    canli = []
    for v in kol:
        canli += a.ekle(v)
    canli += a.bitir()
    assert canli == ta.tekrarlari_bul(kol)


def test_nan_kareler():
    kol = _dizi(_tekrar())
    kol[60:62] = np.nan
    assert len(ta.tekrarlari_bul(kol)) == 1


def test_kural_dosyasi_yaz_oku(tmp_path):
    rng = np.random.default_rng(0)
    df = pd.DataFrame({"hata": ["DOGRU"] * 50 + ["ERR_BENT_ARM"] * 50,
                       ht.puan_sutunu("dirsek", -1): np.r_[rng.uniform(0, .2, 50), rng.uniform(.3, 1, 50)]})
    kural = ht.KararKurali({"ERR_BENT_ARM": "dirsek"}, True, {"dirsek": -1}, {"dirsek": 0.1}, {"dirsek": 0.1},
                           T=1.5, bilgi={"egitim_makro_f1": 0.9})
    esik = {"ERR_BENT_ARM": (0.4, 0.7)}
    kural_dosyasi.kaydet(kural, esik, tmp_path / "k.json", {"commit": "abc"})
    k2, e2, b2 = kural_dosyasi.yukle(tmp_path / "k.json")
    assert e2 == esik and b2["commit"] == "abc" and k2.T == 1.5
    assert (k2.karar(df) == kural.karar(df)).all()
