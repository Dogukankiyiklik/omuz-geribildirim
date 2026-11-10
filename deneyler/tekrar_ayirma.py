"""
Tekrar ayırıcının veri setinde sınanması (Güncelleme 07, Karar 25).

Ayırıcı (cekirdek/tekrar_ayirici.py, uygulamayla aynı kod) Ex1'in bütün sürekli iskelet dizilerinde
(her video × kamera) kare kare çalıştırılır ve Segmentation.csv ile karşılaştırılır.
  * Eşleşme: bulunan ve etiketli tekrar arasında zaman örtüşmesi (IoU) ≥ 0,5; bire bir, en yüksek IoU önce.
  * Raporlanan: bulunan / kaçırılan / fazladan; başlangıç ve bitiş farkının (bulunan − etiket, kare)
    medyanı ve çeyrekleri; hata türüne göre kaçırma. Önden + çapraz ve tüm görüşler ayrı.
  * Fazladan bir tekrarın görüşü, aynı dizide zamanca en yakın etiketli tekrarın yönelimiyle belirlenir.
  * Eşikler bu sonuca göre DEĞİŞTİRİLMEZ. Etiketlilerin %90'ından azı bulunursa ADIM_06'ya yazılır.

Kullanım:
    python -m deneyler.tekrar_ayirma          # ~1 dk
Çıktı: sonuclar/tekrar_ayirma/
"""
from __future__ import annotations

import argparse
import time

import numpy as np
import pandas as pd

from cekirdek import hata_turu as ht
from cekirdek import tekrar_ayirici as ta
from cekirdek import veri
from cekirdek.konsol import sonuclari_yaz, utf8_cikti
from cekirdek.ozellikler import ozellikler
from cekirdek.tekrar_ayirici import IOU_ESIGI, eslestir, iou  # noqa: F401 (eşleştirme çekirdekte)
from deneyler.tablolar import ONDEN_CAPRAZ, TUMU, gorus_maskesi

CIKTI = veri.KOK / "sonuclar" / "tekrar_ayirma"
HEDEF_ORAN = 90.0   # Karar 25: %90'ın altı ADIM_06'ya yazılır ve kullanıcıya söylenir
GORUSLER = (ONDEN_CAPRAZ, TUMU, "profil (70–90°)")


def calistir_diziler(seg: pd.DataFrame):
    kaynak = veri.IskeletKaynagi()
    etiket_satir, fazla_satir = [], []
    for vid, grup in seg.groupby("video_id", sort=True):
        grup = grup.sort_values("first_frame")
        for kam in veri.KAMERALAR:
            a = kaynak.oku(vid, kam, "2d")
            kol = ozellikler(a, [])["kol"]
            bul = ta.tekrarlari_bul(kol)
            et = [(int(r.first_frame), int(r.last_frame)) for _, r in grup.iterrows()]
            es = eslestir(et, [(t.bas, t.son) for t in bul])
            for i, (idx, r) in enumerate(grup.iterrows()):
                s = {"video": vid, "kisi": r.person, "kamera": kam, "yonelim": int(r.person_orientation),
                     "satir": int(idx), "tekrar_no": int(r.repetition_number),
                     "gorus": veri.gorus_acisi(kam, int(r.person_orientation)),
                     "hata": r.error_description or ht.DOGRU, "etiket_bas": et[i][0], "etiket_son": et[i][1]}
                if i in es:
                    j, v = es[i]
                    t = bul[j]
                    s.update({"bulundu": True, "iou": v, "bulunan_bas": t.bas, "bulunan_son": t.son,
                              "bas_farki": t.bas - et[i][0], "son_farki": t.son - et[i][1], "tepe": t.tepe})
                else:
                    s.update({"bulundu": False})
                etiket_satir.append(s)
            eslesen = {j for j, _ in es.values()}
            merkez = np.array([(b + e) / 2 for b, e in et])
            for j, t in enumerate(bul):
                if j in eslesen:
                    continue
                k = int(np.argmin(np.abs(merkez - (t.bas + t.son) / 2)))
                yon = int(grup.iloc[k].person_orientation)
                en_iyi = max((iou(t.bas, t.son, *e) for e in et), default=0.0)
                fazla_satir.append({"video": vid, "kamera": kam, "yonelim": yon, "gorus": veri.gorus_acisi(kam, yon),
                                    "bas": t.bas, "son": t.son, "tepe": t.tepe, "en_iyi_iou": en_iyi})
    return pd.DataFrame(etiket_satir), pd.DataFrame(fazla_satir)


