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
    assert adlar == ["deney1", "deney1_v2", "deney1b", "deney1c", "deney2", "ex7", "deney3", "deney3_saglam",
                     "tekrar_ayirma", "kamera_acisi", "hiz_esigi", "kural_disa_aktar"]
    assert adlar.index("deney2") < adlar.index("deney3") < adlar.index("kural_disa_aktar")
