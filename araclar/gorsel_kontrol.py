"""
Görsel kontrol aracı: bir tekrarı videoda izleyip sistemin ne gördüğünü ve neden o puanı
verdiğini kontrol etmek için.

Kullanım:
    python -m araclar.gorsel_kontrol --video ex1_Honza --kamera cam1 --yonelim 0 --tekrar 5
    python -m araclar.gorsel_kontrol --video ex1_Honza --kamera cam1 --yonelim 0 --tekrar 5 --goster
    python -m araclar.gorsel_kontrol --galeri          # Deney 1 galerisi (sonuclar/deney1/galeri/)

Ekran:
  Sol      : orijinal video + veri setinin MediaPipe iskeleti (yeşil; banttan çıkan bölge kırmızı)
             + referans iskelet (kişinin kendi doğru tekrarı; kareler aynı fazda en yakın kol açısına göre
             eşlenir, kalça ortası / gövde boyu / gövde ekseniyle geometride hizalı; yarı saydam turkuaz)
  Sağ üst  : x = kol açısı, y = seçilen ölçü; kişiye özel açı bandı (kaldırma mavi, indirme turuncu),
             tekrarın kareleri ve hareketli imleç
  Sağ alt  : gerçek etiket, E değerleri, basit eşik kararı, o anki ölçüm

Bant ve E, Deney 1'deki kişiye özel açı bandıyla AYNI hesaptır
(deneyler.deney1.kisiye_ozel_degerlendirmeleri); sayılar sonuclar/deney1/tekrarlar.csv
(kosul = kisiye_ozel) ile birebir tutar.

Basit eşik (yalnızca bu araç ve Deney 1 galerisi için; sistemin asıl kararı Deney 2'dedir):
E > eşik ise "şüpheli". Eşik = DİĞER 4 kişinin doğru tekrarlarındaki
E'nin %90'lık dilimi (test kişisinin verisi eşiğe girmez).
"""
from __future__ import annotations

import argparse
import tempfile
import time
from pathlib import Path

import cv2
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import font_manager
from PIL import Image, ImageDraw, ImageFont

from cekirdek import veri
from cekirdek import aci_bandi as ab
from cekirdek.aci_bandi import aci_bandi_hatasi, aci_eslemesi, tepe_acisi
from cekirdek.ozellikler import ozellikler
from cekirdek.bindirme import KEMIKLER, Bindirici, banttan_cikan_kemikler
from cekirdek.etiketler import OLCUT_ADLARI, ek_hata_adlari, hata_adi
from cekirdek.konsol import utf8_cikti
from deneyler.deney1 import OLCUTLER, SILKME, kisiye_ozel_degerlendirmeleri

SOL_G, SOL_Y = 540, 960          # video paneli (1080x1920'nin yarısı)
SAG_G, GRAFIK_Y = 760, 470       # sağ üst grafik
TUVAL = (SOL_Y, SOL_G + SAG_G)   # (yükseklik, genişlik)
ESIK_YUZDELIK = 90

# Renkler (BGR, OpenCV)
YESIL, KIRMIZI, REF_RENK = (90, 200, 60), (40, 40, 230), (230, 230, 0)  # REF_RENK: turkuaz
# Renkler (matplotlib / PIL)
M_MAVI, M_TURUNCU, M_GRI, M_METIN, M_METIN2 = "#2a78d6", "#eb6834", "#d6d5d0", "#0b0b0b", "#52514e"

_FONT_YOLU = font_manager.findfont("DejaVu Sans")
_FONT_KALIN = font_manager.findfont(font_manager.FontProperties(family="DejaVu Sans", weight="bold"))


def _font(boyut: int, kalin: bool = False):
    return ImageFont.truetype(_FONT_KALIN if kalin else _FONT_YOLU, boyut)


