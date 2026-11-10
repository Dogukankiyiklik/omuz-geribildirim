"""
Kural tabanlı Türkçe geri bildirim (Deney 3; uygulama da aynı kodu kullanır).

Hata türü kararını (cekirdek/hata_turu.py; en fazla 2 hata, 2. hata ancak z'si de T'yi geçerse)
bir "sapma kodu"na ve oradan ölçü içeren bir cümleye çevirir. Tanımlar, kod ve sonuçlardan önce sabitlendi:
  faz      : tekrarın kendi (yumuşatılmış) kol eğrisinden; ≥ 0,85·tepe = "kol en üstteyken",
             öncesi "kaldırırken", sonrası "indirirken". Söylenen faz: beklenen yöndeki bant dışı
             fazlalığın toplamının en büyük olduğu faz (eşitlikte kaldırırken → üstte → indirirken).
  an       : seçilen faz içinde fazlalığın en büyük olduğu kare; ölçü = o karedeki ham değer,
             beklenen = o karedeki μ. Hatalıda μ ve bant_disi n modelin ortalaması (adil model).
  şiddet   : eğitim kişilerinin o hatayla etiketli (önden + çapraz) tekrarlarındaki kural puanının
             üçte birlik dilimleri (az kaldırma dahil; puan max(d, 0)).
  birimler : açı → derece; YENI ve kol_boyu → gövde boyunun %'si; omuz için ayrıca omuz çizgisi
             eğimi (omuz_egim, yalnızca anlatım). En yakın 1'e yuvarlanır; fark yuvarlanmış
             değerlerin farkıdır. Santimetre yok.

Sağlam ölçü (olcu_surumu = "saglam"): ölçü tek kare yerine seçilen fazdaki K karelerinin medyanı.
  K = beklenen yönde fazlalığı > 0 olan ve ölçütün eklemlerinin hepsinin görünürlüğü ≥ 0,5 olan kareler;
  |K| < 3 ise görünürlük koşulu kalkar; yine < 3 ise tek kare kuralı. Tespit, faz ve faz seçimi değişmez.
  Uygulamanın varsayılanı "saglam"; Deney 3'ün birincil sonucu "tek_kare".
İki katmanlı geri bildirim: aynı SapmaKodu'ndan hasta_cumlesi (kısa; yüzde ve şiddet kelimesi yok;
  yalnızca 5°'ye yuvarlanmış derece) ve uzman ayrıntısı (hata_cumlesi, ölçülü cümle).
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

# sağlam ölçü
OLCU_SURUMLERI = ("tek_kare", "saglam")
VARSAYILAN_OLCU = "saglam"               # uygulamanın varsayılanı; Deney 3'ün birincil sonucu "tek_kare" ile
GORUNURLUK_ESIGI = 0.5                   # MediaPipe'ın varsayılan görünürlük eşiği (veriye bakılmadan)
EN_AZ_KARE = 3
# Ölçütün kare başına kullandığı eklemler (MediaPipe indeksleri). YENI ve kol_boyu'nun böldüğü dinlenme
# gövde boyu (g0) tekrar başındaki karelerden gelir, kare başına değildir; bu yüzden listede yok.
GORUNURLUK_EKLEMLERI = {"YENI": (8, 12), "bas": (7, 8, 11, 12, 23, 24), "on_kacma": (12, 16, 24),
                        "kol_boyu": (12, 16), "dirsek": (12, 14, 16), "omuz_egim": (11, 12, 23, 24)}
# cumleler.csv'deki "olcu_yolu" değerleri
YOL_TEK = "tek_kare"                         # olcu_surumu = "tek_kare"
YOL_GORUNUR = "saglam_gorunur"               # K: fazlalık > 0 ve görünürlük ≥ 0,5, |K| ≥ 3
YOL_GORUNURLUKSUZ = "saglam_gorunurluksuz"   # görünürlük koşulu kaldırıldı, |K| ≥ 3
YOL_YEDEK = "saglam_tek_kare_yedek"          # yine |K| < 3: tek kare kuralı
YOL_TEPE = "tepe"                            # az kaldırma: tepe açısı (değişmez)


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
    Adil model: n modelin aci_bandi_hatasi(..., ayrinti=True) ek çıktılarından kare başına μ ve imzalı
    bant_disi ortalaması (geçersiz karelerde NaN; hiçbir modelin geçerli olmadığı kare NaN).
    """
    mu = _nanort([np.where(a["gecerli"], a["mu"][olcut], np.nan) for a in ayrintilar])
    bd = _nanort([a["bant_disi"][olcut] for a in ayrintilar])
    return mu, bd


