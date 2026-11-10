"""
Uygulamanın karar kuralını dışa aktarır.

Kural beş kişinin hepsinin önden + çapraz tekrarlarıyla kurulur. Prosedür LOSO'daki eğitim adımıyla
birebir aynıdır (deneyler/deney3.kararlar ile aynı çağrılar): ölçekleme (medyan, IQR), yönler,
on_kacma/kol_boyu seçimi, T ve şiddet eşikleri. Yöntem (dondurulmuş): açı bandı, yönlü. Değerler LOSO'daki beş değerle yan yana yazdırılır (sonuclar/kural_disa_aktar/loso_karsilastirma.csv).

Kullanım:
    python -m araclar.kural_disa_aktar        # birkaç saniye; önce python -m deneyler.deney2 çalışmış olmalı
Çıktı: modeller/kural_ex1.json, sonuclar/kural_disa_aktar/loso_karsilastirma.csv
"""
from __future__ import annotations

import argparse
import datetime as dt
import subprocess

import pandas as pd

from cekirdek import geribildirim as gb
from cekirdek import hata_turu as ht
from cekirdek import kural_dosyasi, veri
from cekirdek.konsol import sonuclari_yaz, utf8_cikti
from deneyler import deney2
from deneyler.tablolar import gorus_maskesi

MODEL = veri.KOK / "modeller" / "kural_ex1.json"
CIKTI = veri.KOK / "sonuclar" / "kural_disa_aktar"
YONLU = deney2.YONLU


def _commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=veri.KOK, text=True).strip()
    except Exception:
        return "bilinmiyor"


def kur(puan: pd.DataFrame):
    egitim = puan[gorus_maskesi(puan, deney2.AYAR_GORUSU)]
    kural = ht.esik_sec(egitim, YONLU, ht.EX1, ht.VARSAYILAN_KALDIRMA)
    esik = gb.siddet_esikleri(egitim, kural)
    return egitim, kural, esik


def karsilastirma(kural, esik, loso_esik: pd.DataFrame, loso_siddet: pd.DataFrame | None) -> pd.DataFrame:
    """Beş kişiyle kurulan değer + LOSO'daki beş değer (en küçük–en büyük)."""
    satir = []

    def ekle(ad, deger, loso_degerler):
        s = pd.Series(loso_degerler, dtype=float) if loso_degerler is not None else pd.Series(dtype=float)
        satir.append({"parametre": ad, "beş kişi (uygulama)": deger,
                      "LOSO en küçük": s.min() if len(s) else None, "LOSO en büyük": s.max() if len(s) else None,
                      "LOSO aralığında": (bool(s.min() <= deger <= s.max()) if len(s) and isinstance(deger, float)
                                          else None)})
    ekle("T", float(kural.T), loso_esik["T"])
    satir.append({"parametre": "öne kaçma ölçütü", "beş kişi (uygulama)": kural.on_olcut,
                  "LOSO en küçük": ", ".join(sorted(set(loso_esik["öne kaçma ölçütü"]))), "LOSO en büyük": None,
                  "LOSO aralığında": kural.on_olcut in set(loso_esik["öne kaçma ölçütü"])})
    for k in kural.esleme.values():
        satir.append({"parametre": f"yön {k}", "beş kişi (uygulama)": kural.yonler[k],
                      "LOSO en küçük": loso_esik[f"yön {k}"].min(), "LOSO en büyük": loso_esik[f"yön {k}"].max(),
                      "LOSO aralığında": bool(loso_esik[f"yön {k}"].min() <= kural.yonler[k] <= loso_esik[f"yön {k}"].max())})
        ekle(f"medyan {k}", float(kural.medyan[k]), loso_esik[f"medyan {k}"])
        ekle(f"ölçek {k}", float(kural.olcek[k]), loso_esik[f"ölçek {k}"])
    for h, (q1, q2) in esik.items():
        ls = loso_siddet[loso_siddet.hata == h] if loso_siddet is not None else None
        ekle(f"şiddet q1 {ht.KISA_AD[h]}", float(q1), None if ls is None else ls["q1 (%33,3)"])
        ekle(f"şiddet q2 {ht.KISA_AD[h]}", float(q2), None if ls is None else ls["q2 (%66,7)"])
    return pd.DataFrame(satir)


def main():
    ap = argparse.ArgumentParser(description="Uygulamanın karar kuralını dışa aktar")
    ap.add_argument("--model", default=str(MODEL))
    args = ap.parse_args()
    utf8_cikti()
    puan = deney2.puanlari_oku(deney2.CIKTI)
    egitim, kural, esik = kur(puan)
    bilgi = {"egzersiz": "ex1", "sistem": deney2.SISTEM_ADI, "kaldirma_surumu": kural.kaldirma_surumu,
             "olcu_surumu": gb.VARSAYILAN_OLCU, "egitim_gorusu": deney2.AYAR_GORUSU,
             "kisiler": sorted(egitim.kisi.unique().tolist()), "egitim_tekrar": int(len(egitim)),
             "commit": _commit(), "tarih": dt.datetime.now().isoformat(timespec="seconds")}
    kural_dosyasi.kaydet(kural, esik, args.model, bilgi)
    # denetim: dosyadan okunan kural aynı kararı veriyor
    k2, e2, _ = kural_dosyasi.yukle(args.model)
    assert (k2.karar(egitim) == kural.karar(egitim)).all() and e2 == esik

    loso = pd.read_csv(deney2.CIKTI / "esikler.csv", encoding="utf-8-sig")
    sid_yol = veri.KOK / "sonuclar" / "deney3" / "siddet_esikleri.csv"
    loso_sid = pd.read_csv(sid_yol, encoding="utf-8-sig") if sid_yol.exists() else None
    tablo = karsilastirma(kural, esik, loso, loso_sid)
    sonuclari_yaz({"loso_karsilastirma": tablo}, CIKTI)

    pd.set_option("display.width", 200)
    print(f"Kural: {args.model}")
    print(f"  eğitim: {bilgi['egitim_tekrar']} tekrar ({', '.join(bilgi['kisiler'])}; {bilgi['egitim_gorusu']}); "
          f"eğitim makro-F1 {kural.bilgi['egitim_makro_f1']:.4f}; commit {bilgi['commit']}")
    print("\nBeş kişiyle kurulan değerler ve LOSO'daki beş değer:")
    print(tablo.to_string(index=False, float_format=lambda x: f"{x:.4f}"))
    print(f"\nÇıktı: {CIKTI}")


if __name__ == "__main__":
    main()
