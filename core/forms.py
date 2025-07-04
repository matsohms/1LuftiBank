from django import forms
from .models import Customer, SECURITY_QUESTIONS

class LoginForm(forms.Form):
    account_number = forms.CharField(label='Kontonummer', max_length=8)
    pin            = forms.CharField(label='PIN', widget=forms.PasswordInput)
    totp_code      = forms.CharField(label='TOTP-Code', max_length=6)

class CustomerForm(forms.ModelForm):
    security_enabled = forms.BooleanField(label='Mit Sicherheitsfrage', required=False)
    class Meta:
        model = Customer
        fields = [
            'first_name','last_name','middle_names',
            'address_line1','house_number', 'postal_code','city','address_extra',
            'birth_date','phone','email','passport_number',
            'security_enabled','security_question','security_answer'
        ]
        widgets = {
            'birth_date': forms.DateInput(attrs={'type':'date'}),
            'security_question': forms.Select(choices=SECURITY_QUESTIONS),
            'security_answer': forms.PasswordInput(render_value=False)
        }
