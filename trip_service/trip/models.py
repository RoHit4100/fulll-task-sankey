from django.db import models

class Route(models.Model):
    route_id = models.CharField(max_length=10, primary_key=True)
    user_id = models.IntegerField()
    route_name = models.CharField(max_length=100)
    route_origin = models.CharField(max_length=100)
    route_destination = models.CharField(max_length=100)
    route_stops = models.JSONField()

    def __str__(self):
        return self.route_name


class Trip(models.Model):
    trip_id = models.CharField(max_length=10, primary_key=True)
    user_id = models.IntegerField()
    vehicle_id = models.IntegerField()
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    driver_name = models.CharField(max_length=100)

    def __str__(self):
        return self.trip_id