"""
Deney 4 (Adım 8) — LLM ile kural tabanlı geri bildirimin karşılaştırması (Güncelleme 09, Karar 36).

Tasarım ADIM_08.md "Önceden belirlenenler" bölümünde, ilk API isteğinden önce commit'lendi:
  A : Deney 3'ün hasta cümlesi, sağlam ölçüyle (yeni üretim yok; cumleler_saglam.csv ile birebir aynı olduğu denetlenir).
  B : LLM + sapma kodu (JSON): karar, en fazla 2 hata (hata, taraf, faz, yön, 5°'ye yuvarlanmış sayılar).
  C : LLM + ham özet (M21 tarzı): 5 ölçütün min/maks/ort + normal aralığın özeti, tepe ve kalibrasyon tepe medyanı;
      karar ve sapma kodu verilmez.
  Üç koşul da hasta cümlesi üslubunda (Karar 28); sıfır atış; istemler deneyler/istemler/.
  Gemini ücretsiz katmanı, temperature 0, düşünme kapalı (destekleniyorsa); koşul başına tek istek; yanıtlar
  önbellekte (sonuclar/deney4/onbellek.jsonl), yeniden çalıştırmada ağa gidilmez.

Kullanım (işlem sırası):
    python -m deneyler.deney4 hazirla                   # ağ yok, ~1 dk: girdiler.csv (A metni, B ve C girdileri)
    python -m deneyler.deney4 modeller                  # anahtarın erişebildiği Gemini modelleri (kota harcamaz)
    python -m deneyler.deney4 pilot --model gemini-2.5-flash      # 5 tekrar × B, C = 10 istek (raporlanmaz)
    python -m deneyler.deney4 calistir --model gemini-2.5-flash   # 150 × B, C = 300 istek; kesilirse aynı komut
    python -m deneyler.deney4 raporla                   # ağ yok: kayıtlı yanıtlardan tabloları yeniden yazar
    python -m deneyler.deney4 elle-uret                 # 45 cümlelik körlemesine etiketleme dosyası
    python -m deneyler.deney4 elle-degerlendir          # kullanıcının etiketleri ile çıkarıcının uyumu
    python -m deneyler.deney4 kaldirma-uret             # Karar 42: "kaldır" kalıplı bütün cümleler, körlemesine
    python -m deneyler.deney4 kaldirma-degerlendir      # Karar 42: duyarlılık tablosu (birincil tablo değişmez)
    python -m deneyler.deney4 kaldirma-degerlendir --sahte   # etiket yerine çıkarıcının kendisi: farklar 0 olmalı
Çıktı: sonuclar/deney4/ (pilot: sonuclar/deney4/pilot/)
"""
from __future__ import annotations

import argparse
import json
import math
import re
import time
from pathlib import Path

import numpy as np
import pandas as pd

from cekirdek import geribildirim as gb
from cekirdek import hata_turu as ht
from cekirdek import llm
from cekirdek import veri
from cekirdek.degerlendirme import guven_araligi, kisi_bootstrap
from cekirdek.konsol import sonuclari_yaz, utf8_cikti
from cekirdek.metin_cozumleyici import cozumle
from deneyler import deney3
from deneyler.deney4_orneklem import ANAHTAR
from deneyler.tablolar import ONDEN_CAPRAZ, gorus_maskesi

CIKTI = veri.KOK / "sonuclar" / "deney4"
ISTEMLER = veri.KOK / "deneyler" / "istemler"
ORNEKLEM = CIKTI / "orneklem.csv"
SAGLAM = veri.KOK / "sonuclar" / "deney3" / "cumleler_saglam.csv"
VARSAYILAN_MODEL = "gemini-2.5-flash"
LLM_KOSULLARI = ("B", "C")
KOSULLAR = ("A",) + LLM_KOSULLARI
TOHUM_ORNEKLEM, TOHUM_PILOT, TOHUM_ELLE, TOHUM_BOOTSTRAP = 0, 1, 2, 1
PILOT_SAYISI, ELLE_KOSUL_BASINA = 5, 15

# ---------------------------------------------------------------- B girdisi (sapma kodu → JSON)
HATA_ADI = {ht.SILKME: "omuz kalkması", "ERR_HEAD_TO_SIDE": "baş eğme", "ERR_ARM_FORWARD": "kolun öne kaçması",
            "ERR_BENT_ARM": "dirsek bükme", "ERR_LOW_ABDUCTION": "yetersiz kaldırma"}
# (hata, yön ≥ 0): ne olduğunun kısa tarifi (cekirdek/geribildirim.hasta_cumlesi'nin yön dallarıyla aynı anlam)
YON_TARIFI = {(ht.SILKME, False): "sağ omuz kulağa doğru kalktı", (ht.SILKME, True): "sağ omuz normalden aşağıda kaldı",
              ("ERR_HEAD_TO_SIDE", True): "baş yana eğildi", ("ERR_HEAD_TO_SIDE", False): "başın duruşu normalden farklıydı",
              ("ERR_ARM_FORWARD", False): "kol öne kaçtı", ("ERR_ARM_FORWARD", True): "kol vücut hizasından çıktı",
              ("ERR_BENT_ARM", False): "dirsek büküldü", ("ERR_BENT_ARM", True): "dirsek normalden fazla açıldı",
              ("ERR_LOW_ABDUCTION", True): "kol normalden az kaldırıldı",
              ("ERR_LOW_ABDUCTION", False): "kol normalden fazla kaldırıldı"}
OLCU_ADI = {ht.SILKME: "omuz çizgisinin gövdeye göre eğimi (pozitif = sağ omuz yukarı)",
            "ERR_HEAD_TO_SIDE": "baş ile gövde arasındaki açı",
            "ERR_BENT_ARM": "dirsek açısı (180 = düz kol)",
            "ERR_LOW_ABDUCTION": "kolun çıktığı en yüksek açı"}


