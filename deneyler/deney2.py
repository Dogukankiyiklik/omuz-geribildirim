"""
Deney 2 — hata türünü bulma.

Soru: Sistem bir tekrarın doğru olup olmadığını, yanlışsa HANGİ hatayı içerdiğini bulabiliyor mu?

1) Tekrar puanları (her tekrar, her ölçüt; yönsüz ve iki yönlü E, ortalama imzalı fark):
   v2  : açı bandı (ana yöntem)
   v1b : zaman bandı, çoklu referans (yalnızca karşılaştırma temel çizgisi)
   Kaldırma: iki sürüm de hesaplanır; karar kuralı --kaldirma-surumu ile seçer.
     ilk    (varsayılan): d = (tepe medyanı − tepe) / max(IQR, 5°) → sonuclar/deney2/
     revize (başarısız deneme): tek kutulu tepe bandı, E 0–1 → sonuclar/deney2_revize/
   Adillik: doğru tekrar birini-dışarıda-bırak; hatalı tekrar tüm (n−1)'li modellerin ortalaması.
   Bir gruptaki n alt küme modeli bir kez kurulur: doğru tekrar i, i'nci alt kümeyle (kendisi dışarıda)
   değerlendirilir; bu, Deney 1 v2'deki birini-dışarıda-bırak ile aynı modeldir.
2) Karar kuralı (cekirdek/hata_turu.py), kişi bazlı birini-dışarıda-bırak: 4 kişide ölçekleme, yön,
   öne kaçma ölçütü ve T seçilir; 5. kişide test edilir. Ayar yalnızca eğitim kişilerinin
   önden + çapraz (|görüş| ≤ 60°) tekrarlarıyla yapılır (uygulama senaryosu).
3) Temel çizgi: tek toplam hata (z'lerin ortalaması) ile yalnızca doğru/yanlış.
4) "İlk iki": birincil hata en yüksek iki z içinde mi; ikinci z de T'yi geçiyor mu.

Kullanım:
    python -m deneyler.deney2                 # ~5–10 dk (puanlar), sonra karar kuralı ve tablolar
    python -m deneyler.deney2 --puan-hazir    # puanlar sonuclar/deney2/puanlar.csv'den okunur
    python -m deneyler.deney2 --galeri        # ayrıca galeri (sonuclar/deney2/galeri/)
    python -m deneyler.deney2 --kaldirma-surumu revize   # denenip elenen sürüm → sonuclar/deney2_revize/
Çıktı: sonuclar/deney2/ (ilk) ya da sonuclar/deney2_revize/ (revize)
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from cekirdek import veri
from cekirdek import hata_turu as ht
from cekirdek import degerlendirici
from cekirdek.aci_bandi import aci_bandi_modeli, aci_bandi_puanlari, tepe_acisi
from cekirdek.adil_model import birini_disarida_alt_kumeler
from cekirdek.bant import coklu_model_puanlari, coklu_referans_modelleri
from cekirdek.degerlendirme import guven_araligi, karisiklik, kisi_bootstrap, makro_f1, sinif_metrikleri
from cekirdek.konsol import sonuclari_yaz, utf8_cikti
from cekirdek.ozellikler import DENEY2_OLCUTLERI, ozellikler
from deneyler.deney1 import GORUS_GRUPLARI
from deneyler.tablolar import ONDEN_CAPRAZ, TUMU, gorus_maskesi

OLCUTLER = DENEY2_OLCUTLERI
YONLER = (0, 1, -1)
BANTLAR = ("v2", "v1b")
SISTEMLER = [(b, y) for b in BANTLAR for y in (True, False)]   # (bant, yönlü)
ANA_SISTEM = ("v2", True)   # galeri ve "basit anlatım" için; sonuçlar görülmeden seçildi
AYAR_GORUSU = ONDEN_CAPRAZ
GORUSLER = (ONDEN_CAPRAZ, TUMU)
CIKTI = veri.KOK / "sonuclar" / "deney2"
CIKTILAR = {"ilk": CIKTI, "revize": veri.KOK / "sonuclar" / "deney2_revize"}


def sistem_adi(bant: str, yonlu: bool) -> str:
    return f"{bant}_{'yonlu' if yonlu else 'yonsuz'}"


# ---------------------------------------------------------------- 1) tekrar puanları
def _kes(f: dict, s: slice) -> dict:
    return {k: v[s] for k, v in f.items()}


def _ortalama(sozlukler: list[dict]) -> dict:
    """Anahtar başına NaN'ları atlayan ortalama (açı bandında geçerli karesi olmayan model atlanır)."""
    cikti = {}
    for a in sozlukler[0]:
        v = np.array([s[a] for s in sozlukler], dtype=float)
        cikti[a] = float(np.nanmean(v)) if np.any(~np.isnan(v)) else np.nan
    return cikti


