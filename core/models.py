from django.db import models

class Customer(models.Model):
    first_name      = models.CharField(max_length=50)
    last_name       = models.CharField(max_length=50)
    middle_names    = models.CharField(max_length=100, blank=True)
    address_line1   = models.CharField(max_length=100)
    address_line2   = models.CharField(max_length=100, blank=True)
    postal_code     = models.CharField(max_length=20)
    city            = models.CharField(max_length=50)
    birth_date      = models.DateField()
    phone           = models.CharField(max_length=30)
    email           = models.EmailField()

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.last_name}, {self.first_name}"
