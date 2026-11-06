"""
Uygulamanın çizimleri (Adım 6): iskelet, referans bindirme (P3), geri bildirim paneli, omuz eğrisi.

Türkçe karakter için metin PIL (ImageDraw + TTF) ile çizilir; cv2.putText Türkçe çizemez.
Font: matplotlib ile gelen DejaVu Sans (her kurulumda var).
"""
from __future__ import annotations

import textwrap

import cv2
import numpy as np
from matplotlib import font_manager
from PIL import Image, ImageDraw, ImageFont

from cekirdek import geribildirim as gb
from cekirdek import hata_turu as ht
from cekirdek.bindirme import KEMIKLER, OLCUT_UZUVLARI, Bindirici

PANEL_G = 600
YESIL, KIRMIZI, REF, BEYAZ = (90, 200, 60), (40, 40, 230), (230, 230, 0), (255, 255, 255)
P_ARKA, P_METIN, P_IKINCIL, P_DOGRU, P_HATA, P_UYARI = ((248, 247, 244), (20, 20, 20), (95, 95, 90),
                                                       (40, 140, 60), (200, 50, 40), (200, 110, 0))
_FONT = font_manager.findfont("DejaVu Sans")
_FONT_K = font_manager.findfont(font_manager.FontProperties(family="DejaVu Sans", weight="bold"))
_ONBELLEK: dict = {}


def font(boyut: int, kalin: bool = False):
    a = (boyut, kalin)
    if a not in _ONBELLEK:
        _ONBELLEK[a] = ImageFont.truetype(_FONT_K if kalin else _FONT, boyut)
    return _ONBELLEK[a]


# ---------------------------------------------------------------- iskelet
def _px(lm_xy: np.ndarray, G: int, Y: int) -> np.ndarray:
    return np.column_stack([lm_xy[:, 0] * G, lm_xy[:, 1] * Y])


def iskelet_ciz(img, P_px: np.ndarray, renk, kirmizi=frozenset(), kalinlik=3):
    for a, b in KEMIKLER:
        if not np.isfinite(P_px[[a, b]]).all():
            continue
        k = (a, b) in kirmizi
        cv2.line(img, tuple(int(v) for v in P_px[a]), tuple(int(v) for v in P_px[b]), KIRMIZI if k else renk,
                 kalinlik + (2 if k else 0), cv2.LINE_AA)
    for j in {j for kk in KEMIKLER for j in kk}:
        if np.isfinite(P_px[j]).all():
            cv2.circle(img, tuple(int(v) for v in P_px[j]), 4, renk, -1, cv2.LINE_AA)


def canli_iskelet(img, lm: np.ndarray):
    """Canlı görüntüde MediaPipe iskeleti (lm: (33, 4), x, y görüntüye göre 0–1)."""
    Y, G = img.shape[:2]
    iskelet_ciz(img, _px(lm[:, :2], G, Y), YESIL)


def kirmizi_kemikler(sonuc, kural: ht.KararKurali, j: int) -> set:
    """Kullanıcı karesi j'de (etiketli indeks) beklenen yönde banttan çıkan ölçütlerin kemikleri."""
    k_set = set()
    for k in kural.esleme.values():
        if k == ht.KALDIRMA or k not in sonuc.ayrinti["bant_disi"]:
            continue
        bd = sonuc.ayrinti["bant_disi"][k]
        if j < len(bd) and gb.fazlalik(bd[j:j + 1], kural.yon(k))[0] > 0:
            k_set.update(OLCUT_UZUVLARI.get(k, []))
    return k_set


