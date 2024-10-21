from django.contrib.auth import authenticate
import base64
from django.http import JsonResponse

def auth(function_get_response):
    
    def middleware(request, *args, **kwargs):
        response = function_get_response(request)
        auth_header = request.META['HTTP_AUTHORIZATION']
        encoded_credentials = auth_header.split(' ')[1]  # Removes "Basic " to isolate credentials
        decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8").split(':')
        username = decoded_credentials[0]
        password = decoded_credentials[1]
        
        # now check if the user is authenticated or not, if not then send the json response, suggesting that unauthorized
        # print(username)
        # print(password)
        user = authenticate(username=username, password=password)
        if not user: 
            return JsonResponse({'error': 'something wrong with user and password'}, status=401)
        return response
    # #    if request.is_authenticated:
    # response = function(request)
        
    #    return response
    return middleware 