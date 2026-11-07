"""
Görsel kontrol aracı eki (Adım 6b, Karar 48 madde 6): SILUET için açı bandı görünümü + omuz bölgesi çizimi.

Görsel kontrol aracının açı bandı görünümünü (araclar/gorsel_kontrol.py, AciBandiGorseli) kullanır; farkları:
  * İskelet, bant ve ölçütler segmentasyon çalıştırmasının (MediaPipe 1.2.2) noktalarından.
  * Sol panelde omuz bölgesi: saklanan kutu (camgöbeği), 5 arama sütunu (yeşil), siluet sınırı (sarı),
    kulak ve omuz noktaları (mor). Sol altta aynı bölgenin büyütülmüş hali, maske mavi tonla.
  * Bant ve E, deneyler/siluet.py'deki ile aynı hesap (tek ölçüt, nan_atla=True).

Örnek seçimi (önceden kayıt, ADIM_06b ayrıntı g; tohum 0): ortak kümede aynı (video, kamera, yönelim)
grubunda doğru ve silkme tekrarı olan gruplardan biri → o gruptan bir doğru ve bir silkme → bütün ortak
kümedeki yanlış alarm (doğru, E > eşik) ve kaçırma (silkme, E ≤ eşik) birleşiminden biri. Eşik = görsel
kontrol aracının geçici eşiği (test kişisi hariç 4 kişinin doğru tekrarlarındaki SILUET E'sinin %90'ı).

Kullanım: python -m deneyler.siluet --gorsel
"""
from __future__ import annotations

import dataclasses
import tempfile
import time
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw

from araclar.gorsel_kontrol import (M_METIN, M_METIN2, SOL_G, SOL_Y, AciBandiGorseli, _font, esikler)
from cekirdek import veri
from cekirdek.aci_bandi import aci_bandi_hatasi, aci_eslemesi
from cekirdek.bindirme import Bindirici, banttan_cikan_kemikler
from cekirdek.etiketler import OLCUT_ADLARI, ek_hata_adlari, hata_adi
from deneyler.deney1 import SILKME

OLCUT = "SILUET"
OLCEK = SOL_G / veri.VIDEO_GENISLIK      # sol panel / orijinal video (0,5)
ICE_G, ICE_Y = 250, 330                  # büyütülmüş bölge
CAMGOBEGI, SUTUN, SINIR, NOKTA = (230, 230, 0), (60, 200, 60), (0, 230, 255), (220, 60, 220)  # BGR
OLCUT_ADLARI.setdefault("SILUET", "omuz silueti – kulak / gövde")


