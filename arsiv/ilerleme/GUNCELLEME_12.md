# Güncelleme 12 — 9 Kasım 2026 (danışmandan): dondurma

Claude Code: `/clear` sonrası yeni oturum. Sırayla oku:
1. `CLAUDE.md`
2. `PLAN.md`
3. `ilerleme/KARARLAR.md`
4. `ilerleme/ADIM_07.md`
5. `ilerleme/ADIM_06b.md`
6. `ilerleme/ADIM_09.md`
7. `docs/GELECEK_CALISMA.md`
8. bu dosya

Kararları (51–56) `KARARLAR.md`'ye işle. `PLAN.md`'deki durum işaretlerini güncelle (Adım 7 ✅, 6b ✅ olumsuz sonuç, 10 ⛔, Adım 9 🔄).

**Tarih değişikliği:** Dondurma 13 Kasım'ı beklemeden, iş bitince yapılır. Hedef 11 Kasım. Böylece sunuma daha çok zaman kalır.

## Değerlendirme
- **Adım 7 temiz yapıldı.** Önceden kayıt korundu. Kullanıcının videoda gördüğü ek hatalar (18 ve 21'de dirsek, 13'te baş) etiketleri değiştirmeden yalnızca gözlem olarak yazıldı. Doğrusu buydu.
- Suflörsüz ilk kalibrasyon videosunun kullanılmaması doğru: karar değerlendirmeden önce verildi, gerekçesi bakış yönünün iki videoda aynı olmasıydı.
- **Küçük düzeltme:** ADIM_07 "Önceden belirlenenler" madde 5'te "Hatalı tekrarlar (12)" yazıyor. Protokole göre hatalı tekrar 11'dir (3 omuz + 2 baş + 2 dirsek + 2 az kaldırma + 2 öne kaçma). Bu bir yazım hatası; o bölümün altına "düzeltme: 11" notu düşülür, bölümün kendisi değiştirilmez.

## Kararlar

### Karar 51 — Adım 7'nin yorumu ve iddia kapsamı
| İddia | Kanıt (kişi 1, 21 tekrar) | Güç |
| --- | --- | --- |
| Sistem, hiç görmediği bir kişide, ev koşullarında çalışıyor | 21/21 tekrar ayrıldı; hatalılarda katı 9/11, ilk iki 11/11, olumlu cümle 0/11; omuz silkmesi 3/3; normal doğru tekrarlarda gereksiz uyarı 0/5 | **İşaret.** Tek kişi, tek oturum ve kişi aynı zamanda geliştirici. Veri seti sonuçlarıyla yalnızca yan yana konur. |
| Dirsek ile öne kaçma tek kamerada karışıyor | Kaçırmaların ikisi de bu çift (1, 21); 18 ve 21'de kişi gerçekten iki hatayı birden yapmış | Veri setindeki bulguyla (ADIM_06 bulgu 1) tutarlı |
| Başka yere bakmak gereksiz uyarı üretebilir | Bakış 3/3 uyarı, normal 0/5; ama 13'te baş gerçekten eğilmiş, 2 ve 3'te sapmalar küçük | **Zayıf işaret.** Kalibrasyonla değerlendirmede aynı yere bakmak bir kullanım talimatı olarak yazılır. |
| Hızlı yapılan doğru tekrar gereksiz uyarı üretebilir | Hızlı 2/2 küçük omuz uyarısı; hız notu 2/2 doğru çıktı | **İşaret**; sebebi doğrulanmadı |
| Başı sağa eğmek omuz ölçütünü de tetikler | 19 (sağa): omuz ikinci hata olarak söylendi; 11 (sola): söylenmedi | Bulgu 2 ile tutarlı; tek örnek |
- Sunumda tek cümle: **"Kendi videomda 11 hatalı tekrarın 11'inde doğru hata cümlede geçti, 9'unda ilk söylenen oydu; 5 normal doğru tekrarın hiçbirinde uyarı çıkmadı."**
- Sınırlılık olarak yazılır: tek kişi; değerlendiren aynı zamanda geliştirici; hataları bilerek taklit etti.