def grup_modelleri(dogrular_f: list[dict], bant: str, olcutler=OLCUTLER) -> list:
    """Bir grubun n alt küme modeli (i. model: i. doğru tekrar dışarıda)."""
    alt = birini_disarida_alt_kumeler(dogrular_f)
    if bant == "v2":
        return [aci_bandi_modeli(a, olcutler) for a in alt]
    return [coklu_referans_modelleri(a, olcutler) for a in alt]


def _model_puani(model, alt_f, f, bant, olcutler=OLCUTLER, kaldirma=True):
    """Tek bir (n−1)'li modelle puanlar: (E, fark, ek). kaldirma=False: az kaldırma puanı hesaplanmaz."""
    if bant == "v2":   # uygulamayla ortak kod (cekirdek/degerlendirici.py)
        return degerlendirici.tekrar_puanlari(model, alt_f, f, olcutler, kaldirma)
    E, fark = coklu_model_puanlari(model, f, olcutler, YONLER)
    if kaldirma:
        degerlendirici.kaldirma_ekle(E, fark, f, alt_f, YONLER)
    return E, fark, {}


def puan_tablosu(tekrarlar, bant: str, ozl=None, yazdir=True, olcutler=OLCUTLER, kaldirma=True) -> pd.DataFrame:
    """Tekrar başına puanlar (olcutler=DENEY2_OLCUTLERI, kaldirma=True)."""
    olcutler = list(olcutler)
    ozl = ozl or {id(t): ozellikler(t.dizi, olcutler) for t in tekrarlar}
    kayit = []
    for _, grup in veri.gruplara_ayir(tekrarlar).items():
        tl = [(t, _kes(ozl[id(t)], t.etiketli)) for t in grup]
        dogrular = [(t, f) for t, f in tl if t.dogru]
        if len(dogrular) < 3:
            continue
        dogrular_f = [f for _, f in dogrular]
        modeller = grup_modelleri(dogrular_f, bant, olcutler)
        altlar = birini_disarida_alt_kumeler(dogrular_f)
        for t, f in tl:
            if t.dogru:
                i = next(j for j, (u, _) in enumerate(dogrular) if u is t)
                secim = [i]
            else:
                secim = range(len(dogrular))
            sonuc = [_model_puani(modeller[i], altlar[i], f, bant, olcutler, kaldirma) for i in secim]
            E = _ortalama([s[0] for s in sonuc])
            fark = _ortalama([s[1] for s in sonuc])
            r = {"bant": bant, "video": t.video, "kisi": t.kisi, "kamera": t.kamera, "yonelim": t.yonelim,
                 "tekrar_no": t.tekrar_no, "satir": t.satir, "gorus": t.gorus, "hata": t.hata,
                 "ek_hata": t.ek_hata, "model_sayisi": len(sonuc), "tepe_acisi": tepe_acisi(f["kol"])}
            r.update({ht.puan_sutunu(k, y): E[(k, y)] for k in olcutler + ([ht.KALDIRMA] if kaldirma else [])
                      for y in YONLER})
            r.update({ht.fark_sutunu(k): v for k, v in fark.items()})
            if bant == "v2":
                r["kapsam"] = float(np.mean([s[2]["kapsam"] for s in sonuc]))
                # modellerin yarısından fazlasında bayrak
                r["aralik_disi"] = bool(np.mean([s[2]["aralik_disi"] for s in sonuc]) > 0.5)
            kayit.append(r)
    df = pd.DataFrame(kayit)
    df["gorus_grubu"] = df.gorus.map(veri.gorus_grubu)
    return df


