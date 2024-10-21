import os
import django
from faker import Faker
import random


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trip_service.settings')  # replace with your project name
django.setup()

from trip.models import Route, Trip  # replace with your app name

fake = Faker()

def create_dummy_routes(num=10):
    for _ in range(num):
        route_id = f'RT{fake.random_int(min=10000000, max=99999999)}'
        route_origin = fake.city()
        route_destination = fake.city()
        route_name = f'{route_origin} - {route_destination}'
        route_stops = [{'lat': round(random.uniform(50, 500), 2), 'long': round(random.uniform(50, 500), 2), 'stop_name':fake.city()} for _ in range(random.randint(1, 5))]  # Random number of stops
        route_stops.insert(0, {'lat': round(random.uniform(50, 500), 2), 'long': round(random.uniform(50, 500), 2), 'stop_name': route_origin})
        route_stops.append({'lat': round(random.uniform(50, 500), 2), 'long': round(random.uniform(50, 500), 2), 'stop_name':route_destination})
        route = Route(
            route_id=route_id,
            user_id=fake.random_int(min=1, max=100),
            route_name=route_name,
            route_origin=route_origin,
            route_destination=route_destination,
            route_stops=route_stops
        )
        route.save()
        print(f'Created route: {route}')

def create_dummy_trips(num=10):
    routes = Route.objects.all()  # Get all existing routes
    for _ in range(num):
        trip_id = f'TP{fake.random_int(min=10000000, max=99999999)}'
        trip = Trip(
            trip_id=trip_id,
            user_id=fake.random_int(min=1, max=1000),
            vehicle_id=fake.random_int(min=1, max=5000),  # Assuming vehicle_id is a number
            route=random.choice(routes) if routes else None,  # Randomly assign an existing route
            driver_name=fake.name()
        )
        trip.save()
        print(f'Created trip: {trip}')

if __name__ == "__main__":
    create_dummy_routes(50)  
    create_dummy_trips(50)   