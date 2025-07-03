from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
import os
import pyotp
from .forms import LoginForm, CustomerForm
from .models import Customer


def login_view(request):
    error = None
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            acc = form.cleaned_data['account_number']
            pin = form.cleaned_data['pin']
            code = form.cleaned_data['totp_code']

            admin_acc = os.getenv('ADMIN_ACCOUNT_NUMBER')
            admin_pin = os.getenv('ADMIN_PIN')
            admin_secret = os.getenv('ADMIN_TOTP_SECRET')

            if acc != admin_acc or pin != admin_pin:
                error = 'Kontonummer oder PIN falsch.'
            else:
                totp = pyotp.TOTP(admin_secret)
                if not totp.verify(code):
                    error = 'Falscher TOTP-Code.'
                else:
                    request.session['is_admin'] = True
                    return redirect('admin_home')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form, 'error': error})


def admin_home(request):
    if not request.session.get('is_admin'):
        return redirect('login')
    return render(request, 'admin_home.html')


def admin_dashboard(request):
    if not request.session.get('is_admin'):
        return redirect('login')
    return render(request, 'admin_dashboard.html')


def customer_list(request):
    if not request.session.get('is_admin'):
        return redirect('login')
    customers = Customer.objects.all()
    return render(request, 'customer_list.html', {'customers': customers})


def customer_create(request):
    if not request.session.get('is_admin'):
        return redirect('login')
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('customer_list')
    else:
        form = CustomerForm()
    return render(request, 'customer_form.html', {'form': form})


def customer_detail(request, pk):
    if not request.session.get('is_admin'):
        return redirect('login')
    customer = get_object_or_404(Customer, pk=pk)
    return render(request, 'customer_detail.html', {'customer': customer})
