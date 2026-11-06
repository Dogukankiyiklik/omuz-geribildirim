"""
Video ile iskelet dosyası kare kare hizalı mı? (Adım 2b; Adım 0'daki açık soru)

Bazı videolar iskelet dosyasından daha uzun (ör. ex1_Mima cam1: 14027 / 13724 kare). Görsel kontrol aracı
iskeletin k. karesini videonun k. karesine çizer; arada kayma varsa iskelet kişiye oturmaz.

Yöntem: Her videoda iki pencere (ilk tekrarın ve son tekrarın çevresi) alınır. Videodaki hareket
(ardışık kareler arası ortalama piksel farkı) ile iskeletteki hareket (13 eklemin kareden kareye yer
değiştirmesi) karşılaştırılır; ikisinin en iyi örtüştüğü kaydırma (gecikme) bulunur. 0 = hizalı.

Kullanım:
    python -m araclar.senkron_kontrol            # Ex1'in 15 videosu, ~3–5 dk
Çıktı: sonuclar/adim2b/senkron.csv
"""
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

import cv2
import numpy as np
import pandas as pd

from cekirdek import veri
from cekirdek.konsol import utf8_cikti

PENCERE = 900      # kare (30 sn)
EN_COK_KAYMA = 400


def video_hareketi(yol: Path, bas: int, n: int) -> np.ndarray:
    cap = cv2.VideoCapture(str(yol))
    cap.set(cv2.CAP_PROP_POS_FRAMES, bas)
    onceki, h = None, []
    for _ in range(n):
        ok, img = cap.read()
        if not ok:
            break
        g = cv2.resize(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), (135, 240)).astype(np.float32)
        h.append(np.nan if onceki is None else np.abs(g - onceki).mean())
        onceki = g
    cap.release()
    return np.array(h)


def iskelet_hareketi(a: np.ndarray, bas: int, n: int) -> np.ndarray:
    P = a[bas:bas + n][:, veri.EKLEMLER_13, :2].copy()
    P[..., 0] *= veri.EN_BOY
    d = np.linalg.norm(np.diff(P, axis=0), axis=2).mean(1)
    return np.concatenate([[np.nan], d])


def en_iyi_kayma(vid: np.ndarray, isk: np.ndarray, en_cok: int = EN_COK_KAYMA):
    """video[k + kayma] ~ iskelet[k] olacak kaymayı bulur (korelasyon en büyük)."""
    def z(x):
        x = np.nan_to_num(x, nan=np.nanmean(x))
        return (x - x.mean()) / (x.std() + 1e-9)
    v, s = z(vid), z(isk)
    sonuc = []
    for k in range(-en_cok, en_cok + 1):
        a, b = (v[k:], s[:len(v) - k]) if k >= 0 else (v[:k], s[-k:len(v)])
        m = min(len(a), len(b))
        if m < 200:
            continue
        sonuc.append((float(np.corrcoef(a[:m], b[:m])[0, 1]), k))
    r, k = max(sonuc)
    r0 = next(r_ for r_, k_ in sonuc if k_ == 0)
    return k, r, r0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--egzersiz", type=int, default=1)
    args = ap.parse_args()
    utf8_cikti()
    seg = veri.segmentasyon_oku()
    seg = seg[seg.exercise_id == args.egzersiz]
    kaynak = veri.IskeletKaynagi()
    kayit = []
    with tempfile.TemporaryDirectory() as td:
        for vid in sorted(seg.video_id.unique()):
            s = seg[seg.video_id == vid]
            for kam in veri.KAMERALAR:
                yol = veri.video_cikar(vid, kam, td)
                a = kaynak.oku(vid, kam)
                n_video = int(cv2.VideoCapture(str(yol)).get(cv2.CAP_PROP_FRAME_COUNT))
                for ad, bas in [("başta", max(0, int(s.first_frame.min()) - 20)),
                                ("sonda", max(0, int(s.last_frame.max()) + 20 - PENCERE))]:
                    k, r, r0 = en_iyi_kayma(video_hareketi(yol, bas, PENCERE), iskelet_hareketi(a, bas, PENCERE))
                    kayit.append({"video": vid, "kamera": kam, "pencere": ad, "baslangic_kare": bas,
                                  "video_kare": n_video, "iskelet_kare": len(a), "fark": n_video - len(a),
                                  "en_iyi_kayma": k, "korelasyon": round(r, 3), "korelasyon_kayma0": round(r0, 3)})
                    print(f"{vid:10s} {kam} {ad}: video {n_video} / iskelet {len(a)} kare → en iyi kayma {k:+d} "
                          f"(r = {r:.3f}; kayma 0'da r = {r0:.3f})")
                Path(yol).unlink()
    df = pd.DataFrame(kayit)
    cikti = veri.KOK / "sonuclar" / "adim2b"
    cikti.mkdir(parents=True, exist_ok=True)
    df.to_csv(cikti / "senkron.csv", index=False, encoding="utf-8-sig")
    print(f"\nKayma 0 olan pencere: {(df.en_iyi_kayma == 0).sum()} / {len(df)}")
    print(f"Yazıldı: {cikti / 'senkron.csv'}")


if __name__ == "__main__":
    main()
