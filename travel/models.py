from django.db import models
from django.core.validators import MinValueValidator
from django.urls import reverse
from .constants import INDIAN_CITIES, TRAVEL_TYPES


class TravelOption(models.Model):
    """
    Model representing a travel option (Flight, Train, or Bus)
    with Indian routes and pricing in Rupees
    """
    
    travel_type = models.CharField(
        max_length=10,
        choices=TRAVEL_TYPES,
        help_text='Type of travel (Flight, Train, Bus)'
    )
    
    source = models.CharField(
        max_length=100,
        choices=INDIAN_CITIES,
        help_text='Departure city'
    )
    
    destination = models.CharField(
        max_length=100,
        choices=INDIAN_CITIES,
        help_text='Arrival city'
    )
    
    departure_datetime = models.DateTimeField(
        help_text='Departure date and time'
    )
    
    arrival_datetime = models.DateTimeField(
        help_text='Arrival date and time',
        null=True,
        blank=True
    )
    
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text='Price in Indian Rupees (₹)'
    )
    
    total_seats = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text='Total number of seats available'
    )
    
    available_seats = models.PositiveIntegerField(
        validators=[MinValueValidator(0)],
        help_text='Number of seats currently available'
    )
    
    # Additional details
    operator_name = models.CharField(
        max_length=100,
        help_text='Name of the airline, railway, or bus operator',
        blank=True
    )
    
    service_number = models.CharField(
        max_length=50,
        help_text='Flight number, train number, or bus service number',
        blank=True
    )
    
    description = models.TextField(
        blank=True,
        help_text='Additional details about the service'
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text='Whether this travel option is currently bookable'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Travel Option'
        verbose_name_plural = 'Travel Options'
        ordering = ['departure_datetime']
        indexes = [
            models.Index(fields=['source', 'destination']),
            models.Index(fields=['departure_datetime']),
            models.Index(fields=['travel_type']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.get_travel_type_display()} from {self.source} to {self.destination} on {self.departure_datetime.strftime('%d/%m/%Y %H:%M')}"

    def get_absolute_url(self):
        return reverse('travel:detail', kwargs={'pk': self.pk})

    def get_formatted_price(self):
        """Return price formatted with rupee symbol and commas"""
        return f"₹{self.price:,.2f}"

    def get_duration(self):
        """Calculate and return travel duration if arrival time is set"""
        if self.arrival_datetime:
            duration = self.arrival_datetime - self.departure_datetime
            hours, remainder = divmod(duration.total_seconds(), 3600)
            minutes, _ = divmod(remainder, 60)
            return f"{int(hours)}h {int(minutes)}m"
        return "Duration not available"

    def is_available(self):
        """Check if seats are available for booking"""
        return self.is_active and self.available_seats > 0

    def get_occupancy_percentage(self):
        """Calculate occupancy percentage"""
        if self.total_seats > 0:
            occupied = self.total_seats - self.available_seats
            return round((occupied / self.total_seats) * 100, 1)
        return 0

    def clean(self):
        """Custom validation"""
        from django.core.exceptions import ValidationError
        
        # Ensure source and destination are different
        if self.source == self.destination:
            raise ValidationError('Source and destination cannot be the same.')
        
        # Ensure available seats don't exceed total seats
        if self.available_seats > self.total_seats:
            raise ValidationError('Available seats cannot exceed total seats.')
        
        # Ensure arrival time is after departure time
        if self.arrival_datetime and self.arrival_datetime <= self.departure_datetime:
            raise ValidationError('Arrival time must be after departure time.')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
