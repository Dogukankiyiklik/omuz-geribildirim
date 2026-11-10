"""Geri bildirim (Deney 3) testleri: sayı ekleri, faz/an seçimi, şiddet, şablonlar ve anahtar kelime çıkarıcı."""
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


# ---------------------------------------------------------------- sağlam ölçü
def _saglam_durum():
    kol = _kol()
    faz = gb.anlatim_fazlari(kol)
    n = len(kol)
    i_ind = np.flatnonzero(faz == gb.INDIRIRKEN)
    deger, mu, bd = np.full(n, 150.0), np.full(n, 170.0), np.zeros(n)
    return kol, faz, n, i_ind, deger, mu, bd


def test_saglam_gorunurluk_yolu_medyan():
    kol, faz, n, i_ind, deger, mu, bd = _saglam_durum()
    K = i_ind[:6]
    bd[K] = -5.0
    deger[K] = [150, 140, 130, 6, 145, 135]          # 6° çökmüş kare: görünürlüğü düşük
    mu[K] = [170, 171, 172, 173, 174, 175]
    bd[K[3]] = -100.0                                # tek kare kuralı bu kareyi seçerdi
    gor = np.ones(n)
    gor[K[3]] = 0.06
    tek = gb.durus_kodu("ERR_BENT_ARM", "dirsek", -1, "belirgin", kol, deger, mu, bd, olcu_surumu="tek_kare")
    assert (tek.olcu, tek.olcu_yolu, tek.olcu_kare_sayisi) == (6.0, gb.YOL_TEK, 1)
    k = gb.durus_kodu("ERR_BENT_ARM", "dirsek", -1, "belirgin", kol, deger, mu, bd,
                      olcu_surumu="saglam", gorunurluk=gor)
    assert k.olcu_yolu == gb.YOL_GORUNUR and k.olcu_kare_sayisi == 5
    assert k.olcu == np.median([150, 140, 130, 145, 135]) and k.beklenen == np.median([170, 171, 172, 174, 175])
    assert (k.faz, k.kare) == (tek.faz, tek.kare)    # faz ve an değişmez


def test_saglam_gorunurluk_kaldirilir_ve_yedek():
    kol, faz, n, i_ind, deger, mu, bd = _saglam_durum()
    K = i_ind[:4]
    bd[K] = -5.0
    deger[K] = [140, 130, 120, 110]
    gor = np.ones(n)
    gor[K[:2]] = 0.1                                  # görünür kare 2 < 3 → koşul kalkar, |K| = 4
    k = gb.durus_kodu("ERR_BENT_ARM", "dirsek", -1, "hafif", kol, deger, mu, bd, olcu_surumu="saglam", gorunurluk=gor)
    assert k.olcu_yolu == gb.YOL_GORUNURLUKSUZ and k.olcu_kare_sayisi == 4 and k.olcu == 125.0
    # K'de 2 kare: tek kare yedeği
    bd2 = np.zeros(n)
    bd2[i_ind[:2]] = [-5.0, -9.0]
    k = gb.durus_kodu("ERR_BENT_ARM", "dirsek", -1, "hafif", kol, deger, mu, bd2, olcu_surumu="saglam", gorunurluk=gor)
    assert k.olcu_yolu == gb.YOL_YEDEK and k.olcu_kare_sayisi == 1 and k.kare == i_ind[1] and k.olcu == 130.0


def test_saglam_K_bos_yedek_kural():
    kol, faz, n, i_ind, deger, mu, bd = _saglam_durum()   # hiç bant dışı kare yok → K boş
    deger[7] = 120.0
    k = gb.durus_kodu("ERR_BENT_ARM", "dirsek", -1, "hafif", kol, deger, mu, bd, olcu_surumu="saglam",
                      gorunurluk=np.ones(n))
    assert k.olcu_yolu == gb.YOL_YEDEK and k.kare == 7 and k.olcu == 120.0


def test_saglam_omuz_egim_ayni_K():
    kol, faz, n, i_ind, deger, mu, bd = _saglam_durum()
    K = i_ind[:3]
    bd[K] = -0.02
    ek_d, ek_m = np.zeros(n), np.full(n, np.nan)
    ek_d[K], ek_m[K] = [8.0, 10.0, 30.0], [1.0, np.nan, 3.0]
    k = gb.durus_kodu("ERR_ELEVATED_SHOULDER", "YENI", -1, "hafif", kol, deger / 500, mu / 500, bd, ek_d, ek_m,
                      olcu_surumu="saglam", gorunurluk=np.ones(n))
    assert k.ek_olcu == 10.0 and k.ek_beklenen == 2.0


def test_olcu_surumu_gecersiz():
    kol, faz, n, i_ind, deger, mu, bd = _saglam_durum()
    with pytest.raises(ValueError):
        gb.durus_kodu("ERR_BENT_ARM", "dirsek", -1, "hafif", kol, deger, mu, bd, olcu_surumu="baska")


def test_olcut_gorunurlugu():
    dizi = np.ones((4, 33, 4))
    dizi[2, 14, 3] = 0.2
    assert list(gb.olcut_gorunurlugu(dizi, "dirsek")) == [1, 1, 0.2, 1]
    assert list(gb.olcut_gorunurlugu(dizi, "YENI")) == [1, 1, 1, 1]


