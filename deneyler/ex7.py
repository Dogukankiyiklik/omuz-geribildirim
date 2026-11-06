"""
Adım 4b — Ex7 (omuz ekstansiyonu) üzerinde AYARSIZ doğrulama (PLAN.md, Güncelleme 02 ve 05).

Soru: Ex1'de geliştirilen yöntem, hiçbir sabiti değiştirilmeden başka bir harekette de çalışıyor mu?

Değişmeyen sabitler (Ex1'den): açı bandı 5° kutu, kutu başına en az 3 tekrar, %20 "aralık dışı" bayrağı,
pay hariç, Karar 7 adil model, z ölçeği (IQR + ε, ε = 0,01), T ızgarası. Ex7'de az kaldırma sınıfı
yok; 10° tepe alt sınırı kullanılmıyor (kaldirma=False).

1) Deney 1 (silkme/doğru ve silkme/diğer AUC; v1b ve v2; 5 omuz ölçütü), görüş gruplarına göre.
2) Deney 2 kuralı Ex7 hata türleriyle (eşleme Güncelleme 05'te önceden belirlendi; cekirdek/hata_turu.EX7):
     ERR_ELEVATED_SHOULDER → YENI, ERR_TORSO_FORWARD → govde_egim, ERR_TORSO_ROTATION → govde_donme,
     ERR_BENT_ARM → dirsek, ERR_ARM_TO_SIDE → kol_boyu
   Ölçekleme, yön ve T Ex7'nin içinde kişi bazlı birini-dışarıda-bırak ile; ayar yalnızca eğitim
   kişilerinin çapraz + profil (|görüş| ≥ 30°) tekrarlarıyla (önceden yazılmış uygulama senaryosu).

Kullanım:
    python -m deneyler.ex7                 # birkaç dk
    python -m deneyler.ex7 --bootstrap 0   # hızlı sınama
Çıktı: sonuclar/ex7/
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path

import numpy as np
import pandas as pd

from cekirdek import veri
from cekirdek import hata_turu as ht
from cekirdek.degerlendirme import guven_araligi, karisiklik, kisi_bootstrap, makro_f1, sinif_metrikleri
from cekirdek.konsol import sonuclari_yaz, utf8_cikti
from cekirdek.ozellikler import DENEY1_OLCUTLERI, EX7_OLCUTLERI, ozellikler
from deneyler import deney1_v2, deney2
from deneyler.deney1 import GORUS_GRUPLARI, maskeler
from deneyler.tablolar import CAPRAZ_PROFIL, ONDEN_CAPRAZ, TUMU, _auc, fark_bootstrap, gorus_maskesi

EGZERSIZ = 7
TANIM = ht.EX7
AYAR_GORUSU = CAPRAZ_PROFIL           # önceden yazıldı (Güncelleme 05)
GORUSLER = (CAPRAZ_PROFIL, TUMU, ONDEN_CAPRAZ) + tuple(GORUS_GRUPLARI)
D1_KOSULLAR = ("v1b", "v2")
SISTEMLER = [(b, y) for b in ("v2", "v1b") for y in (True, False)]
ANA_SISTEM = ("v2", True)             # Karar 15
CIKTI = veri.KOK / "sonuclar" / "ex7"


# ---------------------------------------------------------------- 1) Deney 1 (silkme)
def deney1_skorlari(tekrarlar) -> pd.DataFrame:
    ozl = deney1_v2.ozellik_tablosu(tekrarlar)
    return pd.concat([deney1_v2.skor_tablosu(tekrarlar, k, 0, ozl) for k in D1_KOSULLAR], ignore_index=True)


def deney1_auc(df: pd.DataFrame) -> pd.DataFrame:
    satirlar = []
    for kosul, g in df.groupby("kosul", sort=False):
        s, d, o = maskeler(g)
        for k in DENEY1_OLCUTLERI:
            for gorus in GORUSLER:
                m = gorus_maskesi(g, gorus)
                satirlar.append({"koşul": kosul, "ölçüt": k, "görüş": gorus,
                                 "silkme": int((s & m).sum()), "doğru": int((d & m).sum()),
                                 "diğer hatalar": int((o & m).sum()),
                                 "AUC silkme/doğru": _auc(g, s & m, d & m, f"bant_{k}"),
                                 "AUC silkme/diğer": _auc(g, s & m, o & m, f"bant_{k}"),
                                 "E boş (NaN)": int(g.loc[m, f"bant_{k}"].isna().sum())})
    return pd.DataFrame(satirlar)


def deney1_kisi(df: pd.DataFrame) -> pd.DataFrame:
    satirlar = []
    for (kosul, kisi), g in df.groupby(["kosul", "kisi"], sort=False):
        s, d, o = maskeler(g)
        for gorus in (CAPRAZ_PROFIL, TUMU):
            m = gorus_maskesi(g, gorus)
            for k in DENEY1_OLCUTLERI:
                satirlar.append({"koşul": kosul, "görüş": gorus, "ölçüt": k, "kisi": kisi,
                                 "AUC silkme/doğru": _auc(g, s & m, d & m, f"bant_{k}")})
    return pd.DataFrame(satirlar)


def deney1_bootstrap(df: pd.DataFrame, n: int, tohum: int = 1) -> pd.DataFrame:
    """v2 ve v1b YENI / M33 AUC'si için kişi bazlı bootstrap %95 GA + v2 − v1b farkları."""
    anahtar = ["video", "kamera", "yonelim", "satir", "kisi", "hata", "ek_hata", "gorus"]
    genis = df.set_index(anahtar + ["kosul"])[[f"bant_{k}" for k in ("YENI", "M33")]].unstack("kosul")
    genis.columns = [f"{a}_{b}" for a, b in genis.columns]
    genis = genis.reset_index()

    def istatistik(b):
        s, d, o = maskeler(b)
        c = {}
        for gorus in (CAPRAZ_PROFIL, TUMU):
            m = gorus_maskesi(b, gorus)
            for ayrim, neg in (("silkme/doğru", d), ("silkme/diğer", o)):
                for k in ("YENI", "M33"):
                    for kosul in D1_KOSULLAR:
                        c[f"{gorus}|{ayrim}|{k}|{kosul}"] = _auc(b, s & m, neg & m, f"bant_{k}_{kosul}")
        return c

    nokta = istatistik(genis)
    bs = kisi_bootstrap(genis, istatistik, n=n, tohum=tohum)
    satirlar = []
    for c in bs.columns:
        alt, ust = guven_araligi(bs[c])
        gorus, ayrim, k, kosul = c.split("|")
        satirlar.append({"görüş": gorus, "ayrım": ayrim, "ölçüt": k, "koşul": kosul, "AUC": nokta[c],
                         "GA %2,5": alt, "GA %97,5": ust})
    farklar = fark_bootstrap(df, "kosul", [("YENI", "v2", "v1b"), ("M33", "v2", "v1b")], n=n, tohum=tohum,
                             ayrimlar=("silkme/doğru", "silkme/diğer"), gorusler=(CAPRAZ_PROFIL, TUMU))
    return pd.DataFrame(satirlar), farklar


