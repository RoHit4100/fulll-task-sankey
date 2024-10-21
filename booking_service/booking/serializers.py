from rest_framework import serializers
from .models import Booking
import re
from django.contrib.auth.models import User


class BookingSerializer(serializers.ModelSerializer):
    traveler_email = serializers.EmailField()

    class Meta:
        model = Booking
        fields = ['ticket_id', 'trip_id', 'traveler_name', 'traveler_number', 'ticket_cost', 'traveler_email']

    # Custom validation for traveler_number
    def validate_traveler_number(self, value):
        if not re.match(r'^\d{10}$', value):
            raise serializers.ValidationError("Traveler number must be a 10-digit number.")
        return value


class UserSerializer(serializers.Serializer):
    username = serializers.CharField()
    email= serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, data):
        # check if username exists or not
        user = User.objects.filter(username=data.get('username')).exists()
        if user:
            raise serializers.ValidationError("Username is already taken")
        return data

    def create(self, validated_date):
        return User.objects.create_user(**validated_date)
        