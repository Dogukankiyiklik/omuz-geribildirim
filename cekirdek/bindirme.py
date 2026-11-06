"""
Referans iskeleti kullanıcının iskeletine çakıştırma (hocanın Problem 3'ü).

İki hizalama birlikte yapılır:
  1. Zamansal: DTW (kol açısına göre). Kullanıcının her karesi, referans tekrarın "aynı andaki"
     karesine eşlenir.
  2. Geometrik: referans iskelet kullanıcının üzerine taşınır:
       * öteleme : referansın kalça ortası, kullanıcının o karedeki kalça ortasına getirilir;
       * ölçek   : dinlenme gövde uzunluklarının oranı (g0_kullanıcı / g0_referans);
       * döndürme: dinlenme gövde ekseni açılarının farkı (kalça ortası → omuz ortası).
     Ölçek ve döndürme tekrar BAŞINDAKİ dinlenme karelerinden bir kez hesaplanır, kare kare değil:
     kare kare gövde uzunluğuna ölçeklemek, omuz kalkınca gövde de "uzadığı" için silkmeyi
     referansa da taşıyıp gizlerdi (bkz. ilerleme/ADIM_02b.md, Kararlar).

Görsel kontrol aracı (araclar/gorsel_kontrol.py) ve uygulama (Adım 6) bu kodu ortak kullanır.
Koordinatlar en-boy düzeltilmiş birimdedir (görüntü yüksekliği = 1); piksele çevirmek için
yükseklikle (H) çarpmak yeter: x_px = x * H, y_px = y * H.
"""
from __future__ import annotations

import numpy as np

from cekirdek.geometri import nokta
from cekirdek.hizalama import dtw_yol
from cekirdek.ozellikler import DINLENME_KARE, OLCUTLER, Iskelet
from cekirdek.veri import EN_BOY

# Çizilecek kemikler (MediaPipe indeksleri). (8, 12) = sağ kulak – sağ omuz: YENI ölçütünün kendisi.
KEMIKLER = [
    (7, 2), (2, 0), (0, 5), (5, 8),            # baş: kulak – göz – burun
    (8, 12), (7, 11),                          # kulak – omuz
    (11, 12),                                  # omuz çizgisi
    (12, 14), (14, 16), (11, 13), (13, 15),    # kollar
    (11, 23), (12, 24), (23, 24),              # gövde
]
EKLEMLER = sorted({j for k in KEMIKLER for j in k})

# Hangi ölçüt banttan çıkınca hangi kemik kırmızı olur (ve hangi eklem vurgulanır).
OLCUT_UZUVLARI: dict[str, list[tuple[int, int]]] = {
    "YENI": [(8, 12)],
    "M01": [(11, 12)],
    "M01_tek": [(11, 12), (12, 24)],
    "M33": [(11, 12)],
    "M39_F2": [(11, 12), (12, 24)],
}


def tum_noktalar(dizi: np.ndarray, en_boy: float = EN_BOY) -> np.ndarray:
    """(kare, 33, 2) en-boy düzeltilmiş koordinatlar."""
    return np.stack([nokta(dizi, j, en_boy) for j in range(dizi.shape[1])], axis=1)


def _govde(P: np.ndarray):
    """P: (kare, 33, 2). Kalça ortası, omuz ortası, gövde ekseni açısı (radyan)."""
    kalca = (P[:, 23] + P[:, 24]) / 2
    omuz = (P[:, 11] + P[:, 12]) / 2
    v = omuz - kalca
    return kalca, np.arctan2(v[:, 1], v[:, 0])


def kare_eslemesi(ref_kol: np.ndarray, kul_kol: np.ndarray) -> np.ndarray:
    """DTW yolu ile kullanıcının her karesine bir referans karesi (birden çok eşleşmede ortalama)."""
    yol = dtw_yol(ref_kol, kul_kol)
    toplam = np.bincount(yol[:, 1], weights=yol[:, 0], minlength=len(kul_kol))
    sayi = np.bincount(yol[:, 1], minlength=len(kul_kol))
    return np.rint(toplam / np.maximum(sayi, 1)).astype(int)


class Bindirici:
    """Bir referans tekrarı bir kullanıcı tekrarına zamanda ve geometride çakıştırır."""

    def __init__(self, ref_dizi: np.ndarray, kul_dizi: np.ndarray, en_boy: float = EN_BOY,
                 ref_kol: np.ndarray | None = None, kul_kol: np.ndarray | None = None):
        self.P_ref = tum_noktalar(ref_dizi, en_boy)
        self.P_kul = tum_noktalar(kul_dizi, en_boy)
        s_ref, s_kul = Iskelet(ref_dizi, en_boy), Iskelet(kul_dizi, en_boy)
        ref_kol = OLCUTLER["kol"](s_ref) if ref_kol is None else ref_kol
        kul_kol = OLCUTLER["kol"](s_kul) if kul_kol is None else kul_kol
        self.esleme = kare_eslemesi(ref_kol, kul_kol)  # kullanıcı karesi -> referans karesi
        self.kalca_ref, aci_ref = _govde(self.P_ref)
        self.kalca_kul, aci_kul = _govde(self.P_kul)
        self.olcek = s_kul.g0 / s_ref.g0
        self.donus = float(np.median(aci_kul[:DINLENME_KARE]) - np.median(aci_ref[:DINLENME_KARE]))
        c, s = np.cos(self.donus), np.sin(self.donus)
        self._R = np.array([[c, -s], [s, c]])

    def referans_karesi(self, j: int) -> int:
        return int(self.esleme[j])

    def referans_noktalari(self, j: int) -> np.ndarray:
        """Kullanıcının j. karesine çakıştırılmış referans iskelet, (33, 2)."""
        i = self.referans_karesi(j)
        merkezli = self.P_ref[i] - self.kalca_ref[i]
        return (merkezli @ self._R.T) * self.olcek + self.kalca_kul[j]

    def kullanici_noktalari(self, j: int) -> np.ndarray:
        return self.P_kul[j]


def banttan_cikan_kemikler(kare_hatasi: dict[str, np.ndarray], i: int, olcutler) -> set[tuple[int, int]]:
    """Referans karesi i'de bandın dışında olan ölçütlerin kemikleri."""
    kemikler = set()
    for k in olcutler:
        if k in kare_hatasi and kare_hatasi[k][i] > 0:
            kemikler.update(OLCUT_UZUVLARI.get(k, []))
    return kemikler
