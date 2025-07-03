from django.urls import path
from .views import login_view, admin_dashboard

urlpatterns = [
    path('', login_view, name='login'),
    path('login/', login_view),
    path('admin-dashboard/', admin_dashboard, name='admin-dashboard'),
]
