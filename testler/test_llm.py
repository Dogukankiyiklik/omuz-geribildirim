"""cekirdek/llm.py (ağ yok) ve Deney 4 örneklemi."""
import json

import pandas as pd
import pytest

from cekirdek import hata_turu as ht
from cekirdek import llm


class Saat:
    def __init__(self):
        self.t, self.uykular = 0.0, []

    def __call__(self):
        return self.t

    def uyu(self, s):
        self.uykular.append(s)
        self.t += s


def _istemci(s, yol=None, **kw):
    saat = Saat()
    return llm.LLMIstemcisi(s, llm.Onbellek(yol), uyku=saat.uyu, saat=saat, **kw), saat


def test_onbellek_ikinci_istekte_aga_gitmez(tmp_path):
    yol = tmp_path / "onbellek.jsonl"
    s = llm.SahteSaglayici()
    ist, _ = _istemci(s, yol)
    i = llm.Istek("merhaba", model="m")
    a = ist.sor(i)
    b = ist.sor(i)
    assert s.cagri == 1 and not a.onbellekten and b.onbellekten and a.metin == b.metin
    # dosyadan yeni bir istemci: yine ağa gitmez
    s2 = llm.SahteSaglayici()
    ist2, _ = _istemci(s2, yol)
    assert ist2.sor(i).onbellekten and s2.cagri == 0
    satirlar = yol.read_text(encoding="utf-8").splitlines()
    assert len(satirlar) == 1 and json.loads(satirlar[0])["istek"]["sicaklik"] == 0.0


def test_anahtar_istegin_her_parcasina_bagli():
    i = llm.Istek("a", model="m")
    farklar = [llm.Istek("b", model="m"), llm.Istek("a", model="m2"), llm.Istek("a", model="m", sistem="s"),
               llm.Istek("a", model="m", sicaklik=0.5), llm.Istek("a", model="m", tohum=1)]
    k = i.anahtar("gemini")
    assert all(f.anahtar("gemini") != k for f in farklar)
    assert i.anahtar("ollama") != k and llm.Istek("a", model="m").anahtar("gemini") == k


def test_gecici_hatada_bekleyip_yeniden_dener():
    s = llm.SahteSaglayici(hatalar=[llm.GeciciHata("429"), llm.GeciciHata("429", bekle_s=17.0)])
    ist, saat = _istemci(s, taban_bekleme_s=5.0)
    y = ist.sor(llm.Istek("x", model="m"))
    assert y.deneme == 3 and s.cagri == 3
    assert saat.uykular == [5.0, 17.0]            # üstel taban, sonra sağlayıcının önerisi


def test_deneme_hakki_biterse_hata():
    s = llm.SahteSaglayici(hatalar=[llm.GeciciHata("503")] * 3)
    ist, _ = _istemci(s, en_fazla_deneme=3)
    with pytest.raises(llm.LLMHatasi):
        ist.sor(llm.Istek("x", model="m"))
    assert len(ist.onbellek) == 0


def test_kalici_hata_ve_bos_yanit_onbellege_girmez():
    ist, _ = _istemci(llm.SahteSaglayici(hatalar=[llm.LLMHatasi("400")]))
    with pytest.raises(llm.LLMHatasi):
        ist.sor(llm.Istek("x", model="m"))
    ist, _ = _istemci(llm.SahteSaglayici(yanitla=lambda i: ""))
    with pytest.raises(llm.LLMHatasi):
        ist.sor(llm.Istek("x", model="m"))
    assert len(ist.onbellek) == 0


def test_istekler_arasi_en_kisa_aralik():
    ist, saat = _istemci(llm.SahteSaglayici(), en_kisa_aralik_s=6.0)
    ist.sor(llm.Istek("1", model="m"))
    ist.sor(llm.Istek("2", model="m"))
    ist.sor(llm.Istek("1", model="m"))           # önbellekten: bekleme yok
    assert saat.uykular == [6.0] and ist.ag_istegi == 2


def test_gemini_govde_ve_cozumleme():
    g = llm.GeminiSaglayici.govde(llm.Istek("soru", model="m", sistem="kural", en_fazla_token=100))
    assert g["generationConfig"] == {"temperature": 0.0, "maxOutputTokens": 100}
    assert g["systemInstruction"]["parts"][0]["text"] == "kural"
    assert g["contents"][0]["parts"][0]["text"] == "soru"
    ham = {"candidates": [{"content": {"parts": [{"text": "düşünce", "thought": True}, {"text": " Omzunu indir. "}]},
                           "finishReason": "STOP"}]}
    assert llm.GeminiSaglayici.coz(ham) == ("Omzunu indir.", "STOP")
    assert llm.GeminiSaglayici.coz({"promptFeedback": {"blockReason": "SAFETY"}}) == ("", "SAFETY")


