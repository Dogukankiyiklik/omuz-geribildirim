"""
Omuz silueti ölçütü `SILUET` (Adım 6b; tanım ilerleme/ADIM_06b.md "Önceden belirlenenler", Karar 48).

Fikir: MediaPipe omzu tek bir nokta olarak verir. Segmentasyon maskesi ise kişinin görüntüdeki şeklini
(silueti) piksel piksel verir. Omuz silkilince boyun ile omuz arasındaki siluet çizgisi (trapez kası hattı)
kulağa doğru yükselir. Bu modül o çizginin kulağa göre yüksekliğini ölçer.

Tanım (piksel koordinatlarında; x_px = x·W, y_px = y·H; y aşağı doğru):
  * Sağ kulak (8) ve sağ omuz (12); ikisinin görünürlüğü ≥ 0,5 değilse kare NaN.
  * Kulak ile omuz x'i arasındaki aralığın ortadaki %50'sinde 5 eşit aralıklı sütun
    (aralığın %25, %37,5, %50, %62,5, %75'i; en yakın piksel).
  * Her sütunda (kulak y − 0,10·g0)'dan (omuz y + 0,20·g0)'a inilir (uçlar dahil, en yakın piksel,
    görüntü içine kırpılmış); maske > 0,5 olan ilk piksel = siluet sınırı; yoksa sütun NaN.
  * Kare değeri = (5 sınırın medyanı − kulak y) / g0; en az 3 geçerli sütun, yoksa NaN.
  * g0 = gövde boyu (omuz ortası – kalça ortası), tekrarın ilk 8 karesinin medyanı (YENI ile aynı;
    NaN kareler medyana girmez).
Omuz silkilince küçülür (YENI ile aynı yön).

Maske, segmentasyon çalıştırmasında yalnızca omuz bölgesinde (kutu) ve ikili (> 0,5) saklanır
(ADIM_06b ayrıntı h); bu modül o kutularla çalışır. Kutunun dışına düşen arama pikselleri "bulunamadı"
sayılır ve ayrıca sayılır ("taşan sütun").
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from cekirdek.ozellikler import DINLENME_KARE

KULAK, OMUZ = 8, 12
SOL_OMUZ, SOL_KALCA, SAG_KALCA = 11, 23, 24
SUTUN_ORANLARI = (0.25, 0.375, 0.5, 0.625, 0.75)
UST_PAY = 0.10            # arama başlangıcı: kulak y − UST_PAY · g0
ALT_PAY = 0.20            # arama sonu: omuz y + ALT_PAY · g0
GORUNURLUK_ESIGI = 0.5
MASKE_ESIGI = 0.5
EN_AZ_SUTUN = 3
# Saklanan kutu (ADIM_06b ayrıntı h): x kulak–omuz ± KUTU_X_PAY piksel; y kulak − KUTU_UST·gövde_kare …
# omuz + KUTU_ALT·gövde_kare. Arama aralığından (0,10 / 0,20 · g0) bilerek çok geniş.
KUTU_X_PAY = 8
KUTU_UST = 0.5
KUTU_ALT = 0.6


@dataclass
class RoiMaske:
    """Bir karenin omuz bölgesi ikili maskesi: bitler[y − y0, x − x0] = maske(x, y) > 0,5."""
    x0: int
    y0: int
    bitler: np.ndarray  # (h, w) bool

    @property
    def x1(self) -> int:
        return self.x0 + self.bitler.shape[1]

    @property
    def y1(self) -> int:
        return self.y0 + self.bitler.shape[0]


# ---------------------------------------------------------------- noktalar
def piksel_noktalar(dizi: np.ndarray, genislik: int, yukseklik: int) -> np.ndarray:
    """(kare, 33, 4) normalize noktalar → (kare, 33, 2) piksel (x·W, y·H)."""
    P = dizi[..., :2].astype(np.float64).copy()
    P[..., 0] *= genislik
    P[..., 1] *= yukseklik
    return P


def govde_piksel(P: np.ndarray) -> np.ndarray:
    """Kare başına gövde boyu (piksel): omuz ortası – kalça ortası. P: (kare, 33, 2) ya da (33, 2)."""
    omuz = (P[..., SOL_OMUZ, :] + P[..., OMUZ, :]) / 2
    kalca = (P[..., SOL_KALCA, :] + P[..., SAG_KALCA, :]) / 2
    return np.linalg.norm(omuz - kalca, axis=-1)


def dinlenme_govde(govde: np.ndarray) -> float:
    """g0: ilk DINLENME_KARE karenin medyanı (NaN'lar hariç); hepsi NaN ise NaN."""
    g = np.asarray(govde[:DINLENME_KARE], np.float64)
    g = g[np.isfinite(g)]
    return float(np.median(g)) if len(g) else np.nan


def yeni_piksel(P: np.ndarray, g0: float) -> np.ndarray:
    """YENI ile aynı tanım, piksel noktalardan: (omuz y − kulak y) / g0."""
    return (P[:, OMUZ, 1] - P[:, KULAK, 1]) / g0


# ---------------------------------------------------------------- kutu (segmentasyon çalıştırmasında)
def roi_kutusu(P: np.ndarray, genislik: int, yukseklik: int) -> tuple[int, int, int, int] | None:
    """Bir karenin saklanacak kutusu (x0, y0, x1, y1; x1/y1 hariç), görüntü içine kırpılmış.
    P: (33, 2) piksel. Noktalar NaN ise ya da kutu boşsa None."""
    k, o = P[KULAK], P[OMUZ]
    g = govde_piksel(P)
    if not (np.isfinite(k).all() and np.isfinite(o).all() and np.isfinite(g)):
        return None
    x0 = int(np.floor(min(k[0], o[0]))) - KUTU_X_PAY
    x1 = int(np.ceil(max(k[0], o[0]))) + KUTU_X_PAY + 1
    y0 = int(np.floor(k[1] - KUTU_UST * g))
    y1 = int(np.ceil(o[1] + KUTU_ALT * g)) + 1
    x0, y0 = max(x0, 0), max(y0, 0)
    x1, y1 = min(x1, genislik), min(y1, yukseklik)
    if x1 <= x0 or y1 <= y0:
        return None
    return x0, y0, x1, y1


def roi_kes(maske: np.ndarray, kutu: tuple[int, int, int, int]) -> RoiMaske:
    """Tam maskeden (H, W) kutuyu keser ve ikiler (> MASKE_ESIGI)."""
    x0, y0, x1, y1 = kutu
    return RoiMaske(x0, y0, np.asarray(maske[y0:y1, x0:x1] > MASKE_ESIGI))


# ---------------------------------------------------------------- tanım
def sutun_xleri(kulak_x: float, omuz_x: float) -> np.ndarray:
    """Kulak–omuz yatay aralığının ortadaki %50'sinde 5 eşit aralıklı sütun (en yakın piksel)."""
    a, b = min(kulak_x, omuz_x), max(kulak_x, omuz_x)
    return np.rint(a + (b - a) * np.asarray(SUTUN_ORANLARI)).astype(np.int64)


def arama_araligi(kulak_y: float, omuz_y: float, g0: float, yukseklik: int) -> tuple[int, int]:
    """Dikey arama: (kulak y − 0,10·g0) … (omuz y + 0,20·g0), uçlar dahil, en yakın piksel, kırpılmış."""
    bas = int(np.rint(kulak_y - UST_PAY * g0))
    son = int(np.rint(omuz_y + ALT_PAY * g0))
    return max(bas, 0), min(son, yukseklik - 1)


def sinir_bul(roi: RoiMaske, x: int, y_bas: int, y_son: int) -> tuple[float, bool]:
    """
    Sütun x'te y_bas'tan y_son'a (dahil) inerken maskenin ilk 1 olduğu y; yoksa NaN.
    İkinci değer: arama aralığının bir kısmı kutunun dışına taştı mı (taşan pikseller "bulunamadı" sayılır).
    """
    tasti = not (roi.x0 <= x < roi.x1) or y_bas < roi.y0 or y_son >= roi.y1
    if not (roi.x0 <= x < roi.x1) or y_son < y_bas:
        return np.nan, tasti
    a, b = max(y_bas, roi.y0), min(y_son, roi.y1 - 1)
    if b < a:
        return np.nan, tasti
    sutun = roi.bitler[a - roi.y0:b - roi.y0 + 1, x - roi.x0]
    i = np.flatnonzero(sutun)
    return (float(a + i[0]) if len(i) else np.nan), tasti


@dataclass
class SiluetKaresi:
    deger: float              # SILUET (NaN olabilir)
    xler: np.ndarray          # (5,) sütun x'leri (görünürlük düşükse boş değil, NaN)
    sinirlar: np.ndarray      # (5,) sınır y'leri (NaN = bulunamadı)
    y_bas: float
    y_son: float
    tasan: int                # kutunun dışına taşan sütun sayısı
    neden: str                # "" (geçerli) / "nokta yok" / "görünürlük" / "g0" / "sütun"


def siluet_karesi(roi: RoiMaske | None, nokta: np.ndarray, gorunurluk: np.ndarray, g0: float,
                  yukseklik: int) -> SiluetKaresi:
    """
    Tek kare. nokta: (33, 2) piksel; gorunurluk: (33,). roi: o karenin kutusu (yoksa None).
    """
    bos = np.full(len(SUTUN_ORANLARI), np.nan)
    k, o = nokta[KULAK], nokta[OMUZ]
    if not (np.isfinite(k).all() and np.isfinite(o).all()):
        return SiluetKaresi(np.nan, bos, bos.copy(), np.nan, np.nan, 0, "nokta yok")
    vk, vo = gorunurluk[KULAK], gorunurluk[OMUZ]
    if not (vk >= GORUNURLUK_ESIGI and vo >= GORUNURLUK_ESIGI):  # NaN da geçersiz
        return SiluetKaresi(np.nan, bos, bos.copy(), np.nan, np.nan, 0, "görünürlük")
    if not np.isfinite(g0) or g0 <= 0:
        return SiluetKaresi(np.nan, bos, bos.copy(), np.nan, np.nan, 0, "g0")
    xs = sutun_xleri(k[0], o[0])
    y_bas, y_son = arama_araligi(k[1], o[1], g0, yukseklik)
    if roi is None:
        return SiluetKaresi(np.nan, xs.astype(float), bos.copy(), y_bas, y_son, 0, "nokta yok")
    ys, tasan = np.full(len(xs), np.nan), 0
    for i, x in enumerate(xs):
        ys[i], t = sinir_bul(roi, int(x), y_bas, y_son)
        tasan += int(t)
    gecerli = np.isfinite(ys)
    if gecerli.sum() < EN_AZ_SUTUN:
        return SiluetKaresi(np.nan, xs.astype(float), ys, y_bas, y_son, tasan, "sütun")
    return SiluetKaresi(float((np.median(ys[gecerli]) - k[1]) / g0), xs.astype(float), ys, y_bas, y_son,
                        tasan, "")


def siluet_dizisi(dizi: np.ndarray, roiler: list[RoiMaske | None], genislik: int, yukseklik: int) -> dict:
    """
    Bir tekrarın bütün kareleri (pay dahil). dizi: (kare, 33, 4) normalize noktalar (bu çalıştırmanın);
    roiler: kare başına kutu maskesi. Dönüş: SILUET, YENI_mp122, g0, sütun x'leri, sınır y'leri,
    arama aralığı, taşan sütun toplamı ve NaN nedenleri.
    """
    P = piksel_noktalar(dizi, genislik, yukseklik)
    g0 = dinlenme_govde(govde_piksel(P))
    kareler = [siluet_karesi(r, P[i], dizi[i, :, 3], g0, yukseklik) for i, r in enumerate(roiler)]
    return {"SILUET": np.array([s.deger for s in kareler]),
            "YENI_mp122": yeni_piksel(P, g0),
            "g0": g0,
            "xler": np.array([s.xler for s in kareler]),
            "sinirlar": np.array([s.sinirlar for s in kareler]),
            "arama": np.array([(s.y_bas, s.y_son) for s in kareler], dtype=np.float64),
            "tasan": int(sum(s.tasan for s in kareler)),
            "neden": [s.neden for s in kareler]}
