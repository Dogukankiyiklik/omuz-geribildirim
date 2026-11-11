"""
Sunum şekli: açı bandı fikri tek bir çekimde.

Yeni bir deney DEĞİLDİR; sayı üretmez. Veri setindeki bir çekimin (varsayılan: ex1_Honza, cam1, yönelim 0)
doğru tekrarlarını ve omuz silkmeli bir tekrarını, uygulamanın kullandığı çekirdek kodla
(cekirdek/ozellikler.py, cekirdek/aci_bandi.py) çizer:

  sol  : kulak–omuz mesafesi zamana göre. Doğru tekrarda da omuz kulağa yaklaşır; bu yüzden
         "başlangıca göre ne kadar değişti?" diye bakan ham ölçü silkmeyi zayıf ayırır.
  sağ  : aynı eğriler kol açısına göre (kaldırma fazı) ve doğru tekrarlardan kurulan bant (μ ± τ).
         Silkmeli tekrar bandın altına iner.

Kullanım:
    python -m araclar.sunum_sekilleri            # birkaç saniye; veri/rehab26/ gerekir
Çıktı: sonuclar/sunum/1_aci_bandi.png
"""
from __future__ import annotations

import argparse

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from cekirdek import veri
from cekirdek.aci_bandi import KALDIRMA, KUTU_GENISLIGI, KUTU_SAYISI, aci_bandi_modeli, fazlar
from cekirdek.konsol import utf8_cikti
from cekirdek.ozellikler import ozellikler

CIKTI = veri.KOK / "sonuclar" / "sunum" / "1_aci_bandi.png"
MAVI, TURUNCU, GRI, MUREKKEP, SOLUK = "#2B6CB0", "#D9622B", "#C9CED6", "#1A2233", "#5B6472"
SILKME = "ERR_ELEVATED_SHOULDER"


def _eksen(ax, baslik, xetiket):
    ax.set_title(baslik, loc="left", fontsize=15, color=MUREKKEP, pad=12)
    ax.set_xlabel(xetiket, fontsize=13, color=SOLUK)
    for k in ("top", "right"):
        ax.spines[k].set_visible(False)
    for k in ("left", "bottom"):
        ax.spines[k].set_color(GRI)
    ax.tick_params(colors=SOLUK, labelsize=12)
    ax.grid(axis="y", color="#E6E9EE", linewidth=1)
    ax.set_axisbelow(True)


def ciz(video="ex1_Honza", kamera="cam1", yonelim=0, cikti=CIKTI):
    tekrarlar = [t for t in veri.tekrarlari_yukle(1, kameralar=(kamera,))
                 if t.video == video and t.yonelim == yonelim]
    dogrular = [t for t in tekrarlar if t.dogru]
    silkme = next(t for t in tekrarlar if t.hata == SILKME)

    def f(t):  # yalnızca etiketli kareler (bant da böyle kurulur)
        return {k: v[t.etiketli] for k, v in ozellikler(t.dizi, ["YENI"]).items()}

    fd, fs = [f(t) for t in dogrular], f(silkme)
    model = aci_bandi_modeli(fd, ["YENI"])

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(14, 5.6), sharey=True, dpi=160)
    fig.patch.set_facecolor("white")

    # sol: zamana göre
    for i, d in enumerate(fd):
        a1.plot(np.linspace(0, 100, len(d["YENI"])), d["YENI"], color=MAVI, lw=2, alpha=0.75,
                label=f"doğru tekrarlar ({len(fd)})" if i == 0 else None)
    a1.plot(np.linspace(0, 100, len(fs["YENI"])), fs["YENI"], color=TURUNCU, lw=2.6, label="omuz silkmeli tekrar")
    _eksen(a1, "Zamana göre: doğru tekrarda da omuz kulağa yaklaşıyor", "tekrarın ilerlemesi (%)")
    a1.set_ylabel("kulak–omuz dikey mesafesi / gövde boyu", fontsize=13, color=SOLUK)
    a1.legend(frameon=False, fontsize=12, loc="lower left")

    # sağ: kol açısına göre, kaldırma fazı + bant
    merkez = (np.arange(KUTU_SAYISI) + 0.5) * KUTU_GENISLIGI
    mu, tau, g = model.mu["YENI"][KALDIRMA], model.tau["YENI"][KALDIRMA], model.gecerli[KALDIRMA]
    a2.fill_between(merkez[g], (mu - tau)[g], (mu + tau)[g], color=GRI, alpha=0.9, lw=0,
                    label="bu kişinin normal aralığı (μ ± τ)")
    for d in fd:
        k = fazlar(d["kol"])[0] == KALDIRMA
        a2.plot(d["kol"][k], d["YENI"][k], color=MAVI, lw=1.6, alpha=0.6)
    k = fazlar(fs["kol"])[0] == KALDIRMA
    a2.plot(fs["kol"][k], fs["YENI"][k], color=TURUNCU, lw=2.6)
    _eksen(a2, "Kol açısına göre: silkme bandın altına iniyor", "kol açısı (°), kaldırma fazı")
    a2.legend(frameon=False, fontsize=12, loc="lower left")

    fig.text(0.01, 0.01, f"Veri: REHAB26-ViewAngles, {video}, {kamera}, yönelim {yonelim}° (CC BY-NC 4.0). "
             "Küçük değer = omuz kulağa yakın.", fontsize=10.5, color=SOLUK)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    cikti.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(cikti, facecolor="white")
    plt.close(fig)
    return cikti


def main():
    ap = argparse.ArgumentParser(description="Sunum şekli: açı bandı fikri")
    ap.add_argument("--video", default="ex1_Honza")
    ap.add_argument("--kamera", default="cam1")
    ap.add_argument("--yonelim", type=int, default=0)
    a = ap.parse_args()
    utf8_cikti()
    print("Yazıldı:", ciz(a.video, a.kamera, a.yonelim))


if __name__ == "__main__":
    main()
