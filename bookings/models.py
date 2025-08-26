from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import transaction
from travel.models import TravelOption
from travel.constants import BOOKING_STATUS_CHOICES

User = get_user_model()


class Booking(models.Model):
    """
    Model representing a travel booking made by a user
    """
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bookings',
        help_text='User who made the booking'
    )
    
    travel_option = models.ForeignKey(
        TravelOption,
        on_delete=models.CASCADE,
        related_name='bookings',
        help_text='Travel option being booked'
    )
    
    num_seats = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text='Number of seats booked'
    )
    
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Total price in Indian Rupees (₹)'
    )
    
    booking_date = models.DateTimeField(
        auto_now_add=True,
        help_text='Date and time when booking was made'
    )
    
    status = models.CharField(
        max_length=20,
        choices=BOOKING_STATUS_CHOICES,
        default='confirmed',
        help_text='Current status of the booking'
    )
    
    # Passenger details (basic for now, can be extended)
    passenger_details = models.JSONField(
        default=dict,
        blank=True,
        help_text='Additional passenger details in JSON format'
    )
    
    # Booking reference number
    booking_reference = models.CharField(
        max_length=20,
        unique=True,
        help_text='Unique booking reference number'
    )
    
    # Contact details
    contact_phone = models.CharField(
        max_length=15,
        help_text='Contact phone number for this booking'
    )
    
    contact_email = models.EmailField(
        help_text='Contact email for this booking'
    )
    
    # Special requests or notes
    special_requests = models.TextField(
        blank=True,
        help_text='Any special requests or notes for this booking'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'
        ordering = ['-booking_date']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['booking_reference']),
            models.Index(fields=['booking_date']),
        ]

    def __str__(self):
        return f"Booking {self.booking_reference} - {self.user.get_full_name()} - {self.travel_option.source} to {self.travel_option.destination}"

    def get_formatted_total_price(self):
        """Return total price formatted with rupee symbol and commas"""
        return f"₹{self.total_price:,.2f}"

    def get_per_seat_price(self):
        """Calculate price per seat"""
        if self.num_seats > 0:
            return self.total_price / self.num_seats
        return 0

    def get_formatted_per_seat_price(self):
        """Return per seat price formatted with rupee symbol"""
        per_seat = self.get_per_seat_price()
        return f"₹{per_seat:,.2f}"

    def can_be_cancelled(self):
        """Check if booking can be cancelled"""
        from django.utils import timezone
        
        # Can't cancel if already cancelled
        if self.status == 'cancelled':
            return False
        
        # Can't cancel if travel date has passed
        if self.travel_option.departure_datetime <= timezone.now():
            return False
        
        # Can cancel if it's at least 2 hours before departure
        time_until_departure = self.travel_option.departure_datetime - timezone.now()
        return time_until_departure.total_seconds() >= 7200  # 2 hours

    def cancel_booking(self):
        """Cancel the booking and restore seats"""
        if not self.can_be_cancelled():
            raise ValueError("This booking cannot be cancelled")
        
        with transaction.atomic():
            # Update booking status
            self.status = 'cancelled'
            self.save()
            
            # Restore seats to travel option
            self.travel_option.available_seats += self.num_seats
            self.travel_option.save()

    def save(self, *args, **kwargs):
        # Generate booking reference if not exists
        if not self.booking_reference:
            import uuid
            import time
            # Create a reference with timestamp and random chars
            timestamp = str(int(time.time()))[-6:]
            unique_id = str(uuid.uuid4()).replace('-', '')[:6].upper()
            self.booking_reference = f"TB{timestamp}{unique_id}"
        
        # Set contact details from user if not provided
        if not self.contact_phone and self.user.phone:
            self.contact_phone = self.user.phone
        if not self.contact_email and self.user.email:
            self.contact_email = self.user.email
        
        # Calculate total price if not set
        if not self.total_price:
            self.total_price = self.travel_option.price * self.num_seats
        
        super().save(*args, **kwargs)

    def clean(self):
        """Custom validation"""
        from django.core.exceptions import ValidationError
        
        # Ensure num_seats doesn't exceed available seats
        if self.travel_option and self.num_seats > self.travel_option.available_seats:
            raise ValidationError(f'Only {self.travel_option.available_seats} seats are available.')
        
        # Ensure booking is for future travel
        from django.utils import timezone
        if self.travel_option and self.travel_option.departure_datetime <= timezone.now():
            raise ValidationError('Cannot book travel for past dates.')
