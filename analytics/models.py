from django.db import models
from django.db.models import Sum, Count
from core.models import business
from orders.models import Order
from whatsapp.models import WhatsAppMessage

class BusinessAnalytics(models.Model):
    business = models.OneToOneField(business, on_delete=models.CASCADE, related_name='analytics')
    total_customers = models.PositiveIntegerField(default=0)
    total_conversations = models.PositiveIntegerField(default=0)
    total_orders = models.PositiveIntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Business Analytics"

    def update_analytics(self):
        # Update order statistics
        orders = Order.objects.filter(business=self.business)
        self.total_orders = orders.count()
        self.total_revenue = orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        
        # Update conversation statistics
        conversations = WhatsAppMessage.objects.filter(business=self.business)
        self.total_conversations = conversations.count()
        self.total_customers = conversations.values('customer_number').distinct().count()
        self.save()

    def __str__(self):
        return f"Analytics for {self.business.business_name}"

class DailyMetric(models.Model):
    business = models.ForeignKey(business, on_delete=models.CASCADE, related_name='daily_metrics')
    date = models.DateField()
    messages_received = models.PositiveIntegerField(default=0)
    messages_sent = models.PositiveIntegerField(default=0)
    new_customers = models.PositiveIntegerField(default=0)
    orders_placed = models.PositiveIntegerField(default=0)
    revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        unique_together = ('business', 'date')
        ordering = ['-date']

    @classmethod
    def update_or_create_for_date(cls, business, date):
        # Get all messages for the date
        messages = WhatsAppMessage.objects.filter(
            business=business,
            timestamp__date=date
        )
        
        # Get all orders for the date
        orders = Order.objects.filter(
            business=business,
            created_at__date=date
        )
        
        # Calculate metrics
        metric, created = cls.objects.get_or_create(
            business=business,
            date=date
        )
        
        metric.messages_received = messages.filter(direction='IN').count()
        metric.messages_sent = messages.filter(direction='OUT').count()
        metric.orders_placed = orders.count()
        metric.revenue = orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        
        # Calculate new customers (first message date)
        metric.new_customers = messages.filter(
            direction='IN'
        ).values('customer_number').annotate(
            first_message=min('timestamp')
        ).filter(
            first_message__date=date
        ).count()
        
        metric.save()
        return metric

    def __str__(self):
        return f"Metrics for {self.business} on {self.date}"