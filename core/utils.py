import os
import random

def get_admin_iban() -> str:
    """
    Baut eine IBAN zusammen aus:
      - Ländercode OH
      - Prüfziffer 11 (statisch für Admin)
      - BANK_CODE aus ENV (4 Stellen)
      - Admin-Kontonummer (10 Stellen aus ENV), gruppiert 4-4-2
    """
    BANK_CODE = os.getenv('BANK_CODE', '0000').zfill(4)
    admin_acc = os.getenv('ADMIN_ACCOUNT_NUMBER', '').zfill(10)
    # Gruppen aufteilen
    g1, g2, g3 = admin_acc[:4], admin_acc[4:8], admin_acc[8:]
    return f"OH11 {BANK_CODE} {g1} {g2} {g3}"
