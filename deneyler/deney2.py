"""
Deney 2 — hata türünü bulma (Adım 4, PLAN.md + Güncelleme 02, 03, 04).

Soru: Sistem bir tekrarın doğru olup olmadığını, yanlışsa HANGİ hatayı içerdiğini bulabiliyor mu?

1) Tekrar puanları (her tekrar, her ölçüt; yönsüz ve iki yönlü E, ortalama imzalı fark):
   v2  : açı bandı (ana yöntem, Karar 6)
   v1b : zaman bandı, çoklu referans (yalnızca karşılaştırma temel çizgisi, Karar 6)
   Kaldırma: tepe kol açısı sapması (bant yok).
   Adillik: doğru tekrar birini-dışarıda-bırak; hatalı tekrar tüm (n−1)'li modellerin ortalaması (Karar 7).
   Bir gruptaki n alt küme modeli bir kez kurulur: doğru tekrar i, i'nci alt kümeyle (kendisi dışarıda)
   değerlendirilir; bu, Deney 1 v2'deki birini-dışarıda-bırak ile aynı modeldir.
2) Karar kuralı (cekirdek/hata_turu.py), kişi bazlı birini-dışarıda-bırak: 4 kişide ölçekleme, yön,
   öne kaçma ölçütü ve T seçilir; 5. kişide test edilir. Ayar yalnızca eğitim kişilerinin
   önden + çapraz (|görüş| ≤ 60°) tekrarlarıyla yapılır (uygulama senaryosu).
3) Temel çizgi: tek toplam hata (z'lerin ortalaması) ile yalnızca doğru/yanlış.

Kullanım:
    python -m deneyler.deney2                 # ~5–10 dk (puanlar), sonra karar kuralı ve tablolar
    python -m deneyler.deney2 --puan-hazir    # puanlar sonuclar/deney2/puanlar.csv'den okunur
    python -m deneyler.deney2 --galeri        # ayrıca galeri (sonuclar/deney2/galeri/)
Çıktı: sonuclar/deney2/
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


def grup_modelleri(dogrular_f: list[dict], bant: str) -> list:
    """Bir grubun n alt küme modeli (i. model: i. doğru tekrar dışarıda)."""
    alt = birini_disarida_alt_kumeler(dogrular_f)
    if bant == "v2":
        return [aci_bandi_modeli(a, OLCUTLER) for a in alt]
    return [coklu_referans_modelleri(a, OLCUTLER) for a in alt]


def _model_puani(model, alt_f, f, bant):
    """Tek bir (n−1)'li modelle puanlar: (E, fark, ek)."""
    tepeler = [tepe_acisi(u["kol"]) for u in alt_f]
    tepe = tepe_acisi(f["kol"])
    if bant == "v2":
        E, fark, ek = aci_bandi_puanlari(model, f, OLCUTLER, YONLER)
        ek = {"kapsam": ek["kapsam"], "aralik_disi": float(ek["aralik_disi"])}
    else:
        E, fark = coklu_model_puanlari(model, f, OLCUTLER, YONLER)
        ek = {}
    fark[ht.KALDIRMA] = ht.kaldirma_sapmasi(tepe, tepeler)
    return E, fark, ek


def puan_tablosu(tekrarlar, bant: str, ozl=None, yazdir=True) -> pd.DataFrame:
    ozl = ozl or {id(t): ozellikler(t.dizi, OLCUTLER) for t in tekrarlar}
    kayit = []
    for _, grup in veri.gruplara_ayir(tekrarlar).items():
        tl = [(t, _kes(ozl[id(t)], t.etiketli)) for t in grup]
        dogrular = [(t, f) for t, f in tl if t.dogru]
        if len(dogrular) < 3:
            continue
        dogrular_f = [f for _, f in dogrular]
        modeller = grup_modelleri(dogrular_f, bant)
        altlar = birini_disarida_alt_kumeler(dogrular_f)
        for t, f in tl:
            if t.dogru:
                i = next(j for j, (u, _) in enumerate(dogrular) if u is t)
                secim = [i]
            else:
                secim = range(len(dogrular))
            sonuc = [_model_puani(modeller[i], altlar[i], f, bant) for i in secim]
            E = _ortalama([s[0] for s in sonuc])
            fark = _ortalama([s[1] for s in sonuc])
            r = {"bant": bant, "video": t.video, "kisi": t.kisi, "kamera": t.kamera, "yonelim": t.yonelim,
                 "tekrar_no": t.tekrar_no, "satir": t.satir, "gorus": t.gorus, "hata": t.hata,
                 "ek_hata": t.ek_hata, "model_sayisi": len(sonuc), "tepe_acisi": tepe_acisi(f["kol"])}
            r.update({ht.puan_sutunu(k, y): E[(k, y)] for k in OLCUTLER for y in YONLER})
            r.update({ht.fark_sutunu(k): v for k, v in fark.items()})
            if bant == "v2":
                r["kapsam"] = float(np.mean([s[2]["kapsam"] for s in sonuc]))
                # Karar 7 ayrıntısı: modellerin yarısından fazlasında bayrak
                r["aralik_disi"] = bool(np.mean([s[2]["aralik_disi"] for s in sonuc]) > 0.5)
            kayit.append(r)
    df = pd.DataFrame(kayit)
    df["gorus_grubu"] = df.gorus.map(veri.gorus_grubu)
    return df


