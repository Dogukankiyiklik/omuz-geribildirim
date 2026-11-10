"""Hata türü (Deney 2) testleri: yeni ölçütler, tek geçişli puanlar, karar kuralı."""
import numpy as np
import pandas as pd
import pytest

from cekirdek import aci_bandi as ab
from cekirdek import hata_turu as ht
from cekirdek.bant import coklu_model_hatasi, coklu_model_puanlari, coklu_referans_modelleri
from cekirdek.degerlendirme import karisiklik, makro_f1, sinif_metrikleri
from cekirdek.ozellikler import OLCUTLER, Iskelet


def _iskelet(kol_derece=90.0, dirsek_bukuk=False, bas_egik=0.0):
    """Tek kareli yapay iskelet (en-boy 1). y aşağı doğru."""
    d = np.zeros((1, 33, 4))
    P = {11: (0.6, 0.4), 12: (0.4, 0.4), 23: (0.58, 0.8), 24: (0.42, 0.8), 7: (0.6, 0.3), 8: (0.4, 0.3)}
    a = np.radians(kol_derece)
    yon = np.array([-np.sin(a), np.cos(a)])  # sağ kol (görüntüde sola) aşağıdan kol_derece kadar kalkmış
    omuz = np.array(P[12])
    dirsek = omuz + 0.15 * yon
    bilek = dirsek + 0.15 * (yon if not dirsek_bukuk else np.array([yon[1], -yon[0]]))
    P[14], P[16] = tuple(dirsek), tuple(bilek)
    if bas_egik:
        b = np.radians(bas_egik)
        orta = np.array([0.5, 0.4])
        for j in (7, 8):
            v = np.array(P[j]) - orta
            P[j] = tuple(orta + np.array([v[0] * np.cos(b) - v[1] * np.sin(b), v[0] * np.sin(b) + v[1] * np.cos(b)]))
    for j, (x, y) in P.items():
        d[0, j, :2] = x, y
    return Iskelet(d, en_boy=1.0)


def test_yeni_olcutler():
    s = _iskelet(90)
    assert OLCUTLER["dirsek"](s)[0] == pytest.approx(180, abs=0.05)  # aci() paydasındaki 1e-9 payı
    assert OLCUTLER["dirsek"](_iskelet(90, dirsek_bukuk=True))[0] == pytest.approx(90, abs=1e-4)
    assert OLCUTLER["bas"](s)[0] == pytest.approx(0, abs=0.05)
    assert OLCUTLER["bas"](_iskelet(90, bas_egik=20))[0] == pytest.approx(20, abs=0.05)
    assert OLCUTLER["kol_boyu"](s)[0] == pytest.approx(0.3 / 0.4, abs=1e-6)
    # kol 90°'de yana açıkken bilek – omuz – kalça açısı ≈ 90° + kalçanın içe kayması
    assert 85 < OLCUTLER["on_kacma"](s)[0] < 95


def _tekrar(rng, n=60, tepe=150.0, kayma=0.0):
    t = np.linspace(0, np.pi, n)
    kol = tepe * np.sin(t) + rng.normal(0, 0.5, n)
    return {"kol": kol, "Y": 0.5 - 0.001 * kol + kayma + rng.normal(0, 0.003, n),
            "Z": 1.0 + rng.normal(0, 0.01, n)}


def test_aci_bandi_puanlari_ayni_hesap():
    rng = np.random.default_rng(0)
    m = ab.aci_bandi_modeli([_tekrar(rng) for _ in range(5)], ["Y", "Z"])
    x = _tekrar(rng, kayma=-0.03)
    E, fark, ek = ab.aci_bandi_puanlari(m, x, ["Y", "Z"])
    for y in (0, 1, -1):
        E2, _ = ab.aci_bandi_hatasi(m, x, ["Y", "Z"], yon={"Y": y, "Z": y})
        for k in ("Y", "Z"):
            assert E[(k, y)] == pytest.approx(E2[k], abs=1e-12)
    assert fark["Y"] < 0 and E[("Y", -1)] > 0 and E[("Y", 1)] == 0
    # ayrıntı: imzalı fark ve bant dışı, geri bildirim için
    _, ay = ab.aci_bandi_hatasi(m, x, ["Y"], ayrinti=True)
    g = ay["gecerli"]
    assert np.allclose(ay["fark"]["Y"][g], x["Y"][g] - ay["mu"]["Y"][g])
    assert np.all(ay["bant_disi"]["Y"][g] <= 0)
    assert np.array_equal(ay["kol"], x["kol"]) and np.array_equal(ay["deger"]["Y"], x["Y"])
    assert np.isnan(ay["fark"]["Y"][~g]).all()


