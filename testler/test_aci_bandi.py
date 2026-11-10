"""Açı bandı ve çoklu referans testleri."""
import numpy as np
import pandas as pd
import pytest

from cekirdek import aci_bandi as ab
from cekirdek import veri
from cekirdek.bant import bant_hatasi, bant_modeli, bant_modeli_ref, coklu_referans_hatasi


def _tekrar(rng, n=60, tepe=150.0, silkme=0.0, gurultu=0.003):
    """Yapay tekrar: kol 0 → tepe → 0; Y kol açısıyla doğal olarak azalır (omuz kalkar), silkme ek düşüş."""
    t = np.linspace(0, np.pi, n)
    kol = tepe * np.sin(t) + rng.normal(0, 0.5, n)
    Y = 0.5 - 0.001 * kol - silkme * np.sin(t) + rng.normal(0, gurultu, n)
    return {"kol": kol, "Y": Y}


def test_fazlar_ve_kutular():
    kol = 150 * np.sin(np.linspace(0, np.pi, 41))  # tepe 20. karede
    faz, tepe = ab.fazlar(kol)
    assert abs(tepe - 20) <= 1  # medyan filtresi tepede eşit değerler üretebilir
    assert (faz[:tepe + 1] == 0).all() and (faz[tepe + 1:] == 1).all()
    assert ab.kutular(np.array([0, 4.99, 5, 179.9, 180, 200])).tolist() == [0, 0, 1, 35, 35, 35]


def test_fazlar_tek_kare_sicramasina_dayanikli():
    kol = np.array([0, 20, 60, 100, 179, 100, 101, 102, 60, 10.0])  # 4. karede tek karelik sıçrama
    _, tepe = ab.fazlar(kol)
    assert tepe != 4


def test_model_gecerlilik_ve_ara_deger():
    rng = np.random.default_rng(0)
    dogrular = [_tekrar(rng, tepe=150) for _ in range(5)]
    m = ab.aci_bandi_modeli(dogrular, ["Y"])
    # Her iki fazda da 0–150° civarı kapsanmalı, 160° üstü kapsanmamalı
    for p in (ab.KALDIRMA, ab.INDIRME):
        gecerli = np.flatnonzero(m.gecerli[p])
        assert gecerli[0] <= 1 and 27 <= gecerli[-1] <= 30
        assert not m.gecerli[p, 32:].any()
        # aralık içinde boşluk yok (ara değer)
        assert (np.diff(gecerli) == 1).all()
        assert not np.isnan(m.mu["Y"][p, gecerli]).any()
        assert (m.tau["Y"][p, gecerli] > 0).all()
    assert m.en_yuksek_aci == pytest.approx(max(m.tepe_acilari))


def test_iki_tekrar_yetmez():
    rng = np.random.default_rng(1)
    m = ab.aci_bandi_modeli([_tekrar(rng) for _ in range(2)], ["Y"])
    assert not m.gecerli.any()
    E, ek = ab.aci_bandi_hatasi(m, _tekrar(rng), ["Y"])
    assert np.isnan(E["Y"]) and ek["kapsam"] == 0.0


def test_silkme_ayrilir_ve_dusuk_kol_cezalanmaz():
    """Asıl fikir: kol az kalksa da omuz AYNI kol açısında karşılaştırılır (Petra bulgusu)."""
    rng = np.random.default_rng(2)
    dogrular = [_tekrar(rng, n=int(rng.integers(55, 70)), tepe=150) for _ in range(5)]
    m = ab.aci_bandi_modeli(dogrular, ["Y"])
    e_dogru = ab.aci_bandi_hatasi(m, _tekrar(rng, tepe=150), ["Y"])[0]["Y"]
    e_alcak = ab.aci_bandi_hatasi(m, _tekrar(rng, tepe=100), ["Y"])[0]["Y"]   # doğru ama az kalkan
    e_silkme = ab.aci_bandi_hatasi(m, _tekrar(rng, tepe=100, silkme=0.05), ["Y"])[0]["Y"]
    assert e_silkme > 0.3
    assert e_silkme > 2 * max(e_dogru, e_alcak)
    assert abs(e_alcak - e_dogru) < 0.1  # az kalkan doğru tekrar, tam kalkan doğru tekrar kadar "normal"


def test_aralik_disi_ve_kapsam():
    rng = np.random.default_rng(3)
    m = ab.aci_bandi_modeli([_tekrar(rng, tepe=120) for _ in range(5)], ["Y"])
    E, ek = ab.aci_bandi_hatasi(m, _tekrar(rng, tepe=175), ["Y"])
    assert ek["aralik_disi"] and ek["kapsam"] < 1.0
    _, ek2 = ab.aci_bandi_hatasi(m, _tekrar(rng, tepe=120), ["Y"])
    assert not ek2["aralik_disi"] and ek2["kapsam"] > 0.9


