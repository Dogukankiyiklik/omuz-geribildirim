"""
Uygulamanın çizimleri: iskelet, referans bindirme (P3), geri bildirim paneli, omuz eğrisi.

Türkçe karakter için metin PIL (ImageDraw + TTF) ile çizilir; cv2.putText Türkçe çizemez.
Font: matplotlib ile gelen DejaVu Sans (her kurulumda var).
"""
from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np
from matplotlib import font_manager
from PIL import Image, ImageDraw, ImageFont

from cekirdek import bilgi_notlari as bn
from cekirdek import geribildirim as gb
from cekirdek import hata_turu as ht
from cekirdek import tekrar_ayirici as ta
from cekirdek.bindirme import KEMIKLER, OLCUT_UZUVLARI, Bindirici

PANEL_G = 600
DUSUK_KALDIRMA = 120.0   # yalnızca kalibrasyonda hatırlatma; karar kuralına girmez
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

    def __init__(self, kayit, referans, kural, en_boy: float, kareler: dict, ayna: bool = False):
        self.k, self.kural, self.kareler, self.ayna = kayit, kural, kareler, ayna
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
        if self.ayna:                                           # yalnızca gösterim; ölçüm aynasız karelerden
            img = cv2.flip(img, 1)
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


@dataclass
class Dugme:
    eylem: str
    etiket: str
    kutu: tuple = (0, 0, 0, 0)      # panel koordinatı (x0, y0, x1, y1)

    def icinde(self, x: int, y: int) -> bool:
        x0, y0, x1, y1 = self.kutu
        return x0 <= x <= x1 and y0 <= y <= y1


def dugmeler(oturum, video: bool) -> list[Dugme]:
    """Duruma göre panelin altındaki düğmeler (fare ile tıklanır; parantezde klavye kısayolu)."""
    d = []
    if oturum.mod == "kalibrasyon":
        if oturum.bekleyen is not None:
            d += [Dugme("kabul", "✓ Kabul (E)"), Dugme("ret", "✗ Reddet (H)")]
        if oturum.geri_alinabilir:
            d.append(Dugme("geri_al", "Son kabulü geri al (Z)"))
        d += [Dugme("bitir", "Kalibrasyonu bitir (K)"), Dugme("bastan", "Baştan (B)")]
    else:
        if oturum.geri_alinabilir:
            d.append(Dugme("geri_al", "Kalibrasyona geri dön (Z)"))
        d += [Dugme("oynat", "Son tekrarı oynat (R)"), Dugme("uzman", "Uzman ayrıntısı (U)")]
    if video:
        d.append(Dugme("duraklat", "Duraklat (Boşluk)"))
    d.append(Dugme("cikis", "Çıkış (Q)"))
    return d


def _dugme_yerlesimi(d, liste: list[Dugme], x: int, G: int, Y: int) -> int:
    """Düğmeleri alttan yukarı satırlara dizer; düğme alanının üst y'sini döndürür."""
    f, yuk, ara = font(16, True), 38, 8
    satirlar, satir, gen = [], [], 0
    for b in liste:
        w = int(d.textlength(b.etiket, font=f)) + 24
        if satir and gen + ara + w > G:
            satirlar.append(satir)
            satir, gen = [], 0
        satir.append((b, w))
        gen += (ara if gen else 0) + w
    if satir:
        satirlar.append(satir)
    ust = Y - 12 - len(satirlar) * (yuk + ara)
    yy = ust
    for satir in satirlar:
        xx = x
        for b, w in satir:
            b.kutu = (xx, yy, xx + w, yy + yuk)
            ana = b.eylem in ("kabul", "ret")
            dolgu = {"kabul": P_DOGRU, "ret": P_HATA}.get(b.eylem, (232, 231, 226))
            d.rounded_rectangle(b.kutu, radius=7, fill=dolgu, outline=(180, 180, 175))
            d.text((xx + 12, yy + 9), b.etiket, font=f, fill=(255, 255, 255) if ana else P_METIN)
            xx += w + ara
        yy += yuk + ara
    return ust


