"""
Canlı tekrar ayırma (kurallar önceden sabitlendi; sınama sonucuna göre değiştirilmez).

Kural:
  * Kol açısı 5 karelik hareketli medyanla yumuşatılır (kenarlarda en yakın değer tekrarlanır;
    aci_bandi.yumusak_kol ile aynı tanım, NaN'lar atlanır).
  * Tekrar adayı, yumuşatılmış açı 30°'nin üstüne çıkınca başlar (s), ardından 20°'nin altına inince
    biter (e). Tepe ≥ 60° ve süre (s → e) ≥ 0,8 s olmalıdır.
  * Sınırlar dinlenmeden dinlenmeye uzatılır:
      dinlenme  = s'den önceki 1 s'nin medyanı (yumuşatılmış açı);
      başlangıç = s'den geriye doğru açının ≤ dinlenme + 5° olduğu son kare; en fazla 2 s geri
                  (bulunamazsa 2 s geri; bir önceki tekrarın bitişinden öteye gidilmez);
      bitiş     = e'den itibaren açının ≤ dinlenme + 5° olduğu ilk kare; en fazla 1 s ileri
                  (bulunamazsa e + 1 s).

Tek uygulama: `TekrarAyirici` kareleri teker teker alır (uygulama, canlı kamera). Bir dizinin tamamı için
`tekrarlari_bul` aynı sınıfı kare kare besler (veri setinde sınama, video dosyası). Yumuşatılmış değer
merkezli pencere gerektirdiği için 2 kare gecikmeyle hesaplanır; `bitir()` kalan kareleri işler.

Etiketle eşleştirme: `eslestir`, bulunan tekrarları veri setinin etiketli tekrarlarıyla zaman örtüşmesine
(IoU ≥ 0,5) göre bire bir eşler. Ayırıcının sınanması (deneyler/tekrar_ayirma.py) ve uygulamanın
veri setiyle sağlık kontrolü (uygulama/toplu.py) aynı fonksiyonu kullanır.
"""
from __future__ import annotations

import warnings
from dataclasses import dataclass

import numpy as np

FPS = 30.0
BASLANGIC_ESIGI = 30.0
BITIS_ESIGI = 20.0
EN_AZ_TEPE = 60.0
EN_AZ_SURE_S = 0.8
DINLENME_PAYI = 5.0
DINLENME_SURE_S = 1.0
GERI_EN_FAZLA_S = 2.0
ILERI_EN_FAZLA_S = 1.0
MEDYAN_PENCERE = 5


@dataclass
class AyrilanTekrar:
    bas: int          # ilk kare (dahil)
    son: int          # son kare (dahil)
    tepe: float       # yumuşatılmış açının en büyüğü (s … e)
    dinlenme: float
    s: int            # 30° geçişi
    e: int            # 20° geçişi


def _nanmedyan(v) -> float:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        return float(np.nanmedian(v)) if len(v) else np.nan


