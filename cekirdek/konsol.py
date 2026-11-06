"""
Çıktı yardımcıları.

  * utf8_cikti   : Windows konsolu (cp1254) Ψ, °, – gibi karakterleri yazamayabilir; çıktıyı UTF-8'e çevirir.
  * sonuclari_yaz: Sonuç tablolarını CSV (asıl kayıt) ve Excel'de düzgün açılan bir .xlsx kopyası olarak yazar.
    CSV'ler UTF-8 BOM ile yazılır, böylece Excel Türkçe karakterleri doğru gösterir. Türkçe Excel, CSV'deki
    ondalık noktayı binlik ayırıcı sanabildiği için Excel'de bakarken .xlsx dosyası kullanılmalı.
"""
import sys
from pathlib import Path


def utf8_cikti() -> None:
    for akim in (sys.stdout, sys.stderr):
        try:
            akim.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def sonuclari_yaz(tablolar: dict, klasor, xlsx_adi: str = "sonuclar.xlsx") -> None:
    """tablolar: {ad: DataFrame}. Her biri <ad>.csv olur; hepsi ayrıca tek bir .xlsx'te ayrı sayfalar."""
    import pandas as pd

    klasor = Path(klasor)
    klasor.mkdir(parents=True, exist_ok=True)
    for ad, df in tablolar.items():
        df.to_csv(klasor / f"{ad}.csv", index=False, encoding="utf-8-sig")
    try:
        with pd.ExcelWriter(klasor / xlsx_adi) as yazici:
            for ad, df in tablolar.items():
                df.to_excel(yazici, sheet_name=ad[:31], index=False)
    except ImportError:  # openpyxl yoksa yalnızca CSV
        pass
