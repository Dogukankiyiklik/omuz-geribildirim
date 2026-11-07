"""Deney 4 (Karar 36) testleri: ağ yok (SahteSaglayici), veri gerekmez."""
import json

import numpy as np
import pandas as pd
import pytest

from cekirdek import geribildirim as gb
from cekirdek import hata_turu as ht
from cekirdek import llm
from deneyler import deney4 as d4

OMUZ, BAS, ONE, DIRSEK, KALDIRMA = ("ERR_ELEVATED_SHOULDER", "ERR_HEAD_TO_SIDE", "ERR_ARM_FORWARD",
                                    "ERR_BENT_ARM", "ERR_LOW_ABDUCTION")


def _kod(hata, yon, olcu=None, beklenen=None, ek_olcu=None, ek_beklenen=None, faz=gb.KALDIRIRKEN):
    olcut = {OMUZ: "YENI", BAS: "bas", ONE: "kol_boyu", DIRSEK: "dirsek", KALDIRMA: ht.KALDIRMA}[hata]
    return gb.SapmaKodu(hata, olcut, yon, "belirgin", olcu, beklenen, faz, 0, ek_olcu, ek_beklenen)


KODLAR = [
    _kod(OMUZ, -1, 0.35, 0.42, 12.0, 3.0), _kod(OMUZ, -1, 0.35, 0.42, 4.0, 3.0), _kod(OMUZ, 1, 0.5, 0.42, -9.0, 2.0),
    _kod(BAS, 1, 22.0, 4.0), _kod(BAS, -1, 2.0, 6.0), _kod(ONE, -1, 0.7, 0.9), _kod(ONE, 1, 1.1, 0.9),
    _kod(DIRSEK, -1, 148.0, 176.0), _kod(DIRSEK, 1, 181.0, 170.0), _kod(DIRSEK, -1, 174.0, 176.0),
    _kod(KALDIRMA, 1, 118.0, 166.0, faz=gb.USTTE), _kod(KALDIRMA, -1, 181.0, 166.0, faz=gb.USTTE),
    _kod(KALDIRMA, 1, 165.0, 166.0, faz=gb.USTTE),
]


@pytest.mark.parametrize("k", KODLAR, ids=lambda k: f"{k.hata}{k.yon}")
def test_b_sayilari_hasta_cumlesiyle_ayni(k):
    """B'ye verilen sayılar, A'nın (hasta cümlesinin) söylediği sayılarla aynı küme olmalı."""
    a = gb.hasta_cumlesi(k)
    girdi = d4.b_girdisi([k], 150.0)
    s = girdi["hatalar"][0].get("sayilar")
    a_say = set(d4.sayilar(a))
    if s is None:
        assert not a_say
    else:
        assert a_say <= {float(s["olcu"]), float(s["beklenen"]), float(s["fark"])}
        assert a_say                                           # sayı varsa cümlede de sayı var
        assert s["birim"] == "derece"
    assert not d4.sayi_uydurdu(a, d4.izinli_b(girdi), 0.0)


def test_b_girdisi_dogru_ve_hata_adlari():
    assert d4.b_girdisi([], 151.0) == {"karar": "doğru", "tepe_kol_acisi": 150}
    g = d4.b_girdisi([KODLAR[0], KODLAR[5]], 150.0)
    assert g["karar"] == "hatalı" and [h["hata"] for h in g["hatalar"]] == ["omuz kalkması", "kolun öne kaçması"]
    assert "sayilar" not in g["hatalar"][1]                    # öne kaçmada sayı yok
    assert g["hatalar"][0]["faz"] == "kaldırırken"


def test_sayi_cikarma():
    assert d4.sayilar("Kolunu 120 dereceye kadar kaldırdın; %41'i, oran 0,41 ve 2.5.") == [120, 41, 0.41, 2.5]
    assert d4.sayilar("Yirmi derece") == []                  # yazıyla yazılanlar yakalanmaz (sınırlılık)


def test_izinli_c_yuvarlama_ve_farklar():
    girdi = {"olcutler": {"bas": {"birim": "derece", "hasta": {"en_kucuk": 5.1, "en_buyuk": 23.4, "ortalama": 8.3},
                                  "normal_aralik": {"alt_sinir_en_kucuk": 1.9, "ust_sinir_en_buyuk": 8.8,
                                                    "orta_ortalama": 5.4}}},
             "tepe_kol_acisi": 121.6, "kalibrasyon_tepe_medyani": 165.9}
    izin = d4.izinli_c(girdi)
    assert 23.4 in izin and 23 in izin and 25 in izin            # ham, 1'e ve 5'e yuvarlanmış
    assert any(abs(x - 18.0) < 1e-9 for x in izin)               # 23.4 − 5.4 = 18.0 (aynı ölçüt)
    assert 44 in izin and 45 in izin                             # 165.9 − 121.6 = 44.3
    assert not d4.sayi_uydurdu("Başını yaklaşık 19 derece eğdin.", izin, 1.0)   # 18 ± 1
    assert d4.sayi_uydurdu("Başını 30 derece eğdin.", izin, 1.0)
    # farklı ölçütler arasındaki fark izinli değil
    assert not any(abs(x - (121.6 - 23.4)) < 1e-6 for x in izin)