# ---------------------------------------------------------------- 2) birini-dışarıda-bırak karar
def loso(puan: pd.DataFrame, yonlu: bool, tanim: ht.HataTanimi = ht.EX1, ayar_gorusu: str = AYAR_GORUSU,
         kaldirma_surumu: str = ht.VARSAYILAN_KALDIRMA):
    """Kişi bazlı birini-dışarıda-bırak. Ayar yalnızca eğitim kişilerinin ayar_gorusu tekrarlarıyla.
    Dönüş: (tahmin tablosu, kural kaydı)."""
    parcalar, kurallar = [], []
    for kisi in sorted(puan.kisi.unique()):
        egitim = puan[(puan.kisi != kisi) & gorus_maskesi(puan, ayar_gorusu)]
        test = puan[puan.kisi == kisi]
        kural = ht.esik_sec(egitim, yonlu, tanim, kaldirma_surumu)
        z = kural.z(test)
        tah = kural.karar(test, z)
        # temel çizgi: aynı ölçekleme, tek toplam hata, yalnızca doğru/yanlış
        z_eg = kural.z(egitim)
        Tb = ht.ikili_esik_sec(ht.toplam_hata(z_eg), egitim.hata != ht.DOGRU)
        toplam = ht.toplam_hata(z)
        p = test[["video", "kisi", "kamera", "yonelim", "tekrar_no", "satir", "gorus", "gorus_grubu",
                  "hata", "ek_hata"]].copy()
        p["tahmin"] = tah
        p["esnek_gercek"] = ht.esnek_gercek(test.hata, test.ek_hata, tah)
        p["max_z"] = z.max(axis=1)
        p["T"] = kural.T
        p = p.join(ht.ilk_iki(z, kural.T))
        for h in kural.hatalar:
            p[f"z_{ht.KISA_AD[h]}"] = z[h]
        p["toplam_hata"] = toplam
        p["temel_tahmin_yanlis"] = toplam >= Tb
        parcalar.append(p)
        kurallar.append({"test kişisi": kisi, "kaldırma sürümü": kural.kaldirma_surumu, "T": kural.T,
                         "öne kaçma ölçütü": kural.on_olcut,
                         "eğitim makro-F1": kural.bilgi["egitim_makro_f1"], "temel çizgi T": Tb,
                         **{f"yön {k}": kural.yonler[k] for k in kural.yonler},
                         **{f"medyan {k}": kural.medyan[k] for k in kural.medyan},
                         **{f"ölçek {k}": kural.olcek[k] for k in kural.olcek}})
    return pd.concat(parcalar), pd.DataFrame(kurallar)


# ---------------------------------------------------------------- 3) tablolar
def _ikili(gercek_yanlis, tahmin_yanlis) -> dict:
    g, t = np.asarray(gercek_yanlis, bool), np.asarray(tahmin_yanlis, bool)
    duy, ozg = t[g].mean(), (~t[~g]).mean()
    return {"ikili doğruluk": float((g == t).mean()), "duyarlılık (hatalıyı yakalama)": float(duy),
            "özgüllük (doğruya doğru deme)": float(ozg), "dengeli doğruluk": float((duy + ozg) / 2)}


def ozet_satiri(p: pd.DataFrame, siniflar=ht.SINIFLAR) -> dict:
    """Bir tahmin tablosu dilimi için ana sayılar (katı ve esnek)."""
    hatali = p.hata != ht.DOGRU
    r = {"tekrar": len(p), "hatalı tekrar": int(hatali.sum())}
    r["makro-F1 (katı)"] = makro_f1(p.hata, p.tahmin, siniflar)
    r["makro-F1 (esnek)"] = makro_f1(p.esnek_gercek, p.tahmin, siniflar)
    r["doğruluk 6 sınıf (katı)"] = float((p.hata == p.tahmin).mean())
    r["doğruluk 6 sınıf (esnek)"] = float((p.esnek_gercek == p.tahmin).mean())
    r.update(_ikili(hatali, p.tahmin != ht.DOGRU))
    # "100 hatalı tekrarın kaçında hatanın türünü doğru söyledi?"
    r["hatalılarda tür doğru /100 (katı)"] = 100 * float((p.tahmin[hatali] == p.hata[hatali]).mean())
    r["hatalılarda tür doğru /100 (esnek)"] = 100 * float((p.tahmin[hatali] == p.esnek_gercek[hatali]).mean())
    r["hatalılarda 'doğru' dedi /100"] = 100 * float((p.tahmin[hatali] == ht.DOGRU).mean())
    yakalanan = hatali & (p.tahmin != ht.DOGRU)
    r["yakalanan hatalılarda tür doğru (%, katı)"] = 100 * float((p.tahmin[yakalanan] == p.hata[yakalanan]).mean())
    return r


