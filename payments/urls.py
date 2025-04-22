from django.urls import path
from .views import payment_methods, initiate_payment, payment_webhook
from django.urls import path
from django.urls import path
from . import views
from .views import PaymentMethodListView
from .views import (
    payment_methods, 
    add_payment_method, 
    edit_payment_method,
    toggle_payment_method,
    payment_checkout
)
from django.urls import path
from . import views

app_name = 'payments'  # This registers the namespace



urlpatterns = [
    
    path('methods/', views.PaymentMethodListView.as_view(), name='payment_methods'),
    path('add_pyment_method/', views.add_payment_method, name='add_payment_method'),
    path('methods/<int:pk>/edit/', views.edit_payment_method, name='edit_payment_method'),
    path('methods/<int:pk>/delete/', views.delete_payment_method, name='delete_payment_method'),
    path('methods/<int:pk>/toggle/', views.toggle_payment_method, name='toggle_payment_method'),
    path('transactions/', views.transactions, name='transactions'),
    path('checkout/<int:order_id>/', views.payment_checkout, name='payment_checkout'),
    path('initiate/', views.initiate_payment, name='initiate_payment'),
    path('webhook/<str:gateway>/', views.payment_webhook, name='payment_webhook'),
    path('add_payment_method/', views.add_payment_method, name='add_method'),
    path('methods/', PaymentMethodListView.as_view(), name='methods'),
    path('transactions/', views.Transaction, name='transactions'),
    path('payment_methods/', views.payment_methods, name='payment_methods'),
    
    
]
    

