"""
Deney 1 v2 — yöntem düzeltmelerinin ablasyonu (Adım 2c, arsiv/ilerleme/GUNCELLEME_02.md).

Koşullar (birikimli; hepsinde 5 omuz ölçütü, yönsüz bant):
  v1  : zaman bandı (M39), pay dahil, tek rastgele referans  = Deney 1 aynen (temel çizgi)
  v1a : zaman bandı, PAY HARİÇ, tek rastgele referans
  v1b : zaman bandı, pay hariç, ÇOKLU referans (sırayla hepsi, E'lerin ortalaması)
  v2  : AÇI BANDI (kol açısına koşullu), pay hariç, referans yok

Adillik (her koşulda): doğru tekrar birini-dışarıda-bırak; hatalı tekrar aynı sayıda (n−1) doğru tekrarla.
  v1, v1a: dışarıda bırakılan doğru tekrar rastgele (tohum) — Deney 1'e sadık.
  v1b, v2: her doğru tekrar sırayla dışarıda, n model, E'lerin ortalaması (Güncelleme 03, Karar 7) →
           E tamamen deterministik.
"Pay hariç": ölçütler tüm dizide hesaplanır (dinlenme tabanı = ilk 8 kare, pay dahil), sonra
DTW / bant / E için yalnızca etiketli kareler (first_frame … last_frame) kullanılır (Karar 3).

Kullanım:
    python -m deneyler.deney1_v2                 # birkaç dk (tohum duyarlılığı için ikinci tohum dahil)
    python -m deneyler.deney1_v2 --sekilsiz      # örnek şekiller üretilmez
Çıktı: sonuclar/deney1_v2/
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path

import numpy as np
import pandas as pd

from cekirdek import veri
from cekirdek.adil_model import adil_ortalama_hata, birini_disarida_alt_kumeler
from cekirdek.aci_bandi import aci_bandi_hatasi, aci_bandi_modeli
from cekirdek.bant import bant_hatasi, bant_modeli, coklu_referans_hatasi
from cekirdek.degerlendirme import auc, guven_araligi, kisi_bootstrap, psi
from cekirdek.konsol import sonuclari_yaz, utf8_cikti
from cekirdek.ozellikler import DENEY1_OLCUTLERI, ozellikler
from deneyler.deney1 import GORUS_GRUPLARI, SILKME, maskeler

OLCUTLER = DENEY1_OLCUTLERI
KOSULLAR = ["v1", "v1a", "v1b", "v2"]
# Güncelleme 03, Karar 7: bu koşullarda hatalı tekrarın E'si tüm (n−1)'li modellerin ortalaması
# (rastgele "atla" yok → E tamamen deterministik). v1 ve v1a Deney 1'e sadık kalır (tek rastgele).
ADIL_ORTALAMA = ("v1b", "v2")
KOSUL_ACIKLAMA = {
    "v1": "zaman bandı, pay dahil, tek rastgele referans (Deney 1)",
    "v1a": "zaman bandı, pay hariç, tek rastgele referans",
    "v1b": "zaman bandı, pay hariç, çoklu referans",
    "v2": "açı bandı, pay hariç, referans yok",
}
CIKTI = veri.KOK / "sonuclar" / "deney1_v2"


def _kes(f: dict, s: slice) -> dict:
    return {k: v[s] for k, v in f.items()}


def ozellik_tablosu(tekrarlar, en_boy=veri.EN_BOY):
    """Her tekrar için tüm dizide ölçütler (bir kez hesaplanır, koşullar arasında paylaşılır)."""
    return {id(t): ozellikler(t.dizi, OLCUTLER, en_boy) for t in tekrarlar}


def degerlendirmeler(tekrarlar, kosul: str, tohum: int = 0, ozl=None):
    """
    Bir koşulda her tekrarın değerlendirmesi. Her tekrar için sözlük üretir:
      t, f (kullanılan kareler), model, digerleri (modeldeki doğru tekrarların Tekrar'ları),
      E, ek (v2: kapsam, aralik_disi, tepe_acisi).
    v1, deneyler.deney1.tekrar_degerlendirmeleri ile aynı rastgele sayı sırasını kullanır.
    """
    if kosul not in KOSULLAR:
        raise ValueError(kosul)
    ozl = ozellik_tablosu(tekrarlar) if ozl is None else ozl
    rng = np.random.default_rng(tohum)
    for _, grup in veri.gruplara_ayir(tekrarlar).items():
        tl = []
        for t in grup:
            f = ozl[id(t)]
            tl.append({"t": t, "f": f if kosul == "v1" else _kes(f, t.etiketli)})
        dogrular = [x for x in tl if x["t"].dogru]
        if len(dogrular) < 3:
            continue
        for x in tl:
            t = x["t"]
            if not t.dogru and kosul in ADIL_ORTALAMA:
                # Karar 7: her doğru tekrar sırayla dışarıda, n model, E'lerin ortalaması.
                yield _adil_ortalama_degerlendirme(x, dogrular, kosul)
                continue
            if t.dogru:
                digerleri = [u for u in dogrular if u is not x]
            else:
                atla = rng.integers(len(dogrular))
                digerleri = [u for i, u in enumerate(dogrular) if i != atla]
            fl = [u["f"] for u in digerleri]
            model, ek = None, {}
            if kosul in ("v1", "v1a"):
                model = bant_modeli(fl, rng, OLCUTLER)
                E = bant_hatasi(model, x["f"], OLCUTLER)
            elif kosul == "v1b":
                E = coklu_referans_hatasi(fl, x["f"], OLCUTLER)
            else:
                model = aci_bandi_modeli(fl, OLCUTLER)
                E, ek = aci_bandi_hatasi(model, x["f"], OLCUTLER)
            yield {"t": t, "f": x["f"], "model": model, "digerleri": [u["t"] for u in digerleri],
                   "digerleri_f": fl, "E": E, "ek": ek, "model_sayisi": 1}


def _adil_ortalama_degerlendirme(x, dogrular, kosul):
    """
    Hatalı tekrar, v1b / v2 (Karar 7). E = n adet (n−1)'li modelin E ortalaması.
    v2 ek bilgileri: kapsam = modellerin ortalaması; aralik_disi = modellerin yarısından fazlasında
    bayrak; tepe_acisi tekrarın kendisinden (modele bağlı değil).
    Görsel araçlar için "model" ilk alt kümenin (1. doğru tekrar dışarıda) modelidir; gösterilen E
    yine ortalamadır ("model_sayisi" > 1 bunu belirtir).
    """
    def hata(alt):
        fl = [u["f"] for u in alt]
        if kosul == "v1b":
            return coklu_referans_hatasi(fl, x["f"], OLCUTLER), {}
        m = aci_bandi_modeli(fl, OLCUTLER)
        E, ek = aci_bandi_hatasi(m, x["f"], OLCUTLER)
        ek["_model"] = m
        return E, ek

    E, sonuclar = adil_ortalama_hata(dogrular, hata, OLCUTLER)
    ekler = [ek for _, ek in sonuclar]
    ek = {}
    if kosul == "v2":
        ek = {"kapsam": float(np.mean([e["kapsam"] for e in ekler])),
              "aralik_disi": bool(np.mean([e["aralik_disi"] for e in ekler]) > 0.5),
              "tepe_acisi": ekler[0]["tepe_acisi"]}
    ilk = birini_disarida_alt_kumeler(dogrular)[0]
    return {"t": x["t"], "f": x["f"], "model": ekler[0].get("_model"),
            "digerleri": [u["t"] for u in dogrular], "digerleri_f": [u["f"] for u in dogrular],
            "model_digerleri_f": [u["f"] for u in ilk],
            "E": E, "ek": ek, "model_sayisi": len(dogrular)}


def skor_tablosu(tekrarlar, kosul, tohum=0, ozl=None) -> pd.DataFrame:
    kayit = []
    for d in degerlendirmeler(tekrarlar, kosul, tohum, ozl):
        t = d["t"]
        r = {"kosul": kosul, "tohum": tohum, "video": t.video, "kisi": t.kisi, "kamera": t.kamera,
             "yonelim": t.yonelim, "tekrar_no": t.tekrar_no, "satir": t.satir, "gorus": t.gorus,
             "hata": t.hata, "ek_hata": t.ek_hata}
        r.update({f"bant_{k}": d["E"][k] for k in OLCUTLER})
        r.update({"kapsam": d["ek"].get("kapsam", np.nan),
                  "aralik_disi": d["ek"].get("aralik_disi", np.nan),
                  "tepe_acisi": d["ek"].get("tepe_acisi", np.nan)})
        kayit.append(r)
    df = pd.DataFrame(kayit)
    df["gorus_grubu"] = pd.Categorical(df.gorus.map(veri.gorus_grubu), categories=GORUS_GRUPLARI)
    return df


# ---------------------------------------------------------------- tablolar
def _auc(df, m_poz, m_neg, c):
    """NaN E'li tekrarlar (v2'de hiç geçerli karesi olmayanlar) AUC'den çıkarılır; sayısı ayrıca raporlanır."""
    v = df[c].notna()
    return auc(df.loc[m_poz & v, c], df.loc[m_neg & v, c])


