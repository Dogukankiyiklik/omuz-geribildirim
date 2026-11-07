"""
Omuz geri bildirim uygulaması (Adım 6): solda görüntü ve iskelet, sağda geri bildirim paneli.

Kullanım:
    # Canlı kamera: önce kalibrasyon, sonra değerlendirme
    python -m uygulama.main --isim dogukan
    python -m uygulama.main --profil profiller/dogukan.npz        # kayıtlı profille doğrudan değerlendirme
    # Video dosyası (Karar 27, birincil demo yolu)
    python -m uygulama.main --isim dogukan --kalibrasyon-video kalibrasyon.mp4 --video test.mp4
    python -m uygulama.main --profil profiller/dogukan.npz --video test.mp4
    # Veri setinden bir video (Karar 40): profil aynı videonun etiketi doğru tekrarlarından kurulur
    python -m uygulama.main --veri-seti ex1_Honza --kamera cam1 --yonelim 0

Kullanım kolaylığı:
  * Panelin altındaki düğmelere fareyle tıklanabilir; klavye kısayolu düğmede parantez içinde yazar
    (büyük/küçük harf fark etmez). Klavye için pencere seçili olmalı (bir kez tıklamak yeter).
  * Kalibrasyonda biten tekrar, --onay-suresi saniye (varsayılan 8) içinde reddedilmezse kendiliğinden
    kabul edilir; böylece kişi kameradan uzaktayken klavyeye gitmesi gerekmez. --elle-onay ile her tekrar
    için Kabul/Reddet beklenir.
Oturum sonuçları oturumlar/<tarih>.csv dosyasına, kalibrasyon profiller/<isim>.npz dosyasına yazılır.
"""
from __future__ import annotations

import argparse
import time

import cv2
import numpy as np

from cekirdek.konsol import utf8_cikti
from uygulama import panel as pn
from uygulama.oturum import EGZERSIZLER, Oturum
from uygulama.poz import PozCikarici

PENCERE = "Omuz geri bildirim"
EKRAN_Y = 760
EN_FAZLA_VIDEO_G = 1400          # 16:9 kamera 760 yükseklikte ~1351 geniş; pencere ekrana sığdırılır
DEPO_SANIYE = 25
MESAJ_SURE_S = 6.0
TUSLAR = {"e": "kabul", "h": "ret", "k": "bitir", "b": "bastan", "u": "uzman", "r": "oynat", " ": "duraklat",
          "q": "cikis", "z": "geri_al"}


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


class Girdi:
    """Klavye ve fare olaylarını tek bir eylem kuyruğunda toplar."""

    def __init__(self):
        self.kuyruk: list[str] = []
        self.dugmeler: list[pn.Dugme] = []
        self.panel_x = 0
        cv2.setMouseCallback(PENCERE, self._fare)

    def _fare(self, olay, x, y, *_):
        if olay != cv2.EVENT_LBUTTONDOWN:
            return
        for b in self.dugmeler:
            if b.icinde(x - self.panel_x, y):
                self.kuyruk.append(b.eylem)
                return

    def bekle(self, ms: int) -> list[str]:
        tus = cv2.waitKey(ms)
        if tus != -1:
            tus &= 0xFF
            if tus == 27:
                self.kuyruk.append("cikis")
            elif chr(tus).lower() in TUSLAR:
                self.kuyruk.append(TUSLAR[chr(tus).lower()])
        e, self.kuyruk = self.kuyruk, []
        return e


def ekrana_sigdir(G: int, Y: int):
    """Pencerenin ilk boyutunu ekrana sığdır (pencere elle de büyütülüp küçültülebilir)."""
    try:
        import ctypes
        u = ctypes.windll.user32
        sw, sh = u.GetSystemMetrics(0), u.GetSystemMetrics(1)
    except Exception:
        return
    k = min(1.0, 0.96 * sw / G, 0.88 * sh / Y)
    cv2.resizeWindow(PENCERE, int(G * k), int(Y * k))


def one_getir():
    """Pencereyi bir kez öne getir (klavye terminale gitmesin)."""
    try:
        cv2.setWindowProperty(PENCERE, cv2.WND_PROP_TOPMOST, 1)
        cv2.waitKey(1)
        cv2.setWindowProperty(PENCERE, cv2.WND_PROP_TOPMOST, 0)
    except cv2.error:
        pass


