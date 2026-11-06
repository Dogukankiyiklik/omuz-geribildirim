"""
Uygulamanın değerlendiricisi (cekirdek/degerlendirici.degerlendir) Deney 3 ile aynı kararı ve cümleyi vermeli.

Deney 3'te doğru bir tekrar, kendisi dışarıda bırakılarak (n−1 doğru tekrar) kurulan modelle değerlendirilir.
Bu, uygulamada o n−1 tekrarla kalibrasyon yapıp tekrarı değerlendirmekle aynı şeydir. Kural, o kişinin
LOSO kuralıdır. Veri ya da Deney 3 çıktısı yoksa test atlanır.
"""
import numpy as np
import pandas as pd
import pytest

from cekirdek import degerlendirici as dg
from cekirdek import veri

CUMLELER = veri.KOK / "sonuclar" / "deney3" / "cumleler.csv"
PUAN = veri.KOK / "sonuclar" / "deney2" / "puanlar.csv"


@pytest.mark.skipif(not (CUMLELER.exists() and PUAN.exists() and veri.ISKELET_ZIP.exists()),
                    reason="veri ya da Deney 3 çıktıları yok")
def test_uygulama_deney3_ile_ayni():
    from deneyler import deney2, deney3
    puan = deney2.puanlari_oku(deney2.CIKTI)["v2"]
    p, kurallar, esikler = deney3.kararlar(puan)
    c = pd.read_csv(CUMLELER, encoding="utf-8-sig", keep_default_na=False)
    tekrarlar = veri.tekrarlari_yukle(1)
    gruplar = veri.gruplara_ayir(tekrarlar)
    rng = np.random.default_rng(0)
    anahtarlar = list(gruplar)
    denetlenen = 0
    for gi in rng.choice(len(anahtarlar), size=8, replace=False):
        grup = gruplar[anahtarlar[gi]]
        dogrular = [t for t in grup if t.dogru]
        t = dogrular[int(rng.integers(len(dogrular)))]
        kisi = t.kisi
        es = esikler[esikler["test kişisi"] == kisi]
        sid = {h: (q1, q2) for h, q1, q2 in zip(es.hata, es["q1 (%33,3)"], es["q2 (%66,7)"])}
        kal = [dg.tekrar_ozellikleri(u.dizi, u.etiketli, veri.EN_BOY)[0] for u in dogrular if u is not t]
        f, gor = dg.tekrar_ozellikleri(t.dizi, t.etiketli, veri.EN_BOY)
        s = dg.degerlendir(dg.Profil(kal), kurallar[kisi], sid, f, gor, sira=t.satir, olcu_surumu="tek_kare")
        r = c[(c.video == t.video) & (c.kamera == t.kamera) & (c.yonelim == t.yonelim) & (c.satir == t.satir)].iloc[0]
        assert s.karar == r.tahmin
        assert s.uzman_ayrintisi == r.uzman_ayrintisi
        assert s.hasta_cumlesi == r.hasta_cumlesi
        denetlenen += 1
    assert denetlenen == 8