class SiluetGorseli(AciBandiGorseli):
    def __init__(self, d: dict, ozl: dict, esik: dict, video_klasoru: Path | None = None):
        self.d, self.esik, self.olcut = d, esik, OLCUT
        self.olcutler, self.yon = [OLCUT], None
        o = ozl[id(d["t"])]
        self.o = o
        self.t = dataclasses.replace(d["t"], dizi=o["dizi"])           # 1.2.2 noktaları
        f = o["f"]
        E0, self.ek = aci_bandi_hatasi(d["model"], f, [OLCUT], ayrinti=True, nan_atla=True)
        if d["model_sayisi"] == 1:
            assert (np.isnan(E0[OLCUT]) and np.isnan(d["E"])) or abs(E0[OLCUT] - d["E"]) < 1e-12
        else:
            self.ek["kapsam"] = d["kapsam"]    # Karar 7: gösterilen E ve kapsam modellerin ortalaması
        self.E = {OLCUT: d["E"]}
        self.d = {**d, "f": f}
        self.f_tam = o["tam"]
        self._konum = {int(i): n for n, i in enumerate(o["etiket_idx"])}
        tepe = float(np.nanmax(f["kol"]))
        ref = min(d["digerleri"], key=lambda u: abs(float(np.nanmax(ozl[id(u)]["f"]["kol"])) - tepe))
        ref_o = ozl[id(ref)]
        self.bindirici = Bindirici(ref_o["dizi"], o["dizi"], ref_kol=ref_o["tam"]["kol"], kul_kol=o["tam"]["kol"],
                                   esleme=aci_eslemesi(ref_o["tam"]["kol"], o["tam"]["kol"]))
        self.video = (veri.video_cikar(self.t.video, self.t.kamera, video_klasoru)
                      if video_klasoru is not None else None)
        self._ice_kutu()
        self._grafik_hazirla()
        self._panel_hazirla()

    # ---- etiketli ve tutulan karelerin konumu (kişi bulunamayan kareler çıkarılmış olabilir)
    def _jj(self, j: int):
        return self._konum.get(j)

    def _ice_kutu(self):
        s = self.o["s"]
        xs, ar = s["xler"], s["arama"]
        x0 = np.nanmin(xs) - 80 if np.isfinite(xs).any() else 300
        x1 = np.nanmax(xs) + 80 if np.isfinite(xs).any() else 600
        y0 = np.nanmin(ar[:, 0]) - 50 if np.isfinite(ar).any() else 500
        y1 = np.nanmax(ar[:, 1]) + 50 if np.isfinite(ar).any() else 900
        # en-boy oranını büyütülmüş pencereye uydur
        w, h = x1 - x0, y1 - y0
        if w / h < ICE_G / ICE_Y:
            ek = (h * ICE_G / ICE_Y - w) / 2
            x0, x1 = x0 - ek, x1 + ek
        else:
            ek = (w * ICE_Y / ICE_G - h) / 2
            y0, y1 = y0 - ek, y1 + ek
        self._ice_alan = tuple(int(round(v)) for v in (x0, y0, x1, y1))

    def _panel_hazirla(self):
        t, k = self.t, OLCUT
        self.supheli = bool(np.isfinite(self.E[k]) and self.E[k] > self.esik[k])
        s = [(f"{t.video} · {t.kamera} · yönelim {t.yonelim}° · görüş {t.gorus}° ({veri.gorus_grubu(t.gorus)})", 15, False, M_METIN2),
             (f"Tekrar {t.tekrar_no} (Segmentation.csv satır {t.satir}) · videoda kare {t.ilk_kare}–{t.ilk_kare + len(t.dizi) - 1}", 15, False, M_METIN2),
             ("", 6, False, M_METIN),
             (f"Gerçek etiket: {hata_adi(t.hata)}", 19, True, M_METIN)]
        if t.ek_hata:
            s.append((f"Ek hata: {ek_hata_adlari(t.ek_hata)}", 15, False, M_METIN))
        y = self.d.get("E_YENI_mp122", np.nan)
        s += [("", 6, False, M_METIN),
              ("Adım 6b (açı bandı, MediaPipe 1.2.2 noktaları ve maskesi):", 15, True, M_METIN),
              (f"▶ SILUET      E = {self.E[k]:.3f}   eşik {self.esik[k]:.3f}   "
               f"{'BANT DIŞI' if self.supheli else 'normal'}", 14, True, M_METIN),
              (f"   YENI_mp122  E = {y:.3f}   (karşılaştırma için)", 14, False, M_METIN),
              (f"Kapsam {self.ek['kapsam']:.0%} · SILUET geçerli kare {self.o['gecerli_kare_orani']:.0%} · "
               f"tepe {self.ek['tepe_acisi']:.0f}°", 13, False, M_METIN2),
              ("", 6, False, M_METIN),
              (f"Geçici karar: {'OMUZ SİLKMESİ ŞÜPHESİ' if self.supheli else 'normal görünüyor'}", 18, True,
               "#c62828" if self.supheli else "#2e7d32"),
              ("Eşik: diğer 4 kişinin doğru tekrarlarındaki SILUET E'sinin %90'lık dilimi (yalnızca görsel).", 12, False, M_METIN2),
              ("Sol: camgöbeği kutu = saklanan bölge, yeşil = 5 sütun, sarı = siluet sınırı, mor = kulak/omuz.", 12, False, M_METIN2)]
        self._satirlar = s

    def _kirmizi(self, j: int):
        jj = self._jj(j)
        if jj is None:
            return set()
        return banttan_cikan_kemikler({"YENI": np.nan_to_num(self.ek["kare_hatasi"][OLCUT])}, jj, ["YENI"])

    def _imlec_ciz(self, g, j: int):
        kol, v = self.f_tam["kol"][j], self.f_tam[OLCUT][j]
        if not np.isfinite(kol):
            return
        x = self._g_x(min(kol, 185))
        cv2.line(g, (x, self._g_y0), (x, self._g_y1), (60, 60, 60), 1, cv2.LINE_AA)
        if self._jj(j) is not None and np.isfinite(v):
            cv2.circle(g, (x, self._g_y(v)), 7, (0, 0, 0), -1, cv2.LINE_AA)

    def _durum(self, j: int):
        kol, v = self.f_tam["kol"][j], self.f_tam[OLCUT][j]
        bas = f"Şu an: kare {j + 1}/{len(self.t.dizi)} · kol {kol:.0f}° · SILUET = {v:.3f}"
        jj = self._jj(j)
        if jj is None:
            return bas + " · pay karesi (değerlendirilmez)", False
        if not self.ek["gecerli"][jj]:
            return bas + " · kalibrasyon aralığı dışı (değerlendirilmez)", False
        if not np.isfinite(v):
            return bas + f" · NaN ({self.o['s']['neden'][j]})", False
        mu, tau = self.ek["mu"][OLCUT][jj], self.ek["tau"][OLCUT][jj]
        dis = bool(np.nan_to_num(self.ek["kare_hatasi"][OLCUT][jj]) > 0)
        return bas + f" (bant {mu - tau:.3f} – {mu + tau:.3f})" + (" → BANT DIŞI" if dis else ""), dis

    # ---- omuz bölgesi çizimi
    def _bolge_ciz(self, img, j: int, olcek: float, ofset=(0, 0)):
        s = self.o["s"]
        roi = self.o["roiler"][j]
        P = self.o["dizi"][j, :, :2] * [veri.VIDEO_GENISLIK, veri.VIDEO_YUKSEKLIK]

        def p(x, y):
            return int(round((x - ofset[0]) * olcek)), int(round((y - ofset[1]) * olcek))
        if roi is not None:
            cv2.rectangle(img, p(roi.x0, roi.y0), p(roi.x1, roi.y1), CAMGOBEGI, 1, cv2.LINE_AA)
        ya, yb = s["arama"][j]
        for x, y in zip(s["xler"][j], s["sinirlar"][j]):
            if np.isfinite(x) and np.isfinite(ya):
                cv2.line(img, p(x, ya), p(x, yb), SUTUN, 1, cv2.LINE_AA)
            if np.isfinite(y):
                cv2.circle(img, p(x, y), max(2, int(3 * olcek)), SINIR, -1, cv2.LINE_AA)
        for e in (8, 12):
            if np.isfinite(P[e]).all():
                cv2.circle(img, p(*P[e]), max(3, int(4 * olcek)), NOKTA, -1, cv2.LINE_AA)

    def _ice(self, video_karesi, j: int):
        x0, y0, x1, y1 = self._ice_alan
        H, W = veri.VIDEO_YUKSEKLIK, veri.VIDEO_GENISLIK
        parca = np.full((y1 - y0, x1 - x0, 3), 40, np.uint8)
        if video_karesi is not None:
            a, b = max(x0, 0), max(y0, 0)
            c, d = min(x1, W), min(y1, H)
            if c > a and d > b:
                parca[b - y0:d - y0, a - x0:c - x0] = video_karesi[b:d, a:c]
        roi = self.o["roiler"][j]
        if roi is not None:
            m = np.zeros(parca.shape[:2], bool)
            a, b = max(roi.x0, x0), max(roi.y0, y0)
            c, d = min(roi.x1, x1), min(roi.y1, y1)
            if c > a and d > b:
                m[b - y0:d - y0, a - x0:c - x0] = roi.bitler[b - roi.y0:d - roi.y0, a - roi.x0:c - roi.x0]
            parca[m] = (0.5 * parca[m] + np.array([127, 60, 0])).astype(np.uint8)
        olcek = ICE_G / (x1 - x0)
        parca = cv2.resize(parca, (ICE_G, ICE_Y), interpolation=cv2.INTER_LINEAR)
        self._bolge_ciz(parca, j, olcek, (x0, y0))
        cv2.rectangle(parca, (0, 0), (ICE_G - 1, ICE_Y - 1), (255, 255, 255), 2)
        return parca

    def _kare(self, j: int, video_karesi):
        tuval = super()._kare(j, video_karesi)
        sol = tuval[:, :SOL_G]
        self._bolge_ciz(sol, j, OLCEK)
        ice = self._ice(video_karesi, j)
        sol[SOL_Y - ICE_Y - 8:SOL_Y - 8, 8:8 + ICE_G] = ice
        pil = Image.fromarray(cv2.cvtColor(tuval, cv2.COLOR_BGR2RGB))
        ciz = ImageDraw.Draw(pil)
        ciz.rectangle([0, 0, SOL_G, 46], fill=(0, 0, 0))
        ciz.text((8, 4), "yeşil: MediaPipe 1.2.2 iskeleti (bu çalıştırma)   kırmızı: kulak–omuz bant dışı",
                 font=_font(13), fill=(255, 255, 255))
        ciz.text((8, 24), "turkuaz (saydam): referans = kişinin kendi doğru tekrarı, hizalı", font=_font(13),
                 fill=(255, 255, 255))
        ciz.text((12, SOL_Y - ICE_Y - 30), "omuz bölgesi (büyütülmüş; mavi = maske)",
                 font=_font(13, True), fill=(255, 255, 255))
        return cv2.cvtColor(np.asarray(pil), cv2.COLOR_RGB2BGR)


