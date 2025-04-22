from django import forms
from django.contrib.auth import get_user_model
from .models import BusinessProfile
from .models import business
User = get_user_model()
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import BusinessProfile
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import business
import phonenumbers
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.password_validation import validate_password
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import business

class BusinessRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = business
        fields = ('username', 'email', 'password1', 'password2', 'company_name', 'phone_number', 'town')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if business.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already in use.")
        return email

######

class BusinessSignupForm(UserCreationForm):
    company_name = forms.CharField(
        required=True,
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Your Business Name'})
    )
    phone_number = forms.CharField(
        required=True,
        max_length=20,
        widget=forms.TextInput(attrs={'placeholder': '+256XXXXXXXXX'})
    )
    whatsapp_number = forms.CharField(
        required=True,
        max_length=20,
        widget=forms.TextInput(attrs={'placeholder': '+256XXXXXXXXX'})
    )
    industry = forms.ChoiceField(
        choices=business.INDUSTRY_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    address = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Physical address'}),
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'business@example.com'})
    )

    class Meta(UserCreationForm.Meta):
        model = business
        fields = UserCreationForm.Meta.fields + (
            'company_name',
            'phone_number',
            'whatsapp_number',
            'industry',
            'address',
            'email'
        )

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if phone:
            # Simple cleaning - remove all non-digit characters except +
            return ''.join(c for c in phone if c.isdigit() or c == '+')
        return phone

    def clean_whatsapp_number(self):
        whatsapp = self.cleaned_data.get('whatsapp_number')
        if whatsapp:
            # Ensure WhatsApp has + prefix
            cleaned = ''.join(c for c in whatsapp if c.isdigit() or c == '+')
            if not cleaned.startswith('+'):
                raise forms.ValidationError("Must include country code with + prefix")
            return cleaned
        return whatsapp




####
class BusinessProfileForm(forms.ModelForm):
    class Meta:
        model = BusinessProfile
        fields = [
            'business_name',
            'description',
            'logo',
            'address',
            'phone_number',
            'whatsapp_number',
            'email',
            'website',
            'industry'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'whatsapp_number': forms.TextInput(attrs={'placeholder': '+256XXXXXXXXX'}),
        }
    
    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if phone:
            # Remove all non-digit characters except leading +
            cleaned = ''.join(c for c in phone if c.isdigit() or c == '+')
            if not cleaned.replace('+', '').isdigit():
                raise forms.ValidationError("Phone number should contain only digits and optional + prefix")
            return cleaned
        return phone
    
    def clean_whatsapp_number(self):
        whatsapp = self.cleaned_data.get('whatsapp_number')
        if whatsapp:
            # Remove all non-digit characters except leading +
            cleaned = ''.join(c for c in whatsapp if c.isdigit() or c == '+')
            if not cleaned.startswith('+'):
                raise forms.ValidationError("WhatsApp number must include country code with + prefix (e.g. +256...)")
            if not cleaned[1:].isdigit():  # Check all characters after + are digits
                raise forms.ValidationError("WhatsApp number should contain only digits after + prefix")
            if len(cleaned) < 10:  # Minimum length check (including +)
                raise forms.ValidationError("WhatsApp number is too short")
            return cleaned
        return whatsapp
    ########## down ##################