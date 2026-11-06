"""
Kural tabanlı Türkçe geri bildirim (Adım 5, Deney 3; uygulama da aynı kodu kullanır).

Deney 2'nin kararını (cekirdek/hata_turu.py; en fazla 2 hata, 2. hata ancak z'si de T'yi geçerse)
bir "sapma kodu"na ve oradan ölçü içeren bir cümleye çevirir. Tanımlar ADIM_05.md "Önceden
belirlenenler" bölümünde, kod ve sonuçlardan önce sabitlendi:
  faz      : tekrarın kendi (yumuşatılmış) kol eğrisinden; ≥ 0,85·tepe = "kol en üstteyken",
             öncesi "kaldırırken", sonrası "indirirken". Söylenen faz: beklenen yöndeki bant dışı
             fazlalığın toplamının en büyük olduğu faz (eşitlikte kaldırırken → üstte → indirirken).
  an       : seçilen faz içinde fazlalığın en büyük olduğu kare; ölçü = o karedeki ham değer,
             beklenen = o karedeki μ. Hatalıda μ ve bant_disi n modelin ortalaması (Karar 7).
  şiddet   : eğitim kişilerinin o hatayla etiketli (önden + çapraz) tekrarlarındaki kural puanının
             üçte birlik dilimleri (az kaldırma dahil; puan max(d, 0)).
  birimler : açı → derece; YENI ve kol_boyu → gövde boyunun %'si; omuz için ayrıca omuz çizgisi
             eğimi (omuz_egim, yalnızca anlatım). En yakın 1'e yuvarlanır; fark yuvarlanmış
             değerlerin farkıdır. Santimetre yok.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from cekirdek import hata_turu as ht
from cekirdek.aci_bandi import yumusak_kol

TEPE_ORANI = 0.85
KALDIRIRKEN, USTTE, INDIRIRKEN = 0, 1, 2
FAZ_ADLARI = {KALDIRIRKEN: "kaldırırken", USTTE: "en üstteyken", INDIRIRKEN: "indirirken"}
FAZ_METNI = {KALDIRIRKEN: "Kolunu kaldırırken", USTTE: "Kolun en üstteyken", INDIRIRKEN: "Kolunu indirirken"}
SIDDETLER = ("hafif", "belirgin", "çok belirgin")
SIDDET_METNI = {"hafif": "biraz", "belirgin": "belirgin şekilde", "çok belirgin": "çok"}
YUZDE_OLCUTLERI = {"YENI", "kol_boyu"}   # gövde boyuna bölünmüş uzunluklar → %
OMUZ_ANLATIM = "omuz_egim"
TARAF = "sağ"                            # Ex1'de sağ kol


# ---------------------------------------------------------------- Türkçe sayı ekleri
_BIRLER = ["", "bir", "iki", "üç", "dört", "beş", "altı", "yedi", "sekiz", "dokuz"]
_ONLAR = ["", "on", "yirmi", "otuz", "kırk", "elli", "altmış", "yetmiş", "seksen", "doksan"]
_UNLULER = "aıoueiöü"


def _son_kelime(n: int) -> str:
    """Sayının okunuşundaki son kelime (ek uyumu buna göre)."""
    n = abs(int(n))
    if n == 0:
        return "sıfır"
    if n % 10:
        return _BIRLER[n % 10]
    if (n // 10) % 10:
        return _ONLAR[(n // 10) % 10]
    if (n // 100) % 10:
        return "yüz"
    return "bin"


def sayi_eki(n: int, tur: str) -> str:
    """Rakamla yazılmış sayının eki (kesme işaretinden sonrası). tur: 'iyelik' (%30'u) ya da 'yonelme' (%30'a)."""
    k = _son_kelime(n)
    unlu = [c for c in k if c in _UNLULER][-1]
    unluyle_biter = k[-1] in _UNLULER
    if tur == "iyelik":
        return ("s" if unluyle_biter else "") + {"a": "ı", "ı": "ı", "o": "u", "u": "u",
                                                 "e": "i", "i": "i", "ö": "ü", "ü": "ü"}[unlu]
    if tur == "yonelme":
        return ("y" if unluyle_biter else "") + ("a" if unlu in "aıou" else "e")
    raise ValueError(tur)


def yuzde(n: int, tur: str | None = None) -> str:
    return f"%{n}" + (f"'{sayi_eki(n, tur)}" if tur else "")


def yuvarla(x: float) -> int:
    """En yakın tam sayı (yarımlar yukarı)."""
    return int(np.floor(float(x) + 0.5))


# ---------------------------------------------------------------- faz ve an
def anlatim_fazlari(kol: np.ndarray) -> np.ndarray:
    """Kare başına anlatım fazı: 0 kaldırırken, 1 kol en üstteyken (≥ 0,85·tepe), 2 indirirken."""
    y = yumusak_kol(kol)
    ust = np.flatnonzero(y >= TEPE_ORANI * y.max())
    faz = np.zeros(len(y), dtype=np.int64)
    faz[ust[0]:ust[-1] + 1] = USTTE
    faz[ust[-1] + 1:] = INDIRIRKEN
    return faz


def _nanort(diziler: list[np.ndarray]) -> np.ndarray:
    a = np.vstack(diziler).astype(float)
    say = (~np.isnan(a)).sum(0)
    top = np.nansum(a, axis=0)
    return np.where(say > 0, top / np.maximum(say, 1), np.nan)


def model_ortalamasi(ayrintilar: list[dict], olcut: str) -> tuple[np.ndarray, np.ndarray]:
    """
    Karar 7: n modelin aci_bandi_hatasi(..., ayrinti=True) ek çıktılarından kare başına μ ve imzalı
    bant_disi ortalaması (geçersiz karelerde NaN; hiçbir modelin geçerli olmadığı kare NaN).
    """
    mu = _nanort([np.where(a["gecerli"], a["mu"][olcut], np.nan) for a in ayrintilar])
    bd = _nanort([a["bant_disi"][olcut] for a in ayrintilar])
    return mu, bd


def an_sec(kol: np.ndarray, deger: np.ndarray, mu: np.ndarray, bant_disi: np.ndarray, yon: int):
    """(faz, kare) — ADIM_05 madde 1–2. Ölçülecek kare yoksa (None, None)."""
    faz = anlatim_fazlari(kol)
    bd = np.asarray(bant_disi, float)
    fazla = np.abs(bd) if yon == 0 else np.maximum(np.sign(yon) * bd, 0.0)
    fazla = np.where(np.isnan(fazla), 0.0, fazla)
    if (fazla > 0).any():
        p = int(np.argmax([fazla[faz == f].sum() for f in (KALDIRIRKEN, USTTE, INDIRIRKEN)]))
        idx = np.flatnonzero(faz == p)
        return p, int(idx[np.argmax(fazla[idx])])
    d = np.asarray(deger, float) - np.asarray(mu, float)
    d = np.abs(d) if yon == 0 else np.sign(yon) * d
    d = np.where(np.isnan(d), -np.inf, d)
    if not np.isfinite(d).any():
        return None, None
    j = int(np.argmax(d))
    return int(faz[j]), j


# ---------------------------------------------------------------- sapma kodu
@dataclass
class SapmaKodu:
    """Bir hatanın kodu: hata türü, taraf, faz, yön, şiddet, ölçü ve beklenen (birimiyle)."""
    hata: str
    olcut: str
    yon: int
    siddet: str
    olcu: float | None          # ham birimde (YENI/kol_boyu oran, diğerleri derece)
    beklenen: float | None
    faz: int | None = None
    kare: int | None = None
    ek_olcu: float | None = None      # omuz: omuz çizgisi eğimi (°)
    ek_beklenen: float | None = None
    taraf: str = TARAF

    @property
    def birim(self) -> str:
        return "%" if self.olcut in YUZDE_OLCUTLERI else "°"

    def _g(self, x):
        return None if x is None or not np.isfinite(x) else yuvarla(100 * x if self.birim == "%" else x)

    @property
    def olcu_g(self):
        """Gösterilen ölçü (yuvarlanmış, kullanıcı biriminde)."""
        return self._g(self.olcu)

    @property
    def beklenen_g(self):
        return self._g(self.beklenen)

    @property
    def fark(self):
        """Gösterilen fark: olcu − beklenen (yuvarlanmış değerlerden); az kaldırmada beklenen − olcu."""
        if self.olcu_g is None or self.beklenen_g is None:
            return None
        return self.beklenen_g - self.olcu_g if self.hata == "ERR_LOW_ABDUCTION" else self.olcu_g - self.beklenen_g

    @property
    def ek_fark(self):
        if self.ek_olcu is None or self.ek_beklenen is None or not (np.isfinite(self.ek_olcu) and np.isfinite(self.ek_beklenen)):
            return None
        return yuvarla(self.ek_olcu) - yuvarla(self.ek_beklenen)

    def sozluk(self) -> dict:
        return {"hata": self.hata, "taraf": self.taraf, "faz": FAZ_ADLARI.get(self.faz, ""), "yon": self.yon,
                "siddet": self.siddet, "olcut": self.olcut, "olcu": self.olcu_g, "beklenen": self.beklenen_g,
                "fark": self.fark, "birim": self.birim, "kare": self.kare, "omuz_egim_fark": self.ek_fark}


def durus_kodu(hata: str, olcut: str, yon: int, siddet: str, kol, deger, mu, bant_disi,
               ek_deger=None, ek_mu=None) -> SapmaKodu:
    """Duruş hatası (omuz, baş, öne kaçma, dirsek) için sapma kodu."""
    faz, j = an_sec(kol, deger, mu, bant_disi, yon)
    if j is None:
        return SapmaKodu(hata, olcut, yon, siddet, None, None)
    eo = eb = None
    if ek_deger is not None and ek_mu is not None:
        eo, eb = float(ek_deger[j]), float(ek_mu[j])
    return SapmaKodu(hata, olcut, yon, siddet, float(deger[j]), float(mu[j]), faz, j, eo, eb)


def kaldirma_kodu(yon: int, siddet: str, tepe: float, beklenen_tepe: float) -> SapmaKodu:
    """Az kaldırma: ölçü = tekrarın tepe açısı, beklenen = kalibrasyon tepelerinin medyanı; faz 'en üstte'."""
    return SapmaKodu("ERR_LOW_ABDUCTION", ht.KALDIRMA, yon, siddet, float(tepe), float(beklenen_tepe), USTTE)


# ---------------------------------------------------------------- şiddet
def siddet_esikleri(egitim: pd.DataFrame, kural: ht.KararKurali) -> dict[str, tuple[float, float]]:
    """Hata türü → (q₁, q₂): eğitimde o hatayla etiketli tekrarların kural puanının %33,3 / %66,7 dilimleri."""
    cikti = {}
    for hata, k in kural.esleme.items():
        g = egitim[egitim.hata == hata]
        p = ht.olcut_puani(g, k, kural.yon(k), kural.kaldirma_surumu).dropna().to_numpy(float)
        q1, q2 = np.percentile(p, [100 / 3, 200 / 3]) if len(p) else (np.nan, np.nan)
        cikti[hata] = (float(q1), float(q2))
    return cikti


def siddet_sinifi(puan: float, esik: tuple[float, float]) -> str:
    q1, q2 = esik
    if puan < q1:
        return "hafif"
    return "belirgin" if puan < q2 else "çok belirgin"


# ---------------------------------------------------------------- cümleler
def _ilk_kucuk(s: str) -> str:
    return s[:1].lower() + s[1:]


def hata_cumlesi(k: SapmaKodu, kisa: bool = False) -> str:
    """Bir sapma kodunun cümlesi: faz + şiddet + ölçü (normalde X, sende Y) + düzeltme."""
    S = SIDDET_METNI[k.siddet]
    F = FAZ_METNI.get(k.faz, "Hareket sırasında")
    b, o, f = k.beklenen_g, k.olcu_g, k.fark
    olculu = b is not None and o is not None
    h, yukari = k.hata, k.yon >= 0

    if h == "ERR_ELEVATED_SHOULDER":
        if not yukari:   # kulak–omuz mesafesi azaldı: omuz kulağa yaklaştı (silkme)
            c = f"{F} {k.taraf} omzunu kulağına doğru {S} kaldırıyorsun"
            if olculu:
                c += (f": kulak ile omzunun arası normalde gövde boyunun {yuzde(b, 'iyelik')} iken "
                      f"{yuzde(o, 'yonelme')} indi")
            c += "."
            if not kisa and k.ek_fark is not None and abs(k.ek_fark) >= 1:
                c += (f" Omuz çizgin normaline göre yaklaşık {abs(k.ek_fark)} derece "
                      f"{'yukarı' if k.ek_fark > 0 else 'aşağı'} eğildi.")
            return c + " Omzunu aşağıda ve gevşek tut."
        c = f"{F} {k.taraf} omzun normalden {S} aşağıda"
        if olculu:
            c += (f": kulak ile omzunun arası normalde gövde boyunun {yuzde(b, 'iyelik')} iken "
                  f"{yuzde(o, 'yonelme')} çıktı")
        return c + ". Omzunu doğal yüksekliğinde ve gevşek tut."

    if h == "ERR_HEAD_TO_SIDE":
        c = f"{F} başını {S} yana eğiyorsun" if yukari else f"{F} başının duruşu normalden {S} farklı"
        if olculu:
            c += (f": başın ile gövden arasındaki açı normalde {b} derece iken {o} dereceye "
                  f"{'çıktı' if yukari else 'indi'}")
        return c + ". Başını dik tut, karşıya bak."

    if h == "ERR_ARM_FORWARD":
        if k.olcut == "kol_boyu":
            c = f"{F} kolun {S} öne kaçıyor" if not yukari else f"{F} kolun normalden {S} uzun görünüyor"
            if olculu:
                c += (f": kolun kamerada normalde gövde boyunun {yuzde(b, 'iyelik')} kadar görünürken "
                      f"{yuzde(o, 'yonelme')} {'kısaldı' if not yukari else 'uzadı'}")
        else:
            c = f"{F} kolun {S} öne kaçıyor"
            if olculu:
                c += (f": kolun ile gövden arasındaki açı normalde {b} derece iken {o} dereceye "
                      f"{'çıktı' if yukari else 'indi'}")
        return c + ". Kolunu vücudunla aynı hizada, tam yana kaldır."

    if h == "ERR_BENT_ARM":
        if not yukari:
            c = f"{F} dirseğini {S} büküyorsun"
            if olculu:
                c += f": dirsek açın normalde {b} derece iken {o} dereceye indi"
            return c + ". Kolunu dirsekten bükmeden düz tut."
        c = f"{F} dirseğin normalden {S} fazla açılıyor"
        if olculu:
            c += f": dirsek açın normalde {b} derece iken {o} dereceye çıktı"
        return c + ". Kolunu doğal ve düz tut."

    if h == "ERR_LOW_ABDUCTION":
        if yukari:   # eksik kaldırma
            c = f"Kolunu {S} az kaldırdın"
            if olculu:
                c += (f": en fazla {o} dereceye çıktı, normalde {b} dereceye kadar çıkıyordun. "
                      f"Kolunu yaklaşık {max(f, 1)} derece daha yukarı kaldır.")
            else:
                c += ". Kolunu daha yukarı kaldır."
            return c
        c = f"Kolunu normalden {S} fazla kaldırdın"
        if olculu:
            c += (f": {o} dereceye çıktı, normalde {b} dereceye kadar çıkıyordun. "
                  f"Kolunu yaklaşık {b} dereceye kadar kaldırman yeterli.")
        else:
            c += ". Kolunu normal yüksekliğine kadar kaldırman yeterli."
        return c
    raise ValueError(h)


OLUMLU = [
    "Hareketi doğru yaptın. Kolun {t} dereceye kadar çıktı; omzun ve dirseğin normal aralıkta kaldı.",
    "Güzel bir tekrar. Kolunu {t} dereceye kadar kaldırdın; omzun, başın ve dirseğin normal aralıktaydı.",
    "Doğru tekrar. Kolun {t} dereceye ulaştı; omzun, başın ve dirseğin normal aralıktaydı. Böyle devam et.",
    "Bu tekrar doğru. Kolunu {t} dereceye kadar kaldırdın ve duruşun normal aralıkta kaldı. Aynı şekilde devam et.",
]


def olumlu_cumle(tepe: float, sira: int, tohum: int = 0) -> str:
    """Doğru tekrar için somut olumlu cümle; varyasyon = (sıra + tohum) mod 4 (ör. sıra = Segmentation satırı)."""
    return OLUMLU[(int(sira) + int(tohum)) % len(OLUMLU)].format(t=yuvarla(tepe))


def geri_bildirim(kodlar: list[SapmaKodu], tepe: float, sira: int, tohum: int = 0) -> str:
    """En fazla 2 hata: '1. cümle' + ' Ayrıca ' + '2. cümle (kısa)'. Hata yoksa olumlu cümle."""
    if not kodlar:
        return olumlu_cumle(tepe, sira, tohum)
    metin = hata_cumlesi(kodlar[0])
    if len(kodlar) > 1:
        metin += " Ayrıca " + _ilk_kucuk(hata_cumlesi(kodlar[1], kisa=True))
    return metin
