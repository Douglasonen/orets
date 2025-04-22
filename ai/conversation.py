import openai
from django.conf import settings
from products.models import Product

class SalesConversation:
    def __init__(self, business, customer_number):
        self.business = business
        self.customer_number = customer_number
        self.conversation_history = []
        
    def generate_response(self, user_message):
        # Add user message to history
        self.conversation_history.append({"role": "user", "content": user_message})
        
        # Get business products
        products = Product.objects.filter(business=self.business)
        products_info = "\n".join([f"{p.name}: {p.description} (Price: {p.price})" for p in products])
        
        # Create system prompt
        system_prompt = f"""
        You are a sales assistant for {self.business.name}. Your role is to:
        - Answer customer questions about products
        - Recommend products based on customer needs
        - Guide customers through the purchasing process
        - Be friendly and professional
        
        Available products:
        {products_info}
        
        When showing products, format them clearly and include price.
        When customer is ready to buy, ask for their preferred payment method.
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            *self.conversation_history
        ]
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
        )
        
        ai_response = response.choices[0].message.content
        self.conversation_history.append({"role": "assistant", "content": ai_response})
        
        return ai_response