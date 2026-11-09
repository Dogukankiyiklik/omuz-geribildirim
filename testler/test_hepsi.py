"""deneyler/hepsi.py karşılaştırma fonksiyonları (Karar 37); deney çalıştırmaz."""
import json

import pandas as pd

from deneyler import hepsi


def _yaz(p, df):
    df.to_csv(p, index=False, encoding="utf-8-sig")


def test_csv_ayni_ve_farkli(tmp_path):
    a = pd.DataFrame({"kisi": ["Honza", "Mima"], "auc": [0.91, 0.85], "not": ["", "x"]})
    _yaz(tmp_path / "a.csv", a)
    _yaz(tmp_path / "b.csv", a)
    assert hepsi.csv_karsilastir(tmp_path / "a.csv", tmp_path / "b.csv", 1e-9)["durum"] == "aynı"
    b = a.copy()
    b.loc[1, "auc"] = 0.8501
    _yaz(tmp_path / "b.csv", b)
    r = hepsi.csv_karsilastir(tmp_path / "a.csv", tmp_path / "b.csv", 1e-9)
    assert r["durum"] == "farklı" and abs(r["en büyük fark"] - 1e-4) < 1e-9
    assert hepsi.csv_karsilastir(tmp_path / "a.csv", tmp_path / "b.csv", 1e-3)["durum"] == "aynı"
    b = a.copy()
    b.loc[0, "kisi"] = "Petra"
    _yaz(tmp_path / "b.csv", b)
    assert hepsi.csv_karsilastir(tmp_path / "a.csv", tmp_path / "b.csv", 1e-9)["durum"] == "farklı"
    _yaz(tmp_path / "b.csv", a.iloc[:1])
    assert hepsi.csv_karsilastir(tmp_path / "a.csv", tmp_path / "b.csv", 1e-9)["durum"] == "farklı"


def test_json_tarih_ve_bilgi_yok_sayilir(tmp_path):
    (tmp_path / "a.json").write_text(json.dumps({"esik": 1.9, "tarih": "2026-11-07", "bilgi": {"git": "abc"}}))
    (tmp_path / "b.json").write_text(json.dumps({"esik": 1.9, "tarih": "2026-11-08", "bilgi": {"git": "def"}}))
    assert hepsi.json_karsilastir(tmp_path / "a.json", tmp_path / "b.json", 1e-9)["durum"] == "aynı"
    (tmp_path / "b.json").write_text(json.dumps({"esik": 2.0, "tarih": "x", "bilgi": {}}))
    assert hepsi.json_karsilastir(tmp_path / "a.json", tmp_path / "b.json", 1e-9)["durum"] == "farklı"


def test_karsilastir_eksik_ve_yeni(tmp_path):
    yeni, eski = tmp_path / "yeni", tmp_path / "eski"
    for k in (yeni, eski):
        (k / "sonuclar" / "d").mkdir(parents=True)
    df = pd.DataFrame({"x": [1.0]})
    _yaz(yeni / "sonuclar" / "d" / "ortak.csv", df)
    _yaz(eski / "sonuclar" / "d" / "ortak.csv", df)
    _yaz(yeni / "sonuclar" / "d" / "yalniz_yeni.csv", df)
    _yaz(eski / "sonuclar" / "d" / "yalniz_eski.csv", df)
    r = hepsi.karsilastir(yeni, [("d", [], ["d"], [])], 1e-9, kayitli_kok=eski).set_index("dosya").durum
    assert r["ortak.csv"] == "aynı" and r["yalniz_yeni.csv"] == "yeni" and r["yalniz_eski.csv"] == "üretilmedi"


def test_adim_sirasi_karar37():
    adlar = [a[0] for a in hepsi.ADIMLAR]
    assert adlar[:12] == ["deney1", "deney1_v2", "deney1b", "deney1c", "deney2", "ex7", "deney3", "deney3_saglam",
                          "tekrar_ayirma", "kamera_acisi", "hiz_esigi", "kural_disa_aktar"]
    assert adlar.index("deney2") < adlar.index("deney3") < adlar.index("kural_disa_aktar")


