from django.conf import settings 
business = settings.AUTH_USER_MODEL
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from .models import business
import django.contrib.gis
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from products.models import Product

User = settings.AUTH_USER_MODEL
class business(AbstractUser):  # Changed from 'business' to 'Business'
    
    INDUSTRY_CHOICES = [
        ('retail', 'Retail'),
        ('manufacturing', 'Manufacturing'),
        ('agriculture', 'Agriculture'),
        ('technology', 'Technology'),
        ('healthcare', 'Healthcare'),
        ('fashion', 'Fashion'),
        ('food', 'Food & Beverage'),
        ('construction', 'Construction'),
        ('education', 'Education'),
        ('other', 'Other'),
    ]
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    whatsapp_number = models.CharField(max_length=20, unique=True)
    whatsapp_verified = models.BooleanField(default=False)
    whatsapp_bot_active = models.BooleanField(default=True)
    industry = models.CharField(max_length=50, choices=INDUSTRY_CHOICES)
    description = models.TextField()
    #############
    company_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    address = models.TextField(blank=True,
                               help_text='The small town in which you have a physical Store')
    town = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="The town or city where your business is located"
    )
    
    # Remove any existing location/coordinates fields if they exist
    # location = models.PointField()  # Remove this line
    
    def __str__(self):
        return f"{self.username} ({self.town})" if self.town else self.username
    is_verified = models.BooleanField(default=False)
  
    
    REQUIRED_FIELDS = ['company_name', 'phone_number']  # Add this
    @property
    def product_count(self):
        from products.models import Product
        return Product.objects.filter(business=self).count()
    class Meta:
        verbose_name_plural = "businesses"  # Capitalized
        db_table = 'core_business'

#####
class BusinessProfile(models.Model):
    # Existing fields (maintaining your original relationship and validation)
    business = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='business_logos/', blank=True)
    
    # New fields you want to add
    business_name = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    whatsapp_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    industry = models.CharField(max_length=50, blank=True)
    
    # Add any additional fields you need
    established_date = models.DateField(null=True, blank=True)
    tax_id = models.CharField(max_length=50, blank=True)
    social_media = models.URLField(blank=True, help_text="Link to main social media profile")
    products = models.ManyToManyField(Product, blank=True)
    def is_complete(self):
        """Efficient check for profile completion status"""
        return (bool(self.business_name) and 
                bool(self.description) and 
                len(self.description.strip()) >= 10 and
                bool(self.phone_number) and
                bool(self.email) 
                
                )
    # Your existing clean method with enhancement for new fields
    def clean(self):
        """Validation when saving"""
        
        super().clean()
        if self.is_complete():  # Only validate complete profiles
            if len(self.description.strip()) < 10:
                raise ValidationError("Description must be at least 10 characters")
            
            # Add validation for new fields if needed
            if self.business_name and len(self.business_name.strip()) < 2:
                raise ValidationError("Business name must be at least 2 characters")
            
            if self.phone_number and not self.phone_number.isdigit():
                raise ValidationError("Phone number must be digits")
    
                
    class Meta:
        db_table = 'core_business_profiles'
            
class ProductCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now) 
    updated_at = models.DateTimeField(auto_now=True)
    

    class Meta:
        ordering = ['name']
    class Meta:
        verbose_name_plural = "Product Categories"
        db_table = 'core_products_categories'
   

    def __str__(self):
        return self.name

class ChatHistory(models.Model):
    business_number = models.CharField(max_length=20)
    customer_number = models.CharField(max_length=20)
    message = models.TextField()
    sender = models.CharField(max_length=10)  # 'customer' or 'bot'
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['business_number', 'customer_number']),
        ]