# ---------------------------------------------------------------- 2) Deney 2 (hata türü)
def deney2_puanlari(tekrarlar) -> dict[str, pd.DataFrame]:
    ozl = {id(t): ozellikler(t.dizi, EX7_OLCUTLERI) for t in tekrarlar}
    return {b: deney2.puan_tablosu(tekrarlar, b, ozl, olcutler=EX7_OLCUTLERI, kaldirma=False) for b in ("v2", "v1b")}


def deney2_tablolari(tahminler: dict, kurallar: dict, puanlar: dict, bootstrap_n: int) -> dict:
    sin = TANIM.siniflar
    ozet, ilk2, temel, sinif, kisi, kar = [], [], [], [], [], {}
    for (bant, yonlu), p in tahminler.items():
        ad = deney2.sistem_adi(bant, yonlu)
        for gorus in GORUSLER:
            g = p[gorus_maskesi(p, gorus)]
            ozet.append({"sistem": ad, "görüş": gorus, **deney2.ozet_satiri(g, sin)})
            ilk2.append({"sistem": ad, "görüş": gorus, **deney2.ilk_iki_satiri(g)})
            o = ozet[-1]
            temel.append({"sistem": ad, "görüş": gorus, "yöntem": "temel çizgi: tek toplam hata (doğru/yanlış)",
                          **deney2.temel_satiri(g)})
            temel.append({"sistem": ad, "görüş": gorus, "yöntem": "6 sınıflı karar kuralı",
                          **{k: o[k] for k in ("tekrar", "hatalı tekrar", "ikili doğruluk",
                                               "duyarlılık (hatalıyı yakalama)", "özgüllük (doğruya doğru deme)",
                                               "dengeli doğruluk", "hatalılarda tür doğru /100 (katı)",
                                               "makro-F1 (katı)")}})
        for gorus in (CAPRAZ_PROFIL, TUMU):
            g = p[gorus_maskesi(p, gorus)]
            s = sinif_metrikleri(g.hata, g.tahmin, sin)
            s.insert(0, "görüş", gorus)
            s.insert(0, "sistem", ad)
            sinif.append(s)
            kar[(ad, gorus)] = karisiklik(g.hata, g.tahmin, sin)
            for k, gk in g.groupby("kisi"):
                h = gk.hata != ht.DOGRU
                kisi.append({"sistem": ad, "görüş": gorus, "kisi": k,
                             "makro-F1 (katı)": makro_f1(gk.hata, gk.tahmin, sin),
                             "hatalılarda tür doğru /100 (katı)": 100 * float((gk.tahmin == gk.hata)[h].mean()),
                             "hatalılarda 'doğru' dedi /100": 100 * float((gk.tahmin == ht.DOGRU)[h].mean()),
                             "doğrularda 'doğru' dedi /100": 100 * float((gk.tahmin == ht.DOGRU)[~h].mean())})
    T = {"d2_ozet": pd.DataFrame(ozet), "d2_ilk_iki": pd.DataFrame(ilk2), "d2_temel_cizgi": pd.DataFrame(temel),
         "d2_siniflar": pd.concat(sinif, ignore_index=True), "d2_kisi": pd.DataFrame(kisi),
         "d2_esikler": pd.concat([k.assign(sistem=deney2.sistem_adi(*s)) for s, k in kurallar.items()],
                                 ignore_index=True),
         "d2_kapsam": kapsam_tablosu(puanlar["v2"])}
    for (ad, gorus), m in kar.items():
        mm = m.copy()
        mm.index = [f"gerçek: {ht.KISA_AD[c]}" for c in mm.index]
        mm.columns = [f"tahmin: {ht.KISA_AD[c]}" for c in mm.columns]
        T[f"d2_karisiklik_{ad}_{'cp' if gorus == CAPRAZ_PROFIL else 'tum'}"] = mm.reset_index().rename(
            columns={"index": ""})
    if bootstrap_n:
        T["d2_bootstrap"] = deney2_bootstrap(tahminler, bootstrap_n)
    return T


