"""
Deney 1 — Omuz silkme ölçütlerinin karşılaştırılması (REHAB26-ViewAngles, Ex1 kol abdüksiyonu).

Soru: Hangi omuz ölçütü "omuz yükselmesi" etiketli tekrarları doğru tekrarlardan (ve diğer
hatalardan) en iyi ayırıyor? Kişiye özel tolerans bandı (M39) bu ayrımı iyileştiriyor mu?

İki değerlendirme:
  ham  : kişiye özel model yok; tekrar başına göre en büyük sapma (%90 yüzdelik)
  bant : kişiye özel tolerans bandı, birini-dışarıda-bırak; hatalı tekrarlar da aynı sayıda
         (n−1) doğru tekrardan kurulan modelle ölçülür (adil model)

Referans: referans/deney1_omuz_olcutleri.py. Bu betik aynı mantığı cekirdek/ ile çalıştırır.

Kullanım:
    python -m deneyler.deney1                     # orijinal veri (zip), en-boy 9/16, tohum 0
    python -m deneyler.deney1 --kaynak npz        # danışmanın küçültülmüş kopyası
Çıktı: sonuclar/deney1/{tekrarlar.csv, ozet.csv, bootstrap.csv, hata_turu_ortalama.csv}
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path

import numpy as np
import pandas as pd

from cekirdek import veri
from cekirdek.konsol import sonuclari_yaz, utf8_cikti
from cekirdek.bant import bant_hatasi, bant_modeli
from cekirdek.degerlendirme import auc, guven_araligi, ham_skor, kisi_bootstrap, psi
from cekirdek.ozellikler import DENEY1_OLCUTLERI, ozellikler

OLCUTLER = DENEY1_OLCUTLERI
SILKME = "ERR_ELEVATED_SHOULDER"
GORUS_GRUPLARI = ["önden (0–20°)", "çapraz (30–60°)", "profil (70–90°)"]


def tekrar_degerlendirmeleri(kaynak: str = "zip", en_boy: float = veri.EN_BOY, tohum: int = 0,
                             npz_yolu=veri.KUCUK_NPZ, tekrarlar=None):
    """
    Deney 1'in tekrar tekrar değerlendirmesi. Her tekrar için bir sözlük üretir:
      t (Tekrar), f (ölçüt eğrileri), model (bant), ref (bandın referans Tekrar'ı),
      ref_f (referansın ölçüt eğrileri), E (bant hataları), H (ham skorlar).
    Görsel kontrol aracı da bunu kullanır; böylece videoda gösterilen bant ve E, tablodakiyle aynıdır.
    Rastgele sayıların çekilme sırası referans kodla aynıdır (değiştirme: regresyon testi bozulur).
    """
    rng = np.random.default_rng(tohum)
    if tekrarlar is None:
        tekrarlar = veri.tekrarlari_yukle(1, kaynak=kaynak, npz_yolu=npz_yolu)
    for (vid, kam, o), grup in veri.gruplara_ayir(tekrarlar).items():
        tl = [{"t": t, "f": ozellikler(t.dizi, OLCUTLER, en_boy)} for t in grup]
        dogrular = [x for x in tl if x["t"].dogru]
        if len(dogrular) < 3:
            continue
        for x in tl:
            t = x["t"]
            if t.dogru:  # birini-dışarıda-bırak: kendisi modele girmesin
                digerleri = [u for u in dogrular if u is not x]
            else:        # adil karşılaştırma: hatalı tekrar da (n−1) doğru tekrarlık modelle ölçülür
                atla = rng.integers(len(dogrular))
                digerleri = [u for i, u in enumerate(dogrular) if i != atla]
            model = bant_modeli([u["f"] for u in digerleri], rng, OLCUTLER)
            ref = digerleri[model["ref_indeks"]]
            yield {"t": t, "f": x["f"], "model": model, "ref": ref["t"], "ref_f": ref["f"],
                   "E": bant_hatasi(model, x["f"], OLCUTLER), "H": ham_skor(x["f"], OLCUTLER)}


def tekrar_skorlari(kaynak: str = "zip", en_boy: float = veri.EN_BOY, tohum: int = 0,
                    npz_yolu=veri.KUCUK_NPZ) -> pd.DataFrame:
    """Her tekrar için bant ve ham skorlar (tekrar başına bir satır)."""
    kayit = []
    for d in tekrar_degerlendirmeleri(kaynak, en_boy, tohum, npz_yolu):
        t, E, H = d["t"], d["E"], d["H"]
        satir = {"video": t.video, "kamera": t.kamera, "yonelim": t.yonelim, "gorus": t.gorus,
                 "hata": t.hata, "ek_hata": t.ek_hata, "satir": t.satir}
        satir.update({f"bant_{k}": E[k] for k in OLCUTLER})
        satir.update({f"ham_{k}": H[k] for k in OLCUTLER})
        kayit.append(satir)
    df = pd.DataFrame(kayit)
    df["kisi"] = df.video.str.split("_").str[1]
    df["gorus_abs"] = df.gorus.abs()
    df["gorus_grubu"] = pd.Categorical(df.gorus.map(veri.gorus_grubu), categories=GORUS_GRUPLARI)
    return df


def maskeler(df: pd.DataFrame):
    """silkme / doğru / diğer hatalar. Ek hatası silkme olan tekrarlar doğru ve diğer gruplarına girmez."""
    silkme = df.hata == SILKME
    ek_silkme = df.ek_hata.str.contains("ELEVATED")
    dogru = (df.hata == "DOGRU") & ~ek_silkme
    diger = (df.hata != "DOGRU") & ~silkme & ~ek_silkme
    return silkme, dogru, diger


def ozet_tablosu(df: pd.DataFrame) -> pd.DataFrame:
    silkme, dogru, diger = maskeler(df)
    satirlar = []
    for yontem in ["ham", "bant"]:
        for k in OLCUTLER:
            c = f"{yontem}_{k}"
            satir = {"yöntem": yontem, "ölçüt": k,
                     "AUC silkme/doğru": auc(df.loc[silkme, c], df.loc[dogru, c]),
                     "AUC silkme/diğer hatalar": auc(df.loc[silkme, c], df.loc[diger, c])}
            for g in GORUS_GRUPLARI:
                m = df.gorus_grubu == g
                satir[f"AUC {g}"] = auc(df.loc[silkme & m, c], df.loc[dogru & m, c])
            satir["Ψ (M39)"] = psi(df, c, SILKME) if yontem == "bant" else np.nan
            satirlar.append(satir)
    return pd.DataFrame(satirlar)


def bootstrap_tablosu(df: pd.DataFrame, n: int = 2000, tohum: int = 1) -> pd.DataFrame:
    """Bant yöntemi, AUC silkme/doğru için kişi bazlı bootstrap %95 güven aralığı."""
    def istatistik(b):
        s, d, _ = maskeler(b)
        return {k: auc(b.loc[s, f"bant_{k}"], b.loc[d, f"bant_{k}"]) for k in OLCUTLER}

    bs = kisi_bootstrap(df, istatistik, n=n, tohum=tohum)
    bs["YENI − M39_F2"] = bs["YENI"] - bs["M39_F2"]
    satirlar = []
    for k in bs.columns:
        alt, ust = guven_araligi(bs[k])
        satirlar.append({"ölçüt": k, "ortalama": bs[k].mean(), "GA %2,5": alt, "GA %97,5": ust})
    return pd.DataFrame(satirlar)


def calistir(kaynak="zip", en_boy=veri.EN_BOY, tohum=0, cikti=veri.KOK / "sonuclar" / "deney1",
             npz_yolu=veri.KUCUK_NPZ, bootstrap_n=2000, yazdir=True) -> pd.DataFrame:
    t0 = time.time()
    df = tekrar_skorlari(kaynak, en_boy, tohum, npz_yolu)
    tablo = ozet_tablosu(df)
    cikti = Path(cikti)
    cikti.mkdir(parents=True, exist_ok=True)
    ort = df.groupby("hata")[[f"bant_{k}" for k in OLCUTLER]].mean()
    bs = bootstrap_tablosu(df, n=bootstrap_n) if bootstrap_n else None
    tablolar = {"tekrarlar": df, "ozet": tablo, "hata_turu_ortalama": ort.reset_index()}
    if bs is not None:
        tablolar["bootstrap"] = bs
    sonuclari_yaz(tablolar, cikti)  # CSV'ler + Excel kopyası (sonuclar.xlsx)

    if yazdir:
        silkme, dogru, diger = maskeler(df)
        print(f"Kaynak: {kaynak}, en-boy: {en_boy:.4f}, tohum: {tohum}")
        print(f"Tekrar sayıları (3 kamera dahil): silkme={silkme.sum()}, doğru={dogru.sum()}, "
              f"diğer hatalar={diger.sum()}\n")
        pd.set_option("display.width", 200)
        print(tablo.round(3).to_string(index=False))
        if bs is not None:
            print(f"\nBant yöntemi, AUC silkme/doğru için %95 güven aralığı "
                  f"(kişi bazlı bootstrap, {bootstrap_n} tekrar):")
            for _, r in bs.iterrows():
                print(f"  {r['ölçüt']:14s} ort. {r['ortalama']:.3f}, %95 GA {r['GA %2,5']:.3f} – {r['GA %97,5']:.3f}")
        print("\nHata türüne göre ortalama bant hatası:")
        print(ort.round(3).to_string())
        print(f"\nSüre: {time.time() - t0:.1f} s · Çıktı: {cikti}")
    return tablo


def main():
    ap = argparse.ArgumentParser(description="Deney 1: omuz silkme ölçütleri")
    ap.add_argument("--kaynak", choices=["zip", "npz"], default="zip")
    ap.add_argument("--en-boy", type=float, default=veri.EN_BOY)
    ap.add_argument("--tohum", type=int, default=0)
    ap.add_argument("--cikti", default=str(veri.KOK / "sonuclar" / "deney1"))
    ap.add_argument("--galeri-yok", action="store_true",
                    help="sonda galeri videolarını üretme (galeri ~1–2 dk sürer, videos.zip gerekir)")
    args = ap.parse_args()
    utf8_cikti()
    calistir(args.kaynak, args.en_boy, args.tohum, args.cikti)
    if not args.galeri_yok and args.kaynak == "zip" and veri.VIDEO_ZIP.exists():
        from araclar.gorsel_kontrol import galeri  # görsel kontrol aracı; çekirdeği içe aktarır
        print("\nGaleri üretiliyor (her gruptan 3 video)...")
        galeri(Path(args.cikti) / "galeri", tohum=args.tohum)


if __name__ == "__main__":
    main()
