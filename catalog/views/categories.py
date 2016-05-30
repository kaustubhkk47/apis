from scripts.utils import customResponse, closeDBConnection, convert_keys_to_string

from ..models.category import Category, validateCategoryData, populateCategoryData
from ..models.product import Product
from ..models.productLot import ProductLot
from ..serializers.category import categories_parser, serialize_categories
from django.template.defaultfilters import slugify
import json

def get_categories_details(request, categoriesArr = []):
	try:
		if len(categoriesArr) == 0:
			categories = Category.objects.filter(delete_status=False)
		else:
			categories = Category.objects.filter(id__in=categoriesArr,delete_status=False)
		closeDBConnection()
		statusCode = "2XX"
		body = {"categories": categories_parser(categories)}

	except Exception as e:
		statusCode = "4XX"
		body = {"error": "Invalid category"}

	return customResponse(statusCode, body)

def post_new_category(request):
	try:
		requestbody = request.body.decode("utf-8")
		category = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse("4XX", {"error": "Invalid data sent in request"})

	if not len(category) or not validateCategoryData(category, Category(), 1):
		return customResponse("4XX", {"error": "Invalid data for category sent"})

	category["slug"] = slugify(category["name"])

	try:
		newCategory = Category()
		populateCategoryData(newCategory, category)
		newCategory.save()
		 
	except Exception as e:
		closeDBConnection()
		return customResponse("4XX", {"error": "unable to create entry in db"})
	else:
		closeDBConnection()
		return customResponse("2XX", {"category" : serialize_categories(newCategory)})


def update_category(request):
	try:
		requestbody = request.body.decode("utf-8")
		category = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse("4XX", {"error": "Invalid data sent in request"})

	if not len(category) or not "categoryID" in category or category["categoryID"]==None:
		return customResponse("4XX", {"error": "Id for category not sent"})

	categoryPtr = Category.objects.filter(id=int(category["categoryID"]))

	if len(categoryPtr) == 0:
		return customResponse("4XX", {"error": "Invalid id for category sent"})

	categoryPtr = categoryPtr[0]

	if not validateCategoryData(category, categoryPtr, 0):
		return customResponse("4XX", {"error": "Invalid data for category sent"})

	category["slug"] = slugify(category["name"])

	try:
		populateCategoryData(categoryPtr, category)
		categoryPtr.save()

	except Exception as e:
		closeDBConnection()
		return customResponse("4XX", {"error": "could not update"})
	else:
		closeDBConnection()
		return customResponse("2XX", {"category": serialize_categories(categoryPtr)})

def delete_category(request):
	try:
		requestbody = request.body.decode("utf-8")
		category = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse("4XX", {"error": "Invalid data sent in request"})

	if not len(category) or not "categoryID" in category or category["categoryID"]==None:
		return customResponse("4XX", {"error": "Id for category not sent"})

	categoryPtr = Category.objects.filter(id=int(category["categoryID"]))

	if len(categoryPtr) == 0:
		return customResponse("4XX", {"error": "Invalid id for category sent"})

	categoryPtr = categoryPtr[0]

	try:
		categoryPtr.delete_status = True
		categoryPtr.save()
	except Exception as e:
		closeDBConnection()
		return customResponse("4XX", {"error": "could not delete"})
	else:
		closeDBConnection()
		return customResponse("2XX", {"category": "category deleted"})