def kapsam_tablosu(p: pd.DataFrame) -> pd.DataFrame:
    """Açı bandı kapsamı ve 'kol normalden yüksek' bayrağı, görüş grubu × gerçek sınıf (betimsel)."""
    satirlar = []
    for gg in GORUS_GRUPLARI:
        g = p[p.gorus_grubu == gg]
        for h in TANIM.siniflar:
            x = g[g.hata == h]
            satirlar.append({"görüş grubu": gg, "gerçek sınıf": ht.KISA_AD[h], "tekrar": len(x),
                             "kapsam ort.": float(x.kapsam.mean()), "aralik_disi oranı": float(x.aralik_disi.mean()),
                             "tepe kol açısı medyan": float(x.tepe_acisi.median()),
                             "E boş (YENI)": int(x[ht.puan_sutunu("YENI", 0)].isna().sum())})
    return pd.DataFrame(satirlar)


def deney2_bootstrap(tahminler: dict, n: int, tohum: int = 1) -> pd.DataFrame:
    anahtar = ["video", "kamera", "yonelim", "satir"]
    taban = None
    for s, p in tahminler.items():
        ad = deney2.sistem_adi(*s)
        q = p.set_index(anahtar)[["kisi", "gorus", "hata", "tahmin"]].rename(columns={"tahmin": ad})
        taban = q if taban is None else taban.join(q[[ad]])
    taban = taban.reset_index()
    adlar = [deney2.sistem_adi(*s) for s in tahminler]
    farklar = [("v2_yonlu", "v1b_yonlu"), ("v2_yonlu", "v2_yonsuz"), ("v2_yonsuz", "v1b_yonsuz")]

    def istatistik(b):
        c = {}
        for gorus in (CAPRAZ_PROFIL, TUMU):
            g = b[gorus_maskesi(b, gorus)]
            h = g.hata != ht.DOGRU
            f1 = {a: makro_f1(g.hata, g[a], TANIM.siniflar) for a in adlar}
            for a in adlar:
                c[f"{gorus}|makro-F1|{a}"] = f1[a]
                c[f"{gorus}|tür doğru/100|{a}"] = 100 * float((g[a][h] == g.hata[h]).mean())
            for x, y in farklar:
                c[f"{gorus}|makro-F1 farkı|{x} − {y}"] = f1[x] - f1[y]
        return c

    nokta = istatistik(taban)
    bs = kisi_bootstrap(taban, istatistik, n=n, tohum=tohum)
    satirlar = []
    for c in bs.columns:
        alt, ust = guven_araligi(bs[c])
        gorus, olcu, ad = c.split("|")
        satirlar.append({"görüş": gorus, "büyüklük": olcu, "sistem / fark": ad, "nokta tahmini": nokta[c],
                         "GA %2,5": alt, "GA %97,5": ust,
                         "GA sıfırı içeriyor": bool(alt <= 0 <= ust) if "farkı" in olcu else ""})
    return pd.DataFrame(satirlar)


