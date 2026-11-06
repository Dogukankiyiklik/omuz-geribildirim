"""
Açı bandı: kol açısına koşullu kişiye özel tolerans bandı (Güncelleme 02, Karar 2).

Soru: "Kol θ derecedeyken bu kişinin omzu normalde nerede?"
Zaman bandı (M39, cekirdek/bant.py) tekrarları DTW ile zamanda hizalar; kol farklı yüksekliğe
kalkınca omuz farklı kol açılarında karşılaştırılır (Adım 2b, Petra bulgusu). Açı bandında zaman
ekseni yoktur: her kare, kolun o anki açısına ve hareketin fazına göre karşılaştırılır. Referans
tekrar gerekmez, bu yüzden rastgelelik de yoktur.

Tanım (parametreler önceden sabitlendi; test verisine bakarak DEĞİŞTİRİLMEZ):
  1. Yalnızca etiketli tekrar kareleri kullanılır (Karar 3; çağıran taraf keser).
  2. Faz: 5 karelik hareketli medyanla yumuşatılmış kol açısının en büyük olduğu kareye kadar
     (tepe dahil) "kaldırma", sonrası "indirme".
  3. Kutular: 0–180°, 5° genişlik, faz başına ayrı (2 × 36 kutu). Kare, ham kol açısıyla kutulanır.
  4. Her kalibrasyon tekrarı her kutuya bir değer verir (o kutuya düşen karelerin ortalaması);
     n = katkı veren tekrar sayısı. μ = ortalama, τ = t(0,975; n−1)·s/√n.
     Alt sınır: geçerli kutulardaki τ'ların birinci çeyreği (M39 ile aynı; iki faz birlikte).
  5. Geçerli kutu: en az 3 tekrar katkı verir. Faz içinde ilk ve son geçerli kutu arasındaki
     boşluklar μ ve τ için doğrusal ara değerle doldurulur. Kalibrasyon aralığının dışı geçersiz.
  6. Değerlendirme: her kare kendi faz/kutusunun (μ, τ)'su ile M39 kare hatasıyla karşılaştırılır
     (yönsüz veya yönlü). E = geçerli karelerin ortalaması. Ayrıca kapsam (geçerli kare oranı)
     ve aralik_disi bayrağı: karelerin %20'sinden fazlası kalibrasyonun en yüksek açısının
     5°'den fazla üstündeyse.
  7. Kalibrasyon aralığı dışındaki kareler değerlendirilmez (o açıda kişinin normalini bilmiyoruz).

Yalnızca duruş ölçütleri içindir (omuz, baş, dirsek, öne kaçma). Kol açısının kendisi için
anlamsızdır; "yetersiz kaldırma" Adım 4'te tepe açısıyla ayrı ele alınır.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache

import numpy as np
from scipy import stats
from scipy.ndimage import median_filter

from cekirdek.bant import kare_hatasi

KUTU_GENISLIGI = 5.0      # derece
KUTU_SAYISI = 36          # 0–180°
EN_AZ_TEKRAR = 3          # geçerli kutu için en az katkı veren tekrar
MEDYAN_PENCERE = 5        # faz için kol açısı yumuşatma (kare)
ARALIK_PAYI = 5.0         # aralik_disi: kalibrasyonun en yüksek açısının bu kadar üstü
ARALIK_ORANI = 0.20       # aralik_disi: bu orandan fazla kare
KALDIRMA, INDIRME = 0, 1
FAZ_ADLARI = {KALDIRMA: "kaldırma", INDIRME: "indirme"}


def yumusak_kol(kol: np.ndarray) -> np.ndarray:
    """5 karelik hareketli medyan (kenarlarda en yakın değer tekrarlanır)."""
    return median_filter(np.asarray(kol, np.float64), size=MEDYAN_PENCERE, mode="nearest")


def fazlar(kol: np.ndarray) -> tuple[np.ndarray, int]:
    """Kare başına faz (0 = kaldırma, 1 = indirme) ve tepe karesinin indeksi."""
    tepe = int(np.argmax(yumusak_kol(kol)))
    faz = np.full(len(kol), KALDIRMA, dtype=np.int64)
    faz[tepe + 1:] = INDIRME
    return faz, tepe


def tepe_acisi(kol: np.ndarray) -> float:
    """Tekrarın en yüksek kol açısı (yumuşatılmış eğriden)."""
    return float(np.max(yumusak_kol(kol)))


def kutular(kol: np.ndarray) -> np.ndarray:
    """Kare başına kutu indeksi 0–35 (180° son kutuya düşer)."""
    return np.clip(np.floor(np.asarray(kol) / KUTU_GENISLIGI).astype(np.int64), 0, KUTU_SAYISI - 1)


@lru_cache(maxsize=None)
def _tq(n: int) -> float:
    """t(0,975; n−1)."""
    return float(stats.t.ppf(0.975, n - 1))


def kutu_merkezleri() -> np.ndarray:
    return (np.arange(KUTU_SAYISI) + 0.5) * KUTU_GENISLIGI


@dataclass
class AciBandi:
    """Kişiye özel açı bandı. Diziler (2 faz, 36 kutu) biçimindedir."""
    mu: dict[str, np.ndarray]
    tau: dict[str, np.ndarray]
    gecerli: np.ndarray        # ara değer dahil değerlendirilebilir kutular
    destek: np.ndarray         # kutuya katkı veren tekrar sayısı
    en_yuksek_aci: float       # kalibrasyon tekrarlarının tepe açılarının en büyüğü
    tepe_acilari: list[float] = field(default_factory=list)
    olcutler: tuple[str, ...] = ()


def _ara_deger(y: np.ndarray, gecerli0: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Bir fazın kutu dizisinde ilk–son geçerli kutu arasını doğrusal ara değerle doldurur."""
    idx = np.flatnonzero(gecerli0)
    cikti = np.full_like(y, np.nan)
    aralik = np.zeros_like(gecerli0)
    if len(idx) == 0:
        return cikti, aralik
    x = np.arange(idx[0], idx[-1] + 1)
    cikti[x] = np.interp(x, idx, y[idx])
    aralik[x] = True
    return cikti, aralik


