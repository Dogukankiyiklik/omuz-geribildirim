"""
Kişiye özel tolerans bandı (M39).

Kişinin birkaç doğru tekrarı DTW ile bir referans tekrara hizalanır; her referans karesi için
ortalama (μ) ve %95 güven aralığı yarıçapı (τ) hesaplanır. Bir tekrarın "bant hatası" E,
banttan ne kadar taştığının kareler üzerinden ortalamasıdır (0 = hep bant içinde, 1 = çok dışında).
"""
from __future__ import annotations

import numpy as np
from scipy import stats

from cekirdek.hizalama import hizala


def bant_modeli(dogrular: list[dict], rng: np.random.Generator, olcutler) -> dict:
    """
    M39: doğru tekrarlardan rastgele biri referans seçilir, diğerleri ona hizalanır;
    kare başına μ ve τ (%95 GA, t dağılımı). τ, alt sınır olarak kendi Q1'inden küçük olamaz
    (M39: çok dar aralıklar yüzünden her küçük sapma hata sayılmasın).

    Dönüş: {"ref_kol": ..., ölçüt: (μ, τ), ...}
    """
    r = rng.integers(len(dogrular))
    return bant_modeli_ref(dogrular, r, olcutler)


def bant_modeli_ref(dogrular: list[dict], r: int, olcutler) -> dict:
    """bant_modeli ile aynı, ama referans tekrar (r. doğru tekrar) dışarıdan verilir."""
    ref = dogrular[r]
    hizali = [ref] + [hizala(ref["kol"], t, olcutler) for i, t in enumerate(dogrular) if i != r]
    model = {"ref_kol": ref["kol"], "ref_indeks": int(r)}
    n = len(hizali)
    tq = stats.t.ppf(0.975, max(n - 1, 1))
    for k in olcutler:
        X = np.vstack([h[k] for h in hizali])
        mu = X.mean(0)
        tau = tq * X.std(0, ddof=1) / np.sqrt(n) if n > 1 else np.zeros_like(mu)
        tau = np.maximum(tau, np.percentile(tau, 25) + 1e-9)
        model[k] = (mu, tau)
    return model


def kare_hatasi(h: np.ndarray, mu: np.ndarray, tau: np.ndarray, yon: int = 0) -> np.ndarray:
    """
    Kare başına bant dışı hata, 0–1 arası: bant içinde 0; dışında (sapma − τ)/τ, en fazla 1.

    yon = 0  : yönsüz (M39, referans) — iki yöndeki sapma da sayılır.
    yon = +1 : yalnızca bandın ÜSTÜNE çıkış sayılır.
    yon = −1 : yalnızca bandın ALTINA iniş sayılır.
    """
    if yon == 0:
        sapma = np.abs(h - mu)
    else:
        sapma = np.maximum(np.sign(yon) * (h - mu), 0.0)
    return np.where(sapma <= tau, 0, np.minimum(1, (sapma - tau) / tau))


def bant_hatasi(model: dict, tekrar: dict, olcutler, yon: dict[str, int] | None = None,
                ayrinti: bool = False):
    """
    Tekrarın her ölçüt için bant hatası E (kare hatalarının ortalaması).
    yon: ölçüt -> 0/+1/−1 (verilmezse hepsi yönsüz). ayrinti=True ise hizalı diziler ve
    kare hataları da döner (görsel kontrol ve geri bildirim için).
    """
    yon = yon or {}
    h = hizala(model["ref_kol"], tekrar, olcutler)
    E, kareler = {}, {}
    for k in olcutler:
        mu, tau = model[k]
        e = kare_hatasi(h[k], mu, tau, yon.get(k, 0))
        E[k] = e.mean()
        kareler[k] = e
    if ayrinti:
        return E, {"hizali": h, "kare_hatasi": kareler}
    return E


def coklu_referans_hatasi(dogrular: list[dict], tekrar: dict, olcutler,
                          yon: dict[str, int] | None = None) -> dict[str, float]:
    """
    Çoklu referans: modeldeki her doğru tekrar sırayla referans yapılır,
    bant kurulur ve E hesaplanır; E'lerin ortalaması döner. Rastgele referans seçimi ortadan kalkar.
    """
    return coklu_model_hatasi(coklu_referans_modelleri(dogrular, olcutler), tekrar, olcutler, yon)


def coklu_referans_modelleri(dogrular: list[dict], olcutler) -> list[dict]:
    """Çoklu referansın bantları: her doğru tekrar sırayla referans (n model). Aynı model kümesiyle
    birçok tekrar değerlendirilecekse (ör. genel bant, Deney 1b) bir kez kurulup yeniden kullanılır."""
    return [bant_modeli_ref(dogrular, r, olcutler) for r in range(len(dogrular))]


def coklu_model_hatasi(modeller: list[dict], tekrar: dict, olcutler,
                       yon: dict[str, int] | None = None) -> dict[str, float]:
    """Hazır çoklu referans modelleriyle E: her modelde bant hatası, ölçüt başına ortalama."""
    Es = [bant_hatasi(m, tekrar, olcutler, yon) for m in modeller]
    return {k: float(np.mean([e[k] for e in Es])) for k in olcutler}


def coklu_model_puanlari(modeller: list[dict], tekrar: dict, olcutler, yonler=(0, 1, -1)):
    """
    Deney 2 için tek geçişte (hizalama her referansta bir kez): her ölçüt ve yön için çoklu referans
    E'si (coklu_model_hatasi ile aynı hesap) ve her ölçüt için ortalama imzalı fark (hizalı h − μ).
    Dönüş: (E[(ölçüt, yön)], fark[ölçüt])
    """
    E = {(k, y): [] for k in olcutler for y in yonler}
    fark = {k: [] for k in olcutler}
    for m in modeller:
        h = hizala(m["ref_kol"], tekrar, olcutler)
        for k in olcutler:
            mu, tau = m[k]
            for y in yonler:
                E[(k, y)].append(kare_hatasi(h[k], mu, tau, y).mean())
            fark[k].append(np.mean(h[k] - mu))
    return ({a: float(np.mean(v)) for a, v in E.items()}, {k: float(np.mean(v)) for k, v in fark.items()})
