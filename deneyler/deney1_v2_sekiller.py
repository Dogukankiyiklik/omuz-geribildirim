"""
Deney 1 v2 şekilleri (Adım 2c).

  1. sonuclar/deney1_v2/auc.png : koşullara göre YENI AUC'si (silkme/doğru ve silkme/diğer);
                                  çubuk = tüm veri, noktalar = kişiler (Karar 5)
  2. sonuclar/deney1_v2/ornekler/<tekrar>.png : aynı tekrar v1 (zaman bandı) ve v2 (açı bandı) yan yana
     Örnekler: Petra cam1 o0 t5, Honza cam1 o0 t5, Terka cam1 o20 t10 (Güncelleme 02).

Kullanım:
    python -m deneyler.deney1_v2_sekiller     # önce: python -m deneyler.deney1_v2
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
from cekirdek import aci_bandi as ab
from cekirdek.bant import bant_hatasi
from cekirdek.etiketler import hata_adi
from cekirdek.konsol import utf8_cikti
from deneyler import deney1_v2 as d2
from deneyler.sekiller import BANT, IZGARA, MAVI, METIN, METIN2, TURUNCU, _stil

ORNEKLER = [("ex1_Petra", "cam1", 0, 5), ("ex1_Honza", "cam1", 0, 5), ("ex1_Terka", "cam1", 20, 10)]
OLCUT = "YENI"
FAZ_RENK = {ab.KALDIRMA: MAVI, ab.INDIRME: TURUNCU}
KISA = {"v1": "zaman bandı\npay dahil\ntek ref. (Deney 1)", "v1a": "zaman bandı\npay hariç\ntek ref.",
        "v1b": "zaman bandı\npay hariç\nçoklu ref.", "v2": "açı bandı\npay hariç\nref. yok"}


# ---------------------------------------------------------------- 1. ablasyon AUC şekli
def auc_sekli(klasor: Path, olcut: str = OLCUT) -> Path:
    tekrarlar = pd.read_csv(klasor / "tekrarlar.csv", keep_default_na=False, na_values=[""])
    tekrarlar["ek_hata"] = tekrarlar.ek_hata.fillna("").astype(str)
    ozet = pd.read_csv(klasor / "ozet.csv")
    _stil()
    fig, eksenler = plt.subplots(1, 2, figsize=(9.5, 4.8), sharey=True)
    x = np.arange(len(d2.KOSULLAR))
    for ax, (sutun, baslik) in zip(eksenler, [("AUC silkme/doğru", "Silkme / doğru tekrar"),
                                              ("AUC silkme/diğer hatalar", "Silkme / diğer hatalar")]):
        o = ozet[ozet["ölçüt"] == olcut].set_index("koşul").loc[d2.KOSULLAR, sutun]
        ax.bar(x, o.values, width=0.56, color=MAVI, alpha=0.85, zorder=2)
        for xi, v in zip(x, o.values):  # değer çubuğun içinde: kişi noktalarıyla çakışmasın
            ax.text(xi, 0.515, f"{v:.3f}", ha="center", va="bottom", fontsize=9, color="white", fontweight="bold", zorder=4)
        # kişi noktaları
        for i, k in enumerate(d2.KOSULLAR):
            g = tekrarlar[tekrarlar.kosul == k]
            for j, (kisi, gk) in enumerate(g.groupby("kisi")):
                s, d, di = d2.maskeler(gk)
                neg = d if sutun == "AUC silkme/doğru" else di
                a = d2._auc(gk, s, neg, f"bant_{olcut}")
                ax.scatter(i + (j - 2) * 0.07, a, s=22, color="white", edgecolor=METIN, linewidth=1, zorder=3)
        ax.set_xticks(x, [f"{k}\n{KISA[k]}" for k in d2.KOSULLAR], fontsize=8)
        ax.set_ylim(0.5, 1.02)
        ax.set_title(baslik, loc="left", fontsize=10)
        ax.yaxis.grid(True, color=IZGARA, lw=0.8, zorder=0)
    eksenler[0].set_ylabel(f"AUC ({olcut})")
    eksenler[1].bar([0], [0], color=MAVI, alpha=0.85, label="tüm veri")
    eksenler[1].scatter([], [], s=22, color="white", edgecolor=METIN, label="tek tek kişiler (5)")
    eksenler[1].legend(loc="upper right", frameon=False, fontsize=8, ncol=2)
    eksenler[1].set_ylim(0.5, 1.06)
    fig.suptitle(f"Deney 1 v2 — yöntem düzeltmelerinin etkisi ({olcut}, kulak–omuz mesafesi)", x=0.01, ha="left", fontsize=11)
    fig.tight_layout()
    yol = klasor / "auc.png"
    fig.savefig(yol)
    plt.close(fig)
    return yol


# ---------------------------------------------------------------- 2. örnek tekrarlar: v1 ve v2 yan yana
def _bul(kayitlar, video, kamera, yonelim, tekrar):
    for d in kayitlar:
        t = d["t"]
        if (t.video, t.kamera, t.yonelim, t.tekrar_no) == (video, kamera, yonelim, tekrar):
            return d
    raise KeyError((video, kamera, yonelim, tekrar))


def zaman_bandi_ciz(ax, d, olcut=OLCUT):
    """v1: referans tekrarın zamanında bant ve DTW ile hizalanmış tekrar."""
    E, ayr = bant_hatasi(d["model"], d["f"], d2.OLCUTLER, ayrinti=True)
    mu, tau = d["model"][olcut]
    h, e = ayr["hizali"][olcut], ayr["kare_hatasi"][olcut]
    x = np.arange(len(mu))
    renk = TURUNCU if d["t"].hata != "DOGRU" else MAVI
    ax.fill_between(x, mu - tau, mu + tau, color=BANT, lw=0, label="bant (μ ± τ)")
    ax.plot(x, mu, color=METIN2, lw=1, ls="--", label="bant ortası μ")
    ax.plot(x, h, color=renk, lw=2, label="bu tekrar (DTW ile hizalı)")
    ax.scatter(x[e > 0], h[e > 0], s=14, color=renk, edgecolor="white", linewidth=0.5, zorder=3, label="bant dışı kare")
    # ikinci eksen yerine: referansın kol açısını üst kenarda metinle göster
    ref_kol = d["model"]["ref_kol"]
    ax.set_title(f"v1 — zaman bandı (M39, pay dahil)   E = {E[olcut]:.3f}\n"
                 f"referansın kol tepesi {ab.tepe_acisi(ref_kol):.0f}°, bu tekrarınki {ab.tepe_acisi(d['f']['kol']):.0f}°",
                 loc="left", fontsize=9.5)
    ax.set_xlabel("referans tekrarın zamanı (kare)")
    ax.set_ylabel(f"{olcut}: kulak–omuz mesafesi / gövde")
    ax.legend(loc="best", frameon=False, fontsize=7.5)
    return E[olcut]


def aci_bandi_ciz(ax, d, olcut=OLCUT, isaret_aci=90.0):
    """v2: x = kol açısı, y = ölçüt; faz başına bant ve tekrarın kareleri."""
    model = d["model"]
    E, ek = ab.aci_bandi_hatasi(model, d["f"], d2.OLCUTLER, ayrinti=True)
    kol, y = d["f"]["kol"], d["f"][olcut]
    xm = ab.kutu_merkezleri()
    for p in (ab.KALDIRMA, ab.INDIRME):
        g = model.gecerli[p]
        mu, tau = model.mu[olcut][p], model.tau[olcut][p]
        ax.fill_between(xm[g], (mu - tau)[g], (mu + tau)[g], color=FAZ_RENK[p], alpha=0.18, lw=0)
        ax.plot(xm[g], mu[g], color=FAZ_RENK[p], lw=1.2, ls="--")
        m = ek["faz"] == p
        disarida = m & (np.nan_to_num(ek["kare_hatasi"][olcut]) > 0)
        gecersiz = m & ~ek["gecerli"]
        ax.scatter(kol[m & ~gecersiz & ~disarida], y[m & ~gecersiz & ~disarida], s=14, color=FAZ_RENK[p],
                   edgecolor="white", linewidth=0.5, zorder=3, label=f"{ab.FAZ_ADLARI[p]}: bant içi kare")
        ax.scatter(kol[disarida], y[disarida], s=26, color=FAZ_RENK[p], edgecolor=METIN, linewidth=1.0,
                   zorder=4, label=f"{ab.FAZ_ADLARI[p]}: bant dışı kare")
        if gecersiz.any():
            ax.scatter(kol[gecersiz], y[gecersiz], s=16, facecolor="none", edgecolor=METIN2, linewidth=0.8,
                       zorder=3, label="kalibrasyon aralığı dışı (değerlendirilmez)" if p == ab.KALDIRMA else None)
    # "kol 90°'deyken omzun normal yeri"
    b = int(isaret_aci // ab.KUTU_GENISLIGI)
    if model.gecerli[ab.KALDIRMA, b]:
        mu90 = model.mu[olcut][ab.KALDIRMA, b]
        ax.axvline(isaret_aci, color=METIN2, lw=0.8, ls=":")
        ax.annotate(f"kol {isaret_aci:.0f}°'deyken bu kişinin\nomzu normalde: {mu90:.3f}",
                    xy=(isaret_aci, mu90), xytext=(8, 22), textcoords="offset points", fontsize=7.5, color=METIN,
                    arrowprops=dict(arrowstyle="-", color=METIN2, lw=0.8))
    ax.set_title(f"v2 — açı bandı (pay hariç)   E = {E[olcut]:.3f}\n"
                 f"kapsam {ek['kapsam']:.0%} · kalibrasyon tepesi en çok {model.en_yuksek_aci:.0f}°"
                 f"{' · ARALIK DIŞI' if ek['aralik_disi'] else ''}", loc="left", fontsize=9.5)
    ax.set_xlabel("kol açısı (°)  —  mavi: kaldırma, turuncu: indirme")
    ax.set_xlim(0, 185)
    ax.legend(loc="best", frameon=False, fontsize=7)
    return E[olcut]


def ornek_sekli(d1, d_v2, klasor: Path, olcut=OLCUT) -> Path:
    _stil()
    t = d1["t"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4.6))
    zaman_bandi_ciz(a1, d1, olcut)
    aci_bandi_ciz(a2, d_v2, olcut)
    alt = min(a1.get_ylim()[0], a2.get_ylim()[0])
    ust = max(a1.get_ylim()[1], a2.get_ylim()[1])
    for ax in (a1, a2):
        ax.set_ylim(alt, ust)  # iki panel aynı y ölçeğinde
    for ax in (a1, a2):
        ax.yaxis.grid(True, color=IZGARA, lw=0.8)
    fig.suptitle(f"{t.video} · {t.kamera} · yönelim {t.yonelim}° (görüş {t.gorus}°) · tekrar {t.tekrar_no} · "
                 f"gerçek etiket: {hata_adi(t.hata)}", x=0.01, ha="left", fontsize=11)
    fig.tight_layout()
    klasor.mkdir(parents=True, exist_ok=True)
    yol = klasor / f"{t.video}_{t.kamera}_o{t.yonelim}_t{t.tekrar_no}_{olcut}.png"
    fig.savefig(yol)
    plt.close(fig)
    return yol


def ornekler(klasor: Path, tohum: int = 0, ornek_listesi=ORNEKLER):
    tekrarlar = veri.tekrarlari_yukle(1)
    ozl = d2.ozellik_tablosu(tekrarlar)
    v1 = list(d2.degerlendirmeler(tekrarlar, "v1", tohum, ozl))
    v2 = list(d2.degerlendirmeler(tekrarlar, "v2", tohum, ozl))
    yollar = []
    for o in ornek_listesi:
        yollar.append(ornek_sekli(_bul(v1, *o), _bul(v2, *o), klasor / "ornekler"))
        print(f"  {yollar[-1]}")
    return yollar


def hepsi(tablolar=None, klasor: Path = d2.CIKTI, tohum: int = 0):
    print(f"  {auc_sekli(klasor)}")
    ornekler(klasor, tohum)


def main():
    ap = argparse.ArgumentParser(description="Deney 1 v2 şekilleri")
    ap.add_argument("--klasor", default=str(d2.CIKTI))
    ap.add_argument("--tohum", type=int, default=0)
    args = ap.parse_args()
    utf8_cikti()
    hepsi(klasor=Path(args.klasor), tohum=args.tohum)


if __name__ == "__main__":
    main()
