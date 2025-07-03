from django import forms
from .models import Customer

class LoginForm(forms.Form):
    account_number = forms.CharField(label='Kontonummer', max_length=8)
    pin            = forms.CharField(label='PIN', widget=forms.PasswordInput)
    totp_code      = forms.CharField(label='TOTP-Code', max_length=6)

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            'first_name','last_name','middle_names',
            'address_line1','address_line2','postal_code','city',
            'birth_date','phone','email'
        ]
        widgets = {
            'birth_date': forms.DateInput(attrs={'type':'date'})
        }
