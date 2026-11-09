"""
Sağlayıcıdan bağımsız LLM arayüzü (Adım 8 / Deney 4 hazırlığı; Güncelleme 08, Karar 35).

Bu dosyada istem metni ve deney YOKTUR; onlar Adım 8'in güncellemesiyle gelecek (deneyler/istemler/).
Burada yalnızca altyapı var:
  * Istek / Yanit        : bir istek (sistem + kullanıcı metni, model, sıcaklık = 0) ve yanıtı.
  * Saglayici            : soyut sınıf. GeminiSaglayici (Google AI Studio ücretsiz katmanı, REST; anahtar
                           GEMINI_API_KEY ortam değişkeninde ya da .env dosyasında), OllamaSaglayici (yerel),
                           SahteSaglayici (testler, ağ yok).
  * Onbellek             : her yanıt sonuclar/deney4/onbellek.jsonl dosyasına bir satır olarak eklenir; aynı istek
                           tekrar sorulursa ağa gidilmez (PLAN Adım 8). Anahtar: sağlayıcı, model, metinler ve
                           üretim ayarlarının SHA-256'sı.
  * LLMIstemcisi         : önbellek + istekler arası en kısa bekleme (dakikalık sınır için) + hız sınırı (429)
                           ve geçici sunucu hatalarında üstel beklemeyle yeniden deneme.

Ücretli API kullanılmaz (CLAUDE.md). Gemini'nin güncel ücretsiz modelleri ve sınırları sık değişir; model adı
burada sabit değildir, çağıran verir. Kontrol: https://ai.google.dev/gemini-api/docs/rate-limits
Yeni paket gerekmez: istekler standart kütüphanedeki urllib ile gönderilir.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import time
import urllib.error
import urllib.request
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Callable

from cekirdek.veri import KOK

ONBELLEK_YOLU = KOK / "sonuclar" / "deney4" / "onbellek.jsonl"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
OLLAMA_URL = "http://localhost:11434/api/chat"


# ---------------------------------------------------------------- istek ve yanıt
@dataclass(frozen=True)
class Istek:
    kullanici: str
    model: str
    sistem: str = ""
    sicaklik: float = 0.0               # PLAN Adım 8: temperature = 0
    en_fazla_token: int | None = None
    tohum: int = 0                      # destekleyen sağlayıcıda (Ollama) üretim tohumu
    dusunme: str | int | None = None    # Gemini "düşünme": int → thinkingBudget (2.5 modelleri; 0 = kapalı),
                                        # str → thinkingLevel (ör. "minimal"); None → modelin varsayılanı (Karar 36)

    def anahtar(self, saglayici: str) -> str:
        d = {"saglayici": saglayici, **asdict(self)}
        if d["dusunme"] is None:        # eski anahtarlar değişmesin
            del d["dusunme"]
        return hashlib.sha256(json.dumps(d, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


@dataclass
class Yanit:
    metin: str
    saglayici: str
    model: str
    sure_s: float
    onbellekten: bool = False
    deneme: int = 1
    bitis_nedeni: str = ""
    ham: dict | None = field(default=None, repr=False)


class LLMHatasi(RuntimeError):
    pass


class GeciciHata(LLMHatasi):
    """Yeniden denenebilir: hız sınırı (429) ya da geçici sunucu hatası (5xx). bekle_s: sağlayıcının önerdiği bekleme."""

    def __init__(self, mesaj: str, bekle_s: float | None = None):
        super().__init__(mesaj)
        self.bekle_s = bekle_s


# ---------------------------------------------------------------- sağlayıcılar
class Saglayici(ABC):
    ad: str = "soyut"

    @abstractmethod
    def gonder(self, istek: Istek) -> tuple[str, str, dict]:
        """Dönüş: (metin, bitiş nedeni, ham yanıt). Geçici hatada GeciciHata, kalıcı hatada LLMHatasi."""


def _post_json(url: str, govde: dict, basliklar: dict, zaman_asimi: float) -> dict:
    veri = json.dumps(govde, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=veri, method="POST",
                                 headers={"Content-Type": "application/json", **basliklar})
    try:
        with urllib.request.urlopen(req, timeout=zaman_asimi) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        metin = e.read().decode("utf-8", "replace")
        if e.code == 429 or e.code >= 500:
            raise GeciciHata(f"HTTP {e.code}: {metin[:300]}", _bekleme_onerisi(e, metin)) from None
        raise LLMHatasi(f"HTTP {e.code}: {metin[:500]}") from None
    except (urllib.error.URLError, TimeoutError) as e:
        raise GeciciHata(f"bağlantı hatası: {e}") from None


def _bekleme_onerisi(e: urllib.error.HTTPError, metin: str) -> float | None:
    """Retry-After başlığı ya da Gemini'nin RetryInfo.retryDelay alanı (ör. "17s")."""
    ra = e.headers.get("Retry-After") if e.headers else None
    if ra:
        try:
            return float(ra)
        except ValueError:
            pass
    try:
        for d in json.loads(metin).get("error", {}).get("details", []):
            if str(d.get("@type", "")).endswith("RetryInfo") and str(d.get("retryDelay", "")).endswith("s"):
                return float(d["retryDelay"][:-1])
    except (ValueError, AttributeError, TypeError):
        pass
    return None


