from django.shortcuts import render, redirect
from django.http import HttpResponse
import os, pyotp
from .forms import LoginForm

# Login-View ohne DB
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

            if acc != ADMIN_ACC or pin != ADMIN_PIN:
                error = 'Kontonummer oder PIN falsch.'
            else:
                totp = pyotp.TOTP(ADMIN_SECRET)
                if not totp.verify(code):
                    error = 'Falscher TOTP-Code.'
                else:
                    request.session['is_admin'] = True
                    return redirect('admin-dashboard')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form, 'error': error})

# Admin-Dashboard

def admin_dashboard(request):
    if not request.session.get('is_admin'):
        return redirect('login')
    customers = []  # später mit echten Daten
    return render(request, 'admin_dashboard.html', {'customers': customers})

# Admin-Startseite (neue URL '/admin/')
def admin_home(request):
    # Zugriff nur für eingeloggte Admins
    if not request.session.get('is_admin'):
        return redirect('login')
    # Einfache Übersichtsseite
    return render(request, 'admin_home.html')
