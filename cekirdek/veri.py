"""
REHAB26-ViewAngles verisini okuma.

Ana kaynak: orijinal Zenodo dosyaları (`veri/rehab26/`). İskeletler doğrudan
`jointSequences-mediapipe.zip` içinden okunur (zip'i açmaya gerek yok); açılmış
bir klasör de verilebilir.

Yardımcı kaynak: `veri/rehab26_kucuk.npz` (danışmanın küçültülmüş kopyası,
13 eklem, float16). Yalnızca regresyon karşılaştırması için.

Her iki kaynak da aynı biçimde döner: her tekrar için (kare, 33, 4) float64 dizi.
Son eksen: x, y (görüntüye göre 0–1, y aşağı doğru), z (MediaPipe göreli derinlik),
görünürlük. npz kaynağında tutulmayan 20 eklem NaN olur. Böylece ölçüt kodu her
iki kaynakta da MediaPipe indeksleriyle (11 sol omuz, 12 sağ omuz, ...) çalışır.

Adım 0'da doğrulanan bilgiler (bkz. ilerleme/ADIM_00.md):
  * 2B x, y piksel değil, görüntü boyutuna bölünmüş (0–1) değerlerdir.
  * Videolar 1080 x 1920 (dikey). Açı/mesafe için x *= 1080/1920 = 9/16 yapılır.
"""
from __future__ import annotations

import io
import json
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

KOK = Path(__file__).resolve().parent.parent
VERI_KLASORU = KOK / "veri" / "rehab26"
SEGMENTASYON = VERI_KLASORU / "Segmentation.csv"
ISKELET_ZIP = VERI_KLASORU / "jointSequences-mediapipe.zip"
VIDEO_ZIP = VERI_KLASORU / "videos.zip"
KUCUK_NPZ = KOK / "veri" / "rehab26_kucuk.npz"

# Videolar 1080 x 1920 (genişlik x yükseklik); normalize x'i yüksekliğe göre ölçeklemek için.
VIDEO_GENISLIK, VIDEO_YUKSEKLIK = 1080, 1920
EN_BOY = VIDEO_GENISLIK / VIDEO_YUKSEKLIK  # = 9/16 = 0.5625

KAMERALAR = ("cam1", "cam2", "cam3")
KAMERA_KONUMU = {"cam1": 0, "cam2": 45, "cam3": 90}  # görüş açısı = kamera konumu − yönelim

# Küçültülmüş npz'de tutulan 13 eklem (MediaPipe indeksleri), sırasıyla.
EKLEMLER_13 = [0, 2, 5, 7, 8, 11, 12, 13, 14, 15, 16, 23, 24]
EKLEM_SAYISI = 33
PAY = 10  # her tekrarın başına ve sonuna eklenen kare sayısı


# ---------------------------------------------------------------- yardımcılar
def gorus_acisi(kamera: str, yonelim: int) -> int:
    """Kameranın kişiyi gördüğü açı: 0 = tam önden, ±90 = profil."""
    return KAMERA_KONUMU[kamera] - int(yonelim)


def gorus_grubu(gorus: float) -> str:
    """Mutlak görüş açısına göre üç grup (önden 0–20, çapraz 30–60, profil 70–90)."""
    g = abs(gorus)
    if g <= 20:
        return "önden (0–20°)"
    if g <= 60:
        return "çapraz (30–60°)"
    return "profil (70–90°)"


def segmentasyon_oku(yol: Path | str = SEGMENTASYON) -> pd.DataFrame:
    """Segmentation.csv'yi okur. İndeks = satır numarası (0'dan, başlık hariç); etiket eşleştirme anahtarı."""
    seg = pd.read_csv(yol, sep=";")
    seg["error_description"] = seg["error_description"].fillna("")
    seg["additional_errors"] = seg["additional_errors"].fillna("")
    return seg


def iskelet_dosya_adi(video_id: str, kamera: str, tur: str = "2d") -> str:
    """Zip içindeki yol, ör. mediapipe/ex1/ex1_Honza_cam1_2d.npy"""
    ex = video_id.split("_")[0]
    return f"mediapipe/{ex}/{video_id}_{kamera}_{tur}.npy"


