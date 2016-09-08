from scripts.utils import customResponse, closeDBConnection, convert_keys_to_string, validate_integer, validate_bool, getArrFromString, save_file_from_request
import json
import settings

from ..models.article import Article, filterArticles, validateArticleData, populateArticleData
from users.models.internalUser import InternalUser
from ..serializers.article import parseArticles, serializeArticle
from django.template.defaultfilters import slugify

from django.core.paginator import Paginator
import logging
log = logging.getLogger("django")

def get_article_details(request, parameters):
	try:
		articles = filterArticles(parameters)

		paginator = Paginator(articles, parameters["itemsPerPage"])

		try:
			pageItems = paginator.page(parameters["pageNumber"])
		except Exception as e:
			pageItems = []

		response = parseArticles(pageItems,parameters)
		statusCode = "2XX"
		body = {"articles": response,"total_items":paginator.count, "total_pages":paginator.num_pages, "page_number":parameters["pageNumber"], "items_per_page":parameters["itemsPerPage"]}

	except Exception as e:
		log.critical(e)
		statusCode = "4XX"
		body = {"error": "Invalid article"}

	closeDBConnection()
	return customResponse(statusCode, body)

def post_new_article(request):
	try:
		requestbody = request.body.decode("utf-8")
		article = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse("4XX", {"error": "Invalid data sent in request"})

	if not len(article) or not validateArticleData(article, Article(), 1):
		return customResponse("4XX", {"error": "Invalid data for article sent"})

	if not "internaluserID" in article or not validate_integer(article["internaluserID"]):
		return customResponse("4XX", {"error": "ID for author not sent"})

	internalUserPtr = InternalUser.objects.filter(id=int(article["internaluserID"]))

	if not internalUserPtr.exists():
		return customResponse("4XX", {"error": "Invalid ID for author sent"})

	article["slug"] = slugify(article["title"])

	try:
		newArticle = Article(author_id=int(article["internaluserID"]))
		populateArticleData(newArticle, article)
		newArticle.save()
		 
	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse("4XX", {"error": "unable to create entry in db"})
	else:
		closeDBConnection()
		return customResponse("2XX", {"article" : serializeArticle(newArticle)})

def upload_article_file(request):
	try:
		requestbody = json.dumps(request.POST).encode("utf-8")
		article = convert_keys_to_string(json.loads(requestbody))
		print article
	except Exception as e:
		return customResponse("4XX", {"error": "Invalid data sent in request"})

	if not len(article) or not "articleID" in article or not validate_integer(article["articleID"]):
		return customResponse("4XX", {"error": "Id for article not sent"})

	articlePtr = Article.objects.filter(id=int(article["articleID"]))

	if len(articlePtr) == 0:
		return customResponse("4XX", {"error": "Invalid ID for article sent"})

	articlePtr = articlePtr[0]

	try:
		if "file" in request.FILES:
			outputLink = "media/uploadedfiles/blogcoverphoto/{}/".format(articlePtr.author.id)
			outputDirectory = settings.STATIC_ROOT + outputLink
			outputFileName = "{}-{}.jpg".format(articlePtr.slug,articlePtr.id)
			articlePtr.cover_photo = outputLink + outputFileName
			save_file_from_request(request, outputDirectory, outputFileName)
			articlePtr.save()
		else:
			return customResponse("4XX", {"error": "No files sent in request"})

	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse("4XX", {"error": "could not save"})
	else:
		closeDBConnection()
		return customResponse("2XX",  {"success" : "file uploaded"})

def update_article(request):
	try:
		requestbody = request.body.decode("utf-8")
		article = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse("4XX", {"error": "Invalid data sent in request"})

	if not len(article) or not "articleID" in article or not validate_integer(article["articleID"]):
		return customResponse("4XX", {"error": "Id for article not sent"})

	articlePtr = Article.objects.filter(id=int(article["articleID"]))

	if len(articlePtr)==0:
		return customResponse("4XX", {"error": "Invalid ID for article sent"})

	articlePtr = articlePtr[0]

	if not validateArticleData(article, articlePtr,0):
		return customResponse("4XX", {"error": "Invalid data for article sent"})

	article["slug"] = slugify(article["title"])

	try:
		populateArticleData(articlePtr, article)
		articlePtr.save()
	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse("4XX", {"error": "could not update"})
	else:
		closeDBConnection()
		return customResponse("2XX",  {"article" : serializeArticle(articlePtr)})

def delete_article(request):
	try:
		requestbody = request.body.decode("utf-8")
		article = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse("4XX", {"error": "Invalid data sent in request"})

	if not len(article) or not "articleID" in article or not validate_integer(article["articleID"]):
		return customResponse("4XX", {"error": "Id for article not sent"})

	articlePtr = Article.objects.filter(id=int(article["articleID"]))

	if len(articlePtr)==0:
		return customResponse("4XX", {"error": "Invalid ID for article sent"})

	articlePtr = articlePtr[0]

	try:
		articlePtr.delete_status = True
		articlePtr.save()
	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse("4XX", {"error": "could not update"})
	else:
		closeDBConnection()
		return customResponse("2XX",  {"body" : "article deleted"})