class PaymentError(Exception):
    """Base payment exception"""
    pass

class PaymentGatewayError(PaymentError):
    """Errors from payment gateways"""
    pass

class InvalidPaymentMethod(PaymentError):
    """Invalid payment method selected"""
    pass