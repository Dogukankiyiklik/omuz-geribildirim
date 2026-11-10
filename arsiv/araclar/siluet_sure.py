"""
Adım 6b süre tahmini (Güncelleme 10, Karar 45). Ölçüt ya da deney DEĞİL: yalnızca MediaPipe segmentasyon
maskesinin ne kadar süreceğini ve ne kadar yer tutacağını ölçer.

Ex1'den 3 video baştan sona iki kez işlenir (aynı PoseLandmarker, VIDEO modu, pose_landmarker_full):
  1) output_segmentation_masks=False  (bugünkü uygulama ile aynı)
  2) output_segmentation_masks=True
Kare başına süre ölçülür (yalnızca model, bir de video çözme dahil "duvar" süresi); maskeler diske yazılmaz, yalnızca her 30. karede bellekte sıkıştırılıp boyutu ölçülür.
Toplam tahmin: önden + çapraz (|görüş| ≤ 60°) Ex1 tekrarlarının kareleri (her tekrar ±10 kare pay dahil) ×
kare başına ortalama süre.

Kullanım:
    python -m araclar.siluet_sure --kare 3000  # ~6 dk (her videodan ilk 3000 kare; kare başına süre sabit)
    python -m araclar.siluet_sure            # bütün kareler, ~45 dk (3 video ~49 600 kare, iki geçiş)
    python -m araclar.siluet_sure --kare 300 # hızlı deneme (her videodan ilk 300 kare)
Çıktı: sonuclar/siluet_sure/ (videolar.csv, ozet.csv)
"""
from __future__ import annotations

import argparse
import io
import time
from pathlib import Path

import cv2
import numpy as np
import pandas as pd

from cekirdek import veri
from cekirdek.konsol import sonuclari_yaz, utf8_cikti
from deneyler.tablolar import ONDEN_CAPRAZ_SINIR
from uygulama.poz import model_yolu

CIKTI = veri.KOK / "sonuclar" / "siluet_sure"
VIDEOLAR = [("ex1_Honza", "cam1"), ("ex1_Petra", "cam2"), ("ex1_Vasil", "cam1")]
ORNEK_ARALIK = 30


def _tespitci(maske: bool):
    from mediapipe.tasks.python import BaseOptions, vision
    s = vision.PoseLandmarkerOptions(base_options=BaseOptions(model_asset_path=str(model_yolu())),
                                     running_mode=vision.RunningMode.VIDEO, num_poses=1,
                                     output_segmentation_masks=maske)
    return vision.PoseLandmarker.create_from_options(s)


def _boyut(dizi: np.ndarray) -> int:
    b = io.BytesIO()
    np.savez_compressed(b, m=dizi)
    return b.getbuffer().nbytes


def video_isle(yol: Path, maske: bool, en_cok: int | None) -> dict:
    import mediapipe as mp
    cap = cv2.VideoCapture(str(yol))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    sureler, b_ikili, b_8bit, b_ham, bulunan = [], [], [], [], 0
    gen = yuk = 0
    with _tespitci(maske) as t:
        d0 = time.perf_counter()
        i = 0
        while en_cok is None or i < en_cok:
            ok, bgr = cap.read()
            if not ok:
                break
            yuk, gen = bgr.shape[:2]
            img = mp.Image(image_format=mp.ImageFormat.SRGB,
                           data=np.ascontiguousarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)))
            t0 = time.perf_counter()
            s = t.detect_for_video(img, int(round(i * 1000 / fps)))
            sureler.append(time.perf_counter() - t0)
            if maske and s.segmentation_masks:
                bulunan += 1
                if i % ORNEK_ARALIK == 0:
                    m = s.segmentation_masks[0].numpy_view()
                    b_ham.append(m.nbytes)
                    b_8bit.append(_boyut((np.clip(m, 0, 1) * 255).astype(np.uint8)))
                    b_ikili.append(_boyut(np.packbits(m > 0.5)))
            i += 1
        duvar = time.perf_counter() - d0          # video çözme + renk dönüşümü + model + maske ölçümü
    cap.release()
    s = np.asarray(sureler)
    return {"kare": len(s), "çözünürlük": f"{gen}x{yuk}", "ms/kare ort.": 1000 * s.mean(),
            "ms/kare medyan": 1000 * np.median(s), "toplam s": s.sum(),
            "duvar ms/kare (çözme dahil)": 1000 * duvar / max(len(s), 1), "duvar s": duvar,
            "maske bulunan kare": bulunan if maske else np.nan,
            "maske kB/kare ham float32": np.mean(b_ham) / 1024 if b_ham else np.nan,
            "maske kB/kare 8 bit sıkıştırılmış": np.mean(b_8bit) / 1024 if b_8bit else np.nan,
            "maske kB/kare ikili sıkıştırılmış": np.mean(b_ikili) / 1024 if b_ikili else np.nan}


