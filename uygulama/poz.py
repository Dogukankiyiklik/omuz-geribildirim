"""
MediaPipe Tasks PoseLandmarker sarmalayıcısı.

Model: pose_landmarker_full.task (veri setiyle aynı "Full" model). İlk çalıştırmada
modeller/ altına indirilir (*.task git'e girmez). Çıktı veri setinin _2d biçimindedir: (33, 4) =
x, y (görüntüye göre 0–1), z (göreli derinlik), görünürlük. Kişi bulunamazsa satır NaN olur.
"""
from __future__ import annotations

import urllib.request
from pathlib import Path

import numpy as np

from cekirdek.veri import KOK

MODEL_URL = ("https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_full/"
             "float16/latest/pose_landmarker_full.task")
MODEL_YOLU = KOK / "modeller" / "pose_landmarker_full.task"
EKLEM = 33


def model_yolu(yol: Path = MODEL_YOLU) -> Path:
    yol = Path(yol)
    if not yol.exists():
        yol.parent.mkdir(parents=True, exist_ok=True)
        print(f"Poz modeli indiriliyor: {MODEL_URL}")
        urllib.request.urlretrieve(MODEL_URL, yol)
    return yol


def mediapipe_surumu() -> str:
    import mediapipe as mp
    return mp.__version__


class PozCikarici:
    """Kareleri sırayla işler (VIDEO modu: zaman damgası artmalı)."""

    def __init__(self, yol: Path = MODEL_YOLU):
        import mediapipe as mp
        from mediapipe.tasks.python import BaseOptions, vision
        self._mp = mp
        secenek = vision.PoseLandmarkerOptions(base_options=BaseOptions(model_asset_path=str(model_yolu(yol))),
                                               running_mode=vision.RunningMode.VIDEO, num_poses=1)
        self._tespit = vision.PoseLandmarker.create_from_options(secenek)
        self.son_ms = -1

    def isle(self, bgr: np.ndarray, zaman_ms: int) -> np.ndarray:
        """Bir BGR kare → (33, 4) float64; kişi yoksa NaN."""
        import cv2
        zaman_ms = max(int(zaman_ms), self.son_ms + 1)
        self.son_ms = zaman_ms
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        img = self._mp.Image(image_format=self._mp.ImageFormat.SRGB, data=np.ascontiguousarray(rgb))
        sonuc = self._tespit.detect_for_video(img, zaman_ms)
        cikti = np.full((EKLEM, 4), np.nan)
        if sonuc.pose_landmarks:
            for j, lm in enumerate(sonuc.pose_landmarks[0]):
                cikti[j] = (lm.x, lm.y, lm.z, lm.visibility if lm.visibility is not None else np.nan)
        return cikti

    def kapat(self):
        self._tespit.close()

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.kapat()
