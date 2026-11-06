#!/usr/bin/env python3
"""
Deney 1 — Omuz silkme ölçütlerinin karşılaştırılması (REHAB26-ViewAngles, Ex1 kol abdüksiyonu).

Soru: Literatürdeki farklı omuz silkme ölçütlerinden hangisi, "omuz yükselmesi" etiketli tekrarları
doğru tekrarlardan (ve diğer hatalardan) en iyi ayırıyor? Kişiye özel tolerans bandı (M39) bu ayrımı iyileştiriyor mu?

Ölçütler (sağ kol egzersiz yapıyor; MediaPipe: 12 sağ omuz, 11 sol omuz, 8 sağ kulak, 24 sağ kalça, 14 sağ dirsek):
  M01      : iki omzun ortalama yüksekliğinin tekrar başındaki değerine göre kalkışı (M01, Denklem 8)
  M01_tek  : aynı ölçüt, yalnızca egzersiz yapan omuz (bizim varyant)
  M39_F2   : sağ omuzdaki açı (sol omuz – sağ omuz – sağ kalça) (M39, Tablo 1, F2)
  M33      : sağ omzun iki omuz orta noktasına (boyun yerine) göre dikey konumu (M33'ten uyarlama)
  YENI     : sağ kulak ile sağ omuz arasındaki dikey mesafe (bizim aday)
Uzunluk tabanlı ölçütler, görüş açısından bağımsız olsun diye gövde uzunluğuna bölünür (omuz genişliği profilde sıfıra iner).

İki değerlendirme:
  ham   : kişiye özel model yok; tekrar başındaki değere göre en büyük sapma (M01 tarzı, %90 yüzdelik)
  bant  : M39'un kişiye özel tolerans bandı (DTW hizalama + kare başına %95 güven aralığı), birini-dışarıda-bırak

Çıktı: sonuclar_deney1.csv (tekrar başına skorlar) ve ekrana AUC/Ψ tabloları.
"""
import sys
import numpy as np
import pandas as pd
from scipy import stats

NPZ = sys.argv[1] if len(sys.argv) > 1 else "rehab26_kucuk.npz"
SEG = sys.argv[2] if len(sys.argv) > 2 else "Segmentation.csv"
EN_BOY = float(sys.argv[3]) if len(sys.argv) > 3 else 9 / 16   # genişlik / yükseklik (dikey telefon videosu)
TOHUM = int(sys.argv[4]) if len(sys.argv) > 4 else 0

J = {j: i for i, j in enumerate([0, 2, 5, 7, 8, 11, 12, 13, 14, 15, 16, 23, 24])}
KAMERA_KONUMU = {"cam1": 0, "cam2": 45, "cam3": 90}   # M39 Şekil 2; görüş açısı = kamera konumu − yönelim
OLCUTLER = ["M01", "M01_tek", "M39_F2", "M33", "YENI"]


# ---------------------------------------------------------------- yardımcılar
def p(a, j):
    """Eklemin en-boy düzeltilmiş 2B koordinatı (y aşağı doğru)."""
    xy = a[:, J[j], :2].astype(np.float64).copy()
    xy[:, 0] *= EN_BOY
    return xy


def aci(u, v):
    c = (u * v).sum(1) / (np.linalg.norm(u, axis=1) * np.linalg.norm(v, axis=1) + 1e-9)
    return np.degrees(np.arccos(np.clip(c, -1, 1)))


def ozellikler(a):
    """Bir tekrar dizisinden kare başına kol açısı ve beş omuz ölçütü."""
    sL, sR, eR, earR, hL, hR = p(a, 11), p(a, 12), p(a, 14), p(a, 8), p(a, 23), p(a, 24)
    govde = np.linalg.norm((sL + sR) / 2 - (hL + hR) / 2, axis=1)
    g0 = np.median(govde[:8])                                  # tekrar başı (dinlenme) gövde uzunluğu
    asagi = np.tile([0.0, 1.0], (len(a), 1))
    f = {"kol": aci(eR - sR, asagi)}                           # kol yükselme açısı (M01, Denklem 5)
    ort_y = (sL[:, 1] + sR[:, 1]) / 2
    f["M01"] = (np.median(ort_y[:8]) - ort_y) / g0             # pozitif = omuz çizgisi kalktı
    f["M01_tek"] = (np.median(sR[:8, 1]) - sR[:, 1]) / g0
    f["M39_F2"] = aci(sL - sR, hR - sR)
    f["M33"] = (ort_y - sR[:, 1]) / g0                         # pozitif = sağ omuz ortanın üstünde
    f["YENI"] = (sR[:, 1] - earR[:, 1]) / g0                   # küçülürse omuz kulağa yaklaşıyor
    return f