def test_coklu_model_puanlari_ayni_hesap():
    rng = np.random.default_rng(1)
    modeller = coklu_referans_modelleri([_tekrar(rng, n=int(rng.integers(50, 70))) for _ in range(4)], ["Y", "Z"])
    x = _tekrar(rng, kayma=0.02)
    E, fark = coklu_model_puanlari(modeller, x, ["Y", "Z"])
    for y in (0, 1, -1):
        E2 = coklu_model_hatasi(modeller, x, ["Y", "Z"], yon={"Y": y, "Z": y})
        for k in ("Y", "Z"):
            assert E[(k, y)] == pytest.approx(E2[k], abs=1e-12)
    assert fark["Y"] > 0


def test_tepe_bandi():
    from scipy.stats import t as td
    mu, tau = ht.tepe_bandi([170, 170, 170, 170])
    assert mu == 170 and tau == 10.0                                  # s = 0 → alt sınır 10°
    x = np.array([120.0, 150, 170, 190])
    mu, tau = ht.tepe_bandi(x)
    beklenen = td.ppf(0.975, 3) * x.std(ddof=1) / 2
    assert beklenen > 10 and mu == pytest.approx(157.5) and tau == pytest.approx(beklenen)


def test_kaldirma_puanlari():
    t = [170] * 4                      # μ = 170, τ = 10
    E, eksik = ht.kaldirma_puanlari(165, t)
    assert eksik == 5 and E == {1: 0.0, -1: 0.0, 0: 0.0}           # τ içinde
    E, eksik = ht.kaldirma_puanlari(150, t)
    assert eksik == 20 and E[1] == pytest.approx(1.0) and E[-1] == 0.0 and E[0] == pytest.approx(1.0)
    E, _ = ht.kaldirma_puanlari(155, t)
    assert E[1] == pytest.approx(0.5)
    E, _ = ht.kaldirma_puanlari(100, t)
    assert E[1] == 1.0                                               # üst sınır 1
    E, _ = ht.kaldirma_puanlari(185, t)                               # fazla kalkma: yalnızca yönsüz ve −1
    assert E[1] == 0.0 and E[-1] == pytest.approx(0.5) and E[0] == pytest.approx(0.5)


def test_kaldirma_sapmasi_ilk_surum():
    """İlk sürüm: d = (medyan − tepe) / max(IQR, 5°)."""
    t = [160.0, 170.0, 180.0, 190.0]                                  # medyan 175, IQR 15
    assert ht.kaldirma_sapmasi(145.0, t) == pytest.approx(2.0)
    assert ht.kaldirma_sapmasi(175.0, [175.0] * 4) == 0.0
    assert ht.kaldirma_sapmasi(165.0, [175.0] * 4) == pytest.approx(2.0)   # IQR 0 → 5° alt sınır
    df = pd.DataFrame({ht.fark_sutunu(ht.KALDIRMA_ILK): [2.0, -1.0]})
    assert list(ht.olcut_puani(df, ht.KALDIRMA, 1)) == [2.0, 0.0]          # varsayılan: ilk
    assert list(ht.olcut_puani(df, ht.KALDIRMA, -1)) == [0.0, 1.0]
    assert list(ht.olcut_puani(df, ht.KALDIRMA, 0)) == [2.0, 1.0]
    assert ht.VARSAYILAN_KALDIRMA == "ilk"
    with pytest.raises(ValueError):
        ht.olcut_puani(df, ht.KALDIRMA, 1, "baska")


def test_ilk_iki():
    z = pd.DataFrame({h: [0.0, 1.0, 0.0] for h in ht.HATALAR})
    z.loc[0, "ERR_BENT_ARM"], z.loc[0, "ERR_HEAD_TO_SIDE"] = 7.0, 3.0
    z.loc[1, "ERR_BENT_ARM"], z.loc[1, "ERR_HEAD_TO_SIDE"] = 2.0, 1.5
    z.loc[2, "ERR_LOW_ABDUCTION"] = np.nan
    r = ht.ilk_iki(z, T=2.5)
    assert list(r.z1_hata[:2]) == ["ERR_BENT_ARM", "ERR_BENT_ARM"]
    assert list(r.z2_hata[:2]) == ["ERR_HEAD_TO_SIDE", "ERR_HEAD_TO_SIDE"]
    assert list(r.soylenen1) == ["ERR_BENT_ARM", ht.DOGRU, ht.DOGRU]
    assert list(r.soylenen2) == ["ERR_HEAD_TO_SIDE", "", ""]
    assert list(r.soylenen1) == list(ht._karar(z, 2.5))              # 1. hata karar kuralıyla aynı