def fazlalik(bant_disi: np.ndarray, yon: int) -> np.ndarray:
    """Kare başına beklenen yöndeki bant dışı büyüklük, max(yön · bant_disi, 0); NaN → 0."""
    bd = np.asarray(bant_disi, float)
    fazla = np.abs(bd) if yon == 0 else np.maximum(np.sign(yon) * bd, 0.0)
    return np.where(np.isnan(fazla), 0.0, fazla)


def an_sec(kol: np.ndarray, deger: np.ndarray, mu: np.ndarray, bant_disi: np.ndarray, yon: int):
    """(faz, kare): modül açıklamasındaki faz ve an kuralı. Ölçülecek kare yoksa (None, None)."""
    faz = anlatim_fazlari(kol)
    fazla = fazlalik(bant_disi, yon)
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


def olcut_gorunurlugu(dizi: np.ndarray, olcut: str) -> np.ndarray:
    """Kare başına ölçütün kullandığı eklemlerin en küçük görünürlüğü (dizi: (kare, 33, 4))."""
    return np.min(np.asarray(dizi)[:, list(GORUNURLUK_EKLEMLERI[olcut]), 3], axis=1)


def saglam_kareler(kol, bant_disi, yon: int, faz_secimi: int, gorunurluk=None):
    """
    Sağlam ölçü: seçilen fazdaki K kareleri ve yolu. Dönüş (indeksler, yol); |K| < 3 ise (None, YOL_YEDEK).
    gorunurluk None ise görünürlük koşulu uygulanamaz ve doğrudan görünürlüksüz yola geçilir.
    """
    K0 = (anlatim_fazlari(kol) == faz_secimi) & (fazlalik(bant_disi, yon) > 0)
    if gorunurluk is not None:
        K1 = K0 & (np.nan_to_num(np.asarray(gorunurluk, float), nan=0.0) >= GORUNURLUK_ESIGI)
        if K1.sum() >= EN_AZ_KARE:
            return np.flatnonzero(K1), YOL_GORUNUR
    if K0.sum() >= EN_AZ_KARE:
        return np.flatnonzero(K0), YOL_GORUNURLUKSUZ
    return None, YOL_YEDEK


def _medyan(x, idx):
    v = np.asarray(x, float)[idx]
    v = v[np.isfinite(v)]
    return float(np.median(v)) if len(v) else None


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
    olcu_yolu: str = ""               # ölçünün hangi yoldan alındığı (YOL_*)
    olcu_kare_sayisi: int = 0         # ölçünün alındığı kare sayısı (|K|; tek kare = 1)

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
                "fark": self.fark, "birim": self.birim, "kare": self.kare, "omuz_egim_fark": self.ek_fark,
                "olcu_yolu": self.olcu_yolu, "olcu_kare_sayisi": self.olcu_kare_sayisi}


