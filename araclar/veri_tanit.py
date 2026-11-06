"""
REHAB26-ViewAngles veri setini tanıtan betik (Adım 0).

Kullanım:
    python -m araclar.veri_tanit                 # tüm tanıtım
    python -m araclar.veri_tanit --resim         # ayrıca bir video karesine iskelet çizip kaydeder

Yazdırdıkları:
  1. Segmentation.txt (sütun açıklamaları)
  2. joint_names.txt (33 eklem, indeksleriyle)
  3. İskelet zip'indeki dosya listesi
  4. Bir dosyanın biçimi ve her sütunun en küçük / en büyük değeri
  5. Egzersiz ve hata türü başına tekrar sayıları
  6. Koordinat kontrolü: veri aralığı ve video çözünürlüğü (videos.zip içindeki MP4 başlığından)
"""
from __future__ import annotations

import argparse
import struct
import zipfile
from collections import Counter
from pathlib import Path

import numpy as np

from cekirdek import veri
from cekirdek.konsol import utf8_cikti

ORNEK_VIDEO = "ex1_Honza"
ORNEK_KAMERA = "cam1"


def baslik(metin: str) -> None:
    print("\n" + "=" * 78 + f"\n{metin}\n" + "=" * 78)


# ---------------------------------------------------------------- MP4 başlığı
def _kutular(f, bas: int, son: int):
    """MP4 kutularını (tür, veri başlangıcı, bitiş) olarak gezer."""
    konum = bas
    while konum + 8 <= son:
        f.seek(konum)
        boy, tur = struct.unpack(">I4s", f.read(8))
        bas_veri = konum + 8
        if boy == 1:
            boy = struct.unpack(">Q", f.read(8))[0]
            bas_veri += 8
        elif boy == 0:
            boy = son - konum
        if boy < 8:
            break
        yield tur.decode("latin-1"), bas_veri, konum + boy
        konum += boy


def mp4_boyutu(zf: zipfile.ZipFile, ad: str) -> dict:
    """Zip içindeki MP4'ün video izinden genişlik, yükseklik, döndürme ve FPS'i okur (dosyayı açmadan)."""
    bilgi = zf.getinfo(ad)
    sonuc = {}
    with zf.open(ad) as f:
        for tur, b, s in _kutular(f, 0, bilgi.file_size):
            if tur != "moov":
                continue
            for tur2, b2, s2 in _kutular(f, b, s):
                if tur2 != "trak":
                    continue
                iz = {}
                for tur3, b3, s3 in _kutular(f, b2, s2):
                    if tur3 == "tkhd":
                        f.seek(b3)
                        ham = f.read(s3 - b3)
                        surum = ham[0]
                        mat_bas = 40 if surum == 0 else 52
                        m = struct.unpack(">9i", ham[mat_bas:mat_bas + 36])
                        w, h = struct.unpack(">II", ham[mat_bas + 36:mat_bas + 44])
                        iz["genislik"], iz["yukseklik"] = w / 65536, h / 65536
                        a, bb = m[0] / 65536, m[1] / 65536
                        iz["dondurme"] = int(round(np.degrees(np.arctan2(bb, a)))) % 360
                    if tur3 == "mdia":
                        for tur4, b4, s4 in _kutular(f, b3, s3):
                            if tur4 == "mdhd":
                                f.seek(b4)
                                ham = f.read(s4 - b4)
                                if ham[0] == 0:
                                    zs, sure = struct.unpack(">II", ham[12:20])
                                else:
                                    zs, sure = struct.unpack(">IQ", ham[20:32])
                                iz["sure_s"] = sure / zs
                if iz.get("genislik"):
                    sonuc = iz
    return sonuc


# ---------------------------------------------------------------- bölümler
def bolum_metinler() -> None:
    baslik("1. Segmentation.txt — sütun açıklamaları")
    print((veri.VERI_KLASORU / "Segmentation.txt").read_text(encoding="utf-8").strip())
    baslik("2. joint_names.txt — 33 eklem (indeks: ad)")
    print((veri.VERI_KLASORU / "joint_names.txt").read_text(encoding="utf-8").strip())
    print("\nKüçültülmüş npz'de tutulan 13 eklem:", veri.EKLEMLER_13)


def bolum_zip(kaynak: veri.IskeletKaynagi) -> None:
    baslik("3. jointSequences-mediapipe.zip — dosya listesi")
    dosyalar = kaynak.dosyalar()
    print(f"Toplam {len(dosyalar)} dosya")
    sayac = Counter((d.split("/")[1], d.rsplit("_", 1)[1].replace(".npy", "")) for d in dosyalar)
    for (ex, tur), n in sorted(sayac.items()):
        print(f"  {ex} {tur}: {n} dosya")
    print("\nTüm dosyalar:")
    for d in sorted(dosyalar):
        print("  " + d)


