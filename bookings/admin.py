from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_reference', 'user', 'travel_option', 'num_seats', 
                   'total_price', 'status', 'booking_date')
    list_filter = ('status', 'booking_date', 'travel_option__travel_type')
    search_fields = ('booking_reference', 'user__username', 'user__email',
                    'contact_phone', 'contact_email')
    date_hierarchy = 'booking_date'
    ordering = ['-booking_date']
    readonly_fields = ('booking_reference', 'booking_date')
    
    fieldsets = (
        ('Booking Details', {
            'fields': ('booking_reference', 'user', 'travel_option', 'num_seats')
        }),
        ('Pricing', {
            'fields': ('total_price',)
        }),
        ('Contact Information', {
            'fields': ('contact_phone', 'contact_email')
        }),
        ('Status', {
            'fields': ('status', 'booking_date')
        }),
        ('Additional Information', {
            'fields': ('special_requests', 'passenger_details')
        }),
    )
