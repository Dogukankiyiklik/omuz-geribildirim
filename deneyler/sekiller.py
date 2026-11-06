"""
Deney 1 şekilleri (Adım 2).

  1. sonuclar/deney1/auc.png         : ölçütlere göre AUC (silkme/doğru), bantsız ve bantlı yan yana,
                                       bantlı için kişi bazlı bootstrap %95 GA
  2. sonuclar/deney1/bant_ornegi.png : ex1_Honza, cam1, yönelim 0; YENI ölçütü için kişiye özel bant
                                       (gri), bir doğru tekrar ve bir silkmeli tekrar

Kullanım:
    python -m deneyler.sekiller            # önce: python -m deneyler.deney1
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from cekirdek import veri
from cekirdek.bant import bant_hatasi, bant_modeli
from cekirdek.konsol import utf8_cikti
from cekirdek.ozellikler import DENEY1_OLCUTLERI, ozellikler

KLASOR = veri.KOK / "sonuclar" / "deney1"

# Renkler (dataviz referans paleti, kategorik sıra): 1 mavi, 2 turuncu; metin ve ızgara nötr
MAVI, TURUNCU = "#2a78d6", "#eb6834"
GRI_HAM = "#a3a29c"
METIN, METIN2, IZGARA, BANT = "#0b0b0b", "#52514e", "#e4e3df", "#d6d5d0"

OLCUT_ADI = {
    "M01": "M01\niki omuz kalkışı",
    "M01_tek": "M01_tek\nsağ omuz kalkışı",
    "M39_F2": "M39_F2\nomuz açısı",
    "M33": "M33\nsağ omuz – omuz ortası",
    "YENI": "YENI\nkulak – omuz mesafesi",
}


def _stil():
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": METIN2,
        "axes.labelcolor": METIN, "xtick.color": METIN2, "ytick.color": METIN2,
        "axes.spines.top": False, "axes.spines.right": False, "figure.dpi": 150,
    })


# ---------------------------------------------------------------- 1. AUC çubuk grafiği
def auc_sekli(klasor: Path = KLASOR) -> Path:
    ozet = pd.read_csv(klasor / "ozet.csv")
    bs = pd.read_csv(klasor / "bootstrap.csv").set_index("ölçüt")
    sutun = "AUC silkme/doğru"
    ham = ozet[ozet["yöntem"] == "ham"].set_index("ölçüt").loc[DENEY1_OLCUTLERI, sutun]
    bant = ozet[ozet["yöntem"] == "bant"].set_index("ölçüt").loc[DENEY1_OLCUTLERI, sutun]

    fig, ax = plt.subplots(figsize=(9, 4.8))
    x = np.arange(len(DENEY1_OLCUTLERI))
    w = 0.36
    b1 = ax.bar(x - w / 2 - 0.01, ham.values, w, color=GRI_HAM, label="bantsız (ham)", zorder=2)
    b2 = ax.bar(x + w / 2 + 0.01, bant.values, w, color=MAVI, label="kişiye özel bant", zorder=2)
    alt = bant.values - bs.loc[DENEY1_OLCUTLERI, "GA %2,5"].values
    ust = bs.loc[DENEY1_OLCUTLERI, "GA %97,5"].values - bant.values
    ax.errorbar(x + w / 2 + 0.01, bant.values, yerr=[alt, ust], fmt="none", ecolor=METIN, elinewidth=1,
                capsize=3, zorder=3, label="%95 güven aralığı (kişi bazlı bootstrap)")
    for cubuklar in (b1, b2):
        for c in cubuklar:
            ax.text(c.get_x() + c.get_width() / 2, 0.505, f"{c.get_height():.2f}", ha="center",
                    va="bottom", fontsize=9, color="white" if cubuklar is b2 else METIN)
    ax.set_ylim(0.5, 1.0)
    ax.set_xticks(x, [OLCUT_ADI[k] for k in DENEY1_OLCUTLERI], fontsize=9)
    ax.set_ylabel("AUC: silkmeli ↔ doğru tekrar")
    ax.yaxis.grid(True, color=IZGARA, lw=0.8, zorder=0)
    ax.set_title("Deney 1 — Kişiye özel bant, omuz silkmesini her ölçütte daha iyi ayırıyor",
                 loc="left", fontsize=11, color=METIN)
    ax.legend(loc="upper left", frameon=False, fontsize=9, ncol=3, bbox_to_anchor=(0, 1.0))
    n = pd.read_csv(klasor / "tekrarlar.csv")
    fig.text(0.01, 0.01, f"REHAB26 Ex1, 5 kişi, 3 kamera. Silkme n={int((n.hata == 'ERR_ELEVATED_SHOULDER').sum())}, "
             "doğru n=834 (ek hatası silkme olanlar hariç). Y ekseni 0,5'ten (yazı-tura) başlar.", fontsize=8, color=METIN2)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    yol = klasor / "auc.png"
    fig.savefig(yol)
    plt.close(fig)
    return yol


# ---------------------------------------------------------------- 2. Bant örneği
def bant_ornegi(klasor: Path = KLASOR, video="ex1_Honza", kamera="cam1", yonelim=0,
                olcut="YENI", tohum=0) -> Path:
    """
    Bant, gösterilen doğru tekrar HARİÇ diğer doğru tekrarlardan kurulur (birini-dışarıda-bırak);
    silkmeli tekrar aynı modelle ölçülür. Her iki tekrar DTW ile referans tekrarın zamanına hizalanır.
    """
    tekrarlar = veri.tekrarlari_yukle(1, kaynak="zip")
    grup = veri.gruplara_ayir(tekrarlar)[(video, kamera, yonelim)]
    dogrular = [t for t in grup if t.dogru]
    dogru = dogrular[0]
    silkme = next(t for t in grup if t.hata == "ERR_ELEVATED_SHOULDER")
    olc = [olcut]
    f = {id(t): ozellikler(t.dizi, olc) for t in grup}
    model = bant_modeli([f[id(t)] for t in dogrular if t is not dogru], np.random.default_rng(tohum), olc)
    mu, tau = model[olcut]
    E_d, a_d = bant_hatasi(model, f[id(dogru)], olc, ayrinti=True)
    E_s, a_s = bant_hatasi(model, f[id(silkme)], olc, ayrinti=True)

    n = len(mu)
    zaman = np.linspace(0, 100, n)
    fig, (ust, alt) = plt.subplots(2, 1, figsize=(9, 6), sharex=True, gridspec_kw={"height_ratios": [1, 2.3]})

    ust.plot(zaman, model["ref_kol"], color=METIN2, lw=2)
    ust.set_ylabel("kol açısı (°)")
    ust.yaxis.grid(True, color=IZGARA, lw=0.8)
    ust.set_title(f"Bant örneği — {video}, {kamera}, yönelim {yonelim}° (önden), ölçüt {olcut}",
                  loc="left", fontsize=11, color=METIN)
    ust.text(1, 0.92, "referans tekrarın kol açısı (hizalama buna göre)", transform=ust.transAxes,
             ha="right", va="top", fontsize=8, color=METIN2)

    alt.fill_between(zaman, mu - tau, mu + tau, color=BANT, lw=0, label="kişiye özel bant (μ ± τ)")
    alt.plot(zaman, mu, color=METIN2, lw=1, ls="--", label="bant ortası μ")
    for a, renk, ad, E, t in [(a_d, MAVI, "doğru tekrar", E_d, dogru), (a_s, TURUNCU, "silkmeli tekrar", E_s, silkme)]:
        h = a["hizali"][olcut]
        alt.plot(zaman, h, color=renk, lw=2, label=f"{ad} (tekrar {t.tekrar_no}), E = {E[olcut]:.2f}")
        disari = a["kare_hatasi"][olcut] > 0
        alt.scatter(zaman[disari], h[disari], s=10, color=renk, edgecolor="white", linewidth=0.5, zorder=3)
    alt.set_xlabel("referans tekrarın zamanı (%) — 0: kol aşağıda, ~50: kol tepede, 100: kol aşağıda")
    alt.set_ylabel("YENI: (omuz y − kulak y) / gövde\n← omuz kulağa yaklaşıyor")
    alt.yaxis.grid(True, color=IZGARA, lw=0.8)
    alt.legend(loc="lower left", frameon=False, fontsize=9)
    fig.text(0.01, 0.01, "Noktalar: bandın dışına çıkan kareler. E = bant dışı hatanın kareler üzerinden ortalaması "
             "(0 = hep bant içinde, 1 = hep çok dışında).", fontsize=8, color=METIN2)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    yol = klasor / "bant_ornegi.png"
    fig.savefig(yol)
    plt.close(fig)
    print(f"Bant örneği: doğru = satır {dogru.satir} (tekrar {dogru.tekrar_no}), E = {E_d[olcut]:.3f}; "
          f"silkme = satır {silkme.satir} (tekrar {silkme.tekrar_no}), E = {E_s[olcut]:.3f}; "
          f"bant {len(dogrular) - 1} doğru tekrardan, referans indeksi {model['ref_indeks']}")
    return yol


# ---------------------------------------------------------------- 3. Puan dağılımı (AUC'yi gözle görmek için)
def dagilim_sekli(klasor: Path = KLASOR, olcut: str = "YENI") -> Path:
    """
    Bantsız ve bantlı puanların dağılımı: doğru / silkme / diğer hatalar. Kesikli çizgi = doğru
    tekrarların %90'ının altında kaldığı eşik; yanındaki yüzde, silkmelerin bu eşiği geçen oranı.
    (Açıklama amaçlı; eşik test verisinde seçildiği için bir değerlendirme sonucu DEĞİLDİR.)
    """
    from deneyler.deney1 import maskeler

    df = pd.read_csv(klasor / "tekrarlar.csv")
    df["ek_hata"] = df["ek_hata"].fillna("")
    silkme, dogru, diger = maskeler(df)
    gruplar = [("doğru tekrar", dogru, MAVI), ("omuz silkmesi", silkme, TURUNCU), ("diğer hatalar", diger, GRI_HAM)]
    fig, eksenler = plt.subplots(1, 2, figsize=(10, 4.4))
    for ax, yontem, baslik_ in zip(eksenler, ["ham", "bant"], ["bantsız (ham) puan", "kişiye özel bant: hata puanı E"]):
        c = f"{yontem}_{olcut}"
        kutular = np.linspace(0, df[c].max(), 31)
        for ad, m, renk in gruplar:
            ax.hist(df.loc[m, c], bins=kutular, density=True, histtype="step", lw=2,
                    color=renk, label=f"{ad} (n={int(m.sum())})")
        esik = df.loc[dogru, c].quantile(0.9)
        yakalanan = (df.loc[silkme, c] > esik).mean()
        ax.axvline(esik, color=METIN, lw=1, ls="--")
        ax.text(esik, ax.get_ylim()[1] * 0.97, f"  silkmelerin %{100 * yakalanan:.0f}'ı\n  bu çizginin sağında",
                va="top", ha="left", fontsize=8.5, color=METIN)
        ax.set_title(baslik_, loc="left", fontsize=10, color=METIN)
        ax.set_xlabel(f"{olcut} puanı (büyük = daha şüpheli)")
        ax.set_yticks([])
        ax.yaxis.grid(False)
    eksenler[0].set_ylabel("tekrar yoğunluğu")
    h, l = eksenler[1].get_legend_handles_labels()
    fig.legend(h, l, loc="upper left", bbox_to_anchor=(0.01, 0.93), ncol=3, frameon=False, fontsize=9)
    fig.suptitle(f"Deney 1 — {olcut}: bant, silkmeli tekrarları doğru tekrarlardan ayırıyor",
                 x=0.01, ha="left", fontsize=11, color=METIN)
    fig.text(0.01, 0.01, "Kesikli çizgi: doğru tekrarların %90'ı bu değerin solunda (yani doğruların %10'una yanlış alarm). "
             "Açıklama amaçlıdır; eşik ayarı değildir.", fontsize=8, color=METIN2)
    fig.tight_layout(rect=(0, 0.04, 1, 0.88))
    yol = klasor / "dagilim.png"
    fig.savefig(yol)
    plt.close(fig)
    return yol


def main():
    ap = argparse.ArgumentParser(description="Deney 1 şekilleri")
    ap.add_argument("--klasor", default=str(KLASOR))
    args = ap.parse_args()
    utf8_cikti()
    _stil()
    k = Path(args.klasor)
    print("Yazıldı:", auc_sekli(k))
    print("Yazıldı:", bant_ornegi(k))
    print("Yazıldı:", dagilim_sekli(k))


if __name__ == "__main__":
    main()
