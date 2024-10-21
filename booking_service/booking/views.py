from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from .models import Booking
from .serializers import BookingSerializer, UserSerializer
import re

@api_view(['POST'])
def register(request):
    try:
        data = request.data
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User is successfully created'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

def validate_ticket_id(value):
    if not re.match(r'^TK\d{8}$', value):
        raise ValidationError('Invalid ID format for Ticket ID.')

def validate_trip_id(value):
    if not re.match(r'^TP\d{8}$', value):
        raise ValidationError(f'Invalid ID format for Trip ID.')


@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def create_booking(request):
    data = request.data
    try:
        # Validate ticket_id format
        validate_ticket_id(data.get('ticket_id'))
        validate_trip_id(data.get('trip_id'))

        # Serializer validation
        serializer = BookingSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Booking created successfully!'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except ValidationError as ve:
        return Response({'error': str(ve)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_booking_list(request):
    try:
        # Sorting
        sort_by = request.query_params.get('sort', None)
        if sort_by:
            bookings = Booking.objects.all().order_by(sort_by)  # Apply sorting based on the sort query parameter
        else:
            bookings = Booking.objects.all().order_by('ticket_id')

        # Pagination
        paginator = PageNumberPagination()
        paginated_bookings = paginator.paginate_queryset(bookings, request)
        serializer = BookingSerializer(paginated_bookings, many=True)

        return paginator.get_paginated_response(serializer.data)  # Use the paginator's response method
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_booking_detail(request, booking_id):
    # Retrieve a specific booking by ID
    try:
        booking = Booking.objects.get(ticket_id=booking_id)
        serializer = BookingSerializer(booking)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Booking.DoesNotExist:
        return Response({'error': 'Booking not found.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_bookings(request, trip_id):
    try:
        # Get the bookings for the given trip_id
        bookings = Booking.objects.filter(trip_id=trip_id)
        # Check if bookings exist
        if not bookings.exists():
            return Response({'error': 'No bookings found for this trip'}, status=status.HTTP_404_NOT_FOUND)

        # Serialize the queryset
        serializer = BookingSerializer(bookings, many=True)  # 'many=True' is needed when serializing a queryset
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])           
def search_with_fields(request):
    data = request.data
    try:
        field = data.get('field')
        query = data.get('query')

        # validate input field and query
        if not field or not query:
            return Response({'error': 'Field and query are required.'}, status=400)

        # filter by the provided field and query
        if field in ['ticket_id', 'trip_id', 'traveler_name', 'traveler_number', 'traveler_email']:
            filter_kwargs = {field: query}
            bookings = Booking.objects.filter(**filter_kwargs)
            if bookings.exists():
                serializer = BookingSerializer(bookings, many=True)
                return Response(serializer.data)
            else:
                return Response({'error': 'No bookings found matching the query.'}, status=404)
        else:
            return Response({'error': 'Invalid search field.'}, status=400)

    except Exception as e:
        return Response({'error': str(e)}, status=500)