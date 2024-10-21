from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
import json
import re
from django.core.paginator import Paginator
from .models import Route, Trip
import requests
from requests.exceptions import RequestException
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from .middleware import auth

def registration(request):
    # here I will get the data related to the user
    try: 
        if request.method == 'POST':
            # get the data for the username and the password with the email
            data = json.loads(request.body)
            email = data['email']
            username = data['username']
            password = data['password']
            
            # create the user
            user = User.objects.create_user(username=username, email=email, password=password) # this will create user with hashing
            return JsonResponse({'message': 'User successfully created'}, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def validate_trip_id(value):
    
        if not re.match(r'^TP\d{8}$', value):
            raise ValidationError('Trip Id must start with (TP) and should be followed by 8 digits.')
        return value
    
def validate_route_id(value):
        if not re.match(r'^RT\d{8}$', value):
            raise ValidationError('Route Id must start with (RT) followed by 8 digits.')
        return value    

@auth
@csrf_exempt
def create_route(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # validate route_id format
            validate_route_id(data.get('route_id'))

            # create Route instance
            route = Route.objects.create(
                route_id=data['route_id'],
                user_id=data['user_id'],
                route_name=data['route_name'],
                route_origin=data['route_origin'],
                route_destination=data['route_destination'],
                route_stops=data['route_stops']
            )
            return JsonResponse({'message': 'Route created successfully!'}, status=200)

        except ValidationError as ve:
            return JsonResponse({'error': str(ve)}, status=400)
        except Exception as e:
            return JsonResponse({'error': 'Something went wrong!'}, status=500)
    else:
        return JsonResponse({'error': 'Only POST requests are allowed.'}, status=405)
    
    
@auth
@csrf_exempt
def create_trip(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # Validate trip_id format
            validate_trip_id(data.get('trip_id'))

            # Create Trip instance
            trip = Trip.objects.create(
                trip_id=data['trip_id'],
                user_id=data['user_id'],
                vehicle_id=data['vehicle_id'],
                route_id=data['route_id'],
                driver_name=data['driver_name']
            )
            return JsonResponse({'message': 'Trip created successfully!'}, status=200)

        except ValidationError as ve:
            return JsonResponse({'error': str(ve)}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Only POST requests are allowed.'}, status=405)


# trip Listing with Pagination and Foreign Key Route Data
@auth
def trip_list(request):
    try:
        if request.method == 'GET':
            sort_by = request.GET.get('sort', None)
            if sort_by:
                trips = Trip.objects.select_related('route').order_by(sort_by).all()
            else:
                trips = Trip.objects.select_related('route').order_by('trip_id').all()
                
            # Implement pagination
            paginator = Paginator(trips, 10)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)

            # Prepare response data with related route details
            trips_data = []
            for trip in page_obj.object_list:
                trips_data.append({
                    'trip_id': trip.trip_id,
                    'user_id': trip.user_id,
                    'vehicle_id': trip.vehicle_id,
                    'route': {
                        'route_id': trip.route.route_id,
                        'route_name': trip.route.route_name,
                        'route_origin': trip.route.route_origin,
                        'route_destination': trip.route.route_destination,
                        'route_stops': trip.route.route_stops,
                    },
                    'driver_name': trip.driver_name,
                })

            return JsonResponse({'trips': trips_data}, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

@auth
# trip detail View with foreign Key Route Data
def trip_detail(request, trip_id):
    try:
        # Fetch trip with its related route data using select_related
        trip = Trip.objects.select_related('route').get(trip_id=trip_id)
        
        # Prepare detailed response with related route data
        trip_data = {
            'trip_id': trip.trip_id,
            'user_id': trip.user_id,
            'vehicle_id': trip.vehicle_id,
            'driver_name': trip.driver_name,
            'route': {
                'route_id': trip.route.route_id,
                'route_name': trip.route.route_name,
                'route_origin': trip.route.route_origin,
                'route_destination': trip.route.route_destination,
                'route_stops': trip.route.route_stops,
            }
        }

        return JsonResponse({'trip': trip_data}, status=200)

    except Trip.DoesNotExist:
        return JsonResponse({'error': 'Trip not found'}, status=404)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

@auth
# interservice call 
def trip_bookings(request):
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            trip_id = data.get('trip_id')
            if not trip_id:
                return JsonResponse({'error': 'Trip id is not given'})
            url = f'http://localhost:5000/api/get-bookings/{trip_id}/'
            username = "hackur777"
            password = "12345678"
            response = requests.get(url, auth=(username, password))
            # print(response.status_cprint(trip_id)
            # print(response.json())
            # response = requests.get(url)

            if response.status_code == 200:
                # Return the JSON data from the external API as a JsonResponse
                return JsonResponse(response.json(), status=200, safe=False)
            else:
                # Handle 404 or other status codes from the external API
                return JsonResponse({'error': 'Not found'}, status=response.status_code)

    except RequestException as e:
        # Handle any exceptions raised during the external API call
        return JsonResponse({'error': f'Failed to fetch data: {str(e)}'}, status=500)

    except Exception as e:
        # General exception handling
        return JsonResponse({'error': str(e)}, status=500)

# iterservice call which sends the booking details as well with the trip details
@auth
@csrf_exempt
def trip_detail_with_bookings(request):
    try:
        # Fetch trip with its related route data using select_related
        data = json.loads(request.body)
        trip_id = data.get('trip_id')
        if not trip_id:
            return JsonResponse({'error': 'Trip id is not given'})
        trip = Trip.objects.select_related('route').get(trip_id=trip_id)
        
        # Prepare detailed trip data with related route info
        trip_data = {
            'trip_id': trip.trip_id,
            'user_id': trip.user_id,
            'vehicle_id': trip.vehicle_id,
            'driver_name': trip.driver_name,
            'route': {
                'route_id': trip.route.route_id,
                'route_name': trip.route.route_name,
                'route_origin': trip.route.route_origin,
                'route_destination': trip.route.route_destination,
                'route_stops': trip.route.route_stops,
            }
        }

        # Fetch bookings from the external API
        try:
            url = f'http://localhost:5000/api/get-bookings/{trip_id}/'
            username = "hackur777"
            password = "12345678"
            response = requests.get(url, auth=(username, password))
            
            if response.status_code == 200:
                bookings_data = response.json()
            else:
                bookings_data = {'error': 'No bookings found'}

        except RequestException as e:
            bookings_data = {'error': f'Failed to fetch bookings: {str(e)}'}

        # Combine trip details and bookings into one response
        response_data = {
            'trip': trip_data,
            'bookings': bookings_data
        }

        return JsonResponse(response_data, status=200)

    except Trip.DoesNotExist:
        return JsonResponse({'error': 'Trip not found'}, status=404)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# searching with the particular field
@auth
@csrf_exempt
def search_with_field(request):
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            field = data.get('field')
            query = data.get('query')
            
            # Validate input field and query
            if not field or not query:
                return JsonResponse({'error': 'Field and query are required.'}, status=400)

            # Adjust filtering for related fields
            if field == 'route_id':
                # Assuming route is a ForeignKey and you want to filter by route name or another attribute
                filter_kwargs = {'route': query}  # Adjust based on your Route model's fields
            elif field in ['trip_id', 'vehicle_id', 'user_id', 'driver_name']:
                filter_kwargs = {field: query}
            else:
                return JsonResponse({'error': 'Invalid search field.'}, status=400)

            # Select related route for optimization
            trips = Trip.objects.select_related('route').filter(**filter_kwargs).all()
            trips_data = []
            for trip in trips:
                trips_data.append({
                    'trip_id': trip.trip_id,
                    'user_id': trip.user_id,
                    'vehicle_id': trip.vehicle_id,
                    'route': {
                        'route_id': trip.route.route_id,
                        'route_name': trip.route.route_name,
                        'route_origin': trip.route.route_origin,
                        'route_destination': trip.route.route_destination,
                        'route_stops': trip.route.route_stops,
                    },
                    'driver_name': trip.driver_name,
                })
            return JsonResponse(trips_data, safe=False)
    
    except Trip.DoesNotExist:
        return JsonResponse({'error': 'No trips found matching the query.'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# helper function to determine if time is day or night
def is_night_time(date):
    return date.hour >= 21 or date.hour < 6

@auth
@csrf_exempt
def time_cycles(request):
    try:
        if request.method == 'POST':
            # parse the JSON request body
            data = json.loads(request.body)
            start_date = datetime.fromisoformat(data.get('start_date'))
            end_date = datetime.fromisoformat(data.get('end_date'))

            # validate that start_date is before end_date
            if start_date > end_date:
                return JsonResponse({'error': 'Please enter a valid start and end date'})

            # Initialize lists for day and night times
            night_time = []
            day_time = []
            current_date = start_date # taking temp variable for further processing

            # First Lap: Check if start_date is during night or day, and calculate first partial period
            if is_night_time(current_date):  # If it's night
                night_end = current_date.replace(hour=6, minute=0, second=0, microsecond=0)
                if night_end > end_date:
                    night_end = end_date
                night_time.append({
                    "start_date": current_date.isoformat(),
                    "end_date": night_end.isoformat()
                })
                current_date = night_end
            else:  # If it's day
                day_end = current_date.replace(hour=21, minute=0, second=0, microsecond=0)
                if day_end > end_date:
                    day_end = end_date
                day_time.append({
                    "start_date": current_date.isoformat(),
                    "end_date": day_end.isoformat()
                })
                current_date = day_end

            # Main Loop: Process full day (6:00 AM - 9:00 PM) and night (9:00 PM - 6:00 AM) cycles
            while current_date < end_date:
                if current_date.hour == 6:  # Start of the day period
                    day_end = current_date.replace(hour=21, minute=0, second=0, microsecond=0)
                    if day_end > end_date:
                        day_end = end_date
                    day_time.append({
                        "start_date": current_date.isoformat(),
                        "end_date": day_end.isoformat()
                    })
                    current_date = day_end

                elif current_date.hour == 21:  # Start of the night period
                    night_end = current_date.replace(hour=6, minute=0, second=0, microsecond=0) + timedelta(days=1)
                    if night_end  > end_date:
                        night_end = end_date
                    night_time.append({
                        "start_date": current_date.isoformat(),
                        "end_date": night_end.isoformat()
                    })
                    current_date = night_end 

                # Move forward to the next period (6:00 AM or 9:00 PM)
                # if current_date.hour < 6:
                #     current_date = current_date.replace(hour=6, minute=0, second=0, microsecond=0)
                # elif current_date.hour < 21:
                #     current_date = current_date.replace(hour=21, minute=0, second=0, microsecond=0)

            print(current_date)
            # Final Lap: If there's any remaining time
            if current_date < end_date:
                if is_night_time(current_date):
                    night_time.append({
                        "start_date": current_date.isoformat(),
                        "end_date": end_date.isoformat()
                    })
                else:
                    day_time.append({
                        "start_date": current_date.isoformat(),
                        "end_date": end_date.isoformat()
                    })

            # Return the JSON response with day and night periods
            return JsonResponse({
                "night_time": night_time,
                "day_time": day_time
            })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