def bolum_bicim(kaynak: veri.IskeletKaynagi) -> np.ndarray:
    baslik(f"4. Bir dosyanın biçimi: {veri.iskelet_dosya_adi(ORNEK_VIDEO, ORNEK_KAMERA)}")
    a = kaynak.oku(ORNEK_VIDEO, ORNEK_KAMERA, "2d")
    print(f"shape = {a.shape}  (kare, eklem, değer)   dtype = {a.dtype}")
    bos = (np.abs(a).sum(axis=(1, 2)) == 0)
    print(f"Tamamen sıfır (iskelet bulunamamış) kare sayısı: {bos.sum()}")
    dolu = a[~bos]
    print("\nSütun        en küçük     en büyük    (sıfır kareler hariç)")
    for c, ad in enumerate(["x", "y", "z", "görünürlük"]):
        print(f"  {ad:11s} {dolu[..., c].min():10.4f}  {dolu[..., c].max():10.4f}")

    print("\nTüm ex1 2B dosyaları (sıfır kareler hariç), sütun aralıkları:")
    for vid in sorted({d.split("/")[-1].rsplit("_", 2)[0] for d in kaynak.dosyalar() if "/ex1/" in d}):
        for kam in veri.KAMERALAR:
            b = kaynak.oku(vid, kam, "2d")
            bb = b[np.abs(b).sum(axis=(1, 2)) != 0]
            # yalnızca 13 ana eklemin x, y aralığı (eller ve ayaklar kadraj dışına daha çok taşar)
            x, y = bb[:, veri.EKLEMLER_13, 0], bb[:, veri.EKLEMLER_13, 1]
            print(f"  {vid:10s} {kam}: kare={b.shape[0]:6d}  x∈[{x.min():.3f}, {x.max():.3f}]  "
                  f"y∈[{y.min():.3f}, {y.max():.3f}]  boş kare={len(b) - len(bb)}")
    return a


def bolum_sayilar(seg) -> None:
    baslik("5. Egzersiz ve hata türü başına tekrar sayıları (Segmentation.csv, kamera başına)")
    print(f"Toplam satır (tekrar): {len(seg)}")
    seg = seg.assign(hata=seg.error_description.replace("", "DOGRU"))
    print("\nEgzersiz başına:")
    print(seg.groupby(["exercise_id"]).size().rename("tekrar").to_string())
    print("\nEgzersiz × birincil hata:")
    print(seg.groupby(["exercise_id", "hata"]).size().rename("tekrar").to_string())
    e1 = seg[seg.exercise_id == 1]
    print("\nEx1, kişi × birincil hata:")
    print(e1.pivot_table(index="person", columns="hata", values="video_id", aggfunc="count", fill_value=0).to_string())
    print("\nEx1, ek hatalar (additional_errors):")
    print(e1.additional_errors[e1.additional_errors != ""].value_counts().to_string())
    print(f"\nEx1, yönelim değerleri: {sorted(e1.person_orientation.unique())}")
    print(f"Ex1, (video, yönelim) dizisi sayısı: {e1.groupby(['video_id', 'person_orientation']).ngroups}")
    print(f"Ex1, ilk karesi 10'dan küçük tekrar (başta tam pay yok): {(e1.first_frame < veri.PAY).sum()}")
    print(f"3 kamera ile Ex1 tekrar parçası beklenen: {len(e1)} × 3 = {3 * len(e1)}")


