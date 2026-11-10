"""
Kamera açısı uyarısının eşiği.

Veri setinin doğru Ex1 tekrarlarında dinlenme omuz genişliği / gövde boyu oranının dağılımı, görüş
grubuna göre. Eşik = çapraz (30–60°) grubundaki oranın 10. yüzdeliği (önceden sabit).

Kullanım:
    python -m deneyler.kamera_acisi          # ~30 s
Çıktı: sonuclar/kamera_acisi/, modeller/kamera_esigi.json
"""
from __future__ import annotations

import datetime as dt
import json

import numpy as np
import pandas as pd

from cekirdek import kamera_acisi as ka
from cekirdek import veri
from cekirdek.konsol import sonuclari_yaz, utf8_cikti
from deneyler.tablolar import GORUS_GRUPLARI

CIKTI = veri.KOK / "sonuclar" / "kamera_acisi"
CAPRAZ = "çapraz (30–60°)"
YUZDELIK = 10


def main():
    utf8_cikti()
    tekrarlar = [t for t in veri.tekrarlari_yukle(1) if t.dogru]
    df = pd.DataFrame([{"video": t.video, "kisi": t.kisi, "kamera": t.kamera, "yonelim": t.yonelim, "satir": t.satir,
                        "gorus": t.gorus, "gorus_grubu": veri.gorus_grubu(t.gorus),
                        "oran": ka.omuz_govde_orani(t.dizi)} for t in tekrarlar])
    esik = float(np.nanpercentile(df.loc[df.gorus_grubu == CAPRAZ, "oran"], YUZDELIK))
    satir = []
    for gg in GORUS_GRUPLARI:
        x = df.loc[df.gorus_grubu == gg, "oran"].dropna()
        satir.append({"görüş grubu": gg, "doğru tekrar": len(x), "%10": x.quantile(.10), "Ç1": x.quantile(.25),
                      "medyan": x.median(), "Ç3": x.quantile(.75), "%90": x.quantile(.90),
                      "eşiğin altında /100": 100 * float((x < esik).mean())})
    gorus = df.groupby("gorus").oran.agg(["count", "median"]).reset_index()
    gorus["eşiğin altında /100"] = [100 * float((df[df.gorus == g].oran < esik).mean()) for g in gorus.gorus]
    T = {"dagilim": pd.DataFrame(satir), "gorus": gorus, "tekrarlar": df}
    sonuclari_yaz(T, CIKTI)
    yol = ka.ESIK_DOSYASI
    yol.parent.mkdir(parents=True, exist_ok=True)
    yol.write_text(json.dumps({"esik": esik, "tanim": f"çapraz (30–60°) doğru tekrarlarda oranın %{YUZDELIK}'u",
                               "oran": "dinlenme (ilk 8 kare) omuz genişliği / gövde boyu, en-boy düzeltmeli",
                               "tarih": dt.datetime.now().isoformat(timespec="seconds")},
                              ensure_ascii=False, indent=2), encoding="utf-8")
    pd.set_option("display.width", 200)
    print("Kamera açısı oranı (doğru tekrarlar):")
    print(T["dagilim"].round(3).to_string(index=False))
    print("\nGörüş açısına göre:")
    print(gorus.round(3).to_string(index=False))
    print(f"\nEşik (çapraz grubun %{YUZDELIK}'u): {esik:.4f} → {yol}")


if __name__ == "__main__":
    main()
