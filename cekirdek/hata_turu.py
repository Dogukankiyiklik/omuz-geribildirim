"""
Hata türünü bulma (Adım 4, Deney 2): bir tekrar doğru mu, yanlışsa hangi hata?

Her hata türünün bir ölçütü vardır (PLAN.md, Adım 4):
  ERR_ELEVATED_SHOULDER : YENI (kulak – omuz mesafesi / gövde)       — açı bandı
  ERR_HEAD_TO_SIDE      : bas (M39 F3)                               — açı bandı
  ERR_ARM_FORWARD       : on_kacma (M39 F1) ya da kol_boyu           — açı bandı; hangisi, eğitim kişilerinde seçilir
  ERR_BENT_ARM          : dirsek (M39 F4)                            — açı bandı
  ERR_LOW_ABDUCTION     : kaldirma = tepe kol açısı sapması          — bant yok (Güncelleme 02)

Karar kuralı (basit ve açıklanabilir):
  1. Her ölçüt için tekrarın puanı: duruş ölçütlerinde bant hatası E (yönsüz ya da yönlü),
     kaldırmada tepe açısı sapması d (yönsüz: |d|, yönlü: beklenen yöndeki kısmı).
  2. Puan, EĞİTİM kişilerinin doğru tekrarlarındaki dağılımla ölçeklenir:
     z = (puan − medyan) / (çeyrekler arası açıklık + ε).
  3. max z < T ise "DOGRU"; değilse hata türü = argmax z.
  4. T (ve öne kaçma ölçütü) eğitim kişilerinde makro-F1'i en yükseğe çıkaracak şekilde seçilir.
  5. Yönlü bantta yön, eğitim kişilerinde (ilgili hatalı tekrarların ortalama imzalı farkı −
     doğru tekrarlarınki) işaretinden bulunur; elle yazılmaz.

Bu modül deneyde (deneyler/deney2.py) ve uygulamada (Adım 6) aynı şekilde kullanılır.
Girdi: tekrar başına puan tablosu (pandas), sütunlar puan_sutunu() / fark_sutunu() ile adlandırılır.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from cekirdek.degerlendirme import makro_f1

DOGRU = "DOGRU"
SILKME = "ERR_ELEVATED_SHOULDER"
HATALAR = ["ERR_ELEVATED_SHOULDER", "ERR_HEAD_TO_SIDE", "ERR_ARM_FORWARD", "ERR_BENT_ARM", "ERR_LOW_ABDUCTION"]
SINIFLAR = [DOGRU] + HATALAR
KISA_AD = {DOGRU: "doğru", "ERR_ELEVATED_SHOULDER": "omuz", "ERR_HEAD_TO_SIDE": "baş",
           "ERR_ARM_FORWARD": "öne kaçma", "ERR_BENT_ARM": "dirsek", "ERR_LOW_ABDUCTION": "az kaldırma"}

KALDIRMA = "kaldirma"
ON_KACMA_ADAYLARI = ("on_kacma", "kol_boyu")
TEPE_IQR_ALT_SINIR = 5.0   # derece (Güncelleme 02)
EPS = 0.01                 # z ölçeğinde payda: IQR + ε (E 0–1 aralığında; %1)
ESIK_IZGARASI = np.linspace(0, 100, 201)  # T adayları: eğitimdeki max z'nin yüzdelikleri


def hata_olcutleri(on_olcut: str = "on_kacma") -> dict[str, str]:
    """Hata kodu -> ölçüt."""
    if on_olcut not in ON_KACMA_ADAYLARI:
        raise ValueError(on_olcut)
    return {"ERR_ELEVATED_SHOULDER": "YENI", "ERR_HEAD_TO_SIDE": "bas", "ERR_ARM_FORWARD": on_olcut,
            "ERR_BENT_ARM": "dirsek", "ERR_LOW_ABDUCTION": KALDIRMA}


# ---------------------------------------------------------------- tekrar başına puanlar
def _yon_eki(yon: int) -> str:
    return {0: "0", 1: "p", -1: "n"}[int(np.sign(yon))]


def puan_sutunu(olcut: str, yon: int) -> str:
    """Duruş ölçütünün bant hatası sütunu, ör. E_YENI_0 (yönsüz), E_YENI_n (yalnızca bandın altı)."""
    return f"E_{olcut}_{_yon_eki(yon)}"


def fark_sutunu(olcut: str) -> str:
    """Ortalama imzalı fark sütunu (h − μ; kaldırmada d)."""
    return f"F_{olcut}"


def kaldirma_sapmasi(tepe: float, kalibrasyon_tepeleri) -> float:
    """
    Yetersiz kaldırma (Güncelleme 02): d = (kalibrasyon tepelerinin medyanı − tekrarın tepesi) /
    max(kalibrasyon tepelerinin IQR'si, 5°). Pozitif = kol normalden az kalktı.
    """
    t = np.asarray(kalibrasyon_tepeleri, dtype=float)
    q1, q3 = np.percentile(t, [25, 75])
    return float((np.median(t) - tepe) / max(q3 - q1, TEPE_IQR_ALT_SINIR))


def olcut_puani(df: pd.DataFrame, olcut: str, yon: int) -> pd.Series:
    """Bir ölçütün tekrar puanı. yon = 0 yönsüz; ±1 yalnızca o yöndeki sapma."""
    if olcut == KALDIRMA:
        d = df[fark_sutunu(KALDIRMA)]
        return d.abs() if yon == 0 else np.maximum(np.sign(yon) * d, 0.0)
    return df[puan_sutunu(olcut, yon)]


def beklenen_yonler(egitim: pd.DataFrame, on_olcut: str) -> dict[str, int]:
    """
    Her ölçütün beklenen hata yönü, eğitim tekrarlarından: işaret(ilgili hatalı tekrarların ortalama
    imzalı farkı − doğru tekrarlarınki). Fark 0 ya da tanımsızsa +1.
    """
    yonler = {}
    for hata, k in hata_olcutleri(on_olcut).items():
        f = egitim[fark_sutunu(k)]
        fark = f[egitim.hata == hata].mean() - f[egitim.hata == DOGRU].mean()
        yonler[k] = -1 if fark < 0 else 1
    return yonler


# ---------------------------------------------------------------- karar kuralı
@dataclass
class KararKurali:
    """Eğitim kişilerinden kurulmuş kural. z = (puan − medyan) / (IQR + ε); max z < T → DOGRU."""
    on_olcut: str
    yonlu: bool
    yonler: dict[str, int]
    medyan: dict[str, float]
    olcek: dict[str, float]
    T: float = np.inf
    bilgi: dict = field(default_factory=dict)

    @property
    def olcutler(self) -> dict[str, str]:
        return hata_olcutleri(self.on_olcut)

    def yon(self, olcut: str) -> int:
        return self.yonler[olcut] if self.yonlu else 0

    def z(self, df: pd.DataFrame) -> pd.DataFrame:
        """Tekrar × hata türü z tablosu (sütunlar HATALAR sırasıyla)."""
        cikti = {}
        for hata, k in self.olcutler.items():
            cikti[hata] = (olcut_puani(df, k, self.yon(k)) - self.medyan[k]) / self.olcek[k]
        return pd.DataFrame(cikti, index=df.index)[HATALAR]

    def karar(self, df: pd.DataFrame, z: pd.DataFrame | None = None) -> pd.Series:
        return _karar(self.z(df) if z is None else z, self.T)


def _karar(z: pd.DataFrame, T: float) -> pd.Series:
    """max z < T → DOGRU, değilse argmax z (eşitlikte HATALAR sırasındaki ilk). NaN z dikkate alınmaz."""
    Z = z.to_numpy(float)
    Zd = np.where(np.isnan(Z), -np.inf, Z)
    en = Zd.max(axis=1)
    tur = np.array(HATALAR, dtype=object)[Zd.argmax(axis=1)]
    return pd.Series(np.where(en < T, DOGRU, tur), index=z.index)


def kural_kur(egitim: pd.DataFrame, on_olcut: str, yonlu: bool) -> KararKurali:
    """Ölçekleme (eğitimdeki doğru tekrarların medyanı ve IQR'si) ve yönler; T henüz seçilmemiş."""
    yonler = beklenen_yonler(egitim, on_olcut)
    dogru = egitim[egitim.hata == DOGRU]
    medyan, olcek = {}, {}
    for k in hata_olcutleri(on_olcut).values():
        p = olcut_puani(dogru, k, yonler[k] if yonlu else 0).dropna()
        q1, q2, q3 = np.percentile(p, [25, 50, 75])
        medyan[k], olcek[k] = float(q2), float(q3 - q1) + EPS
    return KararKurali(on_olcut, yonlu, yonler, medyan, olcek)


def esik_sec(egitim: pd.DataFrame, yonlu: bool, adaylar=ON_KACMA_ADAYLARI) -> KararKurali:
    """
    Eğitim tekrarlarında makro-F1'i (6 sınıf, katı) en yükseğe çıkaran öne kaçma ölçütü ve T.
    T adayları: eğitimdeki max z dağılımının yüzdelikleri (ESIK_IZGARASI). Eşitlikte ilk aday
    (öne kaçmada on_kacma, T'de küçük olan) seçilir.
    """
    en_iyi = None
    for on_olcut in adaylar:
        kural = kural_kur(egitim, on_olcut, yonlu)
        z = kural.z(egitim)
        enz = np.nanmax(np.where(np.isnan(z.to_numpy(float)), -np.inf, z.to_numpy(float)), axis=1)
        for T in np.unique(np.percentile(enz[np.isfinite(enz)], ESIK_IZGARASI)):
            f1 = makro_f1(egitim.hata, _karar(z, T), SINIFLAR)
            if en_iyi is None or f1 > en_iyi[0] + 1e-12:
                en_iyi = (f1, on_olcut, float(T), kural)
    f1, on_olcut, T, kural = en_iyi
    kural.T = T
    kural.bilgi = {"egitim_makro_f1": f1}
    return kural


# ---------------------------------------------------------------- temel çizgi
def toplam_hata(z: pd.DataFrame) -> pd.Series:
    """Temel çizgi: tek bir toplam hata = z'lerin ortalaması (NaN'lar atlanır)."""
    return z.mean(axis=1, skipna=True)


def ikili_esik_sec(toplam: pd.Series, yanlis: pd.Series) -> float:
    """Temel çizgi için eşik: eğitimde dengeli doğruluğu (duyarlılık + özgüllük)/2 en yükseğe çıkaran."""
    v = toplam.to_numpy(float)
    y = yanlis.to_numpy(bool)
    en_iyi = (-1.0, np.inf)
    for T in np.unique(np.percentile(v[~np.isnan(v)], ESIK_IZGARASI)):
        p = v >= T
        dd = 0.5 * (p[y].mean() + (~p[~y]).mean())
        if dd > en_iyi[0] + 1e-12:
            en_iyi = (dd, float(T))
    return en_iyi[1]


# ---------------------------------------------------------------- esnek değerlendirme
def etiket_kumesi(hata: str, ek_hata: str) -> set[str]:
    """Birincil hata + ek hatalar (esnek değerlendirmede bunlardan birini söylemek doğru sayılır)."""
    return {hata} | {e.strip() for e in str(ek_hata).split(",") if e.strip()}


def esnek_gercek(hata: pd.Series, ek_hata: pd.Series, tahmin: pd.Series) -> pd.Series:
    """Esnek gerçek etiket: tahmin etiket kümesindeyse tahmin, değilse birincil hata."""
    return pd.Series([t if t in etiket_kumesi(h, e) else h for h, e, t in zip(hata, ek_hata, tahmin)],
                     index=hata.index)