def bolum_kontrol(kaynak: veri.IskeletKaynagi, seg) -> None:
    baslik("6. Kontroller: tekrar sayıları, boş kareler, koordinat biçimi")
    tekrarlar = veri.tekrarlari_yukle(1, kaynak="zip", seg=seg)
    e1 = seg[seg.exercise_id == 1]
    print(f"cekirdek.veri ile zip'ten yüklenen Ex1 tekrar parçası: {len(tekrarlar)} "
          f"(beklenen {3 * len(e1)}) -> {'TUTUYOR' if len(tekrarlar) == 3 * len(e1) else 'TUTMUYOR'}")
    sayac = Counter(t.hata for t in tekrarlar)
    print("  hata türüne göre (3 kamera dahil):", dict(sorted(sayac.items())))
    gruplar = veri.gruplara_ayir(tekrarlar)
    print(f"  (video, kamera, yönelim) grubu: {len(gruplar)}")
    bos = [(t.video, t.kamera, t.satir, int((np.abs(t.dizi).sum(axis=(1, 2)) == 0).sum()))
           for t in tekrarlar]
    bos = [b for b in bos if b[3] > 0]
    print(f"  İçinde boş (sıfır) kare olan tekrar parçası: {len(bos)}"
          + (" -> " + ", ".join(f"{v} {k} satır{s}: {n} kare" for v, k, s, n in bos[:10]) if bos else ""))

    # Kare sayısı ve video çözünürlüğü
    if not veri.VIDEO_ZIP.exists():
        print("\nvideos.zip bulunamadı; çözünürlük kontrolü atlandı.")
        return
    vz = zipfile.ZipFile(veri.VIDEO_ZIP)
    print("\nEx1 videoları (MP4 başlığından; dosya açılmadan):")
    boyutlar = Counter()
    for vid in sorted(e1.video_id.unique()):
        for kam in veri.KAMERALAR:
            ad = f"videos/ex1/{vid}_{kam}.mp4"
            b = mp4_boyutu(vz, ad)
            n_iskelet = kaynak.oku(vid, kam, "2d").shape[0]
            kayitli = f"{b['genislik']:.0f}x{b['yukseklik']:.0f}"
            dondur = b["dondurme"]
            gorunen = kayitli if dondur in (0, 180) else f"{b['yukseklik']:.0f}x{b['genislik']:.0f}"
            boyutlar[gorunen] += 1
            print(f"  {vid:10s} {kam}: kayıtlı {kayitli}, döndürme {dondur:3d}°, ekranda {gorunen}, "
                  f"süre {b['sure_s']:.1f} s ≈ {b['sure_s'] * 30:.0f} kare; iskelet kare sayısı {n_iskelet}")
    print(f"\nEkranda görünen çözünürlükler: {dict(boyutlar)}")
    print(f"Sonuç: x, y değerleri 0–1 civarında, yani piksel DEĞİL; görüntü boyutuna bölünmüş.")
    print(f"En-boy düzeltmesi: x *= genişlik/yükseklik = {veri.VIDEO_GENISLIK}/{veri.VIDEO_YUKSEKLIK} = {veri.EN_BOY}")


def kare_resmi(kaynak: veri.IskeletKaynagi, seg, cikti: Path) -> None:
    """Bir tekrarın tepe karesini videodan alıp üzerine veri setinin iskeletini çizer (oturuyor mu?)."""
    import cv2
    import tempfile

    r = seg[(seg.video_id == ORNEK_VIDEO)].iloc[0]
    a = kaynak.oku(ORNEK_VIDEO, ORNEK_KAMERA, "2d")
    kol = a[r.first_frame:r.last_frame + 1, 16, 1]
    kare = int(r.first_frame + np.argmin(kol))  # sağ bilek en yukarıdayken
    with tempfile.TemporaryDirectory() as td:
        yol = zipfile.ZipFile(veri.VIDEO_ZIP).extract(f"videos/ex1/{ORNEK_VIDEO}_{ORNEK_KAMERA}.mp4", td)
        cap = cv2.VideoCapture(yol)
        cap.set(cv2.CAP_PROP_POS_FRAMES, kare)
        ok, img = cap.read()
        cap.release()
    if not ok:
        print("Kare okunamadı.")
        return
    h, w = img.shape[:2]
    baglar = [(11, 12), (11, 13), (13, 15), (12, 14), (14, 16), (11, 23), (12, 24), (23, 24), (7, 0), (8, 0)]
    p = a[kare]
    for i, j in baglar:
        cv2.line(img, (int(p[i, 0] * w), int(p[i, 1] * h)), (int(p[j, 0] * w), int(p[j, 1] * h)), (0, 255, 0), 4)
    for i in veri.EKLEMLER_13:
        cv2.circle(img, (int(p[i, 0] * w), int(p[i, 1] * h)), 8, (0, 0, 255), -1)
    cikti.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(cikti), cv2.resize(img, (w // 2, h // 2)))
    print(f"\nİskelet bindirilmiş kare yazıldı: {cikti} (kare {kare}, x*W, y*H ile çizildi)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--resim", action="store_true", help="bir video karesine iskelet çiz")
    args = ap.parse_args()
    utf8_cikti()

    kaynak = veri.IskeletKaynagi()
    seg = veri.segmentasyon_oku()
    bolum_metinler()
    bolum_zip(kaynak)
    bolum_bicim(kaynak)
    bolum_sayilar(seg)
    bolum_kontrol(kaynak, seg)
    if args.resim:
        kare_resmi(kaynak, seg, veri.KOK / "sonuclar" / "adim0" / "iskelet_kontrol.png")


if __name__ == "__main__":
    main()
