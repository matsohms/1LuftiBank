import io
import base64
import os
import random

import qrcode
import pyotp

from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib import messages
from django.forms import ModelForm

from .models import Customer, Account, SECURITY_QUESTIONS
from .forms import (
    LoginForm,
    CustomerForm,
    AccountSettingsForm,
    AccountTOTPForm
)
from .utils import get_admin_iban  # Modul, das ADMIN_ACCOUNT_NUMBER & BANK_CODE ausliest

# ——————————————————————————————————————————————————————————————
# Helfer-Decorator für Admin-Schutz
# ——————————————————————————————————————————————————————————————
def require_admin(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('is_admin'):
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

# ——————————————————————————————————————————————————————————————
# Login / Logout
# ——————————————————————————————————————————————————————————————
def login_view(request):
    error = None
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            acc, pin, code = (
                form.cleaned_data['account_number'],
                form.cleaned_data['pin'],
                form.cleaned_data['totp_code'],
            )
            ADMIN_ACC    = os.getenv('ADMIN_ACCOUNT_NUMBER')
            ADMIN_PIN    = os.getenv('ADMIN_PIN')
            ADMIN_SECRET = os.getenv('ADMIN_TOTP_SECRET')
            totp = pyotp.TOTP(ADMIN_SECRET)
            if acc == ADMIN_ACC and pin == ADMIN_PIN and totp.verify(code):
                request.session.flush()
                request.session['is_admin'] = True
                request.session.save()
                return redirect('admin_dashboard')
            error = 'Kontonummer, PIN oder TOTP falsch.'
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form, 'error': error})

def logout_view(request):
    request.session.flush()
    return redirect('login')

# ——————————————————————————————————————————————————————————————
# Admin-Startseiten
# ——————————————————————————————————————————————————————————————
@require_admin
def admin_home(request):
    # leitet direkt zum Dashboard
    return redirect('admin_dashboard')

@require_admin
def admin_dashboard(request):
    """
    Zeigt IBAN, Kontostand (placeholder) und Links zu Kundenübersicht / -erstellung.
    """
    admin_iban = get_admin_iban()
    # Platzhalter-Kontostand
    balance = "2.597.800.000,00"
    return render(request, 'admin_dashboard.html', {
        'admin_iban': admin_iban,
        'balance': balance
    })

# ——————————————————————————————————————————————————————————————
# Kundenübersicht mit Suche
# ——————————————————————————————————————————————————————————————
@require_admin
def customer_list(request):
    q = request.GET.get('q', '').strip()
    customers = Customer.objects.all()
    if q:
        customers = customers.filter(
            Q(last_name__icontains=q) |
            Q(first_name__icontains=q) |
            Q(customer_number__icontains=q)
        )
    return render(request, 'customer_list.html', {
        'customers': customers,
        'q': q
    })

# ——————————————————————————————————————————————————————————————
# Kunde anlegen
# ——————————————————————————————————————————————————————————————
@require_admin
def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('customer_list')
    else:
        form = CustomerForm()
    return render(request, 'customer_form.html', {
        'form': form, 'edit': False
    })

# ——————————————————————————————————————————————————————————————
# Kunde bearbeiten
# ——————————————————————————————————————————————————————————————
@require_admin
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('customer_detail', pk=pk)
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'customer_form.html', {
        'form': form, 'edit': True
    })

# ——————————————————————————————————————————————————————————————
# Kundenprofil anzeigen
# ——————————————————————————————————————————————————————————————
@require_admin
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    return render(request, 'customer_detail.html', {
        'customer': customer
    })

# ——————————————————————————————————————————————————————————————
# Kunde löschen
# ——————————————————————————————————————————————————————————————
@require_admin
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    expected = f'Kunde {customer.customer_number} löschen'
    if request.method == 'POST':
        confirm = request.POST.get('confirm_input', '').strip().lower()
        if confirm == expected.lower():
            customer.delete()
            messages.success(request, f'Kunde {customer.customer_number} wurde gelöscht.')
            return redirect('customer_list')
        messages.error(request, f'Bitte genau "{expected}" eingeben.')
    return render(request, 'customer_confirm_delete.html', {
        'customer': customer, 'expected': expected
    })

