"""
Uygulamanın karar kuralı dosyası.

Uygulamada test kişisi yoktur; kural beş kişinin hepsinin önden + çapraz tekrarlarıyla, LOSO'daki eğitim
adımıyla birebir aynı prosedürle kurulur (ht.esik_sec + gb.siddet_esikleri). Dosyayı
araclar/kural_disa_aktar.py üretir; uygulama `yukle` ile okur. Böylece uygulamanın kararı, deneyde
ölçülen kararla aynı koddan gelir (ht.KararKurali).
"""
from __future__ import annotations

import json
from pathlib import Path

from cekirdek import hata_turu as ht

SURUM = 1


def kaydet(kural: ht.KararKurali, siddet_esikleri: dict, yol, bilgi: dict | None = None) -> None:
    veri = {
        "dosya_surumu": SURUM,
        "esleme": kural.esleme,
        "yonlu": bool(kural.yonlu),
        "yonler": {k: int(v) for k, v in kural.yonler.items()},
        "medyan": {k: float(v) for k, v in kural.medyan.items()},
        "olcek": {k: float(v) for k, v in kural.olcek.items()},
        "T": float(kural.T),
        "kaldirma_surumu": kural.kaldirma_surumu,
        "siddet_esikleri": {h: [float(q1), float(q2)] for h, (q1, q2) in siddet_esikleri.items()},
        "bilgi": {**{k: v for k, v in kural.bilgi.items()}, **(bilgi or {})},
    }
    yol = Path(yol)
    yol.parent.mkdir(parents=True, exist_ok=True)
    yol.write_text(json.dumps(veri, ensure_ascii=False, indent=2), encoding="utf-8")


def yukle(yol) -> tuple[ht.KararKurali, dict[str, tuple[float, float]], dict]:
    """Dönüş: (kural, şiddet eşikleri, bilgi)."""
    v = json.loads(Path(yol).read_text(encoding="utf-8"))
    if v.get("dosya_surumu") != SURUM:
        raise ValueError(f"kural dosyası sürümü {v.get('dosya_surumu')} (beklenen {SURUM})")
    kural = ht.KararKurali(dict(v["esleme"]), v["yonlu"], dict(v["yonler"]), dict(v["medyan"]), dict(v["olcek"]),
                           T=float(v["T"]), bilgi=dict(v["bilgi"]), kaldirma_surumu=v["kaldirma_surumu"])
    esik = {h: (float(a), float(b)) for h, (a, b) in v["siddet_esikleri"].items()}
    return kural, esik, v["bilgi"]