def test_karar53_onbellekli_adimlar():
    ad = {a.ad: a for a in hepsi.ADIMLAR}
    sira = [a.ad for a in hepsi.ADIMLAR]
    assert sira[-5:] == ["siluet", "deney4_orneklem", "deney4", "deney4_kaldirma", "kendi_kayit"]
    # bağımlılıklar: siluet deney1_v2'den, deney4 deney3'ten (sağlam), kendi_kayit modeller/*.json'dan sonra
    assert sira.index("deney1_v2") < sira.index("siluet")
    assert sira.index("deney3_saglam") < sira.index("deney4_orneklem") < sira.index("deney4") < sira.index("deney4_kaldirma")
    assert sira.index("kural_disa_aktar") < sira.index("kendi_kayit")
    # ağ / video / segmentasyon yok
    assert "onbellekten" in ad["deney4"].komut and "--yalniz-onbellek" in ad["kendi_kayit"].komut
    assert all(ad[k].kaynak for k in ("siluet", "deney4", "kendi_kayit"))
    assert "kendi_kayit" not in hepsi.LISTELENEN


def test_komutu_doldur(tmp_path):
    k = hepsi.komutu_doldur(["m", "{VERI}/a.MOV", "{PROJE}/b", "{HEDEF}/c"], tmp_path / "h", proje=tmp_path / "p",
                            veri_kok=tmp_path / "v")
    assert k == ["m", (tmp_path / "v").as_posix() + "/a.MOV", (tmp_path / "p").as_posix() + "/b",
                 (tmp_path / "h").as_posix() + "/c"]


def test_dosya_secimi_ve_yok_sayilan_sutun(tmp_path):
    yeni, eski = tmp_path / "yeni", tmp_path / "eski"
    for k in (yeni, eski):
        (k / "sonuclar" / "d").mkdir(parents=True)
    _yaz(yeni / "sonuclar" / "d" / "y.csv", pd.DataFrame({"m": ["a"], "onbellekten": [True]}))
    _yaz(eski / "sonuclar" / "d" / "y.csv", pd.DataFrame({"m": ["a"], "onbellekten": [False]}))
    _yaz(eski / "sonuclar" / "d" / "girdi.csv", pd.DataFrame({"x": [1]}))   # insan girdisi: karşılaştırılmaz
    adim = hepsi.Adim("d", [], ["d"], [], dosyalar={"d": ["y.csv"]}, yok_sutun={"d/y.csv": ["onbellekten"]})
    r = hepsi.karsilastir(yeni, [adim], 1e-9, kayitli_kok=eski)
    assert list(r.dosya) == ["y.csv"] and r.durum.iloc[0] == "aynı"
    adim2 = adim._replace(yok_sutun=None)
    assert hepsi.karsilastir(yeni, [adim2], 1e-9, kayitli_kok=eski).durum.iloc[0] == "farklı"


def test_girdileri_kopyala(tmp_path):
    (tmp_path / "p" / "sonuclar" / "d").mkdir(parents=True)
    (tmp_path / "p" / "sonuclar" / "d" / "e.xlsx").write_bytes(b"x")
    a = hepsi.Adim("d", [], ["d"], [], girdiler=("sonuclar/d/e.xlsx",))
    hepsi.girdileri_kopyala(a, tmp_path / "h", proje=tmp_path / "p")
    assert (tmp_path / "h" / "sonuclar" / "d" / "e.xlsx").read_bytes() == b"x"
    import pytest
    with pytest.raises(FileNotFoundError):
        hepsi.girdileri_kopyala(a._replace(girdiler=("yok.csv",)), tmp_path / "h", proje=tmp_path / "p")


def test_bos_csv(tmp_path):
    (tmp_path / "a.csv").write_text("\r\n", encoding="utf-8-sig")   # sonuclar/siluet/nan_nedenleri.csv gibi
    (tmp_path / "b.csv").write_text("\r\n", encoding="utf-8-sig")
    assert hepsi.csv_karsilastir(tmp_path / "a.csv", tmp_path / "b.csv", 1e-9)["durum"] == "aynı"
    _yaz(tmp_path / "b.csv", pd.DataFrame({"x": [1]}))
    assert hepsi.csv_karsilastir(tmp_path / "a.csv", tmp_path / "b.csv", 1e-9)["durum"] == "farklı"