# ---------------------------------------------------------------- değerlendirme ve eşikler
def degerlendir():
    """Deney 1'in kişiye özel açı bandını baştan hesaplar (~15 s); kayıtlar ve E tablosu döner."""
    kayitlar = list(kisiye_ozel_degerlendirmeleri(veri.tekrarlari_yukle(1)))
    df = pd.DataFrame([{
        "video": d["t"].video, "kamera": d["t"].kamera, "yonelim": d["t"].yonelim,
        "tekrar_no": d["t"].tekrar_no, "satir": d["t"].satir, "kisi": d["t"].kisi,
        "hata": d["t"].hata, "ek_hata": d["t"].ek_hata, "gorus": d["t"].gorus,
        **{f"bant_{k}": d["E"][k] for k in OLCUTLER}} for d in kayitlar])
    return kayitlar, df


def esikler(df: pd.DataFrame, kisi: str, olcutler=OLCUTLER, yuzdelik: float = ESIK_YUZDELIK) -> dict:
    """Eşik = test kişisi HARİÇ diğer kişilerin doğru tekrarlarındaki E'nin yüzdeliği (birini-dışarıda-bırak)."""
    m = (df.kisi != kisi) & (df.hata == "DOGRU") & ~df.ek_hata.str.contains("ELEVATED")
    return {k: float(np.percentile(df.loc[m, f"bant_{k}"], yuzdelik)) for k in olcutler}


# ---------------------------------------------------------------- çizim yardımcıları
def _px(P: np.ndarray, olcek: float = SOL_Y) -> np.ndarray:
    """En-boy düzeltilmiş koordinat -> sol panel pikseli (x_px = x * H, y_px = y * H)."""
    return np.rint(P * olcek).astype(int)


def iskelet_ciz(img, P, renk, kalinlik=3, kirmizi=frozenset(), nokta=True):
    p = _px(P)
    for a, b in KEMIKLER:
        if np.isnan(P[[a, b]]).any():
            continue
        r = KIRMIZI if (a, b) in kirmizi else renk
        k = kalinlik + 2 if (a, b) in kirmizi else kalinlik
        cv2.line(img, tuple(p[a]), tuple(p[b]), r, k, cv2.LINE_AA)
    if nokta:
        for j in {j for kemik in KEMIKLER for j in kemik}:
            if not np.isnan(P[j]).any():
                cv2.circle(img, tuple(p[j]), 4, renk, -1, cv2.LINE_AA)


