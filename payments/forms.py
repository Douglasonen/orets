from django import forms
from .models import PaymentMethod
from django import forms
from .models import PaymentMethod

class PaymentMethodForm(forms.ModelForm):
    class Meta:
        model = PaymentMethod
        fields = ['payment_type', 'is_active', 'config']
    
    def __init__(self, *args, **kwargs):
        self.business = kwargs.pop('business')
        super().__init__(*args, **kwargs)
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.business = self.business
        if commit:
            instance.save()
        return instance
''' BElow is the old code ----
class PaymentMethodForm(forms.ModelForm):
    class Meta:
        model = PaymentMethod
        fields = ['payment_type', 'is_active']
        
    def __init__(self, *args, **kwargs):
        self.business = kwargs.pop('business')
        super().__init__(*args, **kwargs)
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.business = self.business
        
        # Handle gateway-specific config
        payment_type = self.cleaned_data['payment_type']
        if payment_type == PaymentMethod.BUSINESS_MPESA:
            instance.config = {
                'business_code': self.data.get('mpesa_business_code'),
                'passkey': self.data.get('mpesa_passkey')
            }
        elif payment_type == PaymentMethod.BUSINESS_STRIPE:
            instance.config = {
                'secret_key': self.data.get('stripe_secret_key'),
                'public_key': self.data.get('stripe_public_key')
            }
        
        if commit:
            instance.save()
        return instance '''