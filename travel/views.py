from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from .models import TravelOption
from bookings.models import Booking
from .constants import INDIAN_CITIES, TRAVEL_TYPES


class TravelSearchView(ListView):
    """View to search and list travel options"""
    model = TravelOption
    template_name = 'travel/search.html'
    context_object_name = 'travel_options'
    paginate_by = 10

    def get_queryset(self):
        queryset = TravelOption.objects.filter(
            is_active=True,
            departure_datetime__gte=timezone.now(),
            available_seats__gt=0
        ).order_by('departure_datetime')
        
        # Apply filters
        source = self.request.GET.get('source')
        if source:
            queryset = queryset.filter(source=source)
        
        destination = self.request.GET.get('destination')
        if destination:
            queryset = queryset.filter(destination=destination)
        
        travel_type = self.request.GET.get('travel_type')
        if travel_type:
            queryset = queryset.filter(travel_type=travel_type)
        
        date = self.request.GET.get('date')
        if date:
            try:
                from datetime import datetime
                date_obj = datetime.strptime(date, '%Y-%m-%d').date()
                queryset = queryset.filter(departure_datetime__date=date_obj)
            except ValueError:
                pass
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cities'] = INDIAN_CITIES
        context['travel_types'] = TRAVEL_TYPES
        context['search_params'] = self.request.GET
        return context


class TravelDetailView(DetailView):
    """View to show travel option details"""
    model = TravelOption
    template_name = 'travel/detail.html'
    context_object_name = 'travel_option'


class BookTravelView(LoginRequiredMixin, DetailView):
    """View to book a travel option"""
    model = TravelOption
    template_name = 'travel/book.html'
    context_object_name = 'travel_option'

    def post(self, request, *args, **kwargs):
        travel_option = self.get_object()
        num_seats = int(request.POST.get('num_seats', 1))
        
        # Basic validation
        if num_seats <= 0 or num_seats > travel_option.available_seats:
            messages.error(request, 'Invalid number of seats requested.')
            return redirect('travel:detail', pk=travel_option.pk)
        
        try:
            # Create booking
            booking = Booking.objects.create(
                user=request.user,
                travel_option=travel_option,
                num_seats=num_seats,
                total_price=travel_option.price * num_seats,
                status='confirmed'
            )
            
            # Reduce available seats
            travel_option.available_seats -= num_seats
            travel_option.save()
            
            messages.success(
                request, 
                f'Booking confirmed! Your booking reference is {booking.booking_reference}'
            )
            return redirect('bookings:detail', pk=booking.pk)
            
        except Exception as e:
            messages.error(request, 'There was an error processing your booking. Please try again.')
            return redirect('travel:detail', pk=travel_option.pk)