def b_sayilari(k: gb.SapmaKodu) -> dict | None:
    """Hasta cümlesinin söyleyeceği sayılar (gb.hasta_cumlesi ile aynı kurallar); sayı söylenmeyecekse None."""
    h, yukari = k.hata, k.yon >= 0
    if h == ht.SILKME:
        o, b = gb.yuvarla5(k.ek_olcu), gb.yuvarla5(k.ek_beklenen)
        e = gb._fark5(k.ek_olcu, k.ek_beklenen)
        d = None if e is None else (-e if yukari else e)
    elif h == "ERR_HEAD_TO_SIDE":
        o, b = gb.yuvarla5(k.olcu), gb.yuvarla5(k.beklenen)
        d = gb._fark5(k.olcu, k.beklenen) if yukari else None
    elif h == "ERR_BENT_ARM":
        o, b = gb.yuvarla5(k.olcu), gb.yuvarla5(k.beklenen)
        d = gb._fark5(k.olcu, k.beklenen) if yukari else gb._fark5(k.beklenen, k.olcu)
    elif h == "ERR_LOW_ABDUCTION":
        o, b = gb.yuvarla5(k.olcu), gb.yuvarla5(k.beklenen)
        d = gb._fark5(k.beklenen, k.olcu) if yukari else gb._fark5(k.olcu, k.beklenen)
    else:                     # öne kaçma: sayı yok (Karar 28)
        return None
    if d is None or d <= 0:
        return None
    return {"olcu_adi": OLCU_ADI[h], "olcu": o, "beklenen": b, "fark": d, "birim": "derece"}


def b_girdisi(kodlar: list[gb.SapmaKodu], tepe: float) -> dict:
    if not kodlar:
        return {"karar": "doğru", "tepe_kol_acisi": gb.yuvarla5(tepe)}
    hatalar = []
    for k in kodlar:
        e = {"hata": HATA_ADI[k.hata], "taraf": k.taraf, "faz": gb.FAZ_ADLARI.get(k.faz, ""),
             "yon": YON_TARIFI[(k.hata, k.yon >= 0)]}
        s = b_sayilari(k)
        if s:
            e["sayilar"] = s
        hatalar.append(e)
    return {"karar": "hatalı", "hatalar": hatalar}


# ---------------------------------------------------------------- C girdisi (ham özet)
C_OLCUTLER = {"YENI": ("kulak_omuz", "gövde boyuna oran"), "bas": ("bas_govde_acisi", "derece"),
              "on_kacma": ("kol_govde_acisi", "derece"), "kol_boyu": ("kol_boyu", "gövde boyuna oran"),
              "dirsek": ("dirsek_acisi", "derece")}


def _sayi(x: float, birim: str):
    return round(float(x), 3 if birim != "derece" else 1)


def c_girdisi(a: dict) -> dict:
    """
    a: deney3.ayrintilar kaydı. Geçerli kareler = model ortalaması μ'nün tanımlı olduğu kareler (Karar 7 ortalaması;
    doğru tekrarda kendisinin dışarıda bırakıldığı tek model).
    """
    o = {}
    for k, (ad, birim) in C_OLCUTLER.items():
        mu, tau, h = np.asarray(a["mu"][k], float), np.asarray(a["tau"][k], float), np.asarray(a["deger"][k], float)
        g = np.isfinite(mu) & np.isfinite(tau) & np.isfinite(h)
        if not g.any():
            o[ad] = {"birim": birim, "hasta": None, "normal_aralik": None}
            continue
        o[ad] = {"birim": birim,
                 "hasta": {"en_kucuk": _sayi(h[g].min(), birim), "en_buyuk": _sayi(h[g].max(), birim),
                           "ortalama": _sayi(h[g].mean(), birim)},
                 "normal_aralik": {"alt_sinir_en_kucuk": _sayi((mu - tau)[g].min(), birim),
                                   "ust_sinir_en_buyuk": _sayi((mu + tau)[g].max(), birim),
                                   "orta_ortalama": _sayi(mu[g].mean(), birim)}}
    return {"olcutler": o, "tepe_kol_acisi": _sayi(a["tepe"], "derece"),
            "kalibrasyon_tepe_medyani": _sayi(a["beklenen_tepe"], "derece")}


# ---------------------------------------------------------------- istemler
def istemleri_oku(klasor: Path = ISTEMLER) -> dict[str, dict[str, str]]:
    ortak = (Path(klasor) / "ortak_uslup.txt").read_text(encoding="utf-8").strip()
    cikti = {}
    for k in LLM_KOSULLARI:
        sistem = (Path(klasor) / f"{k}_sistem.txt").read_text(encoding="utf-8").strip()
        cikti[k] = {"sistem": sistem.replace("{ortak_uslup}", ortak),
                    "kullanici": (Path(klasor) / f"{k}_kullanici.txt").read_text(encoding="utf-8").strip()}
    return cikti


def json_metni(d: dict) -> str:
    return json.dumps(d, ensure_ascii=False, indent=2)


def istek(kosul: str, girdi: dict, istemler: dict, model: str, dusunme) -> llm.Istek:
    i = istemler[kosul]
    return llm.Istek(kullanici=i["kullanici"].replace("{girdi}", json_metni(girdi)), model=model,
                     sistem=i["sistem"], sicaklik=0.0, dusunme=dusunme)


def dusunme_ayari(model: str, secim: str = "otomatik"):
    """'otomatik': gemini-2.5 modellerinde thinkingBudget = 0; diğerlerinde modelin varsayılanı (None)."""
    if secim == "otomatik":
        return 0 if model.startswith("gemini-2.5") else None
    if secim == "varsayilan":
        return None
    return int(secim) if secim.lstrip("-").isdigit() else secim


# ---------------------------------------------------------------- hazırlık (ağ yok)
def _anahtar(r) -> tuple:
    return (r.video, r.kamera, int(r.yonelim), int(r.satir))


def tekrar_secimi(orneklem: pd.DataFrame) -> pd.DataFrame:
    return orneklem[ANAHTAR + ["orneklem_no", "kisi", "tekrar_no", "gorus", "gorus_grubu", "hata", "ek_hata"]]