def test_istemler_ve_istek():
    ist = d4.istemleri_oku()
    for k in d4.LLM_KOSULLARI:
        assert "Üslup kuralları" in ist[k]["sistem"] and "{ortak_uslup}" not in ist[k]["sistem"]
        assert "{girdi}" in ist[k]["kullanici"]
    assert "yeni hata ekleme" in ist["B"]["sistem"] and "Yalnızca verilen sayıları" in ist["B"]["sistem"]
    assert "kendin karar ver" in ist["C"]["sistem"]
    i = d4.istek("B", {"karar": "doğru", "tepe_kol_acisi": 150}, ist, "m", 0)
    assert '"tepe_kol_acisi": 150' in i.kullanici and i.sicaklik == 0.0 and i.dusunme == 0


def test_dusunme_ayari_ve_gemini_govdesi():
    assert d4.dusunme_ayari("gemini-2.5-flash") == 0
    assert d4.dusunme_ayari("gemini-3.5-flash-lite") is None
    assert d4.dusunme_ayari("x", "minimal") == "minimal" and d4.dusunme_ayari("x", "0") == 0
    g = llm.GeminiSaglayici.govde(llm.Istek("k", "m", dusunme=0))
    assert g["generationConfig"]["thinkingConfig"] == {"thinkingBudget": 0}
    g = llm.GeminiSaglayici.govde(llm.Istek("k", "m", dusunme="minimal"))
    assert g["generationConfig"]["thinkingConfig"] == {"thinkingLevel": "minimal"}
    assert "thinkingConfig" not in llm.GeminiSaglayici.govde(llm.Istek("k", "m"))["generationConfig"]
    # düşünme ayarı verilmeyen isteklerin önbellek anahtarı eskisiyle aynı kalır
    assert llm.Istek("k", "m").anahtar("s") != llm.Istek("k", "m", dusunme=0).anahtar("s")


def _girdiler():
    return pd.DataFrame([{"orneklem_no": i, "kisi": k, "hata": h, "ek_hata": "", "gorus": 0, "gorus_grubu": "",
                          "sistem_hatalari": s, "A_metin": "Hareketi doğru yaptın.",
                          "B_girdi": json.dumps({"karar": "doğru", "tepe_kol_acisi": 150, "no": i}),
                          "C_girdi": json.dumps({"olcutler": {}, "tepe_kol_acisi": 150.2,
                                                 "kalibrasyon_tepe_medyani": 160.0, "no": i})}
                         for i, (k, h, s) in enumerate([("P", ht.DOGRU, ""), ("P", OMUZ, OMUZ), ("Q", BAS, BAS)], 1)])


def test_calistir_llm_sahte_ve_onbellek(tmp_path):
    s = llm.SahteSaglayici(lambda i: "Başını yana eğdin. Başını dik tut.")
    ist = llm.LLMIstemcisi(s, llm.Onbellek(tmp_path / "o.jsonl"))
    y, durum = d4.calistir_llm(_girdiler(), ist, "m", 0, d4.istemleri_oku(), yazdir=False)
    assert durum == "tamam" and len(y) == 6 and s.cagri == 6
    ist2 = llm.LLMIstemcisi(s, llm.Onbellek(tmp_path / "o.jsonl"))
    y2, _ = d4.calistir_llm(_girdiler(), ist2, "m", 0, d4.istemleri_oku(), yazdir=False)
    assert s.cagri == 6 and y2.onbellekten.all() and (y2.metin == y.metin).all()


def test_calistir_llm_kalici_hatada_durur():
    sayac = {"n": 0}

    def yanit(i):
        sayac["n"] += 1
        if sayac["n"] == 3:
            raise llm.LLMHatasi("kota")
        return "Doğru tekrar."
    ist = llm.LLMIstemcisi(llm.SahteSaglayici(yanit))
    y, durum = d4.calistir_llm(_girdiler(), ist, "m", 0, d4.istemleri_oku(), yazdir=False)
    assert len(y) == 2 and durum.startswith("durdu")