def ilk_iki_satiri(p: pd.DataFrame) -> dict:
    """Hatalı tekrarlarda birincil hata en yüksek iki z içinde mi; ikinci z de T'yi geçiyor mu."""
    h = p[p.hata != ht.DOGRU]
    d = p[p.hata == ht.DOGRU]
    ilk2 = (h.z1_hata == h.hata) | (h.z2_hata == h.hata)
    soylenen = (h.soylenen1 == h.hata) | (h.soylenen2 == h.hata)
    yakalanan = h.soylenen1 != ht.DOGRU
    return {"tekrar": len(p), "hatalı tekrar": len(h),
            "hatalılarda birincil 1. z /100": 100 * float((h.z1_hata == h.hata).mean()),
            "hatalılarda birincil ilk iki z içinde /100": 100 * float(ilk2.mean()),
            "hatalılarda birincil söylenen ilk iki içinde /100": 100 * float(soylenen.mean()),
            "hatalılarda 2. z ≥ T /100": 100 * float((h.soylenen2 != "").mean()),
            "yakalanan hatalılarda 2. z ≥ T (%)": 100 * float((h.soylenen2 != "")[yakalanan].mean()),
            "hatalılarda söylenen 2. hata = birincil /100": 100 * float((h.soylenen2 == h.hata).mean()),
            "doğrularda 2. z ≥ T /100": 100 * float((d.soylenen2 != "").mean())}


def temel_satiri(p: pd.DataFrame) -> dict:
    hatali = p.hata != ht.DOGRU
    r = {"tekrar": len(p), "hatalı tekrar": int(hatali.sum())}
    r.update(_ikili(hatali, p.temel_tahmin_yanlis))
    return r


def tablolar_uret(tahminler: dict, kurallar: dict, puanlar: dict, bootstrap_n=2000) -> dict:
    T = {}
    ozet, temel, sinif, gorus_grup, kisi, kar, ilk2 = [], [], [], [], [], {}, []
    for (bant, yonlu), p in tahminler.items():
        ad = sistem_adi(bant, yonlu)
        for gorus in GORUSLER + ("profil (70–90°)",):
            g = p[gorus_maskesi(p, gorus)]
            ozet.append({"sistem": ad, "görüş": gorus, **ozet_satiri(g)})
            ilk2.append({"sistem": ad, "görüş": gorus, **ilk_iki_satiri(g)})
            temel.append({"sistem": ad, "görüş": gorus, "yöntem": "temel çizgi: tek toplam hata (doğru/yanlış)",
                          **temel_satiri(g)})
            o = ozet_satiri(g)
            temel.append({"sistem": ad, "görüş": gorus, "yöntem": "6 sınıflı karar kuralı",
                          **{k: o[k] for k in ("tekrar", "hatalı tekrar", "ikili doğruluk",
                                               "duyarlılık (hatalıyı yakalama)", "özgüllük (doğruya doğru deme)",
                                               "dengeli doğruluk", "hatalılarda tür doğru /100 (katı)",
                                               "makro-F1 (katı)")}})
        for gorus in GORUSLER:
            g = p[gorus_maskesi(p, gorus)]
            for degerlendirme, gercek in (("katı", g.hata), ("esnek", g.esnek_gercek)):
                s = sinif_metrikleri(gercek, g.tahmin, ht.SINIFLAR)
                s.insert(0, "değerlendirme", degerlendirme)
                s.insert(0, "görüş", gorus)
                s.insert(0, "sistem", ad)
                sinif.append(s)
                m = karisiklik(gercek, g.tahmin, ht.SINIFLAR)
                kar[(ad, gorus, degerlendirme)] = m
        for gg in GORUS_GRUPLARI:
            g = p[p.gorus_grubu == gg]
            gorus_grup.append({"sistem": ad, "görüş grubu": gg, "tekrar": len(g),
                               "makro-F1 (katı)": makro_f1(g.hata, g.tahmin, ht.SINIFLAR),
                               "makro-F1 (esnek)": makro_f1(g.esnek_gercek, g.tahmin, ht.SINIFLAR),
                               "hatalılarda tür doğru /100 (katı)":
                                   100 * float((g.tahmin == g.hata)[g.hata != ht.DOGRU].mean())})
        for gorus in GORUSLER:
            for k, g in p[gorus_maskesi(p, gorus)].groupby("kisi"):
                kisi.append({"sistem": ad, "görüş": gorus, "kisi": k,
                             "makro-F1 (katı)": makro_f1(g.hata, g.tahmin, ht.SINIFLAR),
                             "hatalılarda tür doğru /100 (katı)":
                                 100 * float((g.tahmin == g.hata)[g.hata != ht.DOGRU].mean()),
                             "hatalılarda 'doğru' dedi /100":
                                 100 * float((g.tahmin == ht.DOGRU)[g.hata != ht.DOGRU].mean()),
                             "hatalılarda birincil ilk iki z içinde /100":
                                 ilk_iki_satiri(g)["hatalılarda birincil ilk iki z içinde /100"]})
    T["ozet"] = pd.DataFrame(ozet)
    T["temel_cizgi"] = pd.DataFrame(temel)
    T["ilk_iki"] = pd.DataFrame(ilk2)
    T["kaldirma"] = kaldirma_tablosu(tahminler, puanlar)
    T["siniflar"] = pd.concat(sinif, ignore_index=True)
    T["gorus_grubu"] = pd.DataFrame(gorus_grup)
    T["kisi"] = pd.DataFrame(kisi)
    T["esikler"] = pd.concat([k.assign(sistem=sistem_adi(*s)) for s, k in kurallar.items()], ignore_index=True)
    for (ad, gorus, d), m in kar.items():
        if (ad == sistem_adi(*ANA_SISTEM)) or d == "katı":
            ad_ = f"karisiklik_{ad}_{'oc' if gorus == ONDEN_CAPRAZ else 'tum'}_{'kati' if d == 'katı' else 'esnek'}"
            mm = m.copy()
            mm.index = [f"gerçek: {ht.KISA_AD[c]}" for c in mm.index]
            mm.columns = [f"tahmin: {ht.KISA_AD[c]}" for c in mm.columns]
            T[ad_] = mm.reset_index().rename(columns={"index": ""})
    T["aralik_disi"] = aralik_disi_tablosu(puanlar["v2"])
    if bootstrap_n:
        T["bootstrap"] = bootstrap_tablosu(tahminler, bootstrap_n)
    T["_kar"] = kar
    return T