class TekrarAyirici:
    """Kol açısını kare kare alır; biten tekrarları `ekle`/`bitir` dönüşünde verir."""

    def __init__(self, fps: float = FPS):
        self.fps = float(fps)
        self.ham: list[float] = []
        self.y: list[float] = []
        self._durum = "dinlenme"
        self._onceki_son = -1
        self._s = self._e = self._bas = None
        self._tepe = -np.inf
        self._dinlenme = np.nan
        self.son_gecersiz: dict | None = None    # yalnızca bilgi (arayüz): sayılmayan son aday

    # ------------------------------------------------ yalnızca okuma (arayüz için; kararı etkilemez)
    @property
    def durum(self) -> str:
        """dinlenme | hareket | bitis_ara"""
        return self._durum

    @property
    def anlik_tepe(self) -> float:
        return float(self._tepe) if self._durum != "dinlenme" else np.nan

    # ------------------------------------------------ yumuşatma (merkezli 5 kare, kenarda en yakın değer)
    def _yumusak(self, i: int) -> float:
        n, h = len(self.ham), MEDYAN_PENCERE // 2
        return _nanmedyan([self.ham[min(max(j, 0), n - 1)] for j in range(i - h, i + h + 1)])

    def ekle(self, aci: float) -> list[AyrilanTekrar]:
        self.ham.append(float(aci) if aci is not None else np.nan)
        cikti = []
        h = MEDYAN_PENCERE // 2
        while len(self.y) + h < len(self.ham):        # penceresi tamamlanan kareler
            self.y.append(self._yumusak(len(self.y)))
            cikti += self._adim(len(self.y) - 1)
        return cikti

    def bitir(self) -> list[AyrilanTekrar]:
        """Dizinin sonu: kalan kareleri kenar kuralıyla işle; bitişi aranan tekrar varsa son kareyle kapat."""
        cikti = []
        while len(self.y) < len(self.ham):
            self.y.append(self._yumusak(len(self.y)))
            cikti += self._adim(len(self.y) - 1)
        if self._durum == "bitis_ara":
            cikti.append(self._kapat(len(self.y) - 1))
        return cikti

    # ------------------------------------------------ durum makinesi
    def _adim(self, i: int) -> list[AyrilanTekrar]:
        v = self.y[i]
        if self._durum == "dinlenme":
            if v > BASLANGIC_ESIGI:
                self._basla(i)
            return []
        if self._durum == "hareket":
            if np.isfinite(v):
                self._tepe = max(self._tepe, v)
            if v < BITIS_ESIGI:
                self._e = i
                if self._tepe >= EN_AZ_TEPE and (i - self._s) / self.fps >= EN_AZ_SURE_S:
                    self._durum = "bitis_ara"
                    return self._bitis_kontrol(i)
                self._durum = "dinlenme"            # aday geçersiz
                self.son_gecersiz = {"kare": i, "tepe": float(self._tepe), "sure_s": (i - self._s) / self.fps}
            return []
        return self._bitis_kontrol(i)               # bitis_ara

    def _basla(self, s: int) -> None:
        self._durum, self._s, self._tepe = "hareket", s, self.y[s]
        y = np.asarray(self.y, float)
        n_d = int(round(DINLENME_SURE_S * self.fps))
        once = y[max(0, s - n_d):s]
        self._dinlenme = _nanmedyan(once) if len(once) else y[s]
        sinir = self._dinlenme + DINLENME_PAYI
        alt = max(s - int(round(GERI_EN_FAZLA_S * self.fps)), self._onceki_son + 1, 0)
        bas = alt
        for j in range(s - 1, alt - 1, -1):
            if y[j] <= sinir:
                bas = j
                break
        self._bas = bas

    def _bitis_kontrol(self, i: int) -> list[AyrilanTekrar]:
        if self.y[i] <= self._dinlenme + DINLENME_PAYI or i >= self._e + int(round(ILERI_EN_FAZLA_S * self.fps)):
            return [self._kapat(i)]
        return []

    def _kapat(self, son: int) -> AyrilanTekrar:
        t = AyrilanTekrar(self._bas, son, float(self._tepe), float(self._dinlenme), self._s, self._e)
        self._onceki_son = son
        self._durum = "dinlenme"
        return t


def tekrarlari_bul(kol: np.ndarray, fps: float = FPS) -> list[AyrilanTekrar]:
    """Bir dizinin tamamı için: TekrarAyirici'yi kare kare besler (uygulamayla aynı kod)."""
    a = TekrarAyirici(fps)
    cikti = []
    for v in np.asarray(kol, float):
        cikti += a.ekle(v)
    return cikti + a.bitir()


# ---------------------------------------------------------------- etiketli tekrarlarla eşleştirme
IOU_ESIGI = 0.5


def iou(a0: int, a1: int, b0: int, b1: int) -> float:
    """Kapalı aralıklar [a0, a1] ve [b0, b1] (kare) için kesişim / birleşim."""
    kes = max(0, min(a1, b1) - max(a0, b0) + 1)
    return kes / ((a1 - a0 + 1) + (b1 - b0 + 1) - kes)


def eslestir(etiketli: list[tuple[int, int]], bulunan: list[tuple[int, int]]):
    """Bire bir açgözlü eşleşme (en yüksek IoU önce). Dönüş: {etiket indeksi: (bulunan indeksi, IoU)}."""
    adaylar = sorted(((iou(*e, *b), i, j) for i, e in enumerate(etiketli) for j, b in enumerate(bulunan)),
                     reverse=True)
    es, kullanilan = {}, set()
    for v, i, j in adaylar:
        if v < IOU_ESIGI:
            break
        if i in es or j in kullanilan:
            continue
        es[i] = (j, v)
        kullanilan.add(j)
    return es
