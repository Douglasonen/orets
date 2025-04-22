from django.core.exceptions import ObjectDoesNotExist
from twilio.rest import Client
from django.conf import settings
from core.models import business, BusinessProfile
from openai import OpenAI
import logging
import re
from datetime import datetime
from products.models import Product
logger = logging.getLogger(__name__)

class WhatsAppHandler:
    def __init__(self):
        self.twilio_client = Client(settings.TWILIO_ACCOUNT_SID, 
                                  settings.TWILIO_AUTH_TOKEN)
        self.key = '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'
        self.openrouter_key = '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'
        self.chat_history = []
    def _normalize_phone_number(self, number):
        """Basic phone number normalization"""
        return re.sub(r'[^\d+]', '', str(number))

    def _find_business(self, whatsapp_number):
        """Find business with flexible number matching"""
        normalized = self._normalize_phone_number(whatsapp_number)
        
        # Try exact match first
        biz = business.objects.filter(whatsapp_number=normalized).first()
        if biz:
            return biz
            
        # Try without + prefix if present
        if normalized.startswith('+'):
            biz = business.objects.filter(whatsapp_number=normalized[1:]).first()
            if biz:
                return biz
                
        # Try last 10 digits
        if len(normalized) >= 10:
            last_10 = normalized[-10:]
            biz = business.objects.filter(whatsapp_number__endswith=last_10).first()
            if biz:
                return biz
                
        raise ObjectDoesNotExist(f"No business found for {whatsapp_number}")

    def create_rep(self, message, chat_history, business_context):
        
        try:
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key='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',
            )

            # Build a rich product listing with images (if available)
            products_text = ""
            for product in business_context.get('products_list', []):
                products_text += f"- {product['name']}: ${product['price']}"
                if product.get('image_url'):
                    products_text += f" [Image: {product['image_url']}]"
                products_text += "\n"

            prompt = (
                f"ROLE: You are a customer service assistant for {business_context['business_name']}.\n"
                f"CONTEXT: {business_context['context']}\n\n"
                f"PRODUCT CATALOG:\n{products_text}\n"
                f"ABOUT THE BUSINESS:\n{business_context.get('about', 'Not specified')}\n\n"
                f"CONVERSATION HISTORY:\n{chat_history}\n\n"
                f"CUSTOMER MESSAGE: {message}\n\n"
                "INSTRUCTIONS:\n"
                "1. Respond professionally and helpfully\n"
                "2. Mention product details (name, price) when relevant\n"
                "3. Include image URLs when available to enhance responses\n"
                "4. Keep responses concise but informative"
            )

            completion = client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": "<YOUR_SITE_URL>",
                    "X-Title": "<YOUR_SITE_NAME>",
                },
                model="deepseek/deepseek-chat-v3-0324:free",
                messages=[{"role": "user", "content": prompt}]
            )
            return completion.choices[0].message.content
        
        except Exception as e:
            print(f'An error occurred: {e}')
            return 'I beg your pardon, there was an error processing your request.'

    
    def _send_message(self, from_number, to_number, message):
        """Send message via Twilio"""
        try:
            response = self.twilio_client.messages.create(
                from_=f"whatsapp:{from_number}",
                body=message,
                to=f"whatsapp:{to_number}"
            )
            logger.info(f"Message sent to {to_number}")
            return True
        except Exception as e:
            logger.error(f"Failed to send message: {str(e)}")
            return False

    def _get_chat_history(self, business_number, customer_number):
        """Retrieve conversation history"""
        # Implement your chat history logic here
        return self.chat_history

    def _update_chat_history(self, business_number, customer_number, incoming_msg, outgoing_msg):
        """Store conversation in database"""
        chat = {'Business_number':business_number, 'customer_number':customer_number, 'incoming_msg':incoming_msg, 'outgoing_msg':outgoing_msg}
        self.chat_history.append(str(chat.values))
        

    ########## FETCH PRODUCTS ########################
    
    '''def _get_business_context(self, business_obj):
        """Fetch products and about info for a business"""
        try:
            # Get the business profile for description
            profile = business_obj.profile
            
            # Fetch products directly from products_product table
            from products.models import Product  # Import your Product model
            products = Product.objects.filter(business=business_obj)
            
            # Format products string
            products_str = "\n".join(
                f"{product.name} - {product.price}" 
                for product in products
            )
            
            return {
                'products': products_str,
                'about': profile.description,
                'context': (
                    f"You are a helpful assistant for {business_obj.company_name}. "
                    "Respond simply and clearly to customer inquiries about products. "
                    "Always include prices when mentioning products."
                )
            }
        except BusinessProfile.DoesNotExist:
            logger.warning(f"No profile found for {business_obj.company_name}")
            # Try to get products even if profile doesn't exist
            from products.models import Product
            products = Product.objects.filter(business=business_obj)
            products_str = "\n".join(f"{p.name} - {p.price}" for p in products)
            
            return {
                'products': products_str,
                'about': "",
                'context': f"You represent {business_obj.company_name}"
            }
        except Exception as e:
            logger.error(f"Error getting business context: {str(e)}")
            return {
                'products': "",
                'about': "",
                'context': f"You represent {business_obj.company_name}"
            }
        '''
        
    ################ new context fetcher #############
    def _get_business_context(self, business_obj):
        """Fetch products with auto-generated image URLs and format them for context."""
        try:
            products = Product.objects.filter(business=business_obj)
            
            products_list = []
            for product in products:
                products_list.append({
                    'name': product.name,
                    'price': product.price,
                    'image_url': product.image_url  # Uses the property
                })
            
            # Format products as text (for LLM context)
            products_text = "\n".join(
                f"{p['name']} - ${p['price']}" + (f" | Image: {p['image_url']}" if p['image_url'] else "")
                for p in products_list
            )
            
            return {
                'products': products_text,
                'products_list': products_list,  # Structured data (e.g., for APIs)
                'business_name': business_obj.company_name,
                'context': "Include product name, price, and image URL when responding."
            }
            
        except ObjectDoesNotExist:
            logger.warning(f"No products found for business: {business_obj.company_name}")
            return {
                'products': "",
                'products_list': [],
                'business_name': business_obj.company_name,
                'context': "No products available."
            }
        except Exception as e:
            logger.error(f"Error fetching business context: {str(e)}")
            return {
                'products': "",
                'products_list': [],
                'business_name': business_obj.company_name,
                'context': "Error loading products."
            }

    
    # ... (keep all other existing methods) ...

    def process_incoming(self, whatsapp_number, customer_number, message):
        try:
            logger.info(f"Processing message from {customer_number}")
            
            # 1. Find the business
            business_obj = self._find_business(whatsapp_number)
            logger.info(f"Found business: {business_obj.company_name}")
            
            # 2. Get business context (products, description)
            business_context = self._get_business_context(business_obj)
            logger.debug(f"Business context: {business_context}")
            
            # 3. Get chat history
            chat_history = self._get_chat_history(whatsapp_number, customer_number)
            
            # 4. Generate AI response
            response = self.create_rep(message, chat_history, business_context)
            
            # 5. Send response
            self._send_message(whatsapp_number, customer_number, response)
            
            # 6. Update chat history
            self._update_chat_history(whatsapp_number, customer_number, message, response)
            
        except ObjectDoesNotExist as e:
            logger.error(f"No business found: {str(e)}")
            self._send_message(
                whatsapp_number,
                customer_number,
                "Sorry, we couldn't find your business account. Please contact support."
            )
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}", exc_info=True)
            self._send_message(
                whatsapp_number,
                customer_number,
                "We're experiencing technical difficulties. Please try again later."
            )