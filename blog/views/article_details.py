from scripts.utils import customResponse, closeDBConnection, convert_keys_to_string, validate_integer, validate_bool, getArrFromString
import json

def getArticles():
    return customResponse("4XX", {"error": "Invalid request"})

def postArticles():
    return customResponse("4XX", {"error": "Invalid request"})
