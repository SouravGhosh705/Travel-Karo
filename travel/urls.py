from django.urls import path
from . import views

app_name = 'travel'

urlpatterns = [
    path('search/', views.TravelSearchView.as_view(), name='search'),
    path('<int:pk>/', views.TravelDetailView.as_view(), name='detail'),
    path('book/<int:pk>/', views.BookTravelView.as_view(), name='book'),
]
