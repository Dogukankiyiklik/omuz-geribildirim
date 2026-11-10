"""
Deneyler için ortak sonuç tabloları.

Girdi: uzun biçimli tekrar tablosu. Her satır bir (koşul, tekrar) çiftidir ve şu sütunları taşır:
video, kamera, yonelim, satir, kisi, gorus, hata, ek_hata, bant_<ölçüt>, ve koşulu tanımlayan
anahtar sütunlar (ör. "kosul").

Her ana sonuç iki biçimde verilir: "uygulama senaryosu: önden + çapraz
(|görüş| ≤ 60°)" ve "tüm görüşler". Profil ayrıca (sınırlılık).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from cekirdek import veri

SILKME = "ERR_ELEVATED_SHOULDER"
GORUS_GRUPLARI = ["önden (0–20°)", "çapraz (30–60°)", "profil (70–90°)"]
ONDEN_CAPRAZ = "önden+çapraz"
TUMU = "tüm görüşler"
ONDEN_CAPRAZ_SINIR = 60


def maskeler(df: pd.DataFrame):
    """silkme / doğru / diğer hatalar. Ek hatası silkme olan tekrarlar doğru ve diğer gruplarına girmez."""
    silkme = df.hata == SILKME
    ek_silkme = df.ek_hata.str.contains("ELEVATED")
    dogru = (df.hata == "DOGRU") & ~ek_silkme
    diger = (df.hata != "DOGRU") & ~silkme & ~ek_silkme
    return silkme, dogru, diger


def gorus_maskesi(df: pd.DataFrame, gorus: str) -> pd.Series:
    if gorus == TUMU:
        return pd.Series(True, index=df.index)
    if gorus == ONDEN_CAPRAZ:
        return df.gorus.abs() <= ONDEN_CAPRAZ_SINIR
    return df.gorus.map(veri.gorus_grubu) == gorus


def hizli_auc(poz: np.ndarray, neg: np.ndarray) -> float:
    """AUC (Mann–Whitney), sıra ortalamalarıyla; cekirdek.degerlendirme.auc ile aynı sonuç, NaN'lar atılır."""
    poz = poz[~np.isnan(poz)]
    neg = neg[~np.isnan(neg)]
    if len(poz) == 0 or len(neg) == 0:
        return np.nan
    from scipy.stats import rankdata
    r = rankdata(np.concatenate([poz, neg]))
    return float((r[:len(poz)].sum() - len(poz) * (len(poz) + 1) / 2) / (len(poz) * len(neg)))


def _auc(g: pd.DataFrame, poz, neg, c: str) -> float:
    return hizli_auc(g.loc[poz, c].to_numpy(float), g.loc[neg, c].to_numpy(float))


def auc_ozeti(df: pd.DataFrame, anahtarlar: list[str], olcutler) -> pd.DataFrame:
    """Koşul × ölçüt AUC tablosu: silkme/doğru ve silkme/diğer (tüm görüşler ve önden+çapraz),
    görüş grupları, kişi özeti (silkme/doğru, tüm görüşler), NaN E sayısı."""
    kt = kisi_auc(df, anahtarlar, olcutler)
    satirlar = []
    for anahtar, g in df.groupby(anahtarlar, sort=False, observed=True):
        anahtar = anahtar if isinstance(anahtar, tuple) else (anahtar,)
        s, d, o = maskeler(g)
        oc = gorus_maskesi(g, ONDEN_CAPRAZ)
        for k in olcutler:
            c = f"bant_{k}"
            r = dict(zip(anahtarlar, anahtar))
            r["ölçüt"] = k
            r["AUC silkme/doğru"] = _auc(g, s, d, c)
            r["AUC silkme/diğer"] = _auc(g, s, o, c)
            r[f"AUC silkme/doğru ({ONDEN_CAPRAZ})"] = _auc(g, s & oc, d & oc, c)
            r[f"AUC silkme/diğer ({ONDEN_CAPRAZ})"] = _auc(g, s & oc, o & oc, c)
            for gg in GORUS_GRUPLARI:
                m = gorus_maskesi(g, gg)
                r[f"AUC {gg}"] = _auc(g, s & m, d & m, c)
            sec = kt
            for a, v in zip(anahtarlar, anahtar):
                sec = sec[sec[a] == v]
            v = sec[sec["ölçüt"] == k]["AUC silkme/doğru"]
            r["kişi AUC ort."], r["kişi AUC en düşük"], r["kişi AUC en yüksek"] = v.mean(), v.min(), v.max()
            r["kişi özeti"] = f"{v.mean():.2f} ({v.min():.2f}–{v.max():.2f})".replace(".", ",")
            r["E boş (NaN) tekrar"] = int(g[c].isna().sum())
            satirlar.append(r)
    return pd.DataFrame(satirlar)


def kisi_auc(df: pd.DataFrame, anahtarlar: list[str], olcutler, gorus: str = TUMU) -> pd.DataFrame:
    """Kişi başına AUC silkme/doğru (uzun biçim)."""
    satirlar = []
    for anahtar, g in df.groupby(anahtarlar + ["kisi"], sort=False, observed=True):
        s, d, _ = maskeler(g)
        m = gorus_maskesi(g, gorus)
        for k in olcutler:
            r = dict(zip(anahtarlar + ["kisi"], anahtar))
            r["ölçüt"] = k
            r["AUC silkme/doğru"] = _auc(g, s & m, d & m, f"bant_{k}")
            satirlar.append(r)
    return pd.DataFrame(satirlar)


def kisi_auc_genis(df, anahtarlar, olcutler, gorus: str = TUMU) -> pd.DataFrame:
    kt = kisi_auc(df, anahtarlar, olcutler, gorus)
    return kt.pivot_table(index=anahtarlar + ["ölçüt"], columns="kisi", values="AUC silkme/doğru",
                          sort=False).reset_index()
