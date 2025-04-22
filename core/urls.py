from django.urls import path
from . import views
from .views import BusinessSignupView, business_profile, edit_profile, business_signup
from .views import register, activate
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from core.views import business, complete_profile
from core import views as core_view
app_name = 'core'  # This enables the core: namespace

urlpatterns = [
    path('', views.dashboard, name='dashboard'),  # Main dashboard at root URL
    path('core/profile/', edit_profile, name='edit_profile'),
    path('business_profile/', business_profile, name='business_profile'),
    path('profile/',business_profile, name='business_profile'),
    path('activate/<uidb64>/<token>/', activate, name='activate'),
    path('registration-sent/', TemplateView.as_view(template_name='registration/registration_sent.html'), name='registration_sent'),
    path('complete_profile/', core_view.complete_profile, name='complete_profile'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('bisiness_signup/', business_signup, name='business_signup'),
    path('products/', views.dashboard, name='dashboard'),
    path('register/', business_signup, name='business_signup'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('accounts/logout/', views.custom_logout, name='logout'),
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)