from django.http import JsonResponse
from django.db import connection

def closeDBConnection():
    connection.close()

def customResponse(statusCode, body):
    response = {}
    response["statusCode"] = statusCode
    response["body"] = body

    return JsonResponse(response)

def convert_keys_to_string(dictionary):
    """Recursively converts dictionary keys to strings."""
    if not isinstance(dictionary, dict):
        return dictionary
    return dict((str(k), convert_keys_to_string(v))
        for k, v in dictionary.items())