# ---------------------------------------------------------------- 2) birini-dışarıda-bırak karar
def loso(puan: pd.DataFrame, yonlu: bool):
    """Kişi bazlı birini-dışarıda-bırak. Dönüş: (tahmin tablosu, kural kaydı)."""
    parcalar, kurallar = [], []
    for kisi in sorted(puan.kisi.unique()):
        egitim = puan[(puan.kisi != kisi) & gorus_maskesi(puan, AYAR_GORUSU)]
        test = puan[puan.kisi == kisi]
        kural = ht.esik_sec(egitim, yonlu)
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
        for h in ht.HATALAR:
            p[f"z_{ht.KISA_AD[h]}"] = z[h]
        p["toplam_hata"] = toplam
        p["temel_tahmin_yanlis"] = toplam >= Tb
        parcalar.append(p)
        kurallar.append({"test kişisi": kisi, "T": kural.T, "öne kaçma ölçütü": kural.on_olcut,
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


def ozet_satiri(p: pd.DataFrame) -> dict:
    """Bir tahmin tablosu dilimi için ana sayılar (katı ve esnek)."""
    hatali = p.hata != ht.DOGRU
    r = {"tekrar": len(p), "hatalı tekrar": int(hatali.sum())}
    r["makro-F1 (katı)"] = makro_f1(p.hata, p.tahmin, ht.SINIFLAR)
    r["makro-F1 (esnek)"] = makro_f1(p.esnek_gercek, p.tahmin, ht.SINIFLAR)
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


def temel_satiri(p: pd.DataFrame) -> dict:
    hatali = p.hata != ht.DOGRU
    r = {"tekrar": len(p), "hatalı tekrar": int(hatali.sum())}
    r.update(_ikili(hatali, p.temel_tahmin_yanlis))
    return r


def tablolar_uret(tahminler: dict, kurallar: dict, puanlar: dict, bootstrap_n=2000) -> dict:
    T = {}
    ozet, temel, sinif, gorus_grup, kisi, kar = [], [], [], [], [], {}
    for (bant, yonlu), p in tahminler.items():
        ad = sistem_adi(bant, yonlu)
        for gorus in GORUSLER + ("profil (70–90°)",):
            g = p[gorus_maskesi(p, gorus)]
            ozet.append({"sistem": ad, "görüş": gorus, **ozet_satiri(g)})
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
                                 100 * float((g.tahmin == g.hata)[g.hata != ht.DOGRU].mean())})
    T["ozet"] = pd.DataFrame(ozet)
    T["temel_cizgi"] = pd.DataFrame(temel)
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


def calistir(cikti=CIKTI, puan_hazir=False, bootstrap_n=2000, yazdir=True):
    t0 = time.time()
    cikti = Path(cikti)
    cikti.mkdir(parents=True, exist_ok=True)
    puanlar = puanlari_oku(cikti) if puan_hazir else puanlari_hesapla(cikti, yazdir)
    tahminler, kurallar = {}, {}
    for bant, yonlu in SISTEMLER:
        tahminler[(bant, yonlu)], kurallar[(bant, yonlu)] = loso(puanlar[bant], yonlu)
    T = tablolar_uret(tahminler, kurallar, puanlar, bootstrap_n)
    kar = T.pop("_kar")
    T["tahminler"] = pd.concat([p.assign(sistem=sistem_adi(*s)) for s, p in tahminler.items()], ignore_index=True)
    sonuclari_yaz(T, cikti)
    for gorus, ek in ((ONDEN_CAPRAZ, "oc"), (TUMU, "tum")):
        for s in SISTEMLER:
            ad = sistem_adi(*s)
            karisiklik_sekli(kar[(ad, gorus, "katı")], f"Deney 2 · {ad} · {gorus} · katı (birincil hata)",
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


def main():
    ap = argparse.ArgumentParser(description="Deney 2: hata türünü bulma")
    ap.add_argument("--cikti", default=str(CIKTI))
    ap.add_argument("--puan-hazir", action="store_true", help="puanlar.csv'yi yeniden hesaplama")
    ap.add_argument("--bootstrap", type=int, default=2000)
    ap.add_argument("--galeri", action="store_true", help="galeri videolarını da üret")
    ap.add_argument("--adet", type=int, default=3)
    args = ap.parse_args()
    utf8_cikti()
    print("Deney 2 — hata türünü bulma")
    T, tahminler, puanlar, kurallar = calistir(args.cikti, args.puan_hazir, args.bootstrap)
    if args.galeri:
        from deneyler import deney2_galeri
        print("\nGaleri üretiliyor...")
        deney2_galeri.galeri(tahminler[ANA_SISTEM], kurallar[ANA_SISTEM], Path(args.cikti) / "galeri", n=args.adet)


if __name__ == "__main__":
    main()
