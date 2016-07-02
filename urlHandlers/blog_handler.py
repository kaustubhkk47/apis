from django.views.decorators.csrf import csrf_exempt

from scripts.utils import customResponse, get_token_payload, getArrFromString

from blog.views import *

@csrf_exempt
def article_details(request):
    if request.method == 'GET':
        params = {}
        params["articleID"] = request.GET.get('articleID', '')
        if params["articleID"] != '':
            params["articleID"] = getArrFromString(articleID)
        else:
            params["articleID"] = []

        return getArticles(request, params)

    elif request.method == 'POST':
        return postArticles()
    else:
        return customResponse('4XX', {"error": "Invalid request"})
