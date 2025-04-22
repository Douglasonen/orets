from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import logging
from .handlers import WhatsAppHandler

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["GET", "POST"])
def twilio_webhook(request):
    if request.method == 'GET':
        return JsonResponse({'status': 'ok'})
    
    elif request.method == 'POST':
        try:
            business_number = request.POST.get('To', '').replace('whatsapp:', '')
            customer_number = request.POST.get('From', '').replace('whatsapp:', '')
            message = request.POST.get('Body', '').strip()
            
            logger.info(f"Received message - Business: {business_number}, Customer: {customer_number}, Message: '{message}'")
            
            handler = WhatsAppHandler()
            
            handler.process_incoming(business_number, customer_number, message)
            
            return HttpResponse(status=200)
        except Exception as e:
            logger.error(f"Webhook error: {str(e)}", exc_info=True)
            return HttpResponse(status=500)
    
    return HttpResponse(status=405)