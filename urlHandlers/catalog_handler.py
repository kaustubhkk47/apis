from django.views.decorators.csrf import csrf_exempt

from catalog.views import categories
from catalog.views import product
from scripts.utils import customResponse, get_token_payload, getArrFromString, getStrArrFromString, validate_number, getPaginationParameters, validate_bool
import jwt as JsonWebToken

from .user_handler import populateSellerIDParameters, populateInternalUserIDParameters

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

		productParameters = populateProductParameters(request, {})

		return product.get_product_details(request,productParameters)
	elif request.method == "POST":
		return product.post_new_product(request)
	elif request.method == "PUT":
		return product.update_product(request)
	elif request.method == "DELETE":
		return product.delete_product(request)

	return customResponse("4XX", {"error": "Invalid request"})

@csrf_exempt
def product_colour_details(request):

	if request.method == "GET":

		return product.get_product_colour_details(request)

	return customResponse("4XX", {"error": "Invalid request"})

@csrf_exempt
def product_fabric_details(request):

	if request.method == "GET":

		return product.get_product_fabric_details(request)

	return customResponse("4XX", {"error": "Invalid request"})

@csrf_exempt
def product_file(request):

	if request.method == "GET":

		productParameters = populateProductParameters(request, {})

		return product.get_product_file(request,productParameters)

	return customResponse("4XX", {"error": "Invalid request"})

@csrf_exempt
def product_catalog(request):

	if request.method == "GET":

		productParameters = populateProductParameters(request, {})

		return product.get_product_catalog(request,productParameters)

	return customResponse("4XX", {"error": "Invalid request"})

def populateProductParameters(request, parameters = {}):

	productID = request.GET.get("productID", "")
	categoryID = request.GET.get("categoryID", "")
	fabric = request.GET.get("fabric", "")
	colour = request.GET.get("colour", "")
	min_price_per_unit = request.GET.get("min_price_per_unit", "")
	max_price_per_unit = request.GET.get("max_price_per_unit", "")

	parameters = getPaginationParameters(request, parameters, 10)

	if productID != "" and productID != None:
		parameters["productsArr"] = getArrFromString(productID)

	if categoryID != "" and categoryID != None:
		parameters["categoriesArr"] = getArrFromString(categoryID)

	if fabric != "" and fabric != None:
		parameters["fabricArr"] = getStrArrFromString(fabric)

	if colour != "" and colour != None:
		parameters["colourArr"] = getStrArrFromString(colour)

	if validate_number(min_price_per_unit) and validate_number(max_price_per_unit) and float(min_price_per_unit) >= 0 and float(max_price_per_unit) > float(min_price_per_unit):
		parameters["price_filter_applied"] = True
		parameters["min_price_per_unit"] = float(min_price_per_unit)
		parameters["max_price_per_unit"] = float(max_price_per_unit)

	parameters = populateSellerIDParameters(request, parameters)

	parameters = populateInternalUserIDParameters(request, parameters)

	return parameters

def populateProductDetailsParameters(request, parameters = {}):

	productDetails = request.GET.get("product_details", None)
	if validate_bool(productDetails):
		parameters["product_details"] = int(productDetails)
	else:
		parameters["product_details"] = 1

	productDetailsDetails = request.GET.get("product_details_details", None)
	if validate_bool(productDetailsDetails):
		parameters["product_details_details"] = int(productDetailsDetails)
	else:
		parameters["product_details_details"] = 1

	productLotDetails = request.GET.get("product_lot_details", None)
	if validate_bool(productLotDetails):
		parameters["product_lot_details"] = int(productLotDetails)
	else:
		parameters["product_lot_details"] = 1

	return parameters