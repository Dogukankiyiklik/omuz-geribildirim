"""Adım 0 testleri: orijinal veriden okuma, tekrar sayıları ve küçültülmüş npz ile eşdeğerlik."""
import os
from pathlib import Path

import numpy as np
import pytest

from cekirdek import veri

VERI_VAR = veri.ISKELET_ZIP.exists() and veri.SEGMENTASYON.exists()
# Eşdeğerlik testi için npz yolu ortam değişkeniyle değiştirilebilir.
NPZ = Path(os.environ.get("REHAB26_KUCUK_NPZ", veri.KUCUK_NPZ))

gerekli = pytest.mark.skipif(not VERI_VAR, reason="veri/rehab26 altında orijinal dosyalar yok")


def test_gorus_acisi_ve_grubu():
    assert veri.gorus_acisi("cam1", 0) == 0
    assert veri.gorus_acisi("cam2", 0) == 45
    assert veri.gorus_acisi("cam3", 90) == 0
    assert veri.gorus_acisi("cam1", 90) == -90
    assert veri.gorus_grubu(-10) == "önden (0–20°)"
    assert veri.gorus_grubu(45) == "çapraz (30–60°)"
    assert veri.gorus_grubu(-90) == "profil (70–90°)"


def test_en_boy():
    assert veri.EN_BOY == pytest.approx(9 / 16)


@pytest.fixture(scope="module")
def ex1_zip():
    return veri.tekrarlari_yukle(1, kaynak="zip")


@gerekli
def test_ex1_tekrar_sayilari(ex1_zip):
    seg = veri.segmentasyon_oku()
    e1 = seg[seg.exercise_id == 1]
    assert len(ex1_zip) == 3 * len(e1)
    # Her satır her kamerada bir kez var ve etiketler Segmentation.csv ile aynı
    from collections import Counter
    sayac = Counter((t.satir, t.kamera) for t in ex1_zip)
    assert set(sayac.values()) == {1}
    assert {s for s, _ in sayac} == set(e1.index)
    for t in ex1_zip[::50]:
        r = seg.loc[t.satir]
        assert t.video == r.video_id and t.yonelim == r.person_orientation
        assert t.dogru == (r.correctness_score == 1)
        assert t.hata == (r.error_description or "DOGRU")
        # Uzunluk: tekrar + iki uçta 10'ar kare pay (videonun başında kırpılabilir)
        assert len(t.dizi) == r.last_frame - max(0, r.first_frame - 10) + 11
        assert t.dizi.shape[1:] == (33, 4) and t.dizi.dtype == np.float64
    assert len(veri.gruplara_ayir(ex1_zip)) == 3 * e1.groupby(["video_id", "person_orientation"]).ngroups


@gerekli
@pytest.mark.skipif(not NPZ.exists(), reason=f"{NPZ} yok; eşdeğerlik testi atlandı")
def test_kucuk_npz_esdegerlik(ex1_zip):
    """Orijinal veriden okunan 13 eklem, rehab26_kucuk.npz ile float16 yuvarlaması içinde aynı olmalı."""
    npz = {(t.satir, t.kamera): t for t in veri.tekrarlari_yukle(1, kaynak="npz", npz_yolu=NPZ)}
    assert len(npz) == len(ex1_zip), "npz'deki Ex1 tekrar parçası sayısı farklı"
    en_buyuk = 0.0
    for t in ex1_zip:
        k = npz[(t.satir, t.kamera)]
        assert k.dizi.shape == t.dizi.shape
        assert k.ilk_kare == t.ilk_kare
        fark = np.abs(k.dizi[:, veri.EKLEMLER_13] - t.dizi[:, veri.EKLEMLER_13]).max()
        en_buyuk = max(en_buyuk, fark)
    print(f"\nEn büyük mutlak fark (13 eklem, 4 sütun): {en_buyuk:.6g}")
    assert en_buyuk <= 1e-3
