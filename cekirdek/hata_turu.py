"""
Hata türünü bulma (Deney 2): bir tekrar doğru mu, yanlışsa hangi hata?

Her hata türünün bir ölçütü vardır:
  ERR_ELEVATED_SHOULDER : YENI (kulak – omuz mesafesi / gövde)       — açı bandı
  ERR_HEAD_TO_SIDE      : bas (M39 F3)                               — açı bandı
  ERR_ARM_FORWARD       : on_kacma (M39 F1) ya da kol_boyu           — açı bandı; hangisi, eğitim kişilerinde seçilir
  ERR_BENT_ARM          : dirsek (M39 F4)                            — açı bandı
  ERR_LOW_ABDUCTION     : kaldirma = tepe kol açısı eksikliği. İki sürüm (kaldirma_surumu):
                          "ilk"    (VARSAYILAN, kullanılan yöntem): d = (kalibrasyon tepelerinin medyanı − tepe)
                                   / max(tepe IQR'si, 5°); yönlü puan max(d, 0), yönsüz |d|; yön eğitimden.
                          "revize" (denenip elenen; yalnızca karşılaştırma için): tek kutulu tepe bandı, E 0–1.

Karar kuralı (basit ve açıklanabilir):
  1. Her ölçüt için tekrarın puanı: duruş ölçütlerinde açı bandı hatası E (yönsüz ya da yönlü),
     kaldırmada ilk sürümde tepe açısı sapması d (kaldirma_sapmasi), revizede tepe bandı E'si.
  2. Puan, EĞİTİM kişilerinin doğru tekrarlarındaki dağılımla ölçeklenir:
     z = (puan − medyan) / (çeyrekler arası açıklık + ε).
  3. max z < T ise "DOGRU"; değilse hata türü = argmax z.
  4. T (ve öne kaçma ölçütü) eğitim kişilerinde makro-F1'i en yükseğe çıkaracak şekilde seçilir.
  5. Yönlü bantta yön, eğitim kişilerinde (ilgili hatalı tekrarların ortalama imzalı farkı −
     doğru tekrarlarınki) işaretinden bulunur; elle yazılmaz.

Bu modül deneyde (deneyler/deney2.py) ve uygulamada aynı şekilde kullanılır.
Girdi: tekrar başına puan tablosu (pandas), sütunlar puan_sutunu() / fark_sutunu() ile adlandırılır.
"""
from __future__ import annotations

import itertools
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
KALDIRMA_ILK = "kaldirma_ilk"   # puan tablosunda ilk sürümün d'si: sütun F_kaldirma_ilk (adil modellerin ortalaması)
KALDIRMA_SURUMLERI = ("ilk", "revize")
VARSAYILAN_KALDIRMA = "ilk"     # önceden belirlenmiş birincil yöntem; dondurulmuş
TEPE_IQR_ALT_SINIR = 5.0   # derece; ilk sürüm
ON_KACMA_ADAYLARI = ("on_kacma", "kol_boyu")
TEPE_ALT_SINIR = 10.0      # derece; tepe bandının yarı genişliği en az bu (literatürden, değiştirilmez)
TEPE_GUVEN = 0.975         # τ = t(0,975; n−1)·s/√n
EPS = 0.01                 # z ölçeğinde payda: IQR + ε (E 0–1 aralığında; %1)
ESIK_IZGARASI = np.linspace(0, 100, 201)  # T adayları: eğitimdeki max z'nin yüzdelikleri


def hata_olcutleri(on_olcut: str = "on_kacma") -> dict[str, str]:
    """Ex1: hata kodu -> ölçüt."""
    if on_olcut not in ON_KACMA_ADAYLARI:
        raise ValueError(on_olcut)
    return {"ERR_ELEVATED_SHOULDER": "YENI", "ERR_HEAD_TO_SIDE": "bas", "ERR_ARM_FORWARD": on_olcut,
            "ERR_BENT_ARM": "dirsek", "ERR_LOW_ABDUCTION": KALDIRMA}


