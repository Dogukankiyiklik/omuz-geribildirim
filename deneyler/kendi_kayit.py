"""
Kendi kayıtlarımızla deneme.

Dondurulmuş yöntem + modeller/kural_ex1.json + yığın modu (uygulama/toplu.py) + MediaPipe 1.2.2.
Hiçbir eşik bu kayıtlara göre değiştirilmez. Metrikler çekimden önce sabitlendi:
  * hatalı tekrarlarda: katı (cümledeki ilk hata = etiket), ilk iki (etiket cümlede söylendi),
    olumlu cümle (hiç hata söylenmedi);
  * doğru tekrarlarda gereksiz uyarı (cümlede en az bir hata), üç grupta ayrı: normal, bakış, hızlı;
  * hız notunun hızlı tekrarlarda ve normal doğru tekrarlarda çıkıp çıkmadığı;
  * karışıklık tablosu (gerçek etiket × cümledeki ilk hata) ve tekrar başına "verilen cümle – gerçek etiket".
  Hata listesi, kullanıcının gördüğü hasta cümlesinden cekirdek/metin_cozumleyici ile çıkarılır (Deney 3 ile
  aynı çıkarıcı); uzman ayrıntısından çıkarılan listeyle aynı olduğu denetlenir. Sayılar "kaçta kaç".
  Güven aralığı verilmez (kişi başına 21 tekrar).

Eşleştirme: test videosunda ayrılan tekrarlar zaman sırasıyla etiketler.csv'deki tekrar_no ile eşlenir.
Sayılar tutmazsa betik durur ve ayrılan tekrarların zamanlarını (karar ve cümle OLMADAN) yazar; kullanıcı
videoya bakarak bir eşleşme dosyası (ayrilan, tekrar_no) hazırlar ve --eslesme ile verir.

Kullanım:
    # 1) Çekimden önce: karışık sıra + etiket şablonu (tohum ile; kâğıda yazdırılır)
    python -m deneyler.kendi_kayit --sablon veri/kendi_kayit/kisi1/etiketler.csv --tohum 0
    # 2) Çekimden sonra: değerlendirme (MediaPipe birkaç dakika; noktalar veri/ara/kendi_kayit/ altına önbelleklenir)
    python -m deneyler.kendi_kayit --kisi kisi1 --kalibrasyon veri/kendi_kayit/kisi1/kalibrasyon.mp4 \\
        --test veri/kendi_kayit/kisi1/test.mp4 --etiketler veri/kendi_kayit/kisi1/etiketler.csv
Çıktı: sonuclar/kendi_kayit/<kisi>/ (tekrarlar.csv, cumle_etiket.csv, karisiklik.csv, ozet.csv, bilgi.json)
       ve bütün kişiler birlikte: sonuclar/kendi_kayit/ozet.csv, karisiklik.csv
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path

import numpy as np
import pandas as pd

from cekirdek import hata_turu as ht
from cekirdek import veri
from cekirdek.konsol import sonuclari_yaz, utf8_cikti
from cekirdek.metin_cozumleyici import cozumle

CIKTI = veri.KOK / "sonuclar" / "kendi_kayit"
ONBELLEK = veri.VERI_KOK / "ara" / "kendi_kayit"   # OMUZ_VERI yoksa veri/ara/kendi_kayit

# test videosunun içeriği (21 tekrar)
ETIKETLER = {"dogru": ht.DOGRU, "omuz": "ERR_ELEVATED_SHOULDER", "bas": "ERR_HEAD_TO_SIDE",
             "dirsek": "ERR_BENT_ARM", "az_kaldirma": "ERR_LOW_ABDUCTION", "one_kacma": "ERR_ARM_FORWARD"}
NOTLAR = ("", "bakis", "hizli")
PROTOKOL = [("dogru", "", 5), ("omuz", "", 3), ("bas", "", 2), ("dirsek", "", 2), ("az_kaldirma", "", 2),
            ("one_kacma", "", 2), ("dogru", "bakis", 3), ("dogru", "hizli", 2)]
ACIKLAMA = {("dogru", ""): "doğru (normal)", ("omuz", ""): "omuz silkme (omzu kulağa doğru kaldır)",
            ("bas", ""): "başı yana eğ", ("dirsek", ""): "dirseği bük", ("az_kaldirma", ""): "kolu az kaldır (~90°)",
            ("one_kacma", ""): "kolu öne doğru kaldır (yandan değil)",
            ("dogru", "bakis"): "doğru, ama yere ya da yana bak", ("dogru", "hizli"): "doğru, ama hızlı (~1 saniye)"}
GRUPLAR = {"normal": "doğru (normal)", "bakis": "doğru, bakış", "hizli": "doğru, hızlı"}


# ---------------------------------------------------------------- 1) çekimden önce: sıra ve şablon
def sira_uret(tohum: int = 0) -> pd.DataFrame:
    """Test videosundaki 21 tekrarın karışık sırası (tohumlu, tekrarlanabilir)."""
    liste = [(e, n) for e, n, adet in PROTOKOL for _ in range(adet)]
    rng = np.random.default_rng(tohum)
    sira = [liste[i] for i in rng.permutation(len(liste))]
    return pd.DataFrame({"tekrar_no": range(1, len(sira) + 1), "etiket": [e for e, _ in sira],
                         "not": [n for _, n in sira], "ne_yapilacak": [ACIKLAMA[s] for s in sira]})


def sablon_yaz(yol, tohum: int = 0) -> pd.DataFrame:
    yol = Path(yol)
    if yol.exists():
        raise SystemExit(f"{yol} zaten var; üzerine yazılmadı.")
    yol.parent.mkdir(parents=True, exist_ok=True)
    df = sira_uret(tohum)
    df[["tekrar_no", "etiket", "not"]].to_csv(yol, index=False, encoding="utf-8")
    return df


# ---------------------------------------------------------------- 2) girdiler
def etiketleri_oku(yol) -> pd.DataFrame:
    df = pd.read_csv(yol, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    df.columns = [c.strip() for c in df.columns]
    eksik = {"tekrar_no", "etiket"} - set(df.columns)
    if eksik:
        raise SystemExit(f"etiketler.csv'de eksik sütun: {sorted(eksik)} (beklenen: tekrar_no, etiket, not)")
    if "not" not in df:
        df["not"] = ""
    df["tekrar_no"] = df.tekrar_no.astype(int)
    df["etiket"] = df.etiket.str.strip().str.lower()
    df["not"] = df["not"].str.strip().str.lower()
    hatali = set(df.etiket) - set(ETIKETLER)
    if hatali:
        raise SystemExit(f"bilinmeyen etiket: {sorted(hatali)}; geçerli: {list(ETIKETLER)}")
    hatali = set(df["not"]) - set(NOTLAR)
    if hatali:
        raise SystemExit(f"bilinmeyen not: {sorted(hatali)}; geçerli: bos, bakis, hizli")
    if ((df["not"] != "") & (df.etiket != "dogru")).any():
        raise SystemExit("'bakis' ve 'hizli' notu yalnızca 'dogru' etiketli tekrarlarda olur")
    if df.tekrar_no.duplicated().any() or sorted(df.tekrar_no) != list(range(1, len(df) + 1)):
        raise SystemExit("tekrar_no 1'den başlayıp birer artmalı ve tekrarsız olmalı")
    return df.sort_values("tekrar_no").reset_index(drop=True)


def onbellekli_pozlar(yol, yalniz_onbellek: bool = False) -> np.ndarray:
    """MediaPipe noktaları; video değişmediyse önbellekten (veri/ara/kendi_kayit/).
    yalniz_onbellek=True: önbellek yoksa MediaPipe çalıştırılmaz, durulur (yeniden üretim)."""
    from uygulama.toplu import pozlar
    yol = Path(yol)
    st = yol.stat()
    anahtar = f"{yol.parent.name}_{yol.stem}_{st.st_size}_{int(st.st_mtime)}"
    dosya = ONBELLEK / f"{anahtar}.npy"
    if dosya.exists():
        return np.load(dosya)
    if yalniz_onbellek:
        raise SystemExit(f"önbellek yok: {dosya} (--yalniz-onbellek: MediaPipe çalıştırılmadı)")
    print(f"MediaPipe: {yol} (birkaç dakika sürebilir)")
    lm = pozlar(yol)
    dosya.parent.mkdir(parents=True, exist_ok=True)
    np.save(dosya, lm)
    return lm


# ---------------------------------------------------------------- 3) eşleştirme
def eslestir(n_ayrilan: int, etiket: pd.DataFrame, eslesme_yolu=None) -> dict[int, int]:
    """{ayrılan tekrar no (1'den): etiketteki tekrar_no}."""
    if eslesme_yolu:
        e = pd.read_csv(eslesme_yolu, encoding="utf-8-sig")
        es = {int(a): int(t) for a, t in zip(e.ayrilan, e.tekrar_no)}
        if len(set(es.values())) != len(es):
            raise SystemExit("eşleşme dosyasında aynı tekrar_no iki kez var")
        return es
    if n_ayrilan != len(etiket):
        return {}
    return {i + 1: int(t) for i, t in enumerate(etiket.tekrar_no)}


def ayrilanlari_yaz(o, yol: Path) -> pd.DataFrame:
    """Sayı tutmadığında: ayrılan tekrarların zamanları (karar ve cümle olmadan)."""
    df = pd.DataFrame([{"ayrilan": k.no, "bas_s": round(k.bas / o.fps, 2), "son_s": round(k.son / o.fps, 2),
                        "sure_s": round((k.son - k.bas + 1) / o.fps, 2),
                        "tepe_aci": round(float(k.tepe), 1) if np.isfinite(k.tepe) else ""} for k in o.tekrarlar])
    yol.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(yol, index=False, encoding="utf-8-sig")
    return df


# ---------------------------------------------------------------- 4) tablo ve metrikler
def _liste(s: str) -> list[str]:
    return [x for x in str(s).split("|") if x]


def tekrar_tablosu(o, etiket: pd.DataFrame, es: dict[int, int], kisi: str) -> pd.DataFrame:
    et = etiket.set_index("tekrar_no")
    satir = []
    for r in o.oturum_satirlari():
        no = es.get(int(r["tekrar"]))
        if no is None:
            continue
        e = et.loc[no]
        h = r.get("hasta_cumlesi", "")
        u = r.get("uzman_ayrintisi", "")
        satir.append({"kisi": kisi, "tekrar_no": no, "etiket": e.etiket, "not": e["not"], "hata": ETIKETLER[e.etiket],
                      "grup": (GRUPLAR["normal"] if e.etiket == "dogru" and not e["not"] else
                               GRUPLAR.get(e["not"], "hatalı: " + ht.KISA_AD[ETIKETLER[e.etiket]])),
                      "ayrilan": r["tekrar"], **{k: v for k, v in r.items() if k != "tekrar"},
                      "cikarilan": "|".join(cozumle(h)), "cikarilan_uzman": "|".join(cozumle(u))})
    df = pd.DataFrame(satir).sort_values("tekrar_no").reset_index(drop=True)
    L = df.cikarilan.map(_liste)
    df["ilk_soylenen"] = [l[0] if l else ht.DOGRU for l in L]
    df["soylenen_sayisi"] = L.map(len)
    return df


def _kac(m: np.ndarray) -> tuple[int, int, str]:
    m = np.asarray(m, bool)
    return int(m.sum()), len(m), f"{int(m.sum())}/{len(m)}"


def ozet_tablosu(df: pd.DataFrame) -> pd.DataFrame:
    L = df.cikarilan.map(_liste)
    hatali = (df.hata != ht.DOGRU).to_numpy()
    satir = []

    def ekle(metrik, grup, m):
        pay, payda, kac = _kac(m)
        satir.append({"metrik": metrik, "grup": grup, "pay": pay, "payda": payda, "kaçta kaç": kac})

    h = df[hatali]
    Lh = L[hatali]
    ekle("katı: cümledeki ilk hata = etiket", "hatalı (hepsi)", (h.ilk_soylenen == h.hata).to_numpy())
    ekle("ilk iki: etiket cümlede söylendi", "hatalı (hepsi)", [x in l for x, l in zip(h.hata, Lh)])
    ekle("olumlu cümle (hiç hata söylenmedi)", "hatalı (hepsi)", (Lh.map(len) == 0).to_numpy())
    for kod in ht.HATALAR:
        m = (h.hata == kod).to_numpy()
        if m.any():
            ad = "hatalı: " + ht.KISA_AD[kod]
            ekle("katı: cümledeki ilk hata = etiket", ad, (h.ilk_soylenen[m] == kod).to_numpy())
            ekle("ilk iki: etiket cümlede söylendi", ad, [kod in l for l in Lh[m]])
    for g in GRUPLAR.values():
        m = (df.grup == g).to_numpy()
        if m.any():
            ekle("gereksiz uyarı (cümlede en az bir hata)", g, (L[m].map(len) > 0).to_numpy())
    for g in (GRUPLAR["hizli"], GRUPLAR["normal"], GRUPLAR["bakis"]):
        m = (df.grup == g).to_numpy()
        if m.any():
            ekle("hız notu çıktı", g, (df.hiz_notu[m].astype(int) == 1).to_numpy())
    ekle("hız notu çıktı (betimsel)", "hatalı (hepsi)", (h.hiz_notu.astype(int) == 1).to_numpy())
    ekle("kamera uyarısı (betimsel)", "bütün tekrarlar", (df.kamera_uyarisi.astype(int) == 1).to_numpy())
    ekle("sol kol notu (betimsel)", "bütün tekrarlar", (df.sol_kol_notu.astype(int) == 1).to_numpy())
    ekle("denetim: hasta ve uzman metninden aynı hata listesi", "bütün tekrarlar",
         (df.cikarilan == df.cikarilan_uzman).to_numpy())
    return pd.DataFrame(satir)


def ayrilma_tablosu(etiket: pd.DataFrame, df: pd.DataFrame) -> pd.DataFrame:
    """Etiketli tekrarlardan kaçı test videosunda ayrıldı (eşlendi)? Ayrılamayanlar metriklerin paydasına girmez."""
    grup = [GRUPLAR["normal"] if e == "dogru" and not n else GRUPLAR.get(n, "hatalı: " + ht.KISA_AD[ETIKETLER[e]])
            for e, n in zip(etiket.etiket, etiket["not"])]
    es = etiket.tekrar_no.isin(df.tekrar_no).to_numpy()
    satir = []
    for g in ["bütün tekrarlar"] + list(dict.fromkeys(grup)):
        m = es if g == "bütün tekrarlar" else es[[x == g for x in grup]]
        pay, payda, kac = _kac(m)
        satir.append({"metrik": "test videosunda ayrıldı", "grup": g, "pay": pay, "payda": payda, "kaçta kaç": kac})
    return pd.DataFrame(satir)


def karisiklik(df: pd.DataFrame) -> pd.DataFrame:
    sira = [ht.KISA_AD[s] for s in ht.SINIFLAR]
    k = pd.crosstab(df.hata.map(ht.KISA_AD), df.ilk_soylenen.map(ht.KISA_AD))
    k = k.reindex(index=[s for s in sira if s in k.index], columns=sira, fill_value=0)
    k.index.name, k.columns.name = "gerçek etiket", "cümledeki ilk hata"
    return k.reset_index()


def cumle_etiket(df: pd.DataFrame) -> pd.DataFrame:
    def ad(s):
        return " + ".join(ht.KISA_AD[x] for x in _liste(s)) or "–"
    return pd.DataFrame({"kişi": df.kisi, "tekrar": df.tekrar_no, "gerçek etiket": df.etiket.map(
        lambda e: ht.KISA_AD[ETIKETLER[e]]) + df["not"].map(lambda n: f" ({n})" if n else ""),
        "cümlede söylenen": df.cikarilan.map(ad), "hasta cümlesi": df.hasta_cumlesi,
        "bilgi notu": df.bilgi_notu, "kamera uyarısı": df.kamera_uyarisi, "süre (s)": df.sure_s,
        "uzman ayrıntısı": df.uzman_ayrintisi})


# ---------------------------------------------------------------- 5) çalıştırma
def calistir(kisi: str, kalibrasyon, test, etiketler, eslesme=None, cikti: Path = CIKTI,
             yalniz_onbellek: bool = False) -> pd.DataFrame | None:
    from uygulama.poz import mediapipe_surumu
    from uygulama.toplu import degerlendir_video, kalibre_et, video_bilgisi
    etiket = etiketleri_oku(etiketler)
    klasor = Path(cikti) / kisi
    fps, W, H, _ = video_bilgisi(kalibrasyon)
    kal = kalibre_et(kalibrasyon, W / H, fps, None, lm=onbellekli_pozlar(kalibrasyon, yalniz_onbellek))
    o = degerlendir_video(test, kal, lm=onbellekli_pozlar(test, yalniz_onbellek))
    es = eslestir(len(o.tekrarlar), etiket, eslesme)
    if not es:
        yol = klasor / "ayrilan_tekrarlar.csv"
        print(ayrilanlari_yaz(o, yol).to_string(index=False))
        raise SystemExit(
            f"\nTest videosunda {len(o.tekrarlar)} tekrar ayrıldı, etiketler.csv'de {len(etiket)} tekrar var.\n"
            f"Ayrılan tekrarların zamanları: {yol}\nVideoyu bu zamanlarda izleyip 'ayrilan,tekrar_no' sütunlu bir "
            "eşleşme dosyası yaz (eşlenemeyen ayrılan tekrarı yazma) ve --eslesme ile ver.")
    df = tekrar_tablosu(o, etiket, es, kisi)
    eslenmeyen = sorted(set(etiket.tekrar_no) - set(df.tekrar_no))
    oz = pd.concat([ayrilma_tablosu(etiket, df), ozet_tablosu(df)], ignore_index=True)
    bilgi = {"kisi": kisi, "tarih": dt.datetime.now().isoformat(timespec="seconds"), "mediapipe": mediapipe_surumu(),
             "kural": kal.kural_bilgi if isinstance(kal.kural_bilgi, (dict, str)) else str(kal.kural_bilgi),
             "hiz_esigi_s": o.hiz_esigi, "kamera_esigi": o.kamera_esigi,
             "kalibrasyon": {"video": str(kalibrasyon), "ayrilan": len(kal.tekrarlar),
                             "kabul": len(kal.kalibrasyon), "kalite_ret": sum(bool(k.kalite_sorunu) for k in kal.tekrarlar),
                             "tepe_acilari": [round(float(k.tepe), 1) for k in kal.kalibrasyon],
                             "uyari": kal.uyari},
             "test": {"video": str(test), "ayrilan": len(o.tekrarlar), "etiketli": len(etiket),
                      "eslesme": "dosya" if eslesme else "sıra", "eslenmeyen_etiketli": eslenmeyen,
                      "en_boy": W / H}}
    sonuclari_yaz({"tekrarlar": df, "cumle_etiket": cumle_etiket(df), "karisiklik": karisiklik(df), "ozet": oz}, klasor)
    (klasor / "bilgi.json").write_text(json.dumps(bilgi, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    birlikte_yaz(cikti)
    pd.set_option("display.width", 250)
    pd.set_option("display.max_colwidth", 90)
    print(f"Kalibrasyon: {len(kal.kalibrasyon)} tekrar kabul (ayrılan {len(kal.tekrarlar)})"
          + (f" · UYARI: {kal.uyari}" if kal.uyari else ""))
    print(f"Test: {len(o.tekrarlar)} tekrar ayrıldı, {len(df)} etiketle eşlendi"
          + (f"; eşlenmeyen etiketli: {eslenmeyen}" if eslenmeyen else ""))
    print("\n" + cumle_etiket(df).drop(columns=["uzman ayrıntısı", "kişi"]).to_string(index=False))
    print("\nKarışıklık (satır: gerçek etiket, sütun: cümledeki ilk hata):")
    print(karisiklik(df).to_string(index=False))
    print("\nÖzet:")
    print(oz.to_string(index=False))
    print(f"\nÇıktı: {klasor}")
    return df


def birlikte_yaz(cikti: Path = CIKTI) -> None:
    """Bütün kişilerin tekrarlar.csv'leri birlikte (bir kişi varsa onunla aynı)."""
    parcalar = [pd.read_csv(p, encoding="utf-8-sig", keep_default_na=False, dtype={"cikarilan": str})
                for p in sorted(Path(cikti).glob("*/tekrarlar.csv"))]
    if not parcalar:
        return
    df = pd.concat(parcalar, ignore_index=True)
    sonuclari_yaz({"ozet": ozet_tablosu(df), "karisiklik": karisiklik(df)}, cikti)
    # not: ayrılma sayıları kişi klasörlerindeki ozet.csv'de (etiket dosyası kişi başına)


def main():
    ap = argparse.ArgumentParser(description="Kendi kayıtlarla deneme (yığın modu)")
    ap.add_argument("--sablon", help="çekimden önce: karışık sırayla etiketler.csv şablonu yaz")
    ap.add_argument("--tohum", type=int, default=0, help="sıra için tohum (ikinci kişi için 1)")
    ap.add_argument("--kisi", default="kisi1")
    ap.add_argument("--kalibrasyon")
    ap.add_argument("--test")
    ap.add_argument("--etiketler")
    ap.add_argument("--eslesme", help="ayrılan tekrar sayısı tutmazsa: 'ayrilan,tekrar_no' CSV")
    ap.add_argument("--yalniz-onbellek", action="store_true",
                    help="MediaPipe noktaları önbellekte yoksa dur (yeniden üretim)")
    args = ap.parse_args()
    utf8_cikti()
    if args.sablon:
        df = sablon_yaz(args.sablon, args.tohum)
        print(df.to_string(index=False))
        print(f"\nŞablon: {args.sablon} (tohum {args.tohum}). Bu sırayı kâğıda yaz ve çekimde uy.")
        return
    if not (args.kalibrasyon and args.test and args.etiketler):
        ap.error("--kalibrasyon, --test ve --etiketler gerekli (ya da --sablon)")
    calistir(args.kisi, args.kalibrasyon, args.test, args.etiketler, args.eslesme,
             yalniz_onbellek=args.yalniz_onbellek)


if __name__ == "__main__":
    main()
