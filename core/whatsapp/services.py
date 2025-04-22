from twilio.rest import Client
from django.conf import settings
from core.models import business
import re
import logging

logger = logging.getLogger(__name__)

def normalize_phone_number(number):
    """Standardize phone number format for storage"""
    # Remove all non-digit characters
    digits = re.sub(r'[^\d]', '', number)
    
    # Ensure international format
    if not digits.startswith('1') and len(digits) == 10:  # US numbers
        return f"+1{digits}"
    elif len(digits) == 12 and digits.startswith('256'):  # Uganda numbers
        return f"+{digits}"
    return f"+{digits}"

def register_whatsapp_number(business_id):
    try:
        biz = business.objects.get(id=business_id)
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        normalized = normalize_phone_number(biz.whatsapp_number)
        
        # Update DB with normalized number
        if biz.whatsapp_number != normalized:
            biz.whatsapp_number = normalized
            biz.save()
        
        # Register with Twilio
        client.incoming_phone_numbers.create(
            phone_number=normalized,
            sms_url=f"{settings.BASE_URL}/whatsapp/webhook/",
            whatsapp=True
        )
        
        biz.whatsapp_verified = True
        biz.save()
        
        logger.info(f"Successfully registered {normalized} for {biz.company_name}")
        return True
    except Exception as e:
        logger.error(f"Registration failed: {str(e)}")
        return False