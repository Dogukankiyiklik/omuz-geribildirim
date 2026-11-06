"""
Deneyler için ortak sonuç tabloları (Adım 3'ten itibaren).

Girdi: uzun biçimli tekrar tablosu. Her satır bir (koşul, tekrar) çiftidir ve şu sütunları taşır:
video, kamera, yonelim, satir, kisi, gorus, hata, ek_hata, bant_<ölçüt>, ve koşulu tanımlayan
anahtar sütunlar (ör. "bant", "kosul").

Karar 6 (Güncelleme 03): Her ana sonuç iki biçimde verilir: "uygulama senaryosu: önden + çapraz
(|görüş| ≤ 60°)" ve "tüm görüşler". Profil ayrıca (sınırlılık).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from cekirdek import veri
from cekirdek.degerlendirme import guven_araligi, kisi_bootstrap, psi
from deneyler.deney1 import GORUS_GRUPLARI, SILKME, maskeler

TEKRAR_ANAHTARI = ["video", "kamera", "yonelim", "satir", "kisi", "hata", "ek_hata", "gorus"]
ONDEN_CAPRAZ = "önden+çapraz"
TUMU = "tüm görüşler"
ONDEN_CAPRAZ_SINIR = 60


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
    görüş grupları, kişi özeti (silkme/doğru, tüm görüşler), Ψ, NaN E sayısı."""
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
            r["Ψ (M39)"] = psi(g[g[c].notna()], c, SILKME)
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


def fark_bootstrap(df: pd.DataFrame, kosul_sutunu: str, farklar, n: int = 2000, tohum: int = 1,
                   ayrimlar=("silkme/doğru",), gorusler=(TUMU, ONDEN_CAPRAZ)) -> pd.DataFrame:
    """
    Koşullar arası AUC farkları için kişi bazlı, eşleştirilmiş bootstrap %95 GA.
    farklar: [(ölçüt, x, y), ...] → "AUC(x) − AUC(y)"; x, y kosul_sutunu değerleri.
    """
    olcutler = sorted({k for k, _, _ in farklar})
    kosullar = sorted({x for _, x, _ in farklar} | {y for _, _, y in farklar})
    d0 = df[df[kosul_sutunu].astype(str).isin(kosullar)].copy()
    d0[kosul_sutunu] = d0[kosul_sutunu].astype(str)
    genis = d0.set_index(TEKRAR_ANAHTARI + [kosul_sutunu])[[f"bant_{k}" for k in olcutler]].unstack(kosul_sutunu)
    genis.columns = [f"{a}_{b}" for a, b in genis.columns]
    genis = genis.reset_index()

    def istatistik(b):
        s, d, o = maskeler(b)
        neg = {"silkme/doğru": d, "silkme/diğer": o}
        cikti = {}
        for gorus in gorusler:
            m = gorus_maskesi(b, gorus)
            for ayrim in ayrimlar:
                for k, x, y in farklar:
                    ax = _auc(b, s & m, neg[ayrim] & m, f"bant_{k}_{x}")
                    ay = _auc(b, s & m, neg[ayrim] & m, f"bant_{k}_{y}")
                    cikti["|".join((gorus, ayrim, k, x, y))] = ax - ay
        return cikti

    nokta = istatistik(genis)
    bs = kisi_bootstrap(genis, istatistik, n=n, tohum=tohum)
    satirlar = []
    for c in bs.columns:
        alt, ust = guven_araligi(bs[c])
        gorus, ayrim, k, x, y = c.split("|")
        satirlar.append({"görüş": gorus, "ayrım": ayrim, "ölçüt": k, "fark": f"{x} − {y}",
                         "nokta tahmini": nokta[c], "bootstrap ort.": bs[c].mean(),
                         "GA %2,5": alt, "GA %97,5": ust, "GA sıfırı içeriyor": bool(alt <= 0 <= ust)})
    return pd.DataFrame(satirlar)
