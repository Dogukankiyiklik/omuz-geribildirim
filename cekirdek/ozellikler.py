"""
Kare başına ölçütler (özellikler).

Her ölçüt `@olcut("AD")` ile kayıt sistemine (OLCUTLER sözlüğü) eklenir; yeni ölçüt eklemek için
yalnızca yeni bir fonksiyon yazmak yeter.

Ölçüt fonksiyonu bir `Iskelet` alır ve (kare,) uzunluğunda bir dizi döndürür.
Sağ kol egzersiz yapıyor. MediaPipe: 8 sağ kulak, 11 sol omuz, 12 sağ omuz, 14 sağ dirsek,
23 sol kalça, 24 sağ kalça.

Deney 1 ölçütleri ilk Deney 1 kodundan alındı; davranış birebir korunur (testler/test_deney1_regresyon.py).
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


# ---------------------------------------------------------------- Deney 2: hata türü ölçütleri
# M39 Tablo 1'den uyarlama (sağ kol). MediaPipe: 7/8 sol/sağ kulak, 16 sağ bilek.
def _orta(s: Iskelet, a: int, b: int) -> np.ndarray:
    return (s.p(a) + s.p(b)) / 2


@olcut("bas")
def bas(s: Iskelet) -> np.ndarray:
    """Baş eğikliği (M39 F3): (omuz ortası → kulak ortası) ile (kalça ortası → omuz ortası) arasındaki açı."""
    omuz = _orta(s, 11, 12)
    return aci(_orta(s, 7, 8) - omuz, omuz - _orta(s, 23, 24))


@olcut("on_kacma")
def on_kacma(s: Iskelet) -> np.ndarray:
    """Kolun gövde düzlemindeki açısı (M39 F1): sağ bilek – sağ omuz – sağ kalça açısı."""
    return aci(s.p(16) - s.p(12), s.p(24) - s.p(12))


@olcut("kol_boyu")
def kol_boyu(s: Iskelet) -> np.ndarray:
    """Sağ omuz – sağ bilek mesafesi / dinlenme gövde uzunluğu. Öne giden kol önden kamerada kısa görünür."""
    return np.linalg.norm(s.p(16) - s.p(12), axis=1) / s.g0


@olcut("dirsek")
def dirsek(s: Iskelet) -> np.ndarray:
    """Dirsek açısı (M39 F4): sağ omuz – sağ dirsek – sağ bilek. 180° = düz kol."""
    return aci(s.p(12) - s.p(14), s.p(16) - s.p(14))


# ---------------------------------------------------------------- yalnızca anlatım (tespite girmez)
@olcut("omuz_egim")
def omuz_egim(s: Iskelet) -> np.ndarray:
    """
    Omuz çizgisinin gövde eksenine göre eğimi (°): 90 − açı(sağ omuz − sol omuz, omuz ortası − kalça ortası).
    Pozitif = sağ omuz, gövde eksenine dik çizginin üstünde. Hocanın P2 listesindeki "omuz çizgisinin gövde
    eksenine göre açısı". Tespite girmez; silkme cümlesinde derece vermek için kullanılır.
    """
    return 90.0 - aci(s.p(12) - s.p(11), _orta(s, 11, 12) - _orta(s, 23, 24))


# Deney 2'nin duruş ölçütleri (açı bandıyla değerlendirilir). "omuz" = YENI.
# Yetersiz kaldırma bant değil, tepe kol açısıyla ele alınır (cekirdek/hata_turu.py).
DENEY2_OLCUTLERI = ["YENI", "bas", "on_kacma", "kol_boyu", "dirsek"]


def ozellikler(dizi: np.ndarray, olcutler=DENEY1_OLCUTLERI, en_boy: float = EN_BOY) -> dict[str, np.ndarray]:
    """Bir tekrar dizisinden kare başına kol açısı ("kol") ve istenen ölçütler."""
    s = Iskelet(dizi, en_boy)
    f = {"kol": OLCUTLER["kol"](s)}
    for k in olcutler:
        if k != "kol":
            f[k] = OLCUTLER[k](s)
    return f