def pilot_secimi(tohum: int = TOHUM_PILOT, n: int = PILOT_SAYISI) -> pd.DataFrame:
    """Örneklem dışından, aynı tabakalardan (sınıf × kişi; önden + çapraz) n tabaka seçilir, her birinden 1 tekrar."""
    c = pd.read_csv(deney3.CIKTI / "cumleler.csv", encoding="utf-8-sig", keep_default_na=False)
    o = pd.read_csv(ORNEKLEM, encoding="utf-8-sig", keep_default_na=False)
    g = c[gorus_maskesi(c, ONDEN_CAPRAZ)].sort_values(ANAHTAR).reset_index(drop=True)
    secili = set(map(_anahtar, o.itertuples()))
    g = g[[_anahtar(r) not in secili for r in g.itertuples()]].reset_index(drop=True)
    rng = np.random.default_rng(tohum)
    tabakalar = sorted({(h, k) for h, k in zip(g.hata, g.kisi)})
    secim = [tabakalar[i] for i in sorted(rng.choice(len(tabakalar), size=n, replace=False))]
    parca = []
    for h, k in secim:
        aday = g[(g.hata == h) & (g.kisi == k)]
        parca.append(aday.iloc[[int(rng.integers(len(aday)))]])
    p = pd.concat(parca, ignore_index=True)
    p.insert(0, "orneklem_no", [f"p{i}" for i in range(1, len(p) + 1)])
    return p


def girdileri_hazirla(secim: pd.DataFrame, yazdir: bool = True) -> pd.DataFrame:
    """Her tekrar için A metni (Deney 3, sağlam ölçü) ve B, C girdileri. Kararlar Deney 3 ile aynı kod."""
    t0 = time.time()
    puan = deney3.deney2.puanlari_oku(deney3.deney2.CIKTI)[deney3.BANT]
    p, kurallar, _ = deney3.kararlar(puan)
    p = p.set_index(ANAHTAR)
    ayr = deney3.ayrintilar(veri.tekrarlari_yukle(1))
    saglam = pd.read_csv(SAGLAM, encoding="utf-8-sig", keep_default_na=False).set_index(ANAHTAR)
    kayit = []
    for r in secim.itertuples():
        anahtar = _anahtar(r)
        q, a = p.loc[anahtar], ayr[anahtar]
        kodlar = [deney3.kod_uret(q[f"soylenen{i}"], q[f"siddet{i}"], kurallar[r.kisi], a, "saglam")
                  for i in (1, 2) if q[f"soylenen{i}"] and q[f"soylenen{i}"] != ht.DOGRU]
        a_metni = gb.hasta_geri_bildirimi(kodlar, a["tepe"], int(r.satir), deney3.TOHUM)
        assert a_metni == saglam.loc[anahtar, "hasta_cumlesi"], anahtar   # A = Deney 3 (sağlam), birebir
        kayit.append({"orneklem_no": r.orneklem_no, **dict(zip(ANAHTAR, anahtar)), "kisi": r.kisi,
                      "tekrar_no": r.tekrar_no, "gorus": r.gorus, "gorus_grubu": r.gorus_grubu, "hata": r.hata,
                      "ek_hata": r.ek_hata, "sistem_hatalari": "|".join(k.hata for k in kodlar),
                      "A_metin": a_metni, "B_girdi": json_metni(b_girdisi(kodlar, a["tepe"])),
                      "C_girdi": json_metni(c_girdisi(a))})
    if yazdir:
        print(f"  girdiler: {len(kayit)} tekrar ({time.time() - t0:.1f} s); A metni Deney 3 (sağlam) ile birebir aynı")
    return pd.DataFrame(kayit)


def girdileri_oku(klasor: Path) -> pd.DataFrame:
    return pd.read_csv(Path(klasor) / "girdiler.csv", encoding="utf-8-sig", keep_default_na=False)


# ---------------------------------------------------------------- LLM çalıştırma
def calistir_llm(girdiler: pd.DataFrame, istemci: llm.LLMIstemcisi, model: str, dusunme, istemler: dict,
                 yazdir: bool = True) -> tuple[pd.DataFrame, str]:
    """Her tekrar × (B, C) için tek istek. Kalıcı hata ya da kota bitince durur; o ana kadarki yanıtlar döner."""
    kayit, durum = [], "tamam"
    toplam = len(girdiler) * len(LLM_KOSULLARI)
    for r in girdiler.itertuples():
        for k in LLM_KOSULLARI:
            ist = istek(k, json.loads(getattr(r, f"{k}_girdi")), istemler, model, dusunme)
            try:
                y = istemci.sor(ist)
            except llm.LLMHatasi as e:
                durum = f"durdu: {e}"
                if yazdir:
                    print(f"\n  DURDU ({len(kayit)}/{toplam} yanıt): {e}\n  Kota bitmiş olabilir. Önbellek korunur; "
                          "aynı komut daha sonra kaldığı yerden devam eder.")
                return pd.DataFrame(kayit), durum
            kayit.append({"orneklem_no": r.orneklem_no, "kosul": k, "metin": y.metin, "bitis_nedeni": y.bitis_nedeni,
                          "onbellekten": y.onbellekten, "deneme": y.deneme, "model": model,
                          "dusunme": "" if dusunme is None else dusunme})
            if yazdir and (len(kayit) % 10 == 0 or len(kayit) == toplam):
                print(f"  {len(kayit)}/{toplam} yanıt (ağ isteği: {istemci.ag_istegi})")
    return pd.DataFrame(kayit), durum


# ---------------------------------------------------------------- metrikler
_SAYI = re.compile(r"(?<![\w])-?\d+(?:[.,]\d+)?")


def sayilar(metin: str) -> list[float]:
    """Metindeki rakamla yazılmış sayılar (Türkçe ondalık virgülü dahil). Yazıyla yazılanlar yakalanmaz."""
    return [float(m.group().replace(",", ".")) for m in _SAYI.finditer(str(metin))]


def _json_sayilari(d) -> list[float]:
    if isinstance(d, bool) or d is None:
        return []
    if isinstance(d, (int, float)):
        return [float(d)]
    if isinstance(d, dict):
        return [x for v in d.values() for x in _json_sayilari(v)]
    if isinstance(d, list):
        return [x for v in d for x in _json_sayilari(v)]
    return []


def izinli_b(girdi: dict) -> set[float]:
    return set(_json_sayilari(girdi))


def izinli_c(girdi: dict) -> set[float]:
    """Girdideki sayılar, 1'e ve 5'e yuvarlanmışları, aynı ölçüt içindeki ikili farklar (onlar da yuvarlanmış)."""
    gruplar = [_json_sayilari(v) for v in girdi.get("olcutler", {}).values()]
    gruplar.append(_json_sayilari({k: girdi.get(k) for k in ("tepe_kol_acisi", "kalibrasyon_tepe_medyani")}))
    taban = set(_json_sayilari(girdi))
    for g in gruplar:
        taban |= {abs(a - b) for i, a in enumerate(g) for b in g[i + 1:]}
    return taban | {float(gb.yuvarla(x)) for x in taban} | {float(gb.yuvarla5(x)) for x in taban}


