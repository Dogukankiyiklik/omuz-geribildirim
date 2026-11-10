"""
Deney 2 — hata türünü bulma.

Soru: Sistem bir tekrarın doğru olup olmadığını, yanlışsa HANGİ hatayı içerdiğini bulabiliyor mu?

1) Puanlar: her hata türünün bir ölçüsü var (cekirdek/hata_turu.py):
     omuz silkmesi → YENI (kulak–omuz), baş eğme → bas, kolun öne kaçması → on_kacma ya da kol_boyu,
     dirsek bükme → dirsek: kişiye özel açı bandı, YÖNLÜ (yalnızca hatanın yönündeki taşma sayılır).
     yetersiz kaldırma → tepe kol açısının kalibrasyon tepelerinin ortancasından eksikliği.
   Adillik (Deney 1 ile aynı): doğru tekrar birini-dışarıda-bırak; hatalı tekrar (n−1)'li bütün
   bantların ortalamasıyla. Bir çekimdeki n bant bir kez kurulur: doğru tekrar i, i'nci bantla
   (kendisi dışarıda) değerlendirilir.
2) Karar kuralı (cekirdek/hata_turu.py), kişi bazlı birini-dışarıda-bırak: 4 kişide ölçekleme (z),
   yönler, öne kaçma ölçüsü ve eşik T seçilir; 5. kişide sınanır. Ayar yalnızca eğitim kişilerinin
   önden + çapraz (|görüş| ≤ 60°) tekrarlarıyla yapılır (uygulamanın kurulumu).
     z = (puan − eğitimdeki doğru tekrarların ortancası) / (çeyrekler arası açıklık + ε)
     en büyük z < T → "doğru"; değilse hata türü = en büyük z'nin hatası.
3) "İlk iki": gerçek hata en yüksek iki z içinde mi; ikinci z de T'yi geçiyor mu (Deney 3'teki
   cümle en fazla iki hata söyler).

Bu, uygulamanın kullandığı yöntemdir; modeller/kural_ex1.json aynı yöntemle beş kişinin hepsiyle
kurulur (araclar/kural_disa_aktar.py).

Kullanım:
    python -m deneyler.deney2                 # ~15 sn
    python -m deneyler.deney2 --puan-hazir    # puanlar sonuclar/deney2/puanlar.csv'den okunur
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
from cekirdek import degerlendirici
from cekirdek.aci_bandi import aci_bandi_modeli, tepe_acisi
from cekirdek.adil_model import birini_disarida_alt_kumeler
from cekirdek.degerlendirme import karisiklik, makro_f1, sinif_metrikleri
from cekirdek.konsol import sonuclari_yaz, utf8_cikti
from cekirdek.ozellikler import DENEY2_OLCUTLERI, ozellikler
from deneyler.tablolar import GORUS_GRUPLARI, ONDEN_CAPRAZ, TUMU, gorus_maskesi

OLCUTLER = DENEY2_OLCUTLERI
YONLER = (0, 1, -1)
YONLU = True                 # yönlü açı bandı (uygulamanın yöntemi)
SISTEM_ADI = "v2_yonlu"      # kural dosyasına yazılan ad: açı bandı (v2), yönlü
AYAR_GORUSU = ONDEN_CAPRAZ
GORUSLER = (ONDEN_CAPRAZ, TUMU)
PROFIL = "profil (70–90°)"
CIKTI = veri.KOK / "sonuclar" / "deney2"


# ---------------------------------------------------------------- 1) tekrar puanları
def _kes(f: dict, s: slice) -> dict:
    return {k: v[s] for k, v in f.items()}


def _ortalama(sozlukler: list[dict]) -> dict:
    """Anahtar başına NaN'ları atlayan ortalama (açı bandında geçerli karesi olmayan bant atlanır)."""
    cikti = {}
    for a in sozlukler[0]:
        v = np.array([s[a] for s in sozlukler], dtype=float)
        cikti[a] = float(np.nanmean(v)) if np.any(~np.isnan(v)) else np.nan
    return cikti


def grup_modelleri(dogrular_f: list[dict], olcutler=OLCUTLER) -> list:
    """Bir çekimin n açı bandı (i. bant: i. doğru tekrar dışarıda)."""
    return [aci_bandi_modeli(a, olcutler) for a in birini_disarida_alt_kumeler(dogrular_f)]


