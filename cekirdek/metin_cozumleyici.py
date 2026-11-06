"""
Anahtar kelime çıkarıcı (Adım 5, Deney 3; Deney 4'te LLM cümleleri de bununla ölçülür).

Bir Türkçe geri bildirim metninden hangi hata türlerinin söz edildiğini bulur. Sözlük tabanlıdır ve
şablonlara özel değildir (ADIM_05, önceden belirlenenler madde 8):
  1. Metin küçük harfe çevrilir (Türkçe I/İ) ve parçalara ayrılır: . ! ? ; : , ve karşıtlık
     bağlaçları (ama, ancak, fakat, ayrıca, yalnız).
  2. Olumlu parçalar ("normal aralıkta", "doğru yaptın", "devam et" vb.) hata saymaz.
  3. Her parçada her hata türü için kök + eylem/yön kuralı aranır.
  4. Dönüş: söz edilen hata türleri, metindeki ilk geçiş sırasıyla (tekrarsız).
Bilinen sınırlılık: olumsuz geçmiş zamanla kurulan olumlu cümleler ("omzun kalkmadı") ayırt edilmez,
çünkü aynı yapı hata da bildirebilir ("kolunu yeterince kaldırmadın").
"""
from __future__ import annotations

import re

OMUZ, BAS, ONE, DIRSEK, KALDIRMA = ("ERR_ELEVATED_SHOULDER", "ERR_HEAD_TO_SIDE", "ERR_ARM_FORWARD",
                                    "ERR_BENT_ARM", "ERR_LOW_ABDUCTION")

_AYIRICI = re.compile(r"[.!?;:,]|\b(?:ama|ancak|fakat|ayrıca|yalnız)\b")
_OLUMLU = re.compile(r"normal aralık|normal sınır|doğru yaptın|doğru tekrar|tekrar doğru|devam et|"
                     r"\bharika\b|\bgüzel\b|iyi iş|sorun yok|yerinde")

_KOL = r"\bkol\w*"
# Her hata türü: (kök deseni, eylem deseni). Eylem None ise kök yeter. Birden çok kural "veya" ile.
KURALLAR: dict[str, list[tuple[str, str | None]]] = {
    OMUZ: [(r"\b(?:omuz|omz)\w*", r"kula[kğ]|kald[ıi]r|kalk|silk|yüksel|yukarı|aşağı|gevşe|indir|çek")],
    BAS: [(r"\b(?:baş(?:ı|ın|ını|ının|ınla|ınız|ınızı)?|kafa\w*|boyn\w*|boyun)\b",
           r"eğ|yana|yatır|dik|bük|çevir|karşıya")],
    ONE: [(r"\b(?:öne|ileri|önüne|önde)\b|aynı hizada|aynı düzlemde|tam yana|yan düzlem", None)],
    DIRSEK: [(r"\bdirse\w*", None),
             (_KOL, r"\bbük|\bkır|kıvır|düz tut|düz olsun")],
    KALDIRMA: [(_KOL, r"daha yukarı|daha yüksek|yukarı kaldır|yeterince|\baz kald|\btam kald|\bfazla kald|"
                      r"\buzan|yükseğe|en fazla \d+ derece")],
}
_DERLI = {h: [(re.compile(k), re.compile(e) if e else None) for k, e in kl] for h, kl in KURALLAR.items()}


def kucult(metin: str) -> str:
    """Türkçe küçük harf (I → ı, İ → i)."""
    return metin.replace("I", "ı").replace("İ", "i").lower()


def parcalar(metin: str) -> list[tuple[int, str]]:
    """(başlangıç konumu, parça) listesi."""
    m = kucult(metin)
    cikti, bas = [], 0
    for a in _AYIRICI.finditer(m):
        if a.start() > bas:
            cikti.append((bas, m[bas:a.start()]))
        bas = a.end()
    if bas < len(m):
        cikti.append((bas, m[bas:]))
    return [(i, p) for i, p in cikti if p.strip()]


def _konum(parca: str, hata: str) -> int | None:
    """Parçada hata türünün ilk eşleşme konumu (kök konumu), yoksa None."""
    en = None
    for kok, eylem in _DERLI[hata]:
        for k in kok.finditer(parca):
            if eylem is None or eylem.search(parca):
                en = k.start() if en is None else min(en, k.start())
                break
    return en


def cozumle(metin: str) -> list[str]:
    """Metinde söz edilen hata türleri (ilk geçiş sırasıyla, tekrarsız)."""
    bulunan: dict[str, int] = {}
    for bas, p in parcalar(metin):
        if _OLUMLU.search(p):
            continue
        for h in _DERLI:
            k = _konum(p, h)
            if k is not None and h not in bulunan:
                bulunan[h] = bas + k
    return sorted(bulunan, key=lambda h: bulunan[h])