# ---------------------------------------------------------------- örnek seçimi ve üretim
def ornek_sec(df: pd.DataFrame, tohum: int = 0) -> tuple[list[tuple[str, int]], pd.Series]:
    """ADIM_06b ayrıntı g. Dönüş: [(rol, df indeksi), ...] ve tekrar başına eşik."""
    o = df[df.ortak].copy()
    esik = {p: esikler(o, p, [OLCUT])[OLCUT] for p in o.kisi.unique()}
    o["esik"] = o.kisi.map(esik)
    ek_silkme = o.ek_hata.str.contains("ELEVATED")
    dogru = (o.hata == "DOGRU") & ~ek_silkme
    silkme = o.hata == SILKME
    rng = np.random.default_rng(tohum)
    anahtar = ["video", "kamera", "yonelim"]
    gruplar = sorted(k for k, g in o.groupby(anahtar) if dogru[g.index].any() and silkme[g.index].any())
    g = gruplar[int(rng.integers(len(gruplar)))]
    m = (o[anahtar] == pd.Series(g, index=anahtar)).all(axis=1)
    d_idx = int(rng.choice(o.index[m & dogru]))
    s_idx = int(rng.choice(o.index[m & silkme]))
    yanlis = o.index[dogru & (o.bant_SILUET > o.esik)]
    kacan = o.index[silkme & (o.bant_SILUET <= o.esik)]
    aday = sorted(set(yanlis) | set(kacan))
    u_idx = int(rng.choice(aday))
    rol3 = "yanlis_alarm" if u_idx in set(yanlis) else "kacirma"
    return [("dogru", d_idx), ("silkme", s_idx), (rol3, u_idx)], o["esik"]