class TekrarGorseli:
    """
    Bir tekrarın görsel kontrol videosunu üretir (kişiye özel açı bandı). Sağ üst: x = kol açısı,
    y = ölçü; kaldırma (mavi) ve indirme (turuncu) bantları, tekrarın kareleri ve hareketli imleç.

    Referans iskelet (yalnızca görsel): bandın doğru tekrarlarından, tepe açısı bu tekrara en yakın olan;
    kareler zamana göre değil, AYNI FAZDA EN YAKIN KOL AÇISINA göre eşlenir ("kol bu açıdayken normal duruşun").
    Etiketli tekrarın öncesindeki ve sonrasındaki kareler videoda görünür ama değerlendirilmez.
    """

    def __init__(self, d: dict, esik: dict, olcut: str = "YENI", video_klasoru: Path | None = None,
                 olcutler=OLCUTLER, yon: dict[str, int] | None = None):
        """olcutler / yon: Deney 2 için (varsayılan: Deney 1'in omuz ölçüleri, yönsüz)."""
        self.d, self.esik, self.olcut = d, esik, olcut
        self.olcutler, self.yon = list(olcutler), yon
        self.t = t = d["t"]
        E0, self.ek = aci_bandi_hatasi(d["model"], d["f"], self.olcutler, yon=yon, ayrinti=True)
        if d.get("model_sayisi", 1) == 1:
            assert all((np.isnan(E0[k]) and np.isnan(d["E"][k])) or abs(E0[k] - d["E"][k]) < 1e-12
                       for k in self.olcutler)
        else:
            # Hatalı tekrar (adil model): E, n adet (n−1)'li modelin ortalaması; çizilen bant ve kare
            # renkleri bunların ilkinden. Gösterilen E ve kapsam deneydeki (ortalama) değerdir.
            self.ek["kapsam"] = d["ek"]["kapsam"]
        self.E = d["E"]
        self.bas = t.etiketli.start
        self.n_etiket = len(d["f"]["kol"])
        self.f_tam = ozellikler(t.dizi, self.olcutler)
        tepe = tepe_acisi(d["f"]["kol"])
        r = int(np.argmin([abs(tepe_acisi(f["kol"]) - tepe) for f in d["digerleri_f"]]))
        self.ref = d["digerleri"][r]
        ref_kol = ozellikler(self.ref.dizi, [])["kol"]
        self.bindirici = Bindirici(self.ref.dizi, t.dizi, ref_kol=ref_kol, kul_kol=self.f_tam["kol"],
                                   esleme=aci_eslemesi(ref_kol, self.f_tam["kol"]))
        self.video = (veri.video_cikar(t.video, t.kamera, video_klasoru) if video_klasoru is not None else None)
        self._grafik_hazirla()
        self._panel_hazirla()

    def _jj(self, j: int) -> int | None:
        jj = j - self.bas
        return jj if 0 <= jj < self.n_etiket else None

    def _grafik_hazirla(self):
        k, m, ek = self.olcut, self.d["model"], self.ek
        kol, y = self.d["f"]["kol"], self.d["f"][k]
        xm = ab.kutu_merkezleri()
        fig, ax = plt.subplots(figsize=(SAG_G / 100, GRAFIK_Y / 100), dpi=100)
        for p, renk in ((ab.KALDIRMA, M_MAVI), (ab.INDIRME, M_TURUNCU)):
            g = m.gecerli[p]
            mu, tau = m.mu[k][p], m.tau[k][p]
            ax.fill_between(xm[g], (mu - tau)[g], (mu + tau)[g], color=renk, alpha=0.16, lw=0)
            ax.plot(xm[g], mu[g], color=renk, lw=1, ls="--", label=f"{ab.FAZ_ADLARI[p]} bandı")
            s = ek["faz"] == p
            dis = s & (np.nan_to_num(ek["kare_hatasi"][k]) > 0)
            ax.scatter(kol[s & ~dis], y[s & ~dis], s=9, color=renk, alpha=0.6, lw=0)
            ax.scatter(kol[dis], y[dis], s=18, color=renk, edgecolor="black", linewidth=0.7, zorder=3)
        ax.scatter([], [], s=18, color="white", edgecolor="black", label="bant dışı kare")
        ax.set_xlim(0, 185)
        ax.set_xlabel("kol açısı (°)")
        ax.set_ylabel(f"{k}: {OLCUT_ADLARI.get(k, k)}")
        ax.set_title(f"{k} — açı bandı ve bu tekrar   (E = {self.E[k]:.3f}, kapsam {ek['kapsam']:.0%})",
                     loc="left", fontsize=10)
        ax.spines[["top", "right"]].set_visible(False)
        ax.yaxis.grid(True, color="#e4e3df", lw=0.8)
        ax.legend(loc="best", frameon=False, fontsize=7.5)
        fig.tight_layout()
        fig.canvas.draw()
        self.grafik = cv2.cvtColor(np.asarray(fig.canvas.buffer_rgba()), cv2.COLOR_RGBA2BGR)
        bbox = ax.get_window_extent()
        Hfig = self.grafik.shape[0]
        self._g_y0, self._g_y1 = int(Hfig - bbox.y1), int(Hfig - bbox.y0)
        self._g_x = lambda v: int(round(ax.transData.transform((v, 0))[0]))
        self._g_y = lambda v: int(round(Hfig - ax.transData.transform((0, v))[1]))
        plt.close(fig)

    # ---- sağ alt: metin paneli (sabit kısım)
    def _panel_hazirla(self):
        t, k = self.t, self.olcut
        self.supheli = self.E[k] > self.esik[k]
        satirlar = [
            (f"{t.video} · {t.kamera} · yönelim {t.yonelim}° · görüş {t.gorus}° ({veri.gorus_grubu(t.gorus)})", 15, False, M_METIN2),
            (f"Tekrar {t.tekrar_no} (Segmentation.csv satır {t.satir}) · videoda kare {t.ilk_kare}–{t.ilk_kare + len(t.dizi) - 1}", 15, False, M_METIN2),
            ("", 6, False, M_METIN),
            (f"Gerçek etiket: {hata_adi(t.hata)}", 19, True, M_METIN),
        ]
        if t.ek_hata:
            satirlar.append((f"Ek hata: {ek_hata_adlari(t.ek_hata)}", 15, False, M_METIN))
        satirlar += [("", 6, False, M_METIN),
                     ("Sistem (Deney 1, kişiye özel açı bandı) — bant hatası E:", 15, True, M_METIN)]
        for o in self.olcutler:
            isaret = "BANT DIŞI" if self.E[o] > self.esik[o] else "normal"
            satirlar.append((f"{'▶ ' if o == k else '   '}{o:8s} E = {self.E[o]:.3f}   eşik {self.esik[o]:.3f}   {isaret}",
                             14, o == k, M_METIN))
        karar = "OMUZ SİLKMESİ ŞÜPHESİ" if self.supheli else "normal görünüyor"
        satirlar += [("", 6, False, M_METIN),
                     (f"Basit eşik kararı ({k}): {karar}", 18, True, "#c62828" if self.supheli else "#2e7d32"),
                     ("Eşik: diğer 4 kişinin doğru tekrarlarındaki E'nin %90'lık dilimi.", 12, False, M_METIN2),
                     ("Sistemin asıl kararı ve cümlesi bu araçta yok (Deney 2 ve 3).", 12, False, M_METIN2)]
        satirlar.insert(-3, (f"Kapsam {self.ek['kapsam']:.0%} · tepe {self.ek['tepe_acisi']:.0f}° · kalibrasyon tepesi en çok "
                             f"{self.d['model'].en_yuksek_aci:.0f}°{' · KOL ARALIK DIŞI' if self.ek['aralik_disi'] else ''}",
                             13, False, M_METIN2))
        self._satirlar = satirlar

    # ---- bir kareyi oluştur
    def _kare(self, j: int, video_karesi: np.ndarray | None) -> np.ndarray:
        tuval = np.full((*TUVAL, 3), 255, np.uint8)
        # sol: video + iskeletler
        sol = (cv2.resize(video_karesi, (SOL_G, SOL_Y), interpolation=cv2.INTER_AREA)
               if video_karesi is not None else np.full((SOL_Y, SOL_G, 3), 40, np.uint8))
        i = self.bindirici.referans_karesi(j)
        katman = sol.copy()
        P_ref = self.bindirici.referans_noktalari(j)
        iskelet_ciz(katman, P_ref, (0, 0, 0), kalinlik=8, nokta=False)       # koyu kenar
        iskelet_ciz(katman, P_ref, REF_RENK, kalinlik=5, nokta=False)
        sol = cv2.addWeighted(katman, 0.65, sol, 0.35, 0)
        iskelet_ciz(sol, self.bindirici.kullanici_noktalari(j), YESIL, kalinlik=2, kirmizi=self._kirmizi(j))
        tuval[:, :SOL_G] = sol
        # sağ üst: grafik + imleç
        g = self.grafik.copy()
        self._imlec_ciz(g, j)
        tuval[:GRAFIK_Y, SOL_G:SOL_G + g.shape[1]] = g[:GRAFIK_Y, :SAG_G]
        # metinler (PIL: Türkçe karakter)
        pil = Image.fromarray(cv2.cvtColor(tuval, cv2.COLOR_BGR2RGB))
        ciz = ImageDraw.Draw(pil)
        ciz.rectangle([0, 0, SOL_G, 46], fill=(0, 0, 0))
        ciz.text((8, 4), "yeşil: veri setinin iskeleti   kırmızı: banttan çıkan bölge", font=_font(13), fill=(255, 255, 255))
        ciz.text((8, 24), "turkuaz (saydam): referans = kişinin kendi doğru tekrarı, hizalı", font=_font(13), fill=(255, 255, 255))
        y = GRAFIK_Y + 6
        for metin, boyut, kalin, renk in self._satirlar:
            ciz.text((SOL_G + 14, y), metin, font=_font(boyut, kalin), fill=renk)
            y += boyut + 6
        metin, disarida = self._durum(j)
        ciz.text((SOL_G + 14, y + 4), metin, font=_font(13, disarida), fill="#c62828" if disarida else M_METIN)
        return cv2.cvtColor(np.asarray(pil), cv2.COLOR_RGB2BGR)

    def _kirmizi(self, j: int):
        jj = self._jj(j)
        return set() if jj is None else banttan_cikan_kemikler(self.ek["kare_hatasi"], jj, [self.olcut])

    def _imlec_ciz(self, g, j: int):
        kol, v = self.f_tam["kol"][j], self.f_tam[self.olcut][j]
        x = self._g_x(min(kol, 185))
        cv2.line(g, (x, self._g_y0), (x, self._g_y1), (60, 60, 60), 1, cv2.LINE_AA)
        if self._jj(j) is not None:
            cv2.circle(g, (x, self._g_y(v)), 7, (0, 0, 0), -1, cv2.LINE_AA)

    def _durum(self, j: int) -> tuple[str, bool]:
        kol, v = self.f_tam["kol"][j], self.f_tam[self.olcut][j]
        bas = f"Şu an: kare {j + 1}/{len(self.t.dizi)} · kol {kol:.0f}° · {self.olcut} = {v:.3f}"
        jj = self._jj(j)
        if jj is None:
            return bas + " · pay karesi (değerlendirilmez)", False
        if not self.ek["gecerli"][jj]:
            return bas + " · kalibrasyon aralığı dışı (değerlendirilmez)", False
        mu, tau = self.ek["mu"][self.olcut][jj], self.ek["tau"][self.olcut][jj]
        dis = bool(self.ek["kare_hatasi"][self.olcut][jj] > 0)
        return (bas + f" ({ab.FAZ_ADLARI[int(self.ek['faz'][jj])]}; bant {mu - tau:.3f} – {mu + tau:.3f})"
                + (" → BANT DIŞI" if dis else "")), dis

    def video_kareleri(self):
        n = len(self.t.dizi)
        if self.video is None:
            for _ in range(n):
                yield None
            return
        cap = cv2.VideoCapture(str(self.video))
        cap.set(cv2.CAP_PROP_POS_FRAMES, self.t.ilk_kare)
        for _ in range(n):
            ok, img = cap.read()
            yield img if ok else None
        cap.release()

    def yaz(self, cikti: Path, fps: float = 30.0) -> Path:
        cikti.parent.mkdir(parents=True, exist_ok=True)
        w = cv2.VideoWriter(str(cikti), cv2.VideoWriter_fourcc(*"mp4v"), fps, (TUVAL[1], TUVAL[0]))
        for j, img in enumerate(self.video_kareleri()):
            w.write(self._kare(j, img))
        w.release()
        return cikti


