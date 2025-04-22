import requests
from django.conf import settings
from .exceptions import PaymentGatewayError

class MpesaGateway:
    def __init__(self, business):
        try:
            self.method = business.payment_methods.get(payment_type='mpesa')
        except PaymentMethod.DoesNotExist:
            raise InvalidPaymentMethod("M-Pesa payment method not configured")
        
        self.config = self.method.config
        
    def initiate_payment(self, phone, amount, reference):
        """Initiate M-Pesa STK push"""
        try:
            # Implementation would go here
            # This would call the M-Pesa API
            return {
                'status': 'pending',
                'checkout_request_id': 'SIMULATED_CHECKOUT_ID'
            }
        except Exception as e:
            raise PaymentGatewayError(f"M-Pesa error: {str(e)}")

class StripeGateway:
    def __init__(self, business):
        try:
            self.method = business.payment_methods.get(payment_type='stripe')
        except PaymentMethod.DoesNotExist:
            raise InvalidPaymentMethod("Stripe payment method not configured")
        
        self.config = self.method.config
        
    def create_payment_intent(self, amount, currency, metadata=None):
        """Create Stripe PaymentIntent"""
        try:
            # Simulated Stripe implementation
            # In real code, this would call Stripe API
            return {
                'client_secret': 'simulated_secret',
                'id': f"simulated_stripe_{metadata['order_id']}"
            }
        except Exception as e:
            raise PaymentGatewayError(f"Stripe error: {str(e)}")