def durus_kodu(hata: str, olcut: str, yon: int, siddet: str, kol, deger, mu, bant_disi,
               ek_deger=None, ek_mu=None, olcu_surumu: str = VARSAYILAN_OLCU, gorunurluk=None) -> SapmaKodu:
    """
    Duruş hatası (omuz, baş, öne kaçma, dirsek) için sapma kodu. Faz ve an: modül açıklamasına bakın.
    olcu_surumu "tek_kare": ölçü o anki tek kare; "saglam": K karelerinin medyanı.
    gorunurluk: kare başına ölçütün eklemlerinin en küçük görünürlüğü (olcut_gorunurlugu).
    """
    if olcu_surumu not in OLCU_SURUMLERI:
        raise ValueError(olcu_surumu)
    faz, j = an_sec(kol, deger, mu, bant_disi, yon)
    if j is None:
        return SapmaKodu(hata, olcut, yon, siddet, None, None)
    ek = ek_deger is not None and ek_mu is not None
    yol = YOL_TEK
    if olcu_surumu == "saglam":
        K, yol = saglam_kareler(kol, bant_disi, yon, faz, gorunurluk)
        if K is not None:
            eo, eb = (_medyan(ek_deger, K), _medyan(ek_mu, K)) if ek else (None, None)
            return SapmaKodu(hata, olcut, yon, siddet, _medyan(deger, K), _medyan(mu, K), faz, j, eo, eb,
                             olcu_yolu=yol, olcu_kare_sayisi=len(K))
    eo, eb = (float(ek_deger[j]), float(ek_mu[j])) if ek else (None, None)
    return SapmaKodu(hata, olcut, yon, siddet, float(deger[j]), float(mu[j]), faz, j, eo, eb,
                     olcu_yolu=yol, olcu_kare_sayisi=1)


def kaldirma_kodu(yon: int, siddet: str, tepe: float, beklenen_tepe: float) -> SapmaKodu:
    """Az kaldırma: ölçü = tekrarın tepe açısı, beklenen = kalibrasyon tepelerinin medyanı; faz 'en üstte'."""
    return SapmaKodu("ERR_LOW_ABDUCTION", ht.KALDIRMA, yon, siddet, float(tepe), float(beklenen_tepe), USTTE,
                     olcu_yolu=YOL_TEPE)


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


# ---------------------------------------------------------------- hasta cümlesi
# Kısa: ne oldu (fazıyla) + ne yapmalı. Yüzde, "gövde boyu" ve şiddet kelimesi yok. Sayı yalnızca derece,
# 5°'ye yuvarlanmış; söylenen fark yuvarlanmış iki değerin farkı. Fark 0 ise (ya da işareti cümlenin
# yönüyle çelişiyorsa) sayı söylenmez. Öne kaçmada sayı söylenmez.
HASTA_FAZ = {KALDIRIRKEN: "Kolunu kaldırırken", USTTE: "Kolun yukarıdayken", INDIRIRKEN: "Kolunu indirirken"}
HASTA_ADIM = 5


def yuvarla5(x) -> int | None:
    """En yakın 5'in katı (yarımlar yukarı); None/NaN → None."""
    if x is None or not np.isfinite(x):
        return None
    return HASTA_ADIM * yuvarla(float(x) / HASTA_ADIM)


def _fark5(a, b) -> int | None:
    """yuvarla5(a) − yuvarla5(b); biri yoksa None."""
    ya, yb = yuvarla5(a), yuvarla5(b)
    return None if ya is None or yb is None else ya - yb


def _yaklasik(d) -> str:
    return f" yaklaşık {d} derece" if d is not None and d > 0 else ""


