from django.shortcuts import render, redirect, get_object_or_404
import os, pyotp
from .forms import LoginForm, CustomerForm
from .models import Customer
from django.db.models import Q
from django.contrib import messages


# Login direkt zum Dashboard
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            acc = form.cleaned_data['account_number']
            pin = form.cleaned_data['pin']
            code = form.cleaned_data['totp_code']
            ADMIN_ACC = os.getenv('ADMIN_ACCOUNT_NUMBER')
            ADMIN_PIN = os.getenv('ADMIN_PIN')
            ADMIN_SECRET = os.getenv('ADMIN_TOTP_SECRET')
            if acc == ADMIN_ACC and pin == ADMIN_PIN and pyotp.TOTP(ADMIN_SECRET).verify(code):
                request.session['is_admin'] = True
                return redirect('admin_dashboard')
        error = 'Anmeldedaten ungültig.'
    else:
        form, error = LoginForm(), None
    return render(request, 'login.html', {'form': form, 'error': error})

# Admin Home
def admin_home(request):
    if not request.session.get('is_admin'): return redirect('login')
    return render(request, 'admin_home.html')

# Dashboard mit Button zur Kundenübersicht
def admin_dashboard(request):
    if not request.session.get('is_admin'): return redirect('login')
    return render(request, 'admin_dashboard.html')

# Kundenübersicht
def customer_list(request):
    if not request.session.get('is_admin'):
        return redirect('login')

    q = request.GET.get('q', '')
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

# Kunde hinzufügen
def customer_create(request):
    if not request.session.get('is_admin'): return redirect('login')
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('customer_list')
    else:
        form = CustomerForm()
    return render(request, 'customer_form.html', {'form': form})

# Kunde bearbeiten (Edit)
def customer_edit(request, pk):
    if not request.session.get('is_admin'): return redirect('login')
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('customer_detail', pk=customer.pk)
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'customer_form.html', {'form': form, 'edit': True})

# Kundenprofil
def customer_detail(request, pk):
    if not request.session.get('is_admin'):
        return redirect('login')
    customer = get_object_or_404(Customer, pk=pk)
    return render(request, 'customer_detail.html', {
        'customer': customer
    })
    

# Kunde löschen
def customer_delete(request, pk):
    if not request.session.get('is_admin'): return redirect('login')
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        customer.delete()
        return redirect('customer_list')
    return render(request, 'customer_confirm_delete.html', {'customer': customer})

# Sicherheitsprüfung
def customer_security(request, pk):
    if not request.session.get('is_admin'): return redirect('login')
    customer = get_object_or_404(Customer, pk=pk)
    correct = None
    if request.method == 'POST':
        answer = request.POST.get('security_answer')
        correct = (answer == customer.security_answer)
    return render(request, 'customer_security.html', {'customer': customer, 'correct': correct})
