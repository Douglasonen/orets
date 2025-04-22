from django.urls import path
from .views import dashboard
from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.analytics_dashboard, name='dashboard'),
    path('dashboard/', dashboard, name='analytics_dashboard'),
]