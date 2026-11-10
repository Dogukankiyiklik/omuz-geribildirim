"""Değerlendirme: AUC, ham skor, karışıklık matrisi ve makro-F1."""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

from cekirdek.ozellikler import DINLENME_KARE


def auc(poz, neg) -> float:
    """ROC eğrisi altındaki alan (Mann–Whitney U / (n_poz · n_neg)). 0,5 = rastgele, 1 = mükemmel ayrım."""
    poz, neg = np.asarray(poz), np.asarray(neg)
    if len(poz) == 0 or len(neg) == 0:
        return np.nan
    return stats.mannwhitneyu(poz, neg, alternative="two-sided").statistic / (len(poz) * len(neg))


def ham_skor(tekrar: dict, olcutler) -> dict[str, float]:
    """Kişiye özel model olmadan: tekrar başına göre mutlak sapmanın %90 yüzdeliği."""
    return {k: np.percentile(np.abs(tekrar[k] - np.median(tekrar[k][:DINLENME_KARE])), 90) for k in olcutler}


# ---------------------------------------------------------------- çok sınıflı sınıflandırma (Deney 2)
def karisiklik(gercek, tahmin, siniflar) -> pd.DataFrame:
    """Karışıklık matrisi: satır = gerçek, sütun = tahmin (sayılar)."""
    g = pd.Categorical(np.asarray(gercek, dtype=object), categories=siniflar)
    t = pd.Categorical(np.asarray(tahmin, dtype=object), categories=siniflar)
    return pd.crosstab(g, t, dropna=False).reindex(index=siniflar, columns=siniflar, fill_value=0)


def sinif_metrikleri(gercek, tahmin, siniflar) -> pd.DataFrame:
    """Sınıf başına destek, duyarlılık, kesinlik, F1 (tanımsız olanlar 0, sklearn'ün zero_division=0'ı gibi)."""
    m = karisiklik(gercek, tahmin, siniflar).to_numpy(float)
    dp = np.diag(m)
    destek, tahmin_say = m.sum(1), m.sum(0)
    duy = np.divide(dp, destek, out=np.zeros_like(dp), where=destek > 0)
    kes = np.divide(dp, tahmin_say, out=np.zeros_like(dp), where=tahmin_say > 0)
    f1 = np.divide(2 * duy * kes, duy + kes, out=np.zeros_like(dp), where=(duy + kes) > 0)
    return pd.DataFrame({"sınıf": siniflar, "destek": destek.astype(int), "duyarlılık": duy,
                         "kesinlik": kes, "F1": f1})


def makro_f1(gercek, tahmin, siniflar) -> float:
    """Desteği olan sınıfların F1 ortalaması."""
    s = sinif_metrikleri(gercek, tahmin, siniflar)
    return float(s.loc[s.destek > 0, "F1"].mean())
