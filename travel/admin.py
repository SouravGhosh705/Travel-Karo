from django.contrib import admin
from .models import TravelOption


@admin.register(TravelOption)
class TravelOptionAdmin(admin.ModelAdmin):
    list_display = ('travel_type', 'source', 'destination', 'departure_datetime', 
                   'price', 'available_seats', 'total_seats', 'is_active')
    list_filter = ('travel_type', 'source', 'destination', 'is_active')
    search_fields = ('source', 'destination', 'operator_name', 'service_number')
    date_hierarchy = 'departure_datetime'
    ordering = ['departure_datetime']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('travel_type', 'source', 'destination')
        }),
        ('Schedule', {
            'fields': ('departure_datetime', 'arrival_datetime')
        }),
        ('Pricing & Capacity', {
            'fields': ('price', 'total_seats', 'available_seats')
        }),
        ('Operator Details', {
            'fields': ('operator_name', 'service_number', 'description')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
