"""
Kamera açısı uyarısı.

Oran = dinlenmede (tekrar öncesi ilk 8 kare) omuz genişliği / gövde boyu, en-boy düzeltmeli, karelerin
medyanı. Kişi kameraya döndükçe 2B'de omuz çizgisi kısalır ve oran düşer. Eşik, veri setinin çapraz
(30–60°) doğru tekrarlarındaki oranın 10. yüzdeliğidir (deneyler/kamera_acisi.py hesaplar,
modeller/kamera_esigi.json'a yazar). Oran eşiğin altındaysa uyarı gösterilir; kalibrasyon engellenmez.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from cekirdek.ozellikler import DINLENME_KARE, Iskelet
from cekirdek.veri import EN_BOY, KOK

ESIK_DOSYASI = KOK / "modeller" / "kamera_esigi.json"
UYARI = "Kameraya daha önden durun."


def omuz_govde_orani(dizi: np.ndarray, en_boy: float = EN_BOY, kare: int = DINLENME_KARE) -> float:
    """Dizinin ilk `kare` karesinde omuz genişliği / gövde boyu oranının medyanı."""
    s = Iskelet(np.asarray(dizi)[:kare], en_boy)
    genislik = np.linalg.norm(s.p(11) - s.p(12), axis=1)
    with np.errstate(invalid="ignore", divide="ignore"):
        return float(np.nanmedian(genislik / s.govde))


def esik_oku(yol=ESIK_DOSYASI) -> float:
    return float(json.loads(Path(yol).read_text(encoding="utf-8"))["esik"])


def uyari_gerekli(oran: float, esik: float) -> bool:
    return bool(np.isfinite(oran) and oran < esik)
