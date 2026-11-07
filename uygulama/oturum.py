"""
Arayüzden bağımsız oturum mantığı (Adım 6). Pencere (uygulama/main.py) ve yığın modu (uygulama/toplu.py)
bunu ortak kullanır. Karar ve cümle yalnızca cekirdek/ içinden gelir.

Akış:
  * Her kare: MediaPipe noktaları (33, 4) → kol açısı → TekrarAyirici (Karar 25).
  * Kalibrasyon: biten her tekrar "onay bekliyor" olur; kullanıcı kabul ya da ret eder. Varsayılan 6,
    en az 5 tekrar (Karar 8). Her kalibrasyon tekrarının dinlenme karelerinde kamera açısı oranı
    ölçülür (Karar 26); eşiğin altındaysa uyarı verilir, kalibrasyon engellenmez.
  * Değerlendirme: tam model (kalibrasyondaki bütün tekrarlar, Karar 24) + modeller/kural_ex1.json
    → cekirdek.degerlendirici.degerlendir → karar, hasta cümlesi, uzman ayrıntısı.
  * Yumuşatma yok (Karar 10): ölçütler ham noktalardan.
"""
from __future__ import annotations

import csv
import datetime as dt
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from cekirdek import degerlendirici as dg
from cekirdek import geribildirim as gb
from cekirdek import kamera_acisi as ka
from cekirdek import kural_dosyasi
from cekirdek import tekrar_ayirici as ta
from cekirdek.aci_bandi import tepe_acisi
from cekirdek.ozellikler import OLCUTLER, Iskelet
from cekirdek.veri import KOK, PAY

KURAL_YOLU = KOK / "modeller" / "kural_ex1.json"
PROFIL_KLASORU = KOK / "profiller"
OTURUM_KLASORU = KOK / "oturumlar"
HEDEF_KALIBRASYON = 6
EN_AZ_KALIBRASYON = 5
GORUNURLUK_ESIGI = 0.5     # arayüz kalite kontrolü: omuz ve kalçaların MediaPipe görünürlüğü (tekrar medyanı)
EGZERSIZLER = {"ex1": "Kolu yana kaldırma (sağ kol)"}   # Karar 27: ilk sürüm yalnızca Ex1


def kalite_sorunu(dizi: np.ndarray) -> str:
    """Tekrar boyunca omuz ve kalçalar kadrajda mıydı? Kol açısı omuz–kalça çizgisine göre ölçülür ve
    ölçütler gövde boyuyla ölçeklenir; kalça görünmezse MediaPipe onu tahmin eder, ölçüler bozulur."""
    v = np.asarray(dizi)[:, [11, 12, 23, 24], 3]
    if not np.isfinite(v).any():
        return "kişi görünmüyordu"
    with np.errstate(all="ignore"):
        m = np.nanmedian(v, axis=0)
    if np.nanmin(m[2:]) < GORUNURLUK_ESIGI:
        return "kalçaların kadrajda değildi"
    if np.nanmin(m[:2]) < GORUNURLUK_ESIGI:
        return "omuzların kadrajda değildi"
    return ""


def kol_acisi(lm: np.ndarray, en_boy: float) -> float:
    return float(OLCUTLER["kol"](Iskelet(np.asarray(lm)[None], en_boy))[0])


@dataclass(eq=False)
class TekrarKaydi:
    no: int
    bas: int                 # oturumdaki ilk kare (dahil)
    son: int                 # son kare (dahil)
    pay: int                 # dizinin başındaki dinlenme karesi sayısı
    dizi: np.ndarray = field(repr=False)     # (pay + tekrar, 33, 4)
    tepe: float = np.nan
    durum: str = ""          # onay_bekliyor | kalibrasyon | reddedildi | degerlendirildi
    kamera_orani: float = np.nan
    sonuc: dg.Sonuc | None = field(default=None, repr=False)
    kalite_sorunu: str = ""  # boş değilse: omuz/kalça kadrajda değildi (yalnızca arayüz uyarısı)

    @property
    def etiketli(self) -> slice:
        return slice(self.pay, None)