def _dagilim(x: pd.Series) -> dict:
    x = x.dropna()
    return {"medyan": x.median(), "Ç1": x.quantile(0.25), "Ç3": x.quantile(0.75)}


def tablolar(et: pd.DataFrame, fz: pd.DataFrame) -> dict:
    ozet, hata = [], []
    for gr in GORUSLER:
        e = et[gorus_maskesi(et, gr)]
        f = fz[gorus_maskesi(fz, gr)] if len(fz) else fz
        b = e[e.bulundu]
        r = {"görüş": gr, "etiketli": len(e), "bulunan": len(b), "kaçırılan": int((~e.bulundu).sum()),
             "fazladan": len(f), "bulunan /100": 100 * len(b) / len(e) if len(e) else np.nan,
             "IoU medyan": b.iou.median() if len(b) else np.nan}
        for ad, sut in (("başlangıç farkı", "bas_farki"), ("bitiş farkı", "son_farki")):
            for k, v in _dagilim(b[sut] if len(b) else pd.Series(dtype=float)).items():
                r[f"{ad} {k} (kare)"] = v
        ozet.append(r)
        if gr in (ONDEN_CAPRAZ, TUMU):
            for h in ht.SINIFLAR:
                g = e[e.hata == h]
                hata.append({"görüş": gr, "gerçek sınıf": ht.KISA_AD[h], "etiketli": len(g),
                             "kaçırılan": int((~g.bulundu).sum()),
                             "kaçırılan /100": 100 * float((~g.bulundu).mean()) if len(g) else np.nan})
    kisi = [{"görüş": gr, "kisi": k, "etiketli": len(g), "bulunan /100": 100 * float(g.bulundu.mean()),
             "fazladan": int((fz[gorus_maskesi(fz, gr)].video == f"ex1_{k}").sum()) if len(fz) else 0}
            for gr in (ONDEN_CAPRAZ, TUMU) for k, g in et[gorus_maskesi(et, gr)].groupby("kisi")]
    return {"ozet": pd.DataFrame(ozet), "hata_turu": pd.DataFrame(hata), "kisi": pd.DataFrame(kisi),
            "etiketli": et, "fazladan": fz}


def main():
    ap = argparse.ArgumentParser(description="Tekrar ayırıcının veri setinde sınanması (Karar 25)")
    ap.parse_args()
    utf8_cikti()
    t0 = time.time()
    seg = veri.segmentasyon_oku()
    seg = seg[seg.exercise_id == 1]
    et, fz = calistir_diziler(seg)
    T = tablolar(et, fz)
    sonuclari_yaz(T, CIKTI)
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 30)
    print("Tekrar ayırma (Karar 25): kural önceden sabit, sonuca göre değiştirilmez")
    print("\n1) Özet:")
    print(T["ozet"].round(2).T.to_string(header=False))
    print("\n2) Hata türüne göre kaçırma:")
    print(T["hata_turu"].round(2).to_string(index=False))
    print("\n3) Kişi:")
    print(T["kisi"].round(2).to_string(index=False))
    for _, r in T["ozet"].iterrows():
        if r["bulunan /100"] < HEDEF_ORAN:
            print(f"\nUYARI: {r['görüş']}: etiketlilerin {r['bulunan /100']:.2f}'i bulundu (< %{HEDEF_ORAN:.0f}); "
                  "Karar 25 gereği eşikler değiştirilmez, ADIM_06'ya yazılır.")
    print(f"\nSüre: {time.time() - t0:.1f} s · Çıktı: {CIKTI}")


if __name__ == "__main__":
    main()
