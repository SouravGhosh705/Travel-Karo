from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils import timezone
from .models import Booking


class MyBookingsView(LoginRequiredMixin, ListView):
    """View to display user's bookings"""
    template_name = 'bookings/my_bookings.html'
    context_object_name = 'bookings'
    paginate_by = 10

    def get_queryset(self):
        return Booking.objects.filter(
            user=self.request.user
        ).order_by('-booking_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Separate upcoming and past bookings
        now = timezone.now()
        all_bookings = self.get_queryset()
        
        context['upcoming_bookings'] = all_bookings.filter(
            travel_option__departure_datetime__gte=now,
            status='confirmed'
        )
        context['past_bookings'] = all_bookings.filter(
            travel_option__departure_datetime__lt=now
        )
        context['cancelled_bookings'] = all_bookings.filter(
            status='cancelled'
        )
        
        return context


class BookingDetailView(LoginRequiredMixin, DetailView):
    """View to show booking details"""
    model = Booking
    template_name = 'bookings/detail.html'
    context_object_name = 'booking'

    def get_queryset(self):
        # Ensure users can only see their own bookings
        return Booking.objects.filter(user=self.request.user)


class CancelBookingView(LoginRequiredMixin, View):
    """View to cancel a booking"""
    
    def post(self, request, pk):
        booking = get_object_or_404(
            Booking, 
            pk=pk, 
            user=request.user
        )
        
        try:
            booking.cancel_booking()
            messages.success(
                request, 
                f'Booking {booking.booking_reference} has been cancelled successfully.'
            )
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, 'There was an error cancelling your booking. Please try again.')
        
        return redirect('bookings:detail', pk=booking.pk)