class Oturum:
    def __init__(self, en_boy: float, fps: float = ta.FPS, kural_yolu=KURAL_YOLU, kamera_esigi_yolu=ka.ESIK_DOSYASI,
                 hedef: int = HEDEF_KALIBRASYON, en_az: int = EN_AZ_KALIBRASYON,
                 olcu_surumu: str = gb.VARSAYILAN_OLCU, tohum: int = 0):
        self.en_boy, self.fps = float(en_boy), float(fps)
        self.kural, self.siddet, self.kural_bilgi = kural_dosyasi.yukle(kural_yolu)
        self.kamera_esigi = ka.esik_oku(kamera_esigi_yolu) if Path(kamera_esigi_yolu).exists() else None
        self.hedef, self.en_az = hedef, en_az
        self.olcu_surumu, self.tohum = olcu_surumu, tohum
        self.kareler: list[np.ndarray] = []
        self.ayirici = ta.TekrarAyirici(self.fps)
        self.tekrarlar: list[TekrarKaydi] = []
        self.kalibrasyon: list[TekrarKaydi] = []
        self.profil: dg.Profil | None = None
        self.uyari: str = ""
        self.ilk_kamera_orani: float = np.nan
        self.kol_anlik: float = np.nan       # son karenin kol açısı (yalnızca arayüz)
        self.kisi_var: bool = False          # son karede kişi bulundu mu (yalnızca arayüz)
        self.kalca_gorunur: bool = False     # son karede iki kalça da görünür mü (yalnızca arayüz)
        self.kalite_kontrol: bool = True     # kalibrasyonda omuz/kalçası görünmeyen tekrarı kendiliğinden reddet

    # ------------------------------------------------ durum
    @property
    def mod(self) -> str:
        return "degerlendirme" if self.profil is not None else "kalibrasyon"

    @property
    def bekleyen(self) -> TekrarKaydi | None:
        return next((t for t in self.tekrarlar if t.durum == "onay_bekliyor"), None)

    def degerlendirilenler(self) -> list[TekrarKaydi]:
        return [t for t in self.tekrarlar if t.durum == "degerlendirildi"]

    # ------------------------------------------------ kareler
    def kare_ekle(self, lm: np.ndarray) -> list[TekrarKaydi]:
        lm = np.asarray(lm, float)
        self.kareler.append(lm)
        if np.isnan(self.ilk_kamera_orani) and self.mod == "kalibrasyon":
            gecerli = [k for k in self.kareler if np.isfinite(k[[11, 12, 23, 24], :2]).all()]
            if len(gecerli) >= 8:
                self.ilk_kamera_orani = ka.omuz_govde_orani(np.stack(gecerli[:8]), self.en_boy)
                self._kamera_kontrol(self.ilk_kamera_orani)
        aci = kol_acisi(lm, self.en_boy)
        self.kol_anlik = aci
        self.kisi_var = bool(np.isfinite(lm[[11, 12, 23, 24], :2]).all())
        self.kalca_gorunur = bool(self.kisi_var and np.nanmin(lm[[23, 24], 3]) >= GORUNURLUK_ESIGI)
        return [self._tekrar(t) for t in self.ayirici.ekle(aci)]

    def bitir(self) -> list[TekrarKaydi]:
        return [self._tekrar(t) for t in self.ayirici.bitir()]

    def _kamera_kontrol(self, oran: float) -> None:
        if self.kamera_esigi is not None and ka.uyari_gerekli(oran, self.kamera_esigi):
            self.uyari = ka.UYARI

    def _tekrar(self, t: ta.AyrilanTekrar) -> TekrarKaydi:
        pay = min(PAY, t.bas)
        dizi = np.stack(self.kareler[t.bas - pay:t.son + 1])
        k = TekrarKaydi(len(self.tekrarlar) + 1, t.bas, t.son, pay, dizi, t.tepe)
        k.kamera_orani = ka.omuz_govde_orani(dizi, self.en_boy)
        self.tekrarlar.append(k)
        k.kalite_sorunu = kalite_sorunu(dizi[pay:])
        if self.mod == "kalibrasyon":
            if self.kalite_kontrol and k.kalite_sorunu:
                k.durum = "reddedildi"              # bozuk tekrar kalibrasyona hiç girmez
            else:
                k.durum = "onay_bekliyor"
                self._kamera_kontrol(k.kamera_orani)
        else:
            self._degerlendir(k)
        return k

    # ------------------------------------------------ kalibrasyon
    def onayla(self, k: TekrarKaydi, kabul: bool) -> None:
        if k.durum != "onay_bekliyor":
            return
        k.durum = "kalibrasyon" if kabul else "reddedildi"
        if kabul:
            self.kalibrasyon.append(k)
            if len(self.kalibrasyon) >= self.hedef:
                self.kalibrasyonu_bitir()

    @property
    def geri_alinabilir(self) -> bool:
        """Son kabul edilen kalibrasyon tekrarı geri alınabilir mi (değerlendirme henüz başlamadıysa)."""
        return (bool(self.kalibrasyon) and not self.degerlendirilenler()
                and all(k.no > 0 for k in self.kalibrasyon))        # dosyadan yüklenen profil geri alınmaz

    def son_kabulu_geri_al(self) -> TekrarKaydi | None:
        if not self.geri_alinabilir:
            return None
        k = self.kalibrasyon.pop()
        k.durum = "reddedildi"
        if self.profil is not None:                  # kalibrasyon bitmişti: yeniden kalibrasyon moduna dön
            self.profil = None
            for t in self.tekrarlar:
                if t.durum == "kullanilmadi":
                    t.durum = "reddedildi"
        return k

    def kalibrasyonu_sifirla(self) -> None:
        """Kabul edilmiş ve bekleyen kalibrasyon tekrarlarını iptal et (baştan başla)."""
        if self.mod != "kalibrasyon":
            return
        for k in self.tekrarlar:
            if k.durum in ("kalibrasyon", "onay_bekliyor"):
                k.durum = "reddedildi"
        self.kalibrasyon = []

    def kalibrasyonu_bitir(self, en_boy: float | None = None) -> bool:
        """en_boy: kalibrasyon görüntüsünün oranı (profil dosyasından yüklerken o dosyanınki)."""
        if len(self.kalibrasyon) < self.en_az:
            return False
        e = self.en_boy if en_boy is None else en_boy
        f = [dg.tekrar_ozellikleri(k.dizi, k.etiketli, e)[0] for k in self.kalibrasyon]
        self.profil = dg.Profil(f)
        for k in self.tekrarlar:                 # kalibrasyon bitti: hâlâ onay bekleyen tekrar kullanılmaz
            if k.durum == "onay_bekliyor":
                k.durum = "kullanilmadi"
        return True

    def referans(self) -> TekrarKaydi | None:
        """Bindirme için referans: tepe açısı kalibrasyon medyanına en yakın kalibrasyon tekrarı."""
        if not self.kalibrasyon:
            return None
        m = np.median([k.tepe for k in self.kalibrasyon])
        return min(self.kalibrasyon, key=lambda k: abs(k.tepe - m))

    # ------------------------------------------------ değerlendirme
    def _degerlendir(self, k: TekrarKaydi) -> None:
        f, gor = dg.tekrar_ozellikleri(k.dizi, k.etiketli, self.en_boy)
        k.sonuc = dg.degerlendir(self.profil, self.kural, self.siddet, f, gor, sira=k.no, tohum=self.tohum,
                                 olcu_surumu=self.olcu_surumu)
        k.tepe = tepe_acisi(f["kol"])
        k.durum = "degerlendirildi"

    # ------------------------------------------------ kayıt
    def profil_kaydet(self, isim: str, klasor: Path = PROFIL_KLASORU) -> Path:
        yol = Path(klasor) / f"{isim}.npz"
        yol.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(yol, en_boy=self.en_boy, paylar=np.array([k.pay for k in self.kalibrasyon]),
                            **{f"tekrar{i}": k.dizi for i, k in enumerate(self.kalibrasyon)})
        return yol

    def profil_yukle(self, yol) -> None:
        v = np.load(yol)
        n = len(v["paylar"])
        self.kalibrasyon = []
        for i in range(n):
            d, p = v[f"tekrar{i}"], int(v["paylar"][i])
            k = TekrarKaydi(-(i + 1), -1, -1, p, d, durum="kalibrasyon")
            k.tepe = tepe_acisi(dg.tekrar_ozellikleri(d, k.etiketli, float(v["en_boy"]))[0]["kol"])
            self.kalibrasyon.append(k)
        if abs(float(v["en_boy"]) - self.en_boy) > 1e-3:
            self.uyari = (f"Profilin en-boy oranı ({float(v['en_boy']):.3f}) bu görüntüden ({self.en_boy:.3f}) farklı; "
                          "aynı kamera yerleşimiyle kalibrasyon önerilir.")
        self.en_az = min(self.en_az, n)
        if not self.kalibrasyonu_bitir(float(v["en_boy"])):
            raise ValueError("profilde yeterli tekrar yok")

    def oturum_satirlari(self) -> list[dict]:
        satir = []
        for k in self.tekrarlar:
            r = {"tekrar": k.no, "bas_kare": k.bas, "son_kare": k.son, "sure_s": round((k.son - k.bas + 1) / self.fps, 2),
                 "durum": k.durum, "kamera_orani": round(k.kamera_orani, 4) if np.isfinite(k.kamera_orani) else "",
                 "tepe_aci": round(float(k.tepe), 1) if np.isfinite(k.tepe) else "", "kalite": k.kalite_sorunu}
            if k.sonuc is not None:
                r.update(k.sonuc.satir())
            satir.append(r)
        return satir

    def oturum_kaydet(self, yol: Path | None = None) -> Path:
        yol = Path(yol) if yol else OTURUM_KLASORU / f"{dt.datetime.now():%Y-%m-%d_%H%M%S}.csv"
        yol.parent.mkdir(parents=True, exist_ok=True)
        satir = self.oturum_satirlari()
        alanlar = list(dict.fromkeys(a for r in satir for a in r)) or ["tekrar"]
        with open(yol, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=alanlar)
            w.writeheader()
            w.writerows(satir)
        return yol
