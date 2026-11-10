"""Kendi kayıt betiği (deneyler/kendi_kayit.py): sıra, etiket okuma, eşleştirme ve önceden belirlenen metrikler."""
import pandas as pd
import pytest

from cekirdek import hata_turu as ht
from deneyler import kendi_kayit as kk


def test_sira_protokole_uyuyor_ve_tekrarlanabilir():
    a, b = kk.sira_uret(0), kk.sira_uret(0)
    pd.testing.assert_frame_equal(a, b)
    assert len(a) == 21
    sayim = a.groupby(["etiket", "not"]).size().to_dict()
    assert sayim == {(e, n): adet for e, n, adet in kk.PROTOKOL}
    assert not kk.sira_uret(1).etiket.equals(a.etiket)


def test_etiket_okuma_denetimleri(tmp_path):
    y = tmp_path / "e.csv"
    y.write_text("tekrar_no,etiket,not\n1,dogru,\n2,Omuz,\n3,dogru,hizli\n", encoding="utf-8")
    df = kk.etiketleri_oku(y)
    assert list(df.etiket) == ["dogru", "omuz", "dogru"] and df["not"].iloc[2] == "hizli"
    y.write_text("tekrar_no,etiket,not\n1,omuz,bakis\n", encoding="utf-8")
    with pytest.raises(SystemExit):
        kk.etiketleri_oku(y)                   # bakış notu yalnızca doğru tekrarda
    y.write_text("tekrar_no,etiket,not\n1,dogru,\n3,dogru,\n", encoding="utf-8")
    with pytest.raises(SystemExit):
        kk.etiketleri_oku(y)                   # numara atlanmış
    y.write_text("tekrar_no,etiket\n1,silkme\n", encoding="utf-8")
    with pytest.raises(SystemExit):
        kk.etiketleri_oku(y)                   # bilinmeyen etiket


def test_sablon_uzerine_yazmaz(tmp_path):
    y = tmp_path / "etiketler.csv"
    kk.sablon_yaz(y, 0)
    assert len(kk.etiketleri_oku(y)) == 21
    with pytest.raises(SystemExit):
        kk.sablon_yaz(y, 0)


def test_eslestirme_sira_ya_da_dosya(tmp_path):
    et = pd.DataFrame({"tekrar_no": [1, 2, 3]})
    assert kk.eslestir(3, et) == {1: 1, 2: 2, 3: 3}
    assert kk.eslestir(4, et) == {}            # sayı tutmuyor: betik durur
    y = tmp_path / "es.csv"
    y.write_text("ayrilan,tekrar_no\n1,1\n3,2\n4,3\n", encoding="utf-8")
    assert kk.eslestir(4, et, y) == {1: 1, 3: 2, 4: 3}


def _df(satirlar):
    df = pd.DataFrame(satirlar, columns=["etiket", "not", "cikarilan", "hiz_notu"])
    df["hata"] = df.etiket.map(kk.ETIKETLER)
    df["grup"] = [kk.GRUPLAR["normal"] if e == "dogru" and not n else kk.GRUPLAR.get(n, "hatalı")
                  for e, n in zip(df.etiket, df["not"])]
    df["cikarilan_uzman"] = df.cikarilan
    df["kamera_uyarisi"] = 0
    df["sol_kol_notu"] = 0
    L = df.cikarilan.map(kk._liste)
    df["ilk_soylenen"] = [l[0] if l else ht.DOGRU for l in L]
    return df


def test_metrikler():
    O, B = "ERR_ELEVATED_SHOULDER", "ERR_HEAD_TO_SIDE"
    df = _df([("omuz", "", O, 0),                  # katı ✓
              ("omuz", "", f"{B}|{O}", 0),         # katı ✗, ilk iki ✓
              ("bas", "", "", 0),                  # olumlu cümle
              ("dogru", "", "", 0), ("dogru", "", B, 0),
              ("dogru", "bakis", B, 0), ("dogru", "hizli", "", 1), ("dogru", "hizli", "", 0)])
    oz = kk.ozet_tablosu(df).set_index(["metrik", "grup"])["kaçta kaç"]
    assert oz[("katı: cümledeki ilk hata = etiket", "hatalı (hepsi)")] == "1/3"
    assert oz[("ilk iki: etiket cümlede söylendi", "hatalı (hepsi)")] == "2/3"
    assert oz[("olumlu cümle (hiç hata söylenmedi)", "hatalı (hepsi)")] == "1/3"
    assert oz[("gereksiz uyarı (cümlede en az bir hata)", "doğru (normal)")] == "1/2"
    assert oz[("gereksiz uyarı (cümlede en az bir hata)", "doğru, bakış")] == "1/1"
    assert oz[("gereksiz uyarı (cümlede en az bir hata)", "doğru, hızlı")] == "0/2"
    assert oz[("hız notu çıktı", "doğru, hızlı")] == "1/2"
    assert oz[("hız notu çıktı", "doğru (normal)")] == "0/2"
    k = kk.karisiklik(df).set_index("gerçek etiket")
    assert k.loc["omuz", "omuz"] == 1 and k.loc["omuz", "baş"] == 1 and k.loc["doğru", "baş"] == 2
