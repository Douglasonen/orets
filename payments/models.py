from django.db import models
from orders.models import Order
from core.models import business
from django.utils import timezone


from django.db import models
from django.conf import settings

class PaymentMethod(models.Model):
    PAYMENT_TYPES = [
        ('credit_card', 'Credit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('mobile_money', 'Mobile Money'),
    ]
    
    business = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payment_methods'
    )
    payment_type = models.CharField(max_length=50, choices=PAYMENT_TYPES)
    account_number = models.CharField(max_length=50, blank=True)
    expiry_date = models.DateField(blank=True, null=True)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.CASCADE,
        null=True,  # Make nullable temporarily
        blank=True ) # Allow blank in forms)
    config = models.JSONField(
    blank=True,
    null=True,
    default=dict,
    help_text="Additional configuration for the payment method"
    )
    class Meta:
        db_table = 'payments_method'  # Matches our manual table
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.get_payment_type_display()} - {self.account_number}"
    
class Transaction(models.Model):
    PENDING = 'pending'
    COMPLETED = 'completed'
    FAILED = 'failed'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (COMPLETED, 'Completed'),
        (FAILED, 'Failed'),
    ]

    # String reference to avoid circular import
    order = models.ForeignKey('orders.Order', on_delete=models.PROTECT, related_name='transactions')
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='KES')
    transaction_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    gateway_response = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now) 
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['transaction_id']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.transaction_id} ({self.get_status_display()})"