def puan_tablosu(tekrarlar, ozl=None, olcutler=OLCUTLER, kaldirma=True) -> pd.DataFrame:
    """Tekrar başına puanlar. Puan kodu uygulamayla ortaktır (cekirdek/degerlendirici.py)."""
    olcutler = list(olcutler)
    ozl = ozl or {id(t): ozellikler(t.dizi, olcutler) for t in tekrarlar}
    kayit = []
    for _, grup in veri.gruplara_ayir(tekrarlar).items():
        tl = [(t, _kes(ozl[id(t)], t.etiketli)) for t in grup]
        dogrular = [(t, f) for t, f in tl if t.dogru]
        if len(dogrular) < 3:
            continue
        dogrular_f = [f for _, f in dogrular]
        modeller = grup_modelleri(dogrular_f, olcutler)
        altlar = birini_disarida_alt_kumeler(dogrular_f)
        for t, f in tl:
            secim = [next(j for j, (u, _) in enumerate(dogrular) if u is t)] if t.dogru else range(len(dogrular))
            sonuc = [degerlendirici.tekrar_puanlari(modeller[i], altlar[i], f, olcutler, kaldirma) for i in secim]
            E = _ortalama([s[0] for s in sonuc])
            fark = _ortalama([s[1] for s in sonuc])
            r = {"video": t.video, "kisi": t.kisi, "kamera": t.kamera, "yonelim": t.yonelim,
                 "tekrar_no": t.tekrar_no, "satir": t.satir, "gorus": t.gorus, "hata": t.hata,
                 "ek_hata": t.ek_hata, "model_sayisi": len(sonuc), "tepe_acisi": tepe_acisi(f["kol"])}
            r.update({ht.puan_sutunu(k, y): E[(k, y)] for k in olcutler + ([ht.KALDIRMA] if kaldirma else [])
                      for y in YONLER})
            r.update({ht.fark_sutunu(k): v for k, v in fark.items()})
            r["kapsam"] = float(np.mean([s[2]["kapsam"] for s in sonuc]))
            r["aralik_disi"] = bool(np.mean([s[2]["aralik_disi"] for s in sonuc]) > 0.5)  # bantların yarısından fazlası
            kayit.append(r)
    df = pd.DataFrame(kayit)
    df["gorus_grubu"] = df.gorus.map(veri.gorus_grubu)
    return df


# ---------------------------------------------------------------- 2) birini-dışarıda-bırak karar
def loso(puan: pd.DataFrame, tanim: ht.HataTanimi = ht.EX1, ayar_gorusu: str = AYAR_GORUSU):
    """Kişi bazlı birini-dışarıda-bırak. Ayar yalnızca eğitim kişilerinin ayar_gorusu tekrarlarıyla.
    Dönüş: (tahmin tablosu, kural kaydı)."""
    parcalar, kurallar = [], []
    for kisi in sorted(puan.kisi.unique()):
        egitim = puan[(puan.kisi != kisi) & gorus_maskesi(puan, ayar_gorusu)]
        test = puan[puan.kisi == kisi]
        kural = ht.esik_sec(egitim, YONLU, tanim)
        z = kural.z(test)
        tah = kural.karar(test, z)
        p = test[["video", "kisi", "kamera", "yonelim", "tekrar_no", "satir", "gorus", "gorus_grubu",
                  "hata", "ek_hata"]].copy()
        p["tahmin"] = tah
        p["esnek_gercek"] = ht.esnek_gercek(test.hata, test.ek_hata, tah)
        p["max_z"] = z.max(axis=1)
        p["T"] = kural.T
        p = p.join(ht.ilk_iki(z, kural.T))
        for h in kural.hatalar:
            p[f"z_{ht.KISA_AD[h]}"] = z[h]
        parcalar.append(p)
        kurallar.append({"test kişisi": kisi, "kaldırma sürümü": kural.kaldirma_surumu, "T": kural.T,
                         "öne kaçma ölçütü": kural.on_olcut,
                         "eğitim makro-F1": kural.bilgi["egitim_makro_f1"],
                         **{f"yön {k}": kural.yonler[k] for k in kural.yonler},
                         **{f"medyan {k}": kural.medyan[k] for k in kural.medyan},
                         **{f"ölçek {k}": kural.olcek[k] for k in kural.olcek}})
    return pd.concat(parcalar), pd.DataFrame(kurallar)


