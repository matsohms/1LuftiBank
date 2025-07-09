from django import forms
from .models import Customer, SECURITY_QUESTIONS, Account

class LoginForm(forms.Form):
    account_number = forms.CharField(
        label='Kontonummer',
        max_length=10,
        min_length=10,
        widget=forms.TextInput(attrs={
            'placeholder': '10-stellige Nummer',
        }),
    )
    pin = forms.CharField(
        label='PIN',
        max_length=5,
        min_length=5,
        widget=forms.PasswordInput(attrs={
            'placeholder': '5-stellige PIN',
        }),
    )
    totp_code = forms.CharField(
        label='TOTP-Code',
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'placeholder': '6-stelliger Code',
        }),
    )

class CustomerForm(forms.ModelForm):
    SECURITY_LEVELS = [
        ('none',     'Keine'),
        ('question', 'Sicherheitsfrage'),
        ('pin',      'PIN'),
    ]

    security_level = forms.ChoiceField(
        label='Erweiterte Sicherheitsstufe',
        choices=SECURITY_LEVELS,
        required=False
    )
    security_question = forms.ChoiceField(
        label='Sicherheitsfrage',
        choices=SECURITY_QUESTIONS,
        required=False
    )
    security_answer = forms.CharField(
        label='Antwort / PIN',
        max_length=100,
        required=False,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Antwort oder PIN eingeben',
        }),
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
            'account_model',
            'max_balance',
            'free_up_to', 'cost_within',
            'free_above', 'cost_above',
        ]
        widgets = {
            'account_model': forms.TextInput(attrs={
                'placeholder': 'Bezeichnung des Modells',
            }),
            'max_balance': forms.NumberInput(attrs={
                'step': '0.01',
                'placeholder': 'Betrag in LUF',
                'data-currency': 'true',
            }),
            'free_up_to': forms.NumberInput(attrs={
                'step': '0.01',
                'placeholder': 'Betrag für Gratis-Überweisungen',
                'data-currency': 'true',
                'id': 'id_free_up_to',
            }),
            'cost_within': forms.NumberInput(attrs={
                'step': '0.01',
                'placeholder': 'Kosten in LUF oder %',
                'data-currency': 'true',
                'id': 'id_cost_within',
            }),
            'free_above': forms.NumberInput(attrs={
                'step': '0.01',
                'placeholder': 'Freies Volumen oberhalb',
                'data-currency': 'true',
            }),
            'cost_above': forms.NumberInput(attrs={
                'step': '0.01',
                'placeholder': 'Kosten in LUF oder %',
                'data-currency': 'true',
            }),
        }

class AccountTOTPForm(forms.Form):
    totp_check = forms.CharField(
        label='TOTP-Code bestätigen',
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'placeholder': '6-stelliger Code',
        }),
    )
