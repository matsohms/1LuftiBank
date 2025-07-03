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

            # Admin-Daten aus ENV
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
                    return redirect('admin-dashboard')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form, 'error': error})

# Einfaches Admin-Dashboard
def admin_dashboard(request):
    return HttpResponse('<h1>Admin-Dashboard</h1><p>Erfolgreich eingeloggt!</p>')
