from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
from .models import WhatsAppMessage, Business
from ai.conversation import SalesConversation

@csrf_exempt
def whatsapp_webhook(request):
    if request.method == 'GET':
        # WhatsApp verification challenge
        return HttpResponse(request.GET.get('hub.challenge'))
    
    elif request.method == 'POST':
        data = json.loads(request.body)
        
        # Process incoming message
        entry = data['entry'][0]
        changes = entry['changes'][0]
        value = changes['value']
        
        if 'messages' in value:
            message = value['messages'][0]
            customer_number = message['from']
            message_content = message['text']['body']
            business_number_id = value['metadata']['phone_number_id']
            
            # Save incoming message
            whatsapp_message = WhatsAppMessage.objects.create(
                business=Business.objects.get(whatsapp_number_id=business_number_id),
                customer_number=customer_number,
                message_content=message_content,
                direction='IN'
            )
            
            # Initialize conversation
            conversation = SalesConversation(whatsapp_message.business, customer_number)
            ai_response = conversation.generate_response(message_content)
            
            # Send response back via WhatsApp
            send_whatsapp_message(business_number_id, customer_number, ai_response)
            
            # Save outgoing message
            WhatsAppMessage.objects.create(
                business=whatsapp_message.business,
                customer_number=customer_number,
                message_content=ai_response,
                direction='OUT'
            )
            
        return JsonResponse({'status': 'success'})

