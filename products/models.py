from django.db import models
from core.models import business
from django.urls import reverse
from django.core.files.storage import default_storage
from django.conf import settings 
from urllib.parse import urljoin
import urllib
import os
class Category(models.Model):
    business = models.ForeignKey(
        business, 
        on_delete=models.CASCADE,
        related_name='categories'
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
        unique_together = ('business', 'name')  # Prevent duplicate names per business

    def __str__(self):
        return f"{self.name} ({self.business.company_name})"
    
class Product(models.Model):
    business = models.ForeignKey(business, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    categories = models.ManyToManyField(Category, through='ProductCategoryMapping')

    @property
    def image_url(self):
       
        if not self.image:
            return None

        # 1. Get the absolute filesystem path (e.g., 'C:\path\to\media\products\image.png')
        absolute_path = os.path.abspath(self.image.path)

        # 2. Convert to URL-encoded file:// path (replaces spaces with %20, etc.)
        file_url = urllib.parse.urljoin('file:', urllib.request.pathname2url(absolute_path))

        return file_url
    def _get_request(self):
        
        """Helper method to fetch the current request object from thread-local storage."""
        from django.conf import settings
        if hasattr(settings, 'THREAD_LOCAL_REQUEST'):
            return settings.THREAD_LOCAL_REQUEST
        return None

    class Meta:
        db_table = 'products_product'

class ProductCategoryMapping(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='category_mappings')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='product_mappings')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'products_product_categories'
        unique_together = (('product', 'category'),)