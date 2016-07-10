from django.views.decorators.csrf import csrf_exempt

from users.views import user, buyer, seller, internaluser
from scripts.utils import customResponse, get_token_payload, getArrFromString, validate_bool, validate_integer, getPaginationParameters
from users.models.buyer import *
from users.serializers.buyer import *
from users.models.seller import *
from users.serializers.seller import *
from users.models.internalUser import *
from users.serializers.internalUser import *
import jwt as JsonWebToken

import settings

@csrf_exempt
def user_details(request, version = "0"):

	if request.method == "GET":
		return user.get_user_details(request)

	return customResponse("4XX", {"error": "Invalid request"})

@csrf_exempt
def buyer_details(request, version = "0"):

	if request.method == "GET":

		buyerParameters = populateBuyerParameters(request, {}, version)

		if buyerParameters["isBuyer"] == 0 and buyerParameters["isInternalUser"] == 0:
			return customResponse("4XX", {"error": "Authentication failure"})

		return buyer.get_buyer_details(request,buyerParameters)
	elif request.method == "POST":
		return buyer.post_new_buyer(request)
	elif request.method == "PUT":
		return buyer.update_buyer(request)
	elif request.method == "DELETE":
		return buyer.delete_buyer(request)

	return customResponse("4XX", {"error": "Invalid request"})

@csrf_exempt
def buyer_shared_product_id_details(request, version = "0"):

	if request.method == "GET":

		buyerParameters = populateBuyerParameters(request, {}, version)

		if buyerParameters["isBuyer"] == 0 and buyerParameters["isInternalUser"] == 0:
			return customResponse("4XX", {"error": "Authentication failure"})

		return buyer.get_buyer_shared_product_id_details(request,buyerParameters)
	elif request.method == "DELETE":
		return buyer.delete_buyer_shared_product_id(request)

	return customResponse("4XX", {"error": "Invalid request"})

@csrf_exempt
def buyer_interest_details(request, version = "0"):

	if request.method == "GET":

		buyerParameters = populateBuyerParameters(request, {}, version )

		if buyerParameters["isBuyer"] == 0 and buyerParameters["isInternalUser"] == 0:
			return customResponse("4XX", {"error": "Authentication failure"})

		return buyer.get_buyer_interest_details(request,buyerParameters)
	elif request.method == "POST":
		return buyer.post_new_buyer_interest(request)
	elif request.method == "PUT":
		return buyer.update_buyer_interest(request)
	elif request.method == "DELETE":
		return buyer.delete_buyer_interest(request)

	return customResponse("4XX", {"error": "Invalid request"})

@csrf_exempt
def buyer_product_details(request, version = "0"):

	if request.method == "GET":

		buyerParameters = populateBuyerProductParameters(request, {}, version )

		if buyerParameters["isBuyer"] == 0 and buyerParameters["isInternalUser"] == 0:
			return customResponse("4XX", {"error": "Authentication failure"})

		return buyer.get_buyer_product_details(request,buyerParameters)
	elif request.method == "POST":
		return buyer.post_new_buyer_product(request)
	elif request.method == "PUT":
		return buyer.update_buyer_product(request)
	#elif request.method == "DELETE":
	#	return buyer.delete_buyer_interest(request)

	return customResponse("4XX", {"error": "Invalid request"})

@csrf_exempt
def buyer_product_whatsapp_details(request, version = "0"):
	
	if request.method == "PUT":
		return buyer.update_buyer_product_whatsapp(request)

	return customResponse("4XX", {"error": "Invalid request"})

@csrf_exempt
def buyer_product_master_update(request,version = "0"):

	if request.method == "POST":
		return buyer.master_update_buyer_product(request)

	return customResponse("4XX", {"error": "Invalid request"})

def populateBuyerProductParameters(request, parameters = {}, version = "0"):

	parameters = populateBuyerParameters(request, parameters, version)

	isActive = request.GET.get("is_active", None)
	responded = request.GET.get("responded", None)
	buyerProductID = request.GET.get("buyerproductID", "")
	buyerInterestID = request.GET.get("buyerinterestID", "")
	productID = request.GET.get("productID", "")
	
	if validate_bool(isActive):
		parameters["buyer_product_is_active"] = int(isActive)

	if validate_integer(responded):
		parameters["responded"] = int(responded)

	if buyerProductID != "":
		parameters["buyerProductsArr"] = getArrFromString(buyerProductID)

	if buyerInterestID != "":
		parameters["buyerInterestArr"] = getArrFromString(buyerInterestID)

	if productID != "":
		parameters["productsArr"] = getArrFromString(productID)

	parameters = getPaginationParameters(request, parameters, 1, version)

	return parameters


