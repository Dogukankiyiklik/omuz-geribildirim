"""Adım 6b: SILUET ölçütü (cekirdek/siluet.py), önbellek okuma ve açı bandının nan_atla yolu."""
from __future__ import annotations

import json

import numpy as np
import pytest

from araclar.siluet_segment import Onbellek
from cekirdek import siluet as sl
from cekirdek.aci_bandi import aci_bandi_hatasi, aci_bandi_modeli
from cekirdek.ozellikler import OLCUTLER, Iskelet

W, H = 400, 800


def _noktalar(kulak=(150.0, 100.0), omuz=(100.0, 200.0), gorunurluk=1.0) -> np.ndarray:
    """(33, 4) normalize noktalar; gövde (omuz ortası – kalça ortası) = 300 piksel."""
    P = np.full((33, 4), np.nan)
    P[:, 3] = gorunurluk
    px = {8: kulak, 12: omuz, 11: (omuz[0] + 100, omuz[1]), 23: (omuz[0], omuz[1] + 300),
          24: (omuz[0] + 100, omuz[1] + 300), 14: (omuz[0] - 10, omuz[1] + 100)}
    for e, (x, y) in px.items():
        P[e, :2] = (x / W, y / H)
    return P


def _maske(sinir_y) -> np.ndarray:
    """Tam maske (H, W): her x sütununda y ≥ sinir_y(x) kişinin içi (1), üstü arka plan (0)."""
    m = np.zeros((H, W), np.float32)
    for x in range(W):
        y = sinir_y(x)
        if y is not None:
            m[int(y):, x] = 0.9
    return m


def _roi(maske, nokta):
    P = sl.piksel_noktalar(nokta[None], W, H)[0]
    return sl.roi_kes(maske, sl.roi_kutusu(P, W, H)), P


# ---------------------------------------------------------------- sütun seçimi ve arama aralığı
def test_sutun_xleri_ortadaki_yuzde_elli():
    assert list(sl.sutun_xleri(100, 200)) == [125, 138, 150, 162, 175]   # np.rint: 137,5 → 138, 162,5 → 162
    assert list(sl.sutun_xleri(200, 100)) == list(sl.sutun_xleri(100, 200))  # sıra fark etmez
    assert list(sl.sutun_xleri(120, 120)) == [120] * 5


def test_arama_araligi_ve_kirpma():
    assert sl.arama_araligi(100, 200, 300, H) == (70, 260)       # 100 − 30, 200 + 60
    assert sl.arama_araligi(10, 790, 300, H) == (0, H - 1)        # görüntü içine kırpılır


# ---------------------------------------------------------------- sınır bulma
def test_sinir_bul_ilk_maske_pikseli():
    roi = sl.RoiMaske(0, 0, _maske(lambda x: 150)[:, :] > 0.5)
    assert sl.sinir_bul(roi, 120, 70, 260) == (150.0, False)
    # maske arama başında zaten 1 ise sınır = arama başı
    assert sl.sinir_bul(roi, 120, 160, 260)[0] == 160.0
    # aralıkta maske yoksa NaN
    y, _ = sl.sinir_bul(roi, 120, 70, 140)
    assert np.isnan(y)


def test_sinir_bul_esik_yarim():
    m = np.zeros((H, W), np.float32)
    m[120:, :] = 0.5     # tam 0,5 sayılmaz (> 0,5)
    m[150:, :] = 0.51
    roi = sl.roi_kes(m, (0, 0, W, H))
    assert sl.sinir_bul(roi, 50, 0, H - 1)[0] == 150.0


def test_sinir_bul_kutu_disina_tasma():
    roi = sl.RoiMaske(100, 100, np.ones((50, 50), bool))
    y, tasti = sl.sinir_bul(roi, 120, 50, 130)       # arama kutunun üstünden başlıyor
    assert tasti and y == 100.0
    y, tasti = sl.sinir_bul(roi, 300, 50, 130)       # sütun kutunun dışında
    assert tasti and np.isnan(y)


# ---------------------------------------------------------------- kare değeri ve NaN kuralları
def test_siluet_karesi_deger():
    nokta = _noktalar()
    roi, P = _roi(_maske(lambda x: 150), nokta)
    s = sl.siluet_karesi(roi, P, nokta[:, 3], 300.0, H)
    assert s.neden == "" and s.tasan == 0
    assert np.allclose(s.sinirlar, 150)
    assert s.deger == pytest.approx((150 - 100) / 300)


