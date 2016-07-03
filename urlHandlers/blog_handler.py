from django.views.decorators.csrf import csrf_exempt

from scripts.utils import customResponse, get_token_payload, getArrFromString, validate_bool, getPaginationParameters

from blog.views import article

from .user_handler import populateInternalUserIDParameters

@csrf_exempt
def article_details(request):
    if request.method == 'GET':

        parameters = getArticleParameters(request)

        return article.get_article_details(request, parameters)

    elif request.method == 'POST':
        return article.post_new_article(request)
    elif request.method == "PUT":
        return article.update_article(request)
    elif request.method == "DELETE":
        return article.delete_article(request)
    
    return customResponse('4XX', {"error": "Invalid request"})

def getArticleParameters(request, parameters = {}):

    articleID = request.GET.get("articleID", "")
    if articleID != "" and articleID != None:
        parameters["articlesArr"] = getArrFromString(articleID)

    showOnline = request.GET.get("show_online", None)
    if validate_bool(showOnline):
        parameters["show_online"] = int(showOnline)

    articleDetails = request.GET.get("article_details", None)
    if validate_bool(articleDetails):
        parameters["article_details"] = int(articleDetails)
    else:
        parameters["article_details"] = 0

    internalUserDetails = request.GET.get("internal_user_details", None)
    if validate_bool(internalUserDetails):
        parameters["internal_user_details"] = int(internalUserDetails)
    else:
        parameters["internal_user_details"] = 0

    parameters = populateInternalUserIDParameters(request, parameters)

    parameters = getPaginationParameters(request, parameters)

    return parameters