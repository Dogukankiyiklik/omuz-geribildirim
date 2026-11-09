"""uygulama/main.py pencere ölçekleme (yalnızca gösterim): oran korunur, tıklama geri çevrilir."""
import numpy as np

from uygulama import main as um


def test_sigdir_oran_korunur_ve_ortalanir():
    img = np.full((760, 1028, 3), 200, np.uint8)
    tuval, k, ox, oy = um.sigdir(img, 1920, 1080)
    assert tuval.shape == (1080, 1920, 3)
    assert abs(k - 1080 / 760) < 1e-9 and oy == 0 and ox > 0
    nw = int(round(1028 * k))
    assert (tuval[:, ox:ox + nw] == 200).all()                    # görüntü yayılmadı
    assert (tuval[:, :ox] == um.KENAR_RENGI[0]).all()             # kenarlar koyu


def test_tiklama_geri_cevrilir():
    img = np.zeros((760, 1028, 3), np.uint8)
    _, k, ox, oy = um.sigdir(img, 1920, 1080)
    um.GORUNUM.update(k=k, ox=ox, oy=oy)
    x, y = um.goruntu_koordinati(ox + 500 * k, oy + 300 * k)
    assert abs(x - 500) < 1e-6 and abs(y - 300) < 1e-6
    um.GORUNUM.update(k=1.0, ox=0, oy=0)