# ---------------------------------------------------------------- hasta cümlesi
def test_yuvarla5():
    assert [gb.yuvarla5(x) for x in (0, 2.4, 2.5, 7.4, 7.5, 168.0, 172.6)] == [0, 0, 5, 5, 10, 170, 175]
    assert gb.yuvarla5(None) is None and gb.yuvarla5(np.nan) is None


def test_hasta_kaldirma_hocanin_ornegi():
    k = gb.kaldirma_kodu(1, "çok belirgin", 148.0, 171.0)      # 150 ve 170 → fark 20
    assert gb.hasta_cumlesi(k) == ("Kolunu 150 dereceye kadar kaldırdın; normalde 170 dereceye çıkıyorsun. "
                                   "Kolunu yaklaşık 20 derece daha yukarı kaldır.")
    k0 = gb.kaldirma_kodu(1, "hafif", 168.0, 171.0)             # 170 ve 170 → fark 0: sayısız
    c = gb.hasta_cumlesi(k0)
    assert not any(ch.isdigit() for ch in c) and cozumle(c) == ["ERR_LOW_ABDUCTION"]


def test_hasta_bes_derece_ve_sifir_fark():
    # dirsek: 152 → 150, 171 → 170: 20 derece (1°'lik fark 19 olurdu)
    k = gb.SapmaKodu("ERR_BENT_ARM", "dirsek", -1, "belirgin", 152.0, 171.0, gb.USTTE, 3)
    assert gb.hasta_cumlesi(k) == "Kolun yukarıdayken dirseğini yaklaşık 20 derece büktün. Kolunu düz tut."
    k = gb.SapmaKodu("ERR_BENT_ARM", "dirsek", -1, "belirgin", 168.0, 171.0, gb.USTTE, 3)
    assert gb.hasta_cumlesi(k) == "Kolun yukarıdayken dirseğini büktün. Kolunu düz tut."
    # baş: 23,6 → 25, 4 → 5: 20 derece
    k = gb.SapmaKodu("ERR_HEAD_TO_SIDE", "bas", 1, "çok belirgin", 23.6, 4.0, gb.USTTE, 3)
    assert "yaklaşık 20 derece yana eğdin" in gb.hasta_cumlesi(k)
    # omuz: eğim farkı yuvarlanınca 0 → sayısız; ters işaret → sayısız
    for eo, eb, bek in ((2.0, 1.0, None), (12.4, 1.0, 10), (1.0, 12.0, None)):
        k = gb.SapmaKodu("ERR_ELEVATED_SHOULDER", "YENI", -1, "belirgin", 0.25, 0.32, gb.KALDIRIRKEN, 3, eo, eb)
        c = gb.hasta_cumlesi(k)
        assert (f"yaklaşık {bek} derece" in c) if bek else not any(ch.isdigit() for ch in c), c


def _kelime(c: str) -> int:
    return len(c.split())


def test_hasta_kurallari_tum_kodlar():
    for k in _tum_kodlar():
        c = gb.hasta_cumlesi(k)
        assert "%" not in c and "gövde boy" not in c, c
        assert not any(w in c for w in ("biraz", "belirgin", "çok ")), c
        assert _kelime(c) <= 20, (c, _kelime(c))
        sayilar = [int(x) for x in __import__("re").findall(r"\d+", c)]
        assert all(x % 5 == 0 for x in sayilar), c
        if k.hata == "ERR_ARM_FORWARD":
            assert not sayilar, c


def test_cikarici_hasta_tek_hata():
    for k in _tum_kodlar():
        c = gb.hasta_cumlesi(k)
        assert cozumle(c) == [k.hata], c


def test_cikarici_hasta_iki_hata():
    tekler = {}
    for k in _tum_kodlar():
        tekler.setdefault((k.hata, k.yon, k.faz, k.olcu is None), k)
    sayi = 0
    for a, b in itertools.permutations(tekler, 2):
        if a[0] == b[0]:
            continue
        c = gb.hasta_geri_bildirimi([tekler[a], tekler[b]], 150, 0)
        assert cozumle(c) == [a[0], b[0]], c
        sayi += 1
    assert sayi > 1000


def test_cikarici_hasta_olumlu():
    for i in range(len(gb.OLUMLU_HASTA)):
        for t in (90.0, 151.4, 176.0):
            c = gb.olumlu_hasta_cumlesi(t, i)
            assert cozumle(c) == [] and "%" not in c, c
    assert gb.olumlu_hasta_cumlesi(168.0, 0) == gb.OLUMLU_HASTA[0].format(t=170)
    ik = gb.iki_katman([], 168.0, 0)
    assert ik["uzman_ayrintisi"] == gb.olumlu_cumle(168.0, 0) and ik["hasta_cumlesi"] == gb.OLUMLU_HASTA[0].format(t=170)


BILINEN_HATALAR = {"Omzun kalkmadı, kolun düzdü, güzel tekrar."}   # olumsuz geçmiş zaman (modül belgesi)


@pytest.mark.parametrize("cumle,beklenen", [
    pytest.param(c, b, marks=pytest.mark.xfail(strict=True, reason="bilinen sınırlılık")) if c in BILINEN_HATALAR
    else (c, b) for c, b in ELLE_CUMLELER])
def test_cikarici_elle_cumleler(cumle, beklenen):
    assert cozumle(cumle) == beklenen
