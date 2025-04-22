# ai/agents.py
import openai

class SalesAgent:
    PROMPT_TEMPLATE = """
    You're a sales assistant for {business_name} that sells {product_details}.
    Current customer message: {message}
    Available products: {products}
    """
    
    def generate_response(self, business, message):
        prompt = self.PROMPT_TEMPLATE.format(
            business_name=business.company_name,
            product_details=business.description,
            message=message,
            products=list(business.products.all().values())
        )
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content