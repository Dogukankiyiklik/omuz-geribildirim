"""
Hız bilgi notunun eşiği (Güncelleme 08, Karar 31).

Veri setinin Ex1 DOĞRU tekrarlarında süre = (last_frame − first_frame + 1) / 30 FPS. Birim, diğer deneylerle
aynı: her (Segmentation.csv satırı, kamera) bir tekrardır; yalnızca önden + çapraz (|görüş| ≤ 60°) kameralar.
Eşik = bu sürelerin 5. yüzdeliği (önceden sabit). Daha kısa tekrarda uygulama "Hareketi biraz daha yavaş yap."
notunu gösterir. Not hata türü değildir; veri setinde hız etiketi olmadığı için doğruluğu ölçülemez.

Kullanım:
    python -m deneyler.hiz_esigi          # birkaç saniye (yalnızca Segmentation.csv okunur)
Çıktı: sonuclar/hiz_esigi/ (ham.csv, ozet.csv), modeller/hiz_esigi.json
"""
from __future__ import annotations

import datetime as dt
import json

import numpy as np
import pandas as pd

from cekirdek import bilgi_notlari as bn
from cekirdek import veri
from cekirdek.konsol import sonuclari_yaz, utf8_cikti
from deneyler.deney1 import GORUS_GRUPLARI

CIKTI = veri.KOK / "sonuclar" / "hiz_esigi"
FPS = 30.0
UYGULAMA = GORUS_GRUPLARI[:2]       # önden + çapraz (Karar 6)


def sure_tablosu(seg: pd.DataFrame | None = None) -> pd.DataFrame:
    seg = veri.segmentasyon_oku() if seg is None else seg
    s = seg[seg.exercise_id == 1]
    satir = []
    for i, r in s.iterrows():
        for kam in veri.KAMERALAR:
            g = veri.gorus_acisi(kam, r.person_orientation)
            satir.append({"satir": i, "video": r.video_id, "kisi": r.person, "kamera": kam,
                          "yonelim": int(r.person_orientation), "gorus": g, "gorus_grubu": veri.gorus_grubu(g),
                          "dogru": bool(r.correctness_score == 1),
                          "hata": r.error_description or "DOGRU",
                          "sure_s": bn.tekrar_suresi(r.first_frame, r.last_frame, FPS)})
    return pd.DataFrame(satir)


def esik_hesapla(df: pd.DataFrame) -> float:
    x = df.loc[df.dogru & df.gorus_grubu.isin(UYGULAMA), "sure_s"]
    return float(np.percentile(x, bn.HIZ_YUZDELIGI))


def main():
    utf8_cikti()
    df = sure_tablosu()
    esik = esik_hesapla(df)
    uyg = df[df.gorus_grubu.isin(UYGULAMA)]
    ozet = []
    for ad, g in [("doğru, önden + çapraz", uyg[uyg.dogru]), ("hatalı, önden + çapraz", uyg[~uyg.dogru])] + \
                 [(f"doğru, {k}", uyg[uyg.dogru & (uyg.kisi == k)]) for k in sorted(uyg.kisi.unique())]:
        x = g.sure_s
        ozet.append({"grup": ad, "tekrar": len(x), "%5": x.quantile(.05), "Ç1": x.quantile(.25), "medyan": x.median(),
                     "Ç3": x.quantile(.75), "en kısa": x.min(), "en uzun": x.max(),
                     "eşikten kısa /100": 100 * float((x < esik).mean())})
    ozet = pd.DataFrame(ozet)
    sonuclari_yaz({"ham": df, "ozet": ozet}, CIKTI)
    yol = bn.HIZ_ESIGI_DOSYASI
    yol.parent.mkdir(parents=True, exist_ok=True)
    yol.write_text(json.dumps({"esik_s": esik,
                               "tanim": f"Ex1 önden + çapraz doğru tekrarlarda sürenin %{bn.HIZ_YUZDELIGI}'i",
                               "sure": "(last_frame − first_frame + 1) / 30 FPS; birim (satır, kamera)",
                               "tekrar": int((uyg.dogru).sum()),
                               "tarih": dt.datetime.now().isoformat(timespec="seconds")},
                              ensure_ascii=False, indent=2), encoding="utf-8")
    pd.set_option("display.width", 200)
    print(ozet.round(3).to_string(index=False))
    print(f"\nHız eşiği (önden + çapraz doğru tekrarların %{bn.HIZ_YUZDELIGI}'i): {esik:.4f} s → {yol}")


if __name__ == "__main__":
    main()
