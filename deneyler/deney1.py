"""
Deney 1 — Omuz silkmesi olan bir tekrarı doğru tekrardan ayırabiliyor muyuz?

Dört omuz ölçüsü (satırlar) üç yolla puanlanır (sütunlar) ve her biri için AUC hesaplanır.

Ölçüler (cekirdek/ozellikler.py; hepsi gövde boyuna bölünür ya da açıdır):
  YENI   : sağ kulak ile sağ omuz arasındaki dikey mesafe (bizim önerimiz)
  M33    : sağ omzun iki omuz ortasına göre yüksekliği
  M39_F2 : sol omuz – sağ omuz – sağ kalça açısı (köşe sağ omuzda)
  M01    : iki omzun ortalama yüksekliğinin tekrar başına göre kalkışı

Puanlama yolları:
  ham          : bant yok. Tekrar kendi başlangıcıyla karşılaştırılır. Her karede ölçünün, tekrarın ilk
                 8 karesindeki (kol aşağıda) ortancadan mutlak sapması alınır; tekrarın puanı bu
                 sapmaların %90'lık dilimidir (cekirdek.degerlendirme.ham_skor). Başlangıç değeri
                 tekrarın önündeki dinlenme karelerinden geldiği için bütün kareler kullanılır.
  genel        : açı bandı, ama aynı kamera ve yönelimdeki DİĞER 4 KİŞİNİN bütün doğru tekrarlarından.
                 Test kişisinin hiçbir tekrarı banda girmez.
  kisiye_ozel  : açı bandı, kişinin kendi doğru tekrarlarından (uygulamanın yöntemi).
                 Doğru tekrar: birini-dışarıda-bırak (kendisi banda girmez).
                 Hatalı tekrar: adil model. Her doğru tekrar sırayla dışarıda bırakılır, n bant kurulur,
                 puanların ortalaması alınır. Böylece hatalı tekrar da (n−1) tekrarlık bantla ölçülür.

Açı bandı (cekirdek/aci_bandi.py): kol açısının her 5°'lik kutusu için (kaldırma ve indirme ayrı)
ortalama μ ve genişlik τ. Bant puanı E: her kare kendi kutusunun bandıyla karşılaştırılır; bant
içindeyse 0, dışındaysa (sapma − τ)/τ (en fazla 1); E bu kare puanlarının ortalaması. Açı bandında
yalnızca veri setinin etiketlediği tekrar kareleri kullanılır.

Kullanım:
    python -m deneyler.deney1            # ~20 sn
Çıktı: sonuclar/deney1/{ozet.csv, kisi_auc.csv, kisi_auc_onden_capraz.csv, tekrarlar.csv, sonuclar.xlsx}
  Not: tablolarda puan sütunları, ham dahil, "bant_<ölçü>" adını taşır (ortak tablo kodu bu adı bekler).
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path

import pandas as pd

from cekirdek import veri
from cekirdek.aci_bandi import aci_bandi_hatasi, aci_bandi_modeli
from cekirdek.adil_model import adil_ortalama_hata
from cekirdek.degerlendirme import ham_skor
from cekirdek.konsol import sonuclari_yaz, utf8_cikti
from cekirdek.ozellikler import ozellikler
from deneyler import tablolar as tb
from deneyler.tablolar import maskeler

OLCUTLER = ["YENI", "M33", "M39_F2", "M01"]
KOSULLAR = ["ham", "genel", "kisiye_ozel"]
KOSUL_ACIKLAMA = {
    "ham": "ham ölçü (bant yok)",
    "genel": "genel bant: diğer 4 kişinin doğru tekrarları",
    "kisiye_ozel": "kişiye özel açı bandı",
}
EN_AZ_DOGRU = 3   # bir çekimde bant kurmak için gereken en az doğru tekrar
CIKTI = veri.KOK / "sonuclar" / "deney1"


# ---------------------------------------------------------------- ölçüler
def ozellik_tablosu(tekrarlar, olcutler=OLCUTLER) -> dict:
    """Her tekrar için bütün dizide (dinlenme kareleri dahil) kol açısı ve ölçüler; bir kez hesaplanır."""
    return {id(t): ozellikler(t.dizi, olcutler) for t in tekrarlar}


def _kes(f: dict, s: slice) -> dict:
    """Ölçü eğrilerinden yalnızca etiketli tekrar kareleri."""
    return {k: v[s] for k, v in f.items()}


def _cekimler(tekrarlar) -> dict:
    """(kişi videosu, kamera, yönelim) → tekrarlar; yalnızca en az EN_AZ_DOGRU doğru tekrarı olanlar."""
    return {g: ts for g, ts in veri.gruplara_ayir(tekrarlar).items() if sum(t.dogru for t in ts) >= EN_AZ_DOGRU}


# ---------------------------------------------------------------- kişiye özel açı bandı
def kisiye_ozel_degerlendirmeleri(tekrarlar, ozl, olcutler=OLCUTLER):
    """Her tekrar için (tekrar, E): kişinin aynı çekimdeki doğru tekrarlarından kurulan açı bandıyla."""
    for _, grup in _cekimler(tekrarlar).items():
        tl = [(t, _kes(ozl[id(t)], t.etiketli)) for t in grup]
        dogrular = [f for t, f in tl if t.dogru]
        for t, f in tl:
            if t.dogru:   # birini-dışarıda-bırak: tekrarın kendisi banda girmez
                model = aci_bandi_modeli([u for u in dogrular if u is not f], olcutler)
                yield t, aci_bandi_hatasi(model, f, olcutler)[0]
            else:         # adil model: n adet (n−1)'li bandın E ortalaması
                def hata(alt, f=f):
                    return aci_bandi_hatasi(aci_bandi_modeli(alt, olcutler), f, olcutler)
                yield t, adil_ortalama_hata(dogrular, hata, olcutler)[0]


# ---------------------------------------------------------------- üç puanlama yolu
def _satir(t, kosul, puan) -> dict:
    r = {"kosul": kosul, "video": t.video, "kisi": t.kisi, "kamera": t.kamera, "yonelim": t.yonelim,
         "tekrar_no": t.tekrar_no, "satir": t.satir, "gorus": t.gorus, "hata": t.hata, "ek_hata": t.ek_hata}
    r.update({f"bant_{k}": puan[k] for k in OLCUTLER})
    return r


def ham_puanlar(tekrarlar, ozl) -> list[dict]:
    return [_satir(t, "ham", ham_skor(ozl[id(t)], OLCUTLER))
            for ts in _cekimler(tekrarlar).values() for t in ts]


def genel_puanlar(tekrarlar, ozl) -> list[dict]:
    gruplar = veri.gruplara_ayir(tekrarlar)
    dogru_f = {g: [_kes(ozl[id(t)], t.etiketli) for t in ts if t.dogru] for g, ts in gruplar.items()}
    kayit = []
    for (vid, kam, o), ts in _cekimler(tekrarlar).items():
        # aynı kamera ve yönelim, başka kişiler: test kişisinin hiçbir tekrarı banda girmez
        digerleri = [g for g in gruplar if g[1] == kam and g[2] == o and g[0] != vid]
        model = aci_bandi_modeli([f for g in digerleri for f in dogru_f[g]], OLCUTLER)
        for t in ts:
            E = aci_bandi_hatasi(model, _kes(ozl[id(t)], t.etiketli), OLCUTLER)[0]
            kayit.append(_satir(t, "genel", E))
    return kayit


def kisiye_ozel_puanlar(tekrarlar, ozl) -> list[dict]:
    return [_satir(t, "kisiye_ozel", E) for t, E in kisiye_ozel_degerlendirmeleri(tekrarlar, ozl)]


# ---------------------------------------------------------------- çalıştır
def calistir(cikti=CIKTI, yazdir=True, tekrarlar=None) -> dict:
    t0 = time.time()
    cikti = Path(cikti)
    cikti.mkdir(parents=True, exist_ok=True)
    tekrarlar = veri.tekrarlari_yukle(1) if tekrarlar is None else tekrarlar
    ozl = ozellik_tablosu(tekrarlar)
    kayit = []
    for kosul, f in (("ham", ham_puanlar), ("genel", genel_puanlar), ("kisiye_ozel", kisiye_ozel_puanlar)):
        t1 = time.time()
        kayit += f(tekrarlar, ozl)
        if yazdir:
            print(f"  {KOSUL_ACIKLAMA[kosul]}: {time.time() - t1:.1f} s")
    df = pd.DataFrame(kayit)
    df["kosul"] = pd.Categorical(df.kosul, categories=KOSULLAR)
    df = df.sort_values(["kosul", "video", "kamera", "yonelim", "satir"]).reset_index(drop=True)
    ozet = tb.auc_ozeti(df, ["kosul"], OLCUTLER)
    tablolar = {"tekrarlar": df, "ozet": ozet,
                "kisi_auc": tb.kisi_auc_genis(df, ["kosul"], OLCUTLER),
                "kisi_auc_onden_capraz": tb.kisi_auc_genis(df, ["kosul"], OLCUTLER, tb.ONDEN_CAPRAZ)}
    sonuclari_yaz(tablolar, cikti)
    if yazdir:
        yazdir_ozet(tablolar)
        print(f"\nSüre: {time.time() - t0:.1f} s · Çıktı: {cikti}")
    return tablolar


def yazdir_ozet(tablolar):
    df, oz = tablolar["tekrarlar"], tablolar["ozet"]
    s, d, o = maskeler(df[df.kosul == "ham"])
    print(f"\nTekrar sayıları (3 kamera dahil): silkme = {s.sum()}, doğru = {d.sum()}, diğer hatalar = {o.sum()}")
    for sutun, baslik in (("AUC silkme/doğru", "tüm görüşler"),
                          (f"AUC silkme/doğru ({tb.ONDEN_CAPRAZ})", "önden + çapraz")):
        print(f"\nAUC silkme/doğru, {baslik} (satır: ölçü, sütun: puanlama):")
        t = oz.pivot_table(index="ölçüt", columns="kosul", values=sutun, observed=True).loc[OLCUTLER, KOSULLAR]
        print(t.round(3).to_string())
    print("\nKişi başına AUC silkme/doğru, YENI (tüm görüşler):")
    k = tablolar["kisi_auc"]
    print(k[k["ölçüt"] == "YENI"].round(3).to_string(index=False))


def main():
    ap = argparse.ArgumentParser(description="Deney 1: ham ölçü / genel bant / kişiye özel açı bandı")
    ap.add_argument("--cikti", default=str(CIKTI))
    args = ap.parse_args()
    utf8_cikti()
    print("Deney 1 — puanlar hesaplanıyor...")
    calistir(args.cikti)


if __name__ == "__main__":
    main()
