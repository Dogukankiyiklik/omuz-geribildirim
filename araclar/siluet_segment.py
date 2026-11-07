"""
Adım 6b: MediaPipe segmentasyon çalıştırması ve önbellek (Karar 48, madde 2 ve 8; ADIM_06b ayrıntı a, h).

Her Ex1 video×kamera için (yalnızca önden + çapraz tekrarları olanlar, 15 video) video baştan sırayla
çözülür; MediaPipe 1.2.2 (pose_landmarker_full, VIDEO modu, output_segmentation_masks=True) yalnızca
önden + çapraz tekrarların ±10 pay dahil karelerinde çalışır. Her işlenen karede saklanan:
  * 33 nokta (x, y, z, görünürlük; normalize, float32)
  * omuz bölgesi kutusu (x0, y0, x1, y1) ve kutunun ikili maskesi (> 0,5), np.packbits ile
Tam maske saklanmaz. Sınır y'leri ve SILUET değerlendirmede hesaplanır (deneyler/siluet.py).

Önbellek: veri/ara/siluet/<video>_<kamera>.npz (video bitince yazılır). Yarıda kalırsa aynı komut tekrar
çalıştırılır; biten videolar atlanır, yarım kalan video baştan işlenir (VIDEO modu takibi yüzünden
video ortasından devam edilmez).

Kullanım:
    python -m araclar.siluet_segment                      # bütün 15 video, tahmini 1,5–2 saat
    python -m araclar.siluet_segment --sinama 500         # kod sınaması: ilk videonun ilk 500 karesi
                                                          # (ayrı klasöre: veri/ara/siluet_sinama/)
    python -m araclar.siluet_segment --durum              # hangi videolar bitti
"""
from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

import numpy as np

from cekirdek import siluet as sl
from cekirdek import veri
from cekirdek.konsol import utf8_cikti

ONDEN_CAPRAZ_SINIR = 60
ONBELLEK = veri.VERI_KOK / "ara" / "siluet"
SINAMA = veri.VERI_KOK / "ara" / "siluet_sinama"
VIDEO_KLASORU = veri.VERI_KOK / "ara" / "videolar"


def gereken_kareler(tekrarlar=None) -> dict[tuple[str, str], np.ndarray]:
    """(video, kamera) -> işlenecek kare numaraları (önden + çapraz tekrarların ±10 pay dahil birleşimi)."""
    T = tekrarlar if tekrarlar is not None else veri.tekrarlari_yukle(1)
    T = [t for t in T if abs(t.gorus) <= ONDEN_CAPRAZ_SINIR]
    cikti: dict[tuple[str, str], set] = {}
    for t in T:
        cikti.setdefault((t.video, t.kamera), set()).update(range(t.ilk_kare, t.ilk_kare + len(t.dizi)))
    return {k: np.array(sorted(v), dtype=np.int64) for k, v in sorted(cikti.items())}


def onbellek_yolu(video: str, kamera: str, klasor: Path = ONBELLEK) -> Path:
    return Path(klasor) / f"{video}_{kamera}.npz"


def _tespitci():
    from mediapipe.tasks.python import BaseOptions, vision
    from uygulama.poz import model_yolu
    s = vision.PoseLandmarkerOptions(base_options=BaseOptions(model_asset_path=str(model_yolu())),
                                     running_mode=vision.RunningMode.VIDEO, num_poses=1,
                                     output_segmentation_masks=True)
    return vision.PoseLandmarker.create_from_options(s)


