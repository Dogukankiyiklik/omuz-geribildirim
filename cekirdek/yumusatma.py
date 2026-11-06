"""
Zamansal yumuşatma (Deney 1c; hocanın P2 için önerdiği "zamansal yumuşatma").

MediaPipe noktaları kareden kareye titrer (jitter). Omuzdaki küçük bir kalkış (silkme) bu titremenin
içinde kaybolabilir. İki filtre:

  - One Euro (Casiraghi ve ark., 2012): NEDENSEL (yalnızca geçmiş kareleri kullanır) → canlı
    uygulamada (Adım 6) aynen kullanılabilir. Hız düşükken çok, hızlıyken az yumuşatır:
    kesim frekansı = min_kesim + beta · |hız|. Hız, görüntü birimi/saniye (x, y 0–1).
  - Savitzky–Golay: nedensel DEĞİL (geleceği de kullanır); tekrar bittikten sonra uygulanabilir.
    Pencere içinde polinom uydurur; tepe biçimini sade hareketli ortalamadan iyi korur.

Yalnızca x, y sütunları yumuşatılır; z ve görünürlük olduğu gibi kalır. Filtre en-boy
düzeltmesinden önce, ham (0–1) koordinatlara uygulanır. Dizi değiştirilmez, kopya döner.
"""
from __future__ import annotations

import numpy as np
from scipy.signal import savgol_filter

FPS = 30.0


def _alfa(kesim, fps: float):
    """Birinci dereceden alçak geçiren filtre katsayısı (kesim Hz)."""
    tau = 1.0 / (2.0 * np.pi * kesim)
    return 1.0 / (1.0 + tau * fps)


def one_euro(dizi: np.ndarray, min_kesim: float = 1.0, beta: float = 0.0, d_kesim: float = 1.0,
             fps: float = FPS) -> np.ndarray:
    """One Euro filtresi, (kare, eklem, ≥2) dizinin x, y sütunlarına, her eklem ve eksen ayrı."""
    cikti = np.array(dizi, dtype=np.float64, copy=True)
    X = cikti[..., :2]
    if len(X) < 2:
        return cikti
    a_d = _alfa(d_kesim, fps)
    x_onceki = X[0].copy()
    dx_onceki = np.zeros_like(x_onceki)
    for i in range(1, len(X)):
        dx = (X[i] - x_onceki) * fps
        dx_sapka = a_d * dx + (1.0 - a_d) * dx_onceki
        a = _alfa(min_kesim + beta * np.abs(dx_sapka), fps)
        x_sapka = a * X[i] + (1.0 - a) * x_onceki
        X[i] = x_sapka
        x_onceki, dx_onceki = x_sapka, dx_sapka
    return cikti


def savitzky_golay(dizi: np.ndarray, pencere: int = 9, derece: int = 2) -> np.ndarray:
    """Savitzky–Golay, zaman ekseninde; kenarlarda polinom uydurma (mode="interp")."""
    cikti = np.array(dizi, dtype=np.float64, copy=True)
    pencere = min(pencere, len(cikti) - (1 - len(cikti) % 2))  # dizi kısaysa tek sayıya kırp
    if pencere <= derece:
        return cikti
    cikti[..., :2] = savgol_filter(cikti[..., :2], pencere, derece, axis=0, mode="interp")
    return cikti


YONTEMLER = {"one_euro": one_euro, "savgol": savitzky_golay}


def yumusat(dizi: np.ndarray, yontem: str | None, **param) -> np.ndarray:
    """yontem: None / "yok" (dizi aynen döner), "one_euro" veya "savgol"."""
    if yontem in (None, "yok"):
        return dizi
    return YONTEMLER[yontem](dizi, **param)
