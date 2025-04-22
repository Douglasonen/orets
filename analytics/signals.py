from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import BusinessAnalytics, DailyMetric
from whatsapp.models import WhatsAppMessage
from orders.models import Order
from django.utils import timezone

@receiver(post_save, sender=WhatsAppMessage)
def update_analytics_on_message(sender, instance, created, **kwargs):
    if created:
        # Update main analytics
        analytics, _ = BusinessAnalytics.objects.get_or_create(business=instance.business)
        analytics.update_analytics()
        
        # Update daily metrics
        DailyMetric.update_or_create_for_date(
            business=instance.business,
            date=instance.timestamp.date()
        )

@receiver(post_save, sender=Order)
def update_analytics_on_order(sender, instance, created, **kwargs):
    if created:
        # Update main analytics
        analytics, _ = BusinessAnalytics.objects.get_or_create(business=instance.business)
        analytics.update_analytics()
        
        # Update daily metrics
        DailyMetric.update_or_create_for_date(
            business=instance.business,
            date=instance.created_at.date()
        )