### Karar 52 — 6b'nin kapanışı
- Sonuç kabul: `SILUET` bu tanımla YENI'den kötü (silkme/doğru 0,72'ye karşı 0,97; GA sıfırı içermiyor); önden 0,94, çapraz 0,55. Raporda ADIM_06b'deki önerilen cümle kullanılır.
- `GELECEK_CALISMA.md`'ye 12. madde: "Görüş açısına dayanıklı siluet ROI'si (aramayı başa değmeyen bir noktadan başlatmak) ve SILUET + YENI birleşimi (kişi bazlı birini-dışarıda-bırak ile ayar)."
- "Başa takılma" tanısı (ADIM_06b bölüm 5) sonradan yapılmış betimsel bir analizdir; raporda öyle anılır.
- Yan bulgu raporda kullanılır: `YENI_mp122` 0,969, kayıtlı YENI 0,968. MediaPipe sürüm farkı bu ölçütü pratikte etkilemiyor (Karar 27'nin sınırlılık notunu hafifletir).

### Karar 53 — Yeniden üretimin kapsamı (`deneyler/hepsi.py`)
Mevcut sıraya şu adımlar **önbellekten** eklenir. Ağ, video ya da segmentasyon gerektiren kısımlar yeniden çalıştırılmaz, yalnızca kayıtlı ara çıktılardan tablolar yeniden üretilir:
- 6b değerlendirmesi: `veri/ara/siluet/` önbelleğinden (`python -m deneyler.siluet`, görselsiz). Segmentasyonun kendisi yeniden çalıştırılmaz ve listede "önbellekten" diye işaretlenir.
- Deney 4: `onbellek.jsonl`'den `raporla` ve `kaldirma-degerlendir`. LLM'e istek gitmez; önbellekte eksik yanıt varsa adım "üretilmedi" olarak işaretlenir, istek atılmaz.
- Adım 7: `veri/ara/kendi_kayit/` MediaPipe önbelleğinden `deneyler.kendi_kayit`.
- Önbelleği olmayan biri için `YENIDEN_KURULUM.md` bu adımların nasıl baştan üretileceğini ayrıca anlatır (segmentasyon ~1,5 saat, LLM için anahtar, kendi videosu).

### Karar 54 — Dondurma belgeleri
Hepsi kaynak dosyadan kopyalanmış sayılarla. **`OZET.md`'deki her sayının yanında kaynak CSV adı** yazılır.

1. **`sonuclar/OZET.md`:**
   - En başta beş cümlelik "ne yaptık, ne bulduk".
   - Her deney için tek bir tablo: Deney 1 v2, 1b, 1c, 2, Ex7, 3, 6b, 4 (birincil + duyarlılık), Adım 7, tekrar ayırma.
   - En önemli 3 şekil: `1_problem`, `2_fikir_aci_bandi`, `5_bindirme`.
   - Birleşik **iddia kapsamı tablosu**: Karar 20, 23, 41, 47 ve 51'in hepsi tek tabloda, güç sütunuyla.
   - **Sınırlılıklar** listesi: 5 sağlıklı kişi ve taklit hatalar; profil görüş; dar bant (τ'nun ortalamanın güven aralığı olması); öne kaçma–dirsek ve baş–omuz karışmaları; tek kare ölçü ve sağlam ölçü; 2B açı; MediaPipe sürümü; tek etiketleyici; Adım 7'nin tek kişi olması; bakış ve hız duyarlılığı; LLM'de tek model ve tek istem.
   - Gelecek çalışma: `GELECEK_CALISMA.md`'ye bağlantı ve maddelerin bir satırlık listesi.
   - **Başarısız ve olumsuz denemeler** ayrı bir bölümde: revize kaldırma puanı (Karar 13), yumuşatma (1c), siluet (6b), LLM sayı uydurma beklentisi.
2. **`docs/YENIDEN_KURULUM.md`:** TASLAK başlığı kalkar. Hocanın 7 başlığı: ortam, girdi hazırlığı, pose çıkarımı, ölçüm/hizalama, hata hesabı, geri bildirim, çıktı. Veri setini indirme, `.venv`, `pip install -r requirements.txt`, `pytest`, deneyleri ve demoyu çalıştırma komutları. Kendi videosuyla kullanım (Adım 7 protokolü ve suflör sayfası; suflör HTML'i `docs/cekim_suflor.html` olarak eklenebilir, kullanıcı dosyayı verirse).
3. **`docs/LLM_KULLANIMI.md`:** Son hali. Hocanın kuralına uygun kısa bir rapor notu da içerir ("Üretken yapay zekâ şu amaçlarla kullanıldı: …"; 3–4 satır, rapora doğrudan konabilecek biçimde).
4. **`docs/SURUMLER.md`:** Son `pip freeze`, Python sürümü, MediaPipe notu (Karar 27 ve 52'deki fark), Gemini model adı ve tarihi.
5. **`docs/ARKA_PLAN.md`:** "Deney 1 sonuçları" bölümünün başına "Bu tablo ilk sürüme (v1) aittir; güncel sonuçlar `sonuclar/OZET.md`'de" notu ve güncel ana satır (v2, YENI: tüm görüşler ve önden + çapraz, silkme/doğru ve silkme/diğer) eklenir. Eski tablo silinmez.
6. **`README.md`:** Kısa bir "sonuçlar" paragrafı ve `OZET.md` bağlantısı.
7. **ADIM_09:** Yapılanlar ve sonuçlar.

### Karar 55 — Dondurma sırası ve kuralı
1. Claude Code: Karar 52–54'ü uygular, `pytest` geçer, her şeyi commit'ler.
2. **Kullanıcı:** `python -m deneyler.hepsi` komutunu çalıştırır (~1–1,5 saat).
3. Bütün dosyalar "aynı" çıkarsa: `OZET.md`'ye commit kimliği ve "yeniden üretim: N/N aynı" satırı eklenir; `v-sunum` etiketi atılır; GitHub'a gönderilir (push, etiket dahil).
4. Fark çıkarsa: **durulur**, ADIM_09'a yazılır ve danışmana sorulur. Sonuç dosyaları elle düzeltilmez.
5. **Etiketten sonra:** Yöntem, deney ve sonuç kodunda değişiklik yapılmaz. Yalnızca sunum materyali hazırlanır. Uygulamada demoyu engelleyen bir hata çıkarsa düzeltilir, ADIM_09'a "dondurma sonrası düzeltme" olarak yazılır ve yeni bir etiket atılır (`v-sunum-2`). Düzeltmeden sonra uygulama = Deney 3 testi yine geçmeli.

### Karar 56 — Sunum için hazırlık girdileri (sunumun kendisi değil)
Sunum danışmanla hazırlanacak. Claude Code yalnızca şunları hazırlar:
1. **`docs/SUNUM_GIRDILERI.md`:** Sunumda kullanılabilecek sayıların listesi, her biri bir cümle ve kaynak dosyasıyla, hocanın problemlerine göre gruplanmış (P1, P2, P3). Ayrıca Karar 41, 47 ve 51'deki "tek cümleler".
2. **Kendi videomdan demo yedeği:** `sonuclar/sunum/demo_kisi1.mp4`. Kişi 1'in kalibrasyonu ile test videosunun şu tekrarları ve oynatımları: 4 (doğru), 7 (omuz), 11 (baş sola), 6 (az kaldırma). Yaklaşık 45–60 saniye. `sunum_sekilleri`'ndeki gibi uygulamanın kendi çizim koduyla, pencere açmadan üretilir. Git'e girmez (kişisel görüntü).
3. **Demo talimatı:** Sunumda canlı olarak çalıştırılacak komutlar ve sırası:
   - kişi 1 profiliyle `test.MOV` video modu;
   - yedek olarak `demo_kisi1.mp4`;
   - ikinci yedek olarak veri seti demosu.
   Her biri için "ne olursa ne yapılır" notu. `docs/DEMO.md`.
4. `4_geri_bildirim.png` ve `5_bindirme.png`'nin kişi 1'den (tekrar 7, omuz) birer sürümü (`4b_`, `5b_`). Veri seti sürümleri de kalır.

## Yapılacaklar
1. ADIM_07'deki "12" için düzeltme notu.
2. Karar 52 (GELECEK_CALISMA madde 12), Karar 53 (`hepsi.py` eklemeleri ve testleri; `--hizli` ile dene), Karar 54 (belgeler), Karar 56 (sunum girdileri).
3. `pytest` geçmeli. Her şeyi commit'le.
4. Kullanıcıya `python -m deneyler.hepsi` komutunu, süresini ve çıktının nasıl okunacağını kısa ve net ver. Sonuç gelince Karar 55'e göre devam et.
5. Bitince kısa bir özet ver. Bana gönderilecekler: ADIM_09 (son hali), `sonuclar/OZET.md`, `docs/SUNUM_GIRDILERI.md`, `docs/DEMO.md`.