def test_ollama_govde():
    g = llm.OllamaSaglayici.govde(llm.Istek("soru", model="m", sistem="kural"))
    assert g["stream"] is False and g["options"] == {"temperature": 0.0, "seed": 0}
    assert [m["role"] for m in g["messages"]] == ["system", "user"]


def test_anahtar_yoksa_acik_hata(tmp_path, monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setattr(llm, "env_oku", lambda ad, env_yolu=None: None)
    with pytest.raises(llm.LLMHatasi, match="GEMINI_API_KEY"):
        llm.GeminiSaglayici()


def test_env_dosyasi(tmp_path, monkeypatch):
    monkeypatch.delenv("DENEME_ANAHTAR", raising=False)
    e = tmp_path / ".env"
    e.write_text('# yorum\nDENEME_ANAHTAR="abc"\n', encoding="utf-8")
    assert llm.env_oku("DENEME_ANAHTAR", e) == "abc"
    monkeypatch.setenv("DENEME_ANAHTAR", "xyz")
    assert llm.env_oku("DENEME_ANAHTAR", e) == "xyz"


def test_orneklem_tabakali_ve_tekrarlanabilir():
    from deneyler.deney4_orneklem import orneklem_sec
    satir = []
    for gg in ("önden (0–20°)", "çapraz (30–60°)", "profil (70–90°)"):
        for h in ht.SINIFLAR:
            for i in range(60 if h == ht.DOGRU else 25):
                satir.append({"video": f"v{i % 5}", "kamera": "cam1", "yonelim": 0, "satir": len(satir),
                              "kisi": f"k{i % 5}", "gorus_grubu": gg, "hata": h})
    c = pd.DataFrame(satir)
    a = orneklem_sec(c, 50, 20, 0)
    pd.testing.assert_frame_equal(a, orneklem_sec(c.sample(frac=1, random_state=3), 50, 20, 0))
    assert len(a) == 150 and (a.gorus_grubu != "profil (70–90°)").all()
    assert a.hata.value_counts().to_dict() == {ht.DOGRU: 50, **{h: 20 for h in ht.HATALAR}}
    assert not a.satir.duplicated().any()
    assert (a.groupby(["hata", "kisi"]).size() == [10 if h == ht.DOGRU else 4
                                                  for h, _ in a.groupby(["hata", "kisi"]).size().index]).all()
    assert not orneklem_sec(c, 50, 20, 1).satir.equals(a.satir)


def test_gunluk_kotada_beklemeden_durur():
    """Sağlayıcı en uzun beklemeden fazlasını isterse (ör. günlük kota, 20 sa) beklemeden durulur."""
    s = llm.SahteSaglayici(hatalar=[llm.GeciciHata("429 per day", bekle_s=72214.0)])
    ist, saat = _istemci(s, en_uzun_bekleme_s=120.0)
    with pytest.raises(llm.LLMHatasi, match="kota"):
        ist.sor(llm.Istek("x", model="m"))
    assert s.cagri == 1 and saat.uykular == [] and len(ist.onbellek) == 0


def test_yalniz_onbellek_saglayici_aga_gitmez(tmp_path):
    """Karar 53: yeniden üretimde önbellekte olan yanıt aynen gelir, olmayan için istek atılmaz, hata verir."""
    yol = tmp_path / "onbellek.jsonl"
    i = llm.Istek("merhaba", model="m")
    s = llm.SahteSaglayici()
    s.ad = "gemini"                                 # anahtar sağlayıcı adına bağlı
    llm.LLMIstemcisi(s, llm.Onbellek(yol)).sor(i)
    boyut = yol.stat().st_size
    yo = llm.YalnizOnbellekSaglayici("gemini")
    ist = llm.LLMIstemcisi(yo, llm.Onbellek(yol))
    y = ist.sor(i)
    assert y.onbellekten and y.metin == "yanıt: merhaba" and yo.cagri == 0
    with pytest.raises(llm.LLMHatasi):
        ist.sor(llm.Istek("başka", model="m"))
    assert yo.cagri == 1 and yol.stat().st_size == boyut    # önbellek dosyasına yazılmadı
