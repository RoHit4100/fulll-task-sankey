from django.db import models

class Booking(models.Model):
    ticket_id = models.CharField(max_length=10, primary_key=True)  # TK12345678
    trip_id = models.CharField(max_length=10)    
    traveler_name = models.CharField(max_length=100)
    traveler_number = models.CharField(max_length=10)  # To be validated by regex
    ticket_cost = models.FloatField()
    traveler_email = models.EmailField()  # Validated by serializer