def kaldirma_tablosu(tahminler: dict, puanlar: dict) -> pd.DataFrame:
    """
    "Az kaldırma" kararlarının dökümü (inceleme tablosunun revize karşılığı): kolun kişinin
    normalinden ne kadar az kalktığı, eksik = μ − tepe (derece; hatalıda adil modellerin ortalaması).
    """
    anahtar = ["video", "kamera", "yonelim", "satir"]
    sut = ht.fark_sutunu(ht.KALDIRMA)

    def satir(ad, gorus, grup, e):
        bos = len(e) == 0
        return {"sistem": ad, "görüş": gorus, "grup": grup, "tekrar": len(e),
                "eksik medyan (°)": np.nan if bos else float(e.median()),
                "eksik Ç1 (°)": np.nan if bos else float(e.quantile(0.25)),
                "eksik Ç3 (°)": np.nan if bos else float(e.quantile(0.75)),
                "eksik en az (°)": np.nan if bos else float(e.min()),
                "eksik < 20° olan": int((e < 20).sum())}

    satirlar = []
    for (bant, yonlu), p in tahminler.items():
        ad = sistem_adi(bant, yonlu)
        q = p.merge(puanlar[bant][anahtar + [sut]], on=anahtar)
        for gorus in GORUSLER:
            g = q[gorus_maskesi(q, gorus)]
            k = g[g.tahmin == "ERR_LOW_ABDUCTION"]
            satirlar.append(satir(ad, gorus, "doğru 'az kaldırma' kararı", k[k.hata == "ERR_LOW_ABDUCTION"][sut]))
            satirlar.append(satir(ad, gorus, "yanlış 'az kaldırma' kararı", k[k.hata != "ERR_LOW_ABDUCTION"][sut]))
            for h in ht.SINIFLAR:
                satirlar.append(satir(ad, gorus, f"gerçek sınıf: {ht.KISA_AD[h]}", g[g.hata == h][sut]))
    return pd.DataFrame(satirlar)


def aralik_disi_tablosu(p: pd.DataFrame) -> pd.DataFrame:
    """Açı bandının kapsamı ve 'kol normalden yüksek' bayrağı, gerçek sınıfa göre (betimsel)."""
    satirlar = []
    for gorus in GORUSLER:
        g = p[gorus_maskesi(p, gorus)]
        for h in ht.SINIFLAR:
            x = g[g.hata == h]
            satirlar.append({"görüş": gorus, "gerçek sınıf": ht.KISA_AD[h], "tekrar": len(x),
                             "aralik_disi oranı": float(x.aralik_disi.mean()),
                             "kapsam ort.": float(x.kapsam.mean()),
                             "E boş (YENI)": int(x[ht.puan_sutunu("YENI", 0)].isna().sum())})
    return pd.DataFrame(satirlar)