class Oynatici:
    """Tekrar sonrası bindirmeli oynatım (P3): kullanıcı iskeleti + yarı saydam referans, banttan çıkan uzuv kırmızı."""

    def __init__(self, kayit, referans, kural, en_boy: float, kareler: dict):
        self.k, self.kural, self.kareler = kayit, kural, kareler
        self.b = Bindirici(referans.dizi, kayit.dizi, en_boy)
        self.sira = list(range(kayit.pay, len(kayit.dizi)))     # kayıt.dizi indeksleri (etiketli kısım)
        self.i = 0
        kod = kayit.sonuc.kodlar[0] if kayit.sonuc and kayit.sonuc.kodlar else None
        self.etiket_kare = (kod.kare if kod is not None and kod.kare is not None else None)
        self.etiket = ""
        if kod is not None:
            ad = ht.KISA_AD.get(kod.hata, kod.hata)
            fark = gb.yuvarla5(abs(kod.fark)) if kod.fark is not None and kod.birim == "°" else None
            self.etiket = f"{ad} ~{fark}°" if fark else ad

    @property
    def bitti(self) -> bool:
        return self.i >= len(self.sira)

    def kare(self, G: int, Y: int) -> np.ndarray | None:
        if self.bitti:
            return None
        d = self.sira[self.i]
        j = d - self.k.pay                                      # etiketli indeks
        img = self.kareler.get(self.k.bas - self.k.pay + d)
        img = np.full((Y, G, 3), 30, np.uint8) if img is None else cv2.resize(img, (G, Y))
        ref = self.b.referans_noktalari(d) * Y                  # en-boy düzeltilmiş → piksel (× yükseklik)
        kul = self.b.kullanici_noktalari(d) * Y
        iskelet_ciz(img, kul, YESIL, kirmizi_kemikler(self.k.sonuc, self.kural, j))
        kat = img.copy()                                        # referans üstte, yarı saydam
        iskelet_ciz(kat, ref, REF, kalinlik=2)
        img = cv2.addWeighted(kat, 0.6, img, 0.4, 0)
        img = metin_yaz(img, f"Tekrar {self.k.no} · oynatım", (10, 10), 18, BEYAZ, kutu=True)
        img = metin_yaz(img, "turkuaz: senin doğru tekrarın", (10, 40), 15, REF[::-1], kutu=True)
        if self.etiket and self.etiket_kare is not None and abs(j - self.etiket_kare) <= 15:
            img = metin_yaz(img, self.etiket, (10, 72), 26, P_HATA, kutu=True)
        self.i += 1
        return img


# ---------------------------------------------------------------- PIL metin
def metin_yaz(img_bgr, metin, xy, boyut, renk_rgb, kalin=False, kutu=False):
    pil = Image.fromarray(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))
    d = ImageDraw.Draw(pil)
    f = font(boyut, kalin)
    if kutu:
        x0, y0, x1, y1 = d.textbbox(xy, metin, font=f)
        d.rectangle((x0 - 6, y0 - 4, x1 + 6, y1 + 4), fill=(0, 0, 0))
    d.text(xy, metin, font=f, fill=renk_rgb)
    return cv2.cvtColor(np.asarray(pil), cv2.COLOR_RGB2BGR)


def _sar(d, metin, f, genislik):
    """Kelime kelime sarma (piksel genişliğine göre)."""
    satirlar = []
    for paragraf in metin.split("\n"):
        satir = ""
        for w in paragraf.split():
            aday = (satir + " " + w).strip()
            if d.textlength(aday, font=f) <= genislik:
                satir = aday
            else:
                if satir:
                    satirlar.append(satir)
                satir = w
        satirlar.append(satir)
    return satirlar