AciBandiGorseli = TekrarGorseli  # eski ad (deneyler/deney2_galeri.py kullanır)


def oynat(yol: Path, fps: float = 30.0) -> None:
    """MP4'ü pencerede oynatır. Boşluk: duraklat, q / Esc: çık."""
    cap = cv2.VideoCapture(str(yol))
    bekle = max(1, int(1000 / fps))
    while True:
        ok, img = cap.read()
        if not ok:
            break
        cv2.imshow("Görsel kontrol (boşluk: duraklat, q: çık)", img)
        tus = cv2.waitKey(bekle) & 0xFF
        if tus == ord(" "):
            tus = cv2.waitKey(0) & 0xFF
        if tus in (ord("q"), 27):
            break
    cap.release()
    cv2.destroyAllWindows()


# ---------------------------------------------------------------- tek tekrar ve galeri
def tek_tekrar(video, kamera, yonelim, tekrar, olcut="YENI", cikti=None, fps=30.0, goster=False):
    kayitlar, df = degerlendir()
    d = next((d for d in kayitlar if d["t"].video == video and d["t"].kamera == kamera
              and d["t"].yonelim == yonelim and d["t"].tekrar_no == tekrar), None)
    if d is None:
        raise SystemExit(f"Tekrar bulunamadı: {video} {kamera} yönelim {yonelim} tekrar {tekrar} "
                         "(ya yok ya da grubunda 3'ten az doğru tekrar var)")
    cikti = Path(cikti) if cikti else veri.KOK / "sonuclar" / "gorsel_kontrol" / f"{video}_{kamera}_o{yonelim}_t{tekrar}_{olcut}.mp4"
    with tempfile.TemporaryDirectory() as td:
        g = TekrarGorseli(d, esikler(df, d["t"].kisi), olcut, Path(td))
        g.yaz(cikti, fps)
    print(f"Gerçek etiket: {d['t'].hata} · {olcut} E = {g.E[olcut]:.3f} · eşik {g.esik[olcut]:.3f} · "
          f"karar: {'şüpheli' if g.supheli else 'normal'}")
    print(f"Yazıldı: {cikti}")
    if goster:
        oynat(cikti, fps)
    return cikti


