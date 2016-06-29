from django.views.decorators.csrf import csrf_exempt

from catalog.views import categories
from catalog.views import product
from scripts.utils import customResponse, get_token_payload, getArrFromString, getStrArrFromString, validate_number
import jwt as JsonWebToken

@csrf_exempt
def categories_details(request):

	if request.method == "GET":

		categoriesParameters = {}

		categoryID = request.GET.get("categoryID", "")
		if categoryID != "":
			categoriesParameters["categoriesArr"] = getArrFromString(categoryID)

		return categories.get_categories_details(request,categoriesParameters)
	elif request.method == "POST":
		return categories.post_new_category(request)
	elif request.method == "PUT":
		return categories.update_category(request)
	elif request.method == "DELETE":
		return categories.delete_category(request)

	return customResponse("4XX", {"error": "Invalid request"})


@csrf_exempt
def product_details(request):

	if request.method == "GET":

		productParameters = getProductParameters(request)

		return product.get_product_details(request,productParameters)
	elif request.method == "POST":
		return product.post_new_product(request)
	elif request.method == "PUT":
		return product.update_product(request)
	elif request.method == "DELETE":
		return product.delete_product(request)

	return customResponse("4XX", {"error": "Invalid request"})

@csrf_exempt
def product_file(request):

	if request.method == "GET":

		productParameters = getProductParameters(request)

		return product.get_product_file(request,productParameters)

	return customResponse("4XX", {"error": "Invalid request"})

def getProductParameters(request):
	productParameters = {}

	productID = request.GET.get("productID", "")
	categoryID = request.GET.get("categoryID", "")
	sellerID = request.GET.get("sellerID", "")
	fabric = request.GET.get("fabric", "")
	colour = request.GET.get("colour", "")
	min_price_per_unit = request.GET.get("min_price_per_unit", "")
	max_price_per_unit = request.GET.get("max_price_per_unit", "")

	try:
		pageNumber = int(request.GET.get("page_number", 1))
		productsperPage = int(request.GET.get("items_per_page", 10))
	except Exception as e:
		pageNumber = 1
		productsperPage = 10

	if not pageNumber > 0 or not productsperPage > 0:
		pageNumber = 1
		productsperPage = 10
			
	accessToken = request.GET.get("access_token", "")

	if productID != "":
		productParameters["productsArr"] = getArrFromString(productID)

	if categoryID != "":
		productParameters["categoriesArr"] = getArrFromString(categoryID)

	if fabric != "":
		productParameters["fabricArr"] = getStrArrFromString(fabric)

	if colour != "":
		productParameters["colourArr"] = getStrArrFromString(colour)

	if validate_number(min_price_per_unit) and validate_number(max_price_per_unit) and float(min_price_per_unit) >= 0 and float(max_price_per_unit) > float(min_price_per_unit):
		productParameters["price_filter_applied"] = True
		productParameters["min_price_per_unit"] = float(min_price_per_unit)
		productParameters["max_price_per_unit"] = float(max_price_per_unit)
		
	tokenPayload = get_token_payload(accessToken, "sellerID")
	productParameters["isSeller"] = 0		
	if "sellerID" in tokenPayload and tokenPayload["sellerID"]!=None:
		productParameters["isSeller"] = 1
		productParameters["sellerArr"] = [tokenPayload["sellerID"]]
	elif sellerID != "":
		productParameters["sellerArr"] = getArrFromString(sellerID)

	tokenPayload = get_token_payload(accessToken, "internaluserID")
	productParameters["isInternalUser"] = 0
	if "internaluserID" in tokenPayload and tokenPayload["internaluserID"]!=None:
		productParameters["internalusersArr"] = [tokenPayload["internaluserID"]]
		productParameters["isInternalUser"] = 1

	productParameters["pageNumber"] = pageNumber
	productParameters["itemsPerPage"] = productsperPage

	return productParameters