def video_isle(video: str, kamera: str, kareler: np.ndarray, hedef: Path, en_cok: int | None = None,
               ilerleme_her: int = 1000) -> dict:
    """Bir video×kamerayı işler ve önbelleği yazar. Dönüş: bilgi sözlüğü."""
    import cv2
    import mediapipe as mp
    yol = veri.video_cikar(video, kamera, VIDEO_KLASORU)
    if yol is None:
        raise SystemExit(f"videos.zip bulunamadı: {veri.VIDEO_ZIP}")
    if en_cok is not None:
        kareler = kareler[:en_cok]
    gerek = np.zeros(int(kareler.max()) + 1, dtype=bool)
    gerek[kareler] = True
    cap = cv2.VideoCapture(str(yol))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    toplam_video = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    n = len(kareler)
    noktalar = np.full((n, 33, 4), np.nan, np.float32)
    kutular = np.zeros((n, 4), np.int32)
    bit_parcalari, ofset = [], [0]
    maske_yok = 0
    W = H = 0
    j = 0
    t0 = time.perf_counter()
    with _tespitci() as tespit:
        for i in range(len(gerek)):
            ok, bgr = cap.read()
            if not ok:
                break
            if not gerek[i]:
                continue
            H, W = bgr.shape[:2]
            img = mp.Image(image_format=mp.ImageFormat.SRGB,
                           data=np.ascontiguousarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)))
            s = tespit.detect_for_video(img, int(round(i * 1000 / fps)))
            parca = np.zeros(0, np.uint8)
            if s.pose_landmarks:
                for e, lm in enumerate(s.pose_landmarks[0]):
                    noktalar[j, e] = (lm.x, lm.y, lm.z, lm.visibility if lm.visibility is not None else np.nan)
                P = sl.piksel_noktalar(noktalar[j][None].astype(np.float64), W, H)[0]
                kutu = sl.roi_kutusu(P, W, H)
                if kutu is not None:
                    if s.segmentation_masks:
                        m = np.squeeze(s.segmentation_masks[0].numpy_view())
                        roi = sl.roi_kes(m, kutu)
                        kutular[j] = kutu
                        parca = np.packbits(roi.bitler.ravel())
                    else:
                        maske_yok += 1
            bit_parcalari.append(parca)
            ofset.append(ofset[-1] + len(parca))
            j += 1
            if ilerleme_her and j % ilerleme_her == 0:
                gecen = time.perf_counter() - t0
                print(f"    {video} {kamera}: {j}/{n} kare · {gecen / 60:.1f} dk · kalan ~{gecen / j * (n - j) / 60:.1f} dk",
                      flush=True)
    cap.release()
    sure = time.perf_counter() - t0
    if j < n:
        raise RuntimeError(f"{video} {kamera}: video {j}/{n} gereken karede bitti (video {toplam_video} kare)")
    bilgi = {"video": video, "kamera": kamera, "kare": n, "video_kare": toplam_video, "fps": fps,
             "genislik": W, "yukseklik": H, "sure_s": sure,
             "kisi_bulunamayan": int(np.isnan(noktalar[:, 0, 0]).sum()), "maske_yok": maske_yok,
             "mediapipe": mp.__version__, "model": "pose_landmarker_full", "mod": "VIDEO",
             "tarih": time.strftime("%Y-%m-%d %H:%M")}
    hedef.parent.mkdir(parents=True, exist_ok=True)
    gecici = hedef.with_suffix(".yaziliyor.npz")
    np.savez_compressed(gecici, kareler=kareler, noktalar=noktalar, kutular=kutular,
                        bitler=np.concatenate(bit_parcalari) if bit_parcalari else np.zeros(0, np.uint8),
                        ofset=np.asarray(ofset, np.int64), bilgi=json.dumps(bilgi, ensure_ascii=False))
    os.replace(gecici, hedef)
    return bilgi