# ---------------------------------------------------------------- 3) tablolar
def ozet_satiri(p: pd.DataFrame, siniflar=ht.SINIFLAR) -> dict:
    """Bir tahmin tablosu dilimi için ana sayılar (katı ve esnek)."""
    hatali = p.hata != ht.DOGRU
    tah_hatali = p.tahmin != ht.DOGRU
    duy, ozg = float(tah_hatali[hatali].mean()), float((~tah_hatali[~hatali]).mean())
    r = {"tekrar": len(p), "hatalı tekrar": int(hatali.sum())}
    r["makro-F1 (katı)"] = makro_f1(p.hata, p.tahmin, siniflar)
    r["makro-F1 (esnek)"] = makro_f1(p.esnek_gercek, p.tahmin, siniflar)
    r["doğruluk 6 sınıf (katı)"] = float((p.hata == p.tahmin).mean())
    r["doğruluk 6 sınıf (esnek)"] = float((p.esnek_gercek == p.tahmin).mean())
    r["ikili doğruluk"] = float((hatali == tah_hatali).mean())
    r["duyarlılık (hatalıyı yakalama)"] = duy
    r["özgüllük (doğruya doğru deme)"] = ozg
    r["dengeli doğruluk"] = (duy + ozg) / 2
    # "100 hatalı tekrarın kaçında hatanın türünü doğru söyledi?"
    r["hatalılarda tür doğru /100 (katı)"] = 100 * float((p.tahmin[hatali] == p.hata[hatali]).mean())
    r["hatalılarda tür doğru /100 (esnek)"] = 100 * float((p.tahmin[hatali] == p.esnek_gercek[hatali]).mean())
    r["hatalılarda 'doğru' dedi /100"] = 100 * float((p.tahmin[hatali] == ht.DOGRU).mean())
    yakalanan = hatali & tah_hatali
    r["yakalanan hatalılarda tür doğru (%, katı)"] = 100 * float((p.tahmin[yakalanan] == p.hata[yakalanan]).mean())
    return r


def ilk_iki_satiri(p: pd.DataFrame) -> dict:
    """Hatalı tekrarlarda gerçek hata en yüksek iki z içinde mi; ikinci z de T'yi geçiyor mu."""
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


def _tur_dogru(g: pd.DataFrame) -> float:
    return 100 * float((g.tahmin == g.hata)[g.hata != ht.DOGRU].mean())


def tablolar_uret(p: pd.DataFrame, kurallar: pd.DataFrame) -> dict:
    T, kar = {}, {}
    ozet, ilk2, sinif = [], [], []
    for gorus in GORUSLER + (PROFIL,):
        g = p[gorus_maskesi(p, gorus)]
        ozet.append({"görüş": gorus, **ozet_satiri(g)})
        ilk2.append({"görüş": gorus, **ilk_iki_satiri(g)})
    for gorus in GORUSLER:
        g = p[gorus_maskesi(p, gorus)]
        for degerlendirme, gercek in (("katı", g.hata), ("esnek", g.esnek_gercek)):
            s = sinif_metrikleri(gercek, g.tahmin, ht.SINIFLAR)
            s.insert(0, "değerlendirme", degerlendirme)
            s.insert(0, "görüş", gorus)
            sinif.append(s)
            kar[(gorus, degerlendirme)] = karisiklik(gercek, g.tahmin, ht.SINIFLAR)
    T["ozet"] = pd.DataFrame(ozet)
    T["ilk_iki"] = pd.DataFrame(ilk2)
    T["siniflar"] = pd.concat(sinif, ignore_index=True)
    T["gorus_grubu"] = pd.DataFrame([
        {"görüş grubu": gg, "tekrar": len(g),
         "makro-F1 (katı)": makro_f1(g.hata, g.tahmin, ht.SINIFLAR),
         "makro-F1 (esnek)": makro_f1(g.esnek_gercek, g.tahmin, ht.SINIFLAR),
         "hatalılarda tür doğru /100 (katı)": _tur_dogru(g)}
        for gg in GORUS_GRUPLARI for g in [p[p.gorus_grubu == gg]]])
    T["kisi"] = pd.DataFrame([
        {"görüş": gorus, "kisi": k,
         "makro-F1 (katı)": makro_f1(g.hata, g.tahmin, ht.SINIFLAR),
         "hatalılarda tür doğru /100 (katı)": _tur_dogru(g),
         "hatalılarda 'doğru' dedi /100": 100 * float((g.tahmin == ht.DOGRU)[g.hata != ht.DOGRU].mean()),
         "hatalılarda birincil ilk iki z içinde /100": ilk_iki_satiri(g)["hatalılarda birincil ilk iki z içinde /100"]}
        for gorus in GORUSLER for k, g in p[gorus_maskesi(p, gorus)].groupby("kisi")])
    T["esikler"] = kurallar
    for (gorus, d), m in kar.items():
        mm = m.copy()
        mm.index = [f"gerçek: {ht.KISA_AD[c]}" for c in mm.index]
        mm.columns = [f"tahmin: {ht.KISA_AD[c]}" for c in mm.columns]
        ad = f"karisiklik_{'oc' if gorus == ONDEN_CAPRAZ else 'tum'}_{'kati' if d == 'katı' else 'esnek'}"
        T[ad] = mm.reset_index().rename(columns={"index": ""})
    T["tahminler"] = p
    return T, kar


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
def puanlari_hesapla(cikti: Path, yazdir=True) -> pd.DataFrame:
    t0 = time.time()
    tekrarlar = veri.tekrarlari_yukle(1)
    puan = puan_tablosu(tekrarlar, {id(t): ozellikler(t.dizi, OLCUTLER) for t in tekrarlar})
    puan.to_csv(cikti / "puanlar.csv", index=False, encoding="utf-8-sig")
    if yazdir:
        print(f"  puanlar: {len(puan)} tekrar, {time.time() - t0:.1f} s")
    return puan


