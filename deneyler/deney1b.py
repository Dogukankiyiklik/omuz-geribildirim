"""
Deney 1b — genel bant ile kişiye özel bant.

Soru: Kalibrasyon kişiye özel olmak zorunda mı? Başkalarının doğru tekrarlarından kurulan bir bant
yeterli olur mu?

Her (kişi, kamera, yönelim) dizisi için dört koşul; iki bant türüyle (v1b: zaman bandı + çoklu
referans, v2: açı bandı), ikisinde de pay hariç:
  bant_yok    : Deney 1'deki "ham" skor (tekrar başına göre mutlak sapmanın %90 yüzdeliği, pay dahil
                tüm dizi; Deney 1 tanımı aynen). Bant türüne bağlı değildir, iki bant için aynı sayılar.
  genel_tum   : Aynı kamera ve yönelimde DİĞER 4 KİŞİNİN bütün doğru tekrarlarından (~20) tek bant.
                Test kişisinin hiçbir tekrarı modele girmez; kişinin bütün tekrarları (doğru ve hatalı)
                aynı modelle değerlendirilir → adil ve deterministik.
  genel_tek   : "Başka birinin kalibrasyonu": diğer kişilerden BİRİNİN doğru tekrarları (~5, kişiye
                özel modeldeki 4'e yakın sayı) ile bant; 4 kişinin her biri sırayla, E'lerin ortalaması.
  kisiye_ozel : Deney 1 v2'deki v1b / v2 aynen (adil model dahil; aynı kod çağrılır).

Kullanım:
    python -m deneyler.deney1b            # birkaç dakika
Çıktı: sonuclar/deney1b/
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path

import numpy as np
import pandas as pd

from cekirdek import veri
from cekirdek.aci_bandi import aci_bandi_hatasi, aci_bandi_modeli
from cekirdek.adil_model import ortalama_E
from cekirdek.bant import coklu_model_hatasi, coklu_referans_modelleri
from cekirdek.degerlendirme import ham_skor
from cekirdek.konsol import sonuclari_yaz, utf8_cikti
from deneyler import deney1_v2 as d2
from deneyler import tablolar as tb

OLCUTLER = d2.OLCUTLER
RAPOR_OLCUTLERI = ["YENI", "M33", "M39_F2"]
BANTLAR = ["v1b", "v2"]
KOSULLAR = ["bant_yok", "genel_tum", "genel_tek", "kisiye_ozel"]
KOSUL_ACIKLAMA = {
    "bant_yok": "bant yok (Deney 1 ham skor)",
    "genel_tum": "genel bant: diğer 4 kişinin tüm doğru tekrarları",
    "genel_tek": "genel bant: başka tek bir kişinin doğru tekrarları (4 kişi, ortalama)",
    "kisiye_ozel": "kişiye özel bant (Deney 1 v2)",
}
CIKTI = veri.KOK / "sonuclar" / "deney1b"


def _satir(t, bant, kosul, E):
    r = {"bant": bant, "kosul": kosul, "video": t.video, "kisi": t.kisi, "kamera": t.kamera,
         "yonelim": t.yonelim, "tekrar_no": t.tekrar_no, "satir": t.satir, "gorus": t.gorus,
         "hata": t.hata, "ek_hata": t.ek_hata}
    r.update({f"bant_{k}": E[k] for k in OLCUTLER})
    return r


class _Model:
    """Bir doğru tekrar kümesinden bant (v1b: çoklu referans modelleri, v2: açı bandı) ve E."""

    def __init__(self, bant, fl):
        self.bant = bant
        self.m = coklu_referans_modelleri(fl, OLCUTLER) if bant == "v1b" else aci_bandi_modeli(fl, OLCUTLER)

    def E(self, f):
        if self.bant == "v1b":
            return coklu_model_hatasi(self.m, f, OLCUTLER)
        return aci_bandi_hatasi(self.m, f, OLCUTLER)[0]


def genel_skorlar(tekrarlar, bant: str, ozl) -> pd.DataFrame:
    """genel_tum ve genel_tek koşulları (bir bant türü için)."""
    gruplar = veri.gruplara_ayir(tekrarlar)
    # her grubun doğru tekrarları (etiketli kareler)
    dogru_f = {g: [d2._kes(ozl[id(t)], t.etiketli) for t in ts if t.dogru] for g, ts in gruplar.items()}
    tek_model = {g: _Model(bant, fl) for g, fl in dogru_f.items() if len(fl) >= 3}
    kayit = []
    for (vid, kam, o), ts in gruplar.items():
        if sum(t.dogru for t in ts) < 3:   # kişiye özel koşulla aynı tekrar kümesi
            continue
        digerleri = [g for g in gruplar if g[1] == kam and g[2] == o and g[0] != vid]
        tum = _Model(bant, [f for g in digerleri for f in dogru_f[g]])
        tekler = [tek_model[g] for g in digerleri if g in tek_model]
        for t in ts:
            f = d2._kes(ozl[id(t)], t.etiketli)
            kayit.append(_satir(t, bant, "genel_tum", tum.E(f)))
            kayit.append(_satir(t, bant, "genel_tek", ortalama_E([m.E(f) for m in tekler], OLCUTLER)))
    return pd.DataFrame(kayit)


def ham_skorlar(tekrarlar, ozl) -> pd.DataFrame:
    kayit = []
    for _, ts in veri.gruplara_ayir(tekrarlar).items():
        if sum(t.dogru for t in ts) < 3:   # kişiye özel koşulla aynı tekrar kümesi
            continue
        for t in ts:
            H = ham_skor(ozl[id(t)], OLCUTLER)
            kayit += [_satir(t, b, "bant_yok", H) for b in BANTLAR]
    return pd.DataFrame(kayit)


def kisiye_ozel_skorlar(tekrarlar, bant, ozl) -> pd.DataFrame:
    df = d2.skor_tablosu(tekrarlar, bant, 0, ozl)
    df = df.rename(columns={"kosul": "bant"})
    df["kosul"] = "kisiye_ozel"
    return df[["bant", "kosul", "video", "kisi", "kamera", "yonelim", "tekrar_no", "satir", "gorus",
               "hata", "ek_hata"] + [f"bant_{k}" for k in OLCUTLER]]


FARKLAR = [(k, x, y) for k in RAPOR_OLCUTLERI
           for x, y in (("genel_tum", "kisiye_ozel"), ("genel_tek", "kisiye_ozel"), ("kisiye_ozel", "bant_yok"))]


def calistir(cikti=CIKTI, bootstrap_n=2000, yazdir=True, tekrarlar=None):
    t0 = time.time()
    cikti = Path(cikti)
    cikti.mkdir(parents=True, exist_ok=True)
    tekrarlar = veri.tekrarlari_yukle(1) if tekrarlar is None else tekrarlar
    ozl = d2.ozellik_tablosu(tekrarlar)
    parcalar = [ham_skorlar(tekrarlar, ozl)]
    for bant in BANTLAR:
        t1 = time.time()
        parcalar.append(genel_skorlar(tekrarlar, bant, ozl))
        parcalar.append(kisiye_ozel_skorlar(tekrarlar, bant, ozl))
        if yazdir:
            print(f"  {bant}: genel + kişiye özel {time.time() - t1:.1f} s")
    df = pd.concat(parcalar, ignore_index=True)
    df["kosul"] = pd.Categorical(df.kosul, categories=KOSULLAR)
    df = df.sort_values(["bant", "kosul", "video", "kamera", "yonelim", "satir"]).reset_index(drop=True)
    tablolar = {"tekrarlar": df,
                "ozet": tb.auc_ozeti(df, ["bant", "kosul"], OLCUTLER),
                "kisi_auc": tb.kisi_auc_genis(df, ["bant", "kosul"], OLCUTLER),
                "kisi_auc_onden_capraz": tb.kisi_auc_genis(df, ["bant", "kosul"], OLCUTLER, tb.ONDEN_CAPRAZ)}
    if bootstrap_n:
        t1 = time.time()
        bs = []
        for bant in BANTLAR:
            b = tb.fark_bootstrap(df[df.bant == bant], "kosul", FARKLAR, n=bootstrap_n)
            b.insert(0, "bant", bant)
            bs.append(b)
        tablolar["bootstrap"] = pd.concat(bs, ignore_index=True)
        if yazdir:
            print(f"  bootstrap ({bootstrap_n}): {time.time() - t1:.1f} s")
    sonuclari_yaz(tablolar, cikti)
    if yazdir:
        yazdir_ozet(tablolar)
        print(f"\nSüre: {time.time() - t0:.1f} s · Çıktı: {cikti}")
    return tablolar


def yazdir_ozet(tablolar):
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 30)
    oz = tablolar["ozet"]
    oz = oz[oz["ölçüt"].isin(RAPOR_OLCUTLERI)]
    print("\n1) AUC — koşul × ölçüt (tamamı ozet.csv):")
    sut = ["bant", "kosul", "ölçüt", "AUC silkme/doğru", f"AUC silkme/doğru ({tb.ONDEN_CAPRAZ})",
           "AUC silkme/diğer", f"AUC silkme/diğer ({tb.ONDEN_CAPRAZ})"] + [f"AUC {g}" for g in d2.GORUS_GRUPLARI] + ["kişi özeti"]
    print(oz[sut].round(3).to_string(index=False))
    print("\n2) Kişi bazlı AUC silkme/doğru (tüm görüşler), YENI:")
    k = tablolar["kisi_auc"]
    print(k[k["ölçüt"] == "YENI"].round(3).to_string(index=False))
    if "bootstrap" in tablolar:
        print("\n3) AUC farkları (silkme/doğru), kişi bazlı bootstrap, %95 GA:")
        for _, r in tablolar["bootstrap"].iterrows():
            print(f"   {r['bant']:4s} {r['görüş']:13s} {r['ölçüt']:7s} {r['fark']:26s} "
                  f"{r['nokta tahmini']:+.3f}   GA {r['GA %2,5']:+.3f} – {r['GA %97,5']:+.3f}")


def main():
    ap = argparse.ArgumentParser(description="Deney 1b: genel bant / kişiye özel bant")
    ap.add_argument("--cikti", default=str(CIKTI))
    ap.add_argument("--bootstrap", type=int, default=2000)
    args = ap.parse_args()
    utf8_cikti()
    print("Deney 1b — koşullar hesaplanıyor...")
    calistir(args.cikti, args.bootstrap)


if __name__ == "__main__":
    main()