def aci_bandi_modeli(dogrular: list[dict], olcutler) -> AciBandi:
    """
    Kalibrasyon (doğru) tekrarlarından açı bandı. dogrular: ölçüt sözlükleri ("kol" + ölçütler),
    yalnızca etiketli kareler.
    """
    olcutler = tuple(olcutler)
    n_t = len(dogrular)
    degerler = {k: np.full((n_t, 2, KUTU_SAYISI), np.nan) for k in olcutler}
    tepeler = []
    for i, f in enumerate(dogrular):
        faz, _ = fazlar(f["kol"])
        kutu = kutular(f["kol"])
        tepeler.append(tepe_acisi(f["kol"]))
        hucre = faz * KUTU_SAYISI + kutu  # (faz, kutu) -> tek indeks
        say = np.bincount(hucre, minlength=2 * KUTU_SAYISI)
        dolu = say > 0
        for k in olcutler:
            top = np.bincount(hucre, weights=f[k], minlength=2 * KUTU_SAYISI)
            d = np.full(2 * KUTU_SAYISI, np.nan)
            d[dolu] = top[dolu] / say[dolu]
            degerler[k][i] = d.reshape(2, KUTU_SAYISI)

    # Katkı veren tekrar sayısı kol açısından (kare varlığından) sayılır.
    destek = np.zeros((2, KUTU_SAYISI), dtype=np.int64)
    for f in dogrular:
        faz, _ = fazlar(f["kol"])
        dolu = np.zeros((2, KUTU_SAYISI), dtype=bool)
        dolu[faz, kutular(f["kol"])] = True
        destek += dolu
    gecerli0 = destek >= EN_AZ_TEKRAR
    hucreler = list(zip(*np.nonzero(gecerli0)))

    mu, tau = {}, {}
    gecerli = np.zeros_like(gecerli0)
    for k in olcutler:
        X = degerler[k]
        m = np.full((2, KUTU_SAYISI), np.nan)
        t_ = np.full((2, KUTU_SAYISI), np.nan)
        for p, b in hucreler:
            v = X[:, p, b]
            v = v[~np.isnan(v)]
            if len(v) >= 2:
                m[p, b] = v.mean()
                t_[p, b] = _tq(len(v)) * v.std(ddof=1) / np.sqrt(len(v))
        ok = ~np.isnan(t_)
        if ok.any():
            t_[ok] = np.maximum(t_[ok], np.percentile(t_[ok], 25) + 1e-9)
        mu_k, tau_k = np.full_like(m, np.nan), np.full_like(m, np.nan)
        for p in (KALDIRMA, INDIRME):
            mu_k[p], aralik = _ara_deger(m[p], ok[p])
            tau_k[p], _ = _ara_deger(t_[p], ok[p])
            gecerli[p] = aralik
        mu[k], tau[k] = mu_k, tau_k
    return AciBandi(mu=mu, tau=tau, gecerli=gecerli, destek=destek,
                    en_yuksek_aci=float(max(tepeler)), tepe_acilari=tepeler, olcutler=olcutler)