def sayi_uydurdu(metin: str, izinli: set[float], tolerans: float) -> bool:
    return any(not any(abs(x - a) <= tolerans + 1e-9 for a in izinli) for x in sayilar(metin))


SAYI_TOLERANSI = {"A": 0.0, "B": 0.0, "C": 1.0}
# "yüzde" kelimesi (yüzde 20, yüzdesi); "bu yüzden" sayılmaz (ilk sürümdeki kod hatası, ADIM_08)
_USLUP = re.compile(r"%|\byüzde(?!n\b)|gövde boy", re.IGNORECASE)


def _liste(s) -> list[str]:
    return [x for x in str(s).split("|") if x]


def uzun_tablo(girdiler: pd.DataFrame, yanitlar: pd.DataFrame) -> pd.DataFrame:
    """Koşul başına bir satır: metin, çıkarılan liste, girdinin hata listesi, sayı uydurma ve üslup bayrakları."""
    g = girdiler.set_index("orneklem_no")
    satir = []
    for r in g.itertuples():
        satir.append({"orneklem_no": r.Index, "kosul": "A", "metin": r.A_metin})
    for r in yanitlar.itertuples():
        satir.append({"orneklem_no": r.orneklem_no, "kosul": r.kosul, "metin": r.metin})
    u = pd.DataFrame(satir)
    u = u.join(g[["kisi", "hata", "ek_hata", "gorus", "gorus_grubu", "sistem_hatalari", "B_girdi", "C_girdi"]],
               on="orneklem_no")
    u["cikarilan"] = u.metin.map(lambda m: "|".join(cozumle(m)))
    u["kelime"] = u.metin.map(lambda m: len(str(m).split()))
    uydur = []
    for r in u.itertuples():
        izin = izinli_c(json.loads(r.C_girdi)) if r.kosul == "C" else izinli_b(json.loads(r.B_girdi))
        uydur.append(sayi_uydurdu(r.metin, izin, SAYI_TOLERANSI[r.kosul]))
    u["sayi_uydurdu"] = uydur
    u["sayi_var"] = u.metin.map(lambda m: bool(sayilar(m)))
    u["uslup_yuzde"] = u.metin.map(lambda m: bool(_USLUP.search(str(m))))
    return u.drop(columns=["B_girdi", "C_girdi"])


METRIKLER = ["katı: ilk söylenen = birincil /100", "ilk iki: birincil söylendi /100",
             "doğrularda gereksiz uyarı /100"]


def metrik_satiri(g: pd.DataFrame) -> dict:
    L = g.cikarilan.map(_liste)
    S = g.sistem_hatalari.map(_liste)
    hatali = (g.hata != ht.DOGRU).to_numpy()
    d = ~hatali
    ilk = np.array([l[0] if l else ht.DOGRU for l in L], dtype=object)
    bos = np.array([not l for l in L])

    def y(m, mask=None):
        m = np.asarray(m, bool)
        mask = np.ones(len(m), bool) if mask is None else mask
        return 100 * float(m[mask].mean()) if mask.any() else np.nan
    return {"tekrar": len(g), "hatalı tekrar": int(hatali.sum()), "doğru tekrar": int(d.sum()),
            "katı: ilk söylenen = birincil /100": y(ilk == g.hata.to_numpy(), hatali),
            "ilk iki: birincil söylendi /100": y([b in l for b, l in zip(g.hata, L)], hatali),
            "hatalılarda olumlu cümle /100": y(bos, hatali),
            "doğrularda gereksiz uyarı /100": y(~bos, d),
            "sadakat: liste = girdi /100": y([l == s for l, s in zip(L, S)]),
            "sadakat: küme = girdi /100": y([set(l) == set(s) for l, s in zip(L, S)]),
            "eklenen hata /100": y([bool(set(l) - set(s)) for l, s in zip(L, S)]),
            "atlanan hata /100": y([bool(set(s) - set(l)) for l, s in zip(L, S)]),
            "sayı uydurdu /100": y(g.sayi_uydurdu),
            "sayı içeren /100": y(g.sayi_var),
            "üslup: %, yüzde, gövde boy /100": y(g.uslup_yuzde),
            "üslup: 2'den fazla hata /100": y([len(l) > 2 for l in L]),
            "ortalama kelime": float(g.kelime.mean())}


def tablolar(u: pd.DataFrame, bootstrap_n: int = 2000, tohum: int = TOHUM_BOOTSTRAP) -> dict[str, pd.DataFrame]:
    kosullar = [k for k in KOSULLAR if k in set(u.kosul)]
    ozet = pd.DataFrame([{"koşul": k, **metrik_satiri(u[u.kosul == k])} for k in kosullar])
    kisi = pd.DataFrame([{"koşul": k, "kisi": p, **metrik_satiri(g)}
                         for k in kosullar for p, g in u[u.kosul == k].groupby("kisi")])
    sinif = pd.DataFrame([{"koşul": k, "gerçek sınıf": ht.KISA_AD[h], **metrik_satiri(g)}
                          for k in kosullar for h in ht.SINIFLAR for g in [u[(u.kosul == k) & (u.hata == h)]]
                          if len(g)])
    T = {"ozet": ozet, "kisi": kisi, "sinif": sinif}
    if bootstrap_n and {"A"} < set(kosullar):
        T["bootstrap"] = bootstrap_farklari(u, [k for k in kosullar if k != "A"], bootstrap_n, tohum)
    return T


def bootstrap_farklari(u: pd.DataFrame, karsi: list[str], n: int, tohum: int,
                       metrikler: list[str] | None = None) -> pd.DataFrame:
    """Kişi bazlı bootstrap: koşul − A eşleştirilmiş farkları (aynı tekrarlar, aynı yeniden örnekleme)."""
    metrikler = METRIKLER if metrikler is None else metrikler

    def ist(b):
        m = {k: metrik_satiri(b[b.kosul == k]) for k in ["A"] + karsi}
        return {f"{k} − A|{a}": m[k][a] - m["A"][a] for k in karsi for a in metrikler}
    nokta = ist(u)
    bs = kisi_bootstrap(u, ist, n=n, tohum=tohum)
    satir = []
    for c in bs.columns:
        alt, ust = guven_araligi(bs[c].dropna())
        fark, metrik = c.split("|")
        satir.append({"fark": fark, "metrik": metrik, "nokta tahmini": nokta[c], "GA %2,5": alt, "GA %97,5": ust})
    return pd.DataFrame(satir)


