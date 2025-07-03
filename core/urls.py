from django.urls import path
from .views import login_view, admin_dashboard

urlpatterns = [
    # Root und /login/ zeigen das Login-Formular
    path('',      login_view,      name='login'),
    path('login/', login_view),

    # Dashboard nur nach Login
    path('admin-dashboard/', admin_dashboard, name='admin-dashboard'),
]