class IskeletKaynagi:
    """jointSequences-mediapipe.zip'i (veya açılmış klasörünü) okur. Son okunan dosyayı bellekte tutar."""

    def __init__(self, yol: Path | str = ISKELET_ZIP):
        self.yol = Path(yol)
        self._zip = zipfile.ZipFile(self.yol) if self.yol.is_file() else None
        self._son: tuple[str, np.ndarray] | None = None

    def dosyalar(self) -> list[str]:
        if self._zip is not None:
            return [i.filename for i in self._zip.infolist() if not i.is_dir()]
        return sorted(str(p.relative_to(self.yol)).replace("\\", "/") for p in self.yol.rglob("*.npy"))

    def oku(self, video_id: str, kamera: str, tur: str = "2d") -> np.ndarray:
        """Bir videonun tüm karelerini (kare, 33, 4) float64 olarak döner."""
        ad = iskelet_dosya_adi(video_id, kamera, tur)
        if self._son is not None and self._son[0] == ad:
            return self._son[1]
        if self._zip is not None:
            a = np.load(io.BytesIO(self._zip.read(ad)), allow_pickle=False)
        else:
            a = np.load(self.yol / ad, allow_pickle=False)
        self._son = (ad, a)
        return a


# ---------------------------------------------------------------- tekrarlar
@dataclass
class Tekrar:
    satir: int  # Segmentation.csv satır indeksi
    video: str
    kisi: str
    kamera: str
    yonelim: int
    tekrar_no: int
    ilk_kare: int  # dizi[0]'ın videodaki kare numarası (pay dahil)
    dizi: np.ndarray = field(repr=False)  # (kare, 33, 4) float64
    dogru: bool
    hata: str  # birincil hata kodu; doğru tekrarda "DOGRU"
    ek_hata: str  # virgülle ayrılmış ek hatalar; yoksa ""
    etiket_bas: int = 0      # dizi içinde etiketli tekrarın ilk karesi (first_frame)
    etiket_son: int | None = None  # dizi içinde etiketli tekrarın son karesinden SONRAKİ indeks (last_frame + 1)

    @property
    def gorus(self) -> int:
        return gorus_acisi(self.kamera, self.yonelim)

    @property
    def etiketli(self) -> slice:
        """Pay kareleri hariç, Segmentation.csv'deki first_frame … last_frame aralığı (Karar 3)."""
        return slice(self.etiket_bas, len(self.dizi) if self.etiket_son is None else self.etiket_son)


def _kes(a: np.ndarray, ilk: int, son: int, pay: int) -> tuple[int, int]:
    """Tekrar aralığı [ilk − pay, son + pay] (son kare dahil), dizinin sınırlarına kırpılmış."""
    b = max(0, int(ilk) - pay)
    s = min(a.shape[0], int(son) + pay + 1)
    return b, s


def _tekrar_olustur(i: int, r: pd.Series, kamera: str, b: int, dizi: np.ndarray) -> Tekrar:
    return Tekrar(
        satir=int(i), video=r.video_id, kisi=r.person, kamera=kamera,
        yonelim=int(r.person_orientation), tekrar_no=int(r.repetition_number),
        ilk_kare=b, dizi=dizi, dogru=bool(r.correctness_score == 1),
        hata=r.error_description if r.error_description else "DOGRU",
        ek_hata=r.additional_errors,
        etiket_bas=max(0, int(r.first_frame) - b),
        etiket_son=min(len(dizi), int(r.last_frame) - b + 1),
    )


def tekrarlari_yukle(egzersiz: int | list[int] = 1, kaynak: str = "zip", pay: int = PAY,
                     kameralar=KAMERALAR, iskelet_yolu: Path | str = ISKELET_ZIP,
                     npz_yolu: Path | str = KUCUK_NPZ,
                     seg: pd.DataFrame | None = None) -> list[Tekrar]:
    """
    Seçilen egzersiz(ler)in tüm tekrarlarını, her kamera için ayrı bir Tekrar olarak döner.

    kaynak = "zip": orijinal veri (ana kaynak), 33 eklem, float64.
    kaynak = "npz": rehab26_kucuk.npz (yalnızca karşılaştırma), 13 eklem dolu, diğerleri NaN.
    """
    seg = segmentasyon_oku() if seg is None else seg
    egz = [egzersiz] if isinstance(egzersiz, int) else list(egzersiz)
    secili = seg[seg.exercise_id.isin(egz)]
    if kaynak == "zip":
        return _zipten(secili, pay, kameralar, iskelet_yolu)
    if kaynak == "npz":
        return _npzden(secili, kameralar, npz_yolu)
    raise ValueError(f"bilinmeyen kaynak: {kaynak}")