def env_oku(ad: str, env_yolu: Path = KOK / ".env") -> str | None:
    """Önce ortam değişkeni, yoksa proje kökündeki .env (git'e girmez) içindeki AD=deger satırı."""
    if os.environ.get(ad):
        return os.environ[ad]
    if Path(env_yolu).exists():
        for satir in Path(env_yolu).read_text(encoding="utf-8").splitlines():
            a, _, b = satir.strip().partition("=")
            if a.strip() == ad and b.strip():
                return b.strip().strip('"').strip("'")
    return None


class GeminiSaglayici(Saglayici):
    ad = "gemini"

    def __init__(self, api_anahtari: str | None = None, zaman_asimi: float = 60.0):
        self.api_anahtari = api_anahtari or env_oku("GEMINI_API_KEY")
        if not self.api_anahtari:
            raise LLMHatasi("GEMINI_API_KEY bulunamadı (ortam değişkeni ya da .env). Google AI Studio'dan "
                            "ücretsiz bir anahtar alın.")
        self.zaman_asimi = zaman_asimi

    @staticmethod
    def govde(istek: Istek) -> dict:
        g = {"contents": [{"role": "user", "parts": [{"text": istek.kullanici}]}],
             "generationConfig": {"temperature": istek.sicaklik}}
        if istek.sistem:
            g["systemInstruction"] = {"parts": [{"text": istek.sistem}]}
        if istek.en_fazla_token:
            g["generationConfig"]["maxOutputTokens"] = istek.en_fazla_token
        if isinstance(istek.dusunme, bool):
            raise ValueError("dusunme: int (bütçe) ya da str (düzey) olmalı")
        if isinstance(istek.dusunme, int):
            g["generationConfig"]["thinkingConfig"] = {"thinkingBudget": istek.dusunme}
        elif isinstance(istek.dusunme, str):
            g["generationConfig"]["thinkingConfig"] = {"thinkingLevel": istek.dusunme}
        return g

    def modeller(self) -> list[dict]:
        """Anahtarın erişebildiği modeller (GET models; ücretsiz, generateContent kotasını harcamaz)."""
        req = urllib.request.Request(GEMINI_URL.split("/models/")[0] + "/models?pageSize=1000",
                                     headers={"x-goog-api-key": self.api_anahtari})
        with urllib.request.urlopen(req, timeout=self.zaman_asimi) as r:
            return json.loads(r.read().decode("utf-8")).get("models", [])

    @staticmethod
    def coz(ham: dict) -> tuple[str, str]:
        aday = (ham.get("candidates") or [{}])[0]
        parcalar = aday.get("content", {}).get("parts", [])
        metin = "".join(p.get("text", "") for p in parcalar if not p.get("thought"))
        neden = aday.get("finishReason", "") or ham.get("promptFeedback", {}).get("blockReason", "")
        return metin.strip(), str(neden)

    def gonder(self, istek: Istek) -> tuple[str, str, dict]:
        ham = _post_json(GEMINI_URL.format(model=istek.model), self.govde(istek),
                         {"x-goog-api-key": self.api_anahtari}, self.zaman_asimi)
        metin, neden = self.coz(ham)
        return metin, neden, ham


