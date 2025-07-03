from django.urls import path
from .views import (
    login_view, admin_home, admin_dashboard,
    customer_list, customer_create, customer_detail
)
urlpatterns = [
    path('',              login_view,       name='login'),
    path('login/',        login_view),
    path('admin/',        admin_home,       name='admin_home'),
    path('admin/dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin/customers/', customer_list,   name='customer_list'),
    path('admin/customers/add/', customer_create, name='customer_create'),
    path('admin/customers/<int:pk>/', customer_detail, name='customer_detail'),
]