def populateBuyerParameters(request, parameters = {}, version = "0"):

	parameters = populateBuyerIDParameters(request, parameters, version)

	parameters = populateInternalUserIDParameters(request, parameters, version)

	buyerInterestID = request.GET.get("buyerinterestID", "")
	buyersharedproductID = request.GET.get("buyersharedproductID", "")

	whatsappSharingActive = request.GET.get("whatsapp_sharing_active", None)
	if validate_bool(whatsappSharingActive):
		parameters["whatsapp_sharing_active"] = int(whatsappSharingActive)

	if buyerInterestID != "":
		parameters["buyerInterestArr"] = getArrFromString(buyerInterestID)

	if buyersharedproductID != "" and validate_integer(buyersharedproductID):
		parameters["buyersharedproductID"] = int(buyersharedproductID)

	parameters = populateBuyerDetailsParameters(request, parameters, version)

	return parameters

def populateBuyerDetailsParameters(request, parameters = {}, version = "0"):

	defaultValue = 1

	if version == "1":
		defaultValue = 0

	buyerDetails = request.GET.get("buyer_details", None)
	if validate_bool(buyerDetails):
		parameters["buyer_details"] = int(buyerDetails)
	else:
		parameters["buyer_details"] = defaultValue

	buyerDetailsDetails = request.GET.get("buyer_details_details", None)
	if validate_bool(buyerDetailsDetails):
		parameters["buyer_details_details"] = int(buyerDetailsDetails)
	else:
		parameters["buyer_details_details"] = defaultValue

	buyerAddressDetails = request.GET.get("buyer_address_details", None)
	if validate_bool(buyerAddressDetails):
		parameters["buyer_address_details"] = int(buyerAddressDetails)
	else:
		parameters["buyer_address_details"] = defaultValue

	buyerInterestDetails = request.GET.get("buyer_interest_details", None)
	if validate_bool(buyerInterestDetails):
		parameters["buyer_interest_details"] = int(buyerInterestDetails)
	else:
		parameters["buyer_interest_details"] = defaultValue

	buyerProductDetails = request.GET.get("buyer_product_details", None)
	buyerProductCount = request.GET.get("buyer_product_count", None)
	if validate_bool(buyerProductDetails):
		parameters["buyer_product_details"] = int(buyerProductDetails)
		parameters["product_image_details"] = 1
		try:
			parameters["buyer_product_count"] = int(buyerProductCount)
		except Exception as e:
			parameters["buyer_product_count"] = 10
	else:
		parameters["buyer_product_details"] = 0

	return parameters

@csrf_exempt
def buyer_address_details(request, version = "0"):

	
	if request.method == "POST":
		return buyer.post_new_buyer(request)
	elif request.method == "PUT":
		return buyer.update_buyer(request)
	elif request.method == "DELETE":
		return buyer.delete_buyer(request)

	return customResponse("4XX", {"error": "Invalid request"})

def populateSellerDetailsParameters(request, parameters = {}, version = "0"):

	defaultValue = 1

	if version == "1":
		defaultValue = 0

	sellerDetails = request.GET.get("seller_details", None)
	if validate_bool(sellerDetails):
		parameters["seller_details"] = int(sellerDetails)
	else:
		parameters["seller_details"] = defaultValue

	sellerDetailsDetails = request.GET.get("seller_details_details", None)
	if validate_bool(sellerDetailsDetails):
		parameters["seller_details_details"] = int(sellerDetailsDetails)
	else:
		parameters["seller_details_details"] = defaultValue

	sellerAddressDetails = request.GET.get("seller_address_details", None)
	if validate_bool(sellerAddressDetails):
		parameters["seller_address_details"] = int(sellerAddressDetails)
	else:
		parameters["seller_address_details"] = defaultValue

	sellerBankDetails = request.GET.get("seller_bank_details", None)
	if validate_bool(sellerBankDetails):
		parameters["seller_bank_details"] = int(sellerBankDetails)
	else:
		parameters["seller_bank_details"] = defaultValue

	return parameters

def populateAllUserIDParameters(request, parameters = {}, version = "0"):

	parameters = populateBuyerIDParameters(request, parameters, version)

	parameters = populateSellerIDParameters(request, parameters, version)

	parameters = populateInternalUserIDParameters(request, parameters, version)

	return parameters

def populateBuyerIDParameters(request, parameters = {}, version = "0"):

	accessToken = request.GET.get("access_token", "")

	buyerID = request.GET.get("buyerID", "")
	tokenPayload = get_token_payload(accessToken, "buyerID")
	parameters["isBuyer"] = 0
	if "buyerID" in tokenPayload and tokenPayload["buyerID"]!=None:
		parameters["buyersArr"] = [tokenPayload["buyerID"]]
		parameters["isBuyer"] = 1
	elif buyerID != "":
		parameters["buyersArr"] = getArrFromString(buyerID)

	return parameters

def populateSellerIDParameters(request, parameters = {}, version = "0"):

	accessToken = request.GET.get("access_token", "")

	sellerID = request.GET.get("sellerID", "")
	tokenPayload = get_token_payload(accessToken, "sellerID")
	parameters["isSeller"] = 0
	if "sellerID" in tokenPayload and tokenPayload["sellerID"]!=None:
		parameters["sellersArr"] = [tokenPayload["sellerID"]]
		parameters["isSeller"] = 1
	elif sellerID != "":
		parameters["sellersArr"] = getArrFromString(sellerID)

	return parameters

