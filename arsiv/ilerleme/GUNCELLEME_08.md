# Güncelleme 08 — 7 Kasım 2026 öğle (danışmandan)

Claude Code: `/clear` sonrası yeni oturum. Sırayla oku:
1. `CLAUDE.md`
2. `PLAN.md`
3. `ilerleme/KARARLAR.md`
4. `ilerleme/ADIM_06.md`
5. `docs/GELECEK_CALISMA.md`
6. bu dosya

Kararları (29–35) `KARARLAR.md`'ye işle. `PLAN.md`'deki durum işaretlerini güncelle (Adım 6 ✅) ve Adım 6 ile Adım 7'nin altına bu güncellemenin kısa notunu ekle.

## Önce kısa bir değerlendirme
Adım 6 iyi iş. Uygulama = Deney 3 testi, beş kişiyle kurulan kuralın LOSO aralığında kalması ve canlı denemenin kullanıcının gözlemleriyle birlikte kaydedilmesi tam istenen şeydi. Gözlemlere bakarak hiçbir eşiğin değiştirilmemesi de doğru.

## Kararlar

### Karar 29 — Bant genişliğine alt sınır eklenmez; dar bantın yapısal sebebi raporlanır
- Yöntem donduruldu (Karar 18). Canlı denemedeki dar bant bir **uygulama gözlemi**; ölçülü bir test sonucu değil. Bunun üzerine yöntem değiştirilmez, Deney 2 de yeniden çalıştırılmaz.
- **Yapısal açıklama (raporda yazılır):** M39'un τ'su, τ = t·s/√n, ortalamanın güven aralığıdır, yeni bir tekrarın düşeceği aralık değildir. n arttıkça ve kalibrasyon tekdüzeleştikçe daralır. Yeni bir tekrar için doğal aralık, tahmin aralığı t·s·√(1+1/n) olurdu; n = 6 için bu yaklaşık 2,6 kat geniştir. Q1 alt sınırı bunu kısmen dengeliyor. Kullanıcının "kendimi çok sıkıp dümdüz yaptım" gözlemi bu yapıyla birebir tutarlı.
- `GELECEK_CALISMA.md`'ye 8. madde: "Tahmin aralığı tabanlı bant ya da popülasyon τ dağılımından alt sınır; LOSO ile önceden kayıtlı sınanır."
- Arayüzde yönerge (yöntem değil): kalibrasyon başında "Doğal ve rahat tekrarlar yap; kendini zorlama. Her tekrarda aynı yere bak."
- Adım 7, doğru tekrarlardaki gereksiz uyarı oranını kendi kayıtlarımızda ölçecek. Bu oran yüksek çıkarsa olduğu gibi raporlanır.

### Karar 30 — Kamera açısı kontrolü değerlendirmede de yapılır (yalnızca arayüz)
- Karar 26'daki eşik (0,3887), her değerlendirme tekrarının dinlenme oranına da uygulanır. Yeni eşik yoktur.
- Eşiğin altındaysa karar ve cümle yine gösterilir. Altına küçük bir not eklenir: "Kameraya göre açın değişti; bu sonuç güvenilir olmayabilir. Kameraya daha önden dur."
- Oturum CSV'sine `kamera_orani` ve `kamera_uyarisi` sütunları eklenir.
- Karar ve metrikler değişmez.

### Karar 31 — Bilgi notları: hız ve sol kol (hata türü değil)
Bunlar karar kuralına girmez, hata türü sayılmaz ve hiçbir metriğe katılmaz. Panelde hasta cümlesinin altında ayrı bir **bilgi notu** olarak gösterilir ve CSV'ye ayrı sütunlarda yazılır.
- **Hız:** Tekrar süresi, veri setinin önden + çapraz **doğru** tekrarlarındaki sürelerin 5. yüzdeliğinden kısaysa: "Hareketi biraz daha yavaş yap." Süre `first_frame`…`last_frame` aralığından hesaplanır, uygulamada da ayırıcının sınırlarından. Eşik bir betikle üretilip `modeller/` altına yazılır ve ADIM_07'de belirtilir. Veri setinde hız etiketi olmadığı için doğruluğu ölçülemez; raporda böyle yazılır.
- **Sol kol:** Tekrar sırasında sol kolun açısı (sağ kolla aynı tanımla) 60°'yi geçerse: "Yalnızca sağ kolunu kaldır." 60°, tekrar ayırıcının tepe şartıyla aynı sayıdır; yeni bir sabit değildir.
- **Genel "hareket tanınmadı" mesajı eklenmez.** Tanımı yeni bir eşik gerektirir ve sınanamaz. Sistemin yalnızca 5 hata türünü bildiği ve tanımsız bir hareketi en yakın türe atadığı sınırlılık olarak yazılır.

### Karar 32 — Bakış yönü Adım 7'de ölçülür
- Kullanıcının gözlemi (kalibrasyonda karşıya, değerlendirmede ekrana bakınca baş hatası) Adım 7 çekiminde **bilerek** sınanır (Karar 33).
- Arayüz yönergesi Karar 29'daki gibidir.
- Ölçüt değişmez.

### Karar 33 — Adım 7 çekim protokolü (önceden sabit)
**Kamera:** Telefon tripodda (ya da sabit bir yüzeyde), göğüs hizasında, 2–2,5 m uzakta. Kişi kameraya önden durur (en fazla 30° çapraz). Baştan kalçaya bütün gövde ve yukarı kalkan sağ kol kadrajda olmalı. Arka plan sade, ışık önden.
**Bakış:** Kişi bütün çekim boyunca kameranın yanındaki **sabit bir noktaya** bakar; bakış tekrarları dışında.

