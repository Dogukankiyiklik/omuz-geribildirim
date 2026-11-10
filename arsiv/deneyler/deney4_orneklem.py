"""
Deney 4 (Adım 8) için tabakalı örneklem (Güncelleme 08, Karar 35: yalnızca örneklem; istem ve deney yok).

Kaynak: Deney 3'ün tekrar tablosu (sonuclar/deney3/cumleler.csv; birincil, tek kare ölçü). Yalnızca uygulama
senaryosu: önden + çapraz (Karar 6). PLAN'daki örnek gibi 50 doğru + her hata türünden 20 = 150 tekrar.
Tabaka = gerçek etiket (birincil hata) × kişi: her sınıfın kotası kişilere eşit bölünür (50 → 10'ar, 20 → 4'er);
bölünmezse artan tekrarlar tohumla karıştırılmış kişi sırasına göre birer birer dağıtılır. Böylece tek bir kişi
bir hata türüne baskın olmaz (sınıf tabakası tek başına öne kaçmanın 10/20'sini Vasil'den seçiyordu).
Her tabakada tablo (video, kamera, yönelim, satır) sırasına dizilir, sonra tohumlu rastgele seçim (yerine koymadan).
Bir tabakada yeterli tekrar yoksa hepsi alınır ve uyarı yazılır.

Kullanım:
    python -m deneyler.deney4_orneklem                # birkaç saniye
    python -m deneyler.deney4_orneklem --dogru 50 --hata 20 --tohum 0
Çıktı: sonuclar/deney4/orneklem.csv (seçilen tekrarların anahtarları + Deney 3 kararı ve cümleleri),
       sonuclar/deney4/orneklem_ozet.csv (tabaka × kişi sayıları)
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

from cekirdek import hata_turu as ht
from cekirdek import veri
from cekirdek.konsol import sonuclari_yaz, utf8_cikti
from deneyler.deney1 import GORUS_GRUPLARI

KAYNAK = veri.KOK / "sonuclar" / "deney3" / "cumleler.csv"
CIKTI = veri.KOK / "sonuclar" / "deney4"
ANAHTAR = ["video", "kamera", "yonelim", "satir"]
SUTUNLAR = ANAHTAR + ["kisi", "tekrar_no", "gorus", "gorus_grubu", "hata", "ek_hata", "tahmin", "soylenen1",
                      "soylenen2", "hasta_cumlesi", "uzman_ayrintisi"]


def orneklem_sec(c: pd.DataFrame, dogru: int = 50, hata: int = 20, tohum: int = 0,
                 gorus_gruplari=tuple(GORUS_GRUPLARI[:2])) -> pd.DataFrame:
    g = c[c.gorus_grubu.isin(gorus_gruplari)].sort_values(ANAHTAR).reset_index(drop=True)
    rng = np.random.default_rng(tohum)
    kisiler = sorted(g.kisi.unique())
    parcalar = []
    for sinif in ht.SINIFLAR:
        kota = dogru if sinif == ht.DOGRU else hata
        pay = {k: kota // len(kisiler) for k in kisiler}
        for k in [kisiler[i] for i in rng.permutation(len(kisiler))][:kota % len(kisiler)]:
            pay[k] += 1
        for k in kisiler:
            aday = g[(g.hata == sinif) & (g.kisi == k)]
            n = min(pay[k], len(aday))
            if n < pay[k]:
                print(f"UYARI: {sinif} × {k} tabakasında yalnızca {len(aday)} tekrar var; hepsi alındı.")
            parcalar.append(aday.iloc[np.sort(rng.choice(len(aday), size=n, replace=False))])
    o = pd.concat(parcalar, ignore_index=True)
    o.insert(0, "orneklem_no", range(1, len(o) + 1))
    return o[["orneklem_no"] + [s for s in SUTUNLAR if s in o.columns]]


def ozet(o: pd.DataFrame) -> pd.DataFrame:
    t = pd.crosstab(o.hata.map(ht.KISA_AD), o.kisi, margins=True, margins_name="toplam")
    t.index.name = "tabaka"
    return t.reset_index()


def main():
    ap = argparse.ArgumentParser(description="Deney 4 tabakalı örneklem")
    ap.add_argument("--dogru", type=int, default=50)
    ap.add_argument("--hata", type=int, default=20)
    ap.add_argument("--tohum", type=int, default=0)
    args = ap.parse_args()
    utf8_cikti()
    c = pd.read_csv(KAYNAK, encoding="utf-8-sig", keep_default_na=False)
    o = orneklem_sec(c, args.dogru, args.hata, args.tohum)
    oz = ozet(o)
    sonuclari_yaz({"orneklem": o, "orneklem_ozet": oz}, CIKTI, xlsx_adi="orneklem.xlsx")
    print(oz.to_string(index=False))
    print(f"\n{len(o)} tekrar (tohum {args.tohum}) → {CIKTI / 'orneklem.csv'}")


if __name__ == "__main__":
    main()
