import random
import pyotp
from datetime import datetime
from django.db import models

# ——————————————————————————————————————————————————————————————
# Sicherheitsfragen für Kunden
# ——————————————————————————————————————————————————————————————
SECURITY_QUESTIONS = [
    ('mother_maiden', 'Wie lautet der Mädchenname Ihrer Mutter?'),
    ('first_pet',     'Wie hieß Ihr erstes Haustier?'),
    ('birth_city',    'In welcher Stadt wurden Sie geboren?'),
]

# ——————————————————————————————————————————————————————————————
# Kunden-Modell
# ——————————————————————————————————————————————————————————————
class Customer(models.Model):
    first_name        = models.CharField(max_length=50)
    middle_names      = models.CharField(max_length=100, blank=True)
    last_name         = models.CharField(max_length=50)
    address_line1     = models.CharField(max_length=100)
    house_number      = models.CharField(max_length=10)
    postal_code       = models.CharField(max_length=20)
    city              = models.CharField(max_length=50)
    address_extra     = models.CharField(max_length=100, blank=True)
    birth_date        = models.DateField()
    phone             = models.CharField(max_length=30)
    email             = models.EmailField()
    passport_number   = models.CharField(max_length=20, blank=True)
    security_level    = models.CharField(
        max_length=10,
        choices=[('none','Keine'),('question','Sicherheitsfrage'),('pin','PIN')],
        default='none'
    )
    security_question = models.CharField(
        max_length=20,
        choices=SECURITY_QUESTIONS,
        blank=True
    )
    security_answer   = models.CharField(max_length=100, blank=True)
    created_at        = models.DateTimeField(auto_now_add=True)
    customer_number   = models.CharField(
        max_length=12,
        unique=True,
        editable=False
    )

    class Meta:
        ordering = ['last_name', 'first_name']

    def save(self, *args, **kwargs):
        if not self.pk:
            super().save(*args, **kwargs)
            year = datetime.now().strftime('%y')
            self.customer_number = f"LB{year}{self.pk:06d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.last_name}, {self.first_name}"

# ——————————————————————————————————————————————————————————————
# Hilfsfunktionen für Konto-Generierung
# ——————————————————————————————————————————————————————————————
def gen_account_number():
    # 20-stellige Zufallsnummer
    return ''.join(str(random.randint(0,9)) for _ in range(20))

def gen_iban(acc):
    # OH82 (Prüfziffer), 7827 (Bankcode), dann 5×4-Stellen
    groups = [acc[i:i+4] for i in range(0, 20, 4)]
    return f"OH82 7827 {' '.join(groups)}"

# ——————————————————————————————————————————————————————————————
# Konto-Modell für Kundenkonten
# ——————————————————————————————————————————————————————————————
class Account(models.Model):
    customer        = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='accounts'
    )
    account_number  = models.CharField(
        max_length=20,
        unique=True,
        default=gen_account_number
    )
    iban            = models.CharField(
        max_length=34,
        unique=True,
        blank=True
    )
    pin             = models.CharField(max_length=5, blank=True)
    totp_secret     = models.CharField(max_length=32, blank=True)
    account_model   = models.CharField(max_length=100)
    max_balance     = models.DecimalField(max_digits=14, decimal_places=2)
    free_up_to      = models.DecimalField(
        max_digits=14, decimal_places=2,
        null=True, blank=True
    )
    cost_within     = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True
    )
    free_above      = models.DecimalField(
        max_digits=14, decimal_places=2,
        null=True, blank=True
    )
    cost_above      = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True
    )
    created_at      = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.iban:
            self.iban = gen_iban(self.account_number)
        if not self.pin:
            self.pin = ''.join(str(random.randint(0,9)) for _ in range(5))
        if not self.totp_secret:
            self.totp_secret = pyotp.random_base32()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.account_number} ({self.account_model})"