def gereken_kare() -> tuple[int, int, int]:
    """Önden + çapraz Ex1 tekrarları: (tekrar sayısı, pay dahil kare toplamı, video×kamera sayısı)."""
    T = [t for t in veri.tekrarlari_yukle(1) if abs(t.gorus) <= ONDEN_CAPRAZ_SINIR]
    return len(T), int(sum(len(t.dizi) for t in T)), len({(t.video, t.kamera) for t in T})


def main():
    ap = argparse.ArgumentParser(description="Adım 6b: segmentasyon maskesi süre tahmini (Karar 45)")
    ap.add_argument("--kare", type=int, default=None, help="her videodan en fazla bu kadar kare (deneme)")
    ap.add_argument("--cikti", default=str(CIKTI))
    args = ap.parse_args()
    utf8_cikti()
    import mediapipe
    gecici = veri.KOK / "veri" / "ara" / "videolar"
    satir = []
    for video, kamera in VIDEOLAR:
        yol = veri.video_cikar(video, kamera, gecici)
        if yol is None:
            raise SystemExit("videos.zip bulunamadı")
        for maske in (False, True):
            r = video_isle(yol, maske, args.kare)
            satir.append({"video": video, "kamera": kamera, "maske": maske, **r})
            print(f"  {video} {kamera} maske={maske}: {r['kare']} kare, {r['ms/kare ort.']:.1f} ms/kare, "
                  f"{r['toplam s']:.0f} s", flush=True)
    v = pd.DataFrame(satir)
    n_tekrar, n_kare, n_video = gereken_kare()
    ozet = []
    for maske, g in v.groupby("maske"):
        ms = 1000 * g["toplam s"].sum() / g.kare.sum()            # kareye göre ağırlıklı ortalama
        oz = {"maske": maske, "ölçülen kare": int(g.kare.sum()), "ms/kare (ağırlıklı ort.)": ms,
              "önden+çapraz tekrar": n_tekrar, "önden+çapraz kare (±10 pay dahil)": n_kare,
              "video×kamera": n_video, "tahmini toplam dk (yalnızca model)": n_kare * ms / 1000 / 60,
              "duvar ms/kare": 1000 * g["duvar s"].sum() / g.kare.sum(),
              "tahmini toplam dk (çözme dahil)": n_kare * g["duvar s"].sum() / g.kare.sum() / 60}
        if maske:
            for k in ["ham float32", "8 bit sıkıştırılmış", "ikili sıkıştırılmış"]:
                oz[f"tahmini disk MB ({k})"] = n_kare * g[f"maske kB/kare {k}"].mean() / 1024
        ozet.append(oz)
    ozet = pd.DataFrame(ozet)
    bilgi = pd.DataFrame([{"mediapipe": mediapipe.__version__, "model": "pose_landmarker_full",
                           "tarih": time.strftime("%Y-%m-%d %H:%M"), "kare sınırı": args.kare}])
    sonuclari_yaz({"videolar": v, "ozet": ozet, "bilgi": bilgi}, Path(args.cikti))
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 30)
    print("\nVideolar:")
    print(v.round(2).to_string(index=False))
    print("\nÖzet:")
    print(ozet.round(2).T.to_string())
    print(f"\nÇıktı: {args.cikti}")


if __name__ == "__main__":
    main()