def bootstrap_tablosu(tahminler: dict, n=2000, tohum=1) -> pd.DataFrame:
    """Kişi bazlı bootstrap: makro-F1 (katı) ve 'hatalılarda tür doğru' için %95 GA; sistem farkları."""
    anahtar = ["video", "kamera", "yonelim", "satir"]
    taban = None
    for s, p in tahminler.items():
        q = p.set_index(anahtar)[["kisi", "gorus", "hata", "ek_hata", "tahmin"]].rename(
            columns={"tahmin": sistem_adi(*s)})
        taban = q if taban is None else taban.join(q[[sistem_adi(*s)]])
    taban = taban.reset_index()
    adlar = [sistem_adi(*s) for s in tahminler]
    farklar = [("v2_yonlu", "v1b_yonlu"), ("v2_yonsuz", "v1b_yonsuz"), ("v2_yonlu", "v2_yonsuz"),
               ("v1b_yonlu", "v1b_yonsuz")]

    def istatistik(b):
        c = {}
        for gorus in GORUSLER:
            g = b[gorus_maskesi(b, gorus)]
            h = g.hata != ht.DOGRU
            f1 = {a: makro_f1(g.hata, g[a], ht.SINIFLAR) for a in adlar}
            for a in adlar:
                c[f"{gorus}|makro-F1|{a}"] = f1[a]
                c[f"{gorus}|tür doğru/100|{a}"] = 100 * float((g[a][h] == g.hata[h]).mean())
            for x, y in farklar:
                c[f"{gorus}|makro-F1 farkı|{x} − {y}"] = f1[x] - f1[y]
        return c

    nokta = istatistik(taban)
    bs = kisi_bootstrap(taban, istatistik, n=n, tohum=tohum)
    satirlar = []
    for c in bs.columns:
        alt, ust = guven_araligi(bs[c])
        gorus, olcu, ad = c.split("|")
        satirlar.append({"görüş": gorus, "büyüklük": olcu, "sistem / fark": ad, "nokta tahmini": nokta[c],
                         "GA %2,5": alt, "GA %97,5": ust,
                         "GA sıfırı içeriyor": bool(alt <= 0 <= ust) if "farkı" in olcu else ""})
    return pd.DataFrame(satirlar)


ILK_SURUM = veri.KOK / "sonuclar" / "deney2_ilk" / "tahminler.csv"


def ilk_surumle_karsilastir(tahminler: dict, yol: Path = ILK_SURUM, n=2000, tohum=1) -> pd.DataFrame | None:
    """
    revize − ilk sürüm, aynı tekrarlarda; kişi bazlı bootstrap %95 GA.
    İlk sürümün tahminleri sonuclar/deney2_ilk/tahminler.csv dosyasından okunur (yoksa None).
    """
    if not Path(yol).exists():
        return None
    ilk = pd.read_csv(yol, encoding="utf-8-sig", keep_default_na=False)
    anahtar = ["video", "kamera", "yonelim", "satir"]
    taban = None
    adlar = []
    for s, p in tahminler.items():
        ad = sistem_adi(*s)
        q = p.set_index(anahtar)[["kisi", "gorus", "hata", "tahmin"]].rename(columns={"tahmin": f"{ad}|revize"})
        e = ilk[ilk.sistem == ad].set_index(anahtar)[["tahmin"]].rename(columns={"tahmin": f"{ad}|ilk"})
        q = q.join(e, how="inner")
        taban = q if taban is None else taban.join(q[[f"{ad}|revize", f"{ad}|ilk"]], how="inner")
        adlar.append(ad)
    taban = taban.reset_index()

    def olculer(g, c):
        h = g.hata != ht.DOGRU
        return {"makro-F1 (katı)": makro_f1(g.hata, g[c], ht.SINIFLAR),
                "hatalılarda tür doğru /100": 100 * float((g[c][h] == g.hata[h]).mean()),
                "hatalılarda 'doğru' dedi /100": 100 * float((g[c][h] == ht.DOGRU).mean()),
                "doğrularda 'doğru' dedi /100": 100 * float((g[c][~h] == ht.DOGRU).mean()),
                "'az kaldırma' kararı kesinliği":
                    float((g.hata[g[c] == "ERR_LOW_ABDUCTION"] == "ERR_LOW_ABDUCTION").mean())}

    def istatistik(b):
        c = {}
        for gorus in GORUSLER:
            g = b[gorus_maskesi(b, gorus)]
            for ad in adlar:
                r, i = olculer(g, f"{ad}|revize"), olculer(g, f"{ad}|ilk")
                for k in r:
                    c[f"{gorus}|{ad}|{k}|ilk"] = i[k]
                    c[f"{gorus}|{ad}|{k}|revize"] = r[k]
                    c[f"{gorus}|{ad}|{k}|fark"] = r[k] - i[k]
        return c

    nokta = istatistik(taban)
    bs = kisi_bootstrap(taban, istatistik, n=n, tohum=tohum) if n else None
    satirlar = {}
    for c, v in nokta.items():
        gorus, ad, olcu, tur = c.split("|")
        r = satirlar.setdefault((gorus, ad, olcu), {"görüş": gorus, "sistem": ad, "büyüklük": olcu,
                                                    "tekrar": int(gorus_maskesi(taban, gorus).sum())})
        r[tur] = v
        if tur == "fark" and bs is not None:
            alt, ust = guven_araligi(bs[c])
            r.update({"fark GA %2,5": alt, "fark GA %97,5": ust, "GA sıfırı içeriyor": bool(alt <= 0 <= ust)})
    return pd.DataFrame(list(satirlar.values()))


