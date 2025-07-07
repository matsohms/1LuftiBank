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
from django.contrib import messages

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
    return render(request, 'admin_home.html')

@require_admin
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')

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
        'form': form,
        'edit': False
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
        'form': form,
        'edit': True
    })

# ——————————————————————————————————————————————————————————————
# Kundenprofil anzeigen
# ——————————————————————————————————————————————————————————————
@require_admin
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    return render(request, 'customer_detail.html', {'customer': customer})

# ——————————————————————————————————————————————————————————————
# Kunde löschen mit Bestätigung
# ——————————————————————————————————————————————————————————————
@require_admin
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    # Erwarteter Text (noch mit Großbuchstaben für die Anzeige)
    expected = f'Kunde {customer.customer_number} löschen'
    # Für den Vergleich in Kleinbuchstaben
    expected_lower = expected.lower()

    if request.method == 'POST':
        confirm = request.POST.get('confirm_input', '').strip().lower()
        if confirm == expected_lower:
            customer.delete()
            messages.success(request, f'Kunde {customer.customer_number} wurde gelöscht.')
            return redirect('customer_list')
        else:
            messages.error(
                request,
                f'Bitte genau "{expected}" eingeben.'
            )

    return render(request, 'customer_confirm_delete.html', {
        'customer': customer,
        'expected': expected  # bleibt mit Großbuchstaben für die Anzeige
    })

# ——————————————————————————————————————————————————————————————
# Sicherheitsprüfung (Feedback korrekt/falsch)
# ——————————————————————————————————————————————————————————————
@require_admin
def customer_security(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    result = None

    if request.method == 'POST':
        answer = request.POST.get('security_answer', '').strip()
        if customer.security_level == 'pin':
            result = 'correct' if answer == customer.security_answer else 'incorrect'
        else:  # Frage
            result = 'correct' if answer.lower() == customer.security_answer.lower() else 'incorrect'

    return render(request, 'customer_security.html', {
        'customer': customer,
        'result':   result
    })

@require_admin
def account_create_step1(request, customer_pk):
    customer = get_object_or_404(Customer, pk=customer_pk)
    if request.method == 'POST':
        form = AccountSettingsForm(request.POST)
        if form.is_valid():
            acc = form.save(commit=False)
            acc.customer = customer
            acc.save()
            request.session['new_account_id'] = acc.id
            return redirect('account_create_step2', customer_pk=customer_pk)
    else:
        form = AccountSettingsForm()
    return render(request, 'account_step1.html', {
        'form': form, 'customer': customer
    })

@require_admin
def account_create_step2(request, customer_pk, account_pk):
    """
    Zeigt den TOTP-QR-Code für das neu angelegte Konto an und verifiziert den
    vom Admin eingegebenen TOTP-Code, bevor wir zu Step 3 weitergehen.
    """
    account = get_object_or_404(Account, pk=account_pk, customer__pk=customer_pk)

    # Erzeuge Provisioning-URI und daraus ein QR-Bild
    totp = pyotp.TOTP(account.totp_secret)
    uri  = totp.provisioning_uri(
        name=account.account_number,
        issuer_name="LuftiBank"
    )
    img = qrcode.make(uri)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    qr_b64 = base64.b64encode(buf.getvalue()).decode()  # Base64-String für <img>

    error = None
    if request.method == 'POST':
        code = request.POST.get('totp_code', '').strip()
        if totp.verify(code):
            return redirect(
                'account_create_step3',
                customer_pk=customer_pk,
                account_pk=account_pk
            )
        else:
            error = 'Ungültiger TOTP-Code. Bitte erneut scannen und testen.'

    return render(request, 'account_step2.html', {
        'account': account,
        'qr_code': qr_b64,
        'error':    error
    })

@require_admin
def account_create_step3(request, customer_pk):
    acc = get_object_or_404(Account, id=request.session.get('new_account_id'))
    if request.method == 'POST':
        form = AccountTOTPForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['totp_check']
            if pyotp.TOTP(acc.totp_secret).verify(code):
                del request.session['new_account_id']
                return redirect('customer_detail', pk=customer_pk)
            form.add_error('totp_check', 'Ungültiger TOTP-Code.')
    else:
        form = AccountTOTPForm()
    return render(request, 'account_step3.html', {
        'form': form, 'account': acc
    })

class AccountForm(ModelForm):
    class Meta:
        model = Account
        fields = [
            'account_model',
            'max_balance','free_up_to','cost_within',
            'free_above','cost_above'
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

# ------------- PIN ändern -------------
@require_admin
def account_pin_change(request, customer_pk, account_pk):
    account = get_object_or_404(Account, pk=account_pk, customer__pk=customer_pk)
    if request.method == 'POST':
        # einfache Neugenerierung
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

@require_admin
def account_delete(request, customer_pk, account_pk):
    account = get_object_or_404(Account, pk=account_pk, customer__pk=customer_pk)
    expected = f'konto {account.account_number} löschen'
    error = None

    if request.method == 'POST':
        inp = request.POST.get('confirm_input','').strip().lower()
        if inp == expected:
            account.delete()
            messages.success(request, f'Konto {account.account_number} gelöscht.')
            return redirect('customer_detail', pk=customer_pk)
        else:
            error = f'Bitte genau "{expected}" eingeben.'

    return render(request, 'account_confirm_delete.html', {
        'account': account,
        'error': error
    })
