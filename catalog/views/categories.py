from scripts.utils import customResponse, closeDBConnection, convert_keys_to_string

from ..models.category import Category, validateCategoryData, populateCategoryData
from ..models.product import Product
from ..models.productLot import ProductLot
from ..serializers.category import categories_parser, serialize_categories
from ..serializers.product import category_products_parser
from django.template.defaultfilters import slugify
import json

def get_categories_details(request, categoriesArr = []):
	try:
		if len(categoriesArr) == 0:
			categories = Category.objects.filter(delete_status=False)
			closeDBConnection()
			return customResponse("2XX", {"categories": categories_parser(categories)})
		else:
			categoriesWithProducts = Product.objects.filter(category__id__in=categoriesArr,delete_status=False,seller__delete_status=False,category__delete_status=False).select_related('category','seller')
			closeDBConnection()
			return customResponse("2XX", {"products": category_products_parser(categoriesWithProducts)})

	except Exception as e:
		print e
		return customResponse("4XX", {"error": "Invalid category"})

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
		print e
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

	if not len(category) or not "categoryID" in category or not category["categoryID"]:
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

	if not len(category) or not "categoryID" in category or not category["categoryID"]:
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