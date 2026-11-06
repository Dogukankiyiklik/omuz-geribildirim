"""cekirdek/bindirme.py testleri: referans iskelet kullanıcıya doğru çakıştırılıyor mu?"""
import numpy as np
import pytest

from cekirdek.bindirme import Bindirici, banttan_cikan_kemikler, kare_eslemesi
from cekirdek.veri import EN_BOY


def _yapay_tekrar(n=60):
    """Kalçalar ve omuzlar sabit, sağ kol 0° → 150° → 0° kalkan basit bir iskelet (en-boy düzeltilmiş birimde)."""
    P = np.zeros((n, 33, 2))
    P[:, 23], P[:, 24] = [0.55, 0.60], [0.45, 0.60]   # sol / sağ kalça
    P[:, 11], P[:, 12] = [0.56, 0.40], [0.44, 0.40]   # sol / sağ omuz
    P[:, 7], P[:, 8] = [0.53, 0.33], [0.47, 0.33]     # kulaklar
    P[:, 0], P[:, 2], P[:, 5] = [0.50, 0.33], [0.52, 0.32], [0.48, 0.32]
    aci = np.radians(150 * np.sin(np.linspace(0, np.pi, n)))
    yon = np.stack([-np.sin(aci), np.cos(aci)], 1)     # sağ kol, aşağıdan dışarı-yukarı
    P[:, 14] = P[:, 12] + 0.12 * yon
    P[:, 16] = P[:, 12] + 0.24 * yon
    P[:, 13], P[:, 15] = P[:, 11] + [0, 0.12], P[:, 11] + [0, 0.24]
    return P


def _diziye(P):
    """En-boy düzeltilmiş noktaları veri biçimine (x normalize) çevirir: (kare, 33, 4)."""
    d = np.zeros((P.shape[0], 33, 4))
    d[..., 0] = P[..., 0] / EN_BOY
    d[..., 1] = P[..., 1]
    d[..., 3] = 1
    return d


def test_ayni_tekrar_kendisine_oturur():
    P = _yapay_tekrar()
    b = Bindirici(_diziye(P), _diziye(P))
    assert (b.esleme == np.arange(len(P))).all()
    for j in (0, 20, 45):
        assert np.allclose(b.referans_noktalari(j), P[j], atol=1e-9)


@pytest.mark.parametrize("olcek,derece,kayma", [(1.5, 0, (0.0, 0.0)), (0.7, 8, (0.05, -0.03)), (1.2, -5, (-0.1, 0.02))])
def test_benzerlik_donusumu_geri_alinir(olcek, derece, kayma):
    """Kullanıcı = referansın ölçeklenmiş, döndürülmüş, kaydırılmış hali → bindirilen referans kullanıcıya oturmalı."""
    P = _yapay_tekrar()
    t = np.radians(derece)
    R = np.array([[np.cos(t), -np.sin(t)], [np.sin(t), np.cos(t)]])
    merkez = (P[0, 23] + P[0, 24]) / 2
    Q = ((P - merkez) @ R.T) * olcek + merkez + np.array(kayma)
    b = Bindirici(_diziye(P), _diziye(Q))
    assert b.olcek == pytest.approx(olcek)
    assert b.donus == pytest.approx(t)
    for j in (0, 30, 59):
        assert np.allclose(b.referans_noktalari(j), Q[j], atol=1e-9)


def test_silkme_gizlenmez():
    """Kullanıcının sağ omzu kalkınca referansın omzu onunla birlikte kalkmamalı (ölçek dinlenmeden alınır)."""
    P = _yapay_tekrar()
    Q = P.copy()
    Q[20:40, 12, 1] -= 0.04                       # sağ omuz 20–40. karelerde yukarı (y küçülür)
    b = Bindirici(_diziye(P), _diziye(Q))
    j = 30
    i = b.referans_karesi(j)
    assert b.referans_noktalari(j)[12, 1] == pytest.approx(P[i, 12, 1], abs=1e-3)
    assert Q[j, 12, 1] < b.referans_noktalari(j)[12, 1] - 0.03


def test_kare_eslemesi_yavas_tekrar():
    ref = 90 * np.sin(np.linspace(0, np.pi, 50))
    yavas = 90 * np.sin(np.linspace(0, np.pi, 100))
    e = kare_eslemesi(ref, yavas)
    assert len(e) == 100 and e[0] == 0 and e[-1] == 49
    assert (np.diff(e) >= 0).all()                # zamanda geri gitmez


def test_banttan_cikan_kemikler():
    kh = {"YENI": np.array([0, 0.5]), "M01": np.array([0.2, 0])}
    assert banttan_cikan_kemikler(kh, 0, ["YENI"]) == set()
    assert banttan_cikan_kemikler(kh, 1, ["YENI"]) == {(8, 12)}
    assert banttan_cikan_kemikler(kh, 0, ["YENI", "M01"]) == {(11, 12)}
