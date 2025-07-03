from django import forms

class LoginForm(forms.Form):
    account_number = forms.CharField(label='Kontonummer', max_length=8)
    pin            = forms.CharField(label='PIN', widget=forms.PasswordInput)
    totp_code      = forms.CharField(label='TOTP-Code', max_length=6)
