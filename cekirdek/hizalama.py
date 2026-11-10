"""
DTW (dinamik zaman bükme) ile zamansal hizalama.

İki tekrar farklı hızda yapılabilir. DTW, tekrarın her karesini referans tekrarın "aynı andaki"
karesine eşler. Eşleme kol açısına göre yapılır (omuz ölçütüne göre değil).

Referans koddaki saf Python döngüsü numba ile derlendi; hesap sırası aynı olduğu için
sonuç (yol) birebir aynıdır (testler/test_cekirdek.py karşılaştırır).
"""
from __future__ import annotations

import numpy as np

try:
    from numba import njit
except ImportError:  # numba yoksa yavaş ama aynı sonuçlu saf Python
    def njit(*a, **k):
        def sar(f):
            return f
        return sar if not a or not callable(a[0]) else a[0]


@njit(cache=True)
def _dtw_birikimli(maliyet: np.ndarray) -> np.ndarray:
    n, m = maliyet.shape
    D = np.full((n + 1, m + 1), np.inf)
    D[0, 0] = 0.0
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            a, b, c = D[i - 1, j], D[i, j - 1], D[i - 1, j - 1]
            en_kucuk = a if a < b else b  # Python min() ile aynı: eşitlikte ilk eleman
            en_kucuk = en_kucuk if en_kucuk <= c else c
            D[i, j] = maliyet[i - 1, j - 1] + en_kucuk
    return D


@njit(cache=True)
def _geri_iz(D: np.ndarray) -> np.ndarray:
    i, j = D.shape[0] - 1, D.shape[1] - 1
    yol = np.empty((i + j, 2), dtype=np.int64)
    k = 0
    while i > 0 and j > 0:
        yol[k, 0], yol[k, 1] = i - 1, j - 1
        k += 1
        # np.argmin([çapraz, yukarı, sol]): eşitlikte ilk indeks
        c, u, s = D[i - 1, j - 1], D[i - 1, j], D[i, j - 1]
        if c <= u and c <= s:
            i, j = i - 1, j - 1
        elif u <= s:
            i = i - 1
        else:
            j = j - 1
    return yol[:k][::-1].copy()


def _znorm(a: np.ndarray) -> np.ndarray:
    return (a - a.mean()) / (a.std() + 1e-9)


def dtw_yol(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """1B diziler için DTW hizalama yolu (z-normalize, M22). Dönüş: (L, 2) dizisi; her satır (i_a, j_b)."""
    a, b = _znorm(np.asarray(a, np.float64)), _znorm(np.asarray(b, np.float64))
    maliyet = np.abs(a[:, None] - b[None, :])
    return _geri_iz(_dtw_birikimli(maliyet))


def hizala(ref_kol: np.ndarray, tekrar: dict[str, np.ndarray], olcutler) -> dict[str, np.ndarray]:
    """
    Tekrarın her ölçütünü referans karelerine eşler. Aynı referans karesine birden çok kare
    düşerse ortalamaları alınır. Dönüş: her ölçüt için len(ref_kol) uzunluğunda dizi.
    """
    yol = dtw_yol(ref_kol, tekrar["kol"])
    n = len(ref_kol)
    say = np.bincount(yol[:, 0], minlength=n).astype(np.float64)
    cikti = {}
    for k in olcutler:
        top = np.bincount(yol[:, 0], weights=tekrar[k][yol[:, 1]], minlength=n)
        cikti[k] = top / np.maximum(say, 1)
    return cikti