@dataclass(frozen=True)
class HataTanimi:
    """
    Bir egzersizin hata türleri ve her hatanın aday ölçütleri (ilk aday eşitlikte seçilir).
    hatalar sırası z tablosunun sütun sırası ve argmax eşitliğinde öncelik sırasıdır.
    """
    ad: str
    hatalar: tuple
    adaylar: dict

    @property
    def siniflar(self) -> list[str]:
        return [DOGRU] + list(self.hatalar)

    def eslemeler(self) -> list[dict[str, str]]:
        """Aday ölçütlerin tüm birleşimleri: [{hata: ölçüt}, ...] (sıra: adayların sırası)."""
        listeler = [self.adaylar[h] for h in self.hatalar]
        return [dict(zip(self.hatalar, secim)) for secim in itertools.product(*listeler)]


EX1 = HataTanimi("ex1", tuple(HATALAR), {"ERR_ELEVATED_SHOULDER": ("YENI",), "ERR_HEAD_TO_SIDE": ("bas",),
                                         "ERR_ARM_FORWARD": ON_KACMA_ADAYLARI, "ERR_BENT_ARM": ("dirsek",),
                                         "ERR_LOW_ABDUCTION": (KALDIRMA,)})


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
    İlk sürüm (kullanılan yöntem): d = (kalibrasyon tepelerinin medyanı − tekrarın
    tepesi) / max(kalibrasyon tepelerinin IQR'si, 5°). Pozitif = kol normalden az kalktı.
    """
    t = np.asarray(kalibrasyon_tepeleri, dtype=float)
    q1, q3 = np.percentile(t, [25, 75])
    return float((np.median(t) - tepe) / max(q3 - q1, TEPE_IQR_ALT_SINIR))


def _surum_kontrol(kaldirma_surumu: str) -> str:
    if kaldirma_surumu not in KALDIRMA_SURUMLERI:
        raise ValueError(f"kaldirma_surumu {KALDIRMA_SURUMLERI} içinden olmalı: {kaldirma_surumu!r}")
    return kaldirma_surumu


def tepe_bandi(kalibrasyon_tepeleri) -> tuple[float, float]:
    """
    Tek kutulu tepe bandı ("revize" sürüm): μ = kalibrasyon tepelerinin ortalaması,
    τ = max(t(0,975; n−1) · s / √n, 10°). s örneklem standart sapması (n−1 paydalı).
    10° alt sınır: MediaPipe–gonyometre uyumu ≈ ±7° (M20), tek kamerada uçta 15°'ye varan hata (M41, M42).
    """
    from scipy.stats import t as t_dagilimi
    x = np.asarray(kalibrasyon_tepeleri, dtype=float)
    n = len(x)
    mu = float(x.mean())
    yari = float(t_dagilimi.ppf(TEPE_GUVEN, n - 1) * x.std(ddof=1) / np.sqrt(n)) if n >= 2 else np.inf
    return mu, max(yari, TEPE_ALT_SINIR)


def kaldirma_puanlari(tepe: float, kalibrasyon_tepeleri) -> tuple[dict[int, float], float]:
    """
    Az kaldırma puanı, duruş ölçütlerinin E'siyle aynı biçimde (0–1).
    eksik = μ − tepe (pozitif = kol normalden az kalktı). Sapma a için E = 0 (a ≤ τ), değilse
    min(1, (a − τ)/τ). Dönüş: ({yon: E}, eksik) — yon +1: yalnızca eksik (az kalkma), −1: yalnızca
    fazla, 0: |eksik| (yönsüz).
    """
    mu, tau = tepe_bandi(kalibrasyon_tepeleri)
    eksik = mu - float(tepe)

    def E(a):
        return 0.0 if a <= tau else float(min(1.0, (a - tau) / tau))
    return {1: E(eksik), -1: E(-eksik), 0: E(abs(eksik))}, eksik


def olcut_puani(df: pd.DataFrame, olcut: str, yon: int, kaldirma_surumu: str = VARSAYILAN_KALDIRMA) -> pd.Series:
    """Bir ölçütün tekrar puanı. yon = 0 yönsüz; ±1 yalnızca o yöndeki sapma.
    Kaldırma, ilk sürüm: ortalama d'den (F_kaldirma_ilk) |d| ya da max(±d, 0) — ilk sürüm koduyla aynı."""
    if olcut == KALDIRMA and _surum_kontrol(kaldirma_surumu) == "ilk":
        d = df[fark_sutunu(KALDIRMA_ILK)]
        return d.abs() if yon == 0 else np.maximum(np.sign(yon) * d, 0.0)
    return df[puan_sutunu(olcut, yon)]


def beklenen_yonler(egitim: pd.DataFrame, esleme, kaldirma_surumu: str = VARSAYILAN_KALDIRMA) -> dict[str, int]:
    """
    Her ölçütün beklenen hata yönü, eğitim tekrarlarından: işaret(ilgili hatalı tekrarların ortalama
    imzalı farkı − doğru tekrarlarınki). Fark 0 ya da tanımsızsa +1.
    Kaldırma: ilk sürümde yön d'den öğrenilir (ilk sürüm koduyla aynı); revizede sabit +1.
    """
    esleme = hata_olcutleri(esleme) if isinstance(esleme, str) else esleme
    yonler = {}
    for hata, k in esleme.items():
        if k == KALDIRMA and _surum_kontrol(kaldirma_surumu) == "revize":
            yonler[k] = 1
            continue
        f = egitim[fark_sutunu(KALDIRMA_ILK if k == KALDIRMA else k)]
        fark = f[egitim.hata == hata].mean() - f[egitim.hata == DOGRU].mean()
        yonler[k] = -1 if fark < 0 else 1
    return yonler


# ---------------------------------------------------------------- karar kuralı
@dataclass
class KararKurali:
    """Eğitim kişilerinden kurulmuş kural. z = (puan − medyan) / (IQR + ε); max z < T → DOGRU.
    esleme: hata -> ölçüt (sıra = z sütunlarının sırası)."""
    esleme: dict
    yonlu: bool
    yonler: dict[str, int]
    medyan: dict[str, float]
    olcek: dict[str, float]
    T: float = np.inf
    bilgi: dict = field(default_factory=dict)
    kaldirma_surumu: str = VARSAYILAN_KALDIRMA

    @property
    def olcutler(self) -> dict[str, str]:
        return self.esleme

    @property
    def hatalar(self) -> list[str]:
        return list(self.esleme)

    @property
    def on_olcut(self):
        """Öne kaçma için seçilen ölçüt (on_kacma ya da kol_boyu)."""
        return self.esleme.get("ERR_ARM_FORWARD")

    def yon(self, olcut: str) -> int:
        return self.yonler[olcut] if self.yonlu else 0

    def z(self, df: pd.DataFrame) -> pd.DataFrame:
        """Tekrar × hata türü z tablosu (sütunlar esleme sırasıyla; Ex1'de HATALAR)."""
        cikti = {}
        for hata, k in self.olcutler.items():
            cikti[hata] = (olcut_puani(df, k, self.yon(k), self.kaldirma_surumu) - self.medyan[k]) / self.olcek[k]
        return pd.DataFrame(cikti, index=df.index)[self.hatalar]

    def karar(self, df: pd.DataFrame, z: pd.DataFrame | None = None) -> pd.Series:
        return _karar(self.z(df) if z is None else z, self.T)


def _karar(z: pd.DataFrame, T: float) -> pd.Series:
    """max z < T → DOGRU, değilse argmax z (eşitlikte sütun sırasındaki ilk). NaN z dikkate alınmaz."""
    Z = z.to_numpy(float)
    Zd = np.where(np.isnan(Z), -np.inf, Z)
    en = Zd.max(axis=1)
    tur = np.array(list(z.columns), dtype=object)[Zd.argmax(axis=1)]
    return pd.Series(np.where(en < T, DOGRU, tur), index=z.index)


def kural_kur(egitim: pd.DataFrame, esleme, yonlu: bool, kaldirma_surumu: str = VARSAYILAN_KALDIRMA) -> KararKurali:
    """Ölçekleme (eğitimdeki doğru tekrarların medyanı ve IQR'si) ve yönler; T henüz seçilmemiş.
    esleme: hata -> ölçüt sözlüğü; Ex1 için öne kaçma ölçütünün adı da verilebilir."""
    esleme = hata_olcutleri(esleme) if isinstance(esleme, str) else dict(esleme)
    yonler = beklenen_yonler(egitim, esleme, kaldirma_surumu)
    dogru = egitim[egitim.hata == DOGRU]
    medyan, olcek = {}, {}
    for k in esleme.values():
        p = olcut_puani(dogru, k, yonler[k] if yonlu else 0, kaldirma_surumu).dropna()
        q1, q2, q3 = np.percentile(p, [25, 50, 75])
        medyan[k], olcek[k] = float(q2), float(q3 - q1) + EPS
    return KararKurali(esleme, yonlu, yonler, medyan, olcek, kaldirma_surumu=kaldirma_surumu)


def esik_sec(egitim: pd.DataFrame, yonlu: bool, tanim: HataTanimi = EX1,
             kaldirma_surumu: str = VARSAYILAN_KALDIRMA) -> KararKurali:
    """
    Eğitim tekrarlarında makro-F1'i (DOGRU + hatalar, katı) en yükseğe çıkaran ölçüt eşlemesi ve T.
    Tek seçim öne kaçma ölçütüdür (on_kacma / kol_boyu).
    T adayları: eğitimdeki max z dağılımının yüzdelikleri (ESIK_IZGARASI). Eşitlikte ilk aday
    (öne kaçmada on_kacma, T'de küçük olan) seçilir.
    """
    en_iyi = None
    for esleme in tanim.eslemeler():
        kural = kural_kur(egitim, esleme, yonlu, kaldirma_surumu)
        z = kural.z(egitim)
        enz = np.nanmax(np.where(np.isnan(z.to_numpy(float)), -np.inf, z.to_numpy(float)), axis=1)
        for T in np.unique(np.percentile(enz[np.isfinite(enz)], ESIK_IZGARASI)):
            f1 = makro_f1(egitim.hata, _karar(z, T), tanim.siniflar)
            if en_iyi is None or f1 > en_iyi[0] + 1e-12:
                en_iyi = (f1, float(T), kural)
    f1, T, kural = en_iyi
    kural.T = T
    kural.bilgi = {"egitim_makro_f1": f1}
    return kural


# ---------------------------------------------------------------- ilk iki hata
def ilk_iki(z: pd.DataFrame, T: float) -> pd.DataFrame:
    """
    Tekrar başına en yüksek iki z'nin hataları ve kuralın söyleyeceği hatalar.
    Sütunlar: z1_hata, z2_hata (eşikten bağımsız sıralama), z1, z2,
              soylenen1 (max z ≥ T ise z1_hata, değilse DOGRU), soylenen2 (z2 ≥ T ise z2_hata, değilse "").
    Eşitlikte sütun sırası (karar kuralıyla aynı). NaN z dikkate alınmaz.
    """
    Z = z.to_numpy(float)
    Zd = np.where(np.isnan(Z), -np.inf, Z)
    sira = np.argsort(-Zd, axis=1, kind="stable")
    ad = np.array(list(z.columns), dtype=object)
    i = np.arange(len(Zd))
    z1, z2 = Zd[i, sira[:, 0]], Zd[i, sira[:, 1]]
    return pd.DataFrame({"z1_hata": ad[sira[:, 0]], "z2_hata": ad[sira[:, 1]], "z1": z1, "z2": z2,
                         "soylenen1": np.where(z1 >= T, ad[sira[:, 0]], DOGRU),
                         "soylenen2": np.where((z1 >= T) & (z2 >= T), ad[sira[:, 1]], "")}, index=z.index)


# ---------------------------------------------------------------- esnek değerlendirme
def etiket_kumesi(hata: str, ek_hata: str) -> set[str]:
    """Birincil hata + ek hatalar (esnek değerlendirmede bunlardan birini söylemek doğru sayılır)."""
    return {hata} | {e.strip() for e in str(ek_hata).split(",") if e.strip()}


def esnek_gercek(hata: pd.Series, ek_hata: pd.Series, tahmin: pd.Series) -> pd.Series:
    """Esnek gerçek etiket: tahmin etiket kümesindeyse tahmin, değilse birincil hata."""
    return pd.Series([t if t in etiket_kumesi(h, e) else h for h, e, t in zip(hata, ek_hata, tahmin)],
                     index=hata.index)
