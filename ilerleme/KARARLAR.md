# Kararlar günlüğü

Birden fazla adımı etkileyen kararlar, tek satırda. Format: `YYYY-AA-GG | karar | gerekçe | kim`

2026-11-05 | Ana veri seti REHAB26-ViewAngles | Her hatalı tekrarın hata türü etiketli; kamera açısı değişkeni var | danışman + kullanıcı
2026-11-05 | Odak egzersiz Ex1 (kol abdüksiyonu, sağ kol), odak hata omuz silkmesi | Hocanın "omuzu algılamıyor" problemi; veri setinde etiketli | danışman + kullanıcı
2026-11-05 | 2B koordinat, 3B değil | M34 ve M39'da 2B daha iyi; küçültülmüş veride yalnızca 2B var | danışman
2026-11-05 | En-boy düzeltmesi x *= 9/16 (REHAB26 için) | Kol kemiği uzunluğu tutarlılığından tahmin 0,62; dikey telefon videosu | danışman
2026-11-05 | Bant yöntemi M39'dan alındı, katkı olarak sunulmaz | M39 bunu zaten yapmış | danışman
2026-11-05 | DTW hizalaması kol açısına göre, omuz ölçütüne göre değil | Silkme hizalamayı bozmasın, hizalamanın içinde kaybolmasın | danışman
2026-11-05 | Uzunluk ölçütleri gövde uzunluğuna bölünür, omuz genişliğine değil | Profil görünümde omuz genişliği sıfıra iner | danışman
2026-11-05 | Geri bildirimde ana yöntem kural tabanlı; LLM yalnızca karşılaştırma | M21: LLM eşik uyduruyor ve aşırı özgüvenli | danışman + kullanıcı
2026-11-05 | LLM: yalnızca Gemini ücretsiz katmanı veya Ollama | Ücretli API yok | kullanıcı
2026-11-06 | REHAB26 2B x, y normalize (0–1), piksel değil; videolar 1080x1920 → en-boy x *= 9/16 doğrulandı | Değer aralığı + videoya iskelet bindirme (Adım 0) | Claude Code
2026-11-06 | Ana veri kaynağı orijinal zip; tekrarlar (kare, 33, 4) float64, npz kaynağında eksik eklemler NaN | Ölçüt kodu iki kaynakta aynı MediaPipe indeksleriyle çalışsın | Claude Code
2026-11-06 | Video ve iskelet kare 0'dan hizalı kabul edildi (bazı videolarda video daha uzun) | Tek kontrolde fazla kareler sonda; Adım 2b'de doğrulanacak | Claude Code
2026-11-06 | Çekirdek (cekirdek/) referans Deney 1'i bit düzeyinde aynı üretiyor (npz); DTW numba ile hızlandırıldı | Davranış koruma; deney 46 s → ~13 s | Claude Code
2026-11-06 | Bant hatası yönsüz (varsayılan, M39) ve yönlü (yon=±1) seçenekli | Adım 4'te hata yönü gerekecek | Claude Code
2026-11-06 | KAPANDI (Güncelleme 02, Karar 1): Tek tekrarın E'si referans tekrar seçimine (tohum) çok duyarlı; çoklu referans önerildi | Adım 4–6'da tek tekrar kararı verilecek | Claude Code → danışman
2026-11-06 | Video ve iskelet kare kare hizalı (±4 kare içinde); fazla video kareleri sonda | Hareket korelasyonu ile 15 Ex1 videosunda ölçüldü (sonuclar/adim2b/senkron.csv) | Claude Code
2026-11-06 | Bindirme: öteleme kalça ortasıyla (kare kare), ölçek ve döndürme dinlenme karelerinden bir kez | Kare kare gövde ölçeği/merkezi omzu içerdiği için silkmeyi gizler; Adım 6 da aynı kodu kullanır | Claude Code
2026-11-06 | Görselleştirmede geçici karar: E > diğer 4 kişinin doğru E'lerinin %90'ı | Adım 4'e kadar karar kuralı yok; test kişisi eşiğe girmez; değerlendirme sonucu değildir | Claude Code
2026-11-06 | KAPANDI (Güncelleme 02, Karar 2): Silkmeli tekrarların %18,2'sinde kol referanstan ≥30° az kalkıyor; z-normalize DTW şekil eşlediği için omuz farklı kol açılarında karşılaştırılıyor | Yönlü bant (Adım 4) ve/veya gerçek açıya göre hizalama önerildi; karar danışmanda | Claude Code → danışman
2026-11-06 | KAPANDI (Güncelleme 02, Karar 3): Tekrar sonrasındaki 10 pay karesi E'ye katılıyor ve yanlış alarm üretiyor; keşifte pay hariç E ile AUC 0.909 → 0.932 | E yalnızca etiketli tekrar karelerinde mi hesaplansın? Referans koddan sapma; karar danışmanda | Claude Code → danışman
2026-11-06 | KAPANDI (Güncelleme 02, Karar 5): Kişi bazlı AUC 0.800 (Vasil) – 0.985 (Honza); raporda ortalamanın yanında kişi aralığı verilmeli | Kullanıcının galeri gözlemi | Claude Code
2026-11-06 | Zaman bandında tek rastgele referans yerine çoklu referans: modeldeki her doğru tekrar sırayla referans, E'lerin ortalaması | Tek tekrar kararı tohuma bağlı olmasın | danışman (Güncelleme 02)
2026-11-06 | Yeni bant türü "açı bandı" (cekirdek/aci_bandi.py): kol açısına koşullu, 5° kutu, kaldırma/indirme fazı ayrı, kutu başına tekrar ortalaması, ≥3 tekrar, boşluklar doğrusal ara değer, kalibrasyon aralığı dışı değerlendirilmez | "Kol θ°'deyken bu kişinin omzu normalde nerede?"; özgün katkı; parametreler önceden sabit, test verisine bakarak değiştirilmez | danışman (Güncelleme 02)
2026-11-06 | Açı bandı yalnızca duruş ölçütleri için (omuz, baş, dirsek, öne kaçma); yetersiz kaldırma tepe açısı ile ayrı ele alınır | Kol açısı kendine koşullanamaz | danışman (Güncelleme 02)
2026-11-06 | Bant hatası, DTW ve bant yalnızca etiketli tekrar karelerinde (first_frame…last_frame); dinlenme tabanı yine ilk 8 kare (pay dahil) | Pay kareleri tekrarın parçası değil; uygulamada da tekrar ayırıcı sınırı belirler | danışman (Güncelleme 02)
2026-11-06 | Bindirmede ölçek ve döndürme tekrar başından bir kez: onaylandı; kameraya yaklaşma/uzaklaşma küçük ölçek hatası (sınırlılık) | Kare kare gövde ölçeği silkmeyi gizler | danışman (Güncelleme 02)
2026-11-06 | Her ana sonuç tablosunun yanında kişi bazlı AUC (5 satır) ve "ortalama (en düşük–en yüksek)"; şekillerde kişi değerleri nokta; Vasil'in etiketleri yorumlanmaz | Sadece 5 kişi, kişiler arası fark büyük | danışman (Güncelleme 02)
2026-11-06 | Deney 1 v1 (M39'a sadık) temel çizgi olarak korunur, silinmez; düzeltmeler Deney 1 v2'de ablasyonla (v1, v1a, v1b, v2) | Her kararın etkisi ayrı görülsün; kazanç aynı veride bulunduğu için iyimser olabilir → Ex7 (Adım 4b) ve kendi kayıtlar (Adım 7) ile ayarsız doğrulama | danışman (Güncelleme 02)
2026-11-06 | Adım 4 ve sonrasında duruş ölçütleri için yalnızca açı bandı; görüşe göre yöntem değiştiren karma çözüm yok; v1b (zaman bandı, çoklu referans) karşılaştırma temel çizgisi, karar kuralına girmez | Görüşe göre seçim test sonuçlarına bakılarak yapılmış olurdu | danışman (Güncelleme 03, Karar 6)
2026-11-06 | Her ana sonuç iki biçimde: "uygulama senaryosu: önden + çapraz (|görüş| ≤ 60°)" ve "tüm görüşler"; profil (70–90°) gerekçesiyle sınırlılık olarak ayrıca | Profilde yana kaldırma kameraya doğru/uzağa bir hareket, 2B kol açısı bozulur; karar Adım 4 sonuçlarından önce verildi | danışman (Güncelleme 03, Karar 6)
2026-11-06 | Adil model: hatalı tekrarda rastgele "atla" yerine her doğru tekrar sırayla dışarıda, n model, E'lerin ortalaması (v1b, v2 ve sonrası; v1/v1a Deney 1'e sadık) | E tamamen deterministik olsun; kod cekirdek/adil_model.py | danışman (Güncelleme 03, Karar 7)
2026-11-06 | Karar 7 ayrıntısı: açı bandında NaN E'li modeller ortalamaya girmez; kapsam = modellerin ortalaması; aralik_disi = modellerin yarısından fazlasında bayrak; görsellerde çizilen bant 1. (n−1)'li modelden, gösterilen E ortalama | Uygulama ayrıntısı, sonuçlara bakılmadan verildi | Claude Code
2026-11-06 | Uygulamada kalibrasyon varsayılan 6 doğru tekrar, en az 5; arayüz bunu söyler | 4 tekrarlık modelde açı bandının "en az 3 tekrar" kuralı sınırda kalıyor | danışman (Güncelleme 03, Karar 8)
2026-11-06 | Uygulamada kamera açısı kontrolü: dinlenmedeki omuz genişliği / gövde uzunluğu oranı, veri setinin önden doğru tekrarlarındaki tipik değerin belirgin altındaysa "Kameraya daha önden durun." | Yöntemin ön koşulu: kol açısı kameradan ölçülebilir olmalı; eşik ADIM_06'da | danışman (Güncelleme 03, Karar 9)
2026-11-06 | Deney 1b'de iki deterministik genel bant: diğer 4 kişinin tüm doğru tekrarları (~20) ve "başka tek kişinin kalibrasyonu" (~5, 4 kişi sırayla, E ortalaması); rastgele 4 tekrar seçilmedi | Karar 7 ile tutarlı, rastgelelik yok; sonuç: genel bant kişiye özelden 0,19–0,33 AUC geride (36/36 GA sıfırı içermiyor) | Claude Code
2026-11-06 | Ortak sonuç tabloları deneyler/tablolar.py'de (AUC özeti tüm görüşler + önden/çapraz, kişi AUC, kişi bazlı bootstrap farkları) | Adım 4 ve sonrası aynı raporlama biçimini kullansın (Karar 5, 6) | Claude Code
2026-11-06 | AÇIK: Zamansal yumuşatma (One Euro, Savitzky–Golay) ana yöntemde kullanılmasın önerisi | Deney 1c: titreme %38–87 azaldı, AUC farkları ±0,006 içinde; One Euro gecikme ekliyor; karar danışmanda | Claude Code → danışman
