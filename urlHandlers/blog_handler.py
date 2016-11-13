from django.views.decorators.csrf import csrf_exempt

from scripts.utils import customResponse, get_token_payload, getArrFromString, validate_bool, getPaginationParameters, getApiVersion

from blog.views import article

from .user_handler import populateInternalUserIDParameters

@csrf_exempt
def article_details(request, version = "0"):
	version = getApiVersion(request.META["HTTP_ACCEPT"])
	parameters = getArticleParameters(request, {}, version)

	if request.method == 'GET':

		return article.get_article_details(request, parameters)

	elif request.method == 'POST':

		if parameters["isInternalUser"] == 0:
			return customResponse(403, error_code = 8)

		return article.post_new_article(request)
	elif request.method == "PUT":
		if parameters["isInternalUser"] == 0:
			return customResponse(403, error_code = 8)
		return article.update_article(request)
	elif request.method == "DELETE":
		if parameters["isInternalUser"] == 0:
			return customResponse(403, error_code = 8)
		return article.delete_article(request)
	
	return customResponse(404, error_code = 7)

@csrf_exempt
def article_cover_photo_details(request, version = "0"):
	version = getApiVersion(request.META["HTTP_ACCEPT"])
 
	if request.method == 'POST':
		parameters = getArticleParameters(request, {}, version)
		if parameters["isInternalUser"] == 0:
			return customResponse(403, error_code = 8)
		return article.upload_article_file(request)
	
	return customResponse(404, error_code = 7)

def getArticleParameters(request, parameters = {}, version = "0"):

	defaultValue = 0

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
		parameters["article_details"] = defaultValue

	internalUserDetails = request.GET.get("internal_user_details", None)
	if validate_bool(internalUserDetails):
		parameters["internal_user_details"] = int(internalUserDetails)
	else:
		parameters["internal_user_details"] = defaultValue

	parameters = populateInternalUserIDParameters(request, parameters)

	parameters = getPaginationParameters(request, parameters)

	return parameters