def karisiklik_sekli(m: pd.DataFrame, baslik: str, yol: Path):
    """Satır normalize (gerçek sınıfın yüzdesi) renk, hücrede sayı."""
    a = m.to_numpy(float)
    oran = a / np.maximum(a.sum(1, keepdims=True), 1)
    fig, ax = plt.subplots(figsize=(7.2, 6.0), dpi=130)
    ax.imshow(oran, cmap="Blues", vmin=0, vmax=1)
    etiket = [ht.KISA_AD[c] for c in m.index]
    ax.set_xticks(range(len(etiket)), etiket, rotation=30, ha="right")
    ax.set_yticks(range(len(etiket)), etiket)
    for i in range(a.shape[0]):
        for j in range(a.shape[1]):
            ax.text(j, i, f"{int(a[i, j])}\n{oran[i, j]:.0%}", ha="center", va="center", fontsize=8,
                    color="white" if oran[i, j] > 0.55 else "#0b0b0b")
    ax.set_xlabel("sistemin kararı")
    ax.set_ylabel("gerçek etiket")
    ax.set_title(baslik, loc="left", fontsize=10)
    fig.tight_layout()
    fig.savefig(yol)
    plt.close(fig)


# ---------------------------------------------------------------- çalıştır
def puanlari_hesapla(cikti: Path, yazdir=True) -> dict[str, pd.DataFrame]:
    tekrarlar = veri.tekrarlari_yukle(1)
    ozl = {id(t): ozellikler(t.dizi, OLCUTLER) for t in tekrarlar}
    puanlar = {}
    for bant in BANTLAR:
        t0 = time.time()
        puanlar[bant] = puan_tablosu(tekrarlar, bant, ozl)
        if yazdir:
            print(f"  puanlar {bant}: {len(puanlar[bant])} tekrar, {time.time() - t0:.1f} s")
    pd.concat(puanlar.values(), ignore_index=True).to_csv(cikti / "puanlar.csv", index=False, encoding="utf-8-sig")
    return puanlar


def puanlari_oku(cikti: Path) -> dict[str, pd.DataFrame]:
    df = pd.read_csv(cikti / "puanlar.csv", encoding="utf-8-sig", keep_default_na=False,
                     na_values=["", "nan", "NaN"])
    df["ek_hata"] = df.ek_hata.astype(str).replace("nan", "")
    return {b: g.reset_index(drop=True) for b, g in df.groupby("bant")}


def calistir(cikti=None, puan_hazir=False, bootstrap_n=2000, yazdir=True,
             kaldirma_surumu: str = ht.VARSAYILAN_KALDIRMA):
    t0 = time.time()
    cikti = Path(cikti) if cikti else CIKTILAR[kaldirma_surumu]
    cikti.mkdir(parents=True, exist_ok=True)
    puanlar = puanlari_oku(cikti) if puan_hazir else puanlari_hesapla(cikti, yazdir)
    tahminler, kurallar = {}, {}
    for bant, yonlu in SISTEMLER:
        tahminler[(bant, yonlu)], kurallar[(bant, yonlu)] = loso(puanlar[bant], yonlu,
                                                                 kaldirma_surumu=kaldirma_surumu)
    T = tablolar_uret(tahminler, kurallar, puanlar, bootstrap_n)
    kar = T.pop("_kar")
    T["tahminler"] = pd.concat([p.assign(sistem=sistem_adi(*s)) for s, p in tahminler.items()], ignore_index=True)
    ilk = ilk_surumle_karsilastir(tahminler, n=bootstrap_n) if kaldirma_surumu == "revize" else None
    if ilk is not None:
        T["ilk_surum_karsilastirma"] = ilk
    sonuclari_yaz(T, cikti)
    for gorus, ek in ((ONDEN_CAPRAZ, "oc"), (TUMU, "tum")):
        for s in SISTEMLER:
            ad = sistem_adi(*s)
            karisiklik_sekli(kar[(ad, gorus, "katı")],
                             f"Deney 2 · {ad} · {gorus} · katı (birincil hata) · kaldırma: {kaldirma_surumu}",
                             cikti / f"karisiklik_{ad}_{ek}.png")
    if yazdir:
        yazdir_ozet(T)
        print(f"\nSüre: {time.time() - t0:.1f} s · Çıktı: {cikti}")
    return T, tahminler, puanlar, kurallar


