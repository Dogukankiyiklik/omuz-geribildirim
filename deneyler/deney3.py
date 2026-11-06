"""
Deney 3 — kural tabanlı Türkçe geri bildirim (Adım 5; PLAN + Güncelleme 01, 05, 06).

Soru: Deney 2'nin kararı ölçü içeren bir Türkçe cümleye çevrildiğinde, cümle doğru hatayı
adlandırıyor mu? Doğru tekrarlarda gereksiz uyarı ne sıklıkta?

Tanımlar ADIM_05.md "Önceden belirlenenler" bölümünde (kod ve sonuçlardan önce commit'lendi):
  * Sistem: dondurulmuş ana sistem (Karar 18): v2 açı bandı + yönlü + ilk sürüm kaldırma.
    Karar Deney 2 ile aynı kod (deneyler/deney2 puanları + cekirdek/hata_turu.esik_sec, kişi bazlı
    birini-dışarıda-bırak); sonuclar/deney2/tahminler.csv ile birebir aynı olduğu denetlenir.
  * En fazla 2 hata (ht.ilk_iki); cümle cekirdek/geribildirim.py; cümleden hata listesi
    cekirdek/metin_cozumleyici.py (Deney 4'te LLM cümleleri de aynı çıkarıcıyla).
  * Metrikler: katı / esnek / ilk iki / ilk iki (esnek), hatalılarda olumlu cümle, doğrularda
    gereksiz uyarı, çıkarıcı uyumu; ana tablo önden + çapraz, ayrıca tüm görüşler, profil, görüş
    grupları, kişiler; kişi bazlı bootstrap (2000, tohum 1).

Kullanım:
    python -m deneyler.deney3                  # ~1–3 dk; önce python -m deneyler.deney2 çalışmış olmalı
    python -m deneyler.deney3 --bootstrap 0    # bootstrap'sız (hızlı sınama)
Çıktı: sonuclar/deney3/
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path

import numpy as np
import pandas as pd

from cekirdek import geribildirim as gb
from cekirdek import hata_turu as ht
from cekirdek import veri
from cekirdek.aci_bandi import aci_bandi_hatasi, tepe_acisi
from cekirdek.adil_model import birini_disarida_alt_kumeler
from cekirdek.degerlendirme import guven_araligi, kisi_bootstrap
from cekirdek.konsol import sonuclari_yaz, utf8_cikti
from cekirdek.metin_cozumleyici import cozumle
from cekirdek.ozellikler import DENEY2_OLCUTLERI, ozellikler
from deneyler import deney2
from deneyler.deney1 import GORUS_GRUPLARI
from deneyler.tablolar import ONDEN_CAPRAZ, TUMU, gorus_maskesi

CIKTI = veri.KOK / "sonuclar" / "deney3"
OLCUTLER = list(DENEY2_OLCUTLERI)
ANLATIM = [gb.OMUZ_ANLATIM]
ANAHTAR = ["video", "kamera", "yonelim", "satir"]
GORUSLER = (ONDEN_CAPRAZ, TUMU, "profil (70–90°)")
BANT, YONLU = deney2.ANA_SISTEM   # ("v2", True)
TOHUM = 0


# ---------------------------------------------------------------- 1) karar (Deney 2 ile aynı)
def kararlar(puan: pd.DataFrame, kaldirma_surumu: str = ht.VARSAYILAN_KALDIRMA):
    """Kişi bazlı birini-dışarıda-bırak: kural (Deney 2 ile aynı), ilk iki hata, şiddet eşikleri ve sınıfları."""
    satirlar, esik_kayit, kurallar = [], [], {}
    for kisi in sorted(puan.kisi.unique()):
        egitim = puan[(puan.kisi != kisi) & gorus_maskesi(puan, deney2.AYAR_GORUSU)]
        test = puan[puan.kisi == kisi]
        kural = ht.esik_sec(egitim, YONLU, ht.EX1, kaldirma_surumu)
        esik = gb.siddet_esikleri(egitim, kural)
        z = kural.z(test)
        ii = ht.ilk_iki(z, kural.T)
        tah = kural.karar(test, z)
        puanlar = {h: ht.olcut_puani(test, k, kural.yon(k), kural.kaldirma_surumu) for h, k in kural.esleme.items()}
        p = test[ANAHTAR + ["kisi", "tekrar_no", "gorus", "gorus_grubu", "hata", "ek_hata"]].copy()
        p["tahmin"] = tah
        p["T"] = kural.T
        p = p.join(ii[["z1", "z2", "soylenen1", "soylenen2"]])
        for sira in (1, 2):
            s = p[f"soylenen{sira}"]
            p[f"siddet{sira}"] = [gb.siddet_sinifi(puanlar[h].loc[i], esik[h]) if h in esik else ""
                                  for i, h in zip(p.index, s)]
        satirlar.append(p)
        kurallar[kisi] = kural
        for h, (q1, q2) in esik.items():
            esik_kayit.append({"test kişisi": kisi, "hata": h, "kısa ad": ht.KISA_AD[h], "ölçüt": kural.esleme[h],
                               "yön": kural.yon(kural.esleme[h]), "q1 (%33,3)": q1, "q2 (%66,7)": q2,
                               "eğitimdeki etiketli tekrar": int((egitim.hata == h).sum())})
    return pd.concat(satirlar), kurallar, pd.DataFrame(esik_kayit)


def deney2_ile_denetle(p: pd.DataFrame, yol: Path = deney2.CIKTI / "tahminler.csv") -> int:
    """Kararlar sonuclar/deney2/tahminler.csv (v2_yonlu) ile birebir aynı olmalı. Dönüş: denetlenen satır."""
    if not Path(yol).exists():
        print("  UYARI: sonuclar/deney2/tahminler.csv yok; denetim atlandı")
        return 0
    d2 = pd.read_csv(yol, encoding="utf-8-sig", keep_default_na=False)
    d2 = d2[d2.sistem == deney2.sistem_adi(BANT, YONLU)].set_index(ANAHTAR)
    q = p.set_index(ANAHTAR).join(d2[["tahmin", "soylenen1", "soylenen2"]], rsuffix="_d2", how="inner")
    assert len(q) == len(p) == len(d2), (len(q), len(p), len(d2))
    for c in ("tahmin", "soylenen1", "soylenen2"):
        assert (q[c].astype(str) == q[f"{c}_d2"].astype(str)).all(), c
    return len(q)


# ---------------------------------------------------------------- 2) kare bazında ayrıntı (Karar 7)
def ayrintilar(tekrarlar) -> dict:
    """Her tekrar için kol, ham değerler, model ortalaması μ ve bant_disi (Karar 7), omuz eğimi bandı, tepe."""
    ozl = {id(t): ozellikler(t.dizi, OLCUTLER + ANLATIM) for t in tekrarlar}
    cikti = {}
    for _, grup in veri.gruplara_ayir(tekrarlar).items():
        tl = [(t, deney2._kes(ozl[id(t)], t.etiketli)) for t in grup]
        dogrular = [(t, f) for t, f in tl if t.dogru]
        if len(dogrular) < 3:
            continue
        dogrular_f = [f for _, f in dogrular]
        modeller = deney2.grup_modelleri(dogrular_f, "v2", OLCUTLER)
        modeller_ek = deney2.grup_modelleri(dogrular_f, "v2", ANLATIM)
        altlar = birini_disarida_alt_kumeler(dogrular_f)
        for t, f in tl:
            secim = ([next(j for j, (u, _) in enumerate(dogrular) if u is t)] if t.dogru
                     else list(range(len(dogrular))))
            ayr = [aci_bandi_hatasi(modeller[i], f, OLCUTLER, ayrinti=True)[1] for i in secim]
            ayr_ek = [aci_bandi_hatasi(modeller_ek[i], f, ANLATIM, ayrinti=True)[1] for i in secim]
            mu, bd = {}, {}
            for k in OLCUTLER:
                mu[k], bd[k] = gb.model_ortalamasi(ayr, k)
            mu_ek, _ = gb.model_ortalamasi(ayr_ek, gb.OMUZ_ANLATIM)
            beklenen_tepe = float(np.mean([np.median([tepe_acisi(u["kol"]) for u in altlar[i]]) for i in secim]))
            cikti[(t.video, t.kamera, int(t.yonelim), int(t.satir))] = {
                "kol": f["kol"], "deger": {k: f[k] for k in OLCUTLER}, "mu": mu, "bd": bd,
                "ek_deger": f[gb.OMUZ_ANLATIM], "ek_mu": mu_ek,
                "tepe": tepe_acisi(f["kol"]), "beklenen_tepe": beklenen_tepe}
    return cikti


def kod_uret(hata: str, siddet: str, kural: ht.KararKurali, a: dict) -> gb.SapmaKodu:
    k = kural.esleme[hata]
    yon = kural.yon(k)
    if k == ht.KALDIRMA:
        return gb.kaldirma_kodu(yon, siddet, a["tepe"], a["beklenen_tepe"])
    ek = (a["ek_deger"], a["ek_mu"]) if hata == ht.SILKME else (None, None)
    return gb.durus_kodu(hata, k, yon, siddet, a["kol"], a["deger"][k], a["mu"][k], a["bd"][k], *ek)


def cumleler(p: pd.DataFrame, kurallar: dict, ayr: dict, tohum: int = TOHUM) -> pd.DataFrame:
    """Her tekrar için sapma kodları, cümle ve çıkarılan hata listesi."""
    kayit = []
    for _, r in p.iterrows():
        a = ayr[(r.video, r.kamera, int(r.yonelim), int(r.satir))]
        kural = kurallar[r.kisi]
        kodlar = []
        for sira in (1, 2):
            h = r[f"soylenen{sira}"]
            if h and h != ht.DOGRU:
                kodlar.append(kod_uret(h, r[f"siddet{sira}"], kural, a))
        metin = gb.geri_bildirim(kodlar, a["tepe"], int(r.satir), tohum)
        L = cozumle(metin)
        niyet = [k.hata for k in kodlar]
        s = {c: r[c] for c in ANAHTAR + ["kisi", "tekrar_no", "gorus", "gorus_grubu", "hata", "ek_hata",
                                          "tahmin", "soylenen1", "soylenen2", "z1", "z2", "T"]}
        s["tepe_acisi"] = gb.yuvarla(a["tepe"])
        for i in (0, 1):
            d = kodlar[i].sozluk() if i < len(kodlar) else {}
            for alan in ("hata", "faz", "yon", "siddet", "olcut", "olcu", "beklenen", "fark", "birim",
                         "omuz_egim_fark"):
                s[f"{i + 1}_{alan}"] = d.get(alan, "")
        s["cumle"] = metin
        s["soylenmek_istenen"] = "|".join(niyet)
        s["cikarilan"] = "|".join(L)
        kayit.append(s)
    return pd.DataFrame(kayit)


# ---------------------------------------------------------------- 3) metrikler
def _liste(s: str) -> list[str]:
    return [x for x in str(s).split("|") if x]


def metrik_satiri(g: pd.DataFrame) -> dict:
    L = g.cikarilan.map(_liste)
    hatali = (g.hata != ht.DOGRU).to_numpy()
    kume = [ht.etiket_kumesi(h, e) for h, e in zip(g.hata, g.ek_hata)]
    ilk = np.array([l[0] if l else ht.DOGRU for l in L], dtype=object)
    birincil = g.hata.to_numpy()
    kati = ilk == birincil
    esnek = np.array([i in k for i, k in zip(ilk, kume)])
    ilk2 = np.array([b in l for b, l in zip(birincil, L)])
    ilk2e = np.array([bool(set(l) & k) for l, k in zip(L, kume)])
    bos = np.array([len(l) == 0 for l in L])
    iki = np.array([len(l) == 2 for l in L])
    uyum = (g.cikarilan == g.soylenmek_istenen).to_numpy()
    h, d = hatali, ~hatali

    def y(m, mask):
        return 100 * float(m[mask].mean()) if mask.any() else np.nan
    d2_tur = (g.tahmin == g.hata).to_numpy()
    d2_ilk2 = ((g.soylenen1 == g.hata) | (g.soylenen2 == g.hata)).to_numpy()
    return {"tekrar": len(g), "hatalı tekrar": int(h.sum()), "doğru tekrar": int(d.sum()),
            "katı: ilk söylenen = birincil /100": y(kati, h),
            "esnek: ilk söylenen ∈ birincil + ek /100": y(esnek, h),
            "ilk iki: birincil söylendi /100": y(ilk2, h),
            "ilk iki (esnek): etiketli bir hata söylendi /100": y(ilk2e, h),
            "hatalılarda olumlu cümle /100": y(bos, h),
            "doğrularda gereksiz uyarı /100": y(~bos, d),
            "doğrularda iki uyarı /100": y(iki, d),
            "hatalılarda iki hata söylendi /100": y(iki, h),
            "çıkarıcı uyumu /100": 100 * float(uyum.mean()),
            "denetim: Deney 2 tür doğru (katı) /100": y(d2_tur, h),
            "denetim: Deney 2 birincil söylenen ilk iki içinde /100": y(d2_ilk2, h)}


ANA_METRIKLER = ["katı: ilk söylenen = birincil /100", "esnek: ilk söylenen ∈ birincil + ek /100",
                 "ilk iki: birincil söylendi /100", "doğrularda gereksiz uyarı /100"]


def bootstrap_tablosu(c: pd.DataFrame, n=2000, tohum=1) -> pd.DataFrame:
    def istatistik(b):
        out = {}
        for gorus in (ONDEN_CAPRAZ, TUMU):
            m = metrik_satiri(b[gorus_maskesi(b, gorus)])
            for k in ANA_METRIKLER:
                out[f"{gorus}|{k}"] = m[k]
        return out
    nokta = istatistik(c)
    bs = kisi_bootstrap(c, istatistik, n=n, tohum=tohum)
    satir = []
    for col in bs.columns:
        alt, ust = guven_araligi(bs[col])
        gorus, olcu = col.split("|")
        satir.append({"görüş": gorus, "metrik": olcu, "nokta tahmini": nokta[col], "GA %2,5": alt, "GA %97,5": ust})
    return pd.DataFrame(satir)


def olcu_tablosu(c: pd.DataFrame) -> pd.DataFrame:
    """Betimsel: söylenen her hata için |fark| dağılımı, şiddet ve faz dağılımı (önden + çapraz)."""
    g = c[gorus_maskesi(c, ONDEN_CAPRAZ)]
    parca = []
    for i in (1, 2):
        x = g[g[f"{i}_hata"] != ""][[f"{i}_{a}" for a in ("hata", "faz", "siddet", "fark", "birim", "omuz_egim_fark")]
                                    + ["hata"]].copy()
        x.columns = ["söylenen", "faz", "siddet", "fark", "birim", "omuz_egim_fark", "gerçek"]
        x["sıra"] = i
        parca.append(x)
    x = pd.concat(parca)
    satir = []
    for h in ht.HATALAR:
        y = x[x["söylenen"] == h]
        f = pd.to_numeric(y.fark, errors="coerce").abs()
        e = pd.to_numeric(y.omuz_egim_fark, errors="coerce").abs()
        r = {"söylenen hata": ht.KISA_AD[h], "kez (1. veya 2.)": len(y), "1. sırada": int((y["sıra"] == 1).sum()),
             "birim": y.birim.iloc[0] if len(y) else "", "gerçek etiketle aynı": int((y["gerçek"] == h).sum()),
             "|fark| medyan": f.median(), "|fark| Ç1": f.quantile(0.25), "|fark| Ç3": f.quantile(0.75),
             "ölçüsüz cümle": int(f.isna().sum())}
        for s in gb.SIDDETLER:
            r[f"şiddet: {s}"] = int((y.siddet == s).sum())
        for fz in gb.FAZ_ADLARI.values():
            r[f"faz: {fz}"] = int((y.faz == fz).sum())
        if h == ht.SILKME:
            r["omuz eğimi |fark| medyan (°)"] = e.median()
            r["omuz eğimi söylenen (|fark| ≥ 1°)"] = int((e >= 1).sum())
        satir.append(r)
    return pd.DataFrame(satir)


def tablolar_uret(c: pd.DataFrame, esikler: pd.DataFrame, bootstrap_n=2000) -> dict:
    T = {"ozet": pd.DataFrame([{"görüş": gr, **metrik_satiri(c[gorus_maskesi(c, gr)])} for gr in GORUSLER]),
         "gorus_grubu": pd.DataFrame([{"görüş grubu": gg, **metrik_satiri(c[c.gorus_grubu == gg])}
                                      for gg in GORUS_GRUPLARI]),
         "kisi": pd.DataFrame([{"görüş": gr, "kisi": k, **metrik_satiri(g)}
                               for gr in (ONDEN_CAPRAZ, TUMU) for k, g in c[gorus_maskesi(c, gr)].groupby("kisi")]),
         "sinif": pd.DataFrame([{"görüş": gr, "gerçek sınıf": ht.KISA_AD[h], **metrik_satiri(g[g.hata == h])}
                                for gr in (ONDEN_CAPRAZ, TUMU) for g in [c[gorus_maskesi(c, gr)]]
                                for h in ht.SINIFLAR]),
         "olcu": olcu_tablosu(c),
         "siddet_esikleri": esikler}
    if bootstrap_n:
        T["bootstrap"] = bootstrap_tablosu(c, bootstrap_n)
    T["cumleler"] = c
    return T


def ornek_cumleler(c: pd.DataFrame, yol: Path, tohum: int = TOHUM) -> None:
    """Önden + çapraz: her gerçek sınıftan 3 + iki hata söylenen 2 tekrar = 20 (tohum sabit)."""
    rng = np.random.default_rng(tohum)
    g = c[gorus_maskesi(c, ONDEN_CAPRAZ)].reset_index(drop=True)
    secim = []
    for h in ht.SINIFLAR:
        idx = np.flatnonzero((g.hata == h).to_numpy())
        secim += [(ht.KISA_AD[h], int(i)) for i in sorted(rng.choice(idx, size=min(3, len(idx)), replace=False))]
    secilen = {i for _, i in secim}
    iki = [i for i in np.flatnonzero((g.soylenen2 != "").to_numpy()) if i not in secilen]
    secim += [("iki hata söylendi", int(i)) for i in sorted(rng.choice(iki, size=min(2, len(iki)), replace=False))]

    def ad(h):
        return ht.KISA_AD.get(h, h) if h else "–"
    md = ["# Deney 3 — örnek geri bildirim cümleleri", "",
          f"Önden + çapraz, tohum {tohum}. Her gerçek sınıftan 3 tekrar ve sistemin iki hata söylediği 2 tekrar.",
          "Ana sistem: v2 açı bandı + yönlü + ilk sürüm kaldırma (Karar 18). Ölçüler kişinin kendi kalibrasyonuna göre.",
          ""]
    for n, (grup, i) in enumerate(secim, 1):
        r = g.iloc[i]
        ek = ", ".join(ad(e) for e in sorted(ht.etiket_kumesi(r.hata, r.ek_hata) - {r.hata})) or "–"
        soy = ad(r.soylenen1) + (f" + {ad(r.soylenen2)}" if r.soylenen2 else "")
        md += [f"## {n}. ({grup}) {r.video} · {r.kamera} · yönelim {r.yonelim}° · görüş {r.gorus}° · tekrar {r.tekrar_no}",
               "",
               f"- **Gerçek etiket:** {ad(r.hata)} · **ek hatalar:** {ek}",
               f"- **Sistemin söylediği:** {soy} · çıkarıcının bulduğu: {', '.join(ad(x) for x in _liste(r.cikarilan)) or '–'}",
               "", f"> {r.cumle}", ""]
    md += ["## Okurken", "- Cümle anlaşılır mı? Ne yapman gerektiğini söylüyor mu?",
           "- Ölçü (derece, gövde %'si) mantıklı görünüyor mu?",
           "- Yanlış etiketlenmiş görünen örnekleri `araclar/gorsel_kontrol.py` ile videoda izleyebilirsin.", ""]
    yol.write_text("\n".join(md), encoding="utf-8")


# ---------------------------------------------------------------- çalıştır
def calistir(cikti=CIKTI, bootstrap_n=2000, yazdir=True, tohum: int = TOHUM):
    t0 = time.time()
    cikti = Path(cikti)
    cikti.mkdir(parents=True, exist_ok=True)
    puan = deney2.puanlari_oku(deney2.CIKTI)[BANT]
    p, kurallar, esikler = kararlar(puan)
    n = deney2_ile_denetle(p)
    if yazdir:
        print(f"  kararlar: {len(p)} tekrar; Deney 2 ile birebir aynı ({n} satır denetlendi)")
    ayr = ayrintilar(veri.tekrarlari_yukle(1))
    c = cumleler(p, kurallar, ayr, tohum)
    if yazdir:
        print(f"  cümleler: {len(c)} ({time.time() - t0:.1f} s)")
    T = tablolar_uret(c, esikler, bootstrap_n)
    sonuclari_yaz(T, cikti)
    ornek_cumleler(c, cikti / "ornek_cumleler.md", tohum)
    if yazdir:
        yazdir_ozet(T)
        print(f"\nSüre: {time.time() - t0:.1f} s · Çıktı: {cikti}")
    return T


def yazdir_ozet(T):
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 40)
    print("\n1) Özet (ana tablo: önden+çapraz):")
    print(T["ozet"].round(2).T.to_string(header=False))
    print("\n2) Görüş grubuna göre:")
    print(T["gorus_grubu"].round(2).T.to_string(header=False))
    print("\n3) Kişi bazlı (önden+çapraz):")
    k = T["kisi"]
    print(k[k["görüş"] == ONDEN_CAPRAZ].set_index("kisi")[ANA_METRIKLER + ["çıkarıcı uyumu /100"]].round(2).to_string())
    print("\n4) Söylenen hatanın ölçüsü (önden+çapraz):")
    print(T["olcu"].round(1).to_string(index=False))
    if "bootstrap" in T:
        print("\n5) Kişi bazlı bootstrap %95 GA:")
        print(T["bootstrap"].round(2).to_string(index=False))


def main():
    ap = argparse.ArgumentParser(description="Deney 3: kural tabanlı Türkçe geri bildirim")
    ap.add_argument("--cikti", default=str(CIKTI))
    ap.add_argument("--bootstrap", type=int, default=2000)
    ap.add_argument("--tohum", type=int, default=TOHUM)
    args = ap.parse_args()
    utf8_cikti()
    print("Deney 3 — kural tabanlı Türkçe geri bildirim (ana sistem: v2 yönlü, kaldırma ilk sürüm)")
    calistir(args.cikti, args.bootstrap, tohum=args.tohum)


if __name__ == "__main__":
    main()