def test_metrikler_sadakat_uydurma_uslup():
    g = _girdiler()
    y = pd.DataFrame([
        {"orneklem_no": 1, "kosul": "B", "metin": "Hareketi doğru yaptın. Kolun 150 dereceye çıktı."},
        {"orneklem_no": 2, "kosul": "B", "metin": "Sağ omzunu kulağına doğru kaldırdın. Başını da yana eğdin."},
        {"orneklem_no": 3, "kosul": "B", "metin": "Kolunu %20 daha yukarı kaldır."},
        {"orneklem_no": 1, "kosul": "C", "metin": "Kolun 150 dereceye çıktı, harika."},
        {"orneklem_no": 2, "kosul": "C", "metin": "Kolunu 30 derece daha yukarı kaldır."},
        {"orneklem_no": 3, "kosul": "C", "metin": "Başını yana eğdin. Başını dik tut."},
    ])
    u = d4.uzun_tablo(g, y)
    b = d4.metrik_satiri(u[u.kosul == "B"])
    assert b["eklenen hata /100"] == pytest.approx(200 / 3)      # 2: baş eklendi; 3: az kaldırma eklendi
    assert b["atlanan hata /100"] == pytest.approx(100 / 3)      # 3: baş atlandı
    assert b["sadakat: liste = girdi /100"] == pytest.approx(100 / 3)
    assert b["katı: ilk söylenen = birincil /100"] == 50.0       # 2 doğru (omuz), 3 yanlış
    assert b["sayı uydurdu /100"] == pytest.approx(100 / 3)      # %20 izinli değil
    assert b["üslup: %, yüzde, gövde boy /100"] == pytest.approx(100 / 3)
    c = d4.metrik_satiri(u[u.kosul == "C"])
    assert c["sayı uydurdu /100"] == pytest.approx(100 / 3)      # 150 ≈ 150.2 izinli; 30 izinli değil (izinli fark 9.8 → 10)
    a = d4.metrik_satiri(u[u.kosul == "A"])
    assert a["doğrularda gereksiz uyarı /100"] == 0.0 and a["hatalılarda olumlu cümle /100"] == 100.0


def _uzun(n_kisi=5, her_sinif=10):
    rng = np.random.default_rng(0)
    satir, no = [], 0
    for k in [f"K{i}" for i in range(n_kisi)]:
        for h in ht.SINIFLAR:
            for _ in range(her_sinif // n_kisi + 1):
                no += 1
                for kosul in d4.KOSULLAR:
                    satir.append({"orneklem_no": no, "kosul": kosul, "metin": f"{kosul} cümle {no}", "kisi": k,
                                  "hata": h, "cikarilan": h if rng.random() < 0.5 and h != ht.DOGRU else ""})
    return pd.DataFrame(satir)


def test_elle_secim_dengeli_ve_tekrarsiz():
    s = d4.elle_secim(_uzun())
    assert len(s) == 45 and (s.kosul.value_counts() == 15).all()
    assert s.orneklem_no.is_unique                                # bir tekrar en fazla bir kez
    for _, g in s.groupby("kosul"):
        assert g.hata.value_counts().min() >= 2 and g.hata.value_counts().max() <= 3
    assert list(s.sira) == list(range(1, 46))
    assert (d4.elle_secim(_uzun()).orneklem_no == s.orneklem_no).all()   # tohumlu, tekrarlanabilir


def test_elle_uret_ve_degerlendir(tmp_path):
    u = _uzun()
    d4.elle_uret(u, tmp_path)
    f = pd.read_csv(tmp_path / "elle_etiket.csv", encoding="utf-8-sig", keep_default_na=False, dtype=str)
    assert list(f.columns) == ["sira", "cumle", "omuz", "bas", "one_kacma", "dirsek", "az_kaldirma", "not"]
    assert "kosul" not in f.columns and "hata" not in f.columns    # körlemesine
    with pytest.raises(SystemExit):
        d4.elle_uret(u, tmp_path)                                  # üzerine yazmaz
    a = pd.read_csv(tmp_path / "elle_etiket_anahtar.csv", encoding="utf-8-sig", keep_default_na=False, dtype=str)
    ad = {h: n for n, h in d4.ELLE_HATALAR}
    for i, r in a.iterrows():                                     # kullanıcı çıkarıcıyla aynı işaretlesin, biri hariç
        for h in [x for x in r.cikarilan.split("|") if x]:
            f.loc[f.sira == r.sira, ad[h]] = "1"
    f.loc[f.sira == "1", "dirsek"] = "1" if f.loc[f.sira == "1", "dirsek"].iloc[0] == "" else ""
    f.to_csv(tmp_path / "elle_etiket.csv", index=False, encoding="utf-8-sig")
    T = d4.elle_degerlendir(tmp_path)
    assert T["elle_uyum"].set_index("koşul").loc["hepsi", "tam eşleşme"] == 44
    assert len(T["elle_uyusmayan"]) == 1
