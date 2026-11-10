"""
Deney 3 — kural tabanlı Türkçe geri bildirim.

Soru: Deney 2'nin kararı ölçü içeren bir Türkçe cümleye çevrildiğinde, cümle doğru hatayı
adlandırıyor mu? Doğru tekrarlarda gereksiz uyarı ne sıklıkta?

Adımlar:
  1. Karar: Deney 2 ile aynı kod (sonuclar/deney2/puanlar.csv + cekirdek/hata_turu.esik_sec, kişi bazlı
     birini-dışarıda-bırak); sonuclar/deney2/tahminler.csv ile birebir aynı olduğu denetlenir.
  2. Şiddet (hafif / orta / belirgin): eşikler eğitim kişilerinin hatalı tekrarlarından (gb.siddet_esikleri).
  3. Ölçü: söylenen hatanın "normalde X, sende Y" değerleri. Uygulamanın kullandığı sağlam ölçü:
     tek kare yerine seçilen fazdaki birkaç karenin medyanı (cekirdek/geribildirim.py).
  4. Metin: en fazla 2 hata; hasta cümlesi ve uzman ayrıntısı (cekirdek/geribildirim.py).
  5. Geri okuma: cümleden hata listesi kararı bilmeden çıkarılır (cekirdek/metin_cozumleyici.py) ve
     metrikler bu listeden hesaplanır. Böylece ölçülen şey metnin kendisidir.

Kullanım:
    python -m deneyler.deney3        # önce python -m deneyler.deney2 çalışmış olmalı
Çıktı: sonuclar/deney3/{ozet.csv, cumleler.csv, metin.csv, siddet_esikleri.csv, ornek_cumleler.md}
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path

import numpy as np
import pandas as pd

from cekirdek import degerlendirici
from cekirdek import geribildirim as gb
from cekirdek import hata_turu as ht
from cekirdek import veri
from cekirdek.aci_bandi import aci_bandi_hatasi, tepe_acisi
from cekirdek.adil_model import birini_disarida_alt_kumeler
from cekirdek.konsol import sonuclari_yaz, utf8_cikti
from cekirdek.metin_cozumleyici import cozumle
from cekirdek.ozellikler import DENEY2_OLCUTLERI, ozellikler
from deneyler import deney2
from deneyler.tablolar import ONDEN_CAPRAZ, TUMU, gorus_maskesi

OLCU_SURUMU = gb.VARSAYILAN_OLCU   # "saglam": uygulamanın kullandığı ölçü

CIKTI = veri.KOK / "sonuclar" / "deney3"
OLCUTLER = list(DENEY2_OLCUTLERI)
ANLATIM = [gb.OMUZ_ANLATIM]
ANAHTAR = ["video", "kamera", "yonelim", "satir"]
GORUSLER = (ONDEN_CAPRAZ, TUMU, "profil (70–90°)")
YONLU = deney2.YONLU   # yönlü açı bandı
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
    """Kararlar sonuclar/deney2/tahminler.csv ile birebir aynı olmalı. Dönüş: denetlenen satır."""
    if not Path(yol).exists():
        print("  UYARI: sonuclar/deney2/tahminler.csv yok; denetim atlandı")
        return 0
    d2 = pd.read_csv(yol, encoding="utf-8-sig", keep_default_na=False)
    d2 = d2.set_index(ANAHTAR)
    q = p.set_index(ANAHTAR).join(d2[["tahmin", "soylenen1", "soylenen2"]], rsuffix="_d2", how="inner")
    assert len(q) == len(p) == len(d2), (len(q), len(p), len(d2))
    for c in ("tahmin", "soylenen1", "soylenen2"):
        assert (q[c].astype(str) == q[f"{c}_d2"].astype(str)).all(), c
    return len(q)


# ---------------------------------------------------------------- 2) kare bazında ayrıntı
def ayrintilar(tekrarlar) -> dict:
    """Her tekrar için kol, ham değerler, model ortalaması μ ve bant_disi, omuz eğimi bandı, tepe."""
    ozl = {id(t): ozellikler(t.dizi, OLCUTLER + ANLATIM) for t in tekrarlar}
    cikti = {}
    for _, grup in veri.gruplara_ayir(tekrarlar).items():
        tl = [(t, deney2._kes(ozl[id(t)], t.etiketli)) for t in grup]
        dogrular = [(t, f) for t, f in tl if t.dogru]
        if len(dogrular) < 3:
            continue
        dogrular_f = [f for _, f in dogrular]
        modeller = deney2.grup_modelleri(dogrular_f, OLCUTLER)
        modeller_ek = deney2.grup_modelleri(dogrular_f, ANLATIM)
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
                "gor": {k: gb.olcut_gorunurlugu(t.dizi[t.etiketli], k) for k in OLCUTLER},
                "ek_deger": f[gb.OMUZ_ANLATIM], "ek_mu": mu_ek,
                "tepe": tepe_acisi(f["kol"]), "beklenen_tepe": beklenen_tepe}
    return cikti


kod_uret = degerlendirici.kod_uret   # uygulamayla ortak (cekirdek/degerlendirici.py)


def _sayi_var(metin: str) -> bool:
    return any(ch.isdigit() for ch in metin)


def cumleler(p: pd.DataFrame, kurallar: dict, ayr: dict, tohum: int = TOHUM,
             olcu_surumu: str = OLCU_SURUMU) -> pd.DataFrame:
    """Her tekrar için sapma kodları, iki metin ve her metinden çıkarılan hata listesi."""
    kayit = []
    for _, r in p.iterrows():
        a = ayr[(r.video, r.kamera, int(r.yonelim), int(r.satir))]
        kural = kurallar[r.kisi]
        kodlar = []
        for sira in (1, 2):
            h = r[f"soylenen{sira}"]
            if h and h != ht.DOGRU:
                kodlar.append(kod_uret(h, r[f"siddet{sira}"], kural, a, olcu_surumu))
        metin = gb.iki_katman(kodlar, a["tepe"], int(r.satir), tohum)
        niyet = [k.hata for k in kodlar]
        s = {c: r[c] for c in ANAHTAR + ["kisi", "tekrar_no", "gorus", "gorus_grubu", "hata", "ek_hata",
                                          "tahmin", "soylenen1", "soylenen2", "z1", "z2", "T"]}
        s["olcu_surumu"] = olcu_surumu
        s["tepe_acisi"] = gb.yuvarla(a["tepe"])
        for i in (0, 1):
            d = kodlar[i].sozluk() if i < len(kodlar) else {}
            for alan in ("hata", "faz", "yon", "siddet", "olcut", "olcu", "beklenen", "fark", "birim",
                         "omuz_egim_fark", "olcu_yolu", "olcu_kare_sayisi"):
                s[f"{i + 1}_{alan}"] = d.get(alan, "")
            hc = gb.hasta_cumlesi(kodlar[i]) if i < len(kodlar) else ""
            s[f"{i + 1}_hasta_sayili"] = _sayi_var(hc) if hc else ""
            s[f"{i + 1}_hasta_kelime"] = len(hc.split()) if hc else ""
        s["hasta_cumlesi"] = metin["hasta_cumlesi"]
        s["uzman_ayrintisi"] = metin["uzman_ayrintisi"]
        s["soylenmek_istenen"] = "|".join(niyet)
        s["cikarilan"] = "|".join(cozumle(metin["uzman_ayrintisi"]))
        s["cikarilan_hasta"] = "|".join(cozumle(metin["hasta_cumlesi"]))
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
    return {"tekrar": len(g), "hatalı tekrar": int(h.sum()), "doğru tekrar": int(d.sum()),
            "katı: ilk söylenen = birincil /100": y(kati, h),
            "esnek: ilk söylenen ∈ birincil + ek /100": y(esnek, h),
            "ilk iki: birincil söylendi /100": y(ilk2, h),
            "ilk iki (esnek): etiketli bir hata söylendi /100": y(ilk2e, h),
            "hatalılarda olumlu cümle /100": y(bos, h),
            "doğrularda gereksiz uyarı /100": y(~bos, d),
            "doğrularda iki uyarı /100": y(iki, d),
            "hatalılarda iki hata söylendi /100": y(iki, h),
            "çıkarıcı uyumu /100": 100 * float(uyum.mean())}


def metin_tablosu(c: pd.DataFrame) -> pd.DataFrame:
    """Betimsel (önden + çapraz): iki metnin kelime sayısı ve hasta cümlesinde sayı içerme oranı."""
    g = c[gorus_maskesi(c, ONDEN_CAPRAZ)]
    kel_h = g.hasta_cumlesi.str.split().str.len()
    kel_u = g.uzman_ayrintisi.str.split().str.len()
    satir = []
    for ad, m in [("bütün tekrarlar", np.ones(len(g), bool)), ("olumlu cümle (hata söylenmedi)", g.soylenen1 == ht.DOGRU),
                  ("bir hata söylendi", (g.soylenen1 != ht.DOGRU) & (g.soylenen2 == "")),
                  ("iki hata söylendi", g.soylenen2 != "")]:
        m = np.asarray(m)
        satir.append({"grup": ad, "tekrar": int(m.sum()),
                      "hasta: ortalama kelime (bütün metin)": kel_h[m].mean(),
                      "uzman: ortalama kelime (bütün metin)": kel_u[m].mean(),
                      "hasta: sayı içeren metin /100": 100 * g.hasta_cumlesi[m].map(_sayi_var).mean(),
                      "uzman: sayı içeren metin /100": 100 * g.uzman_ayrintisi[m].map(_sayi_var).mean()})
    # hata türüne göre: o hatanın kendi hasta cümlesi (1. ya da 2. sırada söylenmiş)
    for h in ht.HATALAR:
        say, kel = [], []
        for i in (1, 2):
            y = g[g[f"{i}_hata"] == h]
            say += [bool(v) for v in y[f"{i}_hasta_sayili"]]
            kel += [int(v) for v in y[f"{i}_hasta_kelime"]]
        satir.append({"grup": f"hata cümlesi: {ht.KISA_AD[h]}", "tekrar": len(say),
                      "hasta: ortalama kelime (bütün metin)": np.nan, "uzman: ortalama kelime (bütün metin)": np.nan,
                      "hasta: hata cümlesi ortalama kelime": float(np.mean(kel)) if kel else np.nan,
                      "hasta: sayı içeren hata cümlesi /100": 100 * float(np.mean(say)) if say else np.nan})
    return pd.DataFrame(satir)


def ozet_tablosu(c: pd.DataFrame) -> pd.DataFrame:
    """Görüş başına metrikler (hasta cümlesi ve uzman ayrıntısı aynı hata listesini verir; calistir denetler)."""
    return pd.DataFrame([{"görüş": gr, **metrik_satiri(c[gorus_maskesi(c, gr)])} for gr in GORUSLER])


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
    surum = str(c.olcu_surumu.iloc[0])
    md = ["# Deney 3 — örnek geri bildirim cümleleri", "",
          f"Önden + çapraz, tohum {tohum}. Her gerçek sınıftan 3 tekrar ve sistemin iki hata söylediği 2 tekrar.",
          "Sistem: kişiye özel açı bandı (yönlü), Deney 2'nin karar kuralı. Ölçüler kişinin kendi kalibrasyonuna göre.",
          f"Ölçü sürümü: `{surum}`. Her örnekte önce **hasta cümlesi** (uygulamada büyük yazı), "
          "altında **uzman ayrıntısı**.", ""]
    for n, (grup, i) in enumerate(secim, 1):
        r = g.iloc[i]
        ek_ham = "" if pd.isna(r.ek_hata) or str(r.ek_hata) == "nan" else str(r.ek_hata)
        ek = ", ".join(ad(e) for e in sorted(ht.etiket_kumesi(r.hata, ek_ham) - {r.hata})) or "–"
        soy = ad(r.soylenen1) + (f" + {ad(r.soylenen2)}" if r.soylenen2 else "")
        md += [f"## {n}. ({grup}) {r.video} · {r.kamera} · yönelim {r.yonelim}° · görüş {r.gorus}° · tekrar {r.tekrar_no}",
               "",
               f"- **Gerçek etiket:** {ad(r.hata)} · **ek hatalar:** {ek}",
               f"- **Sistemin söylediği:** {soy} · çıkarıcının bulduğu: {', '.join(ad(x) for x in _liste(r.cikarilan)) or '–'}",
               "", f"**Hasta cümlesi:** {r.hasta_cumlesi}", "",
               f"<sub>Uzman ayrıntısı: {r.uzman_ayrintisi}</sub>", ""]
    md += ["## Okurken", "- Hasta cümlesi anlaşılır mı? Ne yapman gerektiğini söylüyor mu?",
           "- Uzman ayrıntısındaki ölçü (derece, gövde %'si) mantıklı görünüyor mu?",
           "- Yanlış etiketlenmiş görünen örnekleri `araclar/gorsel_kontrol.py` ile videoda izleyebilirsin.", ""]
    yol.write_text("\n".join(md), encoding="utf-8")


# ---------------------------------------------------------------- çalıştır
def calistir(cikti=CIKTI, yazdir=True, tohum: int = TOHUM):
    t0 = time.time()
    cikti = Path(cikti)
    cikti.mkdir(parents=True, exist_ok=True)
    puan = deney2.puanlari_oku(deney2.CIKTI)
    p, kurallar, esikler = kararlar(puan)
    n = deney2_ile_denetle(p)
    if yazdir:
        print(f"  kararlar: {len(p)} tekrar; Deney 2 ile birebir aynı ({n} satır denetlendi)")
    ayr = ayrintilar(veri.tekrarlari_yukle(1))
    c = cumleler(p, kurallar, ayr, tohum)
    assert (c.cikarilan == c.cikarilan_hasta).all(), "hasta ve uzman metinleri farklı hata listesi verdi"
    if yazdir:
        print(f"  cümleler: {len(c)} ({time.time() - t0:.1f} s); hasta cümlesi ve uzman ayrıntısından aynı hata "
              f"listesi çıktı: {len(c)}/{len(c)}")
    T = {"ozet": ozet_tablosu(c), "metin": metin_tablosu(c), "siddet_esikleri": esikler, "cumleler": c}
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
    print("\n2) Metinler (önden+çapraz): kelime sayısı ve sayı içeren cümle oranı:")
    print(T["metin"].round(1).to_string(index=False))


def main():
    ap = argparse.ArgumentParser(description="Deney 3: kural tabanlı Türkçe geri bildirim")
    ap.add_argument("--cikti", default=str(CIKTI))
    ap.add_argument("--tohum", type=int, default=TOHUM)
    args = ap.parse_args()
    utf8_cikti()
    print("Deney 3 — kural tabanlı Türkçe geri bildirim")
    calistir(args.cikti, tohum=args.tohum)


if __name__ == "__main__":
    main()
