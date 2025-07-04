from django.db import models
from datetime import datetime

SECURITY_QUESTIONS = [
    ('mother_maiden', 'Wie lautet der Mädchenname Ihrer Mutter?'),
    ('first_pet',     'Wie hieß Ihr erstes Haustier?'),
    ('birth_city',    'In welcher Stadt wurden Sie geboren?'),
]

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
    security_question = models.CharField(max_length=20, choices=SECURITY_QUESTIONS, blank=True)
    security_answer   = models.CharField(max_length=100, blank=True)
    created_at        = models.DateTimeField(auto_now_add=True)
    customer_number   = models.CharField(max_length=12, unique=True, editable=False)

    class Meta:
        ordering = ['last_name', 'first_name']

    def save(self, *args, **kwargs):
        # Generiere customer_number beim ersten Speichern
        if not self.pk:
            year = datetime.now().strftime('%y')
            # Temporär speichern, um eine ID zu bekommen
            super().save(*args, **kwargs)
            self.customer_number = f"LB{year}{self.pk:06d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.last_name}, {self.first_name}"
