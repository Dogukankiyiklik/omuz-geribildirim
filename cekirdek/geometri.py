"""Geometri yardımcıları: en-boy düzeltmeli 2B nokta ve iki vektör arasındaki açı."""
from __future__ import annotations

import numpy as np

from cekirdek.veri import EN_BOY


def nokta(dizi: np.ndarray, eklem: int, en_boy: float = EN_BOY) -> np.ndarray:
    """
    Bir eklemin en-boy düzeltilmiş 2B koordinatı, (kare, 2) float64. y aşağı doğrudur.

    dizi: (kare, 33, 4) — eklem MediaPipe indeksiyle seçilir.
    x, görüntü genişliğine bölünmüş olduğu için en_boy (= genişlik/yükseklik) ile çarpılır;
    böylece x ve y aynı birimde (görüntü yüksekliği) olur.
    """
    xy = dizi[:, eklem, :2].astype(np.float64).copy()
    xy[:, 0] *= en_boy
    return xy


def aci(u: np.ndarray, v: np.ndarray) -> np.ndarray:
    """Kare başına u ve v vektörleri arasındaki açı (derece). u, v: (kare, 2)."""
    c = (u * v).sum(1) / (np.linalg.norm(u, axis=1) * np.linalg.norm(v, axis=1) + 1e-9)
    return np.degrees(np.arccos(np.clip(c, -1, 1)))
