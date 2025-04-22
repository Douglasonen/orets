from django.db import models
from core.models import business
from django.utils import timezone
from django.conf import settings
from products.models import Product



# app registration is pending creation

# orders/models.py
''' The ommited order class
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('shipped', 'Shipped')
    ]
    
    business = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    customer_whatsapp = models.CharField(max_length=20)
    negotiated_price = models.DecimalField(max_digits=10, decimal_places=2)
    products = models.ManyToManyField('products.Product')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)'''
###
class Order(models.Model):
    PENDING = 'pending'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (PROCESSING, 'Processing'),
        (COMPLETED, 'Completed'),
        (CANCELLED, 'Cancelled'),
    ]

    business = models.ForeignKey(business, on_delete=models.CASCADE, related_name='orders')
    customer_name = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=20)
    customer_address = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='KES')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now) 
    updated_at = models.DateTimeField(auto_now=True)
    
    business = models.ForeignKey(
        'core.business',  # String reference
        on_delete=models.CASCADE
    )
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Order #{self.id} - {self.customer_name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_name = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    @property
    def total(self):
        return self.quantity * self.price

    def __str__(self):
        return f"{self.quantity}x {self.product_name} for Order #{self.order.id}"