class OllamaSaglayici(Saglayici):
    ad = "ollama"

    def __init__(self, url: str = OLLAMA_URL, zaman_asimi: float = 300.0):
        self.url, self.zaman_asimi = url, zaman_asimi

    @staticmethod
    def govde(istek: Istek) -> dict:
        mesajlar = ([{"role": "system", "content": istek.sistem}] if istek.sistem else []) + \
                   [{"role": "user", "content": istek.kullanici}]
        secenek = {"temperature": istek.sicaklik, "seed": istek.tohum}
        if istek.en_fazla_token:
            secenek["num_predict"] = istek.en_fazla_token
        return {"model": istek.model, "messages": mesajlar, "stream": False, "options": secenek}

    def gonder(self, istek: Istek) -> tuple[str, str, dict]:
        ham = _post_json(self.url, self.govde(istek), {}, self.zaman_asimi)
        return ham.get("message", {}).get("content", "").strip(), str(ham.get("done_reason", "")), ham


class SahteSaglayici(Saglayici):
    """Testler için: ağ yok. yanitla(istek) metni üretir; hatalar listesi sırayla fırlatılır."""
    ad = "sahte"

    def __init__(self, yanitla: Callable[[Istek], str] | None = None, hatalar: list[Exception] | None = None):
        self.yanitla = yanitla or (lambda i: f"yanıt: {i.kullanici}")
        self.hatalar = list(hatalar or [])
        self.cagri = 0

    def gonder(self, istek: Istek) -> tuple[str, str, dict]:
        self.cagri += 1
        if self.hatalar:
            raise self.hatalar.pop(0)
        return self.yanitla(istek), "STOP", {}


class YalnizOnbellekSaglayici(Saglayici):
    """Yeniden üretim için (Karar 53): ağa hiç gitmez. Önbellek anahtarı gerçek sağlayıcının adıyla kurulsun diye
    `ad` verilir; önbellekte olmayan her istek kalıcı hata (LLMHatasi) verir."""

    def __init__(self, ad: str = "gemini"):
        self.ad = ad
        self.cagri = 0

    def gonder(self, istek: Istek) -> tuple[str, str, dict]:
        self.cagri += 1
        raise LLMHatasi("önbellekte yok (yalnızca önbellek kipi; istek gönderilmedi)")


def saglayici_olustur(ad: str, **kw) -> Saglayici:
    tur = {"gemini": GeminiSaglayici, "ollama": OllamaSaglayici, "sahte": SahteSaglayici}
    if ad not in tur:
        raise ValueError(f"bilinmeyen sağlayıcı: {ad}; geçerli: {list(tur)}")
    return tur[ad](**kw)


