from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import business, ProductCategory

@admin.register(business)
class BusinessAdmin(UserAdmin):
    list_display = ('username', 'company_name', 'email', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Business Info', {'fields': ('company_name', 'phone_number', 'address', 'is_verified')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Business Info', {'fields': ('company_name', 'phone_number', 'address', 'is_verified')}),
    )