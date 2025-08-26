from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'phone', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'state', 'gender')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'phone')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Personal Info', {
            'fields': ('phone', 'date_of_birth', 'gender', 'address', 'city', 'state', 'pin_code', 'aadhaar_number')
        }),
    )