def hasta_cumlesi(k: SapmaKodu) -> str:
    """Bir sapma kodunun hasta cümlesi (ne oldu + ne yapmalı; hata başına ~20 kelimeyi geçmez)."""
    F = HASTA_FAZ.get(k.faz, "Hareket sırasında")
    h, yukari = k.hata, k.yon >= 0

    if h == "ERR_ELEVATED_SHOULDER":
        e = _fark5(k.ek_olcu, k.ek_beklenen)   # omuz çizgisi eğimi; pozitif = sağ omuz yukarı
        if not yukari:   # silkme: kulak–omuz mesafesi azaldı
            return f"{F} {k.taraf} omzunu kulağına doğru{_yaklasik(e)} kaldırdın. Omzunu aşağıda ve gevşek tut."
        d = -e if e is not None else None
        return (f"{F} {k.taraf} omzun normalden{_yaklasik(d)} aşağıdaydı. "
                "Omzunu doğal yüksekliğinde ve gevşek tut.")

    if h == "ERR_HEAD_TO_SIDE":
        if yukari:
            return f"{F} başını{_yaklasik(_fark5(k.olcu, k.beklenen))} yana eğdin. Başını dik tut, karşıya bak."
        return f"{F} başının duruşu normalden farklıydı. Başını dik tut, karşıya bak."

    if h == "ERR_ARM_FORWARD":
        if k.olcut == "kol_boyu" and yukari:
            c = f"{F} kolun vücut hizasından çıktı."
        else:
            c = "Kolun yukarıdayken öne kaçtı." if k.faz == USTTE else f"{F} kolun öne kaçtı."
        return c + " Kolunu tam yana, vücudunla aynı hizada kaldır."

    if h == "ERR_BENT_ARM":
        if not yukari:
            return f"{F} dirseğini{_yaklasik(_fark5(k.beklenen, k.olcu))} büktün. Kolunu düz tut."
        return f"{F} dirseğin normalden{_yaklasik(_fark5(k.olcu, k.beklenen))} fazla açıldı. Kolunu doğal ve düz tut."

    if h == "ERR_LOW_ABDUCTION":
        o, b = yuvarla5(k.olcu), yuvarla5(k.beklenen)
        if yukari:   # eksik kaldırma (hocanın örneği)
            d = _fark5(k.beklenen, k.olcu)
            if d is None or d <= 0:
                return "Kolunu yeterince kaldırmadın. Kolunu daha yukarı kaldır."
            return (f"Kolunu {o} dereceye kadar kaldırdın; normalde {b} dereceye çıkıyorsun. "
                    f"Kolunu yaklaşık {d} derece daha yukarı kaldır.")
        d = _fark5(k.olcu, k.beklenen)
        if d is None or d <= 0:
            return "Kolunu normalden fazla kaldırdın. Kolunu normal yüksekliğine kadar kaldırman yeterli."
        return (f"Kolunu normalden fazla kaldırdın; {o} dereceye çıktı, normalde {b} dereceye çıkıyorsun. "
                f"Kolunu {b} dereceye kadar kaldırman yeterli.")
    raise ValueError(h)


OLUMLU_HASTA = [
    "Hareketi doğru yaptın. Kolun yaklaşık {t} dereceye çıktı, omzun ve dirseğin yerindeydi.",
    "Güzel bir tekrar. Kolunu yaklaşık {t} dereceye kaldırdın; omzun, başın ve dirseğin yerindeydi.",
    "Doğru tekrar. Kolun yaklaşık {t} dereceye çıktı ve duruşun düzgündü. Böyle devam et.",
    "Bu tekrar doğru. Kolunu yaklaşık {t} dereceye kadar kaldırdın, omzun yerindeydi. Aynı şekilde devam et.",
]


def olumlu_hasta_cumlesi(tepe: float, sira: int, tohum: int = 0) -> str:
    """Doğru tekrar için kısa hasta cümlesi; varyasyon seçimi olumlu_cumle ile aynı ((sıra + tohum) mod 4)."""
    return OLUMLU_HASTA[(int(sira) + int(tohum)) % len(OLUMLU_HASTA)].format(t=yuvarla5(tepe))


def hasta_geri_bildirimi(kodlar: list[SapmaKodu], tepe: float, sira: int, tohum: int = 0) -> str:
    """En fazla 2 hata: '1. hata cümlesi' + ' Ayrıca ' + '2. hata cümlesi'. Hata yoksa olumlu cümle."""
    if not kodlar:
        return olumlu_hasta_cumlesi(tepe, sira, tohum)
    metin = hasta_cumlesi(kodlar[0])
    if len(kodlar) > 1:
        metin += " Ayrıca " + _ilk_kucuk(hasta_cumlesi(kodlar[1]))
    return metin


def iki_katman(kodlar: list[SapmaKodu], tepe: float, sira: int, tohum: int = 0) -> dict:
    """İki katman: {'hasta_cumlesi', 'uzman_ayrintisi'}; uygulama paneli ve Deney 3 bunu kullanır."""
    return {"hasta_cumlesi": hasta_geri_bildirimi(kodlar, tepe, sira, tohum),
            "uzman_ayrintisi": geri_bildirim(kodlar, tepe, sira, tohum)}
