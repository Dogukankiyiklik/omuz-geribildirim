"""
Tek bir tekrarın değerlendirilmesi: puan → karar → sapma kodu → iki katmanlı cümle.

Deney 2 (puanlar), Deney 3 (sapma kodu) ve uygulama bu modülü ortak kullanır. Böylece uygulamanın
verdiği karar, deneyde ölçülen kararla aynı koddan gelir.

  * tekrar_puanlari : bir açı bandı modeliyle puanlar (Deney 2 regresyon testi denetler).
  * puan_satiri     : puanları kural.z'nin okuduğu sütunlara çevirir (deney2.puan_tablosu ile aynı adlar).
  * kod_uret        : bir hata için SapmaKodu.
  * Profil, degerlendir : uygulama. Kalibrasyondaki bütün doğru tekrarlardan kurulan TAM model;
                      değerlendirilen tekrar kalibrasyona girmez.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from cekirdek import geribildirim as gb
from cekirdek import hata_turu as ht
from cekirdek.aci_bandi import aci_bandi_hatasi, aci_bandi_modeli, aci_bandi_puanlari, tepe_acisi
from cekirdek.ozellikler import DENEY2_OLCUTLERI, ozellikler

OLCUTLER = list(DENEY2_OLCUTLERI)
ANLATIM = [gb.OMUZ_ANLATIM]
YONLER = (0, 1, -1)


# ---------------------------------------------------------------- puanlar (Deney 2 ile ortak)
def kaldirma_ekle(E: dict, fark: dict, f: dict, kalibrasyon_f: list[dict], yonler=YONLER) -> None:
    """Az kaldırma: revize puan (yalnızca karşılaştırma) ve ilk sürüm d (kullanılan yöntem)."""
    tepeler = [tepe_acisi(u["kol"]) for u in kalibrasyon_f]
    Ek, fark[ht.KALDIRMA] = ht.kaldirma_puanlari(tepe_acisi(f["kol"]), tepeler)
    E.update({(ht.KALDIRMA, y): Ek[y] for y in yonler})
    fark[ht.KALDIRMA_ILK] = ht.kaldirma_sapmasi(tepe_acisi(f["kol"]), tepeler)


def tekrar_puanlari(model, kalibrasyon_f: list[dict], f: dict, olcutler=OLCUTLER, kaldirma: bool = True):
    """Açı bandı modeliyle puanlar: (E[(ölçüt, yön)], fark[ölçüt], ek)."""
    E, fark, ek = aci_bandi_puanlari(model, f, olcutler, YONLER)
    ek = {"kapsam": ek["kapsam"], "aralik_disi": float(ek["aralik_disi"])}
    if kaldirma:
        kaldirma_ekle(E, fark, f, kalibrasyon_f)
    return E, fark, ek


def puan_satiri(E: dict, fark: dict, olcutler=OLCUTLER, kaldirma: bool = True) -> dict:
    r = {ht.puan_sutunu(k, y): E[(k, y)] for k in list(olcutler) + ([ht.KALDIRMA] if kaldirma else [])
         for y in YONLER}
    r.update({ht.fark_sutunu(k): v for k, v in fark.items()})
    return r


# ---------------------------------------------------------------- sapma kodu (Deney 3 ile ortak)
def kod_uret(hata: str, siddet: str, kural: ht.KararKurali, a: dict, olcu_surumu: str = "tek_kare") -> gb.SapmaKodu:
    """a: kol, deger, mu, bd, gor (ölçüt → kare dizisi), ek_deger, ek_mu (omuz eğimi), tepe, beklenen_tepe."""
    k = kural.esleme[hata]
    yon = kural.yon(k)
    if k == ht.KALDIRMA:
        return gb.kaldirma_kodu(yon, siddet, a["tepe"], a["beklenen_tepe"])
    ek = (a["ek_deger"], a["ek_mu"]) if hata == ht.SILKME else (None, None)
    return gb.durus_kodu(hata, k, yon, siddet, a["kol"], a["deger"][k], a["mu"][k], a["bd"][k], *ek,
                         olcu_surumu=olcu_surumu, gorunurluk=a["gor"][k])


# ---------------------------------------------------------------- uygulama
def tekrar_ozellikleri(dizi: np.ndarray, etiketli: slice, en_boy: float) -> tuple[dict, dict]:
    """
    Bir tekrarın ölçütleri (dinlenme tabanı için pay dahil dizide hesaplanır, sonra etiketli kısım alınır;
    deneylerle aynı) ve kare başına görünürlükler.
    """
    f = ozellikler(dizi, OLCUTLER + ANLATIM, en_boy)
    f = {k: v[etiketli] for k, v in f.items()}
    gor = {k: gb.olcut_gorunurlugu(np.asarray(dizi)[etiketli], k) for k in OLCUTLER}
    return f, gor


@dataclass
class Profil:
    """Kişinin kalibrasyonu: onaylanan doğru tekrarların ölçütleri ve onlardan kurulan tam model."""
    kalibrasyon_f: list[dict]
    model: object = field(init=False)
    model_ek: object = field(init=False)
    tepeler: list[float] = field(init=False)

    def __post_init__(self):
        if len(self.kalibrasyon_f) < 3:
            raise ValueError("kalibrasyon için en az 3 tekrar gerekir (uygulama en az 5 ister)")
        self.model = aci_bandi_modeli(self.kalibrasyon_f, OLCUTLER)
        self.model_ek = aci_bandi_modeli(self.kalibrasyon_f, ANLATIM)
        self.tepeler = [tepe_acisi(u["kol"]) for u in self.kalibrasyon_f]


@dataclass
class Sonuc:
    karar: str                      # DOGRU ya da hata kodu
    soylenen: list[str]             # en fazla 2 hata
    z: dict
    kodlar: list
    hasta_cumlesi: str
    uzman_ayrintisi: str
    tepe: float
    ayrinti: dict                   # çizim için: kol, deger, mu, tau, bant_disi, kare_hatasi, faz, gecerli

    def satir(self) -> dict:
        d = {"karar": self.karar, "soylenen1": self.soylenen[0] if self.soylenen else ht.DOGRU,
             "soylenen2": self.soylenen[1] if len(self.soylenen) > 1 else "", "tepe_acisi": gb.yuvarla(self.tepe),
             "hasta_cumlesi": self.hasta_cumlesi, "uzman_ayrintisi": self.uzman_ayrintisi}
        d.update({f"z_{ht.KISA_AD.get(h, h)}": v for h, v in self.z.items()})
        for i, k in enumerate(self.kodlar[:2], 1):
            d.update({f"{i}_{a}": v for a, v in k.sozluk().items()})
        return d


def degerlendir(profil: Profil, kural: ht.KararKurali, siddet_esikleri: dict, f: dict, gor: dict,
                sira: int = 0, tohum: int = 0, olcu_surumu: str = gb.VARSAYILAN_OLCU) -> Sonuc:
    """Bir tekrarı değerlendirir: Deney 2 kararı (aynı puan, z, T, ilk iki) + Deney 3 sapma kodu ve cümleler."""
    E, fark, _ = tekrar_puanlari(profil.model, profil.kalibrasyon_f, f)
    df = pd.DataFrame([puan_satiri(E, fark)])
    z = kural.z(df)
    ii = ht.ilk_iki(z, kural.T).iloc[0]
    karar = kural.karar(df, z).iloc[0]
    soylenen = [h for h in (ii.soylenen1, ii.soylenen2) if h and h != ht.DOGRU]
    _, ayr = aci_bandi_hatasi(profil.model, f, OLCUTLER, ayrinti=True)
    _, ayr_ek = aci_bandi_hatasi(profil.model_ek, f, ANLATIM, ayrinti=True)
    mu, bd = {}, {}
    for k in OLCUTLER:
        mu[k], bd[k] = gb.model_ortalamasi([ayr], k)
    ek_mu, _ = gb.model_ortalamasi([ayr_ek], gb.OMUZ_ANLATIM)
    tepe = tepe_acisi(f["kol"])
    a = {"kol": f["kol"], "deger": {k: f[k] for k in OLCUTLER}, "mu": mu, "bd": bd, "gor": gor,
         "ek_deger": f[gb.OMUZ_ANLATIM], "ek_mu": ek_mu, "tepe": tepe,
         "beklenen_tepe": float(np.median(profil.tepeler))}
    kodlar = []
    for h in soylenen:
        k = kural.esleme[h]
        puan = float(ht.olcut_puani(df, k, kural.yon(k), kural.kaldirma_surumu).iloc[0])
        kodlar.append(kod_uret(h, gb.siddet_sinifi(puan, siddet_esikleri[h]), kural, a, olcu_surumu))
    metin = gb.iki_katman(kodlar, tepe, sira, tohum)
    return Sonuc(karar, soylenen, {h: float(z.iloc[0][h]) for h in z.columns}, kodlar,
                 metin["hasta_cumlesi"], metin["uzman_ayrintisi"], tepe, ayr)
