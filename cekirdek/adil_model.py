"""
Adil model: hatalı bir tekrar, doğru tekrarlarla AYNI SAYIDA (n−1) doğru tekrardan kurulan modelle
değerlendirilir. Böylece doğru ve hatalı tekrarlar eşit koşulda karşılaştırılır.

Her doğru tekrar SIRAYLA dışarıda bırakılır, n model kurulur ve E'lerin ortalaması alınır. Böylece
hatalı tekrarların E'si rastgelelikten bağımsız (deterministik) olur. Doğru tekrarlar zaten
birini-dışarıda-bırak ile değerlendirilir; onlar için bu fonksiyon gerekmez.

Bu bir deney protokolüdür: uygulamada kalibrasyonun bütün tekrarları tek bir modele girer.
"""
from __future__ import annotations

import warnings
from typing import Callable

import numpy as np


def birini_disarida_alt_kumeler(dogrular: list) -> list[list]:
    """n elemanlı listeden, her biri bir elemanı dışarıda bırakan n alt küme (sırayla)."""
    return [[u for j, u in enumerate(dogrular) if j != i] for i in range(len(dogrular))]


def ortalama_E(Eler: list[dict[str, float]], olcutler) -> dict[str, float]:
    """Ölçüt başına E ortalaması. NaN E'ler (açı bandında geçerli karesi olmayan model) atlanır;
    hepsi NaN ise NaN."""
    cikti = {}
    for k in olcutler:
        v = np.array([e[k] for e in Eler], dtype=np.float64)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            cikti[k] = float(np.nanmean(v)) if np.any(~np.isnan(v)) else np.nan
    return cikti


def adil_ortalama_hata(dogrular: list, hata: Callable[[list], tuple[dict, dict]], olcutler):
    """
    Her (n−1)'li alt küme için hata(alt_kume) -> (E, ek) çağrılır; E'lerin ortalaması döner.

    Dönüş: (E_ortalama, ekler) — ekler: her alt kümenin (E, ek) çifti, sırayla (i. eleman = i. doğru
    tekrar dışarıda). Çağıran taraf ek bilgileri (ör. kapsam) kendi kuralıyla birleştirir.
    """
    sonuclar = [hata(alt) for alt in birini_disarida_alt_kumeler(dogrular)]
    return ortalama_E([E for E, _ in sonuclar], olcutler), sonuclar