def kisi_auc(df) -> pd.DataFrame:
    satirlar = []
    for (kosul, kisi), g in df.groupby(["kosul", "kisi"]):
        s, d, _ = maskeler(g)
        for k in OLCUTLER:
            satirlar.append({"kosul": kosul, "ölçüt": k, "kisi": kisi,
                             "AUC silkme/doğru": _auc(g, s, d, f"bant_{k}")})
    return pd.DataFrame(satirlar)


def ozet_tablosu(df, kisi_tablo) -> pd.DataFrame:
    satirlar = []
    for kosul in KOSULLAR:
        g = df[df.kosul == kosul]
        s, d, o = maskeler(g)
        for k in OLCUTLER:
            c = f"bant_{k}"
            r = {"koşul": kosul, "ölçüt": k,
                 "AUC silkme/doğru": _auc(g, s, d, c),
                 "AUC silkme/diğer hatalar": _auc(g, s, o, c)}
            # Karar 6: uygulama senaryosu = önden + çapraz (|görüş| ≤ 60°)
            oc = g.gorus.abs() <= 60
            r["AUC silkme/doğru (önden+çapraz)"] = _auc(g, s & oc, d & oc, c)
            r["AUC silkme/diğer (önden+çapraz)"] = _auc(g, s & oc, o & oc, c)
            for gg in GORUS_GRUPLARI:
                m = g.gorus_grubu == gg
                r[f"AUC {gg}"] = _auc(g, s & m, d & m, c)
            kt = kisi_tablo[(kisi_tablo.kosul == kosul) & (kisi_tablo["ölçüt"] == k)]["AUC silkme/doğru"]
            r["kişi AUC ort."] = kt.mean()
            r["kişi AUC en düşük"] = kt.min()
            r["kişi AUC en yüksek"] = kt.max()
            r["kişi özeti"] = f"{kt.mean():.2f} ({kt.min():.2f}–{kt.max():.2f})".replace(".", ",")
            r["Ψ (M39)"] = psi(g[g[c].notna()], c, SILKME)
            r["E boş (NaN) tekrar"] = int(g[c].isna().sum())
            satirlar.append(r)
    return pd.DataFrame(satirlar)


