from scripts.utils import customResponse, closeDBConnection, convert_keys_to_string, validate_integer

from ..models.category import Category, validateCategoryData, populateCategoryData, filterCategories
from ..models.product import Product
from ..models.productLot import ProductLot
from ..serializers.category import categories_parser, serialize_categories
from django.template.defaultfilters import slugify
import json

import logging
log = logging.getLogger("django")

def get_categories_details(request, parameters):
	try:
		if "isBuyer" in parameters and parameters["isBuyer"] == 1:
			parameters["category_show_online"] = 1
		elif "isBuyerStore" in parameters and parameters["isBuyerStore"] == 1:
			parameters["category_show_online"] = 1
		elif "isSeller" in parameters and parameters["isSeller"] == 1:
			pass
		elif "isInternalUser" in parameters and parameters["isInternalUser"] == 1:
			pass
		else:
			parameters["category_show_online"] = 1

		categories = filterCategories(parameters)

		statusCode = 200
		body = {"categories": categories_parser(categories, parameters)}

	except Exception as e:
		log.critical(e)
		statusCode = 500
		body = {}
		
	closeDBConnection()
	return customResponse(statusCode, body,  error_code=0)

def post_new_category(request):
	try:
		requestbody = request.body.decode("utf-8")
		category = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse(400, error_code=4)

	if not len(category) or not validateCategoryData(category, Category(), 1):
		return customResponse(400, error_code=5, error_details= "Invalid data for category sent")

	category["slug"] = slugify(category["name"])

	try:
		newCategory = Category()
		populateCategoryData(newCategory, category)
		newCategory.save()
		 
	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse(500, error_code = 1)
	else:
		closeDBConnection()
		return customResponse(200, {"categories" : serialize_categories(newCategory)})


def update_category(request):
	try:
		requestbody = request.body.decode("utf-8")
		category = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse(400, error_code=4)

	if not len(category) or not "categoryID" in category or not validate_integer(category["categoryID"]):
		return customResponse(400, error_code=5,  error_details= "Id for category not sent")

	categoryPtr = Category.objects.filter(id=int(category["categoryID"]))

	if len(categoryPtr) == 0:
		return customResponse(400, error_code=6, error_details = "Invalid id for category sent")

	categoryPtr = categoryPtr[0]

	if not validateCategoryData(category, categoryPtr, 0):
		return customResponse(400, error_code=5, error_details= "Invalid data for category sent")

	category["slug"] = slugify(category["name"])

	try:
		populateCategoryData(categoryPtr, category)
		categoryPtr.save()

	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse(500, error_code = 3)
	else:
		closeDBConnection()
		return customResponse(200, {"categories": serialize_categories(categoryPtr)})

def delete_category(request):
	try:
		requestbody = request.body.decode("utf-8")
		category = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse(400, error_code=4)

	if not len(category) or not "categoryID" in category or not validate_integer(category["categoryID"]):
		return customResponse(400, error_code=5,  error_details= "Id for category not sent")

	categoryPtr = Category.objects.filter(id=int(category["categoryID"]), delete_status=False)

	if len(categoryPtr) == 0:
		return customResponse(400, error_code=6, error_details = "Invalid id for category sent")

	categoryPtr = categoryPtr[0]

	try:
		categoryPtr.delete_status = True
		categoryPtr.save()
	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse(500, error_code = 3)
	else:
		closeDBConnection()
		return customResponse(200, {"success": "category deleted"})