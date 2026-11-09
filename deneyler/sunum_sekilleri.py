"""
Sunum için şekil adayları (Karar 38) → sonuclar/sunum/. Hangilerinin slayta gireceğine 13–15 Kasım'da karar verilir.

Sayılar yalnızca kayıtlı sonuç dosyalarından okunur; hiçbir deney yeniden çalıştırılmaz.
  1_problem.png        : bantsız (ham ölçü) ile kişiye özel açı bandı, omuz silkme tespiti (Ex1, YENI; Deney 1, 1b)
  2_fikir_aci_bandi.png: açı bandı görseli, Petra cam1 yönelim 0: doğru tekrar bandın içinde, silkmeli tekrar 5 dışında
                         (bant, çekirdekteki aci_bandi_modeli ile o grubun doğru tekrarlarından çizilir; gösterilen
                         doğru tekrar modele girmez)
  3_kalibrasyon.png    : genel bant ile kişiye özel bant (Deney 1b, v2, YENI)
  4_geri_bildirim.png  : uygulamanın ekranı, Honza sağlık kontrolü tekrar 5 (omuz) oynatımında: hasta cümlesi,
                         bindirme, kırmızı uzuv
  5_bindirme.png       : aynı tekrarın 3 karesi (kaldırırken, tepede, indirirken): turkuaz referans + kullanıcı iskeleti
  demo_yedek_veriseti.mp4: uygulama ekranının ~25 s'lik kaydı (Honza, tekrar 5–7), pencere açmadan aynı çizim koduyla
Karar 56 (--kendi-kayit): kişi 1'in kendi kaydından (veri/kendi_kayit/kisi1/, MediaPipe noktaları önbellekten)
  4b_geri_bildirim.png, 5b_bindirme.png : tekrar 7 (omuz) için 4 ve 5'in aynısı
  demo_kisi1.mp4      : tekrar 4 (doğru), 7 (omuz), 11 (baş sola), 6 (az kaldırma) ve oynatımları (~45–60 s)
  Profil profiller/kisi1.npz olarak kaydedilir (canlı demo komutu bunu kullanır). Kişisel görüntü: git'e girmez.
4 ve 5 ile video, uygulamanın kendi kodunu (uygulama/panel.py, uygulama/oturum.py) pencere açmadan çalıştırır; profil
Karar 40'taki veri seti profilidir (Honza cam1 yönelim 0, kalibrasyon tekrarları 1, 2, 3, 9, 10).

Kullanım:
    python -m deneyler.sunum_sekilleri                 # ~2 dk (MediaPipe ~45 s)
    python -m deneyler.sunum_sekilleri --uygulamasiz   # yalnızca 1–3, ~15 s
    python -m deneyler.sunum_sekilleri --kendi-kayit   # yalnızca 4b, 5b ve demo_kisi1.mp4 (Karar 56), ~3–5 dk
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path

import cv2
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from cekirdek import aci_bandi as ab  # noqa: E402
from cekirdek import geribildirim as gb  # noqa: E402
from cekirdek import veri  # noqa: E402
from cekirdek.konsol import utf8_cikti  # noqa: E402
from cekirdek.ozellikler import ozellikler  # noqa: E402

CIKTI = veri.KOK / "sonuclar" / "sunum"
S = veri.KOK / "sonuclar"
# Renkler (dataviz referans paleti, açık mod): 1. kategori mavi, 2. turuncu; nötr gri temel çizgi.
MAVI, TURUNCU, GRI = "#2a78d6", "#eb6834", "#8a8984"
METIN, METIN2, IZGARA, ZEMIN = "#0b0b0b", "#52514e", "#e4e3df", "#ffffff"
BOYUT = (13.333, 7.5)          # 16:9
DPI = 150
KISILER = ["Honza", "Mima", "Petra", "Terka", "Vasil"]


def _stil():
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 18, "axes.titlesize": 24,
                         "axes.labelsize": 19, "xtick.labelsize": 17, "ytick.labelsize": 17,
                         "axes.edgecolor": METIN2, "axes.labelcolor": METIN, "xtick.color": METIN2,
                         "ytick.color": METIN2, "axes.spines.top": False, "axes.spines.right": False,
                         "figure.facecolor": ZEMIN, "axes.facecolor": ZEMIN, "savefig.facecolor": ZEMIN})


def _oku(yol) -> pd.DataFrame:
    return pd.read_csv(yol, encoding="utf-8-sig")


def _satir(df, **kosul):
    m = np.ones(len(df), bool)
    for k, v in kosul.items():
        m &= (df[k] == v).to_numpy()
    assert m.sum() == 1, kosul
    return df[m].iloc[0]


def auc_cubuklari(ax, cubuklar: list[tuple[str, float, list[float], str]], baslik: str, deger_ustte: bool = False):
    """cubuklar: (etiket, AUC, kişi AUC'leri, renk). Kişi değerleri nokta (Karar 5).
    deger_ustte: değer yazısı çubuğun içi yerine üstüne, kişi noktalarının da üstüne yazılır (Karar 44)."""
    x = np.arange(len(cubuklar))
    for i, (ad, v, kisi, renk) in enumerate(cubuklar):
        ax.bar(i, v, width=0.56, color=renk, zorder=2)
        jit = np.linspace(-0.12, 0.12, len(kisi))
        ax.scatter(i + jit, kisi, s=70, color=ZEMIN, edgecolor=METIN, linewidth=1.4, zorder=3,
                   label="kişi başına AUC" if i == 0 else None)
        if deger_ustte:
            ax.text(i, max(v, max(kisi)) + 0.02, f"{v:.2f}".replace(".", ","), ha="center", va="bottom",
                    fontsize=30, fontweight="bold", color=METIN, zorder=4)
        else:
            ax.text(i, 0.33, f"{v:.2f}".replace(".", ","), ha="center", va="bottom", fontsize=30,
                    fontweight="bold", color=ZEMIN, zorder=4)
    ax.axhline(0.5, color=METIN2, lw=1.2, ls=":", zorder=1, label="şans düzeyi (0,5)")
    ax.set_xticks(x, [c[0] for c in cubuklar])
    ax.set_ylim(0.3, 1.16 if deger_ustte else 1.08)
    ax.set_yticks([0.4, 0.6, 0.8, 1.0], ["0,4", "0,6", "0,8", "1,0"])
    ax.set_ylabel("AUC: silkmeli tekrar ile doğru tekrarı ayırma")
    ax.yaxis.grid(True, color=IZGARA, lw=1, zorder=0)
    ax.set_title(baslik, loc="left", pad=18)
    ax.legend(loc="upper left", frameon=False, fontsize=15)


def onden_capraz_notu(oz1b: pd.DataFrame) -> str:
    """Karar 44: altyazıya önden + çapraz değerleri (deney1b/ozet.csv, v2, YENI)."""
    def v(kosul):
        x = float(_satir(oz1b, bant="v2", kosul=kosul, **{"ölçüt": "YENI"})["AUC silkme/doğru (önden+çapraz)"])
        return f"{x:.2f}".replace(".", ",")
    return f"Önden + çapraz: ham {v('bant_yok')} → bant {v('kisiye_ozel')}."


def sekil_problem(klasor: Path) -> Path:
    oz1b, k1b = _oku(S / "deney1b" / "ozet.csv"), _oku(S / "deney1b" / "kisi_auc.csv")
    c = []
    for kosul, ad, renk in [("bant_yok", "Ham ölçü\n(bant yok)", GRI), ("kisiye_ozel", "Kişiye özel\naçı bandı", MAVI)]:
        v = float(_satir(oz1b, bant="v2", kosul=kosul, **{"ölçüt": "YENI"})["AUC silkme/doğru"])
        kisi = [float(_satir(k1b, bant="v2", kosul=kosul, **{"ölçüt": "YENI"})[p]) for p in KISILER]
        c.append((ad, v, kisi, renk))
    _stil()
    fig, ax = plt.subplots(figsize=BOYUT)
    auc_cubuklari(ax, c, "Omuz silkmesi: ham ölçü yetmiyor, kişiye özel bant yetiyor")
    fig.subplots_adjust(bottom=0.19)
    fig.text(0.01, 0.015, "Ex1, kulak–omuz dikey mesafesi / gövde boyu, 5 kişi, tüm görüşler. "
             f"{onden_capraz_notu(oz1b)}\nKaynak: sonuclar/deney1b/ozet.csv, kisi_auc.csv (v2).",
             fontsize=12, color=METIN2)
    return _kaydet(fig, klasor / "1_problem.png")


def sekil_kalibrasyon(klasor: Path) -> Path:
    oz1b, k1b = _oku(S / "deney1b" / "ozet.csv"), _oku(S / "deney1b" / "kisi_auc.csv")
    c = []
    for kosul, ad, renk in [("genel_tum", "Genel bant\n(diğer 4 kişinin\ndoğru tekrarları)", GRI),
                            ("genel_tek", "Genel bant\n(başka bir kişinin\nkalibrasyonu)", GRI),
                            ("kisiye_ozel", "Kişiye özel bant\n(kendi\nkalibrasyonu)", MAVI)]:
        v = float(_satir(oz1b, bant="v2", kosul=kosul, **{"ölçüt": "YENI"})["AUC silkme/doğru"])
        kisi = [float(_satir(k1b, bant="v2", kosul=kosul, **{"ölçüt": "YENI"})[p]) for p in KISILER]
        c.append((ad, v, kisi, renk))
    _stil()
    fig, ax = plt.subplots(figsize=BOYUT)
    auc_cubuklari(ax, c, "Kalibrasyon kişiye özel olmalı", deger_ustte=True)
    fig.subplots_adjust(bottom=0.2)
    fig.text(0.01, 0.015, "Ex1, açı bandı (v2), kulak–omuz ölçütü, tüm görüşler. "
             f"{onden_capraz_notu(oz1b)} Kaynak: sonuclar/deney1b/ozet.csv, kisi_auc.csv.",
             fontsize=12, color=METIN2)
    return _kaydet(fig, klasor / "3_kalibrasyon.png")


def sekil_fikir(klasor: Path, video="ex1_Petra", kamera="cam1", yonelim=0, silkme_no=5) -> Path:
    """Açı bandı: x = kol açısı, y = kulak–omuz mesafesi (gövde boyunun %'si); yalnızca kaldırma fazı."""
    grup = [t for t in veri.tekrarlari_yukle(1) if (t.video, t.kamera, t.yonelim) == (video, kamera, yonelim)]
    f = {t.tekrar_no: {k: v[t.etiketli] for k, v in ozellikler(t.dizi, ["YENI"]).items()} for t in grup}
    dogrular = [t for t in grup if t.dogru]
    medyan = np.median([ab.tepe_acisi(f[t.tekrar_no]["kol"]) for t in dogrular])
    goster = min(dogrular, key=lambda t: abs(ab.tepe_acisi(f[t.tekrar_no]["kol"]) - medyan))
    model = ab.aci_bandi_modeli([f[t.tekrar_no] for t in dogrular if t is not goster], ["YENI"])
    silkme = next(t for t in grup if t.tekrar_no == silkme_no)
    assert silkme.hata == "ERR_ELEVATED_SHOULDER", silkme.hata
    xm = ab.kutu_merkezleri()
    p = ab.KALDIRMA
    g = model.gecerli[p]
    mu, tau = 100 * model.mu["YENI"][p], 100 * model.tau["YENI"][p]
    _stil()
    fig, ax = plt.subplots(figsize=BOYUT)
    ax.fill_between(xm[g], (mu - tau)[g], (mu + tau)[g], color=MAVI, alpha=0.16, lw=0, label="bu kişinin normal aralığı")
    ax.plot(xm[g], mu[g], color=MAVI, lw=2, ls="--")
    for t, renk, ad in [(goster, MAVI, f"doğru tekrar ({goster.tekrar_no})"),
                        (silkme, TURUNCU, f"omuz silkmeli tekrar ({silkme.tekrar_no})")]:
        ff = f[t.tekrar_no]
        faz, _ = ab.fazlar(ff["kol"])
        m = faz == p
        ax.plot(ff["kol"][m], 100 * ff["YENI"][m], color=renk, lw=2, zorder=3)
        ax.scatter(ff["kol"][m], 100 * ff["YENI"][m], s=36, color=renk, edgecolor=ZEMIN, linewidth=0.8, zorder=4,
                   label=ad)
    b = int(90 // ab.KUTU_GENISLIGI)
    if model.gecerli[p, b]:
        m90 = 100 * model.mu["YENI"][p, b]
        ax.axvline(90, color=METIN2, lw=1, ls=":")
        ax.annotate("kol 90°'deyken bu kişinin\nomzu normalde burada", xy=(90, m90), xytext=(105, m90 + 9),
                    fontsize=17, color=METIN, arrowprops=dict(arrowstyle="-", color=METIN2, lw=1.2))
    ax.set_xlim(0, 185)
    ax.set_xlabel("kol açısı (°), kolu kaldırırken")
    ax.set_ylabel("kulak ile omuz arası (gövde boyunun %'si)\n↓ küçülürse omuz kulağa yaklaşıyor")
    ax.yaxis.grid(True, color=IZGARA, lw=1, zorder=0)
    ax.set_title("Fikir: \"Kol θ°'deyken bu kişinin omzu normalde nerede?\"", loc="left", pad=18)
    ax.legend(loc="lower left", frameon=False, fontsize=16)
    fig.subplots_adjust(bottom=0.16, left=0.12)
    fig.text(0.01, 0.015, f"{video.split('_')[1]}, {kamera}, yönelim {yonelim}°. Bant: o grubun doğru tekrarlarından "
             f"(gösterilen doğru tekrar hariç, {len(dogrular) - 1} tekrar), 5°'lik kutular, μ ± τ (M39).",
             fontsize=12, color=METIN2)
    return _kaydet(fig, klasor / "2_fikir_aci_bandi.png")


def _kaydet(fig, yol: Path) -> Path:
    yol.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(yol, dpi=DPI)
    plt.close(fig)
    return yol


# ---------------------------------------------------------------- uygulama ekranı (pencere açmadan)
def uygulama_ciktilari(klasor: Path, video_id="ex1_Honza", kamera="cam1", yonelim=0, hedef_etiket=5,
                       demo_bas_s=24.3, demo_sure_s=25.0) -> list[Path]:
    """uygulama/main.calistir'daki video döngüsünün pencere açmayan karşılığı (aynı panel, oturum ve oynatım kodu)."""
    from uygulama import main as um
    from uygulama import panel as pn
    from uygulama.oturum import EGZERSIZLER, Oturum
    from uygulama.poz import PozCikarici
    from uygulama.toplu import veri_seti_profili

    yol, profil, _ = veri_seti_profili(video_id, kamera, yonelim)
    cap = cv2.VideoCapture(str(yol))
    W, H = cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    G, Y = um.boyut(int(W), int(H))
    kal = Oturum(W / H)
    kal.profil_yukle(profil)
    o = Oturum(W / H, fps)
    o.kalibrasyon, o.profil = kal.kalibrasyon, kal.profil
    egz = EGZERSIZLER["ex1"]
    depo = um.KareDeposu(fps)
    seg = veri.segmentasyon_oku()
    s = seg[(seg.video_id == video_id) & (seg.person_orientation == yonelim)]
    r = s[s.repetition_number == hedef_etiket].iloc[0]
    hedef_orta = (int(r.first_frame) + int(r.last_frame)) / 2
    bas_k, son_k = int(demo_bas_s * fps), int((demo_bas_s + demo_sure_s) * fps)
    yazici = cv2.VideoWriter(str(klasor / "demo_yedek_veriseti.mp4"), cv2.VideoWriter_fourcc(*"mp4v"), fps,
                             (G + pn.PANEL_G, Y))
    ekran_goruntusu, hedef_kayit, oynatici = None, None, None
    lm = np.full((33, 4), np.nan)
    t0, i = time.time(), 0
    with PozCikarici() as poz:
        while True:
            ok, kare = cap.read()
            if not ok:
                break
            lm = poz.isle(kare, int(round(i * 1000 / fps)))
            gor = cv2.resize(kare, (G, Y))
            depo.ekle(i, gor)
            for k in o.kare_ekle(lm):
                yeni = um._yeni_tekrar(k, o, depo, False)
                oynatici = yeni or oynatici
                if yeni is not None and k.bas <= hedef_orta <= k.son:
                    hedef_kayit = k
            i += 1
            sol = oynatici.kare(G, Y) if oynatici is not None else None
            if sol is None:
                oynatici = None
                sol = depo.get(i - 1)
                if np.isfinite(lm).any():
                    pn.canli_iskelet(sol, lm)
            sag, _ = pn.panel(Y, o, False, oynatici is not None, "", egz, None, video=True)
            img = pn.ekran(sol, sag)
            if bas_k <= i < son_k:
                yazici.write(img)
            if (ekran_goruntusu is None and oynatici is not None and oynatici.k is hedef_kayit
                    and oynatici.etiket_kare is not None and oynatici.i - 1 == oynatici.etiket_kare):
                ekran_goruntusu = img.copy()
            if i % 300 == 0:
                print(f"  {i} kare ({time.time() - t0:.0f} s)")
            if i >= son_k and ekran_goruntusu is not None:
                break
    cap.release()
    yazici.release()
    if hedef_kayit is None or ekran_goruntusu is None:
        raise SystemExit("hedef tekrar ayrılamadı ya da oynatımı yakalanamadı")
    yollar = [klasor / "demo_yedek_veriseti.mp4", klasor / "4_geri_bildirim.png"]
    cv2.imwrite(str(yollar[1]), ekran_goruntusu)
    print(f"  tekrar {hedef_kayit.no} (kare {hedef_kayit.bas}–{hedef_kayit.son}): {hedef_kayit.sonuc.hasta_cumlesi}")

    # 5) bindirme: aynı tekrarın üç karesi (anlatım fazlarının ortaları)
    yollar.append(bindirme_sekli(hedef_kayit, o, depo, G, Y, klasor / "5_bindirme.png",
                                 f"Honza, cam1, yönelim 0°, tekrar {hedef_etiket} (gerçek etiket: omuz). Zamansal hizalama "
                                 "DTW (kol açısı), geometrik: öteleme + ölçek + döndürme."))
    return yollar


def bindirme_sekli(k, o, depo, G: int, Y: int, yol: Path, altyazi: str) -> Path:
    """Bir tekrarın üç karesi (kaldırırken, tepede, indirirken): uygulamanın oynatım kodu (pn.Oynatici)."""
    from uygulama import panel as pn
    f = {kk: v[k.etiketli] for kk, v in ozellikler(k.dizi, [], o.en_boy).items()}
    faz = gb.anlatim_fazlari(f["kol"])
    secim = [(int(np.median(np.flatnonzero(faz == p))), ad) for p, ad in
             [(gb.KALDIRIRKEN, "kaldırırken"), (gb.USTTE, "tepede"), (gb.INDIRIRKEN, "indirirken")]]
    _stil()
    fig, axs = plt.subplots(1, 3, figsize=BOYUT)
    for ax, (j, ad) in zip(axs, secim):
        oy = pn.Oynatici(k, o.referans(), o.kural, o.en_boy, depo)
        oy.i = j
        img = oy.kare(G, Y)
        ax.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        ax.set_title(f"{ad} · kol {f['kol'][j]:.0f}°", fontsize=20)
        ax.axis("off")
    fig.suptitle("Referans (turkuaz) ve kullanıcı aynı karede: banttan çıkan uzuv kırmızı", x=0.01, ha="left",
                 fontsize=22)
    fig.text(0.01, 0.015, altyazi, fontsize=12, color=METIN2)
    fig.tight_layout(rect=(0, 0.04, 1, 0.93))
    return _kaydet(fig, yol)


# ---------------------------------------------------------------- Karar 56: kişi 1'in kendi kaydı
ETIKET_ADI = {"dogru": "doğru", "omuz": "omuz silkmesi", "bas": "baş eğme", "dirsek": "dirsek bükme",
              "az_kaldirma": "yetersiz kaldırma", "one_kacma": "kolun öne kaçması"}


def _baslik_karesi(G: int, Y: int, metin1: str, metin2: str) -> np.ndarray:
    from uygulama import panel as pn
    img = np.full((Y, G, 3), 24, np.uint8)
    img = pn.metin_yaz(img, metin1, (40, Y // 2 - 60), 44, (255, 255, 255), kalin=True)
    return pn.metin_yaz(img, metin2, (40, Y // 2 + 10), 30, (200, 200, 200))


def kendi_kayit_ciktilari(klasor: Path, kisi: str = "kisi1", secim=(4, 7, 11, 6), hedef_no: int = 7,
                          once_s: float = 2.0, sonra_s: float = 1.5, baslik_s: float = 1.5) -> list[Path]:
    """
    Karar 56: kişi 1'in kalibrasyonu (profil) + test videosunda seçilen tekrarlar ve oynatımları.
    uygulama_ciktilari ile aynı döngü (aynı panel, oturum ve oynatım kodu); MediaPipe noktaları Adım 7'nin
    önbelleğinden (aynı video, aynı model: veri/ara/kendi_kayit/), yoksa durur. Kalibrasyon yığın modunun
    kalibre_et'i ile (Adım 7 ile aynı) kurulur ve profiller/<kisi>.npz olarak kaydedilir; değerlendirme bu
    profili yükleyerek yapılır (canlı demo komutu ile aynı yol).
    """
    import tempfile
    from deneyler.kendi_kayit import etiketleri_oku, onbellekli_pozlar
    from uygulama import main as um
    from uygulama import panel as pn
    from uygulama.oturum import EGZERSIZLER, PROFIL_KLASORU, Oturum
    from uygulama.toplu import kalibre_et, oturum_isle, video_bilgisi, video_kareleri

    kk = veri.VERI_KOK / "kendi_kayit" / kisi
    kal_yol, test_yol = kk / "kalibrasyon.MOV", kk / "test.MOV"
    fps_k, Wk, Hk, _ = video_bilgisi(kal_yol)
    kalibre_et(kal_yol, Wk / Hk, fps_k, kisi, lm=onbellekli_pozlar(kal_yol, yalniz_onbellek=True))
    profil = PROFIL_KLASORU / f"{kisi}.npz"
    fps, W, H, _ = video_bilgisi(test_yol)
    lm_hepsi = onbellekli_pozlar(test_yol, yalniz_onbellek=True)
    prof = Oturum(W / H)
    prof.profil_yukle(profil)

    def yeni_oturum():
        o = Oturum(W / H, fps)
        o.kalibrasyon, o.profil = prof.kalibrasyon, prof.profil
        return o

    # 1. geçiş (görüntüsüz): tekrar sınırları; etiketlerle sırayla eşlenir (Adım 7'deki gibi)
    o1 = yeni_oturum()
    oturum_isle(lm_hepsi, o1)
    etiket = etiketleri_oku(kk / "etiketler.csv").set_index("tekrar_no")
    if len(o1.tekrarlar) != len(etiket):
        raise SystemExit(f"{len(o1.tekrarlar)} tekrar ayrıldı, etikette {len(etiket)}; sırayla eşlenemiyor")
    bas = {no: max(0, o1.tekrarlar[no - 1].bas - int(once_s * fps)) for no in secim}

    # 2. geçiş: uygulamanın video döngüsü (pencere açmadan)
    G, Y = um.boyut(int(W), int(H))
    egz = EGZERSIZLER["ex1"]
    depo = um.KareDeposu(fps)
    o = yeni_oturum()
    gecici = Path(tempfile.mkdtemp(prefix="demo_kisi1_"))
    yazici = {no: cv2.VideoWriter(str(gecici / f"{no}.mp4"), cv2.VideoWriter_fourcc(*"mp4v"), fps,
                                  (G + pn.PANEL_G, Y)) for no in secim}
    kayit, bitis, kapandi = {}, {}, set()
    ekran_goruntusu, sekil, oynatici = None, None, None
    yollar = []
    t0 = time.time()
    for i, kare in video_kareleri(test_yol):
        if i >= len(lm_hepsi) or len(kapandi) == len(secim):
            break
        lm = lm_hepsi[i]
        gor = cv2.resize(kare, (G, Y))
        depo.ekle(i, gor)
        for k in o.kare_ekle(lm):
            yeni = um._yeni_tekrar(k, o, depo, False)
            oynatici = yeni or oynatici
            if yeni is not None and k.no in secim:
                kayit[k.no] = k
                if k.no == hedef_no:
                    sekil = bindirme_sekli(k, o, depo, G, Y, klasor / "5b_bindirme.png",
                                           f"Kişi 1 (kendi kaydımız), test videosu tekrar {hedef_no} "
                                           f"(gerçek etiket: {ETIKET_ADI[etiket.loc[hedef_no, 'etiket']]}). "
                                           "Hizalama: DTW (kol açısı) + öteleme, ölçek, döndürme.")
        sol = oynatici.kare(G, Y) if oynatici is not None else None
        if sol is None:
            oynatici = None
            sol = depo.get(i)
            if np.isfinite(lm).any():
                pn.canli_iskelet(sol, lm)
        aktif = [no for no in secim if bas[no] <= i and no not in kapandi]
        if aktif:
            sag, _ = pn.panel(Y, o, False, oynatici is not None, "", egz, None, video=True)
            img = pn.ekran(sol, sag)
            for no in aktif:
                yazici[no].write(img)
            if (ekran_goruntusu is None and oynatici is not None and oynatici.k is kayit.get(hedef_no)
                    and oynatici.etiket_kare is not None and oynatici.i - 1 == oynatici.etiket_kare):
                ekran_goruntusu = img.copy()
        for no in aktif:                    # oynatımı bittikten sonra sonra_s saniye daha, sonra kapanır
            if no in kayit and no not in bitis and (oynatici is None or oynatici.k is not kayit[no]):
                bitis[no] = i + int(sonra_s * fps)
            if no in bitis and i >= bitis[no]:
                yazici[no].release()
                kapandi.add(no)
        if i % 600 == 0:
            print(f"  {i} kare ({time.time() - t0:.0f} s)", flush=True)
    for no in secim:
        if no not in kapandi:
            yazici[no].release()
    if ekran_goruntusu is None or sekil is None or set(kayit) != set(secim):
        raise SystemExit(f"seçilen tekrarların oynatımı yakalanamadı (bulunan: {sorted(kayit)})")
    cv2.imwrite(str(klasor / "4b_geri_bildirim.png"), ekran_goruntusu)
    yollar += [klasor / "4b_geri_bildirim.png", sekil]

    # birleştirme: istenen sırayla, her parçanın önünde kısa başlık
    hedef = klasor / f"demo_{kisi}.mp4"
    son = cv2.VideoWriter(str(hedef), cv2.VideoWriter_fourcc(*"mp4v"), fps, (G + pn.PANEL_G, Y))
    toplam = 0
    for no in secim:
        e = etiket.loc[no]
        ek = f" ({e['aciklama']})" if "aciklama" in etiket.columns and e["aciklama"] else ""
        b = _baslik_karesi(G + pn.PANEL_G, Y, f"Tekrar {no}", f"gerçek etiket: {ETIKET_ADI[e['etiket']]}{ek}")
        for _ in range(int(baslik_s * fps)):
            son.write(b)
            toplam += 1
        cap = cv2.VideoCapture(str(gecici / f"{no}.mp4"))
        while True:
            ok, f = cap.read()
            if not ok:
                break
            son.write(f)
            toplam += 1
        cap.release()
    son.release()
    for p_ in gecici.glob("*.mp4"):
        p_.unlink()
    gecici.rmdir()
    yollar.append(hedef)
    print(f"  demo: {toplam} kare, {toplam / fps:.1f} s")
    kayitli = pd.read_csv(S / "kendi_kayit" / kisi / "tekrarlar.csv", encoding="utf-8-sig",
                          keep_default_na=False).set_index("tekrar_no")
    for no in secim:
        c = kayit[no].sonuc.hasta_cumlesi
        print(f"  tekrar {no} ({etiket.loc[no, 'etiket']}): {c}\n"
              f"      Adım 7 kaydıyla {'AYNI' if c == kayitli.loc[no, 'hasta_cumlesi'] else 'FARKLI'}")
    return yollar


def main():
    ap = argparse.ArgumentParser(description="Sunum şekil adayları (Karar 38)")
    ap.add_argument("--cikti", default=str(CIKTI))
    ap.add_argument("--uygulamasiz", action="store_true", help="yalnızca 1–3 (MediaPipe çalıştırılmaz)")
    ap.add_argument("--kendi-kayit", action="store_true",
                    help="yalnızca kişi 1'in 4b, 5b ve demo_kisi1.mp4'ü (Karar 56)")
    args = ap.parse_args()
    utf8_cikti()
    klasor = Path(args.cikti)
    klasor.mkdir(parents=True, exist_ok=True)
    if args.kendi_kayit:
        for y in kendi_kayit_ciktilari(klasor):
            print(f"  {y}")
        return
    yollar = [sekil_problem(klasor), sekil_fikir(klasor), sekil_kalibrasyon(klasor)]
    if not args.uygulamasiz:
        yollar += uygulama_ciktilari(klasor)
    for y in yollar:
        print(f"  {y}")


if __name__ == "__main__":
    main()
