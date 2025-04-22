from django.db import models
from django.conf import settings
from django.utils import timezone
Business = settings.AUTH_USER_MODEL

class WhatsAppMessage(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    customer_number = models.CharField(max_length=20)
    message_content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now) 
    direction = models.CharField(max_length=10, choices=[('IN', 'Incoming'), ('OUT', 'Outgoing')])
    status = models.CharField(max_length=20, default='received')
    
    def __str__(self):
        return f"{self.customer_number}: {self.message_content[:50]}"