# ——————————————————————————————————————————————————————————————
# Sicherheitsprüfung
# ——————————————————————————————————————————————————————————————
@require_admin
def customer_security(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    result = None
    if request.method == 'POST':
        answer = request.POST.get('security_answer', '').strip()
        if customer.security_level == 'pin':
            result = 'correct' if answer == customer.security_answer else 'incorrect'
        else:
            result = 'correct' if answer.lower() == customer.security_answer.lower() else 'incorrect'
    return render(request, 'customer_security.html', {
        'customer': customer, 'result': result
    })

# ——————————————————————————————————————————————————————————————
# Konto-Erstellung Schritt 1: Einstellungen in Session
# ——————————————————————————————————————————————————————————————
@require_admin
def account_create_step1(request, customer_pk):
    customer = get_object_or_404(Customer, pk=customer_pk)
    if request.method == 'POST':
        form = AccountSettingsForm(request.POST)
        if form.is_valid():
            # Form-Daten in Session speichern
            request.session['new_account_data'] = form.cleaned_data
            # Kontonummer & TOTP-Secret generieren
            from .models import gen_account_number
            acct_no = gen_account_number()
            totp_secret = pyotp.random_base32()
            request.session['new_account_number'] = acct_no
            request.session['new_totp_secret'] = totp_secret
            return redirect('account_create_step2', customer_pk=customer_pk)
    else:
        form = AccountSettingsForm()
    return render(request, 'account_step1.html', {
        'form': form, 'customer': customer
    })

# ——————————————————————————————————————————————————————————————
# Konto-Erstellung Schritt 2: QR-Code & TOTP-Verifikation
# ——————————————————————————————————————————————————————————————
@require_admin
def account_create_step2(request, customer_pk):
    acct_no    = request.session.get('new_account_number')
    totp_secret= request.session.get('new_totp_secret')
    if not acct_no or not totp_secret:
        return redirect('account_create_step1', customer_pk=customer_pk)

    totp = pyotp.TOTP(totp_secret)
    uri  = totp.provisioning_uri(name=acct_no, issuer_name="LuftiBank")
    img  = qrcode.make(uri)
    buf  = io.BytesIO(); img.save(buf, format='PNG')
    qr_b64 = base64.b64encode(buf.getvalue()).decode()

    error = None
    if request.method == 'POST':
        code = request.POST.get('totp_code','').strip()
        if totp.verify(code):
            return redirect('account_create_step3', customer_pk=customer_pk)
        error = 'Ungültiger TOTP-Code. Bitte erneut scannen und testen.'

    return render(request, 'account_step2.html', {
        'qr_code': qr_b64,
        'error':   error
    })

# ——————————————————————————————————————————————————————————————
# Konto-Erstellung Schritt 3: Abschluss & echte DB-Anlage
# ——————————————————————————————————————————————————————————————
@require_admin
def account_create_step3(request, customer_pk):
    data    = request.session.get('new_account_data')
    acct_no = request.session.get('new_account_number')
    secret  = request.session.get('new_totp_secret')
    if not data or not acct_no or not secret:
        return redirect('account_create_step1', customer_pk=customer_pk)

    if request.method == 'POST':
        form = AccountTOTPForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['totp_check']
            if pyotp.TOTP(secret).verify(code):
                # Erst jetzt Konto in der DB speichern
                customer = get_object_or_404(Customer, pk=customer_pk)
                acc = Account(
                    customer=customer,
                    account_number=acct_no,
                    totp_secret=secret,
                    **data
                )
                acc.save()
                # Session aufräumen
                for k in ('new_account_data','new_account_number','new_totp_secret'):
                    request.session.pop(k, None)
                return redirect('customer_detail', pk=customer_pk)
            form.add_error('totp_check','Ungültiger TOTP-Code.')
    else:
        form = AccountTOTPForm()

    return render(request, 'account_step3.html', {
        'form':          form,
        'account_number': acct_no
    })

# ——————————————————————————————————————————————————————————————
# Konto bearbeiten
# ——————————————————————————————————————————————————————————————
class AccountForm(ModelForm):
    class Meta:
        model  = Account
        fields = [
            'account_model',
            'max_balance', 'free_up_to', 'cost_within',
            'free_above',  'cost_above'
        ]

@require_admin
def account_edit(request, customer_pk, account_pk):
    account = get_object_or_404(Account, pk=account_pk, customer__pk=customer_pk)
    if request.method == 'POST':
        form = AccountForm(request.POST, instance=account)
        if form.is_valid():
            form.save()
            return redirect('customer_detail', pk=customer_pk)
    else:
        form = AccountForm(instance=account)
    return render(request, 'account_form.html', {
        'form': form,
        'customer': account.customer,
        'edit': True
    })

# ——————————————————————————————————————————————————————————————
# PIN ändern
# ——————————————————————————————————————————————————————————————
@require_admin
def account_pin_change(request, customer_pk, account_pk):
    account = get_object_or_404(Account, pk=account_pk, customer__pk=customer_pk)
    if request.method == 'POST':
        new_pin = ''.join(str(random.randint(0,9)) for _ in range(5))
        account.pin = new_pin
        account.save()
        return render(request, 'account_pin_changed.html', {
            'customer': account.customer,
            'account': account,
            'new_pin': new_pin
        })
    return render(request, 'account_pin_confirm.html', {
        'customer': account.customer,
        'account': account
    })

# ——————————————————————————————————————————————————————————————
# Konto löschen
# ——————————————————————————————————————————————————————————————
@require_admin
def account_delete(request, customer_pk, account_pk):
    account = get_object_or_404(Account, pk=account_pk, customer__pk=customer_pk)
    expected = f"konto {account.account_number} löschen"
    error = None
    if request.method == 'POST':
        inp = request.POST.get('confirm_input','').strip().lower()
        if inp == expected:
            account.delete()
            messages.success(request, f"Konto {account.account_number} gelöscht.")
            return redirect('customer_detail', pk=customer_pk)
        error = f'Bitte genau "{expected}" eingeben.'
    return render(request, 'account_confirm_delete.html', {
        'account': account,
        'error': error
    })
