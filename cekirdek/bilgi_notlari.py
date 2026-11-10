"""
Bilgi notları. Hata türü DEĞİLDİR.

Bu notlar karar kuralına girmez, hiçbir metriğe (katı, ilk iki, gereksiz uyarı ...) katılmaz.
Uygulamada hasta cümlesinin altında ayrı bir not olarak gösterilir ve oturum CSV'sine ayrı sütunlarda yazılır.

  * Hız: tekrar süresi, veri setinin önden + çapraz DOĞRU tekrarlarındaki sürelerin 5. yüzdeliğinden
    kısaysa "Hareketi biraz daha yavaş yap." Süre = (son kare − ilk kare + 1) / FPS; veri setinde
    first_frame…last_frame, uygulamada tekrar ayırıcının sınırları. Eşik deneyler/hiz_esigi.py ile üretilir
    (modeller/hiz_esigi.json). Veri setinde hız etiketi olmadığı için doğruluğu ölçülemez.
  * Sol kol: tekrar sırasında sol kolun açısı (sağ kolla aynı tanım: üst kol ile aşağı yön arasındaki
    açı; tepe, aynı 5 karelik medyanla yumuşatılmış eğriden) 60°'yi geçerse "Yalnızca sağ kolunu kaldır."
    60° tekrar ayırıcının tepe şartıdır (ta.EN_AZ_TEPE); yeni bir sabit değildir.
  * Kamera: her değerlendirme tekrarının dinlenme oranına kamera açısı eşiği (cekirdek/kamera_acisi.py) uygulanır.
    Eşiğin altındaysa karar ve cümle yine gösterilir, altına not eklenir. Yeni eşik yoktur.

Genel bir "hareket tanınmadı" notu bilerek YOKTUR: tanımı yeni bir eşik gerektirir ve sınanamaz.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from cekirdek import kamera_acisi as ka
from cekirdek import tekrar_ayirici as ta
from cekirdek.aci_bandi import tepe_acisi
from cekirdek.geometri import aci
from cekirdek.ozellikler import Iskelet
from cekirdek.veri import EN_BOY, KOK

HIZ_ESIGI_DOSYASI = KOK / "modeller" / "hiz_esigi.json"
HIZ_YUZDELIGI = 5
SOL_KOL_ESIGI = ta.EN_AZ_TEPE          # 60°: ayırıcının tepe şartıyla aynı sayı

HIZ_NOTU = "Hareketi biraz daha yavaş yap."
SOL_KOL_NOTU = "Yalnızca sağ kolunu kaldır."
KAMERA_NOTU = "Kameraya göre açın değişti; bu sonuç güvenilir olmayabilir. Kameraya daha önden dur."
KALIBRASYON_YONERGESI = "Doğal ve rahat tekrarlar yap; kendini zorlama. Her tekrarda aynı yere bak."


# ---------------------------------------------------------------- hız
def tekrar_suresi(ilk_kare: int, son_kare: int, fps: float = ta.FPS) -> float:
    """Saniye cinsinden süre; ilk ve son kare dahil."""
    return (int(son_kare) - int(ilk_kare) + 1) / float(fps)


def hiz_esigi_oku(yol=HIZ_ESIGI_DOSYASI) -> float:
    return float(json.loads(Path(yol).read_text(encoding="utf-8"))["esik_s"])


def hiz_notu_gerekli(sure_s: float, esik_s: float | None) -> bool:
    return bool(esik_s is not None and np.isfinite(sure_s) and sure_s < esik_s)


# ---------------------------------------------------------------- sol kol
def sol_kol_acisi(dizi: np.ndarray, en_boy: float = EN_BOY) -> np.ndarray:
    """Kare başına sol kol açısı: sol üst kol (11 → 13) ile aşağı yön arasındaki açı (sağ kolun aynası)."""
    s = Iskelet(np.asarray(dizi), en_boy)
    return aci(s.p(13) - s.p(11), s.asagi)


def sol_kol_tepesi(dizi: np.ndarray, en_boy: float = EN_BOY) -> float:
    a = sol_kol_acisi(dizi, en_boy)
    if not np.isfinite(a).any():
        return np.nan
    return tepe_acisi(np.where(np.isfinite(a), a, np.nanmedian(a)))


def sol_kol_notu_gerekli(tepe: float) -> bool:
    return bool(np.isfinite(tepe) and tepe > SOL_KOL_ESIGI)


# ---------------------------------------------------------------- hepsi birden
@dataclass
class BilgiNotlari:
    sure_s: float
    hiz: bool
    sol_kol_tepe: float
    sol_kol: bool
    kamera_orani: float
    kamera: bool

    @property
    def metinler(self) -> list[str]:
        return ([HIZ_NOTU] if self.hiz else []) + ([SOL_KOL_NOTU] if self.sol_kol else [])

    def satir(self) -> dict:
        return {"hiz_notu": int(self.hiz), "sol_kol_tepe": round(self.sol_kol_tepe, 1) if np.isfinite(self.sol_kol_tepe) else "",
                "sol_kol_notu": int(self.sol_kol), "kamera_uyarisi": int(self.kamera),
                "bilgi_notu": " ".join(self.metinler)}


def notlar(dizi_etiketli: np.ndarray, sure_s: float, kamera_orani: float, en_boy: float,
           hiz_esigi_s: float | None, kamera_esigi: float | None) -> BilgiNotlari:
    """dizi_etiketli: tekrarın kendisi (dinlenme payı hariç)."""
    tepe = sol_kol_tepesi(dizi_etiketli, en_boy)
    kamera = kamera_esigi is not None and ka.uyari_gerekli(kamera_orani, kamera_esigi)
    return BilgiNotlari(float(sure_s), hiz_notu_gerekli(sure_s, hiz_esigi_s), tepe, sol_kol_notu_gerekli(tepe),
                        float(kamera_orani), bool(kamera))
