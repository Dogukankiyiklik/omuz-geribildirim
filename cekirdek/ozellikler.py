"""
Kare başına ölçütler (özellikler).

Her ölçüt `@olcut("AD")` ile kayıt sistemine (OLCUTLER sözlüğü) eklenir; yeni ölçüt eklemek için
yalnızca yeni bir fonksiyon yazmak yeter (Adım 4'te hata türü ölçütleri buraya eklenecek).

Ölçüt fonksiyonu bir `Iskelet` alır ve (kare,) uzunluğunda bir dizi döndürür.
Sağ kol egzersiz yapıyor. MediaPipe: 8 sağ kulak, 11 sol omuz, 12 sağ omuz, 14 sağ dirsek,
23 sol kalça, 24 sağ kalça.

Kaynak: referans/deney1_omuz_olcutleri.py — davranış birebir korunur.
"""
from __future__ import annotations

from functools import cached_property
from typing import Callable

import numpy as np

from cekirdek.geometri import aci, nokta
from cekirdek.veri import EN_BOY

DINLENME_KARE = 8  # tekrar başındaki dinlenme kareleri (pay 10 karenin ilk 8'i)


class Iskelet:
    """Bir tekrar dizisinin en-boy düzeltilmiş noktalarına ve sık kullanılan büyüklüklere erişim."""

    def __init__(self, dizi: np.ndarray, en_boy: float = EN_BOY):
        self.dizi = dizi
        self.en_boy = en_boy
        self._onbellek: dict[int, np.ndarray] = {}

    def p(self, eklem: int) -> np.ndarray:
        if eklem not in self._onbellek:
            self._onbellek[eklem] = nokta(self.dizi, eklem, self.en_boy)
        return self._onbellek[eklem]

    def __len__(self) -> int:
        return len(self.dizi)

    @cached_property
    def govde(self) -> np.ndarray:
        """Kare başına gövde uzunluğu: omuz ortası – kalça ortası mesafesi."""
        sL, sR, hL, hR = self.p(11), self.p(12), self.p(23), self.p(24)
        return np.linalg.norm((sL + sR) / 2 - (hL + hR) / 2, axis=1)

    @cached_property
    def g0(self) -> float:
        """Tekrar başındaki (dinlenme) gövde uzunluğu; uzunluk ölçütleri buna bölünür."""
        return float(np.median(self.govde[:DINLENME_KARE]))

    @cached_property
    def asagi(self) -> np.ndarray:
        return np.tile([0.0, 1.0], (len(self), 1))


OLCUTLER: dict[str, Callable[[Iskelet], np.ndarray]] = {}


def olcut(ad: str):
    """Ölçüt fonksiyonunu kayıt sistemine ekleyen dekoratör."""
    def kaydet(f):
        if ad in OLCUTLER:
            raise ValueError(f"ölçüt zaten kayıtlı: {ad}")
        OLCUTLER[ad] = f
        return f
    return kaydet


# ---------------------------------------------------------------- hizalama özelliği
@olcut("kol")
def kol_acisi(s: Iskelet) -> np.ndarray:
    """Kol yükselme açısı: sağ üst kol ile aşağı yön arasındaki açı (M01, Denklem 5). DTW bununla yapılır."""
    return aci(s.p(14) - s.p(12), s.asagi)


# ---------------------------------------------------------------- Deney 1: omuz ölçütleri
def _omuz_ort_y(s: Iskelet) -> np.ndarray:
    return (s.p(11)[:, 1] + s.p(12)[:, 1]) / 2


@olcut("M01")
def m01(s: Iskelet) -> np.ndarray:
    """İki omzun ortalama yüksekliğinin tekrar başına göre kalkışı / gövde. Pozitif = omuz çizgisi kalktı."""
    ort_y = _omuz_ort_y(s)
    return (np.median(ort_y[:DINLENME_KARE]) - ort_y) / s.g0


@olcut("M01_tek")
def m01_tek(s: Iskelet) -> np.ndarray:
    """Aynı ölçüt, yalnızca egzersiz yapan (sağ) omuz."""
    sR = s.p(12)
    return (np.median(sR[:DINLENME_KARE, 1]) - sR[:, 1]) / s.g0


@olcut("M39_F2")
def m39_f2(s: Iskelet) -> np.ndarray:
    """Sağ omuzdaki açı: sol omuz – sağ omuz – sağ kalça (M39, Tablo 1, F2)."""
    return aci(s.p(11) - s.p(12), s.p(24) - s.p(12))


@olcut("M33")
def m33(s: Iskelet) -> np.ndarray:
    """Sağ omzun iki omuz orta noktasına göre dikey konumu / gövde. Pozitif = sağ omuz ortanın üstünde."""
    return (_omuz_ort_y(s) - s.p(12)[:, 1]) / s.g0


@olcut("YENI")
def yeni(s: Iskelet) -> np.ndarray:
    """Sağ kulak ile sağ omuz arasındaki dikey mesafe / gövde. Küçülürse omuz kulağa yaklaşıyor."""
    return (s.p(12)[:, 1] - s.p(8)[:, 1]) / s.g0


DENEY1_OLCUTLERI = ["M01", "M01_tek", "M39_F2", "M33", "YENI"]


def ozellikler(dizi: np.ndarray, olcutler=DENEY1_OLCUTLERI, en_boy: float = EN_BOY) -> dict[str, np.ndarray]:
    """Bir tekrar dizisinden kare başına kol açısı ("kol") ve istenen ölçütler."""
    s = Iskelet(dizi, en_boy)
    f = {"kol": OLCUTLER["kol"](s)}
    for k in olcutler:
        if k != "kol":
            f[k] = OLCUTLER[k](s)
    return f
