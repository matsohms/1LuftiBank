import os

def get_admin_iban(raw: bool = False) -> str:
    """
    Baut aus ENV-Variablen ADMIN_ACCOUNT_NUMBER (10-stellig) 
    und BANK_CODE (8-stellig) eine IBAN:
      OH11 AAAA BBBB CCCC DDDD EE
    wobei AAAA BBBB die Bankleitzahl und
    CCCC DDDD EE die 10-stellige Admin-Kontonummer in 4-4-2 splittet.
    """
    acct = os.getenv('ADMIN_ACCOUNT_NUMBER', '').zfill(10)
    blz  = os.getenv('BANK_CODE', '').zfill(8)
    # Prüfziffer statisch „11“
    parts = [
      "OH11",
      blz[:4],
      blz[4:],
      acct[:4],
      acct[4:8],
      acct[8:]
    ]
    if raw:
        # ohne Leerzeichen
        return "".join(parts)
    else:
        # mit Leerzeichen, gruppiert
        return " ".join(parts)
