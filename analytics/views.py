from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import BusinessAnalytics, DailyMetric
from datetime import datetime, timedelta
from django.utils import timezone
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def analytics_dashboard(request):
    return render(request, 'analytics/dashboard.html')
## Adds are above
@login_required
def dashboard(request):
    analytics, _ = BusinessAnalytics.objects.get_or_create(business=request.user)
    analytics.update_analytics()
    
    # Handle date filtering
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    
    if 'start_date' in request.GET:
        try:
            start_date = datetime.strptime(request.GET['start_date'], '%Y-%m-%d').date()
        except (ValueError, TypeError):
            pass
    
    if 'end_date' in request.GET:
        try:
            end_date = datetime.strptime(request.GET['end_date'], '%Y-%m-%d').date()
        except (ValueError, TypeError):
            pass
    
    daily_metrics = DailyMetric.objects.filter(
        business=request.user,
        date__range=[start_date, end_date]
    ).order_by('date')
    
    # Prepare data for charts
    dates = [metric.date.strftime('%Y-%m-%d') for metric in daily_metrics]
    messages_received = [metric.messages_received for metric in daily_metrics]
    messages_sent = [metric.messages_sent for metric in daily_metrics]
    orders_data = [metric.orders_placed for metric in daily_metrics]
    revenue_data = [float(metric.revenue) for metric in daily_metrics]
    
    context = {
        'analytics': analytics,
        'dates': dates,
        'messages_received': messages_received,
        'messages_sent': messages_sent,
        'orders_data': orders_data,
        'revenue_data': revenue_data,
        'currency': request.user.currency,
    }
    
    return render(request, 'analytics/dashboard.html', context)