def boyut(W: int, H: int) -> tuple[int, int]:
    g = int(round(EKRAN_Y * W / H))
    if g > EN_FAZLA_VIDEO_G:
        return EN_FAZLA_VIDEO_G, int(round(EN_FAZLA_VIDEO_G * H / W))
    return g, EKRAN_Y


CANLI_COZUNURLUK = (1280, 720)     # main() --cozunurluk ile değiştirir


def kaynak_ac(kaynak):
    cap = cv2.VideoCapture(kaynak)
    if not cap.isOpened():
        raise SystemExit(f"Görüntü kaynağı açılamadı: {kaynak}"
                         + ("  (başka bir kamera için --kamera 1 deneyin)" if isinstance(kaynak, int) else ""))
    if isinstance(kaynak, int):
        # OpenCV varsayılanı 640x480 (4:3); geniş (16:9) sensörlü kameralar bunu kırparak verir → "zoom".
        # Geniş çözünürlük istenince kamera tam görüş alanını verir.
        G, Y = CANLI_COZUNURLUK
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, G)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, Y)
        print(f"Kamera {kaynak}: istenen {G}x{Y}, alınan "
              f"{int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
    return cap


def hazirlik(cap, poz, girdi: Girdi, sure: float, ayna: bool) -> float | None:
    """Başlangıçtaki bekleme: kişi yerine geçer. Bu bir kalibrasyon ya da ölçüm DEĞİLDİR; yalnızca
    bilgisayarın saniyede kaç kare işlediği ölçülür (zaman eşikleri buna göre). Boşluk ile atlanabilir.
    Dönüş None: kullanıcı çıkmak istedi."""
    t0, n, ilk = time.time(), 0, poz.son_ms + 1
    beyaz, yesil, kirmizi = (255, 255, 255), (120, 230, 120), (255, 110, 110)
    while time.time() - t0 < sure:
        ok, kare = cap.read()
        if not ok:
            break
        lm = poz.isle(kare, int(ilk + (time.time() - t0) * 1000))
        n += 1
        if np.isfinite(lm).any():
            pn.canli_iskelet(kare, lm)
        img = cv2.flip(kare, 1) if ayna else kare
        kisi = np.isfinite(lm[[11, 12, 23, 24], :2]).all()
        kalca = kisi and np.nanmin(lm[[23, 24], 3]) >= 0.5
        durum, renk = (("✓ Seni görüyorum, kalçaların da kadrajda. Hazırsın.", yesil) if kalca else
                       ("✗ Kalçaların görünmüyor: biraz geri çekil ya da kamerayı aşağı eğ.", kirmizi) if kisi else
                       ("✗ Seni göremiyorum: kameranın karşısına geç.", kirmizi))
        satirlar = [(f"HAZIRLIK  {sure - (time.time() - t0):.0f}", 34, beyaz, True),
                    ("Yerine geçmen için bekleme süresi. Henüz hiçbir şey kaydedilmiyor.", 20, beyaz, False),
                    ("Süre bitince KALİBRASYON başlar. Beklemek istemezsen Boşluk'a bas.", 20, beyaz, False),
                    (pn.bn.KALIBRASYON_YONERGESI, 20, (255, 230, 140), True),
                    (durum, 22, renk, True)]
        y = 16
        for metin, boy, rk, kalin in satirlar:
            img = pn.metin_yaz(img, metin, (16, y), boy, rk, kalin=kalin, kutu=True)
            y += int(boy * 1.7)
        cv2.imshow(PENCERE, img)
        if n == 1:
            ekrana_sigdir(img.shape[1], img.shape[0])
            one_getir()
        e = girdi.bekle(1)
        if "cikis" in e:
            return None
        if "duraklat" in e and n > 5:
            break
    return max(10.0, n / max(time.time() - t0, 1e-3))


def calistir(cap, oturum: Oturum, poz, girdi: Girdi, canli: bool, otomatik_onay: bool, isim: str | None,
             onay_suresi: float | None, ayna: bool = False) -> bool:
    """Bir kaynağı sonuna kadar işler. Dönüş: kullanıcı çıkmak istedi mi.
    onay_suresi: kalibrasyonda bekleyen tekrar bu kadar saniye sonra kendiliğinden kabul edilir (None: elle).
    ayna: görüntüyü ayna gibi göster (yalnızca gösterim; MediaPipe ve ölçümler aynasız kareyi kullanır)."""
    fps = oturum.fps
    G, Y = boyut(int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    girdi.panel_x = G
    depo = KareDeposu(fps)
    uzman, oynatici, durak, i, t0 = False, None, False, 0, time.time()
    mesaj, mesaj_t = "", -1e9
    lm = np.full((33, 4), np.nan)
    ilk_ms = poz.son_ms + 1000.0 / fps          # zaman damgası kaynaklar arasında artmaya devam eder
    egz = EGZERSIZLER["ex1"]
    bekleme_bas: dict[int, float] = {}          # tekrar no → onay beklemeye başladığı an

    def simdi() -> float:                       # canlıda duvar saati, videoda video zamanı
        return time.time() if canli else i / fps

    def bildir(m: str):
        nonlocal mesaj, mesaj_t
        mesaj, mesaj_t = m, time.time()

    def onayla(k, kabul: bool, kendiliginden: bool = False):
        oturum.onayla(k, kabul)
        if oturum.profil is not None:
            m = "Kalibrasyon tamam. Değerlendirme başladı: şimdi tekrarlarını yap."
            if isim:
                m += f" Profil kaydedildi: {oturum.profil_kaydet(isim).name}"
            bildir(m)
        elif kabul:
            bildir(f"Tekrar {k.no} kalibrasyona alındı{' (kendiliğinden)' if kendiliginden else ''}. "
                   f"{len(oturum.kalibrasyon)}/{oturum.hedef}")
        else:
            bildir(f"Tekrar {k.no} reddedildi.")

    first = True
    while True:
        if not durak:
            ok, kare = cap.read()
            if not ok:
                for k in oturum.bitir():
                    oynatici = _yeni_tekrar(k, oturum, depo, otomatik_onay, ayna) or oynatici
                break
            ms = ilk_ms + ((time.time() - t0) * 1000 if canli else i * 1000 / fps)
            lm = poz.isle(kare, int(ms))
            gor = cv2.resize(kare, (G, Y))
            depo.ekle(i, gor)
            for k in oturum.kare_ekle(lm):
                if k.durum == "reddedildi" and k.kalite_sorunu:
                    bildir(f"Tekrar {k.no} kalibrasyona alınmadı: {k.kalite_sorunu}. Kadraja girip tekrar yap.")
                oynatici = _yeni_tekrar(k, oturum, depo, otomatik_onay, ayna) or oynatici
            i += 1

        # kalibrasyon: bekleyen tekrarın otomatik kabulü
        b = oturum.bekleyen
        kalan = None
        if b is not None and onay_suresi is not None:
            bas = bekleme_bas.setdefault(b.no, simdi())
            kalan = onay_suresi - (simdi() - bas)
            if kalan <= 0:
                onayla(b, True, kendiliginden=True)
                b, kalan = oturum.bekleyen, None

        sol = oynatici.kare(G, Y) if oynatici is not None else None
        if sol is None:
            oynatici = None
            sol = depo.get(i - 1) if i else np.zeros((Y, G, 3), np.uint8)
            if not durak and np.isfinite(lm).any():
                pn.canli_iskelet(sol, lm)
            if ayna:
                sol = cv2.flip(sol, 1)
        if time.time() - mesaj_t > MESAJ_SURE_S:
            mesaj = ""
        sag, girdi.dugmeler = pn.panel(Y, oturum, uzman, oynatici is not None, mesaj, egz, kalan, video=not canli)
        cv2.imshow(PENCERE, pn.ekran(sol, sag))
        if first:
            ekrana_sigdir(G + pn.PANEL_G, Y)
            one_getir()
            first = False

        for e in girdi.bekle(1 if (canli or not durak) else 30):
            if e == "cikis":
                return True
            if e == "uzman":
                uzman = not uzman
                bildir("Uzman ayrıntısı " + ("açık." if uzman else "kapalı."))
            elif e == "duraklat":
                if canli:
                    bildir("Duraklatma yalnızca video dosyasında çalışır.")
                else:
                    durak = not durak
                    bildir("Duraklatıldı." if durak else "Devam.")
            elif e == "oynat":
                son = oturum.degerlendirilenler()
                if son and oturum.referans() is not None:
                    oynatici = pn.Oynatici(son[-1], oturum.referans(), oturum.kural, oturum.en_boy, depo, ayna)
                else:
                    bildir("Henüz değerlendirilen tekrar yok; oynatılacak bir şey yok.")
            elif e in ("kabul", "ret"):
                b = oturum.bekleyen
                if b is None:
                    bildir("Şu an onay bekleyen tekrar yok. Önce bir tekrar yap: kolu kaldır, indir, 1–2 sn bekle."
                           if oturum.mod == "kalibrasyon" else "Kalibrasyon bitti; onaylanacak tekrar yok.")
                else:
                    onayla(b, e == "kabul")
            elif e == "bitir":
                if oturum.mod != "kalibrasyon":
                    bildir("Kalibrasyon zaten bitti.")
                elif oturum.kalibrasyonu_bitir():
                    bildir("Kalibrasyon tamam. Değerlendirme başladı: şimdi tekrarlarını yap."
                           + (f" Profil kaydedildi: {oturum.profil_kaydet(isim).name}" if isim else ""))
                else:
                    bildir(f"Bitirmek için en az {oturum.en_az} kabul edilmiş tekrar gerekli "
                           f"(şu an {len(oturum.kalibrasyon)}).")
            elif e == "geri_al":
                k = oturum.son_kabulu_geri_al()
                if k is None:
                    bildir("Geri alınacak kalibrasyon tekrarı yok (değerlendirme başladıysa geri alınamaz).")
                else:
                    bildir(f"Tekrar {k.no} kalibrasyondan çıkarıldı. Kalibrasyon: "
                           f"{len(oturum.kalibrasyon)}/{oturum.hedef}")
            elif e == "bastan":
                if oturum.mod == "kalibrasyon":
                    oturum.kalibrasyonu_sifirla()
                    bildir("Kalibrasyon baştan başladı (0 tekrar).")
                else:
                    bildir("Kalibrasyon bitti; baştan almak için uygulamayı yeniden başlat.")
    # kaynak bitti: son oynatımı ve paneli göster
    while oynatici is not None and not oynatici.bitti:
        sag, girdi.dugmeler = pn.panel(Y, oturum, uzman, True, mesaj, egz, video=not canli)
        cv2.imshow(PENCERE, pn.ekran(oynatici.kare(G, Y), sag))
        if "cikis" in girdi.bekle(int(1000 / fps)):
            return True
    return False


def _yeni_tekrar(k, oturum: Oturum, depo, otomatik_onay: bool, ayna: bool = False):
    if k.durum == "onay_bekliyor" and otomatik_onay:
        oturum.onayla(k, True)
    if k.durum == "degerlendirildi" and oturum.referans() is not None:
        return pn.Oynatici(k, oturum.referans(), oturum.kural, oturum.en_boy, depo, ayna)
    return None


YARDIM = """
Omuz geri bildirim uygulaması açılıyor.
  * Uygulama penceresine bir kez tıklayın: klavye kısayolları ancak pencere seçiliyken çalışır.
  * Panelin altındaki düğmelere fareyle de tıklayabilirsiniz.
  * Önce HAZIRLIK ekranı gelir: yerine geçmen için bekleme süresi, hiçbir şey kaydedilmez (Boşluk ile atlanır).
  * Kalibrasyon: kolu yandan, rahatça çıkabildiğin en yüksek noktaya kaldır → indir → 1–2 sn bekle.
    Doğal ve rahat tekrarlar yap; kendini zorlama. Her tekrarda (değerlendirmede de) aynı yere bak.
    Biten tekrar {sure} kendiliğinden kabul edilir; kötü olduysa Reddet (H), yanlışlıkla kabul edildiyse
    "Son kabulü geri al" (Z). {hedef} tekrar kabul edilince değerlendirme kendiliğinden başlar.
  * Başından kalçana kadar kadrajda ol (bacakların görünmesi gerekmez).
  * Çıkmak için Q, Esc ya da Çıkış düğmesi.
"""


def main():
    utf8_cikti()
    ap = argparse.ArgumentParser(description="Omuz geri bildirim uygulaması")
    ap.add_argument("--isim", help="kalibrasyon profili adı (profiller/<isim>.npz)")
    ap.add_argument("--profil", help="kayıtlı profil (.npz); verilirse kalibrasyon atlanır")
    ap.add_argument("--kalibrasyon-video", help="kalibrasyon videosu (tekrarlar otomatik kabul edilir)")
    ap.add_argument("--video", help="değerlendirilecek video; verilmezse canlı kamera")
    ap.add_argument("--kamera", default="0",
                    help="canlı kamera numarası (varsayılan 0); --veri-seti ile veri setindeki kamera (cam1/cam2/cam3)")
    ap.add_argument("--veri-seti", help="veri setinden video, ör. ex1_Honza (Karar 40; --kamera camN --yonelim ile)")
    ap.add_argument("--yonelim", type=int, default=0, help="--veri-seti ile kişinin yönelimi (derece)")
    ap.add_argument("--cozunurluk", default="1280x720",
                    help="canlı kamera çözünürlüğü, GxY (varsayılan 1280x720; geniş görüş için). Ör. 1920x1080")
    ap.add_argument("--otomatik-onay", action="store_true", help="kalibrasyon tekrarlarını hiç sormadan kabul et")
    ap.add_argument("--onay-suresi", type=float, default=8.0,
                    help="kalibrasyonda biten tekrar bu kadar saniye içinde reddedilmezse kabul edilir (varsayılan 8)")
    ap.add_argument("--hazirlik", type=float, default=10.0,
                    help="canlı kamerada başlangıçta yerine geçme süresi, saniye (varsayılan 10; Boşluk ile atlanır)")
    ap.add_argument("--aynasiz", action="store_true",
                    help="canlı görüntüyü ayna gibi çevirme (varsayılan: ayna gibi gösterilir; ölçümü etkilemez)")
    ap.add_argument("--elle-onay", action="store_true", help="otomatik kabul yok; her tekrar için Kabul/Reddet bekle")
    args = ap.parse_args()
    if args.veri_seti:
        # Karar 40: profil, aynı videonun etiketi doğru ilk tekrarlarından (sağlık kontrolüyle aynı yol);
        # yeni yöntem kodu yok. Kalibrasyona giren tekrarların kararı adil bir sınama değildir.
        from uygulama.toplu import veri_seti_profili
        if args.profil or args.kalibrasyon_video or args.video:
            ap.error("--veri-seti, --profil / --kalibrasyon-video / --video ile birlikte kullanılmaz")
        yol, profil, nolar = veri_seti_profili(args.veri_seti, args.kamera, args.yonelim)
        args.video, args.profil = str(yol), str(profil)
        print(f"Video: {yol}\nProfil: {profil}\nKalibrasyona giren tekrarlar (etiket numarası): "
              f"{', '.join(map(str, nolar)) or '?'} — bunların kararı adil bir sınama değildir.")
    else:
        try:
            args.kamera = int(args.kamera)
        except ValueError:
            ap.error("--kamera canlıda bir sayı olmalı (cam1/cam2/cam3 yalnızca --veri-seti ile)")
    global CANLI_COZUNURLUK
    CANLI_COZUNURLUK = tuple(int(v) for v in args.cozunurluk.lower().split("x"))
    onay_suresi = None if args.elle_onay else args.onay_suresi
    if not args.profil:
        print(YARDIM.format(sure=f"{onay_suresi:.0f} sn içinde reddedilmezse" if onay_suresi else "Kabul (E) ile",
                            hedef=6))
    cv2.namedWindow(PENCERE, cv2.WINDOW_NORMAL)
    girdi = Girdi()
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
            if calistir(cap, kalibrasyon, poz, girdi, False, True, args.isim, None):
                return
            cap.release()
            if not kalibrasyon.kalibrasyonu_bitir():
                raise SystemExit(f"Kalibrasyon videosunda yeterli tekrar yok ({len(kalibrasyon.kalibrasyon)}).")
            if args.isim:
                print(f"Profil: {kalibrasyon.profil_kaydet(args.isim)}")

        canli = not args.video
        cap = kaynak_ac(args.video if args.video else args.kamera)
        W, H = cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        ayna = canli and not args.aynasiz
        fps = hazirlik(cap, poz, girdi, args.hazirlik, ayna) if canli else (cap.get(cv2.CAP_PROP_FPS) or 30.0)
        if fps is None:
            cap.release()
            cv2.destroyAllWindows()
            return
        oturum = Oturum(W / H, fps)
        if kalibrasyon is not None:
            oturum.kalibrasyon, oturum.profil = kalibrasyon.kalibrasyon, kalibrasyon.profil
            if kalibrasyon.uyari:
                oturum.uyari = kalibrasyon.uyari
        try:
            calistir(cap, oturum, poz, girdi, canli, args.otomatik_onay, args.isim, onay_suresi, ayna)
        finally:
            cap.release()
            if oturum.tekrarlar:
                print(f"Oturum kaydedildi: {oturum.oturum_kaydet()}")
            if oturum.profil is not None and args.isim and kalibrasyon is None:
                print(f"Profil: {oturum.profil_kaydet(args.isim)}")
            cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
