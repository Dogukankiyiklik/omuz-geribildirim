"""
Deney 2 galerisi (Adım 4, Güncelleme 04 not 2): sonuclar/deney2/galeri/

Ana sistem (v2 = açı bandı, yönlü), yalnızca önden + çapraz (|görüş| ≤ 60°), katı değerlendirme.
Gruplar (her birinden n video, tohum 0):
  * en sık karışan iki hata çifti (gerçek hata A → sistem B dedi, A ≠ B, ikisi de hata);
  * kaçırılan hatalar (gerçek hata → sistem "doğru" dedi).
Görsel, KARARI VEREN ölçütün eğrisini ve bandını gösterir: karışmada sistemin seçtiği hatanın ölçütü,
kaçırmada gerçek hatanın ölçütü. Kaldırma ölçütünde bant yoktur; kol açısı zamana göre ve kalibrasyon
tepelerinin tepe bandı μ ± τ çizilir (Güncelleme 05, Karar 13).

Kullanım (Deney 2'den sonra; puanlar.csv ve tahminler.csv hazır olmalı):
    python -m deneyler.deney2_galeri
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

from araclar.gorsel_kontrol import GRAFIK_Y, M_METIN, M_METIN2, M_MAVI, M_TURUNCU, SAG_G, AciBandiGorseli
from cekirdek import veri
from cekirdek import hata_turu as ht
from cekirdek.aci_bandi import aci_bandi_hatasi, aci_bandi_modeli, tepe_acisi
from cekirdek.adil_model import birini_disarida_alt_kumeler, ortalama_E
from cekirdek.etiketler import OLCUT_ADLARI, ek_hata_adlari, hata_adi
from cekirdek.konsol import utf8_cikti
from cekirdek.ozellikler import DENEY2_OLCUTLERI, ozellikler
from deneyler.tablolar import ONDEN_CAPRAZ, gorus_maskesi

OLCUTLER = DENEY2_OLCUTLERI
DOSYA_AD = {ht.DOGRU: "dogru", "ERR_ELEVATED_SHOULDER": "omuz", "ERR_HEAD_TO_SIDE": "bas",
            "ERR_ARM_FORWARD": "one_kacma", "ERR_BENT_ARM": "dirsek", "ERR_LOW_ABDUCTION": "az_kaldirma"}


def _kes(f, s):
    return {k: v[s] for k, v in f.items()}


def degerlendirme_kaydi(t: veri.Tekrar, grup: list[veri.Tekrar], yon: dict[str, int]) -> dict:
    """Görsel araç için bir tekrarın açı bandı kaydı (Deney 2'deki ile aynı hesap, verilen yönlerle)."""
    f = _kes(ozellikler(t.dizi, OLCUTLER), t.etiketli)
    dogrular = [u for u in grup if u.dogru]
    dogrular_f = [_kes(ozellikler(u.dizi, OLCUTLER), u.etiketli) for u in dogrular]
    altlar = birini_disarida_alt_kumeler(list(range(len(dogrular))))
    if t.dogru:
        i = next(j for j, u in enumerate(dogrular) if u is t)
        altlar = [altlar[i]]
    sonuc = []
    for alt in altlar:
        m = aci_bandi_modeli([dogrular_f[j] for j in alt], OLCUTLER)
        E, ek = aci_bandi_hatasi(m, f, OLCUTLER, yon=yon)
        sonuc.append((m, alt, E, ek))
    m0, alt0 = sonuc[0][0], sonuc[0][1]
    return {"t": t, "f": f, "model": m0, "digerleri": [dogrular[j] for j in alt0],
            "digerleri_f": [dogrular_f[j] for j in alt0],
            "E": ortalama_E([s[2] for s in sonuc], OLCUTLER),
            "ek": {"kapsam": float(np.mean([s[3]["kapsam"] for s in sonuc])),
                   "aralik_disi": bool(np.mean([s[3]["aralik_disi"] for s in sonuc]) > 0.5),
                   "tepe_acisi": tepe_acisi(f["kol"])},
            "model_sayisi": len(sonuc),
            "kalibrasyon_tepeleri": [[tepe_acisi(dogrular_f[j]["kol"]) for j in s[1]] for s in sonuc]}


class Deney2Gorseli(AciBandiGorseli):
    """Açı bandı görünümü + Deney 2 kararı (z tablosu, eşik, karar veren ölçüt)."""

    def __init__(self, d, satir: pd.Series, kural: pd.Series, olcut: str, video_klasoru=None):
        self.satir, self.kural = satir, kural
        yon = {k: int(kural[f"yön {k}"]) for k in ht.hata_olcutleri(kural["öne kaçma ölçütü"]).values()
               if k != ht.KALDIRMA}
        self.kaldirma = olcut == ht.KALDIRMA
        self.olcut_karar = olcut
        goster = "YENI" if self.kaldirma else olcut
        super().__init__(d, {}, goster, video_klasoru, olcutler=OLCUTLER, yon=yon)

    # kaldırma: kol açısı zamana göre + kalibrasyon tepeleri
    def _grafik_hazirla(self):
        if not getattr(self, "kaldirma", False):
            return super()._grafik_hazirla()
        kol = self.f_tam["kol"]
        tepeler = np.concatenate([np.asarray(x) for x in self.d["kalibrasyon_tepeleri"]])
        mu, tau = ht.tepe_bandi(self.d["kalibrasyon_tepeleri"][0])
        x = np.arange(len(kol))
        fig, ax = plt.subplots(figsize=(SAG_G / 100, GRAFIK_Y / 100), dpi=100)
        ax.axhspan(mu - tau, mu + tau, color=M_MAVI, alpha=0.15, lw=0,
                   label=f"tepe bandı μ ± τ = {mu:.0f}° ± {tau:.0f}°")
        ax.axhline(mu, color=M_MAVI, lw=1, ls="--")
        ax.plot(x, kol, color=M_TURUNCU, lw=2, label="bu tekrarın kol açısı")
        ax.axhline(self.ek["tepe_acisi"], color=M_TURUNCU, lw=1, ls=":", label=f"bu tekrarın tepesi {self.ek['tepe_acisi']:.0f}°")
        ax.set_xlim(-1, len(kol))
        ax.set_ylim(0, max(185, float(np.nanmax(kol)) + 5, float(tepeler.max()) + 5))
        ax.set_xlabel("kare")
        ax.set_ylabel("kol açısı (°)")
        ax.set_title(f"kaldırma — eksik {self.satir_eksik():.0f}° · E = {self.satir_d():.3f}", loc="left", fontsize=10)
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

    def satir_d(self) -> float:
        """Kaldırmanın yönlü E'si (Karar 7: modellerin ortalaması)."""
        return float(np.mean([ht.kaldirma_puanlari(self.ek["tepe_acisi"], t)[0][1]
                              for t in self.d["kalibrasyon_tepeleri"]]))

    def satir_eksik(self) -> float:
        return float(np.mean([ht.kaldirma_puanlari(self.ek["tepe_acisi"], t)[1] for t in self.d["kalibrasyon_tepeleri"]]))

    def _imlec_ciz(self, g, j):
        if not self.kaldirma:
            return super()._imlec_ciz(g, j)
        x = self._g_x(j)
        cv2.line(g, (x, self._g_y0), (x, self._g_y1), (60, 60, 60), 1, cv2.LINE_AA)
        cv2.circle(g, (x, self._g_y(self.f_tam["kol"][j])), 7, (0, 0, 0), -1, cv2.LINE_AA)

    def _kirmizi(self, j):
        return set() if self.kaldirma else super()._kirmizi(j)

    def _durum(self, j):
        if not self.kaldirma:
            return super()._durum(j)
        return f"Şu an: kare {j + 1}/{len(self.t.dizi)} · kol {self.f_tam['kol'][j]:.0f}°", False

    def _panel_hazirla(self):
        t, r, k = self.t, self.satir, self.kural
        tahmin = r["tahmin"]
        dogru_mu = tahmin == t.hata
        satirlar = [
            (f"{t.video} · {t.kamera} · yönelim {t.yonelim}° · görüş {t.gorus}° ({veri.gorus_grubu(t.gorus)})", 15, False, M_METIN2),
            (f"Tekrar {t.tekrar_no} (Segmentation.csv satır {t.satir})", 15, False, M_METIN2),
            ("", 4, False, M_METIN),
            (f"Gerçek etiket: {hata_adi(t.hata)}", 18, True, M_METIN),
        ]
        if t.ek_hata and t.ek_hata != t.hata:
            satirlar.append((f"Ek hata: {ek_hata_adlari(t.ek_hata)}", 14, False, M_METIN))
        satirlar += [(f"Sistem kararı (Deney 2, açı bandı, yönlü): {hata_adi(tahmin)}", 17, True,
                      "#2e7d32" if dogru_mu else "#c62828"),
                     ("", 4, False, M_METIN),
                     (f"z = (puan − eğitim doğrularının medyanı) / (IQR + ε)   ·   eşik T = {k['T']:.2f}", 13, False, M_METIN2)]
        for h in ht.HATALAR:
            o = ht.hata_olcutleri(k["öne kaçma ölçütü"])[h]
            z = r[f"z_{ht.KISA_AD[h]}"]
            ok = "▶ " if o == self.olcut_karar else "   "
            puan = f"E = {self.satir_d():.3f}" if o == ht.KALDIRMA else f"E = {self.E[o]:.3f}"
            satirlar.append((f"{ok}{ht.KISA_AD[h]:11s} ({o}) {puan}   z = {z:6.2f}{'  ≥ T' if z >= k['T'] else ''}",
                             13, o == self.olcut_karar, M_METIN))
        satirlar += [("", 4, False, M_METIN),
                     (f"Grafikteki ölçüt: {self.olcut_karar} ({OLCUT_ADLARI.get(self.olcut_karar, '')})", 13, True, M_METIN),
                     (f"Kapsam {self.ek['kapsam']:.0%} · tepe {self.ek['tepe_acisi']:.0f}°"
                      f"{' · KOL ARALIK DIŞI' if self.ek['aralik_disi'] else ''}", 12, False, M_METIN2)]
        self._satirlar = satirlar


def galeri(tahmin: pd.DataFrame, kurallar: pd.DataFrame, klasor: Path, n: int = 3, tohum: int = 0) -> Path:
    klasor = Path(klasor)
    klasor.mkdir(parents=True, exist_ok=True)
    p = tahmin[gorus_maskesi(tahmin, ONDEN_CAPRAZ)].reset_index(drop=True)
    hatali = p.hata != ht.DOGRU
    karisan = p[hatali & (p.tahmin != ht.DOGRU) & (p.tahmin != p.hata)]
    ciftler = karisan.groupby(["hata", "tahmin"]).size().sort_values(ascending=False, kind="stable")
    gruplar = []
    for (a, b), say in ciftler.head(2).items():
        gruplar.append((f"karisma_{DOSYA_AD[a]}_{DOSYA_AD[b]}",
                        f"{hata_adi(a)} → sistem \"{hata_adi(b)}\" dedi ({say} tekrar)",
                        (p.hata == a) & (p.tahmin == b)))
    kac = hatali & (p.tahmin == ht.DOGRU)
    gruplar.append(("kacirilan", f"Kaçırılan hatalar: hatalı tekrar, sistem \"doğru\" dedi ({int(kac.sum())} tekrar)", kac))

    tekrarlar = veri.tekrarlari_yukle(1)
    gr = veri.gruplara_ayir(tekrarlar)
    kural_kisi = kurallar.set_index("test kişisi")
    rng = np.random.default_rng(tohum)
    md = ["# Deney 2 galerisi (ana sistem: açı bandı, yönlü · önden + çapraz · katı)", "",
          "Her video: solda video + iskelet (kırmızı: grafikteki ölçütün banttan çıktığı uzuv), sağ üstte KARARI VEREN "
          "ölçütün açı bandı (kaçırmada gerçek hatanın ölçütü), sağ altta z tablosu ve karar.", "",
          "En sık karışan hata çiftleri (önden + çapraz): " +
          ", ".join(f"{ht.KISA_AD[a]} → {ht.KISA_AD[b]} = {s}" for (a, b), s in ciftler.head(5).items()), ""]
    with tempfile.TemporaryDirectory() as td:
        for ad, baslik, m in gruplar:
            md += [f"## {baslik}", "", "| Dosya | Gerçek | Ek hata | Karar | Görüş | Grafikteki ölçüt | max z | T |",
                   "| --- | --- | --- | --- | --- | --- | --- | --- |"]
            idx = np.flatnonzero(m.values)
            secim = sorted(rng.choice(idx, size=min(n, len(idx)), replace=False))
            for s, i in enumerate(secim):
                r = p.iloc[i]
                grup = gr[(r.video, r.kamera, int(r.yonelim))]
                t = next(u for u in grup if u.satir == int(r.satir))
                k = kural_kisi.loc[t.kisi]
                olcut = ht.hata_olcutleri(k["öne kaçma ölçütü"])[r.tahmin if r.tahmin != ht.DOGRU else t.hata]
                yon = {o: int(k[f"yön {o}"]) for o in ht.hata_olcutleri(k["öne kaçma ölçütü"]).values() if o != ht.KALDIRMA}
                d = degerlendirme_kaydi(t, grup, yon)
                dosya = f"{ad}_{s + 1}_{t.video}_{t.kamera}_o{t.yonelim}_t{t.tekrar_no}.mp4"
                bas = time.time()
                Deney2Gorseli(d, r, k, olcut, Path(td)).yaz(klasor / dosya)
                print(f"  {dosya}  ({time.time() - bas:.1f} s)")
                md.append(f"| `{dosya}` | {ht.KISA_AD[t.hata]} | {(ek_hata_adlari(t.ek_hata) if t.ek_hata != t.hata else '') or '–'} | "
                          f"{ht.KISA_AD[r.tahmin]} | {t.gorus}° | {olcut} | {r.max_z:.2f} | {k['T']:.2f} |")
            md.append("")
    md += ["## Neye bakmalı?",
           "- **Karışmalarda:** Videoda gerçekten etiketteki hata mı görülüyor, yoksa sistemin söylediği hata da var mı? "
           "(Örneğin baş eğerken omuz da kalkıyor olabilir; etiket yalnızca birincil hatayı veriyor.)",
           "- **Grafikteki ölçüt** gerçekten banttan çıkıyor mu, ve çıktığı an videoda o uzvun hareketiyle tutarlı mı?",
           "- **Kaçırılanlarda:** Hata gözle görülüyor mu? Görülüyorsa ölçüt neden yakalamadı (bant geniş mi, kapsam düşük mü, "
           "hata kalibrasyon aralığının dışındaki açılarda mı)?", ""]
    (klasor / "liste.md").write_text("\n".join(md), encoding="utf-8")
    print(f"Galeri: {klasor}")
    return klasor


def main():
    ap = argparse.ArgumentParser(description="Deney 2 galerisi")
    ap.add_argument("--klasor", default=str(veri.KOK / "sonuclar" / "deney2"))
    ap.add_argument("--adet", type=int, default=3)
    args = ap.parse_args()
    utf8_cikti()
    k = Path(args.klasor)
    tum = pd.read_csv(k / "tahminler.csv", encoding="utf-8-sig", keep_default_na=False, na_values=["", "nan"])
    tum["ek_hata"] = tum.ek_hata.astype(str).replace("nan", "")
    tah = tum[tum.sistem == "v2_yonlu"].reset_index(drop=True)
    kur = pd.read_csv(k / "esikler.csv", encoding="utf-8-sig")
    kur = kur[kur.sistem == "v2_yonlu"]
    galeri(tah, kur, k / "galeri", n=args.adet)


if __name__ == "__main__":
    main()
