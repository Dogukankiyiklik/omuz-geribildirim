"""
Deney 1c — zamansal yumuşatma (Adım 3; hocanın P2 önerisi).

Soru: MediaPipe noktalarının kareden kareye titremesini (jitter) filtrelemek, kişiye özel bandın
silkmeyi bulmasını iyileştiriyor mu?

Yöntem:
  - Filtreler (cekirdek/yumusatma.py): One Euro (nedensel, canlı uygulamaya uygun) ve
    Savitzky–Golay (nedensel değil). Noktaların x, y koordinatlarına, ölçütler hesaplanmadan ÖNCE
    uygulanır; kol açısı da yumuşatılmış noktalardan gelir (DTW ve açı kutuları dahil).
  - Bant: kişiye özel, v1b (zaman bandı, çoklu referans) ve v2 (açı bandı); Deney 1 v2 ile aynı kod.
  - Parametre seçimi (CLAUDE.md, birini-dışarıda-bırak): her test kişisi için, her (bant, filtre,
    ölçüt) üçlüsünde, parametre ızgarasından DİĞER 4 KİŞİNİN tekrarlarında (birleşik) AUC
    silkme/doğru'yu (tüm görüşler) en yükseğe çıkaran seçilir; eşitlikte ızgaradaki ilk (en az
    yumuşatan) seçilir. Test kişisinin verisi seçime girmez. Kişiye özel bantta bir tekrarın E'si
    yalnızca o kişinin verisine bağlıdır; bu yüzden her ayar için E bir kez hesaplanır, seçim sonra
    yapılır.
  - Ayrıca: titreme ölçüsü (doğru tekrarlarda omuz/kulak noktasının ikinci farkının RMS'i) ve
    titreme.png şekli.

Kullanım:
    python -m deneyler.deney1c            # ~15–20 dk (21 ayar × 2 bant)
    python -m deneyler.deney1c --hizli    # yalnızca kod denemesi: küçük ızgara (sonuç raporlanmaz)
Çıktı: sonuclar/deney1c/
"""
from __future__ import annotations

import argparse
import itertools
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from cekirdek import veri
from cekirdek.konsol import sonuclari_yaz, utf8_cikti
from cekirdek.ozellikler import ozellikler
from cekirdek.yumusatma import yumusat
from deneyler import deney1_v2 as d2
from deneyler import tablolar as tb
from deneyler.deney1 import maskeler
from deneyler.sekiller import IZGARA, MAVI, METIN, METIN2, TURUNCU, _stil

OLCUTLER = ["YENI", "M33", "M39_F2"]
BANTLAR = ["v1b", "v2"]
CIKTI = veri.KOK / "sonuclar" / "deney1c"

# Parametre ızgarası (önceden sabit; sonuçlara bakılarak değiştirilmez)
IZGARA_ONE_EURO = [{"min_kesim": m, "beta": b} for m, b in itertools.product([0.5, 1.0, 2.0, 4.0], [0.0, 1.0, 10.0])]
IZGARA_SAVGOL = [{"pencere": p, "derece": d} for p, d in itertools.product([5, 9, 15, 21], [2, 3])]
IZGARA_HIZLI = {"one_euro": [{"min_kesim": 1.0, "beta": 1.0}], "savgol": [{"pencere": 9, "derece": 2}]}
FILTRELER = ["one_euro", "savgol"]


def ayar_adi(yontem, p) -> str:
    if yontem == "yok":
        return "yok"
    return yontem + "(" + ", ".join(f"{k}={v:g}" for k, v in p.items()) + ")"


def ayarlar(hizli=False):
    izg = IZGARA_HIZLI if hizli else {"one_euro": IZGARA_ONE_EURO, "savgol": IZGARA_SAVGOL}
    cikti = [("yok", {})]
    for y in FILTRELER:
        cikti += [(y, p) for p in izg[y]]
    return cikti


def ozellik_tablosu(tekrarlar, yontem, param):
    """Yumuşatılmış noktalardan ölçütler (tüm dizi; pay dahil, dinlenme tabanı için)."""
    return {id(t): ozellikler(yumusat(t.dizi, yontem, **param), d2.OLCUTLER) for t in tekrarlar}


