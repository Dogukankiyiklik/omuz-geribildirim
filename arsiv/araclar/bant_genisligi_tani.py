"""
Tanı aracı (Adım 6, kullanıcının canlı denemesi sonrası): uygulama profilindeki bant genişliği (τ),
veri setindeki kişilerin aynı yöntemle kurulmuş bantlarıyla karşılaştırılır.

Soru: Kullanıcının kalibrasyon tekrarları çok tekdüze olduğu için bandı veri setine göre dar mı?
(τ, kalibrasyon tekrarları arasındaki yayılımla orantılıdır; dar bant küçük sapmalarda büyük z verir.)

Veri seti tarafı: Ex1, önden görüş (|görüş| ≤ 20°), her (video, kamera, yönelim) grubunun ilk 6 doğru tekrarı
(uygulamanın varsayılan kalibrasyon sayısı), cekirdek.degerlendirici.Profil ile. Hiçbir sabit ayarlanmaz.
Ölçü: her ölçüt için geçerli hücrelerdeki τ'nun medyanı.

    python -m araclar.bant_genisligi_tani --profil profiller/dogukan.npz
Çıktı: sonuclar/bant_genisligi/ham.csv, ozet.csv
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

from cekirdek import degerlendirici as dg
from cekirdek import veri
from cekirdek.konsol import utf8_cikti

KLASOR = veri.KOK / "sonuclar" / "bant_genisligi"
N_KALIBRASYON = 6


def tau_medyanlari(profil: dg.Profil) -> dict[str, float]:
    m = profil.model
    cikti = {}
    for k in dg.OLCUTLER:
        t = np.asarray(m.tau[k])[np.asarray(m.gecerli, bool)]
        t = t[np.isfinite(t)]
        cikti[k] = float(np.median(t)) if len(t) else np.nan
    return cikti


def profil_oku(yol) -> dg.Profil:
    v = np.load(yol)
    e = float(v["en_boy"])
    f = [dg.tekrar_ozellikleri(v[f"tekrar{i}"], slice(int(p), None), e)[0] for i, p in enumerate(v["paylar"])]
    return dg.Profil(f)


def main():
    utf8_cikti()
    ap = argparse.ArgumentParser()
    ap.add_argument("--profil", nargs="+", required=True)
    args = ap.parse_args()

    satir = []
    tekrarlar = veri.tekrarlari_yukle(1)
    for (video, kamera, yonelim), grup in veri.gruplara_ayir(tekrarlar).items():
        if abs(veri.gorus_acisi(kamera, yonelim)) > 20:
            continue
        dogru = sorted([t for t in grup if t.dogru], key=lambda t: t.tekrar_no)[:N_KALIBRASYON]
        if len(dogru) < 5:
            continue
        f = [dg.tekrar_ozellikleri(t.dizi, slice(t.etiket_bas, t.etiket_son), veri.EN_BOY)[0] for t in dogru]
        satir.append({"kaynak": "veri_seti", "kim": f"{video}|{kamera}|{yonelim}", "n": len(f),
                      **tau_medyanlari(dg.Profil(f))})
    for yol in args.profil:
        p = profil_oku(yol)
        satir.append({"kaynak": "uygulama", "kim": str(yol), "n": len(p.kalibrasyon_f), **tau_medyanlari(p)})
    ham = pd.DataFrame(satir)
    KLASOR.mkdir(parents=True, exist_ok=True)
    ham.to_csv(KLASOR / "ham.csv", index=False)

    vs = ham[ham.kaynak == "veri_seti"]
    oz = []
    for k in dg.OLCUTLER:
        r = {"olcut": k, "veri_seti_grup": len(vs), "veri_seti_medyan": vs[k].median(),
             "veri_seti_en_kucuk": vs[k].min(), "veri_seti_en_buyuk": vs[k].max()}
        for _, u in ham[ham.kaynak == "uygulama"].iterrows():
            r[f"{u.kim}"] = u[k]
            r[f"{u.kim} / veri_seti_medyan"] = u[k] / vs[k].median()
            r[f"{u.kim} altinda kalan veri_seti grubu"] = int((vs[k] < u[k]).sum())
        oz.append(r)
    oz = pd.DataFrame(oz)
    oz.to_csv(KLASOR / "ozet.csv", index=False)
    with pd.option_context("display.width", 250, "display.max_columns", 20):
        print(oz.round(4).to_string(index=False))


if __name__ == "__main__":
    main()