def _yapay_tablo(rng, kisiler=("A", "B", "C", "D", "E"), n_dogru=30, n_hata=10):
    """Her hata türü kendi ölçütünü beklenen yönde bozar."""
    satir = []
    yon = {"YENI": -1, "bas": 1, "on_kacma": 1, "kol_boyu": -1, "dirsek": -1}
    hata_olcut = ht.hata_olcutleri("kol_boyu")
    for k in kisiler:
        for h in [ht.DOGRU] * n_dogru + [h for h in ht.HATALAR for _ in range(n_hata)]:
            r = {"kisi": k, "hata": h, "ek_hata": "", "gorus": 0}
            for o in ("YENI", "bas", "on_kacma", "kol_boyu", "dirsek"):
                bozuk = hata_olcut.get(h) == o
                f = yon[o] * (0.3 if bozuk else 0.0) + rng.normal(0, 0.02)
                for y in (0, 1, -1):
                    e = abs(f) if y == 0 else max(np.sign(y) * f, 0)
                    r[ht.puan_sutunu(o, y)] = e + abs(rng.normal(0, 0.01))
                r[ht.fark_sutunu(o)] = f
            eksik = (30.0 if h == "ERR_LOW_ABDUCTION" else 0.0) + rng.normal(0, 2.0)
            E, r[ht.fark_sutunu(ht.KALDIRMA)] = ht.kaldirma_puanlari(170 - eksik, [170.0] * 4)
            for y in (0, 1, -1):
                r[ht.puan_sutunu(ht.KALDIRMA, y)] = E[y] + abs(rng.normal(0, 0.01))
            r[ht.fark_sutunu(ht.KALDIRMA_ILK)] = ht.kaldirma_sapmasi(170 - eksik, [168.0, 170.0, 171.0, 173.0])
            satir.append(r)
    return pd.DataFrame(satir)


@pytest.mark.parametrize("surum", ["ilk", "revize"])
def test_karar_kurali_yapay_veride_ayirir(surum):
    rng = np.random.default_rng(3)
    df = _yapay_tablo(rng)
    egitim, test = df[df.kisi != "E"], df[df.kisi == "E"]
    for yonlu in (False, True):
        kural = ht.esik_sec(egitim, yonlu, kaldirma_surumu=surum)
        assert kural.kaldirma_surumu == surum
        assert kural.on_olcut == "kol_boyu"
        assert kural.yonler == {"YENI": -1, "bas": 1, "kol_boyu": -1, "dirsek": -1, "kaldirma": 1}
        tah = kural.karar(test)
        assert makro_f1(test.hata, tah, ht.SINIFLAR) > 0.95


def test_esik_secimi_test_kisisine_bagli_degil():
    """Eğitim aynıysa test kişisinin verisi ne olursa olsun kural aynı (birini-dışarıda-bırak)."""
    rng = np.random.default_rng(4)
    df = _yapay_tablo(rng)
    egitim = df[df.kisi != "E"]
    k1 = ht.esik_sec(egitim, True)
    k2 = ht.esik_sec(egitim.copy(), True)
    assert k1.T == k2.T and k1.medyan == k2.medyan and k1.olcek == k2.olcek



def test_hata_tanimi_eslemeleri():
    e1 = ht.EX1.eslemeler()
    assert [e["ERR_ARM_FORWARD"] for e in e1] == ["on_kacma", "kol_boyu"]
    assert e1[0] == ht.hata_olcutleri("on_kacma")



def test_karar_nan_ve_esik():
    z = pd.DataFrame({h: [0.0, 5.0, np.nan] for h in ht.HATALAR})
    z.loc[1, "ERR_BENT_ARM"] = 7.0
    z.loc[2, "ERR_HEAD_TO_SIDE"] = 3.0
    k = ht._karar(z, T=2.5)
    assert list(k) == [ht.DOGRU, "ERR_BENT_ARM", "ERR_HEAD_TO_SIDE"]


def test_esnek_gercek_ve_metrikler():
    hata = pd.Series(["ERR_HEAD_TO_SIDE", "DOGRU", "ERR_BENT_ARM"])
    ek = pd.Series(["ERR_HEAD_TO_SIDE,ERR_ELEVATED_SHOULDER", "", ""])
    tah = pd.Series(["ERR_ELEVATED_SHOULDER", "DOGRU", "DOGRU"])
    assert list(ht.esnek_gercek(hata, ek, tah)) == ["ERR_ELEVATED_SHOULDER", "DOGRU", "ERR_BENT_ARM"]
    m = karisiklik(hata, tah, ht.SINIFLAR)
    assert m.to_numpy().sum() == 3 and m.loc["ERR_BENT_ARM", "DOGRU"] == 1
    s = sinif_metrikleri(hata, tah, ht.SINIFLAR).set_index("sınıf")
    assert s.loc["DOGRU", "duyarlılık"] == 1.0 and s.loc["DOGRU", "kesinlik"] == 0.5
