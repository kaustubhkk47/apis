from django.views.decorators.csrf import csrf_exempt

from catalog.views import categories
from catalog.views import product
from scripts.utils import customResponse, get_token_payload, getArrFromString, getStrArrFromString, validate_number, getPaginationParameters, validate_bool, getApiVersion
import jwt as JsonWebToken

from .user_handler import populateSellerIDParameters, populateInternalUserIDParameters, populateSellerDetailsParameters, populateAllUserIDParameters

@csrf_exempt
def categories_details(request, version = "0"):

	version = getApiVersion(request)

	parameters = populateCategoryParameters(request, {}, version)

	if request.method == "GET":

		return categories.get_categories_details(request,parameters)
	elif request.method == "POST":
		if parameters["isInternalUser"] == 0:
			return customResponse(403, error_code = 8)
		return categories.post_new_category(request)
	elif request.method == "PUT":
		if parameters["isInternalUser"] == 0:
			return customResponse(403, error_code = 8)
		return categories.update_category(request)
	elif request.method == "DELETE":
		if parameters["isInternalUser"] == 0:
			return customResponse(403, error_code = 8)
		return categories.delete_category(request)

	return customResponse(404, error_code = 7)

def populateCategoryParameters(request, parameters = {}, version = "0"):
	version = getApiVersion(request)
	categoryID = request.GET.get("categoryID", "")
	if categoryID != "":
		parameters["categoriesArr"] = getArrFromString(categoryID)

	categoryShowOnline = request.GET.get("category_show_online", "")
	if categoryShowOnline != "" and validate_bool(categoryShowOnline):
		parameters["category_show_online"] = int(categoryShowOnline)

	parameters = populateAllUserIDParameters(request, parameters, version)

	parameters = populateCategorytDetailsParameters(request, parameters, version)

	return parameters

def populateCategorytDetailsParameters(request, parameters = {}, version = "0"):

	defaultValue = 1

	if version == "1":
		defaultValue = 0

	sellerCategoryDetails = request.GET.get("seller_category_details", None)
	if validate_bool(sellerCategoryDetails):
		parameters["seller_category_details"] = int(sellerCategoryDetails)
	else:
		parameters["seller_category_details"] = defaultValue

	parameters["category_details_details"] = 1

	return parameters


@csrf_exempt
def product_details(request, version = "0"):
	version = getApiVersion(request)
	parameters = populateProductParameters(request, {}, version)

	if request.method == "GET":
		return product.get_product_details(request,parameters)
	elif request.method == "POST":
		if parameters["isSeller"] == 0 and parameters["isInternalUser"] == 0:
			return customResponse(403, error_code = 8)
		return product.post_new_product(request, parameters)
	elif request.method == "PUT":
		if parameters["isSeller"] == 0 and parameters["isInternalUser"] == 0:
			return customResponse(403, error_code = 8)
		return product.update_product(request, parameters)
	elif request.method == "DELETE":
		if parameters["isSeller"] == 0 and parameters["isInternalUser"] == 0:
			return customResponse(403, error_code = 8)
		return product.delete_product(request)

	return customResponse(404, error_code = 7)

@csrf_exempt
def product_colour_details(request, version = "0"):

	version = getApiVersion(request)

	if request.method == "GET":

		return product.get_product_colour_details(request)

	return customResponse(404, error_code = 7)

@csrf_exempt
def product_fabric_details(request, version = "0"):

	version = getApiVersion(request)

	if request.method == "GET":

		return product.get_product_fabric_details(request)

	return customResponse(404, error_code = 7)

@csrf_exempt
def product_file(request, version = "0"):

	version = getApiVersion(request)

	parameters = populateProductParameters(request, {}, version)

	if request.method == "GET":

		if parameters["isInternalUser"] == 0:
			return customResponse(403, error_code = 8)

		return product.get_product_file(request,parameters)

	return customResponse(404, error_code = 7)

@csrf_exempt
def product_catalog(request, version = "0"):

	version = getApiVersion(request)

	parameters = populateProductParameters(request, {}, version)

	if request.method == "GET":

		if parameters["isInternalUser"] == 0:
			return customResponse(403, error_code = 8)

		return product.get_product_catalog(request,parameters)

	return customResponse(404, error_code = 7)

def populateProductParameters(request, parameters = {}, version = "0"):

	print parameters
	parameters = getPaginationParameters(request, parameters, 10)

	parameters = populateProductFilterParameters(request, parameters, version)

	parameters = populateAllUserIDParameters(request, parameters, version)

	parameters = populateProductDetailsParameters(request, parameters, version)

	return parameters

def populateProductFilterParameters(request, parameters = {}, version = "0"):

	productID = request.GET.get("productID", "")
	categoryID = request.GET.get("categoryID", "")
	fabric = request.GET.get("fabric", "")
	colour = request.GET.get("colour", "")
	min_price_per_unit = request.GET.get("min_price_per_unit", "")
	max_price_per_unit = request.GET.get("max_price_per_unit", "")
	productShowOnline = request.GET.get("product_show_online", "")
	productVerification = request.GET.get("product_verification", "")


	if productID != "" and productID != None:
		parameters["productsArr"] = getArrFromString(productID)

	if categoryID != "" and categoryID != None:
		parameters["categoriesArr"] = getArrFromString(categoryID)

	if fabric != "" and fabric != None:
		parameters["fabricArr"] = getStrArrFromString(fabric)

	if colour != "" and colour != None:
		parameters["colourArr"] = getStrArrFromString(colour)

	if productShowOnline != "" and validate_bool(productShowOnline):
		parameters["product_show_online"] = int(productShowOnline)

	if productVerification != "" and validate_bool(productVerification):
		parameters["product_verification"] = int(productVerification)

	if validate_number(min_price_per_unit) and validate_number(max_price_per_unit) and float(min_price_per_unit) >= 0 and float(max_price_per_unit) > float(min_price_per_unit):
		parameters["price_filter_applied"] = True
		parameters["min_price_per_unit"] = float(min_price_per_unit)
		parameters["max_price_per_unit"] = float(max_price_per_unit)

	productOrderBy = request.GET.get("product_order_by", "")
	if productOrderBy != "" and productOrderBy != None:
		parameters["product_order_by"] = productOrderBy

	return parameters


def populateProductDetailsParameters(request, parameters = {}, version = "0"):

	defaultValue = 1

	if version == "1":
		defaultValue = 0

	productDetails = request.GET.get("product_details", None)
	if validate_bool(productDetails):
		parameters["product_details"] = int(productDetails)
	else:
		parameters["product_details"] = defaultValue

	productDetailsDetails = request.GET.get("product_details_details", None)
	if validate_bool(productDetailsDetails):
		parameters["product_details_details"] = int(productDetailsDetails)
	else:
		parameters["product_details_details"] = defaultValue

	productLotDetails = request.GET.get("product_lot_details", None)
	if validate_bool(productLotDetails):
		parameters["product_lot_details"] = int(productLotDetails)
	else:
		parameters["product_lot_details"] = defaultValue

	productImageDetails = request.GET.get("product_image_details", None)
	if validate_bool(productImageDetails):
		parameters["product_image_details"] = int(productImageDetails)
	else:
		parameters["product_image_details"] = defaultValue

	categoryDetails = request.GET.get("category_details", None)
	if validate_bool(categoryDetails):
		parameters["category_details"] = int(categoryDetails)
	else:
		parameters["category_details"] = defaultValue

	parameters = populateSellerDetailsParameters(request, parameters, version)

	return parameters