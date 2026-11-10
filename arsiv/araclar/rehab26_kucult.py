#!/usr/bin/env python3
"""
REHAB26-ViewAngles 'jointSequences-mediapipe.zip' dosyasını küçültür.

Yaptıkları:
  1. Zip'in içindekileri listeler  -> rehab26_icerik.txt
  2. Yalnızca seçilen egzersizlerin (varsayılan: 1 = kol abdüksiyonu, 7 = omuz ekstansiyonu)
     tekrar karelerini (Segmentation.csv'deki first_frame..last_frame, ± pay) keser
  3. Yalnızca baş/omuz/kol/kalça eklemlerini tutar (MediaPipe 33 -> 13 eklem)
  4. float16 olarak sıkıştırılmış tek bir .npz dosyasına yazar -> rehab26_kucuk.npz

Kurulum:  pip install numpy pandas
Kullanım: python rehab26_kucult.py jointSequences-mediapipe.zip Segmentation.csv
Seçenekler:
  --egzersiz 1          sadece kol abdüksiyonu (daha küçük çıktı)
  --uc-boyut            3B (world) dizileri de dahil et (çıktı büyür)
  --pay 10              tekrar başı/sonuna eklenen kare sayısı
"""
import argparse
import io
import json
import re
import sys
import zipfile
from pathlib import Path

try:
    import numpy as np
    import pandas as pd
except ImportError:
    sys.exit("Önce şunu çalıştır:  pip install numpy pandas")

# MediaPipe Pose indeksleri: burun, sol/sağ göz, sol/sağ kulak, omuzlar, dirsekler, bilekler, kalçalar
EKLEMLER = [0, 2, 5, 7, 8, 11, 12, 13, 14, 15, 16, 23, 24]


def icerik_listele(zf, cikti):
    satirlar = []
    for zi in zf.infolist():
        if zi.is_dir():
            continue
        bilgi = f"{zi.filename}\t{zi.file_size} bayt"
        if zi.filename.endswith((".npy", ".npz")) and len(satirlar) < 400:
            try:
                with zf.open(zi) as f:
                    obj = np.load(io.BytesIO(f.read()), allow_pickle=False)
                if isinstance(obj, np.ndarray):
                    bilgi += f"\tshape={obj.shape}\tdtype={obj.dtype}"
                else:
                    bilgi += "\t" + ", ".join(f"{k}:{obj[k].shape}" for k in obj.files)
            except Exception as e:
                bilgi += f"\tOKUNAMADI: {e}"
        satirlar.append(bilgi)
    Path(cikti).write_text("\n".join(satirlar), encoding="utf-8")
    return satirlar


def dizileri_oku(zf, ad):
    with zf.open(ad) as f:
        obj = np.load(io.BytesIO(f.read()), allow_pickle=False)
    if isinstance(obj, np.ndarray):
        return {"": obj}
    return {k: obj[k] for k in obj.files}


def boyut_turu(ad, anahtar):
    s = (ad + " " + anahtar).lower()
    if re.search(r"3d|world", s):
        return "3d"
    if re.search(r"2d|image|pixel", s):
        return "2d"
    return "?"


def kamera_adi(ad):
    m = re.search(r"(cam(?:era)?[ _-]?\d+|c\d+(?=[_./-]))", ad, re.I)
    return m.group(1) if m else Path(ad).stem


def eklem_sec(a):
    eksen = [i for i, n in enumerate(a.shape) if n == 33]
    if not eksen:
        return a, "eklem ekseni bulunamadı, hepsi tutuldu"
    return np.take(a, EKLEMLER, axis=eksen[0]), f"eklem ekseni={eksen[0]}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("zip_dosyasi")
    ap.add_argument("segmentasyon_csv")
    ap.add_argument("--egzersiz", type=int, nargs="+", default=[1, 7])
    ap.add_argument("--uc-boyut", action="store_true")
    ap.add_argument("--pay", type=int, default=10)
    args = ap.parse_args()

    seg = pd.read_csv(args.segmentasyon_csv, sep=";")
    seg = seg[seg.exercise_id.isin(args.egzersiz)]
    videolar = sorted(seg.video_id.unique())

    zf = zipfile.ZipFile(args.zip_dosyasi)
    satirlar = icerik_listele(zf, "rehab26_icerik.txt")
    print(f"Zip içinde {len(satirlar)} dosya var; liste rehab26_icerik.txt dosyasına yazıldı.")

    cikti, meta, eslesen = {}, {"eklemler": EKLEMLER, "pay": args.pay, "dosyalar": {}}, 0
    for zi in zf.infolist():
        ad = zi.filename
        if zi.is_dir() or not ad.endswith((".npy", ".npz")):
            continue
        vid = next((v for v in videolar if v.lower() in ad.lower()), None)
        if vid is None:
            continue
        for anahtar, a in dizileri_oku(zf, ad).items():
            tur = boyut_turu(ad, anahtar)
            if tur == "3d" and not args.uc_boyut:
                continue
            if a.ndim < 2 or not np.issubdtype(a.dtype, np.number):
                continue
            a, not_ = eklem_sec(a)
            kam = kamera_adi(ad)
            on = f"{vid}|{kam}|{tur}|{anahtar or 'veri'}"
            meta["dosyalar"][on] = {"zip_adi": ad, "orijinal_shape": list(a.shape), "not": not_}
            for i, r in seg[seg.video_id == vid].iterrows():
                b = max(0, int(r.first_frame) - args.pay)
                s = min(a.shape[0], int(r.last_frame) + args.pay + 1)
                if b >= s:
                    continue
                # i = Segmentation.csv'deki satır numarası (0'dan başlar, başlık hariç): etiketlerle eşleştirme anahtarı
                cikti[f"{on}|satir{i}|rep{int(r.repetition_number)}|o{int(r.person_orientation)}"] = a[b:s].astype(np.float16)
            eslesen += 1
            print(f"  + {ad} [{anahtar or '-'}] -> {tur}, {not_}")

    if not cikti:
        print("\nHiçbir dosya video_id ile eşleşmedi. Lütfen rehab26_icerik.txt dosyasını Claude'a gönder.")
        return
    cikti["__meta__"] = np.array(json.dumps(meta, ensure_ascii=False))
    np.savez_compressed("rehab26_kucuk.npz", **cikti)
    mb = Path("rehab26_kucuk.npz").stat().st_size / 1e6
    print(f"\n{eslesen} dizi işlendi, {len(cikti) - 1} tekrar parçası yazıldı.")
    print(f"Çıktı: rehab26_kucuk.npz ({mb:.1f} MB) ve rehab26_icerik.txt")
    if mb > 30:
        print("Dosya büyük kaldı; '--egzersiz 1' ile yalnızca kol abdüksiyonunu deneyebilirsin.")


if __name__ == "__main__":
    main()
