# ADIM 08 — Deney 4: LLM ile kural tabanlı karşılaştırması

**Tarih:** 2026-11-07 (hazırlık)
**Durum:** Kısmen: yalnızca altyapı hazır (Güncelleme 08, Karar 35). İstem metinleri, koşullar ve deney **yazılmadı**; ayrıntılar danışmanın sonraki güncellemesinde gelecek. Koşul: Adım 7 çekimi en geç 9 Kasım akşamı yapılmalı; yapılmazsa bu adım durur.

## Basit anlatım
- Deney 4'te aynı bilgiyi bir yapay zekâ dil modeline (LLM) verip, onun yazdığı cümlenin bizim kurallarla ürettiğimiz cümleden iyi mi kötü mü olduğunu ölçeceğiz.
- Şimdilik yalnızca **altyapıyı** hazırladık. Hangi yazılı talimatın (istemin) kullanılacağı danışmanın kararı.
- Altyapının üç parçası var:
  - **Ortak arayüz:** Kod hangi modelle konuştuğunu bilmek zorunda değil. Model Gemini (Google'ın ücretsiz katmanı) ya da kendi bilgisayarımızda çalışan Ollama olabilir.
  - **Önbellek:** Her cevap bir dosyaya yazılıyor. Deneyi tekrar çalıştırınca aynı soru için internete tekrar gidilmiyor. Bu, ücretsiz kotayı korur ve sonuçları tekrarlanabilir yapar.
  - **Örneklem:** Ücretsiz kotalar yüzünden bütün tekrarlar yerine seçilmiş 150 tekrar kullanılacak. Seçim her kişiden ve her hata türünden eşit sayıda tekrar alacak şekilde yapıldı.

*Jargon:* **LLM:** büyük dil modeli. **İstem (prompt):** modele verilen yazılı talimat. **Tabakalı örneklem:** gruplara (tabakalara) ayırıp her gruptan belirli sayıda seçmek. **Sıcaklık (temperature) = 0:** modelin her seferinde aynı cevabı vermeye en yakın ayarı.

## Yapılanlar
- `cekirdek/llm.py`:
  - `Istek` / `Yanit`; sıcaklık varsayılanı 0.
  - `GeminiSaglayici` (REST `generateContent`; anahtar `GEMINI_API_KEY` ortam değişkeninden ya da git'e girmeyen `.env` dosyasından), `OllamaSaglayici` (yerel, `localhost:11434`), `SahteSaglayici` (testler, ağ yok).
  - `Onbellek`: `sonuclar/deney4/onbellek.jsonl`, `.gitignore`'da. Anahtar, isteğin bütün parçalarının SHA-256'sı.
  - `LLMIstemcisi`:
    - önbellek;
    - istekler arası en kısa bekleme (dakikalık sınır için);
    - 429/5xx/bağlantı hatasında yeniden deneme: sağlayıcının önerdiği süre (`Retry-After` ya da Gemini `retryDelay`), yoksa üstel bekleme;
    - boş yanıt ve kalıcı hata önbelleğe yazılmaz.
  - Model adı kodda sabit değil; güncel ücretsiz model ve sınırlar Adım 8'de resmi sayfadan kontrol edilecek.
  - Yeni paket yok (standart kütüphane `urllib`); `requirements.txt` notu güncellendi.
- `deneyler/deney4_orneklem.py`: Deney 3 tablosundan (`sonuclar/deney3/cumleler.csv`) yalnızca önden + çapraz tekrarlar alınır. 50 doğru + her hata türünden 20 = 150 tekrar seçilir, tohum 0. Tabaka = **sınıf × kişi**: her kişiden 10 doğru ve hata türü başına 4 tekrar. Çıktı: `sonuclar/deney4/orneklem.csv`, `orneklem_ozet.csv`.
- `testler/test_llm.py` (ağ kullanmaz):
  - önbellek: ikinci istekte ve dosyadan yeni istemcide ağa gidilmiyor;
  - anahtarın isteğin her parçasına bağlı olması;
  - yeniden deneme ve bekleme süreleri, deneme hakkının bitmesi;
  - kalıcı hatanın ve boş yanıtın önbelleğe girmemesi;
  - en kısa aralık;
  - Gemini ve Ollama istek gövdeleri ve Gemini yanıt çözümlemesi ("düşünce" parçaları atılır);
  - eksik anahtar uyarısı, `.env` okuma;
  - örneklemin tabakalı ve tekrarlanabilir olması.

## Sonuçlar
Örneklem (`python -m deneyler.deney4_orneklem` çıktısından):

| tabaka | Honza | Mima | Petra | Terka | Vasil | toplam |
| --- | --- | --- | --- | --- | --- | --- |
| az kaldırma | 4 | 4 | 4 | 4 | 4 | 20 |
| baş | 4 | 4 | 4 | 4 | 4 | 20 |
| dirsek | 4 | 4 | 4 | 4 | 4 | 20 |
| doğru | 10 | 10 | 10 | 10 | 10 | 50 |
| omuz | 4 | 4 | 4 | 4 | 4 | 20 |
| öne kaçma | 4 | 4 | 4 | 4 | 4 | 20 |
| toplam | 30 | 30 | 30 | 30 | 30 | 150 |

## Kararlar ve sapmalar
- **Tabaka = sınıf × kişi** (PLAN yalnızca "tabakalı" diyor). İlk denemede yalnızca sınıfa göre tabakalandırdım; öne kaçmanın 20 tekrarından 10'u Vasil'den, 1'i Petra'dan geldi. Kişi dengesi için tabakaya kişiyi de ekledim. Bu seçim yalnızca örneklemin bileşimine bakılarak yapıldı; hiçbir LLM sonucu yoktu. Danışman farklı bir tabaka isterse tek satırla değişir.
- Örneklem birimi Deney 3'teki gibi (satır, kamera) tekrarıdır. Aynı hareketin iki kamerası ayrı tekrar sayılır. Danışmana soru: aynı hareketin iki görüşü birlikte seçilebilsin mi?

## Açık sorular / danışmana notlar
- İstem metinleri, B ve C koşullarının girdi biçimi (JSON alanları) ve kullanılacak Gemini modeli sonraki güncellemede.
- Ollama için yerel model seçimi ve Türkçe kalitesi henüz denenmedi.
- Kullanıcı Google AI Studio'dan ücretsiz bir `GEMINI_API_KEY` alacak (Karar 35).