GALERI_GRUPLARI = {
    "yakalanan_silkme": ("Doğru yakalanan silkmeler", "Silkme etiketli, sistem şüpheli dedi."),
    "kacirilan_silkme": ("Kaçırılan silkmeler", "Silkme etiketli, sistem normal dedi."),
    "yanlis_alarm": ("Yanlış alarm verilen doğru tekrarlar", "Doğru etiketli, sistem şüpheli dedi."),
}


GORUS_SECENEKLERI = {"onden": "önden (0–20°)", "capraz": "çapraz (30–60°)", "profil": "profil (70–90°)"}


def galeri(klasor: Path | None = None, n: int = 3, olcut: str = "YENI", tohum: int = 0, kayitlar_df=None,
           gorus: str | None = None) -> Path:
    """
    Deney 1 galerisi: her gruptan n örnek (tohum sabit) ve neye bakılacağını anlatan liste.md.
    gorus: None (hepsi) ya da "onden" / "capraz" / "profil" — yalnızca o görüş grubundan örnek seçer.
    Eşikler görüş grubundan bağımsızdır (tüm görüşlerdeki doğru tekrarlardan).
    """
    varsayilan = "galeri" if gorus is None else f"galeri_{gorus}"
    klasor = Path(klasor) if klasor else veri.KOK / "sonuclar" / "deney1" / varsayilan
    klasor.mkdir(parents=True, exist_ok=True)
    kayitlar, df = kayitlar_df if kayitlar_df is not None else degerlendir()
    esik_kisi = {p: esikler(df, p, [olcut]) for p in df.kisi.unique()}
    df["esik"] = df.kisi.map(lambda p: esik_kisi[p][olcut])
    df["supheli"] = df[f"bant_{olcut}"] > df["esik"]
    ek_silkme = df.ek_hata.str.contains("ELEVATED")
    secili = (df.gorus.map(veri.gorus_grubu) == GORUS_SECENEKLERI[gorus]) if gorus else pd.Series(True, index=df.index)
    maske = {
        "yakalanan_silkme": (df.hata == SILKME) & df.supheli & secili,
        "kacirilan_silkme": (df.hata == SILKME) & ~df.supheli & secili,
        "yanlis_alarm": (df.hata == "DOGRU") & ~ek_silkme & df.supheli & secili,
    }
    rng = np.random.default_rng(tohum)
    baslik_ek = f", yalnızca {GORUS_SECENEKLERI[gorus]}" if gorus else ""
    md = [f"# Deney 1 galerisi ({olcut}, basit eşik{baslik_ek})", "",
          "Basit eşik (yalnızca bu galeri için): E > eşik ise \"şüpheli\". Eşik = test kişisi hariç diğer 4 kişinin "
          f"doğru tekrarlarındaki E'nin %{ESIK_YUZDELIK}'lık dilimi. Sistemin asıl karar kuralı Deney 2'dedir "
          "(cekirdek/hata_turu.py).", "",
          "Grup büyüklükleri (3 kamera dahil): " + ", ".join(f"{a} = {int(m.sum())}" for a, m in maske.items()), ""]
    with tempfile.TemporaryDirectory() as td:
        for ad, m in maske.items():
            baslik, aciklama = GALERI_GRUPLARI[ad]
            md += [f"## {baslik}", aciklama, "", "| Dosya | Gerçek etiket | Ek hata | Görüş | E | Eşik |", "| --- | --- | --- | --- | --- | --- |"]
            secim = rng.choice(np.flatnonzero(m.values), size=min(n, int(m.sum())), replace=False)
            for s, idx in enumerate(sorted(secim)):
                d, r = kayitlar[idx], df.iloc[idx]
                t = d["t"]
                dosya = f"{ad}_{s + 1}_{t.video}_{t.kamera}_o{t.yonelim}_t{t.tekrar_no}.mp4"
                bas = time.time()
                TekrarGorseli(d, esikler(df, t.kisi), olcut, Path(td)).yaz(klasor / dosya)
                print(f"  {dosya}  ({time.time() - bas:.1f} s)")
                md.append(f"| `{dosya}` | {hata_adi(t.hata)} | {ek_hata_adlari(t.ek_hata) or '–'} | "
                          f"{t.gorus}° ({veri.gorus_grubu(t.gorus)}) | {r[f'bant_{olcut}']:.3f} | {r.esik:.3f} |")
            md.append("")
    md += ["## Neye bakmalı?",
           "- **İskelet oturuyor mu?** Yeşil noktalar kişinin kulak, omuz, dirsek, bilek ve kalçasına oturuyor mu? "
           "Oturmuyorsa ya MediaPipe yanılmış ya da video ile iskelet arasında kare kayması var.",
           "- **Referans (turkuaz) mantıklı mı?** Turkuaz kol, yeşil kolla aynı açıda mı (kareler kol açısına göre eşlenir)? Kalçalar üst üste mi? Silkmede turkuaz kulak–omuz çizgisi yeşilden uzun görünmeli (referansta omuz kulaktan daha uzak).",
           "- **Kırmızı ne zaman yanıyor?** Kulak–omuz çizgisi kırmızıyken videoda omuz gerçekten kulağa doğru kalkıyor mu?",
           "- **Kaçırılan silkmelerde:** Silkme gözle görülüyor mu? Görülmüyorsa etiket/performans belirsiz olabilir; "
           "görülüyorsa ölçüt neden kaçırdı (profil görüş mü, bant mı geniş)?",
           "- **Yanlış alarmlarda:** Kişi gerçekten omzunu kaldırıyor mu (etiket hatası olabilir), yoksa başka bir şey mi "
           "(gövde eğilmesi, MediaPipe titremesi, referans tekrarın kendisi mi tuhaf)?", ""]
    (klasor / "liste.md").write_text("\n".join(md), encoding="utf-8")
    print(f"Galeri: {klasor}")
    return klasor