def yazdir_ozet(T):
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 40)
    o = T["ozet"]
    print("\n1) Özet (katı = yalnızca birincil hata; esnek = ek hatalardan birini söylemek de doğru):")
    sut = ["sistem", "görüş", "tekrar", "makro-F1 (katı)", "makro-F1 (esnek)", "doğruluk 6 sınıf (katı)",
           "dengeli doğruluk", "hatalılarda tür doğru /100 (katı)", "hatalılarda tür doğru /100 (esnek)",
           "hatalılarda 'doğru' dedi /100"]
    print(o[sut].round(3).to_string(index=False))
    print("\n2) Temel çizgi (tek toplam hata, doğru/yanlış) ve 6 sınıflı kural:")
    t = T["temel_cizgi"]
    print(t[t["görüş"] != "profil (70–90°)"].round(3).to_string(index=False))
    print("\n2b) İlk iki:")
    print(T["ilk_iki"].round(2).to_string(index=False))
    print("\n2c) Az kaldırma kararları ve eksik açı (ana sistem):")
    kd = T["kaldirma"]
    print(kd[kd.sistem == sistem_adi(*ANA_SISTEM)].round(1).to_string(index=False))
    print("\n3) Sınıf başına (ana sistem, önden+çapraz, katı):")
    s = T["siniflar"]
    print(s[(s.sistem == sistem_adi(*ANA_SISTEM)) & (s["görüş"] == ONDEN_CAPRAZ) & (s["değerlendirme"] == "katı")]
          .round(3).to_string(index=False))
    print("\n4) Karışıklık (ana sistem, önden+çapraz, katı):")
    print(T[f"karisiklik_{sistem_adi(*ANA_SISTEM)}_oc_kati"].to_string(index=False))
    print("\n5) Görüş grubuna göre:")
    print(T["gorus_grubu"].round(3).to_string(index=False))
    print("\n6) Seçilen eşikler (her satır bir test kişisi; ayar diğer 4 kişide):")
    e = T["esikler"]
    print(e[["sistem", "test kişisi", "T", "öne kaçma ölçütü", "eğitim makro-F1", "temel çizgi T"]
            + [c for c in e.columns if c.startswith("yön ")]].round(3).to_string(index=False))
    print("\n7) Kişi bazlı (katı):")
    k = T["kisi"]
    print(k.pivot_table(index=["sistem", "görüş"], columns="kisi", values="makro-F1 (katı)", sort=False)
          .round(3).to_string())
    if "bootstrap" in T:
        print("\n8) Kişi bazlı bootstrap %95 GA:")
        print(T["bootstrap"].round(3).to_string(index=False))
    if "ilk_surum_karsilastirma" in T:
        print("\n9) Revize − ilk sürüm (kişi bazlı bootstrap %95 GA):")
        print(T["ilk_surum_karsilastirma"].round(3).to_string(index=False))


def main():
    ap = argparse.ArgumentParser(description="Deney 2: hata türünü bulma")
    ap.add_argument("--cikti", default=None, help="varsayılan: sonuclar/deney2 (ilk) ya da deney2_revize")
    ap.add_argument("--kaldirma-surumu", choices=ht.KALDIRMA_SURUMLERI, default=ht.VARSAYILAN_KALDIRMA,
                    help="az kaldırma puanı: ilk (varsayılan) ya da revize (denenip elenen sürüm)")
    ap.add_argument("--puan-hazir", action="store_true", help="puanlar.csv'yi yeniden hesaplama")
    ap.add_argument("--bootstrap", type=int, default=2000)
    ap.add_argument("--galeri", action="store_true", help="galeri videolarını da üret")
    ap.add_argument("--adet", type=int, default=3)
    args = ap.parse_args()
    utf8_cikti()
    print(f"Deney 2 — hata türünü bulma (kaldırma sürümü: {args.kaldirma_surumu})")
    T, tahminler, puanlar, kurallar = calistir(args.cikti, args.puan_hazir, args.bootstrap,
                                               kaldirma_surumu=args.kaldirma_surumu)
    cikti = Path(args.cikti) if args.cikti else CIKTILAR[args.kaldirma_surumu]
    if args.galeri:
        from deneyler import deney2_galeri
        print("\nGaleri üretiliyor...")
        deney2_galeri.galeri(tahminler[ANA_SISTEM], kurallar[ANA_SISTEM], cikti / "galeri", n=args.adet)


if __name__ == "__main__":
    main()
