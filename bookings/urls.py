from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('my-bookings/', views.MyBookingsView.as_view(), name='my_bookings'),
    path('<int:pk>/', views.BookingDetailView.as_view(), name='detail'),
    path('<int:pk>/cancel/', views.CancelBookingView.as_view(), name='cancel'),
]
