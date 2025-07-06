from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
import os, pyotp

from .forms import LoginForm, CustomerForm
from .models import Customer

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
