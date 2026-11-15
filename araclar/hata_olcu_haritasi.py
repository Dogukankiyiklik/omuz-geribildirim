"""
Sunum şekli: her hata türünde hangi ölçünün sapması büyüyor?

Yeni bir deney DEĞİLDİR; yeni bir sayı üretmez, yalnızca var olan iki dosyayı birleştirip çizer:
  - sonuclar/deney2/puanlar.csv  (her tekrarın beş ölçü puanı)
  - modeller/kural_ex1.json      (uygulamanın karar kuralı: ölçekleme ve T eşiği)

Her hücre: o gerçek etiketteki tekrarların, uygulamanın kuralına göre hesaplanan sapma puanının (z) ortancası.
0 = kişinin normali; T (3,80) ve üstü kalın yazılır. Önden ve çapraz çekimler (profil hariç).

Kullanım:
    python -m araclar.hata_olcu_haritasi
Çıktı: sonuclar/sunum/2_hata_olcu_isi_haritasi.png
"""
from __future__ import annotations

import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

from cekirdek import veri
from cekirdek.hata_turu import KararKurali

PUANLAR = veri.KOK / "sonuclar" / "deney2" / "puanlar.csv"
KURAL = veri.KOK / "modeller" / "kural_ex1.json"
CIKTI = veri.KOK / "sonuclar" / "sunum" / "2_hata_olcu_isi_haritasi.png"

SIRA = ["ERR_ELEVATED_SHOULDER", "ERR_HEAD_TO_SIDE", "ERR_ARM_FORWARD", "ERR_BENT_ARM", "ERR_LOW_ABDUCTION"]
SATIRLAR = ["Omuz silkmesi", "Baş eğme", "Kolun öne kaçması", "Dirsek bükme", "Kolu az kaldırma", "Doğru tekrar"]
SUTUNLAR = ["Kulak–omuz\nmesafesi", "Baş–gövde\naçısı", "Omuz–bilek\nmesafesi", "Dirsek\naçısı", "En yüksek\nkol açısı"]
MUREKKEP, SOLUK = "#14213D", "#5B6472"


def main() -> None:
    d = json.loads(KURAL.read_text(encoding="utf-8"))
    kural = KararKurali(d["esleme"], d["yonlu"], d["yonler"], d["medyan"], d["olcek"], d["T"],
                        kaldirma_surumu=d["kaldirma_surumu"])
    df = pd.read_csv(PUANLAR)
    df = df[~df.gorus_grubu.str.startswith("profil")]
    z = kural.z(df)
    z["hata"] = df.hata.values
    m = z.groupby("hata").median().loc[SIRA + ["DOGRU"], SIRA]
    n = z.groupby("hata").size().loc[SIRA + ["DOGRU"]]

    renk = LinearSegmentedColormap.from_list("turkuaz", ["#F4F7F7", "#BFE3DD", "#5FBFB1", "#0B7F73", "#064A43"])
    fig, ax = plt.subplots(figsize=(16.64, 6.2), dpi=150)
    V = m.to_numpy()
    ax.imshow(np.clip(V, 0, 8), cmap=renk, vmin=0, vmax=8, aspect="auto")
    for i in range(V.shape[0]):
        for j in range(V.shape[1]):
            v = V[i, j]
            koyu = min(max(v, 0), 8) / 8 > 0.45
            yazi = f"{v:.1f}".replace(".", ",").replace("-0,0", "0,0")
            ax.text(j, i, yazi, ha="center", va="center", fontsize=22, color="white" if koyu else MUREKKEP,
                    fontweight="bold" if v >= d["T"] else "normal")
    ax.set_xticks(range(len(SUTUNLAR)))
    ax.set_xticklabels(SUTUNLAR, fontsize=18, color=MUREKKEP)
    ax.set_yticks(range(len(SATIRLAR)))
    ax.set_yticklabels([f"{s}  ({n.iloc[i]})" for i, s in enumerate(SATIRLAR)], fontsize=18, color=MUREKKEP)
    ax.xaxis.tick_top()
    ax.tick_params(length=0)
    for k in ax.spines.values():
        k.set_visible(False)
    ax.set_xticks(np.arange(-.5, len(SUTUNLAR), 1), minor=True)
    ax.set_yticks(np.arange(-.5, len(SATIRLAR), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=3)
    ax.tick_params(which="minor", length=0)
    ax.axhline(4.5, color=SOLUK, lw=1.5, ls=(0, (4, 3)))
    ax.set_ylabel("Veri setindeki gerçek etiket (tekrar sayısı)", fontsize=15, color=SOLUK, labelpad=14)
    plt.tight_layout()
    CIKTI.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(CIKTI, facecolor="white")
    print(f"Yazıldı: {CIKTI}")


if __name__ == "__main__":
    main()
