"""Arşiv: Deney 1c (zamansal yumuşatma) testi; çalışır hâli v-sunum etiketinde."""
import numpy as np


def test_yumusatma():
    """One Euro ve Savitzky–Golay: sabit sinyali bozmaz, gürültüyü azaltır, z/görünürlüğe dokunmaz."""
    from cekirdek.yumusatma import yumusat
    rng = np.random.default_rng(0)
    n = 120
    temiz = np.zeros((n, 33, 4))
    temiz[:, :, 1] = np.sin(np.linspace(0, np.pi, n))[:, None] * 0.1 + 0.5
    temiz[:, :, 0] = 0.3
    temiz[:, :, 2] = 7.0
    temiz[:, :, 3] = 0.9
    gurultulu = temiz.copy()
    gurultulu[..., :2] += rng.normal(0, 0.003, (n, 33, 2))
    for y, p in [("one_euro", {"min_kesim": 1.0, "beta": 1.0}), ("savgol", {"pencere": 9, "derece": 2})]:
        sabit = yumusat(temiz[:, :, :], y, **p)
        assert np.allclose(sabit[:, :, 0], 0.3)
        out = yumusat(gurultulu, y, **p)
        assert np.array_equal(out[..., 2:], gurultulu[..., 2:])
        assert np.std(np.diff(out[..., 1], n=2, axis=0)) < 0.5 * np.std(np.diff(gurultulu[..., 1], n=2, axis=0))
    assert yumusat(gurultulu, "yok") is gurultulu