FARKLAR = [("v2", "v1"), ("v1a", "v1"), ("v1b", "v1a"), ("v2", "v1b")]
# Güncelleme 03: silkme/diğer ayrımı için farklar (açı bandının asıl katkısı burada)
# (ayrım, ölçüt, x, y)
FARKLAR_DIGER = [("silkme/diğer", k, x, y) for k in ("YENI", "M33") for x, y in (("v2", "v1b"), ("v2", "v1"))]
FARKLAR_TUMU = [("silkme/doğru", "YENI", x, y) for x, y in FARKLAR] + FARKLAR_DIGER


def bootstrap_tablosu(df, n=2000, tohum=1, farklar=FARKLAR_TUMU) -> pd.DataFrame:
    """Koşullar arası AUC farkı için kişi bazlı bootstrap %95 GA (eşleştirilmiş: aynı kişiler)."""
    olcutler = sorted({k for _, k, _, _ in farklar})
    genis = df.pivot_table(index=["video", "kamera", "yonelim", "satir", "kisi", "hata", "ek_hata"],
                           columns="kosul", values=[f"bant_{k}" for k in olcutler]).reset_index()
    genis.columns = ["_".join(c for c in col if c) if isinstance(col, tuple) else col for col in genis.columns]

    def istatistik(b):
        s, d, o = maskeler(b)
        neg = {"silkme/doğru": d, "silkme/diğer": o}
        cikti = {}
        for ayrim, k, x, y in farklar:
            a = {kz: _auc(b, s, neg[ayrim], f"bant_{k}_{kz}") for kz in (x, y)}
            cikti[f"{ayrim} · {k}: {x} − {y}"] = a[x] - a[y]
        return cikti

    bs = kisi_bootstrap(genis, istatistik, n=n, tohum=tohum)
    nokta = istatistik(genis)
    satirlar = []
    for c in bs.columns:
        alt, ust = guven_araligi(bs[c])
        satirlar.append({"fark": c, "nokta tahmini": nokta[c], "bootstrap ort.": bs[c].mean(),
                         "GA %2,5": alt, "GA %97,5": ust})
    return pd.DataFrame(satirlar)


