from scripts.utils import customResponse, closeDBConnection, convert_keys_to_string, validate_integer, validate_bool, getArrFromString
import json

from ..models.articles import Post

def getArticles(request, params):
    articles = Post.objects.filter(show_online=True, delete_status=False).select_related('InternalUser')

    if len(articleID) > 0:
        articles = articles.filter(id__in=params["articleID"])
        
    return customResponse("4XX", {"error": "Invalid request"})

def postArticles():
    return customResponse("4XX", {"error": "Invalid request"})