def test_siluet_karesi_medyan_ve_en_az_uc_sutun():
    nokta = _noktalar()
    xs = list(sl.sutun_xleri(150, 100))        # kulak x 150, omuz x 100 → 112, 119, 125, 131, 138
    assert xs == [112, 119, 125, 131, 138]
    # ikisinde sınır yok (NaN), üçünde 140, 150, 160
    sinir = {xs[0]: None, xs[1]: 140, xs[2]: 150, xs[3]: 160, xs[4]: None}
    roi, P = _roi(_maske(lambda x: sinir.get(x, None)), nokta)
    s = sl.siluet_karesi(roi, P, nokta[:, 3], 300.0, H)
    assert np.isfinite(s.sinirlar).sum() == 3
    assert s.deger == pytest.approx((150 - 100) / 300)
    # yalnızca iki geçerli sütun → NaN
    sinir2 = {xs[0]: None, xs[1]: None, xs[2]: 150, xs[3]: 160, xs[4]: None}
    roi2, _ = _roi(_maske(lambda x: sinir2.get(x, None)), nokta)
    s2 = sl.siluet_karesi(roi2, P, nokta[:, 3], 300.0, H)
    assert np.isnan(s2.deger) and s2.neden == "sütun"


def test_siluet_karesi_gorunurluk():
    for v_kulak, v_omuz in [(0.49, 0.9), (0.9, 0.49), (np.nan, 0.9)]:
        nokta = _noktalar()
        nokta[8, 3], nokta[12, 3] = v_kulak, v_omuz
        roi, P = _roi(_maske(lambda x: 150), nokta)
        s = sl.siluet_karesi(roi, P, nokta[:, 3], 300.0, H)
        assert np.isnan(s.deger) and s.neden == "görünürlük"
    nokta = _noktalar(gorunurluk=0.5)                         # tam 0,5 geçerli (≥ 0,5)
    roi, P = _roi(_maske(lambda x: 150), nokta)
    assert np.isfinite(sl.siluet_karesi(roi, P, nokta[:, 3], 300.0, H).deger)


def test_siluet_karesi_nokta_yok_ve_roi_yok():
    nokta = _noktalar()
    nokta[:, :2] = np.nan
    P = sl.piksel_noktalar(nokta[None], W, H)[0]
    assert sl.roi_kutusu(P, W, H) is None
    assert sl.siluet_karesi(None, P, nokta[:, 3], 300.0, H).neden == "nokta yok"


def test_silkme_degeri_kucultur():
    """Omuz silkilince siluet sınırı kulağa yaklaşır → SILUET küçülür (YENI ile aynı yön)."""
    nokta = _noktalar()
    roi_n, P = _roi(_maske(lambda x: 150), nokta)
    roi_s, _ = _roi(_maske(lambda x: 125), nokta)
    n = sl.siluet_karesi(roi_n, P, nokta[:, 3], 300.0, H).deger
    s = sl.siluet_karesi(roi_s, P, nokta[:, 3], 300.0, H).deger
    assert s < n


# ---------------------------------------------------------------- tekrar dizisi, g0 ve YENI
def test_siluet_dizisi_g0_ve_yeni_esdegerligi():
    rng = np.random.default_rng(0)
    dizi = np.stack([_noktalar() for _ in range(20)])
    dizi[:, :, :2] += rng.normal(0, 0.002, dizi[:, :, :2].shape)
    roiler = [_roi(_maske(lambda x: 150), dizi[i])[0] for i in range(20)]
    s = sl.siluet_dizisi(dizi, roiler, W, H)
    P = sl.piksel_noktalar(dizi, W, H)
    assert s["g0"] == pytest.approx(np.median(sl.govde_piksel(P)[:8]))
    # YENI_mp122, kayıtlı YENI ile aynı tanım (en-boy = W/H)
    yeni = OLCUTLER["YENI"](Iskelet(dizi, W / H))
    assert np.allclose(s["YENI_mp122"], yeni)
    assert s["SILUET"].shape == (20,) and np.isfinite(s["SILUET"]).all()
    # g0'da NaN kare atlanır
    dizi[2, :, :2] = np.nan
    s2 = sl.siluet_dizisi(dizi, roiler, W, H)
    assert np.isfinite(s2["g0"]) and np.isnan(s2["SILUET"][2]) and s2["neden"][2] == "nokta yok"