def ornekler_uret(df: pd.DataFrame, tekrarlar, ozl, klasor: Path, tohum: int = 0) -> Path:
    from deneyler.siluet import degerlendirmeler
    klasor.mkdir(parents=True, exist_ok=True)
    secim, esik_sutun = ornek_sec(df, tohum)
    anahtar = {(t.video, t.kamera, t.yonelim, t.satir): t for t in tekrarlar}
    md = ["# Adım 6b — SILUET görsel örnekleri", "",
          "Seçim önceden kayıtlı (ADIM_06b ayrıntı g, tohum 0). Eşik yalnızca görsel içindir: test kişisi hariç "
          "4 kişinin doğru tekrarlarındaki SILUET E'sinin %90'lık dilimi.", "",
          "| Dosya | Rol | Gerçek etiket | Görüş | SILUET E | Eşik | YENI_mp122 E |", "| --- | --- | --- | --- | --- | --- | --- |"]
    with tempfile.TemporaryDirectory() as td:
        for rol, idx in secim:
            r = df.loc[idx]
            t = anahtar[(r.video, r.kamera, int(r.yonelim), int(r.satir))]
            grup = [u for u in tekrarlar if (u.video, u.kamera, u.yonelim) == (t.video, t.kamera, t.yonelim)]
            d = next(x for x in degerlendirmeler(grup, ozl, OLCUT) if x["t"] is t)
            d["E_YENI_mp122"] = float(r.bant_YENI_mp122)
            dosya = f"{rol}_{t.video}_{t.kamera}_o{t.yonelim}_t{t.tekrar_no}.mp4"
            bas = time.time()
            g = SiluetGorseli(d, ozl, {OLCUT: float(esik_sutun.loc[idx])}, Path(td))
            g.yaz(klasor / dosya)
            print(f"  {dosya} ({time.time() - bas:.1f} s)")
            md.append(f"| `{dosya}` | {rol} | {hata_adi(t.hata)} | {t.gorus}° | {r.bant_SILUET:.3f} | "
                      f"{esik_sutun.loc[idx]:.3f} | {r.bant_YENI_mp122:.3f} |")
    md += ["", "## Neye bakmalı?",
           "- Sarı noktalar (siluet sınırı) boyun–omuz çizgisine oturuyor mu? Saça, kulağa ya da arka plana mı takılıyor?",
           "- Kol yukarıdayken sütunlar kola mı değiyor (Karar 48 madde 4: ayrı kural yok, bant bunu içermeli)?",
           "- Silkmeli tekrarda sarı çizgi kulağa doğru kalkıyor mu; grafikteki nokta bandın altına iniyor mu?", ""]
    (klasor / "liste.md").write_text("\n".join(md), encoding="utf-8")
    print(f"Görsel örnekler: {klasor}")
    return klasor
