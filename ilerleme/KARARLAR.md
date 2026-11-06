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
2026-11-06 | AÇIK: Tek tekrarın E'si referans tekrar seçimine (tohum) çok duyarlı; çoklu referans önerildi, karar bekleniyor | Adım 4–6'da tek tekrar kararı verilecek | Claude Code → danışman
2026-11-06 | Video ve iskelet kare kare hizalı (±4 kare içinde); fazla video kareleri sonda | Hareket korelasyonu ile 15 Ex1 videosunda ölçüldü (sonuclar/adim2b/senkron.csv) | Claude Code
2026-11-06 | Bindirme: öteleme kalça ortasıyla (kare kare), ölçek ve döndürme dinlenme karelerinden bir kez | Kare kare gövde ölçeği/merkezi omzu içerdiği için silkmeyi gizler; Adım 6 da aynı kodu kullanır | Claude Code
2026-11-06 | Görselleştirmede geçici karar: E > diğer 4 kişinin doğru E'lerinin %90'ı | Adım 4'e kadar karar kuralı yok; test kişisi eşiğe girmez; değerlendirme sonucu değildir | Claude Code
2026-11-06 | AÇIK: Silkmeli tekrarların %18,2'sinde kol referanstan ≥30° az kalkıyor; z-normalize DTW şekil eşlediği için omuz farklı kol açılarında karşılaştırılıyor | Yönlü bant (Adım 4) ve/veya gerçek açıya göre hizalama önerildi; karar danışmanda | Claude Code → danışman
2026-11-06 | AÇIK: Tekrar sonrasındaki 10 pay karesi E'ye katılıyor ve yanlış alarm üretiyor; keşifte pay hariç E ile AUC 0.909 → 0.932 | E yalnızca etiketli tekrar karelerinde mi hesaplansın? Referans koddan sapma; karar danışmanda | Claude Code → danışman
2026-11-06 | AÇIK: Kişi bazlı AUC 0.800 (Vasil) – 0.985 (Honza); raporda ortalamanın yanında kişi aralığı verilmeli | Kullanıcının galeri gözlemi | Claude Code
