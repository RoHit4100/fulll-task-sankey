from django.urls import path
from . import views 

urlpatterns = [
    path('register/', views.registration, name='register'),
    path('create-route/', views.create_route, name='create_route'),
    path('create-trip/', views.create_trip, name='create_trip'),
    path('trips/', views.trip_list, name='trip_list'),
    path('trips/<str:trip_id>/', views.trip_detail, name='trip_details'),
    path('trips-booking/', views.trip_bookings, name='trip_bookings'),
    path('trips-booking-details/', views.trip_detail_with_bookings, name='trip_detail_with_bookings'),
    path('trips-search/', views.search_with_field, name='search_with_field'),
    path('time-cycles/', views.time_cycles, name='time_cycles'),   
]