def ornekler_md(u: pd.DataFrame, yol: Path, n: int = 5, tohum: int = 0) -> None:
    """Her koşuldan 5 örnek: aynı 5 tekrar (sınıflardan dengeli, tohum 0), üç koşul yan yana."""
    rng = np.random.default_rng(tohum)
    nolar = sorted(u.orneklem_no.unique(), key=str)
    sinif = u.drop_duplicates("orneklem_no").set_index("orneklem_no").hata
    secim = []
    for h in [ht.DOGRU] + [x for x in rng.permutation(ht.HATALAR)][: n - 1]:
        aday = [x for x in nolar if sinif[x] == h]
        if aday:
            secim.append(aday[int(rng.integers(len(aday)))])
    md = ["# Deney 4 — örnek cümleler", "", f"Aynı {len(secim)} tekrar, üç koşul (tohum {tohum}).", ""]
    for x in secim:
        r = u[u.orneklem_no == x]
        b = r.iloc[0]
        md += [f"## {x}. {b.kisi} · görüş {b.gorus}° · gerçek etiket: {ht.KISA_AD.get(b.hata, b.hata)}", ""]
        for k in KOSULLAR:
            q = r[r.kosul == k]
            if len(q):
                q = q.iloc[0]
                ad = ", ".join(ht.KISA_AD.get(h, h) for h in _liste(q.cikarilan)) or "–"
                md += [f"- **{k}:** {q.metin}", f"  <sub>çıkarıcı: {ad}</sub>"]
        md.append("")
    Path(yol).write_text("\n".join(md), encoding="utf-8")


# ---------------------------------------------------------------- elle etiketleme (çıkarıcının bağımsız sınaması)
ELLE_HATALAR = [("omuz", ht.SILKME), ("bas", "ERR_HEAD_TO_SIDE"), ("one_kacma", "ERR_ARM_FORWARD"),
                ("dirsek", "ERR_BENT_ARM"), ("az_kaldirma", "ERR_LOW_ABDUCTION")]


