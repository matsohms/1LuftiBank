from django import forms
from .models import Customer, SECURITY_QUESTIONS

class LoginForm(forms.Form):
    account_number = forms.CharField(label='Kontonummer', max_length=8)
    pin            = forms.CharField(label='PIN', widget=forms.PasswordInput)
    totp_code      = forms.CharField(label='TOTP-Code', max_length=6)

class CustomerForm(forms.ModelForm):
    SECURITY_LEVELS = [
        ('none', 'Keine'),
        ('question', 'Sicherheitsfrage'),
        ('pin', 'PIN'),
    ]
    security_level = forms.ChoiceField(label='Erweiterte Sicherheitsstufe',
        choices=SECURITY_LEVELS, required=False)
    security_response = forms.CharField(label='Antwort / PIN', max_length=100, required=True)
        widget=forms.TextInput)

    class Meta:
        model = Customer
        fields = [
            'first_name','last_name','middle_names',
            'address_line1','house_number','postal_code','city','address_extra',
            'birth_date','phone','email','passport_number',
            'security_level','security_question','security_answer'
        ]
        widgets = {
            'birth_date': forms.DateInput(attrs={'type':'date'}),
            'security_question': forms.Select(choices=SECURITY_QUESTIONS),
        }