def panel(Y: int, oturum, uzman_acik: bool, oynatim: bool, mesaj: str = "", egzersiz: str = "") -> np.ndarray:
    pil = Image.new("RGB", (PANEL_G, Y), P_ARKA)
    d = ImageDraw.Draw(pil)
    x, y, G = 24, 18, PANEL_G - 48
    d.text((x, y), egzersiz, font=font(20, True), fill=P_METIN)
    y += 32
    if oturum.mod == "kalibrasyon":
        n = len(oturum.kalibrasyon)
        d.text((x, y), f"KALİBRASYON  {n}/{oturum.hedef}  (en az {oturum.en_az})", font=font(18, True), fill=P_UYARI)
        y += 30
        for s in _sar(d, "Fizyoterapistin gösterdiği gibi kolunu doğru şekilde yana kaldır. Her tekrardan sonra "
                         "kabul (E) ya da ret (H) et.", font(16), G):
            d.text((x, y), s, font=font(16), fill=P_IKINCIL)
            y += 21
    else:
        d.text((x, y), "DEĞERLENDİRME", font=font(18, True), fill=P_DOGRU)
        y += 30
    if oturum.uyari:
        for s in _sar(d, "⚠ " + oturum.uyari, font(17, True), G):
            d.text((x, y), s, font=font(17, True), fill=P_UYARI)
            y += 23
    y += 8
    b = oturum.bekleyen
    if b is not None:
        d.text((x, y), f"Tekrar {b.no} bitti (kol {gb.yuvarla5(b.tepe)}°). Kalibrasyona alınsın mı?",
               font=font(18, True), fill=P_METIN)
        y += 28
        d.text((x, y), "E: evet    H: hayır", font=font(18), fill=P_IKINCIL)
        y += 36
    son = oturum.degerlendirilenler()
    if son:
        k = son[-1]
        s = k.sonuc
        dogru = s.karar == ht.DOGRU
        baslik = "DOĞRU" if dogru else "HATA: " + " + ".join(ht.KISA_AD[h] for h in s.soylenen)
        d.text((x, y), f"Tekrar {k.no}", font=font(18), fill=P_IKINCIL)
        y += 26
        d.text((x, y), baslik, font=font(30, True), fill=P_DOGRU if dogru else P_HATA)
        y += 44
        for sat in _sar(d, s.hasta_cumlesi, font(25), G):          # hasta cümlesi: büyük
            d.text((x, y), sat, font=font(25), fill=P_METIN)
            y += 33
        y += 6
        if uzman_acik:
            for sat in _sar(d, "Uzman: " + s.uzman_ayrintisi, font(14), G):
                d.text((x, y), sat, font=font(14), fill=P_IKINCIL)
                y += 18
        y += 10
        y = _omuz_grafigi(d, x, y, G, 130, k)
        y += 12
        d.text((x, y), "Son tekrarlar", font=font(16, True), fill=P_METIN)
        y += 24
        for kk in reversed(son[-5:]):
            ss = kk.sonuc
            ad = "doğru" if ss.karar == ht.DOGRU else " + ".join(ht.KISA_AD[h] for h in ss.soylenen)
            d.text((x, y), f"#{kk.no}  {'✓' if ss.karar == ht.DOGRU else '✗'}  {ad}", font=font(16),
                   fill=P_DOGRU if ss.karar == ht.DOGRU else P_HATA)
            y += 22
    alt = "Q: çıkış · U: uzman ayrıntısı · R: son tekrarı oynat"
    if oturum.mod == "kalibrasyon":
        alt += " · K: kalibrasyonu bitir"
    if mesaj:
        d.text((x, Y - 52), mesaj, font=font(15, True), fill=P_UYARI)
    d.text((x, Y - 28), alt + (" · (oynatılıyor)" if oynatim else ""), font=font(13), fill=P_IKINCIL)
    return cv2.cvtColor(np.asarray(pil), cv2.COLOR_RGB2BGR)


def _omuz_grafigi(d, x, y, G, H, k) -> int:
    """Son tekrarın omuz ölçütü (kulak–omuz, YENI) ve kişiye özel bandı (μ ± τ), kare başına."""
    a = k.sonuc.ayrinti
    v, mu, tau = np.asarray(a["deger"]["YENI"]), np.asarray(a["mu"]["YENI"]), np.asarray(a["tau"]["YENI"])
    d.text((x, y), "Omuz: kulak–omuz mesafesi ve normal aralığın (gri)", font=font(14, True), fill=P_METIN)
    y += 20
    ust, alt_ = mu + tau, mu - tau
    tum = np.concatenate([v[np.isfinite(v)], ust[np.isfinite(ust)], alt_[np.isfinite(alt_)]])
    if len(tum) < 2:
        return y + H
    lo, hi = float(tum.min()), float(tum.max())
    hi = hi if hi > lo else lo + 1e-3
    n = len(v)

    def p(i, val):
        return x + G * i / max(n - 1, 1), y + H - H * (val - lo) / (hi - lo)
    d.rectangle((x, y, x + G, y + H), outline=(210, 210, 205))
    for i in range(n - 1):
        if np.isfinite([ust[i], alt_[i], ust[i + 1], alt_[i + 1]]).all():
            d.polygon([p(i, ust[i]), p(i + 1, ust[i + 1]), p(i + 1, alt_[i + 1]), p(i, alt_[i])], fill=(214, 213, 208))
    pts = [p(i, v[i]) for i in range(n) if np.isfinite(v[i])]
    if len(pts) > 1:
        d.line(pts, fill=(42, 120, 214), width=3)
    d.text((x + 4, y + H + 2), "küçülürse omuz kulağa yaklaşıyor", font=font(12), fill=P_IKINCIL)
    return y + H + 18


def ekran(video_img: np.ndarray, panel_img: np.ndarray) -> np.ndarray:
    return np.hstack([video_img, panel_img])


def satir_sar(metin: str, n: int = 60) -> str:
    return "\n".join(textwrap.wrap(metin, n))