def dtw_yol(a, b):
    """1B diziler için DTW hizalama yolu (z-normalize edilmiş, M22)."""
    a = (a - a.mean()) / (a.std() + 1e-9)
    b = (b - b.mean()) / (b.std() + 1e-9)
    n, m = len(a), len(b)
    D = np.full((n + 1, m + 1), np.inf)
    D[0, 0] = 0
    maliyet = np.abs(a[:, None] - b[None, :])
    for i in range(1, n + 1):
        satir = D[i]
        onceki = D[i - 1]
        for j in range(1, m + 1):
            satir[j] = maliyet[i - 1, j - 1] + min(onceki[j], satir[j - 1], onceki[j - 1])
    i, j, yol = n, m, []
    while i > 0 and j > 0:
        yol.append((i - 1, j - 1))
        k = np.argmin([D[i - 1, j - 1], D[i - 1, j], D[i, j - 1]])
        i, j = (i - 1, j - 1) if k == 0 else (i - 1, j) if k == 1 else (i, j - 1)
    return yol[::-1]


def hizala(ref_kol, tekrar):
    """Tekrarın her ölçütünü referans karelerine eşler (aynı ref karesine düşenlerin ortalaması)."""
    yol = dtw_yol(ref_kol, tekrar["kol"])
    n = len(ref_kol)
    cikti = {}
    for k in OLCUTLER:
        top, say = np.zeros(n), np.zeros(n)
        for i, j in yol:
            top[i] += tekrar[k][j]
            say[i] += 1
        cikti[k] = top / np.maximum(say, 1)
    return cikti


def bant_modeli(dogrular, rng):
    """M39: rastgele bir doğru tekrar referans; diğerleri hizalanır; kare başına μ ve τ (%95 GA, t dağılımı)."""
    r = rng.integers(len(dogrular))
    ref = dogrular[r]
    hizali = [ref] + [hizala(ref["kol"], t) for i, t in enumerate(dogrular) if i != r]
    model = {"ref_kol": ref["kol"]}
    n = len(hizali)
    tq = stats.t.ppf(0.975, max(n - 1, 1))
    for k in OLCUTLER:
        X = np.vstack([h[k] for h in hizali])
        mu = X.mean(0)
        tau = tq * X.std(0, ddof=1) / np.sqrt(n) if n > 1 else np.zeros_like(mu)
        tau = np.maximum(tau, np.percentile(tau, 25) + 1e-9)   # M39: dar aralıklar için alt sınır (Q1)
        model[k] = (mu, tau)
    return model


def bant_hatasi(model, tekrar):
    h = hizala(model["ref_kol"], tekrar)
    E = {}
    for k in OLCUTLER:
        mu, tau = model[k]
        sapma = np.abs(h[k] - mu)
        e = np.where(sapma <= tau, 0, np.minimum(1, (sapma - tau) / tau))
        E[k] = e.mean()
    return E


def ham_skor(tekrar):
    """Kişiye özel model olmadan: tekrar başına göre mutlak sapmanın %90 yüzdeliği."""
    return {k: np.percentile(np.abs(tekrar[k] - np.median(tekrar[k][:8])), 90) for k in OLCUTLER}


def auc(poz, neg):
    poz, neg = np.asarray(poz), np.asarray(neg)
    if len(poz) == 0 or len(neg) == 0:
        return np.nan
    return stats.mannwhitneyu(poz, neg, alternative="two-sided").statistic / (len(poz) * len(neg))