def _simdi(oturum) -> tuple[str, str, tuple]:
    """Kişiye o anda ne yapması gerektiğini söyleyen kısa yönerge (başlık, alt satır, renk)."""
    ay = oturum.ayirici
    if not oturum.kisi_var:
        return "Seni göremiyorum", "Başından kalçana kadar kadrajda ol.", P_HATA
    if not oturum.kalca_gorunur and ay.durum == "dinlenme":
        return "Kalçaların görünmüyor", "Biraz geri çekil ya da kamerayı aşağı eğ: kalçaların kadraja girsin.", P_HATA
    if ay.durum == "hareket":
        tepe = ay.anlik_tepe
        if oturum.mod == "kalibrasyon" and np.isfinite(tepe) and tepe < ta.EN_AZ_TEPE:
            return "Tekrar sürüyor…", f"Sayılması için kol en az {ta.EN_AZ_TEPE:.0f}°'ye çıkmalı.", P_DOGRU
        return "Tekrar sürüyor…", "Kolunu indirince tekrar biter.", P_DOGRU
    if ay.durum == "bitis_ara":
        return "Kolunu indir ve 1–2 saniye bekle", "", P_DOGRU
    g = ay.son_gecersiz
    if g is not None and len(ay.y) - g["kare"] < 4 * oturum.fps:
        if g["tepe"] < ta.EN_AZ_TEPE:
            neden = f"Kol en fazla {g['tepe']:.0f}°'ye çıktı; en az {ta.EN_AZ_TEPE:.0f}° gerekli."
        else:
            sure = f"{g['sure_s']:.1f}".replace(".", ",")
            en_az = f"{ta.EN_AZ_SURE_S:g}".replace(".", ",")
            neden = f"Çok hızlıydı ({sure} sn); en az {en_az} sn sürmeli."
        return "Bu hareket tekrar sayılmadı", neden, P_UYARI
    kol = oturum.kol_anlik
    if np.isfinite(kol) and kol > ta.BITIS_ESIGI:
        return "Kolunu tam aşağı indir", "Tekrarlar arasında kol aşağıda dinlensin.", P_UYARI
    return ("Hazır: kolunu yana kaldır",
            "Kolunu yandan, rahatça çıkabildiğin en yüksek noktaya kaldır (genelde baş hizasının üstü); "
            "sonra indir, 1–2 saniye bekle.", P_METIN)


def _aci_gostergesi(d, x, y, G, kol, normal: float | None = None) -> int:
    """Kol açısı çubuğu (0–180°). Çizgi: tekrarın sayılması için en az açı (hedef değil);
    değerlendirmede ayrıca kişinin kalibrasyondaki tepe açısı (normali)."""
    d.text((x, y), f"Kol açısı: {kol:.0f}°" if np.isfinite(kol) else "Kol açısı: –", font=font(15), fill=P_IKINCIL)
    y += 22
    H = 14
    d.rectangle((x, y, x + G, y + H), fill=(226, 225, 220))
    if np.isfinite(kol):
        d.rectangle((x, y, x + int(G * min(max(kol, 0), 180) / 180), y + H), fill=(42, 120, 214))
    xx = x + int(G * ta.EN_AZ_TEPE / 180)
    d.line((xx, y - 3, xx, y + H + 3), fill=P_METIN, width=2)
    d.text((xx + 3, y + H + 2), f"en az {ta.EN_AZ_TEPE:.0f}° (sayılması için)", font=font(11), fill=P_IKINCIL)
    if normal is not None and np.isfinite(normal):
        xx = x + int(G * min(normal, 180) / 180)
        d.line((xx, y - 3, xx, y + H + 3), fill=P_DOGRU, width=3)
        d.text((xx - 100, y + H + 2), f"senin normalin {normal:.0f}°", font=font(11, True), fill=P_DOGRU)
    return y + H + 18