def tum_ayar_skorlari(tekrarlar, hizli=False, yazdir=True) -> pd.DataFrame:
    parcalar = []
    liste = ayarlar(hizli)
    for i, (yontem, p) in enumerate(liste, 1):
        t1 = time.time()
        ozl = ozellik_tablosu(tekrarlar, yontem, p)
        for bant in BANTLAR:
            df = d2.skor_tablosu(tekrarlar, bant, 0, ozl).rename(columns={"kosul": "bant"})
            df["yontem"], df["ayar"] = yontem, ayar_adi(yontem, p)
            parcalar.append(df[["bant", "yontem", "ayar"] + tb.TEKRAR_ANAHTARI + ["tekrar_no"]
                               + [f"bant_{k}" for k in OLCUTLER]])
        if yazdir:
            print(f"  [{i:2d}/{len(liste)}] {ayar_adi(yontem, p):40s} {time.time() - t1:5.1f} s", flush=True)
    return pd.concat(parcalar, ignore_index=True)


def _auc_sd(g, c):
    s, d, _ = maskeler(g)
    return tb._auc(g, s, d, c)


def izgara_tablosu(df) -> pd.DataFrame:
    """Her ayar için AUC silkme/doğru: tüm kişiler ve 'kişi hariç' (seçimin gördüğü eğitim AUC'si)."""
    kisiler = sorted(df.kisi.unique())
    satirlar = []
    for (bant, yontem, ayar), g in df.groupby(["bant", "yontem", "ayar"], sort=False):
        for k in OLCUTLER:
            r = {"bant": bant, "yontem": yontem, "ayar": ayar, "ölçüt": k,
                 "AUC silkme/doğru (tüm kişiler)": _auc_sd(g, f"bant_{k}")}
            for kisi in kisiler:
                r[f"eğitim AUC ({kisi} hariç)"] = _auc_sd(g[g.kisi != kisi], f"bant_{k}")
            satirlar.append(r)
    return pd.DataFrame(satirlar)


def secim(izgara: pd.DataFrame, kisiler) -> pd.DataFrame:
    """Birini-dışarıda-bırak parametre seçimi: test kişisi hariç eğitim AUC'si en yüksek ayar."""
    satirlar = []
    for (bant, yontem, k), g in izgara[izgara.yontem != "yok"].groupby(["bant", "yontem", "ölçüt"], sort=False):
        for kisi in kisiler:
            c = f"eğitim AUC ({kisi} hariç)"
            i = int(np.nanargmax(g[c].to_numpy()))  # eşitlikte ilk (ızgara sırası)
            satirlar.append({"bant": bant, "yontem": yontem, "ölçüt": k, "test kişisi": kisi,
                             "seçilen ayar": g.iloc[i]["ayar"], "eğitim AUC": g.iloc[i][c]})
    return pd.DataFrame(satirlar)


def secilmis_tablo(df: pd.DataFrame, sec: pd.DataFrame) -> pd.DataFrame:
    """Her test kişisinin tekrarlarına, o kişi için seçilen ayarın E'si (ölçüt başına ayrı seçim)."""
    parcalar = [df[df.yontem == "yok"].assign(kosul="yumusatmasiz")]
    anahtar = ["bant"] + tb.TEKRAR_ANAHTARI
    for bant in BANTLAR:
        for yontem in FILTRELER:
            taban = df[(df.bant == bant) & (df.yontem == "yok")][anahtar + ["tekrar_no"]].copy()
            for k in OLCUTLER:
                s = sec[(sec.bant == bant) & (sec.yontem == yontem) & (sec["ölçüt"] == k)]
                esle = dict(zip(s["test kişisi"], s["seçilen ayar"]))
                d = df[(df.bant == bant) & (df.yontem == yontem)]
                d = d[d.ayar == d.kisi.map(esle)]
                taban = taban.merge(d[anahtar + [f"bant_{k}"]], on=anahtar, how="left")
            parcalar.append(taban.assign(kosul=yontem, yontem=yontem, ayar="LOSO seçimi"))
    out = pd.concat(parcalar, ignore_index=True)
    out["kosul"] = pd.Categorical(out.kosul, categories=["yumusatmasiz"] + FILTRELER)
    return out.sort_values(["bant", "kosul", "video", "kamera", "yonelim", "satir"]).reset_index(drop=True)


# ---------------------------------------------------------------- titreme
TITREME_EKLEMLERI = {"sağ omuz": 12, "sağ kulak": 8}


