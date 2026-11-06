"""Hata kodlarının ve ölçütlerin kullanıcıya gösterilen Türkçe adları."""

HATA_ADLARI = {
    "DOGRU": "doğru",
    "ERR_ELEVATED_SHOULDER": "omuz silkme (omuz kulağa doğru kalkıyor)",
    "ERR_HEAD_TO_SIDE": "baş yana eğik",
    "ERR_ARM_FORWARD": "kol öne kaçıyor",
    "ERR_BENT_ARM": "dirsek bükük",
    "ERR_LOW_ABDUCTION": "kol yeterince kalkmıyor",
}

OLCUT_ADLARI = {
    "kol": "kol açısı",
    "YENI": "kulak – omuz mesafesi",
    "M01": "iki omuz kalkışı",
    "M01_tek": "sağ omuz kalkışı",
    "M39_F2": "sağ omuz açısı",
    "M33": "sağ omuz – omuz ortası",
    "bas": "baş eğikliği (°)",
    "on_kacma": "bilek – omuz – kalça açısı (°)",
    "kol_boyu": "omuz – bilek mesafesi / gövde",
    "dirsek": "dirsek açısı (°)",
    "kaldirma": "tepe kol açısı sapması",
}


def hata_adi(kod: str) -> str:
    return HATA_ADLARI.get(kod, kod)


def ek_hata_adlari(ek: str) -> str:
    """Virgülle ayrılmış ek hata kodlarını Türkçe adlara çevirir; yoksa boş."""
    return ", ".join(hata_adi(k.strip()) for k in ek.split(",") if k.strip())