def puanlari_oku(cikti: Path = CIKTI) -> pd.DataFrame:
    df = pd.read_csv(Path(cikti) / "puanlar.csv", encoding="utf-8-sig", keep_default_na=False,
                     na_values=["", "nan", "NaN"])
    df["ek_hata"] = df.ek_hata.astype(str).replace("nan", "")
    return df


def calistir(cikti=CIKTI, puan_hazir=False, yazdir=True):
    t0 = time.time()
    cikti = Path(cikti)
    cikti.mkdir(parents=True, exist_ok=True)
    puan = puanlari_oku(cikti) if puan_hazir else puanlari_hesapla(cikti, yazdir)
    tahmin, kurallar = loso(puan)
    T, kar = tablolar_uret(tahmin, kurallar)
    sonuclari_yaz(T, cikti)
    for gorus, ek in ((ONDEN_CAPRAZ, "oc"), (TUMU, "tum")):
        karisiklik_sekli(kar[(gorus, "katı")], f"Deney 2 · {gorus} · katı (birincil hata)",
                         cikti / f"karisiklik_{ek}.png")
    if yazdir:
        yazdir_ozet(T)
        print(f"\nSüre: {time.time() - t0:.1f} s · Çıktı: {cikti}")
    return T, tahmin, puan, kurallar


def yazdir_ozet(T):
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 40)
    print("\n1) Özet (katı = yalnızca birincil hata; esnek = ek hatalardan birini söylemek de doğru):")
    sut = ["görüş", "tekrar", "makro-F1 (katı)", "makro-F1 (esnek)", "hatalılarda tür doğru /100 (katı)",
           "hatalılarda 'doğru' dedi /100", "özgüllük (doğruya doğru deme)"]
    print(T["ozet"][sut].round(3).to_string(index=False))
    print("\n2) İlk iki:")
    print(T["ilk_iki"].round(2).to_string(index=False))
    print("\n3) Sınıf başına (önden+çapraz, katı):")
    s = T["siniflar"]
    print(s[(s["görüş"] == ONDEN_CAPRAZ) & (s["değerlendirme"] == "katı")].round(3).to_string(index=False))
    print("\n4) Karışıklık (önden+çapraz, katı):")
    print(T["karisiklik_oc_kati"].to_string(index=False))
    print("\n5) Görüş grubuna göre:")
    print(T["gorus_grubu"].round(3).to_string(index=False))
    print("\n6) Seçilen eşikler (her satır bir test kişisi; ayar diğer 4 kişide):")
    e = T["esikler"]
    print(e[["test kişisi", "T", "öne kaçma ölçütü", "eğitim makro-F1"]
            + [c for c in e.columns if c.startswith("yön ")]].round(3).to_string(index=False))
    print("\n7) Kişi bazlı makro-F1 (katı):")
    print(T["kisi"].pivot_table(index="görüş", columns="kisi", values="makro-F1 (katı)", sort=False)
          .round(3).to_string())


def main():
    ap = argparse.ArgumentParser(description="Deney 2: hata türünü bulma")
    ap.add_argument("--cikti", default=str(CIKTI))
    ap.add_argument("--puan-hazir", action="store_true", help="puanlar.csv'yi yeniden hesaplama")
    args = ap.parse_args()
    utf8_cikti()
    print("Deney 2 — hata türünü bulma")
    calistir(args.cikti, args.puan_hazir)


if __name__ == "__main__":
    main()
