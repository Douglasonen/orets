from django.urls import path
from . import views # Make sure to import the view
from .views import dashboard
from django.conf import settings
from django.conf.urls.static import static



app_name = 'products'


urlpatterns = [

    path('dashboard/', views.dashboard, name='dashboard'),
    path('add_product/', views.add_product, name='add_product'),
    path('add_category/', views.add_category, name='add_category'),
    path('', views.dashboard, name='dashboard'),
    path('add/', views.add_product, name='add_product'),
  
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)