# ---------------------------------------------------------------- önbellek
class Onbellek:
    """Ekleme kipinde JSONL. Her satır: anahtar, zaman, sağlayıcı, istek, yanıt metni, bitiş nedeni, süre."""

    def __init__(self, yol: Path | str | None = ONBELLEK_YOLU):
        self.yol = Path(yol) if yol else None
        self._d: dict[str, dict] = {}
        if self.yol and self.yol.exists():
            for satir in self.yol.read_text(encoding="utf-8").splitlines():
                if satir.strip():
                    k = json.loads(satir)
                    self._d[k["anahtar"]] = k

    def __len__(self) -> int:
        return len(self._d)

    def __contains__(self, anahtar: str) -> bool:
        return anahtar in self._d

    def al(self, anahtar: str) -> dict | None:
        return self._d.get(anahtar)

    def koy(self, anahtar: str, saglayici: str, istek: Istek, y: Yanit) -> None:
        kayit = {"anahtar": anahtar, "zaman": dt.datetime.now().isoformat(timespec="seconds"),
                 "saglayici": saglayici, "istek": asdict(istek), "metin": y.metin,
                 "bitis_nedeni": y.bitis_nedeni, "sure_s": round(y.sure_s, 3), "deneme": y.deneme}
        self._d[anahtar] = kayit
        if self.yol:
            self.yol.parent.mkdir(parents=True, exist_ok=True)
            with open(self.yol, "a", encoding="utf-8") as f:
                f.write(json.dumps(kayit, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------- istemci
class LLMIstemcisi:
    """
    sor(istek): önbellekte varsa oradan; yoksa sağlayıcıya gönderir.
      * en_kisa_aralik_s: iki ağ isteği arasındaki en kısa süre (ör. dakikada 10 istek → 6 s).
      * GeciciHata'da bekler ve yeniden dener: sağlayıcının önerdiği süre, yoksa taban·2^(deneme−1) (en fazla
        en_uzun_bekleme_s); en_fazla_deneme sonunda hata yükselir.
      * Boş yanıt önbelleğe yazılmaz (sonraki çalıştırmada tekrar sorulur) ve LLMHatasi verir.
    """

    def __init__(self, saglayici: Saglayici, onbellek: Onbellek | None = None, en_kisa_aralik_s: float = 0.0,
                 en_fazla_deneme: int = 6, taban_bekleme_s: float = 5.0, en_uzun_bekleme_s: float = 120.0,
                 uyku: Callable[[float], None] = time.sleep, saat: Callable[[], float] = time.monotonic):
        self.saglayici = saglayici
        self.onbellek = onbellek if onbellek is not None else Onbellek(None)
        self.en_kisa_aralik_s, self.en_fazla_deneme = en_kisa_aralik_s, en_fazla_deneme
        self.taban_bekleme_s, self.en_uzun_bekleme_s = taban_bekleme_s, en_uzun_bekleme_s
        self._uyku, self._saat = uyku, saat
        self._son_istek: float | None = None
        self.ag_istegi = 0

    def _aralik_bekle(self) -> None:
        if self._son_istek is not None and self.en_kisa_aralik_s > 0:
            kalan = self.en_kisa_aralik_s - (self._saat() - self._son_istek)
            if kalan > 0:
                self._uyku(kalan)

    def sor(self, istek: Istek) -> Yanit:
        anahtar = istek.anahtar(self.saglayici.ad)
        k = self.onbellek.al(anahtar)
        if k is not None:
            return Yanit(k["metin"], self.saglayici.ad, istek.model, float(k.get("sure_s", 0.0)), True,
                         int(k.get("deneme", 1)), k.get("bitis_nedeni", ""))
        for deneme in range(1, self.en_fazla_deneme + 1):
            self._aralik_bekle()
            t0 = self._saat()
            self._son_istek = t0
            self.ag_istegi += 1
            try:
                metin, neden, ham = self.saglayici.gonder(istek)
            except GeciciHata as e:
                if deneme == self.en_fazla_deneme:
                    raise LLMHatasi(f"{self.en_fazla_deneme} denemede başarısız: {e}") from e
                if e.bekle_s is not None and e.bekle_s > self.en_uzun_bekleme_s:
                    # Sağlayıcı çok uzun bekleme istiyor (ör. günlük kota bitti, "retry in 20h"): beklemek boşuna.
                    raise LLMHatasi(f"kota: sağlayıcı {e.bekle_s / 3600:.1f} sa beklemeyi öneriyor; durduruldu. {e}") from e
                bekle = e.bekle_s if e.bekle_s is not None else self.taban_bekleme_s * 2 ** (deneme - 1)
                self._uyku(min(bekle, self.en_uzun_bekleme_s))
                continue
            y = Yanit(metin, self.saglayici.ad, istek.model, self._saat() - t0, False, deneme, neden, ham)
            if not metin:
                raise LLMHatasi(f"boş yanıt (bitiş nedeni: {neden or '?'})")
            self.onbellek.koy(anahtar, self.saglayici.ad, istek, y)
            return y
        raise LLMHatasi("ulaşılmaz")
