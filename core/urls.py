from django.urls import path
from .views import (
    login_view, admin_home, admin_dashboard,
    customer_list, customer_create, customer_detail,
    customer_delete, customer_security
)
urlpatterns = [
    path('', login_view, name='login'),
    path('admin/', admin_home, name='admin_home'),
    path('admin/dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin/customers/', customer_list, name='customer_list'),
    path('admin/customers/add/', customer_create, name='customer_create'),
    path('admin/customers/<int:pk>/', customer_detail, name='customer_detail'),
    path('admin/customers/<int:pk>/delete/', customer_delete, name='customer_delete'),
    path('admin/customers/<int:pk>/security/', customer_security, name='customer_security'),
]