def _zipten(secili, pay, kameralar, iskelet_yolu) -> list[Tekrar]:
    kaynak = IskeletKaynagi(iskelet_yolu)
    cikti = []
    for vid, grup in secili.groupby("video_id", sort=True):
        for kam in kameralar:
            a = kaynak.oku(vid, kam, "2d")
            for i, r in grup.iterrows():
                b, s = _kes(a, r.first_frame, r.last_frame, pay)
                if b >= s:
                    continue
                cikti.append(_tekrar_olustur(i, r, kam, b, a[b:s].astype(np.float64)))
    return cikti


def npz_anahtarlari(npz_yolu: Path | str = KUCUK_NPZ) -> dict[tuple[int, str], str]:
    """npz anahtarlarını (satır, kamera) -> anahtar sözlüğüne çevirir. Biçim: vid|kam|2d|veri|satirN|repR|oY"""
    d = np.load(npz_yolu)
    cikti = {}
    for k in d.files:
        if k == "__meta__":
            continue
        vid, kam, tur, _, satir, _, _ = k.split("|")
        if tur == "2d":
            cikti[(int(satir[5:]), kam)] = k
    return cikti


def _npzden(secili, kameralar, npz_yolu) -> list[Tekrar]:
    d = np.load(npz_yolu)
    meta = json.loads(str(d["__meta__"])) if "__meta__" in d.files else {}
    eklemler = meta.get("eklemler", EKLEMLER_13)
    pay = int(meta.get("pay", PAY))
    anahtarlar = npz_anahtarlari(npz_yolu)
    cikti = []
    for vid, grup in secili.groupby("video_id", sort=True):
        for kam in kameralar:
            for i, r in grup.iterrows():
                k = anahtarlar.get((int(i), kam))
                if k is None:
                    continue
                kucuk = d[k].astype(np.float64)
                dizi = np.full((kucuk.shape[0], EKLEM_SAYISI, kucuk.shape[2]), np.nan)
                dizi[:, eklemler, :] = kucuk
                b = max(0, int(r.first_frame) - pay)
                cikti.append(_tekrar_olustur(i, r, kam, b, dizi))
    return cikti


def video_adi(video_id: str, kamera: str) -> str:
    """videos.zip içindeki yol, ör. videos/ex1/ex1_Honza_cam1.mp4"""
    return f"videos/{video_id.split('_')[0]}/{video_id}_{kamera}.mp4"


def video_cikar(video_id: str, kamera: str, hedef: Path | str, video_zip: Path | str = VIDEO_ZIP) -> Path | None:
    """
    Bir videoyu videos.zip'ten hedef klasöre çıkarır (OpenCV zip içinden okuyamaz). Zip'e dokunmaz.
    Video zaten oradaysa yeniden çıkarmaz. videos.zip yoksa None döner.
    """
    video_zip = Path(video_zip)
    if not video_zip.exists():
        return None
    ad = video_adi(video_id, kamera)
    yol = Path(hedef) / ad
    if not yol.exists():
        with zipfile.ZipFile(video_zip) as z:
            z.extract(ad, hedef)
    return yol


def gruplara_ayir(tekrarlar: list[Tekrar]) -> dict[tuple[str, str, int], list[Tekrar]]:
    """(video, kamera, yönelim) gruplarına ayırır; her grup = bir kişinin bir kameradan bir yönelimdeki dizisi."""
    gruplar: dict[tuple[str, str, int], list[Tekrar]] = {}
    for t in tekrarlar:
        gruplar.setdefault((t.video, t.kamera, t.yonelim), []).append(t)
    for g in gruplar.values():
        g.sort(key=lambda t: t.satir)
    return dict(sorted(gruplar.items()))