# ---------------------------------------------------------------- ana akış
def main():
    rng = np.random.default_rng(TOHUM)
    seg = pd.read_csv(SEG, sep=";")
    d = np.load(NPZ)
    kayit = []
    gruplar = {}
    for anahtar in d.files:
        if not anahtar.startswith("ex1_"):
            continue
        vid, kam, _, _, satir, _, o = anahtar.split("|")
        gruplar.setdefault((vid, kam, int(o[1:])), []).append((int(satir[5:]), anahtar))

    for (vid, kam, o), uyeler in sorted(gruplar.items()):
        tekrarlar = []
        for satir, anahtar in uyeler:
            r = seg.loc[satir]
            tekrarlar.append({
                "satir": satir, "f": ozellikler(d[anahtar]),
                "dogru": r.correctness_score == 1,
                "hata": r.error_description if isinstance(r.error_description, str) else "DOGRU",
                "ek_hata": r.additional_errors if isinstance(r.additional_errors, str) else "",
            })
        dogrular = [t for t in tekrarlar if t["dogru"]]
        if len(dogrular) < 3:
            continue
        for t in tekrarlar:
            if t["dogru"]:   # birini-dışarıda-bırak: kendisi modele girmesin
                digerleri = [u["f"] for u in dogrular if u is not t]
            else:            # adil karşılaştırma: hatalı tekrar da (n−1) doğru tekrarlık modelle ölçülür
                atla = rng.integers(len(dogrular))
                digerleri = [u["f"] for i, u in enumerate(dogrular) if i != atla]
            E = bant_hatasi(bant_modeli(digerleri, rng), t["f"])
            H = ham_skor(t["f"])
            satir = {"video": vid, "kamera": kam, "yonelim": o,
                     "gorus": KAMERA_KONUMU[kam] - o, "hata": t["hata"], "ek_hata": t["ek_hata"],
                     "satir": t["satir"]}
            satir.update({f"bant_{k}": E[k] for k in OLCUTLER})
            satir.update({f"ham_{k}": H[k] for k in OLCUTLER})
            kayit.append(satir)

    df = pd.DataFrame(kayit)
    df["kisi"] = df.video.str.split("_").str[1]
    df["gorus_abs"] = df.gorus.abs()
    df["gorus_grubu"] = pd.cut(df.gorus_abs, [-1, 20, 60, 90], labels=["önden (0–20°)", "çapraz (30–60°)", "profil (70–90°)"])
    df.to_csv("sonuclar_deney1.csv", index=False)

    silkme = df.hata == "ERR_ELEVATED_SHOULDER"
    dogru = (df.hata == "DOGRU") & ~df.ek_hata.str.contains("ELEVATED")
    diger = (df.hata != "DOGRU") & ~silkme & ~df.ek_hata.str.contains("ELEVATED")
    print(f"Tekrar sayıları (3 kamera dahil): silkme={silkme.sum()}, doğru={dogru.sum()}, diğer hatalar={diger.sum()}\n")

    satirlar = []
    for yontem in ["ham", "bant"]:
        for k in OLCUTLER:
            c = f"{yontem}_{k}"
            satir = {"yöntem": yontem, "ölçüt": k,
                     "AUC silkme/doğru": auc(df.loc[silkme, c], df.loc[dogru, c]),
                     "AUC silkme/diğer hatalar": auc(df.loc[silkme, c], df.loc[diger, c])}
            for g in df.gorus_grubu.cat.categories:
                m = df.gorus_grubu == g
                satir[f"AUC {g}"] = auc(df.loc[silkme & m, c], df.loc[dogru & m, c])
            if yontem == "bant":   # M39 Ψ: silkme tekrarının hatası − doğruların ortalama hatası
                psi = []
                for (v, ka, o), g in df.groupby(["video", "kamera", "yonelim"]):
                    s = g.loc[g.hata == "ERR_ELEVATED_SHOULDER", c]
                    if len(s):
                        psi += list(s - g.loc[g.hata == "DOGRU", c].mean())
                satir["Ψ (M39)"] = np.mean(psi)
            satirlar.append(satir)
    tablo = pd.DataFrame(satirlar)
    pd.set_option("display.width", 200)
    print(tablo.round(3).to_string(index=False))
    tablo.to_csv("ozet_deney1.csv", index=False)

    # Kişi bazlı bootstrap: 5 kişi yeniden örneklenir (aynı kişinin tekrarları bağımsız sayılmaz)
    print("\nBant yöntemi, AUC silkme/doğru için %95 güven aralığı (kişi bazlı bootstrap, 2000 tekrar):")
    kisiler = df.kisi.unique()
    bs = {k: [] for k in OLCUTLER}
    brng = np.random.default_rng(1)
    for _ in range(2000):
        secim = brng.choice(kisiler, len(kisiler), replace=True)
        b = pd.concat([df[df.kisi == s] for s in secim])
        bs_silkme = b.hata == "ERR_ELEVATED_SHOULDER"
        bs_dogru = (b.hata == "DOGRU") & ~b.ek_hata.str.contains("ELEVATED")
        for k in OLCUTLER:
            bs[k].append(auc(b.loc[bs_silkme, f"bant_{k}"], b.loc[bs_dogru, f"bant_{k}"]))
    for k in OLCUTLER:
        print(f"  {k:8s} {np.percentile(bs[k], 2.5):.3f} – {np.percentile(bs[k], 97.5):.3f}")
    fark = np.array(bs["YENI"]) - np.array(bs["M39_F2"])
    print(f"  YENI − M39_F2 farkı: ort. {fark.mean():.3f}, %95 GA {np.percentile(fark, 2.5):.3f} – {np.percentile(fark, 97.5):.3f}")

    # Hangi hata türleri silkme ile karışıyor? (bant yöntemi, hata türüne göre ortalama skor)
    print("\nHata türüne göre ortalama bant hatası:")
    print(df.groupby("hata")[[f"bant_{k}" for k in OLCUTLER]].mean().round(3).to_string())


if __name__ == "__main__":
    main()
