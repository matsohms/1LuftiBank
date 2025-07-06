from django.urls import path
from .views import (
    login_view, logout_view,
    admin_dashboard, customer_list,
    customer_create, customer_detail,
    customer_edit, customer_delete,
    customer_security,
)

urlpatterns = [
    # Login- und Logout
    path('', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    # Admin-Dashboard
    path('admin/dashboard/', admin_dashboard, name='admin_dashboard'),

    # CRUD für Kunden
    path('admin/customers/', customer_list, name='customer_list'),
    path('admin/customers/create/', customer_create, name='customer_create'),
    path('admin/customers/<int:pk>/', customer_detail, name='customer_detail'),
    path('admin/customers/<int:pk>/edit/', customer_edit, name='customer_edit'),
    path('admin/customers/<int:pk>/delete/', customer_delete, name='customer_delete'),

    # Konto-Erstellung (3 Schritte)
    path('admin/customers/<int:customer_pk>/accounts/add/step1/',
         account_create_step1, name='account_create_step1'),
    path('admin/customers/<int:customer_pk>/accounts/add/step2/',
         account_create_step2, name='account_create_step2'),
    path('admin/customers/<int:customer_pk>/accounts/add/step3/',
         account_create_step3, name='account_create_step3'),

    # Sicherheitsprüfung
    path('admin/customers/<int:pk>/security/', customer_security, name='customer_security'),
]