def kapsam_tablosu(df) -> pd.DataFrame:
    g = df[df.kosul == "v2"]
    t = g.groupby("hata").agg(tekrar=("kapsam", "size"), kapsam_ort=("kapsam", "mean"),
                              kapsam_medyan=("kapsam", "median"),
                              aralik_disi_orani=("aralik_disi", lambda x: float(np.mean(x.astype(bool)))),
                              E_bos=("bant_YENI", lambda x: int(x.isna().sum())))
    hepsi = pd.DataFrame([{"hata": "HEPSİ", "tekrar": len(g), "kapsam_ort": g.kapsam.mean(),
                           "kapsam_medyan": g.kapsam.median(),
                           "aralik_disi_orani": float(np.mean(g.aralik_disi.astype(bool))),
                           "E_bos": int(g.bant_YENI.isna().sum())}])
    return pd.concat([t.reset_index(), hepsi], ignore_index=True)


def tohum_tablosu(df0, df1, kosullar=("v1", "v1b", "v2")) -> pd.DataFrame:
    """Aynı tekrarın tohum 0 ve tohum 1'deki E farkı: medyan |ΔE| ve |ΔE| > 0,05 oranı."""
    anahtar = ["video", "kamera", "yonelim", "satir"]
    satirlar = []
    for kosul in kosullar:
        a = df0[df0.kosul == kosul].set_index(anahtar)
        b = df1[df1.kosul == kosul].set_index(anahtar).loc[a.index]
        for k in OLCUTLER:
            fark = (a[f"bant_{k}"] - b[f"bant_{k}"]).abs()
            for grup, m in [("hepsi", slice(None)), ("doğru", a.hata == "DOGRU"), ("hatalı", a.hata != "DOGRU")]:
                f = fark[m].dropna()
                satirlar.append({"koşul": kosul, "ölçüt": k, "tekrar grubu": grup, "n": len(f),
                                 "medyan |ΔE|": float(f.median()), "|ΔE| > 0,05 oranı": float((f > 0.05).mean()),
                                 "en büyük |ΔE|": float(f.max())})
    return pd.DataFrame(satirlar)