def test_yonlu():
    rng = np.random.default_rng(4)
    m = ab.aci_bandi_modeli([_tekrar(rng) for _ in range(5)], ["Y"])
    s = _tekrar(rng, silkme=0.05)  # Y düşer
    assert ab.aci_bandi_hatasi(m, s, ["Y"], yon={"Y": +1})[0]["Y"] < ab.aci_bandi_hatasi(m, s, ["Y"], yon={"Y": -1})[0]["Y"]


def test_aci_eslemesi_ayni_faz():
    ref = np.array([0, 30, 60, 90, 60, 30, 0.0])
    kul = np.array([0, 60, 90, 30.0])
    assert ab.aci_eslemesi(ref, kul).tolist() == [0, 2, 3, 5]


def test_bant_modeli_ref_ayni():
    rng = np.random.default_rng(5)
    d = [_tekrar(rng, n=int(rng.integers(50, 70))) for _ in range(4)]
    r1 = np.random.default_rng(9)
    m = bant_modeli(d, r1, ["Y"])
    m2 = bant_modeli_ref(d, m["ref_indeks"], ["Y"])
    assert np.array_equal(m["Y"][0], m2["Y"][0]) and np.array_equal(m["Y"][1], m2["Y"][1])


def test_coklu_referans_ortalama():
    rng = np.random.default_rng(6)
    d = [_tekrar(rng, n=int(rng.integers(50, 70))) for _ in range(4)]
    t = _tekrar(rng, silkme=0.03)
    beklenen = np.mean([bant_hatasi(bant_modeli_ref(d, r, ["Y"]), t, ["Y"])["Y"] for r in range(4)])
    assert coklu_referans_hatasi(d, t, ["Y"])["Y"] == pytest.approx(beklenen)


@pytest.mark.skipif(not veri.ISKELET_ZIP.exists(), reason="orijinal zip yok")
def test_etiketli_kareler():
    seg = veri.segmentasyon_oku()
    ts = veri.tekrarlari_yukle(1)
    for t in ts[:50]:
        r = seg.loc[t.satir]
        s = t.etiketli
        assert t.ilk_kare + s.start == r.first_frame
        assert t.ilk_kare + s.stop - 1 == r.last_frame


def test_adil_ortalama_hata():
    """Adil model: her doğru tekrar sırayla dışarıda, E'lerin ortalaması; NaN'lar atlanır."""
    from cekirdek.adil_model import adil_ortalama_hata, birini_disarida_alt_kumeler, ortalama_E
    alt = birini_disarida_alt_kumeler([1, 2, 3, 4])
    assert alt == [[2, 3, 4], [1, 3, 4], [1, 2, 4], [1, 2, 3]]
    E, s = adil_ortalama_hata([1, 2, 3, 4], lambda a: ({"Y": float(sum(a))}, {}), ["Y"])
    assert E["Y"] == pytest.approx(np.mean([9, 8, 7, 6])) and len(s) == 4
    assert ortalama_E([{"Y": np.nan}, {"Y": 0.4}], ["Y"])["Y"] == pytest.approx(0.4)
    assert np.isnan(ortalama_E([{"Y": np.nan}, {"Y": np.nan}], ["Y"])["Y"])


@pytest.mark.skipif(not veri.ISKELET_ZIP.exists(), reason="orijinal zip yok")
def test_genel_bant_test_kisisini_icermez(monkeypatch):
    """Deney 1: genel bant, test kişisi hariç aynı kamera/yönelimdeki diğer kişilerin doğru tekrarlarından kurulur."""
    from deneyler import deney1
    gorulen = []
    eski = deney1.aci_bandi_modeli

    def kaydet(fl, olcutler):
        gorulen.append(len(fl))
        return eski(fl, olcutler)

    ts = [t for t in veri.tekrarlari_yukle(1) if t.kamera == "cam1" and t.yonelim == 0]
    ozl = deney1.ozellik_tablosu(ts)
    monkeypatch.setattr(deney1, "aci_bandi_modeli", kaydet)
    deney1.genel_puanlar(ts, ozl)
    dogru_say = {g[0]: sum(t.dogru for t in grup) for g, grup in veri.gruplara_ayir(ts).items()}
    beklenen = [sum(v for vid, v in dogru_say.items() if vid != g[0]) for g in deney1._cekimler(ts)]
    assert len(beklenen) >= 2 and gorulen == beklenen