def elle_secim(u: pd.DataFrame, tohum: int = TOHUM_ELLE, n: int = ELLE_KOSUL_BASINA) -> pd.DataFrame:
    """Her koşuldan n cümle, sınıflara dengeli (n // 6 her sınıftan, kalan sınıflar tohumla); bir tekrar en fazla bir kez."""
    rng = np.random.default_rng(tohum)
    kullanilan, parca = set(), []
    for k in KOSULLAR:
        g = u[u.kosul == k].sort_values("orneklem_no")
        pay = {h: n // len(ht.SINIFLAR) for h in ht.SINIFLAR}
        for h in [ht.SINIFLAR[i] for i in rng.permutation(len(ht.SINIFLAR))][: n % len(ht.SINIFLAR)]:
            pay[h] += 1
        for h in ht.SINIFLAR:
            aday = g[(g.hata == h) & ~g.orneklem_no.isin(kullanilan)]
            m = min(pay[h], len(aday))
            s = aday.iloc[np.sort(rng.choice(len(aday), size=m, replace=False))]
            kullanilan |= set(s.orneklem_no)
            parca.append(s)
    s = pd.concat(parca, ignore_index=True)
    s = s.iloc[rng.permutation(len(s))].reset_index(drop=True)
    s.insert(0, "sira", range(1, len(s) + 1))
    return s


def elle_uret(u: pd.DataFrame, klasor: Path) -> Path:
    s = elle_secim(u)
    form = s[["sira", "metin"]].rename(columns={"metin": "cumle"})
    for ad, _ in ELLE_HATALAR:
        form[ad] = ""
    form["not"] = ""
    yol = Path(klasor) / "elle_etiket.csv"
    if yol.exists():
        raise SystemExit(f"{yol} zaten var; üzerine yazılmaz (kullanıcının etiketleri olabilir).")
    form.to_csv(yol, index=False, encoding="utf-8-sig")
    try:                                   # kullanıcının dolduracağı Excel kopyası (Türkçe Excel CSV'yi bölmeyebilir)
        with pd.ExcelWriter(Path(klasor) / "elle_etiket.xlsx") as yazici:
            form.to_excel(yazici, sheet_name="etiket", index=False)
            sh = yazici.sheets["etiket"]
            from openpyxl.styles import Alignment
            for sutun, gen in zip("ABCDEFGH", (6, 90, 8, 8, 11, 9, 13, 30)):
                sh.column_dimensions[sutun].width = gen
            for satir in sh.iter_rows(min_row=2):
                satir[1].alignment = Alignment(wrap_text=True, vertical="top")
            sh.freeze_panes = "C2"
    except ImportError:
        pass
    s[["sira", "orneklem_no", "kosul", "cikarilan"]].to_csv(Path(klasor) / "elle_etiket_anahtar.csv", index=False,
                                                            encoding="utf-8-sig")
    return yol


def elle_degerlendir(klasor: Path) -> dict[str, pd.DataFrame]:
    xlsx = Path(klasor) / "elle_etiket.xlsx"
    if xlsx.exists():                      # kullanıcı Excel kopyasını doldurur
        f = pd.read_excel(xlsx, dtype=str).fillna("")
    else:
        f = pd.read_csv(Path(klasor) / "elle_etiket.csv", encoding="utf-8-sig", keep_default_na=False, dtype=str)
    f["sira"] = f["sira"].astype(str).str.replace(r"\.0$", "", regex=True)
    a = pd.read_csv(Path(klasor) / "elle_etiket_anahtar.csv", encoding="utf-8-sig", keep_default_na=False, dtype=str)
    m = f.merge(a, on="sira")
    m["kullanici"] = ["|".join(h for ad, h in ELLE_HATALAR if str(r[ad]).strip() not in ("", "0"))
                      for _, r in m.iterrows()]
    m["uyum"] = [set(_liste(x)) == set(_liste(y)) for x, y in zip(m.kullanici, m.cikarilan)]
    oz = pd.DataFrame([{"koşul": k, "cümle": int((m.kosul == k).sum()), "tam eşleşme": int(m[m.kosul == k].uyum.sum())}
                       for k in KOSULLAR] + [{"koşul": "hepsi", "cümle": len(m), "tam eşleşme": int(m.uyum.sum())}])
    return {"elle_uyum": oz, "elle_uyusmayan": m[~m.uyum][["sira", "kosul", "cumle", "kullanici", "cikarilan", "not"]]}


# ---------------------------------------------------------------- duyarlılık analizi: "az kaldırma" (Güncelleme 10, Karar 42)
# Önceden kayıt: ADIM_08 "Ek: Güncelleme 10". Seçim yalnızca metne dayanır; birincil tablo ve sözlük değişmez.
KALDIRMA_DESENI = re.compile(r"kald|kalk|yüks|yukarı", re.IGNORECASE)
KALDIRMA = "ERR_LOW_ABDUCTION"
TOHUM_KALDIRMA = 3
KALDIRMA_DOSYA, KALDIRMA_ANAHTAR = "elle_kaldirma.xlsx", "elle_kaldirma_anahtar.csv"
# sıradan bağımsız metrikler (katı yeniden hesaplanmaz: sıra insan etiketinden çıkmaz)
KALDIRMA_METRIKLERI = ["ilk iki: birincil söylendi /100", "hatalılarda olumlu cümle /100",
                       "doğrularda gereksiz uyarı /100", "sadakat: küme = girdi /100", "eklenen hata /100",
                       "atlanan hata /100"]
KALDIRMA_TALIMAT = [
    "Her satırda bir geri bildirim cümlesi var. Hangi tekrara ya da hangi yönteme ait olduğu gizli.",
    "",
    "TEK SORU: Bu cümle, kolun YETERİNCE KALDIRILMADIĞINI / DAHA YUKARI KALDIRILMASI GEREKTİĞİNİ bir hata olarak "
    "söylüyor mu?",
    "   Evet ise 'az_kaldirma' sütununa 1 yaz. Hayır ise boş bırak.",
    "",
    "NOT: Doğru tekrarı öven 'kolunu 145 dereceye kaldırdın' gibi cümleler HAYIR.",
    "NOT: Başka bir hatanın düzeltmesi içinde geçen 'kolunu yana kaldır' gibi ifadeler de, kolun az kalktığını "
    "söylemiyorsa HAYIR.",
    "",
    "Yalnızca cümleye bak; videoyu ya da başka bir dosyayı açma. İstersen 'not' sütununa kısa bir not yazabilirsin.",
    "'etiket' sayfasını doldur, dosyayı aynı adla kaydet.",
]


def kaldirma_secimi(u: pd.DataFrame, tohum: int = TOHUM_KALDIRMA) -> pd.DataFrame:
    """Deseni içeren bütün cümleler (üç koşul), karışık sırayla (tohumlu)."""
    s = u[u.metin.astype(str).map(lambda m: bool(KALDIRMA_DESENI.search(m)))]
    s = s.sort_values(["orneklem_no", "kosul"]).reset_index(drop=True)
    s = s.iloc[np.random.default_rng(tohum).permutation(len(s))].reset_index(drop=True)
    s.insert(0, "sira", range(1, len(s) + 1))
    return s


def kaldirma_uret(u: pd.DataFrame, klasor: Path) -> tuple[Path, int]:
    klasor = Path(klasor)
    yol, anahtar = klasor / KALDIRMA_DOSYA, klasor / KALDIRMA_ANAHTAR
    for p in (yol, anahtar):
        if p.exists():
            raise SystemExit(f"{p} zaten var; üzerine yazılmaz (kullanıcının etiketleri olabilir).")
    s = kaldirma_secimi(u)
    form = s[["sira", "metin"]].rename(columns={"metin": "cumle"})
    form["az_kaldirma"] = ""
    form["not"] = ""
    from openpyxl.styles import Alignment, Font
    with pd.ExcelWriter(yol) as yazici:
        pd.DataFrame({"talimat": KALDIRMA_TALIMAT}).to_excel(yazici, sheet_name="talimat", index=False)
        form.to_excel(yazici, sheet_name="etiket", index=False)
        t = yazici.sheets["talimat"]
        t.column_dimensions["A"].width = 120
        for satir in t.iter_rows(min_row=2):
            satir[0].alignment = Alignment(wrap_text=True, vertical="top")
            satir[0].font = Font(size=12)
        sh = yazici.sheets["etiket"]
        for sutun, gen in zip("ABCD", (6, 95, 12, 30)):
            sh.column_dimensions[sutun].width = gen
        for satir in sh.iter_rows(min_row=2):
            satir[1].alignment = Alignment(wrap_text=True, vertical="top")
        sh.freeze_panes = "C2"
    s[["sira", "orneklem_no", "kosul", "cikarilan"]].to_csv(anahtar, index=False, encoding="utf-8-sig")
    return yol, len(s)


def kaldirma_etiketleri(klasor: Path) -> pd.DataFrame:
    """Kullanıcının dosyası + anahtar → sira, orneklem_no, kosul, cikarilan, insan (bool), not."""
    f = pd.read_excel(Path(klasor) / KALDIRMA_DOSYA, sheet_name="etiket", dtype=str).fillna("")
    f["sira"] = f["sira"].astype(str).str.replace(r"\.0$", "", regex=True)
    deger = f["az_kaldirma"].astype(str).str.strip().str.replace(r"\.0$", "", regex=True)
    hatali = f[~deger.isin(["", "0", "1"])]
    if len(hatali):
        raise SystemExit(f"'az_kaldirma' yalnızca 1 ya da boş olabilir; sorunlu sıralar: {list(hatali.sira)}")
    f["insan"] = deger == "1"
    a = pd.read_csv(Path(klasor) / KALDIRMA_ANAHTAR, encoding="utf-8-sig", keep_default_na=False, dtype=str)
    m = a.merge(f[["sira", "cumle", "insan", "not"]], on="sira", how="left", validate="1:1")
    if m.insan.isna().any():
        raise SystemExit("Etiket dosyasında anahtardaki bazı sıralar yok; dosyanın satırları silinmiş olabilir.")
    m["orneklem_no"] = m.orneklem_no.astype(int)
    m["insan"] = m.insan.astype(bool)
    return m


def kaldirma_duzelt(u: pd.DataFrame, etiket: pd.DataFrame) -> pd.DataFrame:
    """Seçilen cümlelerde çıkarıcının 'az kaldırma' varlığı insan etiketiyle değiştirilir; diğer türler aynen kalır.
    Çıkarıcı da insan da evet diyorsa liste değişmez; yalnızca insan evet diyorsa sona eklenir."""
    d = u.copy()
    d["orneklem_no"] = d.orneklem_no.astype(int)
    insan = {(int(r.orneklem_no), r.kosul): bool(r.insan) for r in etiket.itertuples()}
    yeni = []
    for r in d.itertuples():
        l = _liste(r.cikarilan)
        e = insan.get((r.orneklem_no, r.kosul))
        if e is not None:
            if not e:
                l = [h for h in l if h != KALDIRMA]
            elif KALDIRMA not in l:
                l = l + [KALDIRMA]
        yeni.append("|".join(l))
    d["cikarilan"] = yeni
    return d


def kaldirma_degerlendir(u: pd.DataFrame, etiket: pd.DataFrame, bootstrap_n: int = 2000,
                         tohum: int = TOHUM_BOOTSTRAP) -> dict[str, pd.DataFrame]:
    d = kaldirma_duzelt(u, etiket)
    kosullar = [k for k in KOSULLAR if k in set(u.kosul)]
    satir = []
    for k in kosullar:
        b, c = metrik_satiri(u[u.kosul == k]), metrik_satiri(d[d.kosul == k])
        for a in KALDIRMA_METRIKLERI:
            satir.append({"koşul": k, "metrik": a, "birincil": b[a], "düzeltilmiş": c[a], "fark": c[a] - b[a]})
    ozet = pd.DataFrame(satir)

    e = etiket.copy()
    e["cikarici"] = e.cikarilan.map(lambda x: KALDIRMA in _liste(x))
    e["cikarici_ilk"] = e.cikarilan.map(lambda x: (_liste(x) or [""])[0] == KALDIRMA)
    uyum = pd.DataFrame([{
        "koşul": k, "seçilen cümle": int((e.kosul == k).sum()),
        "çıkarıcı evet / insan evet": int((g.cikarici & g.insan).sum()),
        "çıkarıcı evet / insan hayır": int((g.cikarici & ~g.insan).sum()),
        "çıkarıcı hayır / insan evet": int((~g.cikarici & g.insan).sum()),
        "çıkarıcı hayır / insan hayır": int((~g.cikarici & ~g.insan).sum()),
        "insan hayır, çıkarıcı ilk sırada az kaldırma": int((g.cikarici_ilk & ~g.insan).sum()),
    } for k in kosullar for g in [e[e.kosul == k]]])

    T = {"kaldirma_ozet": ozet, "kaldirma_uyum": uyum}
    if bootstrap_n and {"A"} < set(kosullar):
        T["kaldirma_bootstrap"] = bootstrap_farklari(d, [k for k in kosullar if k != "A"], bootstrap_n, tohum,
                                                     metrikler=KALDIRMA_METRIKLERI)
    sec = e.merge(d[["orneklem_no", "kosul", "cikarilan"]].rename(columns={"cikarilan": "duzeltilmis"}),
                  on=["orneklem_no", "kosul"], how="left")
    T["kaldirma_cumleler"] = sec[["sira", "orneklem_no", "kosul", "cumle", "insan", "cikarici", "cikarilan",
                                  "duzeltilmis", "not"]]
    return T


# ---------------------------------------------------------------- komutlar
def _istemci(saglayici: str, onbellek_yolu, rpm: float) -> llm.LLMIstemcisi:
    if saglayici == "sahte":
        s = llm.SahteSaglayici(lambda i: "Hareketi doğru yaptın. Böyle devam et.")
        return llm.LLMIstemcisi(s, llm.Onbellek(None))
    return llm.LLMIstemcisi(llm.saglayici_olustur(saglayici), llm.Onbellek(onbellek_yolu),
                            en_kisa_aralik_s=60.0 / rpm if rpm > 0 else 0.0)


def raporla(girdiler: pd.DataFrame, yanitlar: pd.DataFrame, klasor: Path, bootstrap_n: int, yazdir=True) -> dict:
    u = uzun_tablo(girdiler, yanitlar)
    T = tablolar(u, bootstrap_n)
    T["cumleler"] = u
    sonuclari_yaz(T, klasor)
    ornekler_md(u, Path(klasor) / "ornek_cumleler.md")
    if yazdir:
        pd.set_option("display.width", 250)
        pd.set_option("display.max_columns", 40)
        print("\nÖzet:")
        print(T["ozet"].round(2).set_index("koşul").T.to_string())
        if "bootstrap" in T:
            print("\nKişi bazlı bootstrap (koşul − A):")
            print(T["bootstrap"].round(2).to_string(index=False))
    return T


def main():
    ap = argparse.ArgumentParser(description="Deney 4: LLM ile kural tabanlı geri bildirim")
    ap.add_argument("islem", choices=["hazirla", "modeller", "pilot", "calistir", "raporla", "elle-uret",
                                      "elle-degerlendir", "kaldirma-uret", "kaldirma-degerlendir"])
    ap.add_argument("--model", default=VARSAYILAN_MODEL)
    ap.add_argument("--dusunme", default="otomatik",
                    help="otomatik (2.5'te bütçe 0, diğerlerinde varsayılan) | varsayilan | sayı (bütçe) | düzey adı")
    ap.add_argument("--saglayici", default="gemini", choices=["gemini", "ollama", "sahte"])
    ap.add_argument("--rpm", type=float, default=10.0, help="dakikadaki en fazla istek (bekleme = 60/rpm s)")
    ap.add_argument("--bootstrap", type=int, default=2000)
    ap.add_argument("--cikti", default=str(CIKTI))
    ap.add_argument("--sahte", action="store_true",
                    help="kaldirma-degerlendir: insan etiketi yerine çıkarıcının kendi kararı (boru hattı denemesi; "
                         "sonuclar/'a yazılmaz)")
    args = ap.parse_args()
    utf8_cikti()
    klasor = Path(args.cikti)
    pilot_klasor = klasor / "pilot"

    if args.islem == "modeller":
        for m in llm.GeminiSaglayici().modeller():
            if "generateContent" in m.get("supportedGenerationMethods", []):
                print(f"{m['name'].split('/')[-1]:45s} {m.get('displayName', '')}"
                      + ("  [düşünme]" if m.get("thinking") else ""))
        return

    if args.islem == "hazirla":
        o = pd.read_csv(ORNEKLEM, encoding="utf-8-sig", keep_default_na=False)
        g = girdileri_hazirla(tekrar_secimi(o))
        sonuclari_yaz({"girdiler": g}, klasor, xlsx_adi="girdiler.xlsx")
        pilot_klasor.mkdir(parents=True, exist_ok=True)
        gp = girdileri_hazirla(pilot_secimi(), yazdir=False)
        sonuclari_yaz({"girdiler": gp}, pilot_klasor, xlsx_adi="girdiler.xlsx")
        print(f"  pilot: {len(gp)} tekrar (örneklem dışı, tohum {TOHUM_PILOT}) → {pilot_klasor}")
        u = uzun_tablo(g, pd.DataFrame(columns=["orneklem_no", "kosul", "metin"]))
        print("\nA koşulu (denetim: sadakat 100 ve sayı uydurma 0 olmalı):")
        for a, v in metrik_satiri(u).items():
            print(f"  {a}: {v:.2f}" if isinstance(v, float) else f"  {a}: {v}")
        return

    if args.islem in ("pilot", "calistir"):
        hedef = pilot_klasor if args.islem == "pilot" else klasor
        g = girdileri_oku(hedef)
        dusunme = dusunme_ayari(args.model, args.dusunme)
        istemci = _istemci(args.saglayici, llm.ONBELLEK_YOLU, args.rpm)
        print(f"{args.islem}: {len(g)} tekrar × {len(LLM_KOSULLARI)} koşul · {args.saglayici} {args.model} · "
              f"düşünme {dusunme if dusunme is not None else 'model varsayılanı'} · en az {60 / args.rpm if args.rpm > 0 else 0:.1f} s aralık")
        t0 = time.time()
        y, durum = calistir_llm(g, istemci, args.model, dusunme, istemleri_oku())
        bilgi = {"islem": args.islem, "saglayici": args.saglayici, "model": args.model, "dusunme": dusunme,
                 "sicaklik": 0.0, "yanit": len(y), "beklenen": len(g) * len(LLM_KOSULLARI), "durum": durum,
                 "ag_istegi": istemci.ag_istegi, "sure_s": round(time.time() - t0, 1),
                 "tarih": time.strftime("%Y-%m-%d %H:%M")}
        if args.saglayici == "sahte":
            print("  sahte sağlayıcı: yalnızca boru hattı denemesi, hiçbir şey yazılmadı")
            raporla(g, y, Path(veri.KOK / "veri" / "ara" / "deney4_sahte"), 0, yazdir=True)
            return
        sonuclari_yaz({"yanitlar": y}, hedef, xlsx_adi="yanitlar.xlsx")
        (hedef / "bilgi.json").write_text(json.dumps(bilgi, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  {len(y)} yanıt, {istemci.ag_istegi} ağ isteği, {bilgi['sure_s']} s · {durum}")
        if len(y) == bilgi["beklenen"]:
            raporla(g, y, hedef, args.bootstrap if args.islem == "calistir" else 0)
        if args.islem == "pilot":
            print("\nPilot yanıtları (yalnızca biçim denetimi; raporlanmaz):")
            for r in y.itertuples():
                print(f"\n[{r.orneklem_no} · {r.kosul}] {r.metin}")
        print(f"\nÇıktı: {hedef}")
        return

    if args.islem == "raporla":            # ağ yok: kayıtlı girdiler + yanıtlardan tabloları yeniden yazar
        y = pd.read_csv(klasor / "yanitlar.csv", encoding="utf-8-sig", keep_default_na=False)
        raporla(girdileri_oku(klasor), y, klasor, args.bootstrap)
        return

    if args.islem == "elle-uret":
        u = pd.read_csv(klasor / "cumleler.csv", encoding="utf-8-sig", keep_default_na=False)
        print(f"Etiketleme dosyası: {elle_uret(u, klasor)}")
        return

    if args.islem == "elle-degerlendir":
        T = elle_degerlendir(klasor)
        sonuclari_yaz(T, klasor, xlsx_adi="elle_uyum.xlsx")
        print(T["elle_uyum"].to_string(index=False))
        print("\nUyuşmayanlar:")
        print(T["elle_uyusmayan"].to_string(index=False))
        return

    if args.islem == "kaldirma-uret":
        u = pd.read_csv(klasor / "cumleler.csv", encoding="utf-8-sig", keep_default_na=False)
        yol, n = kaldirma_uret(u, klasor)
        print(f"Etiketleme dosyası: {yol} ({n} cümle). Anahtar: {klasor / KALDIRMA_ANAHTAR} (açma).")
        return

    if args.islem == "kaldirma-degerlendir":
        u = pd.read_csv(klasor / "cumleler.csv", encoding="utf-8-sig", keep_default_na=False)
        if args.sahte:                     # çıkarıcının kendi kararı etiket yerine: düzeltilmiş = birincil olmalı
            e = kaldirma_secimi(u)[["sira", "orneklem_no", "kosul", "cikarilan", "metin"]].rename(
                columns={"metin": "cumle"})
            e["insan"] = e.cikarilan.map(lambda x: KALDIRMA in _liste(x))
            e["not"] = ""
            hedef = Path(veri.KOK / "veri" / "ara" / "deney4_kaldirma_sahte")
        else:
            e = kaldirma_etiketleri(klasor)
            hedef = klasor
        T = kaldirma_degerlendir(u, e, args.bootstrap)
        sonuclari_yaz(T, hedef, xlsx_adi="kaldirma_sonuclar.xlsx")
        pd.set_option("display.width", 250)
        print(f"Seçilen cümle: {len(e)} · insanın 'evet' dediği: {int(e.insan.sum())}"
              + ("  [SAHTE: etiket = çıkarıcı]" if args.sahte else ""))
        print("\nUyum (koşul başına):")
        print(T["kaldirma_uyum"].to_string(index=False))
        print("\nBirincil ve düzeltilmiş metrikler:")
        print(T["kaldirma_ozet"].round(2).to_string(index=False))
        if "kaldirma_bootstrap" in T:
            print("\nKişi bazlı bootstrap, düzeltilmiş (koşul − A):")
            print(T["kaldirma_bootstrap"].round(2).to_string(index=False))
        print(f"\nÇıktı: {hedef}")


if __name__ == "__main__":
    main()
