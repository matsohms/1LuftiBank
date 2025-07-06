from django.shortcuts import render, redirect, get_object_or_404
import os, pyotp
from .forms import LoginForm, CustomerForm
from .models import Customer
from django.db.models import Q
from django.contrib import messages


# Login direkt zum Dashboard
def login_view(request):
    error = None
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            acc  = form.cleaned_data['account_number']
            pin  = form.cleaned_data['pin']
            code = form.cleaned_data['totp_code']

            ADMIN_ACC    = os.getenv('ADMIN_ACCOUNT_NUMBER')
            ADMIN_PIN    = os.getenv('ADMIN_PIN')
            ADMIN_SECRET = os.getenv('ADMIN_TOTP_SECRET')

            if acc == ADMIN_ACC and pin == ADMIN_PIN and pyotp.TOTP(ADMIN_SECRET).verify(code):
                # Session-Flag setzen
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

def require_admin(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('is_admin'):
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

# Admin Home
def admin_home(request):
    if not request.session.get('is_admin'): return redirect('login')
    return render(request, 'admin_home.html')

# Dashboard mit Button zur Kundenübersicht
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')

# Kundenübersicht
def customer_list(request):
    from django.db.models import Q
    q = request.GET.get('q','')
    qs = Customer.objects.all()
    if q:
        qs = qs.filter(
            Q(last_name__icontains=q) |
            Q(first_name__icontains=q) |
            Q(customer_number__icontains=q)
        )
    return render(request, 'customer_list.html', {'customers': qs, 'q': q})

# Kunde hinzufügen
def customer_create(request):
    if request.method=='POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('customer_list')
    else:
        form = CustomerForm()
    return render(request, 'customer_form.html', {'form': form, 'edit': False})

# Kunde bearbeiten (Edit)
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method=='POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('customer_detail', pk=pk)
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'customer_form.html', {'form': form, 'edit': True})

# Kundenprofil
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    return render(request, 'customer_detail.html', {'customer': customer})

# Kunde löschen
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    expected = f'kunde {customer.customer_number} löschen'
    if request.method=='POST':
        confirm = request.POST.get('confirm_input','').strip().lower()
        if confirm == expected:
            customer.delete()
            messages.success(request, 'Kunde gelöscht.')
            return redirect('customer_list')
        else:
            messages.error(request, f'Bitte genau "{expected}" eingeben.')
    return render(request, 'customer_confirm_delete.html', {
        'customer': customer,
        'expected': expected
    })

# Sicherheitsprüfung
def customer_security(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    result = None

    if request.method == 'POST':
        resp = request.POST.get('security_response','').strip()
        # Je nach Level prüfen
        if customer.security_level == 'pin':
            result = 'correct' if resp == customer.security_answer else 'incorrect'
        else:  # 'question'
            result = 'correct' if resp.lower() == customer.security_answer.lower() else 'incorrect'

    return render(request, 'customer_security.html', {
        'customer': customer,
        'result':   result
    })