# ---------------------------------------------------------------- çalıştır
def calistir(cikti=CIKTI, bootstrap_n=2000, yazdir=True):
    t0 = time.time()
    cikti = Path(cikti)
    cikti.mkdir(parents=True, exist_ok=True)
    tekrarlar = veri.tekrarlari_yukle(EGZERSIZ)
    if yazdir:
        print(f"  Ex7: {len(tekrarlar)} tekrar (3 kamera dahil), {time.time() - t0:.1f} s")
    T = {}
    # 1) Deney 1
    t1 = time.time()
    d1 = deney1_skorlari(tekrarlar)
    T["d1_tekrarlar"] = d1
    T["d1_auc"] = deney1_auc(d1)
    kt = deney1_kisi(d1)
    T["d1_kisi_auc"] = kt.pivot_table(index=["koşul", "görüş", "ölçüt"], columns="kisi", values="AUC silkme/doğru",
                                      sort=False).reset_index()
    if bootstrap_n:
        T["d1_auc_ga"], T["d1_farklar"] = deney1_bootstrap(d1, bootstrap_n)
    if yazdir:
        print(f"  Deney 1 (v1b, v2): {time.time() - t1:.1f} s")
    # 2) Deney 2
    t1 = time.time()
    puanlar = deney2_puanlari(tekrarlar)
    tahminler, kurallar = {}, {}
    for bant, yonlu in SISTEMLER:
        tahminler[(bant, yonlu)], kurallar[(bant, yonlu)] = deney2.loso(puanlar[bant], yonlu, TANIM, AYAR_GORUSU)
    T.update(deney2_tablolari(tahminler, kurallar, puanlar, bootstrap_n))
    T["d2_puanlar"] = pd.concat(puanlar.values(), ignore_index=True)
    T["d2_tahminler"] = pd.concat([p.assign(sistem=deney2.sistem_adi(*s)) for s, p in tahminler.items()],
                                  ignore_index=True)
    if yazdir:
        print(f"  Deney 2 (4 sistem): {time.time() - t1:.1f} s")
    T["ozet"] = ozet_tablosu(T)
    sonuclari_yaz(T, cikti)
    for (ad, gorus), ek in (((deney2.sistem_adi(*ANA_SISTEM), CAPRAZ_PROFIL), "cp"),
                            ((deney2.sistem_adi(*ANA_SISTEM), TUMU), "tum")):
        m = karisiklik(*_gercek_tahmin(tahminler[ANA_SISTEM], gorus), TANIM.siniflar)
        deney2.karisiklik_sekli(m, f"Ex7 · Deney 2 · {ad} · {gorus} · katı", cikti / f"d2_karisiklik_{ad}_{ek}.png")
    if yazdir:
        yazdir_ozet(T)
        print(f"\nSüre: {time.time() - t0:.1f} s · Çıktı: {cikti}")
    return T


def _gercek_tahmin(p, gorus):
    g = p[gorus_maskesi(p, gorus)]
    return g.hata, g.tahmin