def main():
    ap = argparse.ArgumentParser(description="Görsel kontrol aracı")
    ap.add_argument("--video", help="ör. ex1_Honza")
    ap.add_argument("--kamera", default="cam1", choices=list(veri.KAMERALAR))
    ap.add_argument("--yonelim", type=int, default=0)
    ap.add_argument("--tekrar", type=int, help="Segmentation.csv'deki repetition_number")
    ap.add_argument("--olcut", default="YENI", choices=OLCUTLER)
    ap.add_argument("--cikti", help="MP4 yolu (varsayılan: sonuclar/gorsel_kontrol/...)")
    ap.add_argument("--fps", type=float, default=30.0, help="ör. 15 = yarı hızda oynatım")
    ap.add_argument("--goster", action="store_true", help="yazdıktan sonra pencerede oynat")
    ap.add_argument("--galeri", action="store_true", help="Deney 1 galerisini üret")
    ap.add_argument("--gorus", choices=list(GORUS_SECENEKLERI), help="galeri: yalnızca bu görüş grubundan örnekler")
    ap.add_argument("--adet", type=int, default=3, help="galeri: her gruptan kaç video")
    ap.add_argument("--tohum", type=int, default=0, help="galeri: örneklerin rastgele seçimi")
    args = ap.parse_args()
    utf8_cikti()
    if args.galeri:
        galeri(n=args.adet, olcut=args.olcut, tohum=args.tohum, gorus=args.gorus)
    elif args.video and args.tekrar:
        tek_tekrar(args.video, args.kamera, args.yonelim, args.tekrar, args.olcut, args.cikti,
                   args.fps, args.goster)
    else:
        ap.error("--video ve --tekrar ya da --galeri gerekli")


if __name__ == "__main__":
    main()
