from django.db import models

SECURITY_QUESTIONS = [
    ('mother_maiden', 'Wie lautet der Mädchenname Ihrer Mutter?'),
    ('first_pet', 'Wie hieß Ihr erstes Haustier?'),
    ('birth_city', 'In welcher Stadt wurden Sie geboren?'),
]

class Customer(models.Model):
    first_name       = models.CharField(max_length=50)
    last_name        = models.CharField(max_length=50)
    middle_names     = models.CharField(max_length=100, blank=True)
    address_line1    = models.CharField(max_length=100)
    house_number     = models.CharField(max_length=10)
    postal_code      = models.CharField(max_length=20)
    city             = models.CharField(max_length=50)
    address_extra    = models.CharField(max_length=100, blank=True)
    birth_date       = models.DateField()
    phone            = models.CharField(max_length=30)
    email            = models.EmailField()
    passport_number  = models.CharField(max_length=20, blank=True)
    security_enabled = models.BooleanField(default=False)
    security_question= models.CharField(max_length=20, choices=SECURITY_QUESTIONS, blank=True)
    security_answer  = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.last_name}, {self.first_name}"
