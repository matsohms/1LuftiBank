from django.urls import include, path

urlpatterns = [
    # Leitet alle Anfragen an die core-App weiter
    path('', include('core.urls')),
]
