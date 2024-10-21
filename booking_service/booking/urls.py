from django.urls import path
from .views import create_booking, get_booking_list, get_booking_detail, get_bookings, search_with_fields, register

urlpatterns = [
    path('register/', register, name='register'),
    path('bookings/', get_booking_list, name='booking-list'),  # For listing bookings
    path('bookings/create/', create_booking, name='booking-create'),  # For creating a booking
    path('bookings/<str:booking_id>/', get_booking_detail, name='booking-detail'),  # For retrieving a specific booking
    path('get-bookings/<str:trip_id>/', get_bookings, name='get_bookings'),
    path('booking-search/', search_with_fields, name='serach-with-booking')
]
