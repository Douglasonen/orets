"""
URL configuration for orets project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings 
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.contrib import admin
from core.views import business_profile, dashboard, business_signup
from django.urls import path, include
from core.views import home  # Add this import
#from django.contrib.auth import views as auth_views
from django.contrib import admin
from django.urls import path, include
from core import views
from payments import views as pay_views
from products import views as ve
from core.whatsapp import webhooks

urlpatterns = [
    path('admin/', admin.site.urls),
    path('core/', include('core.urls')),
      # or whatever your app name is  # Core URLs at root
    path('payments/', include('payments.urls')),
    path('analytics/', include('analytics.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('products/', include('products.urls')),
    path('', home, name='home'),
     path('dashboard/', views.dashboard, name='dashboard'),
    path('complete_profile/', views.complete_profile, name='complete_profile'),
    path('business_profile/', business_profile, name='business_profile'),
    path('business_dashboard', dashboard, name='business_dashboard' ),
    path('profile/',business_profile, name='business_profile'),
    path('register/', views.register, name='register'),  # This was missing
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('products/add/', ve.add_product, name='add_product'),
    path('profile/', business_profile, name='business_profile'),
    path('edit_product', ve.edit_product, name='edit_product'), 
    path('whatsapp/webhook/', webhooks.twilio_webhook, name='whatsapp_webhook'),
    path('accounts/logout/', views.custom_logout, name='logout'),
    path('bisiness_signup/', business_signup, name='business_signup'),
     path('payment_methods/', pay_views.payment_methods, name='payment_methods'),
    #subscription_expiry
    
    
    
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 