def _rms_ikinci_fark(dizi, eklem, en_boy=veri.EN_BOY):
    p = dizi[:, eklem, :2] * np.array([en_boy, 1.0])
    return float(np.sqrt(np.mean(np.sum(np.diff(p, n=2, axis=0) ** 2, axis=1))))


def titreme_tablosu(tekrarlar, ayar_listesi) -> pd.DataFrame:
    """Doğru tekrarlarda, ikinci farkın RMS'i (görüntü yüksekliği birimi / kare²). Titreme ↓ → değer ↓.
    Not: hareketin kendisi de ikinci farka katkı verir; değer saf gürültü değildir."""
    dogrular = [t for t in tekrarlar if t.dogru]
    satirlar = []
    for yontem, p in ayar_listesi:
        r = {"yontem": yontem, "ayar": ayar_adi(yontem, p)}
        for ad, e in TITREME_EKLEMLERI.items():
            v = [_rms_ikinci_fark(yumusat(t.dizi, yontem, **p), e) for t in dogrular]
            r[f"{ad} medyan RMS(Δ²)"] = float(np.median(v))
        satirlar.append(r)
    t = pd.DataFrame(satirlar)
    ham = t.iloc[0]
    for ad in TITREME_EKLEMLERI:
        c = f"{ad} medyan RMS(Δ²)"
        t[f"{ad} ham'a oranı"] = t[c] / ham[c]
    return t


def _ayar_param(ayar: str):
    if ayar == "yok":
        return "yok", {}
    yontem, ic = ayar.split("(")
    p = {}
    for parca in ic.rstrip(")").split(", "):
        k, v = parca.split("=")
        p[k] = int(v) if k in ("pencere", "derece") else float(v)
    return yontem, p


def en_sik_secilen(sec, bant="v2", olcut="YENI"):
    s = sec[(sec.bant == bant) & (sec["ölçüt"] == olcut)]
    return {y: s[s.yontem == y]["seçilen ayar"].mode().iloc[0] for y in FILTRELER}


def titreme_sekli(tekrarlar, sec, klasor: Path, ornek=("ex1_Honza", "cam1", 0)) -> Path:
    """Bir doğru tekrarda sağ omuzun dikey konumu ve YENI: ham ve iki filtre (en sık seçilen ayarlar)."""
    t = next(t for t in tekrarlar if (t.video, t.kamera, t.yonelim) == ornek and t.dogru)
    secilen = en_sik_secilen(sec)
    _stil()
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(9.5, 6.2), sharex=True)
    zaman = np.arange(len(t.dizi)) / 30.0
    seriler = [("ham (MediaPipe)", "yok", {}, METIN, 1.0)]
    renk = {"one_euro": MAVI, "savgol": TURUNCU}
    ad = {"one_euro": "One Euro", "savgol": "Savitzky–Golay"}
    for y in FILTRELER:
        yy, p = _ayar_param(secilen[y])
        seriler.append((f"{ad[y]}: {secilen[y].split('(')[1].rstrip(')')}", yy, p, renk[y], 2.0))
    for etiket, yontem, p, c, lw in seriler:
        d = yumusat(t.dizi, yontem, **p)
        z = 4 if yontem == "yok" else 2  # ham çizgi üstte, filtrelerin altında kaybolmasın
        a1.plot(zaman, -d[:, 12, 1], color=c, lw=lw, label=etiket, zorder=z)
        a2.plot(zaman, ozellikler(d, ["YENI"])["YENI"], color=c, lw=lw, label=etiket, zorder=z)
    s = t.etiketli
    for ax in (a1, a2):
        ax.axvspan(zaman[s.start], zaman[s.stop - 1], color=IZGARA, alpha=0.5, lw=0, zorder=0)
        ax.yaxis.grid(True, color=IZGARA, lw=0.8)
    a1.set_ylabel("sağ omuz yüksekliği\n(−y, görüntü birimi)")
    a2.set_ylabel("YENI: kulak–omuz / gövde")
    a2.set_xlabel("zaman (s) — gri alan: etiketli tekrar (pay hariç)")
    a1.legend(loc="best", frameon=False, fontsize=8)
    a1.set_title(f"{t.video} {t.kamera} yönelim {t.yonelim} tekrar {t.tekrar_no} (doğru tekrar) — "
                 "ham ve yumuşatılmış nokta", loc="left", fontsize=10)
    fig.text(0.01, 0.005, "Filtre ayarları: v2 / YENI için birini-dışarıda-bırak seçiminde en sık seçilen ayar.",
             fontsize=7.5, color=METIN)
    fig.tight_layout(rect=(0, 0.02, 1, 1))
    klasor.mkdir(parents=True, exist_ok=True)
    yol = klasor / "titreme.png"
    fig.savefig(yol)
    plt.close(fig)
    return yol


