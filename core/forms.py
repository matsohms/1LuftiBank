from django import forms
from .models import Customer, SECURITY_QUESTIONS

class LoginForm(forms.Form):
    account_number = forms.CharField(label='Kontonummer', max_length=8)
    pin            = forms.CharField(label='PIN', widget=forms.PasswordInput)
    totp_code      = forms.CharField(label='TOTP-Code', max_length=6)

class CustomerForm(forms.ModelForm):
    SECURITY_LEVELS = [
        ('none',     'Keine'),
        ('question', 'Sicherheitsfrage'),
        ('pin',      'PIN'),
    ]

    security_level    = forms.ChoiceField(
        label='Erweiterte Sicherheitsstufe',
        choices=SECURITY_LEVELS,
        required=False
    )
    security_question = forms.ChoiceField(
        label='Sicherheitsfrage',
        choices=SECURITY_QUESTIONS,
        required=False
    )
    security_answer   = forms.CharField(
        label='Antwort / PIN',
        max_length=100,
        required=False,  # wir validieren im View je nach Level
        widget=forms.PasswordInput
    )

    class Meta:
        model = Customer
        fields = [
            'first_name', 'middle_names', 'last_name',
            'address_line1', 'house_number', 'postal_code', 'city', 'address_extra',
            'birth_date', 'phone', 'email', 'passport_number',
            'security_level', 'security_question', 'security_answer'
        ]
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }

class AccountSettingsForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = [
            'account_model', 'max_balance',
            'free_up_to', 'cost_within',
            'free_above', 'cost_above',
        ]
        widgets = {
            'max_balance': forms.NumberInput(attrs={'step':'0.01'}),
            'free_up_to':  forms.NumberInput(attrs={'step':'0.01'}),
            'cost_within': forms.NumberInput(attrs={'step':'0.01'}),
            'free_above':  forms.NumberInput(attrs={'step':'0.01'}),
            'cost_above':  forms.NumberInput(attrs={'step':'0.01'}),
        }

class AccountTOTPForm(forms.Form):
    totp_check = forms.CharField(label='TOTP-Code', max_length=6)