def aci_bandi_hatasi(model: AciBandi, tekrar: dict, olcutler, yon: dict[str, int] | None = None,
                     ayrinti: bool = False):
    """
    Tekrarın her ölçüt için açı bandı hatası E (geçerli karelerin ortalaması; geçerli kare yoksa NaN).
    Dönüş: (E, ek) — ek: kapsam, aralik_disi; ayrinti=True ise kare başına faz, kutu, geçerlilik,
    μ, τ ve kare hataları (geçersiz karelerde NaN), ayrıca (Adım 5'teki "normalde X, sende Y"
    cümleleri için):
      kol       : kare başına kol açısı (°)
      deger     : ölçütün ham değeri (ölçüt -> dizi)
      fark      : imzalı fark h − μ (geçersiz karelerde NaN)
      bant_disi : imzalı bant dışı büyüklük: h > μ + τ ise (h − μ − τ) > 0, h < μ − τ ise
                  (h − μ + τ) < 0, bant içinde 0 (geçersiz karelerde NaN)
    """
    yon = yon or {}
    kol = tekrar["kol"]
    faz, tepe = fazlar(kol)
    kutu = kutular(kol)
    g = model.gecerli[faz, kutu]
    ek = {"kapsam": float(g.mean()),
          "aralik_disi": bool(np.mean(kol > model.en_yuksek_aci + ARALIK_PAYI) > ARALIK_ORANI),
          "tepe_acisi": tepe_acisi(kol)}
    E, kareler, mus, taus = {}, {}, {}, {}
    for k in olcutler:
        mu = model.mu[k][faz, kutu]
        tau = model.tau[k][faz, kutu]
        e = np.full(len(kol), np.nan)
        if g.any():
            e[g] = kare_hatasi(tekrar[k][g], mu[g], tau[g], yon.get(k, 0))
        E[k] = float(e[g].mean()) if g.any() else np.nan
        kareler[k], mus[k], taus[k] = e, mu, tau
    if ayrinti:
        fark, disi = {}, {}
        for k in olcutler:
            d = np.where(g, tekrar[k] - mus[k], np.nan)
            fark[k] = d
            disi[k] = np.where(np.isnan(d), np.nan, np.sign(d) * np.maximum(np.abs(d) - taus[k], 0.0))
        ek.update({"faz": faz, "tepe": tepe, "kutu": kutu, "gecerli": g,
                   "kare_hatasi": kareler, "mu": mus, "tau": taus,
                   "kol": np.asarray(kol), "deger": {k: np.asarray(tekrar[k]) for k in olcutler},
                   "fark": fark, "bant_disi": disi})
    return E, ek


def aci_bandi_puanlari(model: AciBandi, tekrar: dict, olcutler, yonler=(0, 1, -1)):
    """
    Deney 2 için tek geçişte: her ölçüt ve yön için E (aci_bandi_hatasi ile aynı hesap), her ölçüt
    için geçerli karelerdeki ortalama imzalı fark (h − μ; beklenen yönü bulmak için) ve ek bilgiler.
    Dönüş: (E[(ölçüt, yön)], fark[ölçüt], ek) — geçerli kare yoksa NaN.
    """
    _, ek = aci_bandi_hatasi(model, tekrar, olcutler, ayrinti=True)
    g = ek["gecerli"]
    E, fark = {}, {}
    for k in olcutler:
        mu, tau = ek["mu"][k][g], ek["tau"][k][g]
        for y in yonler:
            E[(k, y)] = float(kare_hatasi(tekrar[k][g], mu, tau, y).mean()) if g.any() else np.nan
        fark[k] = float(np.mean(tekrar[k][g] - mu)) if g.any() else np.nan
    return E, fark, ek


def aci_eslemesi(ref_kol: np.ndarray, kul_kol: np.ndarray) -> np.ndarray:
    """
    Görselleştirme için: kullanıcının her karesine, referans tekrarda AYNI FAZDA ve kol açısı en yakın
    kare. (Zaman bandındaki DTW eşlemesinin açı bandındaki karşılığı; yalnızca bindirme için.)
    """
    rf, _ = fazlar(ref_kol)
    kf, _ = fazlar(kul_kol)
    cikti = np.empty(len(kul_kol), dtype=np.int64)
    for j in range(len(kul_kol)):
        aday = np.flatnonzero(rf == kf[j])
        if len(aday) == 0:
            aday = np.arange(len(ref_kol))
        cikti[j] = aday[np.argmin(np.abs(ref_kol[aday] - kul_kol[j]))]
    return cikti