def panel(Y: int, oturum, uzman_acik: bool, oynatim: bool, mesaj: str = "", egzersiz: str = "",
          kabul_kalan: float | None = None, video: bool = False) -> tuple[np.ndarray, list[Dugme]]:
    """Sağ panel. Dönüş: (görüntü, düğmeler). kabul_kalan: bekleyen tekrarın otomatik kabulüne kalan saniye."""
    pil = Image.new("RGB", (PANEL_G, Y), P_ARKA)
    d = ImageDraw.Draw(pil)
    x, y, G = 24, 16, PANEL_G - 48
    liste = dugmeler(oturum, video)
    alt_sinir = _dugme_yerlesimi(d, liste, x, G, Y)
    if mesaj:
        alt_sinir -= 4
        for sat in reversed(_sar(d, mesaj, font(16, True), G)):
            alt_sinir -= 22
            d.text((x, alt_sinir), sat, font=font(16, True), fill=P_UYARI)
    alt_sinir -= 6

    def yaz(metin, boyut, renk, kalin=False, aralik=None):
        nonlocal y
        for sat in _sar(d, metin, font(boyut, kalin), G):
            if y + boyut > alt_sinir:
                return
            d.text((x, y), sat, font=font(boyut, kalin), fill=renk)
            y += aralik or int(boyut * 1.32)

    d.text((x, y), egzersiz, font=font(20, True), fill=P_METIN)
    y += 30
    if oturum.mod == "kalibrasyon":
        n = len(oturum.kalibrasyon)
        yaz(f"1. KALİBRASYON — kabul edilen: {n}/{oturum.hedef}  (en az {oturum.en_az})", 18, P_UYARI, True)
        yaz("Kolunu doğru şekilde, yandan yukarı tam kaldır. Sistem bu tekrarlardan senin normal hareketini "
            "öğrenir; hatalar sonra buna göre bulunur.", 15, P_IKINCIL)
        yaz(bn.KALIBRASYON_YONERGESI, 16, P_METIN, True)
    else:
        yaz(f"2. DEĞERLENDİRME — kalibrasyon: {len(oturum.kalibrasyon)} tekrar", 18, P_DOGRU, True)
    if oturum.uyari:
        yaz("⚠ " + oturum.uyari, 16, P_UYARI, True)
    y += 6

    # Şimdi ne yapmalı (canlı yönerge + kol açısı), çerçeveli kutu
    baslik, alt, renk = _simdi(oturum)
    kutu_ust = y
    y += 10
    x0, G0 = x, G
    x, G = x + 14, G - 28
    yaz(baslik, 24 if oturum.mod == "kalibrasyon" else 20, renk, True)
    if alt:
        yaz(alt, 15, P_IKINCIL)
    normal = (float(np.median([k.tepe for k in oturum.kalibrasyon]))
              if oturum.mod == "degerlendirme" and oturum.kalibrasyon else None)
    y = _aci_gostergesi(d, x, y + 2, G, oturum.kol_anlik, normal)
    x, G = x0, G0
    d.rounded_rectangle((x - 6, kutu_ust, x + G + 6, y + 4), radius=8, outline=(200, 200, 195), width=2)
    y += 16

    b = oturum.bekleyen
    if b is not None:
        yaz(f"Tekrar {b.no} bitti (kol {gb.yuvarla5(b.tepe)}°). Kalibrasyona alınsın mı?", 19, P_METIN, True)
        if np.isfinite(b.tepe) and b.tepe < DUSUK_KALDIRMA:
            yaz(f"⚠ Kol yalnızca {gb.yuvarla5(b.tepe)}°'ye çıktı. Bu egzersizde kol genelde ~150°'ye (baş "
                "hizasının üstüne) kalkar. Tam kaldırmadıysan Reddet.", 16, P_UYARI, True)
        if kabul_kalan is not None:
            yaz(f"{max(kabul_kalan, 0):.0f} saniye içinde kendiliğinden KABUL edilecek. "
                "Tekrar kötü olduysa Reddet'e tıkla ya da H'ye bas.", 16, P_IKINCIL)
        else:
            yaz("Kabul'e ya da Reddet'e tıkla (E / H).", 16, P_IKINCIL)
        y += 8
    son = oturum.degerlendirilenler()
    if son:
        k = son[-1]
        s = k.sonuc
        dogru = s.karar == ht.DOGRU
        yaz(f"Son tekrar: {k.no}", 16, P_IKINCIL)
        yaz("DOĞRU" if dogru else "HATA: " + " + ".join(ht.KISA_AD[h] for h in s.soylenen), 30,
            P_DOGRU if dogru else P_HATA, True, 42)
        if k.kalite_sorunu:
            yaz(f"⚠ Bu tekrarda {k.kalite_sorunu}; sonuç güvenilir değil.", 16, P_UYARI, True)
        yaz(s.hasta_cumlesi, 23, P_METIN)                                # hasta cümlesi: büyük
        if k.notlar is not None and k.notlar.kamera:                     # yalnızca arayüz
            yaz("⚠ " + bn.KAMERA_NOTU, 15, P_UYARI, True)
        if k.notlar is not None and k.notlar.metinler:                   # bilgi notu, hata değil
            yaz("Bilgi: " + " ".join(k.notlar.metinler), 17, (42, 100, 170), True)
        y += 4
        if uzman_acik:
            yaz("Uzman: " + s.uzman_ayrintisi, 14, P_IKINCIL)
        y += 8
        if y + 150 < alt_sinir:
            y = _omuz_grafigi(d, x, y, G, 100, k) + 8
        if y + 46 < alt_sinir:
            yaz("Son tekrarlar", 16, P_METIN, True, 22)
            for kk in reversed(son[-5:]):
                ss = kk.sonuc
                ad = "doğru" if ss.karar == ht.DOGRU else " + ".join(ht.KISA_AD[h] for h in ss.soylenen)
                yaz(f"#{kk.no}  {'✓' if ss.karar == ht.DOGRU else '✗'}  {ad}", 16,
                    P_DOGRU if ss.karar == ht.DOGRU else P_HATA, aralik=21)
    elif oturum.mod == "degerlendirme":
        yaz("Henüz değerlendirilen tekrar yok. Bir tekrar yap: sonuç burada görünecek.", 17, P_IKINCIL)
    if oynatim:
        d.text((PANEL_G - 150, 18), "▶ oynatılıyor", font=font(14, True), fill=P_IKINCIL)
    return cv2.cvtColor(np.asarray(pil), cv2.COLOR_RGB2BGR), liste


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