# ---------------------------------------------------------------- çalıştır
FARKLAR = [(k, y, "yumusatmasiz") for k in OLCUTLER for y in FILTRELER]


def calistir(cikti=CIKTI, bootstrap_n=2000, hizli=False, yazdir=True, sekil=True):
    t0 = time.time()
    cikti = Path(cikti)
    cikti.mkdir(parents=True, exist_ok=True)
    tekrarlar = veri.tekrarlari_yukle(1)
    df = tum_ayar_skorlari(tekrarlar, hizli, yazdir)
    izg = izgara_tablosu(df)
    kisiler = sorted(df.kisi.unique())
    sec = secim(izg, kisiler)
    sl = secilmis_tablo(df, sec)
    tablolar = {"tum_ayarlar": df, "izgara": izg, "secim": sec, "tekrarlar": sl,
                "ozet": tb.auc_ozeti(sl, ["bant", "kosul"], OLCUTLER),
                "kisi_auc": tb.kisi_auc_genis(sl, ["bant", "kosul"], OLCUTLER),
                "titreme": titreme_tablosu(tekrarlar, ayarlar(hizli))}
    if bootstrap_n:
        bs = []
        for bant in BANTLAR:
            b = tb.fark_bootstrap(sl[sl.bant == bant], "kosul", FARKLAR, n=bootstrap_n)
            b.insert(0, "bant", bant)
            bs.append(b)
        tablolar["bootstrap"] = pd.concat(bs, ignore_index=True)
    sonuclari_yaz(tablolar, cikti)
    if sekil:
        print(f"  {titreme_sekli(tekrarlar, sec, cikti)}")
    if yazdir:
        yazdir_ozet(tablolar)
        print(f"\nSüre: {time.time() - t0:.1f} s · Çıktı: {cikti}")
    return tablolar


def yazdir_ozet(tablolar):
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 30)
    print("\n1) AUC — yumuşatmasız / One Euro / Savitzky–Golay (LOSO seçimi):")
    sut = ["bant", "kosul", "ölçüt", "AUC silkme/doğru", f"AUC silkme/doğru ({tb.ONDEN_CAPRAZ})",
           "AUC silkme/diğer", f"AUC silkme/diğer ({tb.ONDEN_CAPRAZ})"] + [f"AUC {g}" for g in d2.GORUS_GRUPLARI] + ["kişi özeti"]
    print(tablolar["ozet"][sut].round(3).to_string(index=False))
    print("\n2) Seçilen ayarlar (test kişisi başına):")
    s = tablolar["secim"]
    print(s.pivot_table(index=["bant", "yontem", "ölçüt"], columns="test kişisi", values="seçilen ayar",
                        aggfunc="first", sort=False).to_string())
    print("\n3) Titreme (doğru tekrarlar, ikinci farkın medyan RMS'i; ham'a oranı):")
    print(tablolar["titreme"].round(4).to_string(index=False))
    if "bootstrap" in tablolar:
        print("\n4) AUC farkı (silkme/doğru), filtre − yumuşatmasız, kişi bazlı bootstrap, %95 GA:")
        for _, r in tablolar["bootstrap"].iterrows():
            print(f"   {r['bant']:4s} {r['görüş']:13s} {r['ölçüt']:7s} {r['fark']:24s} "
                  f"{r['nokta tahmini']:+.3f}   GA {r['GA %2,5']:+.3f} – {r['GA %97,5']:+.3f}")


def main():
    ap = argparse.ArgumentParser(description="Deney 1c: zamansal yumuşatma")
    ap.add_argument("--cikti", default=str(CIKTI))
    ap.add_argument("--bootstrap", type=int, default=2000)
    ap.add_argument("--hizli", action="store_true", help="küçük ızgara, yalnızca kod denemesi")
    args = ap.parse_args()
    utf8_cikti()
    print("Deney 1c — ayarlar hesaplanıyor...")
    calistir(args.cikti, args.bootstrap, args.hizli)


if __name__ == "__main__":
    main()
