# Güncelleme 04 — 6 Kasım 2026 gece (danışmandan)

Claude Code: `/clear` sonrası yeni oturum. Sırayla oku:
1. `CLAUDE.md`
2. `PLAN.md`
3. `ilerleme/KARARLAR.md`
4. `ilerleme/ADIM_03.md`
5. bu dosya

Kararları `KARARLAR.md`'ye işle, sonra **Adım 4**'e başla.

Adım 3 temiz ve dürüst bir çalışmaydı. Özellikle genel bant sonucu beklenmedik çıktığında hata araması yapılması doğruydu.

## Kararlar

### Karar 10 — Zamansal yumuşatma ana yöntemde kullanılmaz
- Deney 1c'ye göre titreme %38–87 azaldı, ama AUC değişmedi (±0,006).
- Raporda Problem 2 için "denendi, etkisiz" olarak verilir. Yorumu: silkme, MediaPipe titremesinden çok daha büyük ve yavaş bir sinyal. E zaten kareler üzerinden ortalama alıyor.
- **Uygulamada da yumuşatma kullanılmaz.** One Euro gecikme ekliyor ve kazancı yok. Yalnızca ekranda iskelet çizimi titrek görünürse, **sadece görsel** amaçla hafif bir One Euro uygulanabilir. Karar hesaplarına girmez.
- `cekirdek/yumusatma.py` kalır.

### Karar 11 — Kişiye özel kalibrasyon zorunlu; "dinlenme ayarlı genel bant" denenmeyecek
- Deney 1b'ye göre genel bant kişiye özelden 0,19–0,33 AUC geride. Sonuç her ölçütte, her bant türünde ve iki görüş kapsamında tutarlı.
- Uygulama zaten kalibrasyon yapacağı için ara yol kapsam dışı. Gelecek çalışma olarak not edilir.

### Karar 12 — Karar 7'nin "pürüzsüzleştirme" notu kabul
- v2 − v1b farkı silkme/doğru ayrımında zaten anlamlı değil, bu yüzden bir iddiamız yok.
- Asıl iddia silkme/diğer ayrımı (+0,108, GA +0,053 – +0,190). Bu fark o etkiyle açıklanamayacak kadar büyük ve M33'te de aynı.
- Raporda not olarak geçer.

## Adım 4 için ek notlar
`PLAN.md` + Güncelleme 02 ve 03'e ek olarak:

1. **Adım 5'e hazırlık:** Açı bandı hatası, her ölçüt için kare bazında şunları döndürebilmeli:
   - imzalı sapma (bandın üstü veya altı, büyüklüğü);
   - faz (kaldırma / indirme);
   - kol açısı;
   - ölçütün **ham değeri** ve bandın μ değeri.

   Adım 5'teki "normalde X, sende Y" cümleleri buradan üretilecek. Gerekirse `ayrinti=True` benzeri bir çıktı ekle. Davranışı değiştirme; regresyon testleri geçmeli.
2. **Galeri:** Adım 4 sonunda `sonuclar/deney2/galeri/` (önden + çapraz). Gruplar:
   - en sık karışan iki hata çifti, örneğin "baş eğme → omuz denmiş";
   - kaçırılan hatalar ("doğru" denmiş).
   Her gruptan 3 video. Görsel araç, kararı veren ölçütün eğrisini ve bandını göstersin.
3. **Önce basit temel çizgi, sonra kural:** Tek toplam hatayla "doğru/yanlış" ayrımı (PLAN'daki temel çizgi) ve 6 sınıflı karar kuralı aynı tabloda yer alsın. Böylece "hata türünü bulmak" ile "bir şey yanlış demek" arasındaki fark görünür olur.
4. **Basit anlatım:** "100 hatalı tekrarın kaçında hatanın türünü doğru söyledi?" biçiminde bir cümle.