# ---------------------------------------------------------------- önbellek okuma
def test_onbellek_roi_paketleme(tmp_path):
    rng = np.random.default_rng(1)
    kutular = np.array([[10, 20, 23, 31], [0, 0, 0, 0], [5, 5, 12, 9]], np.int32)
    bitler, ofset, asil = [], [0], []
    for x0, y0, x1, y1 in kutular:
        b = rng.random((max(y1 - y0, 0), max(x1 - x0, 0))) > 0.5
        asil.append(b)
        p = np.packbits(b.ravel()) if b.size else np.zeros(0, np.uint8)
        bitler.append(p)
        ofset.append(ofset[-1] + len(p))
    bilgi = {"video": "v", "kamera": "c", "genislik": W, "yukseklik": H}
    yol = tmp_path / "v_c.npz"
    np.savez_compressed(yol, kareler=np.array([100, 101, 102]), noktalar=np.zeros((3, 33, 4), np.float32),
                        kutular=kutular, bitler=np.concatenate(bitler), ofset=np.array(ofset),
                        bilgi=json.dumps(bilgi))
    ob = Onbellek(yol)
    assert ob.roi(1) is None
    for i in (0, 2):
        r = ob.roi(i)
        assert (r.x0, r.y0, r.x1, r.y1) == tuple(kutular[i])
        assert np.array_equal(r.bitler, asil[i])
    dizi, roiler = ob.tekrar(101, 2)
    assert dizi.shape == (2, 33, 4) and roiler[0] is None
    with pytest.raises(KeyError):
        ob.tekrar(102, 2)


# ---------------------------------------------------------------- açı bandı, nan_atla
def _yapay_tekrar(rng, n=60):
    kol = np.concatenate([np.linspace(5, 150, n // 2), np.linspace(150, 5, n - n // 2)]) + rng.normal(0, 1, n)
    return {"kol": kol, "A": 0.3 + 0.001 * kol + rng.normal(0, 0.01, n)}


def test_nan_atla_sonlu_veride_ayni():
    rng = np.random.default_rng(0)
    dogrular = [_yapay_tekrar(rng) for _ in range(6)]
    test = _yapay_tekrar(rng)
    m0 = aci_bandi_modeli(dogrular, ["A"])
    m1 = aci_bandi_modeli(dogrular, ["A"], nan_atla=True)
    assert np.array_equal(m0.gecerli, m1.gecerli)
    assert np.allclose(m0.mu["A"], m1.mu["A"], equal_nan=True)
    assert np.allclose(m0.tau["A"], m1.tau["A"], equal_nan=True)
    E0, _ = aci_bandi_hatasi(m0, test, ["A"])
    E1, _ = aci_bandi_hatasi(m1, test, ["A"], nan_atla=True)
    assert E0["A"] == E1["A"]


def test_nan_atla_nan_kareleri_yok_sayar():
    rng = np.random.default_rng(0)
    dogrular = [_yapay_tekrar(rng) for _ in range(6)]
    for f in dogrular:
        f["A"][::7] = np.nan
    test = _yapay_tekrar(rng)
    test["A"][::5] = np.nan
    m = aci_bandi_modeli(dogrular, ["A"], nan_atla=True)
    E, _ = aci_bandi_hatasi(m, test, ["A"], nan_atla=True)
    assert np.isfinite(E["A"])
    # eski yol NaN'ı yayar (bu yüzden SILUET'te nan_atla gerekir)
    E_eski, _ = aci_bandi_hatasi(aci_bandi_modeli(dogrular, ["A"]), test, ["A"])
    assert np.isnan(E_eski["A"])


def test_nan_atla_en_az_uc_tekrar():
    """Bir kutuya NaN olmayan değer veren tekrar 3'ten azsa kutu geçersiz."""
    rng = np.random.default_rng(0)
    dogrular = [_yapay_tekrar(rng) for _ in range(4)]
    for f in dogrular[:2]:
        f["A"][:] = np.nan            # yalnızca 2 tekrar değer veriyor
    m = aci_bandi_modeli(dogrular, ["A"], nan_atla=True)
    assert not m.gecerli.any()
