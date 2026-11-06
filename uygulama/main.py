"""
Omuz geri bildirim uygulaması (Adım 6): solda görüntü ve iskelet, sağda geri bildirim paneli.

Kullanım:
    # Birincil demo yolu (Karar 27): video dosyası
    python -m uygulama.main --isim dogukan --kalibrasyon-video kalibrasyon.mp4 --video test.mp4
    python -m uygulama.main --profil profiller/dogukan.npz --video test.mp4
    # Canlı kamera: önce kalibrasyon (her tekrarı E/H ile onayla), sonra değerlendirme
    python -m uygulama.main --isim dogukan
    python -m uygulama.main --profil profiller/dogukan.npz        # kayıtlı profille doğrudan değerlendirme

Tuşlar: E/H kalibrasyon tekrarını kabul/ret · K kalibrasyonu bitir (en az 5) · U uzman ayrıntısı
        R son tekrarı yeniden oynat · Boşluk duraklat (video) · Q / Esc çıkış
Oturum sonuçları oturumlar/<tarih>.csv dosyasına, kalibrasyon profiller/<isim>.npz dosyasına yazılır.
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path

import cv2
import numpy as np

from cekirdek.konsol import utf8_cikti
from uygulama import panel as pn
from uygulama.oturum import EGZERSIZLER, Oturum
from uygulama.poz import PozCikarici

PENCERE = "Omuz geri bildirim"
EKRAN_Y = 760
EN_FAZLA_VIDEO_G = 1000
DEPO_SANIYE = 25


class KareDeposu:
    """Son DEPO_SANIYE saniyenin görüntülerini JPEG olarak tutar (oynatım için)."""

    def __init__(self, fps: float):
        self.n = int(DEPO_SANIYE * fps)
        self.d: dict[int, bytes] = {}

    def ekle(self, i: int, img: np.ndarray):
        self.d[i] = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 80])[1].tobytes()
        self.d.pop(i - self.n, None)

    def get(self, i: int):
        b = self.d.get(i)
        return None if b is None else cv2.imdecode(np.frombuffer(b, np.uint8), cv2.IMREAD_COLOR)


def boyut(W: int, H: int) -> tuple[int, int]:
    g = int(round(EKRAN_Y * W / H))
    if g > EN_FAZLA_VIDEO_G:
        return EN_FAZLA_VIDEO_G, int(round(EN_FAZLA_VIDEO_G * H / W))
    return g, EKRAN_Y


def kaynak_ac(kaynak):
    cap = cv2.VideoCapture(kaynak)
    if not cap.isOpened():
        raise SystemExit(f"Görüntü kaynağı açılamadı: {kaynak}")
    return cap


def fps_olc(cap, poz, sure: float = 3.0) -> float:
    """Canlı kamerada gerçek işleme hızını ölç (zaman eşikleri buna göre). Bu sırada kişi yerini alır."""
    t0, n, ilk = time.time(), 0, poz.son_ms + 1
    while time.time() - t0 < sure:
        ok, kare = cap.read()
        if not ok:
            break
        poz.isle(kare, int(ilk + (time.time() - t0) * 1000))
        n += 1
        img = pn.metin_yaz(kare, f"Hazırlanın: {sure - (time.time() - t0):.0f}  — kameranın tam karşısına, "
                                 "2–2,5 m uzağa geçin", (20, 20), 26, (255, 255, 255), kutu=True)
        cv2.imshow(PENCERE, img)
        cv2.waitKey(1)
    return max(10.0, n / max(time.time() - t0, 1e-3))


def calistir(cap, oturum: Oturum, poz, canli: bool, otomatik_onay: bool, isim: str | None) -> bool:
    """Bir kaynağı sonuna kadar işler. Dönüş: kullanıcı çıkmak istedi mi."""
    fps = oturum.fps
    G, Y = boyut(int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    depo = KareDeposu(fps)
    uzman, oynatici, durak, mesaj, i, t0 = False, None, False, "", 0, time.time()
    lm = np.full((33, 4), np.nan)
    ilk_ms = poz.son_ms + 1000.0 / fps          # zaman damgası kaynaklar arasında artmaya devam eder
    egz = EGZERSIZLER["ex1"]
    while True:
        if not durak:
            ok, kare = cap.read()
            if not ok:
                for k in oturum.bitir():
                    oynatici = _yeni_tekrar(k, oturum, depo, otomatik_onay) or oynatici
                break
            ms = ilk_ms + ((time.time() - t0) * 1000 if canli else i * 1000 / fps)
            lm = poz.isle(kare, int(ms))
            gor = cv2.resize(kare, (G, Y))
            depo.ekle(i, gor)
            for k in oturum.kare_ekle(lm):
                oynatici = _yeni_tekrar(k, oturum, depo, otomatik_onay) or oynatici
            i += 1
        sol = oynatici.kare(G, Y) if oynatici is not None else None
        if sol is None:
            oynatici = None
            sol = depo.get(i - 1) if i else np.zeros((Y, G, 3), np.uint8)
            if not durak and np.isfinite(lm).any():
                pn.canli_iskelet(sol, lm)
        sag = pn.panel(Y, oturum, uzman, oynatici is not None, mesaj, egz)
        cv2.imshow(PENCERE, pn.ekran(sol, sag))
        tus = cv2.waitKey(1 if (canli or not durak) else 30) & 0xFF
        if tus in (ord("q"), 27):
            return True
        if tus == ord("u"):
            uzman = not uzman
        if tus == ord(" ") and not canli:
            durak = not durak
        if tus == ord("r"):
            son = oturum.degerlendirilenler()
            if son and oturum.referans() is not None:
                oynatici = pn.Oynatici(son[-1], oturum.referans(), oturum.kural, oturum.en_boy, depo)
        b = oturum.bekleyen
        if b is not None and tus in (ord("e"), ord("h")):
            oturum.onayla(b, tus == ord("e"))
            mesaj = f"Tekrar {b.no} {'kalibrasyona alındı' if tus == ord('e') else 'reddedildi'}."
            if oturum.profil is not None:
                mesaj = "Kalibrasyon tamam. Değerlendirme başladı."
                if isim:
                    mesaj += f" Profil: {oturum.profil_kaydet(isim).name}"
        if tus == ord("k") and oturum.mod == "kalibrasyon":
            if oturum.kalibrasyonu_bitir():
                mesaj = "Kalibrasyon tamam. Değerlendirme başladı."
                if isim:
                    mesaj += f" Profil: {oturum.profil_kaydet(isim).name}"
            else:
                mesaj = f"En az {oturum.en_az} kalibrasyon tekrarı gerekli."
    # kaynak bitti: son oynatımı ve paneli göster, bir tuş bekle
    while oynatici is not None and not oynatici.bitti:
        cv2.imshow(PENCERE, pn.ekran(oynatici.kare(G, Y), pn.panel(Y, oturum, uzman, True, mesaj, egz)))
        if cv2.waitKey(int(1000 / fps)) & 0xFF in (ord("q"), 27):
            return True
    return False


def _yeni_tekrar(k, oturum: Oturum, depo, otomatik_onay: bool):
    if k.durum == "onay_bekliyor" and otomatik_onay:
        oturum.onayla(k, True)
    if k.durum == "degerlendirildi" and oturum.referans() is not None:
        return pn.Oynatici(k, oturum.referans(), oturum.kural, oturum.en_boy, depo)
    return None


def main():
    ap = argparse.ArgumentParser(description="Omuz geri bildirim uygulaması")
    ap.add_argument("--isim", help="kalibrasyon profili adı (profiller/<isim>.npz)")
    ap.add_argument("--profil", help="kayıtlı profil (.npz); verilirse kalibrasyon atlanır")
    ap.add_argument("--kalibrasyon-video", help="kalibrasyon videosu (tekrarlar otomatik kabul edilir)")
    ap.add_argument("--video", help="değerlendirilecek video; verilmezse canlı kamera")
    ap.add_argument("--kamera", type=int, default=0)
    ap.add_argument("--otomatik-onay", action="store_true", help="kalibrasyon tekrarlarını sormadan kabul et")
    args = ap.parse_args()
    utf8_cikti()
    cv2.namedWindow(PENCERE, cv2.WINDOW_NORMAL)
    with PozCikarici() as poz:
        kalibrasyon = None
        if args.profil:
            cap = kaynak_ac(args.video if args.video else args.kamera)
            W, H = cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            cap.release()
            kalibrasyon = Oturum(W / H)
            kalibrasyon.profil_yukle(args.profil)
        elif args.kalibrasyon_video:
            cap = kaynak_ac(args.kalibrasyon_video)
            W, H = cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
            kalibrasyon = Oturum(W / H, fps)
            if calistir(cap, kalibrasyon, poz, False, True, args.isim):
                return
            cap.release()
            if not kalibrasyon.kalibrasyonu_bitir():
                raise SystemExit(f"Kalibrasyon videosunda yeterli tekrar yok ({len(kalibrasyon.kalibrasyon)}).")
            if args.isim:
                print(f"Profil: {kalibrasyon.profil_kaydet(args.isim)}")

        canli = not args.video
        cap = kaynak_ac(args.video if args.video else args.kamera)
        W, H = cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        fps = fps_olc(cap, poz) if canli else (cap.get(cv2.CAP_PROP_FPS) or 30.0)
        oturum = Oturum(W / H, fps)
        if kalibrasyon is not None:
            oturum.kalibrasyon, oturum.profil = kalibrasyon.kalibrasyon, kalibrasyon.profil
            if kalibrasyon.uyari:
                oturum.uyari = kalibrasyon.uyari
        try:
            calistir(cap, oturum, poz, canli, args.otomatik_onay, args.isim)
        finally:
            cap.release()
            if oturum.tekrarlar:
                print(f"Oturum kaydedildi: {oturum.oturum_kaydet()}")
            if oturum.profil is not None and args.isim and kalibrasyon is None:
                print(f"Profil: {oturum.profil_kaydet(args.isim)}")
            cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
