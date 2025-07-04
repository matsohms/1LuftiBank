from django.shortcuts import render, redirect, get_object_or_404
import os, pyotp
from .forms import LoginForm, CustomerForm
from .models import Customer

# Login direkt zum Dashboard
def login_view(request):
    if request.method=='POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            acc, pin, code = (form.cleaned_data[f] for f in ['account_number','pin','totp_code'])
            ADMIN_ACC = os.getenv('ADMIN_ACCOUNT_NUMBER')
            ADMIN_PIN = os.getenv('ADMIN_PIN')
            ADMIN_SECRET = os.getenv('ADMIN_TOTP_SECRET')
            if acc==ADMIN_ACC and pin==ADMIN_PIN and pyotp.TOTP(ADMIN_SECRET).verify(code):
                request.session['is_admin']=True
                return redirect('admin_dashboard')
        error='Anmeldedaten ungültig.'
    else:
        form, error = LoginForm(), None
    return render(request,'login.html',{'form':form,'error':error})

# Admin Home unverändert
def admin_home(request):
    if not request.session.get('is_admin'): return redirect('login')
    return render(request,'admin_home.html')

# Dashboard mit Button zur Kundenübersicht
def admin_dashboard(request):
    if not request.session.get('is_admin'): return redirect('login')
    return render(request,'admin_dashboard.html')

# Liste mit alternierenden Farben
def customer_list(request):
    if not request.session.get('is_admin'): return redirect('login')
    customers = Customer.objects.all()
    return render(request,'customer_list.html',{'customers':customers})

# Erstellung mit zweispaltigem Layout
def customer_create(request):
    if not request.session.get('is_admin'): return redirect('login')
    if request.method=='POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('customer_list')
    else:
        form = CustomerForm()
    return render(request,'customer_form.html',{'form':form})

# Detail mit Links und Keine Abfrage, wenn none
def customer_detail(request,pk):
    if not request.session.get('is_admin'): return redirect('login')
    cust=get_object_or_404(Customer,pk=pk)
    return render(request,'customer_detail.html',{'customer':cust})

# Delete mit dunklem Button
def customer_delete(request,pk):
    if not request.session.get('is_admin'): return redirect('login')
    cust=get_object_or_404(Customer,pk=pk)
    if request.method=='POST':
        cust.delete()
        return redirect('customer_list')
    return render(request,'customer_confirm_delete.html',{'customer':cust})

# Sicherheitsprüfung nur wenn aktiv
def customer_security(request,pk):
    if not request.session.get('is_admin'): return redirect('login')
    cust=get_object_or_404(Customer,pk=pk)
    correct=None
    if request.method=='POST':
        ans=request.POST.get('security_answer')
        correct=(ans==cust.security_answer)
    return render(request,'customer_security.html',{'customer':cust,'correct':correct})
