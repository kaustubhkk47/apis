from django.views.decorators.csrf import csrf_exempt

from scripts.utils import customResponse, get_token_payload, getArrFromString, validate_bool

from blog.views import article

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

def getArticleParameters(request):

    parameters = {}

    articleID = request.GET.get("articleID", "")
    if articleID != "" and articleID != None:
        parameters["articlesArr"] = getArrFromString(articleID)

    accessToken = request.GET.get("access_token", "")
    tokenPayload = get_token_payload(accessToken, "internaluserID")
    parameters["isInternalUser"] = 0
    if "internaluserID" in tokenPayload and tokenPayload["internaluserID"]!=None:
        parameters["internalusersArr"] = [tokenPayload["internaluserID"]]
        parameters["isInternalUser"] = 1

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

    try:
        pageNumber = int(request.GET.get("page_number", 1))
        itemsPerPage = int(request.GET.get("items_per_page", 10))
    except Exception as e:
        pageNumber = 1
        itemsPerPage = 10

    if not pageNumber > 0 or not itemsPerPage > 0:
        pageNumber = 1
        itemsPerPage = 10
    parameters["pageNumber"] = pageNumber
    parameters["itemsPerPage"] = itemsPerPage

    return parameters