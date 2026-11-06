"""
Anahtar kelime çıkarıcı için elle yazılmış cümleler (ADIM_05, önceden belirlenenler madde 8).
Deney 3 çalıştırılmadan önce yazıldı; şablonlardan farklı ifadeler, iki hatalı ve olumlu cümleler.
Beklenen: söz edilen hata türleri, metindeki ilk geçiş sırasıyla.
"""
O, B, K, D, L = ("ERR_ELEVATED_SHOULDER", "ERR_HEAD_TO_SIDE", "ERR_ARM_FORWARD", "ERR_BENT_ARM",
                 "ERR_LOW_ABDUCTION")

ELLE_CUMLELER = [
    ("Omzunu kulağına doğru çekiyorsun, omzunu aşağıda tut.", [O]),
    ("Kolu kaldırırken omuz yükseliyor; omzunu gevşet.", [O]),
    ("Başını yana yatırma, karşıya bak.", [B]),
    ("Kafanı dik tut.", [B]),
    ("Dirseğini bükme, kolun tamamen düz olsun.", [D]),
    ("Kolunu düz tut, bükme.", [D]),
    ("Kolun öne kaçıyor; tam yana doğru kaldır.", [K]),
    ("Kolunu vücudunla aynı hizada tut.", [K]),
    ("Kolunu daha yukarı kaldırmalısın, omuz hizasının üstüne çık.", [L]),
    ("Kolunu yeterince kaldırmadın, yaklaşık 20 derece daha yukarı uzan.", [L]),
    ("Hareketi doğru yaptın, omzun ve dirseğin normal aralıkta kaldı.", []),
    ("Harika, böyle devam et.", []),
    ("Omzunu kaldırıyorsun ve başını da yana eğiyorsun.", [O, B]),
    ("Başını eğme; ayrıca dirseğin bükülüyor.", [B, D]),
    ("Dirseğin hafif bükük, ayrıca kolunu biraz daha yukarı kaldır.", [D, L]),
    ("Kolun ileri gidiyor, kolunu yana açarak kaldır.", [K]),
    ("Sağ omzun kulağına yaklaşıyor.", [O]),
    ("Boynunu yana bükme.", [B]),
    ("Kolunu tam kaldıramadın; normalde 160 dereceye çıkıyordun.", [L]),
    ("İyi iş, duruşun normal sınırlarda.", []),
    ("Omzunu silkme.", [O]),
    ("Kolunu biraz öne kaydırıyorsun, gövdenle aynı düzlemde tut.", [K]),
    ("Omzun kalkmadı, kolun düzdü, güzel tekrar.", []),
    ("Kolunu indirirken omzun yukarıda kalıyor, omzunu indir.", [O]),
]
