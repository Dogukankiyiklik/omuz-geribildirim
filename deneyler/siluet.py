"""
Adım 6b — omuz silueti ölçütü `SILUET` ile `YENI_mp122`'nin karşılaştırması (Karar 48; önceden kayıt:
ilerleme/ADIM_06b.md "Önceden belirlenenler" ve "Uygulama ayrıntıları").

Önce segmentasyon çalıştırması gerekir: python -m araclar.siluet_segment (kullanıcı, ~1,5–2 saat).

Değerlendirme Deney 1 v2'nin v2 koşulunun aynısıdır: açı bandı, yönsüz, pay hariç, Karar 7 adil modeli,
bütün sabitler aynı (cekirdek/aci_bandi.py). Her ölçüt kendi modeliyle (nan_atla=True; NaN içermeyen
YENI_mp122'de sonuç nan_atla=False ile aynıdır). Birincil AUC ve bootstrap, iki ölçütün de E'si olan
tekrarlarda (ortak küme). Birleşik ölçüt yok.

Kullanım:
    python -m deneyler.siluet                 # değerlendirme, birkaç dakika → sonuclar/siluet/
    python -m deneyler.siluet --gorsel        # ayrıca 3 görsel örnek video (sonuclar/siluet/gorsel/)
    python -m deneyler.siluet --onbellek veri/ara/siluet_sinama --sinama   # kod sınaması (AUC yok)
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path

import numpy as np
import pandas as pd

from araclar.siluet_segment import ONBELLEK, ONDEN_CAPRAZ_SINIR, Onbellek, onbellek_yolu
from cekirdek import siluet as sl
from cekirdek import veri
from cekirdek.adil_model import adil_ortalama_hata
from cekirdek.aci_bandi import aci_bandi_hatasi, aci_bandi_modeli
from cekirdek.degerlendirme import auc, guven_araligi, kisi_bootstrap
from cekirdek.konsol import sonuclari_yaz, utf8_cikti
from cekirdek.ozellikler import OLCUTLER as KAYITLI_OLCUTLER, Iskelet
from deneyler.deney1 import GORUS_GRUPLARI, maskeler

OLCUTLER = ["SILUET", "YENI_mp122"]
CIKTI = veri.KOK / "sonuclar" / "siluet"
DENEY1_V2_OZET = veri.KOK / "sonuclar" / "deney1_v2" / "ozet.csv"
BOOTSTRAP_N, BOOTSTRAP_TOHUM = 2000, 1


# ---------------------------------------------------------------- tekrar başına ölçütler
def tekrar_ozellikleri(t: veri.Tekrar, ob: Onbellek) -> dict:
    """
    Bir tekrarın (pay dahil) bu çalıştırmadan ölçütleri. Kişi bulunamayan kareler (kol açısı NaN) iki
    ölçütten de çıkarılır (ayrıntı c). Dönüş: f (etiketli ve tutulan kareler: kol, SILUET, YENI_mp122),
    tam (bütün kareler), tut (bütün karelerde tutulan kare maskesi), etiket_idx (f'nin karelerinin tam
    dizideki indeksleri) ve betimsel sayılar.
    """
    dizi, roiler = ob.tekrar(t.ilk_kare, len(t.dizi))
    s = sl.siluet_dizisi(dizi, roiler, ob.genislik, ob.yukseklik)
    kol = KAYITLI_OLCUTLER["kol"](Iskelet(dizi, ob.genislik / ob.yukseklik))
    tut = np.isfinite(kol)
    etiket = np.zeros(len(dizi), bool)
    etiket[t.etiketli] = True
    sec = etiket & tut
    tam = {"kol": kol, "SILUET": s["SILUET"], "YENI_mp122": s["YENI_mp122"]}
    return {"f": {k: v[sec] for k, v in tam.items()}, "tam": tam, "tut": tut,
            "etiket_idx": np.flatnonzero(sec), "dizi": dizi, "roiler": roiler, "s": s,
            "kisi_yok": int((etiket & ~tut).sum()), "etiketli_kare": int(etiket.sum()),
            "gecerli_kare_orani": float(np.isfinite(s["SILUET"][sec]).mean()) if sec.any() else np.nan,
            "tasan": s["tasan"],
            "neden": pd.Series(np.asarray(s["neden"], dtype=object)[sec]).value_counts().to_dict()}


def tekrarlar_ve_ozellikler(onbellek: Path = ONBELLEK, sinama: bool = False):
    """Önden + çapraz Ex1 tekrarları ve ölçütleri. sinama=True: yalnızca önbellekte tam olan tekrarlar."""
    T = [t for t in veri.tekrarlari_yukle(1) if abs(t.gorus) <= ONDEN_CAPRAZ_SINIR]
    obler, ozl, eksik = {}, {}, []
    for t in T:
        anahtar = (t.video, t.kamera)
        if anahtar not in obler:
            yol = onbellek_yolu(*anahtar, onbellek)
            obler[anahtar] = Onbellek(yol) if yol.exists() else None
        ob = obler[anahtar]
        if ob is None:
            eksik.append(anahtar)
            continue
        try:
            ozl[id(t)] = tekrar_ozellikleri(t, ob)
        except KeyError:
            if not sinama:
                raise
    if eksik and not sinama:
        raise SystemExit("Önbellekte eksik video var: " + ", ".join(sorted({f"{v} {k}" for v, k in eksik}))
                         + "\nÖnce: python -m araclar.siluet_segment")
    return [t for t in T if id(t) in ozl], ozl, obler


# ---------------------------------------------------------------- v2 değerlendirmesi (ölçüt başına ayrı model)
def _model_ve_hata(fl: list[dict], f: dict, olcut: str):
    m = aci_bandi_modeli(fl, [olcut], nan_atla=True)
    E, ek = aci_bandi_hatasi(m, f, [olcut], nan_atla=True)
    ek["_model"] = m
    return E, ek


def degerlendirmeler(tekrarlar, ozl, olcut: str):
    """
    Deney 1 v2'nin v2 koşulu, tek ölçüt. Doğru tekrar: birini-dışarıda-bırak; hatalı tekrar: Karar 7
    (n adet (n−1)'li modelin E ortalaması, kapsam da ortalama). Grubunda 3'ten az doğru varsa atlanır.
    """
    for _, grup in veri.gruplara_ayir(tekrarlar).items():
        dogrular = [t for t in grup if t.dogru]
        if len(dogrular) < 3:
            continue
        for t in grup:
            f = ozl[id(t)]["f"]
            if t.dogru:
                digerleri = [u for u in dogrular if u is not t]
                E, ek = _model_ve_hata([ozl[id(u)]["f"] for u in digerleri], f, olcut)
                yield {"t": t, "E": E[olcut], "kapsam": ek["kapsam"], "model": ek["_model"],
                       "digerleri": digerleri, "model_sayisi": 1}
            else:
                E, sonuc = adil_ortalama_hata([ozl[id(u)]["f"] for u in dogrular],
                                              lambda alt: _model_ve_hata(alt, f, olcut), [olcut])
                yield {"t": t, "E": E[olcut], "kapsam": float(np.mean([e["kapsam"] for _, e in sonuc])),
                       "model": sonuc[0][1]["_model"], "digerleri": dogrular[1:], "model_sayisi": len(dogrular)}


def skor_tablosu(tekrarlar, ozl) -> pd.DataFrame:
    satirlar = {}
    for k in OLCUTLER:
        for d in degerlendirmeler(tekrarlar, ozl, k):
            t = d["t"]
            r = satirlar.setdefault(id(t), {
                "video": t.video, "kisi": t.kisi, "kamera": t.kamera, "yonelim": t.yonelim,
                "tekrar_no": t.tekrar_no, "satir": t.satir, "gorus": t.gorus, "hata": t.hata,
                "ek_hata": t.ek_hata, "etiketli_kare": ozl[id(t)]["etiketli_kare"],
                "kisi_yok_kare": ozl[id(t)]["kisi_yok"],
                "gecerli_kare_orani": ozl[id(t)]["gecerli_kare_orani"], "tasan_sutun": ozl[id(t)]["tasan"],
                **{f"nan_{n}": c for n, c in ozl[id(t)]["neden"].items() if n}})
            r[f"bant_{k}"] = d["E"]
            r[f"kapsam_{k}"] = d["kapsam"]
    df = pd.DataFrame(list(satirlar.values()))
    for c in [c for c in df.columns if c.startswith("nan_")]:
        df[c] = df[c].fillna(0).astype(int)
    df["gorus_grubu"] = pd.Categorical(df.gorus.map(veri.gorus_grubu), categories=GORUS_GRUPLARI)
    df["ortak"] = df[[f"bant_{k}" for k in OLCUTLER]].notna().all(axis=1)
    return df


# ---------------------------------------------------------------- tablolar
def _auc(g, poz, neg, c):
    return auc(g.loc[poz, c], g.loc[neg, c])


def ozet_tablosu(df: pd.DataFrame, kisi_tablo: pd.DataFrame) -> pd.DataFrame:
    o = df[df.ortak]
    s, d, di = maskeler(o)
    satirlar = []
    for k in OLCUTLER:
        c = f"bant_{k}"
        kt = kisi_tablo[kisi_tablo["ölçüt"] == k]["AUC silkme/doğru"]
        r = {"ölçüt": k, "küme": "ortak (iki ölçütün de E'si var)",
             "silkme": int(s.sum()), "doğru": int(d.sum()), "diğer hatalar": int(di.sum()),
             "AUC silkme/doğru": _auc(o, s, d, c), "AUC silkme/diğer": _auc(o, s, di, c)}
        for gg in GORUS_GRUPLARI[:2]:
            m = o.gorus_grubu == gg
            r[f"AUC silkme/doğru {gg}"] = _auc(o, s & m, d & m, c)
        r.update({"kişi AUC ort.": kt.mean(), "kişi AUC en düşük": kt.min(), "kişi AUC en yüksek": kt.max(),
                  "kişi özeti": f"{kt.mean():.2f} ({kt.min():.2f}–{kt.max():.2f})".replace(".", ","),
                  "E boş (NaN) tekrar (bütün değerlendirilen)": int(df[c].isna().sum()),
                  "değerlendirilen tekrar": len(df)})
        satirlar.append(r)
    # Bilgi: Deney 1 v2'nin kayıtlı YENI'si (veri setinin 0.10.20 noktaları, aynı önden+çapraz tekrarlar değil
    # tam olarak: ortak küme dışı tekrarlar da dahil)
    if DENEY1_V2_OZET.exists():
        v2 = pd.read_csv(DENEY1_V2_OZET)
        v2 = v2[(v2["koşul"] == "v2") & (v2["ölçüt"] == "YENI")].iloc[0]
        satirlar.append({"ölçüt": "YENI (Deney 1 v2, kayıtlı; 0.10.20 noktaları)",
                         "küme": "Deney 1 v2'nin bütün önden+çapraz tekrarları",
                         "AUC silkme/doğru": v2["AUC silkme/doğru (önden+çapraz)"],
                         "AUC silkme/diğer": v2["AUC silkme/diğer (önden+çapraz)"],
                         f"AUC silkme/doğru {GORUS_GRUPLARI[0]}": v2[f"AUC {GORUS_GRUPLARI[0]}"],
                         f"AUC silkme/doğru {GORUS_GRUPLARI[1]}": v2[f"AUC {GORUS_GRUPLARI[1]}"]})
    return pd.DataFrame(satirlar)


def kisi_auc(df: pd.DataFrame) -> pd.DataFrame:
    satirlar = []
    for kisi, g in df[df.ortak].groupby("kisi"):
        s, d, di = maskeler(g)
        for k in OLCUTLER:
            satirlar.append({"ölçüt": k, "kisi": kisi, "AUC silkme/doğru": _auc(g, s, d, f"bant_{k}"),
                             "AUC silkme/diğer": _auc(g, s, di, f"bant_{k}"),
                             "silkme": int(s.sum()), "doğru": int(d.sum())})
    return pd.DataFrame(satirlar)


def bootstrap_tablosu(df: pd.DataFrame, n: int = BOOTSTRAP_N, tohum: int = BOOTSTRAP_TOHUM) -> pd.DataFrame:
    o = df[df.ortak].copy()

    def istatistik(b):
        s, d, di = maskeler(b)
        cikti = {}
        for ayrim, neg in (("silkme/doğru", d), ("silkme/diğer", di)):
            cikti[f"{ayrim} · SILUET − YENI_mp122"] = (_auc(b, s, neg, "bant_SILUET")
                                                        - _auc(b, s, neg, "bant_YENI_mp122"))
        return cikti

    bs = kisi_bootstrap(o, istatistik, n=n, tohum=tohum)
    nokta = istatistik(o)
    satirlar = []
    for c in bs.columns:
        alt, ust = guven_araligi(bs[c])
        satirlar.append({"fark": c, "nokta tahmini": nokta[c], "bootstrap ort.": bs[c].mean(),
                         "GA %2,5": alt, "GA %97,5": ust})
    return pd.DataFrame(satirlar)


def betimsel_tablo(df: pd.DataFrame) -> pd.DataFrame:
    """Geçerli kare oranı ve kapsam, hata türüne göre (bütün değerlendirilen tekrarlar)."""
    sut = {"tekrar": ("hata", "size"), "geçerli kare oranı ort.": ("gecerli_kare_orani", "mean"),
           "geçerli kare oranı medyan": ("gecerli_kare_orani", "median"),
           **{f"kapsam {k} ort.": (f"kapsam_{k}", "mean") for k in OLCUTLER},
           **{f"E boş {k}": (f"bant_{k}", lambda x: int(x.isna().sum())) for k in OLCUTLER},
           "kişi bulunamayan kare": ("kisi_yok_kare", "sum"), "taşan sütun": ("tasan_sutun", "sum")}
    t = df.groupby("hata").agg(**sut).reset_index()
    hepsi = df.assign(hata="HEPSİ").groupby("hata").agg(**sut).reset_index()
    return pd.concat([t, hepsi], ignore_index=True)


def nan_neden_tablosu(df: pd.DataFrame) -> pd.DataFrame:
    c = [c for c in df.columns if c.startswith("nan_")]
    toplam = df.etiketli_kare.sum() - df.kisi_yok_kare.sum()
    return pd.DataFrame([{"neden": k[4:], "kare": int(df[k].sum()), "oran (tutulan etiketli kare)": df[k].sum() / toplam}
                         for k in c])


# ---------------------------------------------------------------- kare başına sınırlar (madde 8)
def sinirlari_yaz(tekrarlar, ozl, yol: Path):
    """Kare başına 5 sütun x'i, 5 sınır y'si, arama aralığı ve SILUET (pay dahil bütün kareler)."""
    yol.parent.mkdir(parents=True, exist_ok=True)
    d = {}
    for t in tekrarlar:
        s = ozl[id(t)]["s"]
        a = f"{t.video}|{t.kamera}|satir{t.satir}"
        d[f"{a}|xler"] = s["xler"].astype(np.float32)
        d[f"{a}|sinirlar"] = s["sinirlar"].astype(np.float32)
        d[f"{a}|arama"] = s["arama"].astype(np.float32)
        d[f"{a}|SILUET"] = s["SILUET"].astype(np.float32)
        d[f"{a}|ilk_kare"] = np.array([t.ilk_kare])
    np.savez_compressed(yol, **d)


# ---------------------------------------------------------------- çalıştır
def calistir(onbellek: Path = ONBELLEK, cikti: Path = CIKTI, bootstrap_n: int = BOOTSTRAP_N, yazdir=True,
             sinirlar_yolu: Path | None = None):
    t0 = time.time()
    tekrarlar, ozl, _ = tekrarlar_ve_ozellikler(onbellek)
    if yazdir:
        print(f"  ölçütler: {len(tekrarlar)} tekrar, {time.time() - t0:.1f} s", flush=True)
    df = skor_tablosu(tekrarlar, ozl)
    kt = kisi_auc(df)
    tablolar = {"tekrarlar": df, "ozet": ozet_tablosu(df, kt),
                "kisi_auc": kt, "betimsel": betimsel_tablo(df), "nan_nedenleri": nan_neden_tablosu(df)}
    if bootstrap_n:
        tablolar["bootstrap"] = bootstrap_tablosu(df, n=bootstrap_n)
    sonuclari_yaz(tablolar, Path(cikti))
    # Kare başına sınırlar (görsel/tanı için). Yeniden üretimde (deneyler/hepsi.py) veri/ dışına yazılır.
    sinirlari_yaz(tekrarlar, ozl, Path(sinirlar_yolu) if sinirlar_yolu else Path(onbellek) / "sinirlar.npz")
    if yazdir:
        yazdir_ozet(tablolar)
        print(f"\nSüre: {time.time() - t0:.1f} s · Çıktı: {cikti}")
    return tablolar, tekrarlar, ozl


def yazdir_ozet(tablolar):
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 30)
    print("\n1) AUC (ortak küme; açı bandı, yönsüz):")
    print(tablolar["ozet"].round(3).T.to_string())
    print("\n2) Kişi bazlı AUC (ortak küme):")
    print(tablolar["kisi_auc"].round(3).to_string(index=False))
    if "bootstrap" in tablolar:
        print(f"\n3) AUC farkı, kişi bazlı bootstrap ({BOOTSTRAP_N}, tohum {BOOTSTRAP_TOHUM}), %95 GA:")
        for _, r in tablolar["bootstrap"].iterrows():
            print(f"   {r['fark']:34s} {r['nokta tahmini']:+.3f}   GA {r['GA %2,5']:+.3f} – {r['GA %97,5']:+.3f}")
    print("\n4) Betimsel (hata türüne göre):")
    print(tablolar["betimsel"].round(3).to_string(index=False))
    print("\n5) SILUET NaN nedenleri (etiketli kareler):")
    print(tablolar["nan_nedenleri"].round(4).to_string(index=False))


def sinama(onbellek: Path):
    """Kod sınaması (Güncelleme 11): önbellekte tam olan tekrarlarda ölçütler hesaplanır; AUC hesaplanmaz."""
    tekrarlar, ozl, _ = tekrarlar_ve_ozellikler(onbellek, sinama=True)
    print(f"Önbellekte tam olan tekrar: {len(tekrarlar)}")
    for t in tekrarlar:
        o = ozl[id(t)]
        s = o["tam"]["SILUET"]
        print(f"  {t.video} {t.kamera} tekrar {t.tekrar_no} ({t.hata}): {len(s)} kare, g0 {o['s']['g0']:.1f} px, "
              f"SILUET geçerli {np.isfinite(s).mean():.0%}, medyan {np.nanmedian(s):.3f} "
              f"(YENI_mp122 medyan {np.nanmedian(o['tam']['YENI_mp122']):.3f}), taşan sütun {o['tasan']}, "
              f"NaN nedenleri {o['neden']}")
    return tekrarlar, ozl


def main():
    ap = argparse.ArgumentParser(description="Adım 6b: SILUET ile YENI_mp122 karşılaştırması")
    ap.add_argument("--onbellek", default=str(ONBELLEK))
    ap.add_argument("--cikti", default=str(CIKTI))
    ap.add_argument("--bootstrap", type=int, default=BOOTSTRAP_N)
    ap.add_argument("--gorsel", action="store_true", help="3 görsel örnek video da üret")
    ap.add_argument("--sinama", action="store_true", help="kod sınaması: AUC yok")
    ap.add_argument("--sinirlar", help="kare başına sınırların yazılacağı .npz (varsayılan: <onbellek>/sinirlar.npz)")
    args = ap.parse_args()
    utf8_cikti()
    if args.sinama:
        sinama(Path(args.onbellek))
        return
    print("Adım 6b — SILUET değerlendirmesi...")
    tablolar, tekrarlar, ozl = calistir(Path(args.onbellek), Path(args.cikti), args.bootstrap,
                                       sinirlar_yolu=args.sinirlar)
    if args.gorsel:
        from araclar.siluet_gorsel import ornekler_uret
        ornekler_uret(tablolar["tekrarlar"], tekrarlar, ozl, Path(args.cikti) / "gorsel")


if __name__ == "__main__":
    main()