# ---------------------------------------------------------------- çalıştır
def calistir(tohum=0, cikti=CIKTI, bootstrap_n=2000, tohum_duyarliligi=True, yazdir=True, kaynak="zip"):
    t0 = time.time()
    cikti = Path(cikti)
    cikti.mkdir(parents=True, exist_ok=True)
    tekrarlar = veri.tekrarlari_yukle(1, kaynak=kaynak)
    ozl = ozellik_tablosu(tekrarlar)
    parcalar = []
    for kosul in KOSULLAR:
        t1 = time.time()
        parcalar.append(skor_tablosu(tekrarlar, kosul, tohum, ozl))
        if yazdir:
            print(f"  {kosul:4s} ({KOSUL_ACIKLAMA[kosul]}): {time.time() - t1:.1f} s")
    df = pd.concat(parcalar, ignore_index=True)
    kt = kisi_auc(df)
    ozet = ozet_tablosu(df, kt)
    tablolar = {"tekrarlar": df, "ozet": ozet,
                "kisi_auc": kt.pivot_table(index=["kosul", "ölçüt"], columns="kisi",
                                           values="AUC silkme/doğru").reset_index(),
                "kapsam": kapsam_tablosu(df)}
    if bootstrap_n:
        tablolar["bootstrap"] = bootstrap_tablosu(df, n=bootstrap_n)
    if tohum_duyarliligi:
        t1 = time.time()
        df1 = pd.concat([skor_tablosu(tekrarlar, k, tohum + 1, ozl) for k in ("v1", "v1b", "v2")], ignore_index=True)
        tablolar["tohum"] = tohum_tablosu(df, df1)
        if yazdir:
            print(f"  tohum {tohum + 1} (v1, v1b, v2): {time.time() - t1:.1f} s")
    sonuclari_yaz(tablolar, cikti)
    if yazdir:
        yazdir_ozet(tablolar, df, tohum, bootstrap_n)
        print(f"\nSüre: {time.time() - t0:.1f} s · Çıktı: {cikti}")
    return tablolar


def yazdir_ozet(tablolar, df, tohum, bootstrap_n):
    pd.set_option("display.width", 220)
    pd.set_option("display.max_columns", 30)
    s, d, o = maskeler(df[df.kosul == "v1"])
    print(f"\nTohum: {tohum} · Tekrar sayıları (3 kamera dahil): silkme={s.sum()}, doğru={d.sum()}, diğer hatalar={o.sum()}")
    ozet = tablolar["ozet"]
    print("\n1) Ablasyon tablosu — AUC (koşul × ölçüt):")
    sut = (["koşul", "ölçüt", "AUC silkme/doğru", "AUC silkme/diğer hatalar",
            "AUC silkme/doğru (önden+çapraz)", "AUC silkme/diğer (önden+çapraz)"]
           + [f"AUC {g}" for g in GORUS_GRUPLARI] + ["Ψ (M39)", "E boş (NaN) tekrar"])
    print(ozet[sut].round(3).to_string(index=False))
    print("\n2) Kişi bazlı AUC silkme/doğru:")
    print(tablolar["kisi_auc"].round(3).to_string(index=False))
    print("\n   Özet 'ortalama (en düşük–en yüksek)':")
    for _, r in ozet[ozet["ölçüt"] == "YENI"].iterrows():
        print(f"   {r['koşul']:4s} YENI: {r['kişi özeti']}")
    if "bootstrap" in tablolar:
        print(f"\n3) AUC farkları, kişi bazlı bootstrap ({bootstrap_n} tekrar), %95 GA:")
        for _, r in tablolar["bootstrap"].iterrows():
            print(f"   {r['fark']:32s} {r['nokta tahmini']:+.3f}   GA {r['GA %2,5']:+.3f} – {r['GA %97,5']:+.3f}")
    print("\n4) v2 kapsam ve aralık dışı oranı (hata türüne göre):")
    print(tablolar["kapsam"].round(3).to_string(index=False))
    if "tohum" in tablolar:
        t = tablolar["tohum"]
        print("\n5) Tohum duyarlılığı (YENI; tohum 0 ile 1 arasında aynı tekrarın E farkı):")
        print(t[t["ölçüt"] == "YENI"].round(4).to_string(index=False))


def main():
    ap = argparse.ArgumentParser(description="Deney 1 v2: yöntem düzeltmeleri ablasyonu")
    ap.add_argument("--tohum", type=int, default=0)
    ap.add_argument("--cikti", default=str(CIKTI))
    ap.add_argument("--bootstrap", type=int, default=2000)
    ap.add_argument("--sekilsiz", action="store_true", help="şekilleri üretme")
    args = ap.parse_args()
    utf8_cikti()
    print("Deney 1 v2 — koşullar hesaplanıyor...")
    tablolar = calistir(args.tohum, args.cikti, args.bootstrap)
    if not args.sekilsiz:
        from deneyler import deney1_v2_sekiller
        print("\nŞekiller üretiliyor...")
        deney1_v2_sekiller.hepsi(tablolar, Path(args.cikti), tohum=args.tohum)


if __name__ == "__main__":
    main()
