# Güncelleme 03 — 6 Kasım 2026 gece (danışmandan)

Claude Code: `/clear` sonrası yeni oturum. Sırayla oku: `CLAUDE.md`, `PLAN.md`, `ilerleme/KARARLAR.md`, `ilerleme/ADIM_02c.md`, bu dosya. Kararları `KARARLAR.md`'ye işle, `PLAN.md`'yi güncelle, sonra aşağıdaki "Yapılacaklar" sırasıyla ilerle.

Adım 2c çok iyi bir ablasyondu. Özellikle tohum duyarlılığı analizi ve profil bulgusu değerliydi.

## Danışmanın yorumu (kısaca)
- **Silkme/doğru ayrımı:** Pay hariç ve çoklu referans küçük ama güvenilir kazançlar veriyor (+0,018, +0,014). Açı bandı bu ayrımda zaman bandıyla aynı düzeyde (fark −0,006, GA sıfırı içeriyor).
- **Silkme/diğer ayrımı:** Açı bandının asıl katkısı burada, ve 5 ölçütün hepsinde görülüyor (YENI 0,713 → 0,812). Geri bildirim cümlesinin doğru hatayı söylemesi için en önemli özellik bu.
- **Profil görünüm:** Açı bandının profilde kötüleşmesi, 2B kol açısının profilde ölçülemez olmasıyla tutarlı. Yöntemin ön koşulu: kol açısı kameradan ölçülebilir olmalı.

## Kararlar

### Karar 6 — Tek yöntem: açı bandı; profil bir sınırlılık
- Adım 4 ve sonrasında duruş ölçütleri için **yalnızca açı bandı** kullanılır. Görüşe göre yöntem değiştiren karma bir çözüm yapılmaz, çünkü test sonuçlarına bakılarak seçilmiş olur.
- **Raporlama:** Her ana sonuç iki şekilde verilir. Bu karar Adım 4 sonuçları görülmeden, şimdi veriliyor.
  - "uygulama senaryosu: önden + çapraz (|görüş| ≤ 60°)"
  - "tüm görüşler"
- Profil (70–90°) sınırlılık olarak ayrıca raporlanır, gerekçesiyle: yana kaldırma profilden kameraya doğru veya kameradan uzağa bir hareket olduğu için 2B kol açısı bozulur.
- v1b (zaman bandı, çoklu referans) **karşılaştırma temel çizgisi** olarak Adım 4'te de raporlanır. Karar kuralına girmez.

### Karar 7 — "Atla" rastgeleliği kaldırılır: tüm (n−1)'li modellerin ortalaması
Hatalı bir tekrar değerlendirilirken, adil model için tek bir doğru tekrar rastgele dışarıda bırakılmıyordu; bundan vazgeçiliyor. Yeni yöntem:
- Her doğru tekrar **sırayla** dışarıda bırakılır, n model kurulur, E'lerin ortalaması alınır.
- Doğru tekrarlar zaten birini-dışarıda-bırak ile değerlendiriliyor; onlar değişmez.
- Bu, v1b ve v2'de E'yi tamamen **deterministik** yapar.
- Kabul ölçütü: tohum 0 ile 1 arasında |ΔE| hatalı tekrarlarda da 0.

### Karar 8 — Uygulamada kalibrasyon en az 6 doğru tekrar
4 tekrarlık modellerde "en az 3 tekrar" kuralı sınırda kalıyor. ADIM_02c'deki 0,89'luk değişim bundan. Veri setinde sayı sabit (yaklaşık 5), değiştirilemez. Adım 6'daki uygulamada:
- kalibrasyon varsayılan 6 doğru tekrar, en az 5;
- arayüz bunu söyler.

### Karar 9 — Uygulamada kamera açısı kontrolü
Adım 6'ya eklenir. Kalibrasyonun başında, dinlenme duruşundaki omuz genişliği / gövde uzunluğu oranından kişinin kameraya ne kadar dönük olduğu kabaca tahmin edilir.
- Oran, önden durumdaki tipik değerin belirgin altındaysa uyarı verilir: "Kameraya daha önden durun."
- Tipik değer veri setinin önden (0–20°) doğru tekrarlarından alınır.
- Eşik ve gerekçe ADIM_06'ya yazılır.

## Yapılacaklar (sırasıyla)

1. **Karar 7'yi uygula** ve Deney 1 v2'yi yeniden çalıştır. Sonuçları `sonuclar/deney1_v2/` altına yaz; eski çıktıyı `sonuclar/deney1_v2_atla_rastgele/` olarak sakla.
   - `bootstrap.csv`'ye **silkme/diğer** ayrımı için farkları ekle: v2 − v1b ve v2 − v1, YENI ve M33 için.
   - Ablasyon tablosuna "önden + çapraz" sütununu ekle.
   - Bu kısa bir alt adım: ADIM_02c'nin sonuna "Ek: Güncelleme 03" bölümü olarak yaz, yeni ADIM dosyası açma. Kullanıcıya yalnızca yeni tablo ile eskisi arasındaki farkları anlat.
2. **Adım 3** (Deney 1b genel bant + Deney 1c yumuşatma), v1b ve v2 ile, Karar 6'daki iki raporlama biçimiyle.
3. **Adım 4**: Güncelleme 02 + Karar 6–7.

## Kullanıcıya not (Claude Code, ADIM dosyalarında)
Kullanıcı tabloları yorumlamakta zorlanıyor. Her ADIM dosyasının "Basit anlatım" bölümünde:
- en önemli **tek** sonucu bir cümleyle söyle;
- ardından "bu sayı ne demek" diye bir örnekle açıkla (ör. "100 silkmeli tekrarın ...");
- ayrıntılı tabloları sonra ver.
