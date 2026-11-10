"""
Yığın modu: pencere açmadan aynı değerlendirme. Kendi kayıt deneyi (deneyler/kendi_kayit.py) bunu kullanır.

Kullanım:
    # 1) Kalibrasyon videosundan profil + test videosunu değerlendirme
    python -m uygulama.toplu --isim adin --kalibrasyon-video kalibrasyon.mp4 --video test.mp4
    # 2) Kayıtlı profille değerlendirme
    python -m uygulama.toplu --profil profiller/adin.npz --video test.mp4
    # 3) Sağlık kontrolü: veri setinden bir video; MediaPipe yeniden çalıştırılır ve veri setindeki iskeletle karşılaştırılır
    python -m uygulama.toplu --veri-seti ex1_Honza --kamera cam1 --yonelim 0
    # Pencere modunda aynı video: python -m uygulama.main --veri-seti ex1_Honza --kamera cam1 --yonelim 0

Kalibrasyon videosunda ayrılan bütün tekrarlar kabul edilir (en fazla 6; videoda yalnızca doğru tekrarlar
olmalı). Çıktı: oturum CSV'si (varsayılan oturumlar/<tarih>.csv) ve terminalde tablo.
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path

import cv2
import numpy as np
import pandas as pd

from cekirdek import hata_turu as ht
from cekirdek import veri
from cekirdek.konsol import sonuclari_yaz, utf8_cikti
from uygulama.oturum import EN_AZ_KALIBRASYON, HEDEF_KALIBRASYON, Oturum
from uygulama.poz import PozCikarici, mediapipe_surumu

SAGLIK = veri.KOK / "sonuclar" / "uygulama_saglik"
GECICI_VIDEO = veri.KOK / "veri" / "ara" / "videolar"
SAGLIK_EKLEMLERI = [0, 2, 5, 7, 8, 11, 12, 13, 14, 15, 16, 23, 24]


def video_kareleri(yol, bas: int = 0, son: int | None = None):
    """(kare no, BGR) üreteci; [bas, son] aralığı (son dahil)."""
    cap = cv2.VideoCapture(str(yol))
    if not cap.isOpened():
        raise FileNotFoundError(yol)
    if bas:
        cap.set(cv2.CAP_PROP_POS_FRAMES, bas)
    i = bas
    while son is None or i <= son:
        ok, kare = cap.read()
        if not ok:
            break
        yield i, kare
        i += 1
    cap.release()


def video_bilgisi(yol) -> tuple[float, int, int, int]:
    cap = cv2.VideoCapture(str(yol))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    W, H = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    return fps, W, H, n


def pozlar(yol, bas: int = 0, son: int | None = None, yazdir: bool = True) -> np.ndarray:
    """Videonun karelerinden MediaPipe noktaları, (kare, 33, 4)."""
    fps, *_ = video_bilgisi(yol)
    cikti, t0 = [], time.time()
    with PozCikarici() as poz:
        for i, kare in video_kareleri(yol, bas, son):
            cikti.append(poz.isle(kare, int(round(i * 1000 / fps))))
            if yazdir and len(cikti) % 300 == 0:
                print(f"  {len(cikti)} kare ({time.time() - t0:.0f} s)")
    return np.stack(cikti)


def oturum_isle(lm: np.ndarray, oturum: Oturum) -> None:
    for k in lm:
        oturum.kare_ekle(k)
    oturum.bitir()


def kalibre_et(yol, en_boy: float, fps: float, isim: str | None, lm: np.ndarray | None = None) -> Oturum:
    """Kalibrasyon videosu: ayrılan tekrarlar sırayla kabul edilir (en fazla HEDEF_KALIBRASYON).
    lm: videonun önceden çıkarılmış MediaPipe noktaları (verilirse MediaPipe yeniden çalıştırılmaz)."""
    o = Oturum(en_boy, fps)
    o.hedef = 10 ** 6
    oturum_isle(pozlar(yol) if lm is None else lm, o)
    for k in [t for t in o.tekrarlar if t.durum == "onay_bekliyor"][:HEDEF_KALIBRASYON]:
        o.onayla(k, True)
    if not o.kalibrasyonu_bitir():
        raise SystemExit(f"Kalibrasyon videosunda {len(o.kalibrasyon)} tekrar bulundu; en az {EN_AZ_KALIBRASYON} gerekir.")
    if isim:
        print(f"Profil kaydedildi: {o.profil_kaydet(isim)}")
    print(f"Kalibrasyon: {len(o.kalibrasyon)} tekrar" + (f" · UYARI: {o.uyari}" if o.uyari else ""))
    return o


def degerlendir_video(yol, kalibrasyon: Oturum, lm: np.ndarray | None = None) -> Oturum:
    fps, W, H, _ = video_bilgisi(yol)
    o = Oturum(W / H, fps)
    o.kalibrasyon, o.profil = kalibrasyon.kalibrasyon, kalibrasyon.profil   # profil kendi en-boy oranıyla kuruldu
    oturum_isle(pozlar(yol) if lm is None else lm, o)
    return o


# ---------------------------------------------------------------- sağlık kontrolü (veri setinden)
def veri_seti_kalibrasyonu(video_id: str, kamera: str, yonelim: int, kalibrasyon_sayisi: int = HEDEF_KALIBRASYON):
    """
    Veri setinden bir video: MediaPipe yeniden çalıştırılır, tekrarlar ayrılır, Segmentation.csv ile eşlenir ve
    etiketi doğru olan ilk `kalibrasyon_sayisi` tekrarla kalibrasyon yapılır (sağlık kontrolü ve main.py --veri-seti).
    Dönüş: sözlük (yol, fps, W, H, bas, son, lm, s, o, es, etiket, kal, poz_farki).
    """
    from deneyler.tekrar_ayirma import eslestir
    seg = veri.segmentasyon_oku()
    s = seg[(seg.video_id == video_id) & (seg.person_orientation == yonelim)].sort_values("first_frame")
    if s.empty:
        raise SystemExit("seçilen video/yönelim için etiket yok")
    yol = veri.video_cikar(video_id, kamera, GECICI_VIDEO)
    if yol is None:
        raise SystemExit("videos.zip bulunamadı")
    fps, W, H, n = video_bilgisi(yol)
    bas = max(0, int(s.first_frame.min()) - int(2 * fps))
    son = min(n - 1, int(s.last_frame.max()) + int(2 * fps))
    print(f"{video_id} {kamera} yönelim {yonelim}: kare {bas}–{son}, {W}x{H}, {fps:.1f} FPS; "
          f"MediaPipe {mediapipe_surumu()}")
    t0 = time.time()
    lm = pozlar(yol, bas, son)
    print(f"  poz: {len(lm)} kare, {time.time() - t0:.1f} s")

    # yeni MediaPipe çıktısı ile veri setindeki iskelet (aynı kareler)
    eski = veri.IskeletKaynagi().oku(video_id, kamera, "2d")[bas:bas + len(lm)]
    from cekirdek.ozellikler import ozellikler
    kol_yeni, kol_eski = ozellikler(lm, [], W / H)["kol"], ozellikler(eski, [], veri.EN_BOY)["kol"]
    fark_xy = np.abs(lm[:, SAGLIK_EKLEMLERI, :2] - eski[:, SAGLIK_EKLEMLERI, :2])
    poz_farki = {"kare": len(lm), "kişi bulunamayan kare": int(np.isnan(lm[:, 0, 0]).sum()),
                 "|Δx| medyan (görüntü oranı)": float(np.nanmedian(fark_xy[..., 0])),
                 "|Δy| medyan (görüntü oranı)": float(np.nanmedian(fark_xy[..., 1])),
                 "|Δ kol açısı| medyan (°)": float(np.nanmedian(np.abs(kol_yeni - kol_eski))),
                 "|Δ kol açısı| %95 (°)": float(np.nanpercentile(np.abs(kol_yeni - kol_eski), 95)),
                 "mediapipe": mediapipe_surumu(), "en_boy": W / H}

    o = Oturum(W / H, fps)
    o.hedef = 10 ** 6
    o.kalite_kontrol = False          # sağlık kontrolünde kadraj nedeniyle hiçbir tekrar reddedilmez
    oturum_isle(lm, o)
    et = [(int(r.first_frame) - bas, int(r.last_frame) - bas) for _, r in s.iterrows()]
    es = eslestir(et, [(k.bas, k.son) for k in o.tekrarlar])
    etiket = {j: s.iloc[i] for i, (j, _) in es.items()}
    dogru = [o.tekrarlar[j] for j in sorted(etiket) if etiket[j].correctness_score == 1]
    kal = dogru[:kalibrasyon_sayisi]
    if len(kal) < EN_AZ_KALIBRASYON:
        raise SystemExit(f"yalnızca {len(kal)} doğru tekrar eşleşti; en az {EN_AZ_KALIBRASYON} gerekir")
    for k in o.tekrarlar:
        o.onayla(k, k in kal)
    o.en_az = len(kal)
    o.kalibrasyonu_bitir()
    return {"yol": yol, "fps": fps, "W": W, "H": H, "bas": bas, "son": son, "lm": lm, "s": s, "o": o, "es": es,
            "etiket": etiket, "kal": kal, "poz_farki": poz_farki}


def veri_seti_profili(video_id: str, kamera: str, yonelim: int, klasor: Path | None = None):
    """
    Pencere modunda veri setinden bir videoyu denemek için profil. İlk çalıştırmada
    veri_seti_kalibrasyonu (MediaPipe, ~1 dk) ve profiller/veriseti_<video>_<kamera>_o<yönelim>.npz kaydı;
    sonraki çalıştırmalarda bu dosya yüklenir. Dönüş: (video yolu, profil dosyası, kalibrasyon tekrar numaraları).
    """
    from uygulama.oturum import PROFIL_KLASORU
    klasor = Path(klasor or PROFIL_KLASORU)
    ad = f"veriseti_{video_id}_{kamera}_o{yonelim}"
    profil = klasor / f"{ad}.npz"
    bilgi = klasor / f"{ad}.txt"
    yol = veri.video_cikar(video_id, kamera, GECICI_VIDEO)
    if yol is None:
        raise SystemExit("videos.zip bulunamadı")
    if not profil.exists():
        print(f"Veri setinden profil kuruluyor ({video_id} {kamera} yönelim {yonelim}); MediaPipe ~1 dk sürer...")
        d = veri_seti_kalibrasyonu(video_id, kamera, yonelim)
        d["o"].profil_kaydet(ad, klasor)
        nolar = [int(d["etiket"][j].repetition_number) for j, k in enumerate(d["o"].tekrarlar) if k in d["kal"]]
        bilgi.write_text(",".join(map(str, nolar)), encoding="utf-8")
    nolar = [int(x) for x in bilgi.read_text(encoding="utf-8").split(",") if x] if bilgi.exists() else []
    return yol, profil, nolar


def saglik_kontrolu(video_id: str, kamera: str, yonelim: int, kalibrasyon_sayisi: int = HEDEF_KALIBRASYON):
    d = veri_seti_kalibrasyonu(video_id, kamera, yonelim, kalibrasyon_sayisi)
    bas, s, o, es, etiket, kal, poz_farki = (d[k] for k in ("bas", "s", "o", "es", "etiket", "kal", "poz_farki"))
    for k in o.tekrarlar:
        if k.durum == "reddedildi":
            o._degerlendir(k)
    satir = []
    for j, k in enumerate(o.tekrarlar):
        r = etiket.get(j)
        satir.append({"ayrılan tekrar": k.no, "kare": f"{k.bas + bas}–{k.son + bas}",
                      "etiketli tekrar": int(r.repetition_number) if r is not None else "",
                      "gerçek etiket": (ht.KISA_AD.get(r.error_description or ht.DOGRU, r.error_description)
                                        if r is not None else "(etiket yok)"),
                      "rol": "kalibrasyon" if k in kal else "değerlendirme",
                      "karar": ht.KISA_AD.get(k.sonuc.karar, k.sonuc.karar) if k.sonuc else "",
                      "söylenen": " + ".join(ht.KISA_AD[h] for h in k.sonuc.soylenen) if k.sonuc else "",
                      "hasta cümlesi": k.sonuc.hasta_cumlesi if k.sonuc else "",
                      "uzman ayrıntısı": k.sonuc.uzman_ayrintisi if k.sonuc else ""})
    kacan = [int(s.iloc[i].repetition_number) for i in range(len(s)) if i not in es]
    tablo = pd.DataFrame(satir)
    ad = f"{video_id}_{kamera}_o{yonelim}"
    sonuclari_yaz({f"{ad}_tekrarlar": tablo, f"{ad}_poz_farki": pd.DataFrame([poz_farki])}, SAGLIK,
                  xlsx_adi=f"{ad}.xlsx")
    pd.set_option("display.width", 250)
    pd.set_option("display.max_colwidth", 120)
    print("\nYeni MediaPipe çıktısı ile veri setindeki iskelet:")
    for a, v in poz_farki.items():
        print(f"  {a}: {v:.4f}" if isinstance(v, float) else f"  {a}: {v}")
    print(f"\nAyrılan tekrar: {len(o.tekrarlar)} · etiketli: {len(s)} · eşleşmeyen etiketli: {kacan or '–'}")
    print(f"Kalibrasyon: {len(kal)} doğru tekrar" + (f" · UYARI: {o.uyari}" if o.uyari else ""))
    print(tablo.drop(columns=["uzman ayrıntısı"]).to_string(index=False))
    print(f"\nÇıktı: {SAGLIK}")
    return tablo, poz_farki


def main():
    ap = argparse.ArgumentParser(description="Yığın modu: pencere açmadan değerlendirme")
    ap.add_argument("--video")
    ap.add_argument("--profil")
    ap.add_argument("--kalibrasyon-video")
    ap.add_argument("--isim", help="kalibrasyon videosundan kurulan profilin adı (profiller/<isim>.npz)")
    ap.add_argument("--cikti", help="oturum CSV yolu (varsayılan oturumlar/<tarih>.csv)")
    ap.add_argument("--veri-seti", help="sağlık kontrolü: veri setinden video, ör. ex1_Honza")
    ap.add_argument("--kamera", default="cam1")
    ap.add_argument("--yonelim", type=int, default=0)
    args = ap.parse_args()
    utf8_cikti()
    if args.veri_seti:
        saglik_kontrolu(args.veri_seti, args.kamera, args.yonelim)
        return
    if not args.video or not (args.profil or args.kalibrasyon_video):
        ap.error("--video ve (--profil ya da --kalibrasyon-video) gerekli")
    if args.kalibrasyon_video:
        fps, W, H, _ = video_bilgisi(args.kalibrasyon_video)
        kal = kalibre_et(args.kalibrasyon_video, W / H, fps, args.isim)
    else:
        fps, W, H, _ = video_bilgisi(args.video)
        kal = Oturum(W / H, fps)
        kal.profil_yukle(args.profil)
    o = degerlendir_video(args.video, kal)
    yol = o.oturum_kaydet(args.cikti)
    df = pd.DataFrame(o.oturum_satirlari())
    pd.set_option("display.width", 250)
    pd.set_option("display.max_colwidth", 120)
    sut = [c for c in ("tekrar", "bas_kare", "son_kare", "karar", "hasta_cumlesi") if c in df]
    print(df[sut].to_string(index=False))
    print(f"\nOturum: {yol}")


if __name__ == "__main__":
    main()