**`kalibrasyon.mp4`:** 6 doğru tekrar, doğal ve rahat.

**`test.mp4`:** Toplam 21 tekrar, sıra karışık. Sırayı çekimden **önce** bir kâğıda yazın ve buna uyun.
| etiket | adet |
| --- | --- |
| doğru | 5 |
| omuz | 3 |
| baş | 2 |
| dirsek | 2 |
| az kaldırma | 2 |
| öne kaçma | 2 |
| doğru, farklı yere bakarak (ör. yere ya da yana) | 3 |
| doğru, hızlı (yaklaşık 1 saniyede) | 2 |

- `etiketler.csv`: `tekrar_no, etiket, not`. "Bakış" ve "hızlı" tekrarlarının etiketi `dogru`, notu `bakis` ya da `hizli`.
- Mümkünse ikinci bir kişiyle (arkadaş ya da aile) aynı çekim tekrarlanır.

**Metrikler (çekimden önce sabit):**
- katı, ilk iki, hatalılarda olumlu cümle;
- **doğru tekrarlarda gereksiz uyarı**, üç grupta ayrı ayrı: normal doğru, bakış, hızlı;
- hız notunun hızlı tekrarlarda çıkıp çıkmadığı ve normal doğru tekrarlarda çıkıp çıkmadığı;
- karışıklık tablosu ve "verilen cümle – gerçek etiket" tablosu (`sonuclar/kendi_kayit/`).
- Sayılar küçük olacak (kişi başına 21 tekrar). GA verilmez; sayılar "kaçta kaç" olarak yazılır.

**Değerlendirme:** Dondurulmuş yöntem ve `modeller/kural_ex1.json`, yığın modu, MediaPipe 1.2.2. Hiçbir eşik bu kayıtlara göre değiştirilmez.

**Sunum yedeği:** Bu iki video ve yığın modu çıktısı Karar 27'deki sunum yedeğidir.

### Karar 34 — Açık soruların cevapları
- **Tekrar ayırma:** Önden + çapraz 95,0 ile kabul. Tüm görüşler 87,4 ve profil 53,1 sınırlılık olarak yazılır.
- **MediaPipe 1.2.2:** Sınırlılık notu yeterli. Ölçülen fark (kol açısı medyanı 0,9°, %95'lik dilimi 3,1°) raporda yazılır. Ortamı bozmamak için 0,10.20'ye geçilmemesi doğru karardı.
- **8 saniyelik otomatik kabul:** Uygun. Ret ve "son kabulü geri al" hakları duruyor, kalite kontrolü de var. Küçük arayüz sapması olarak ADIM_06'da kalır.
- **Kalite kontrolünün sağlık kontrolünde kapalı olması:** Doğru.

### Karar 35 — Sıra (takvim)
- Önce bu dosyadaki küçük arayüz işleri (Karar 29–31; kısa).
- Ardından Adım 7'nin **hazırlığı**: `etiketler.csv` şablonu, değerlendirme betiği (`python -m deneyler.kendi_kayit --kalibrasyon ... --test ... --etiketler ...`) ve ADIM_07'nin "Önceden belirlenenler" bölümü (Karar 33'ün metrikleri). Bu bölüm çekimden önce commit'lenir.
- **Adım 8 (LLM) çekimle paralel başlayabilir.** Kullanıcı videoları çekerken Claude Code Adım 8'in kodunu hazırlayabilir, çünkü Adım 8 yalnızca Deney 3 çıktılarını kullanır. Koşul: Adım 7'nin çekimi **en geç 9 Kasım akşamı** yapılır. Yapılmazsa Adım 8 durdurulur ve önce Adım 7 bitirilir.
- Adım 8 için kullanıcı Google AI Studio'dan ücretsiz bir API anahtarı alır (`GEMINI_API_KEY`). Adım 8'in ayrıntıları ayrı bir güncellemede verilecek. Claude Code bu arada yalnızca sağlayıcıdan bağımsız arayüzü (`cekirdek/llm.py`), önbelleği ve örneklem seçimini hazırlar; istem metinlerini ve koşulları yazmaz.
- 6b (siluet) ve 10 (REHAB24-6), Adım 7 ve 8 bittikten sonra, vakit kalırsa yapılır.

## Yapılacaklar
1. Karar 29 (yönerge), 30 ve 31'i uygula; testler ve hız eşiği betiği dahil. `pytest` geçmeli. Sağlık kontrolü sonuçları (ADIM_06 tablo 4) değişmemeli.
2. `GELECEK_CALISMA.md` madde 8 (Karar 29).
3. Adım 7 hazırlığı (Karar 33, 35): şablon, betik, ADIM_07 "Önceden belirlenenler", commit. Kullanıcıya çekim talimatını kısa ve madde madde ver; bir kâğıda yazdırılabilecek bir kontrol listesi (`docs/CEKIM_LISTESI.md`) de hazırla.
4. `cekirdek/llm.py` iskeleti, önbellek ve tabakalı örneklem (PLAN Adım 8). İstem metni ve deney yok; ayrıntılar sonraki güncellemede.
5. ADIM_06'nın sonuna kısa bir "Ek: Güncelleme 08" yaz: yapılan arayüz değişiklikleri ve hız eşiği değeri.
