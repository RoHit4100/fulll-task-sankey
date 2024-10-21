import os
import django
from faker import Faker
import random

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'booking_service.settings') # REPLACE WITH YOUR PROJECT NAME
django.setup()

from booking.models import Booking  # REPLACE WITH YOUR APP MODEL

fake = Faker()

def generate_fake_booking_data():
    for _ in range(50):
        ticket_id = f'TK{random.randint(10000000, 99999999)}'
        trip_id = f'TP{random.randint(10000000, 99999999)}'
        traveler_name = fake.name()
        traveler_number = f'{random.randint(6000000000, 9999999999)}'
        ticket_cost = round(random.uniform(50, 500), 2)
        traveler_email = fake.email()

        booking = Booking(
            ticket_id=ticket_id,
            trip_id=trip_id,
            traveler_name=traveler_name,
            traveler_number=traveler_number,
            ticket_cost=ticket_cost,
            traveler_email=traveler_email
        )
        booking.save()

if __name__ == '__main__':
    generate_fake_booking_data()
    print("Successfully generated 35 fake bookings.")