def ozet_tablosu(T: dict) -> pd.DataFrame:
    """Tek bakışta: Deney 1 (v2/v1b, YENI) ve Deney 2 (4 sistem) ana sayıları, çapraz+profil ve tüm görüşler."""
    satirlar = []
    a = T["d1_auc"]
    for kosul in D1_KOSULLAR:
        for gorus in (CAPRAZ_PROFIL, TUMU):
            r = a[(a["koşul"] == kosul) & (a["ölçüt"] == "YENI") & (a["görüş"] == gorus)].iloc[0]
            satirlar.append({"deney": "Deney 1 (silkme, YENI)", "sistem": kosul, "görüş": gorus,
                             "büyüklük": "AUC silkme/doğru", "değer": r["AUC silkme/doğru"]})
            satirlar.append({"deney": "Deney 1 (silkme, YENI)", "sistem": kosul, "görüş": gorus,
                             "büyüklük": "AUC silkme/diğer", "değer": r["AUC silkme/diğer"]})
    o = T["d2_ozet"]
    for _, r in o[o["görüş"].isin([CAPRAZ_PROFIL, TUMU])].iterrows():
        for b in ("makro-F1 (katı)", "hatalılarda tür doğru /100 (katı)", "hatalılarda 'doğru' dedi /100",
                  "özgüllük (doğruya doğru deme)"):
            satirlar.append({"deney": "Deney 2 (hata türü)", "sistem": r["sistem"], "görüş": r["görüş"],
                             "büyüklük": b, "değer": r[b]})
    return pd.DataFrame(satirlar)


def yazdir_ozet(T):
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 40)
    print("\n0) Özet:")
    print(T["ozet"].round(3).to_string(index=False))
    a = T["d1_auc"]
    print("\n1) Deney 1 — AUC (YENI ve M33):")
    print(a[a["ölçüt"].isin(["YENI", "M33"])].round(3).to_string(index=False))
    print("\n1b) Deney 1 — kişi bazlı AUC silkme/doğru (YENI):")
    k = T["d1_kisi_auc"]
    print(k[k["ölçüt"] == "YENI"].round(3).to_string(index=False))
    if "d1_auc_ga" in T:
        print("\n1c) Deney 1 — kişi bazlı bootstrap %95 GA:")
        print(T["d1_auc_ga"].round(3).to_string(index=False))
        print(T["d1_farklar"][["görüş", "ayrım", "ölçüt", "fark", "nokta tahmini", "GA %2,5", "GA %97,5",
                               "GA sıfırı içeriyor"]].round(3).to_string(index=False))
    o = T["d2_ozet"]
    print("\n2) Deney 2 — özet:")
    sut = ["sistem", "görüş", "tekrar", "hatalı tekrar", "makro-F1 (katı)", "makro-F1 (esnek)",
           "dengeli doğruluk", "hatalılarda tür doğru /100 (katı)", "hatalılarda 'doğru' dedi /100",
           "özgüllük (doğruya doğru deme)"]
    print(o[sut].round(3).to_string(index=False))
    print("\n2b) İlk iki:")
    i = T["d2_ilk_iki"]
    print(i[i["görüş"].isin([CAPRAZ_PROFIL, TUMU])].round(2).to_string(index=False))
    print("\n2c) Sınıf başına (v2 yönlü):")
    s = T["d2_siniflar"]
    print(s[s.sistem == deney2.sistem_adi(*ANA_SISTEM)].round(3).to_string(index=False))
    print("\n2d) Karışıklık (v2 yönlü, çapraz+profil):")
    print(T[f"d2_karisiklik_{deney2.sistem_adi(*ANA_SISTEM)}_cp"].to_string(index=False))
    print("\n2e) Seçilen eşikler ve yönler (her satır bir test kişisi; ayar diğer 4 kişide):")
    e = T["d2_esikler"]
    print(e[["sistem", "test kişisi", "T", "eğitim makro-F1"] + [c for c in e.columns if c.startswith("yön ")]]
          .round(3).to_string(index=False))
    print("\n2f) Kişi bazlı (çapraz+profil):")
    k = T["d2_kisi"]
    print(k[k["görüş"] == CAPRAZ_PROFIL].round(3).to_string(index=False))
    print("\n2g) Açı bandı kapsamı (v2):")
    print(T["d2_kapsam"].round(3).to_string(index=False))
    if "d2_bootstrap" in T:
        print("\n2h) Deney 2 — kişi bazlı bootstrap %95 GA:")
        print(T["d2_bootstrap"].round(3).to_string(index=False))


def main():
    ap = argparse.ArgumentParser(description="Adım 4b: Ex7'de ayarsız doğrulama")
    ap.add_argument("--cikti", default=str(CIKTI))
    ap.add_argument("--bootstrap", type=int, default=2000)
    args = ap.parse_args()
    utf8_cikti()
    print("Adım 4b — Ex7 (omuz ekstansiyonu), ayarsız doğrulama")
    calistir(args.cikti, args.bootstrap)


if __name__ == "__main__":
    main()