class Onbellek:
    """Bir video×kameranın önbelleği: kare numarasına göre noktalar ve kutu maskeleri."""

    def __init__(self, yol: Path):
        d = np.load(yol, allow_pickle=False)
        self.kareler = d["kareler"]
        self.noktalar = d["noktalar"]
        self.kutular = d["kutular"]
        self.bitler = d["bitler"]
        self.ofset = d["ofset"]
        self.bilgi = json.loads(str(d["bilgi"]))
        self.genislik, self.yukseklik = int(self.bilgi["genislik"]), int(self.bilgi["yukseklik"])
        self._sira = {int(k): i for i, k in enumerate(self.kareler)}

    def indeksler(self, ilk: int, n: int) -> np.ndarray:
        try:
            return np.array([self._sira[k] for k in range(ilk, ilk + n)], dtype=np.int64)
        except KeyError as e:
            raise KeyError(f"önbellekte kare yok: {e} ({self.bilgi['video']} {self.bilgi['kamera']})") from None

    def roi(self, i: int) -> sl.RoiMaske | None:
        x0, y0, x1, y1 = (int(v) for v in self.kutular[i])
        if x1 <= x0 or y1 <= y0:
            return None
        bit = np.unpackbits(self.bitler[self.ofset[i]:self.ofset[i + 1]])[:(x1 - x0) * (y1 - y0)]
        return sl.RoiMaske(x0, y0, bit.reshape(y1 - y0, x1 - x0).astype(bool))

    def tekrar(self, ilk: int, n: int) -> tuple[np.ndarray, list]:
        """Tekrarın (pay dahil) kareleri: (n, 33, 4) float64 noktalar ve kutu maskeleri."""
        idx = self.indeksler(ilk, n)
        return self.noktalar[idx].astype(np.float64), [self.roi(int(i)) for i in idx]


def durum(klasor: Path = ONBELLEK) -> list[tuple[str, str, bool]]:
    return [(v, k, onbellek_yolu(v, k, klasor).exists()) for v, k in gereken_kareler()]


def main():
    ap = argparse.ArgumentParser(description="Adım 6b: segmentasyon çalıştırması ve önbellek")
    ap.add_argument("--sinama", type=int, metavar="KARE",
                    help="kod sınaması: ilk videonun yalnızca ilk KARE gereken karesi, ayrı klasöre")
    ap.add_argument("--durum", action="store_true", help="hangi videoların bittiğini yazar")
    ap.add_argument("--klasor", default=None, help="önbellek klasörü (varsayılan veri/ara/siluet)")
    args = ap.parse_args()
    utf8_cikti()
    klasor = Path(args.klasor) if args.klasor else (SINAMA if args.sinama else ONBELLEK)
    if args.durum:
        d = durum(klasor)
        for v, k, bitti in d:
            print(f"  {v} {k}: {'bitti' if bitti else 'bekliyor'}")
        print(f"{sum(b for *_, b in d)}/{len(d)} video bitti · {klasor}")
        return
    gerek = gereken_kareler()
    if args.sinama:
        gerek = dict(list(gerek.items())[:1])
    toplam = sum(len(v) for v in gerek.values())
    print(f"Segmentasyon: {len(gerek)} video×kamera, {toplam} kare · önbellek: {klasor}", flush=True)
    t0 = time.perf_counter()
    for s, ((video, kamera), kareler) in enumerate(gerek.items(), 1):
        hedef = onbellek_yolu(video, kamera, klasor)
        if hedef.exists() and not args.sinama:
            print(f"  [{s}/{len(gerek)}] {video} {kamera}: önbellekte var, atlandı", flush=True)
            continue
        print(f"  [{s}/{len(gerek)}] {video} {kamera}: {len(kareler)} kare işleniyor...", flush=True)
        b = video_isle(video, kamera, kareler, hedef, en_cok=args.sinama)
        print(f"  [{s}/{len(gerek)}] {video} {kamera}: bitti, {b['sure_s'] / 60:.1f} dk "
              f"({1000 * b['sure_s'] / b['kare']:.1f} ms/kare) · kişi bulunamayan kare {b['kisi_bulunamayan']} · "
              f"toplam {(time.perf_counter() - t0) / 60:.1f} dk", flush=True)
    print(f"Bitti: {(time.perf_counter() - t0) / 60:.1f} dk · {klasor}")


if __name__ == "__main__":
    main()