def populateInternalUserIDParameters(request, parameters = {}, version = "0"):
	accessToken = request.GET.get("access_token", "")
	tokenPayload = get_token_payload(accessToken, "internaluserID")
	internalUserID = request.GET.get("internaluserID", "")

	parameters["isInternalUser"] = 0
	if "internaluserID" in tokenPayload and tokenPayload["internaluserID"]!=None:
		parameters["internalusersArr"] = [tokenPayload["internaluserID"]]
		parameters["isInternalUser"] = 1
	elif internalUserID != "":
		parameters["internalusersArr"] = getArrFromString(internalUserID)

	return parameters

@csrf_exempt
def seller_details(request, version = "0"):

	if request.method == "GET":

		parameters = populateSellerParameters(request, {}, version)
		
		if parameters["isSeller"] == 0 and parameters["isInternalUser"] == 0:
			return customResponse("4XX", {"error": "Authentication failure"})

		return seller.get_seller_details(request,parameters)
	elif request.method == "POST":
		return seller.post_new_seller(request)
	elif request.method == "PUT":
		return seller.update_seller(request)
	elif request.method == "DELETE":
		return seller.delete_seller(request)

	return customResponse("4XX", {"error": "Invalid request"})

@csrf_exempt
def internal_user_details(request, version = "0"):

	if request.method == "GET":

		parameters = populateInternalUserIDParameters(request, {}, version)
		
		#if parameters["isInternalUser"] == 0:
		#	return customResponse("4XX", {"error": "Authentication failure"})

		return internaluser.get_internal_user_details(request,parameters)

	return customResponse("4XX", {"error": "Invalid request"})

def populateSellerParameters(request, parameters = {}, version = "0"):

	parameters = populateSellerIDParameters(request, parameters, version)

	parameters = populateInternalUserIDParameters(request, parameters, version)
	
	parameters = populateSellerDetailsParameters(request, parameters, version)

	return parameters

@csrf_exempt
def buyer_login(request, version = "0"):

	response = {}
	if request.method == 'POST':
		mobile_number = request.POST.get('mobile_number', '')
		password = request.POST.get('password', '')

		if not mobile_number or not password:
			return customResponse("4XX", {"error": "Either mobile number or password was empty"})

		# if check_token(request)
		try:
			buyer = Buyer.objects.get(mobile_number=mobile_number)
		except Buyer.DoesNotExist:
			return customResponse("4XX", {"error": "Invalid buyer credentials"})

		if password == buyer.password:
			tokenPayload = {
				"user": "buyer",
				"buyerID": buyer.id,
			}

			encoded = JsonWebToken.encode(tokenPayload, settings.SECRET_KEY, algorithm='HS256')
			response = {
				"token": encoded.decode("utf-8"),
				"buyer": serialize_buyer(buyer)
			}
			return customResponse("2XX", response)
		else:
			return customResponse("4XX", {"error": "Invalid buyer credentials"})

	return customResponse("4XX", {"error": "Invalid request"})

@csrf_exempt
def seller_login(request, version = "0"):

	response = {}
	if request.method == 'POST':
		email = request.POST.get('email', '')
		password = request.POST.get('password', '')

		if not email or not password:
			return customResponse("4XX", {"error": "Either email or password was empty"})

		# if check_token(request)
		try:
			seller = Seller.objects.get(email=email)
		except Seller.DoesNotExist:
			return customResponse("4XX", {"error": "Invalid seller credentials"})

		if password == seller.password:
			tokenPayload = {
				"user": "seller",
				"sellerID": seller.id,
			}

			encoded = JsonWebToken.encode(tokenPayload, settings.SECRET_KEY, algorithm='HS256')
			response = {
				"token": encoded.decode("utf-8"),
				"seller": serialize_seller(seller)
			}
			return customResponse("2XX", response)
		else:
			return customResponse("4XX", {"error": "Invalid seller credentials"})

	return customResponse("4XX", {"error": "Invalid request"})


@csrf_exempt
def internaluser_login(request, version = "0"):

	response = {}
	if request.method == 'POST':
		email = request.POST.get('email', '')
		password = request.POST.get('password', '')

		if not email or not password:
			return customResponse("4XX", {"error": "Either email or password was empty"})

		# if check_token(request)
		try:
			internaluser = InternalUser.objects.get(email=email)
		except InternalUser.DoesNotExist:
			return customResponse("4XX", {"error": "Invalid internaluser credentials"})

		if password == internaluser.password:
			tokenPayload = {
				"user": "internaluser",
				"internaluserID": internaluser.id,
			}

			encoded = JsonWebToken.encode(tokenPayload, settings.SECRET_KEY, algorithm='HS256')
			response = {
				"token": encoded.decode("utf-8"),
				"internaluser": serialize_internaluser(internaluser)
			}
			return customResponse("2XX", response)
		else:
			return customResponse("4XX", {"error": "Invalid internaluser credentials"})

	return customResponse("4XX", {"error": "Invalid request"})