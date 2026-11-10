"""
Bütün deneylerin temiz bir klasörde yeniden üretilmesi ve kayıtlı sonuçlarla karşılaştırılması.

Ne yapar?
  1. Son commit'in (HEAD) temiz bir kopyasını açar: `git worktree add --detach <hedef> HEAD`. Commit'lenmemiş
     değişiklikler kopyaya girmez. Kopyada sonuclar/ ve deneylerin ürettiği modeller/*.json dosyaları silinir.
  2. Veri kopyalanmaz ve bağlanmaz: kopyadaki kod, OMUZ_VERI ortam değişkeniyle asıl veri/ klasörünü yalnızca okur.
  3. Deneyleri aşağıdaki ADIMLAR sırasıyla, aynı Python yorumlayıcısıyla, kopyanın içinde çalıştırır. Her adımın günlüğü
     <hedef>/hepsi_gunluk/ altına yazılır.
  4. Üretilen her CSV'yi ve modeller/*.json'u, bu klasördeki (proje) kayıtlı dosyayla karşılaştırır.
     Regresyon özeti: sonuclar/hepsi/regresyon.csv (çalıştırınca oluşur), adimlar.csv, ozet.md.
Kendi kayıt deneyi, kayıtlı ara çıktılardan (önbellekten) üretilir; video üzerinde MediaPipe yeniden
çalıştırılmaz. Önbellek yoksa adım başarısız olur ("üretilmedi").
Ödevin dışında kalan eski deneyler burada yok.

Kullanım:
    python -m deneyler.hepsi                 # tam çalıştırma (~1,5 dk)
    python -m deneyler.hepsi --hizli         # küçük alt küme (deney 1, kamera açısı, hız eşiği), ~1 dk
    python -m deneyler.hepsi --adimlar deney2 deney3   # yalnızca seçilen adımlar (bağımlılıklar kullanıcının işi)
    python -m deneyler.hepsi --temizle       # temiz kopyayı (git worktree) kaldırır
Karşılaştırma: sayısal sütunlarda en büyük mutlak fark ≤ --tolerans (varsayılan 1e-9) ise "aynı".
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import NamedTuple

import numpy as np
import pandas as pd

from cekirdek import veri
from cekirdek.konsol import sonuclari_yaz, utf8_cikti

KOK = veri.KOK
CIKTI = KOK / "sonuclar" / "hepsi"
VARSAYILAN_HEDEF = Path(tempfile.gettempdir()) / "omuz_hepsi_temiz"

class Adim(NamedTuple):
    """Bir yeniden üretim adımı.
    komut: modül + argümanlar; {VERI}, {PROJE}, {HEDEF} yer tutucuları çalıştırmada doldurulur.
    klasorler: karşılaştırılacak sonuç klasörleri; modeller: üretilen modeller/*.json.
    girdiler: adımdan önce projeden temiz kopyaya kopyalanan insan girdisi dosyalar (ör. kullanıcı etiketleri);
      bunlar yeniden üretilmez ve karşılaştırılmaz.
    dosyalar: {klasör: [dosya, ...]} yalnızca bu CSV'ler karşılaştırılır (None: klasördeki bütün CSV'ler).
    yok_sutun: {"klasör/dosya": [sütun, ...]} karşılaştırmada yok sayılan sütunlar.
    kaynak: "" (baştan) ya da önbellekten üretimin açıklaması."""
    ad: str
    komut: list
    klasorler: list
    modeller: list
    girdiler: tuple = ()
    dosyalar: dict | None = None
    yok_sutun: dict | None = None
    kaynak: str = ""


ADIMLAR = [
    Adim("deney1", ["deneyler.deney1"], ["deney1"], []),
    Adim("deney2", ["deneyler.deney2"], ["deney2"], []),
    Adim("deney3", ["deneyler.deney3"], ["deney3"], []),
    Adim("tekrar_ayirma", ["deneyler.tekrar_ayirma"], ["tekrar_ayirma"], []),
    Adim("kamera_acisi", ["deneyler.kamera_acisi"], ["kamera_acisi"], ["kamera_esigi.json"]),
    Adim("hiz_esigi", ["deneyler.hiz_esigi"], ["hiz_esigi"], ["hiz_esigi.json"]),
    Adim("kural_disa_aktar", ["araclar.kural_disa_aktar"], ["kural_disa_aktar"], ["kural_ex1.json"]),
    # önbellekten: video üzerinde MediaPipe yeniden çalıştırılmaz
    Adim("kendi_kayit", ["deneyler.kendi_kayit", "--kisi", "kisi1",
                         "--kalibrasyon", "{VERI}/kendi_kayit/kisi1/kalibrasyon.MOV",
                         "--test", "{VERI}/kendi_kayit/kisi1/test.MOV",
                         "--etiketler", "{VERI}/kendi_kayit/kisi1/etiketler.csv", "--yalniz-onbellek"],
         ["kendi_kayit"], [], kaynak="önbellekten: veri/ara/kendi_kayit/ (MediaPipe noktaları)"),
]
HIZLI = ["deney1", "kamera_acisi", "hiz_esigi"]
URETILEN_MODELLER = sorted({m for a in ADIMLAR for m in a.modeller})
# Yeniden üretilmeyen, yalnızca listelenen kayıtlı çıktılar
LISTELENEN = {"gorsel_kontrol": "görsel kontrol aracı çıktıları",
              "uygulama_saglik": "uygulama sağlık kontrolü (MediaPipe sürüm farkı)",
              "sunum": "sunum şekil adayları"}
YOK_SAYILAN_ANAHTARLAR = {"bilgi", "tarih"}   # JSON'larda sürüm/tarih bilgisi


# ---------------------------------------------------------------- temiz kopya
def _git(*a, cwd=KOK) -> str:
    return subprocess.check_output(["git", *a], cwd=cwd, text=True, encoding="utf-8").strip()


def kirli_dosyalar() -> list[str]:
    return [s for s in _git("status", "--porcelain").splitlines() if s.strip()]


def temiz_kopya(hedef: Path) -> str:
    """HEAD'in worktree kopyası; sonuçlar ve üretilen modeller silinir. Dönüş: commit."""
    hedef = Path(hedef)
    if hedef.exists():
        raise SystemExit(f"{hedef} zaten var. Önce: python -m deneyler.hepsi --temizle --hedef \"{hedef}\"")
    _git("worktree", "add", "--detach", str(hedef), "HEAD")
    shutil.rmtree(hedef / "sonuclar", ignore_errors=True)
    for m in URETILEN_MODELLER:
        (hedef / "modeller" / m).unlink(missing_ok=True)
    return _git("rev-parse", "--short", "HEAD", cwd=hedef)


def temizle(hedef: Path) -> None:
    hedef = Path(hedef)
    if not hedef.exists():
        print(f"{hedef} yok.")
        return
    if not (hedef / ".git").is_file():          # worktree'de .git bir dosyadır; başka bir klasörü silmeyelim
        raise SystemExit(f"{hedef} bir git worktree'si gibi görünmüyor; elle kontrol et.")
    _git("worktree", "remove", "--force", str(hedef))
    print(f"Kaldırıldı: {hedef}")


# ---------------------------------------------------------------- çalıştırma
def komutu_doldur(komut: list[str], hedef: Path, proje: Path = KOK, veri_kok: Path | None = None) -> list[str]:
    yer = {"{VERI}": Path(veri_kok or veri.VERI_KOK).as_posix(), "{PROJE}": Path(proje).as_posix(),
           "{HEDEF}": Path(hedef).as_posix()}
    cikti = []
    for k in komut:
        for a, b in yer.items():
            k = k.replace(a, b)
        cikti.append(k)
    return cikti


def girdileri_kopyala(adim: Adim, hedef: Path, proje: Path = KOK) -> None:
    """İnsan girdisi dosyaları (yeniden üretilemez) projeden temiz kopyaya; eksikse adım çalışmaz."""
    for g in adim.girdiler:
        kaynak, varis = Path(proje) / g, Path(hedef) / g
        if not kaynak.exists():
            raise FileNotFoundError(f"girdi yok: {kaynak}")
        varis.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(kaynak, varis)


def adim_calistir(ad: str, komut: list[str], hedef: Path, gunluk: Path) -> dict:
    ortam = {**os.environ, "OMUZ_VERI": str(veri.VERI_KOK), "PYTHONIOENCODING": "utf-8", "MPLBACKEND": "Agg"}
    komut = komutu_doldur(komut, hedef)
    (Path(hedef) / "hepsi_ara").mkdir(exist_ok=True)
    t0 = time.time()
    with open(gunluk / f"{ad}.log", "w", encoding="utf-8") as f:
        r = subprocess.run([sys.executable, "-m", *komut], cwd=hedef, env=ortam, stdout=f, stderr=subprocess.STDOUT)
    return {"adım": ad, "komut": "python -m " + " ".join(komut), "çıkış kodu": r.returncode,
            "süre (s)": round(time.time() - t0, 1)}


# ---------------------------------------------------------------- karşılaştırma
def _csv_oku(p: Path) -> pd.DataFrame | None:
    """Boş (sütunsuz) CSV için None."""
    try:
        return pd.read_csv(p, encoding="utf-8-sig", keep_default_na=False, low_memory=False)
    except pd.errors.EmptyDataError:
        return None


def csv_karsilastir(yeni: Path, eski: Path, tolerans: float, yok_sutun=()) -> dict:
    a, b = _csv_oku(yeni), _csv_oku(eski)
    if a is None or b is None:
        ayni = a is None and b is None
        return {"durum": "aynı" if ayni else "farklı", "ayrıntı": "boş dosya" if ayni else "biri boş",
                "en büyük fark": 0.0 if ayni else np.nan}
    yok_sutun = list(yok_sutun or ())
    if yok_sutun:
        a = a.drop(columns=[c for c in yok_sutun if c in a.columns])
        b = b.drop(columns=[c for c in yok_sutun if c in b.columns])
    if list(a.columns) != list(b.columns) or a.shape != b.shape:
        return {"durum": "farklı", "ayrıntı": f"boyut/sütun: {a.shape} / {b.shape}", "en büyük fark": np.nan}
    en, metin_farki = 0.0, []
    for c in a.columns:
        x, y = pd.to_numeric(a[c].replace("", np.nan), errors="coerce"), pd.to_numeric(b[c].replace("", np.nan),
                                                                                   errors="coerce")
        sayisal = x.notna() | y.notna()
        if sayisal.any() and (x.notna() == y.notna()).all() and x.notna().sum() == sayisal.sum():
            d = np.abs(x[sayisal].to_numpy(float) - y[sayisal].to_numpy(float))
            d = np.where(np.isnan(d), 0.0, d)
            en = max(en, float(d.max()) if len(d) else 0.0)
            ayni_metin = (a[c][~sayisal].astype(str) == b[c][~sayisal].astype(str)).all()
        else:
            ayni_metin = (a[c].astype(str) == b[c].astype(str)).all()
        if not ayni_metin:
            metin_farki.append(c)
    if metin_farki:
        return {"durum": "farklı", "ayrıntı": "metin sütunları: " + ", ".join(metin_farki[:5]), "en büyük fark": en}
    ayr = f"yok sayılan sütun: {', '.join(yok_sutun)}" if yok_sutun else ""
    return {"durum": "aynı" if en <= tolerans else "farklı", "ayrıntı": ayr, "en büyük fark": en}


def _json_duzle(d, on="") -> dict:
    if isinstance(d, dict):
        return {k2: v2 for k, v in d.items() if k not in YOK_SAYILAN_ANAHTARLAR
                for k2, v2 in _json_duzle(v, f"{on}.{k}" if on else k).items()}
    if isinstance(d, list):
        return {k2: v2 for i, v in enumerate(d) for k2, v2 in _json_duzle(v, f"{on}[{i}]").items()}
    return {on: d}


def json_karsilastir(yeni: Path, eski: Path, tolerans: float) -> dict:
    a, b = (_json_duzle(json.loads(Path(p).read_text(encoding="utf-8"))) for p in (yeni, eski))
    if set(a) != set(b):
        return {"durum": "farklı", "ayrıntı": f"anahtarlar: {sorted(set(a) ^ set(b))[:5]}", "en büyük fark": np.nan}
    en, farkli = 0.0, []
    for k in a:
        if isinstance(a[k], (int, float)) and isinstance(b[k], (int, float)) and not isinstance(a[k], bool):
            en = max(en, abs(float(a[k]) - float(b[k])))
        elif a[k] != b[k]:
            farkli.append(k)
    if farkli:
        return {"durum": "farklı", "ayrıntı": ", ".join(farkli[:5]), "en büyük fark": en}
    return {"durum": "aynı" if en <= tolerans else "farklı", "ayrıntı": "", "en büyük fark": en}


def _adim(a) -> Adim:
    return a if isinstance(a, Adim) else Adim(*a)


def karsilastirma_plani(adimlar: list) -> tuple[dict, dict]:
    """{klasör: None (bütün CSV'ler) ya da dosya kümesi}, {"klasör/dosya": yok sayılan sütunlar}."""
    plan, yok = {}, {}
    for a in map(_adim, adimlar):
        for k in a.klasorler:
            d = (a.dosyalar or {}).get(k)
            if d is None:
                plan[k] = None
            elif k not in plan or plan[k] is not None:
                plan[k] = set(plan.get(k) or ()) | set(d)
        yok.update(a.yok_sutun or {})
    return plan, yok


def karsilastir(hedef: Path, adimlar: list, tolerans: float, kayitli_kok: Path = KOK) -> pd.DataFrame:
    satir = []
    plan, yok = karsilastirma_plani(adimlar)
    for k in sorted(plan):
        yeni_k, eski_k = Path(hedef) / "sonuclar" / k, Path(kayitli_kok) / "sonuclar" / k
        yeni = {p.relative_to(yeni_k).as_posix() for p in yeni_k.rglob("*.csv")} if yeni_k.exists() else set()
        eski = {p.relative_to(eski_k).as_posix() for p in eski_k.rglob("*.csv")} if eski_k.exists() else set()
        if plan[k] is not None:
            yeni, eski = yeni & plan[k], eski & plan[k]
        for f in sorted(yeni | eski):
            r = {"klasör": k, "dosya": f}
            if f not in yeni:
                r.update({"durum": "üretilmedi", "ayrıntı": "kayıtlıda var, yeniden üretimde yok", "en büyük fark": np.nan})
            elif f not in eski:
                r.update({"durum": "yeni", "ayrıntı": "kayıtlıda yok", "en büyük fark": np.nan})
            else:
                r.update(csv_karsilastir(yeni_k / f, eski_k / f, tolerans, yok.get(f"{k}/{f}")))
            satir.append(r)
    for m in sorted({m for a in map(_adim, adimlar) for m in a.modeller}):
        yeni, eski = Path(hedef) / "modeller" / m, Path(kayitli_kok) / "modeller" / m
        r = {"klasör": "modeller", "dosya": m}
        if not yeni.exists():
            r.update({"durum": "üretilmedi", "ayrıntı": "", "en büyük fark": np.nan})
        else:
            r.update(json_karsilastir(yeni, eski, tolerans))
        satir.append(r)
    return pd.DataFrame(satir, columns=["klasör", "dosya", "durum", "ayrıntı", "en büyük fark"])


def listelenenler(kayitli_kok: Path = KOK) -> pd.DataFrame:
    satir = []
    for k, neden in LISTELENEN.items():
        p = Path(kayitli_kok) / "sonuclar" / k
        satir.append({"klasör": k, "neden yeniden üretilmedi": neden, "var mı": p.exists(),
                      "dosya sayısı": sum(1 for x in p.rglob("*") if x.is_file()) if p.exists() else 0})
    return pd.DataFrame(satir)


def md_tablo(df: pd.DataFrame) -> str:
    """Basit markdown tablosu (tabulate paketi gerekmesin)."""
    def h(v):
        return "" if v is None or (isinstance(v, float) and np.isnan(v)) else str(v).replace("|", "/")
    satir = ["| " + " | ".join(map(str, df.columns)) + " |", "| " + " | ".join("---" for _ in df.columns) + " |"]
    satir += ["| " + " | ".join(h(v) for v in r) + " |" for r in df.itertuples(index=False)]
    return "\n".join(satir)


def ozet_md(adim_t: pd.DataFrame, reg: pd.DataFrame, liste: pd.DataFrame, commit: str, hizli: bool) -> str:
    say = reg.durum.value_counts().to_dict()
    md = [f"# Yeniden üretim özeti{' (--hizli, yalnızca deneme)' if hizli else ''}", "",
          f"- Tarih: {dt.datetime.now():%Y-%m-%d %H:%M} · commit: `{commit}` · Python {sys.version.split()[0]}",
          f"- Adım: {len(adim_t)} · başarısız: {int((adim_t['çıkış kodu'] != 0).sum())} · "
          f"toplam süre: {adim_t['süre (s)'].sum() / 60:.1f} dk",
          f"- Karşılaştırılan dosya: {len(reg)} · " + " · ".join(f"{k}: {v}" for k, v in say.items()),
          f"- Yeniden üretim: {say.get('aynı', 0)}/{len(reg)} aynı", "",
          "## Adımlar", "", md_tablo(adim_t), "",
          "## Aynı olmayan dosyalar", ""]
    farkli = reg[reg.durum != "aynı"]
    md += [md_tablo(farkli) if len(farkli) else "Yok: bütün dosyalar aynı.", "",
           "## Yeniden üretilmeyen kayıtlı çıktılar", "", md_tablo(liste), ""]
    return "\n".join(md)


def main():
    ap = argparse.ArgumentParser(description="Bütün deneyleri temiz kopyada yeniden üret ve karşılaştır")
    ap.add_argument("--hedef", default=str(VARSAYILAN_HEDEF), help="temiz kopyanın klasörü (git worktree)")
    ap.add_argument("--hizli", action="store_true", help=f"yalnızca {', '.join(HIZLI)}")
    ap.add_argument("--adimlar", nargs="+", choices=[a.ad for a in ADIMLAR])
    ap.add_argument("--tolerans", type=float, default=1e-9)
    ap.add_argument("--temizle", action="store_true", help="temiz kopyayı kaldır ve çık")
    ap.add_argument("--cikti", default=str(CIKTI))
    args = ap.parse_args()
    utf8_cikti()
    hedef = Path(args.hedef)
    if args.temizle:
        temizle(hedef)
        return
    secim = args.adimlar or (HIZLI if args.hizli else [a.ad for a in ADIMLAR])
    adimlar = [a for a in ADIMLAR if a.ad in secim]
    kirli = [s for s in kirli_dosyalar() if not s[3:].startswith("sonuclar/hepsi")]
    if kirli:
        print(f"UYARI: {len(kirli)} commit'lenmemiş değişiklik var; temiz kopya yalnızca HEAD'i içerir.")
    commit = temiz_kopya(hedef)
    gunluk = hedef / "hepsi_gunluk"
    gunluk.mkdir()
    print(f"Temiz kopya: {hedef} (commit {commit}); veri: {veri.VERI_KOK} (yalnızca okunur)")
    adim_k = []
    for i, a in enumerate(adimlar, 1):
        ad, komut = a.ad, a.komut
        print(f"[{i}/{len(adimlar)}] {ad}: python -m {' '.join(komutu_doldur(komut, hedef))} ...", flush=True)
        try:
            girdileri_kopyala(a, hedef)
        except FileNotFoundError as e:
            print(f"      {e} → adım çalıştırılmadı", flush=True)
            adim_k.append({"adım": ad, "komut": "python -m " + " ".join(komut), "çıkış kodu": -1, "süre (s)": 0.0,
                           "kaynak": a.kaynak or "baştan"})
            continue
        r = adim_calistir(ad, komut, hedef, gunluk)
        r["kaynak"] = a.kaynak or "baştan"
        adim_k.append(r)
        print(f"      çıkış {r['çıkış kodu']} · {r['süre (s)']} s" +
              (f"  ← HATA, günlük: {gunluk / (ad + '.log')}" if r["çıkış kodu"] else ""), flush=True)
    adim_t = pd.DataFrame(adim_k)
    reg = karsilastir(hedef, adimlar, args.tolerans)
    liste = listelenenler()
    cikti = Path(args.cikti) / ("hizli" if args.hizli and not args.adimlar else "")
    sonuclari_yaz({"adimlar": adim_t, "regresyon": reg, "listelenen": liste}, cikti, xlsx_adi="hepsi.xlsx")
    (cikti / "ozet.md").write_text(ozet_md(adim_t, reg, liste, commit, args.hizli), encoding="utf-8")
    print("\n" + reg.durum.value_counts().to_string())
    farkli = reg[reg.durum != "aynı"]
    if len(farkli):
        print("\nAynı olmayanlar:")
        print(farkli.to_string(index=False))
    print(f"\nÖzet: {cikti / 'ozet.md'}\nTemiz kopya duruyor (incelemek için). Kaldırmak için: "
          f"python -m deneyler.hepsi --temizle")


if __name__ == "__main__":
    main()
