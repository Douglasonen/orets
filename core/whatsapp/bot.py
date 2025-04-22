from openai import OpenAI
from django.conf import settings
from core.models import business
from products.models import Product
import logging
from openai import OpenAI
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class SalesBot:
    def __init__(self, business_id):
        self.business_id = business_id
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key='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',  # Your OpenRouter key
        )
        
        # Initialize with your existing product/context data
        self.products = "Bags - UGX70,000: https://... (your product list)"
        self.about = "(your about text)"
        self.context = "(your context instructions)"

    def generate_response(self, message, chat_history=""):
        try:
            completion = self.client.chat.completions.create(
                model="deepseek/deepseek-chat-v3-0324:free",  # Free model
                messages=[
                    {
                        "role": "system", 
                        "content": f"{self.context}\n\nProducts:\n{self.products}\n\nAbout Us:\n{self.about}"
                    },
                    {
                        "role": "user",
                        "content": f"{message}\n\nChat History:\n{chat_history}"
                    }
                ],
                extra_headers={
                    "HTTP-Referer": "https://yourbusiness.com",
                    "X-Title": "Your Business Name"
                }
            )
            return completion.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return "Thanks for your message! We'll get back to you shortly."
