from django.views.decorators.csrf import csrf_exempt

from users.views import user, buyer, seller, internaluser, businesstype
from scripts.utils import customResponse, get_token_payload, getArrFromString, validate_bool, validate_integer, getPaginationParameters, convert_keys_to_string, getApiVersion
from users.models.buyer import *
from users.serializers.buyer import *
from users.models.seller import *
from users.serializers.seller import *
from users.models.internalUser import *
from users.serializers.internalUser import *
import jwt as JsonWebToken

import settings


### ALL USERS
@csrf_exempt
def user_details(request, version = "0"):

	version = getApiVersion(request.META["HTTP_ACCEPT"])

	parameters = populateAllUserIDParameters(request, {}, version)

	if request.method == "GET":
		if parameters["isBuyer"] == 0 and parameters["isInternalUser"] == 0 and parameters["isSeller"]:
			return customResponse("4XX", {"error": "Authentication failure"})

		return user.get_user_details(request)

	return customResponse("4XX", {"error": "Invalid request"})

def populateAllUserIDParameters(request, parameters = {}, version = "0"):

	parameters = populateBuyerIDParameters(request, parameters, version)

	parameters = populateSellerIDParameters(request, parameters, version)

	parameters = populateInternalUserIDParameters(request, parameters, version)

	return parameters

### BUYER

@csrf_exempt
def buyer_details(request, version = "0"):

	version = getApiVersion(request.META["HTTP_ACCEPT"])

	parameters = populateBuyerProductParameters(request, {}, version)

	if request.method == "GET":

		if parameters["isBuyer"] == 0 and parameters["isInternalUser"] == 0 and parameters["isBuyerStore"] == 0:
			return customResponse("4XX", {"error": "Authentication failure"})

		return buyer.get_buyer_details(request,parameters)
	elif request.method == "POST":
		return buyer.post_new_buyer(request)
	elif request.method == "PUT":

		if parameters["isBuyer"] == 0 and parameters["isInternalUser"] == 0:
			return customResponse("4XX", {"error": "Authentication failure"})

		return buyer.update_buyer(request, parameters)
	elif request.method == "DELETE":

		if parameters["isInternalUser"] == 0:
			return customResponse("4XX", {"error": "Authentication failure"})

		return buyer.delete_buyer(request, parameters)

	return customResponse("4XX", {"error": "Invalid request"})

@csrf_exempt
def buyer_panel_tracking_details(request, version = "0"):

	version = getApiVersion(request.META["HTTP_ACCEPT"])

	parameters = populateBuyerParameters(request, {}, version)

	if request.method == "POST":
		if parameters["isBuyer"] == 0:
			return customResponse("4XX", {"error": "Authentication failure"})
		return buyer.post_new_buyer_panel_tracking(request, parameters)

	return customResponse("4XX", {"error": "Invalid request"})

@csrf_exempt
def buyer_store_lead_details(request, version = "0"):

	version = getApiVersion(request.META["HTTP_ACCEPT"])

	parameters = populateBuyerStoreParameters(request, {}, version)

	if request.method == "GET":

		if parameters["isBuyer"] == 0 and parameters["isInternalUser"] == 0:
			return customResponse("4XX", {"error": "Authentication failure"})

		return buyer.get_buyer_store_lead_details(request,parameters)
	elif request.method == "POST":

		if parameters["isBuyer"] == 0 and parameters["isInternalUser"] == 0 and parameters["isBuyerStore"] == 0:
			return customResponse("4XX", {"error": "Authentication failure"})

		return buyer.post_new_buyer_store_lead(request, parameters)
	elif request.method == "PUT":

		if parameters["isBuyer"] == 0 and parameters["isInternalUser"] == 0:
			return customResponse("4XX", {"error": "Authentication failure"})
		return buyer.update_buyer_store_lead(request,parameters)

	return customResponse("4XX", {"error": "Invalid request"})

def populateBuyerStoreParameters(request, parameters = {}, version = "0"):

	parameters = populateBuyerProductParameters(request, parameters, version)

	buyerStoreLeadID = request.GET.get("buyerstoreleadID", "")
	if buyerStoreLeadID != "":
		parameters["buyerStoreLeadsArr"] = getArrFromString(buyerStoreLeadID)

	buyerStoreLeadStatus = request.GET.get("buyer_store_lead_status", None)
	if buyerStoreLeadStatus:
		parameters["buyer_store_lead_status"] = getArrFromString(buyerStoreLeadStatus)

	return parameters



def populateBuyerParameters(request, parameters = {}, version = "0"):

	parameters = populateBuyerIDParameters(request, parameters, version)

	parameters = populateInternalUserIDParameters(request, parameters, version)

	buyerInterestID = request.GET.get("buyerinterestID", "")
	

	whatsappSharingActive = request.GET.get("whatsapp_sharing_active", None)
	if validate_bool(whatsappSharingActive):
		parameters["whatsapp_sharing_active"] = int(whatsappSharingActive)

	testBuyer = request.GET.get("test_buyer", None)
	if validate_bool(testBuyer):
		parameters["test_buyer"] = int(testBuyer)

	if buyerInterestID != "":
		parameters["buyerInterestArr"] = getArrFromString(buyerInterestID)

	buyersharedproductID = request.GET.get("buyersharedproductID", "")
	if buyersharedproductID != "" and validate_integer(buyersharedproductID):
		parameters["buyersharedproductID"] = int(buyersharedproductID)

	buyerMinID = request.GET.get("buyer_min_ID", "")
	if buyerMinID != "" and validate_integer(buyerMinID):
		parameters["buyer_min_ID"] = int(buyerMinID)

	buyerMaxID = request.GET.get("buyer_max_ID", "")
	if buyerMaxID != "" and validate_integer(buyerMaxID):
		parameters["buyer_max_ID"] = int(buyerMaxID)

	buyerPurchasingStateID = request.GET.get("buyerpurchasingstateID", "")
	if buyerPurchasingStateID != "":
		parameters["buyerPurchasingStateArr"] = getArrFromString(buyerPurchasingStateID)

	parameters = populateBuyerDetailsParameters(request, parameters, version)

	return parameters

@csrf_exempt
def buyer_purchasing_state_details(request, version = "0"):

	version = getApiVersion(request.META["HTTP_ACCEPT"])

	parameters = populateBuyerParameters(request, {}, version)

	if request.method == "GET":

		if parameters["isBuyer"] == 0 and parameters["isInternalUser"] == 0:
			return customResponse("4XX", {"error": "Authentication failure"})

		return buyer.get_buyer_purchasing_state_details(request,parameters)
	elif request.method == "POST":

		if parameters["isInternalUser"] == 0:
			return customResponse("4XX", {"error": "Authentication failure"})

		return buyer.post_new_buyer_purchasing_state(request, parameters)
	#elif request.method == "PUT":
	#	return buyer.update_buyer_purchasing_state(request)
	elif request.method == "DELETE":

		if parameters["isInternalUser"] == 0:
			return customResponse("4XX", {"error": "Authentication failure"})
		return buyer.delete_buyer_purchasing_state(request, parameters)

	return customResponse("4XX", {"error": "Invalid request"})

@csrf_exempt
def buyer_buys_from_details(request, version = "0"):

	version = getApiVersion(request.META["HTTP_ACCEPT"])

	parameters = populateBuyerParameters(request, {}, version)

	if request.method == "GET":

		if parameters["isBuyer"] == 0 and parameters["isInternalUser"] == 0:
			return customResponse("4XX", {"error": "Authentication failure"})

		return buyer.get_buyer_buys_from_details(request,parameters)
	elif request.method == "POST":

		if parameters["isInternalUser"] == 0:
			return customResponse("4XX", {"error": "Authentication failure"})

		return buyer.post_new_buyer_buys_from(request, parameters)
	#elif request.method == "PUT":
	#	return buyer.update_buyer_purchasing_state(request)
	elif request.method == "DELETE":

		if parameters["isInternalUser"] == 0:
			return customResponse("4XX", {"error": "Authentication failure"})

		return buyer.delete_buyer_buys_from(request, parameters)

	return customResponse("4XX", {"error": "Invalid request"})


@csrf_exempt
def buyer_access_token_details(request, version = "0"):

	version = getApiVersion(request.META["HTTP_ACCEPT"])

	if request.method == "GET":
		parameters = {}
		parameters["buyer_panel_url"] = request.GET.get("buyer_panel_url", "")

		return buyer.get_buyer_access_token_details(request, parameters)

	return customResponse("4XX", {"error": "Invalid request"})

@csrf_exempt
def buyer_shared_product_id_details(request, version = "0"):

	version = getApiVersion(request.META["HTTP_ACCEPT"])

	parameters = populateBuyerParameters(request, {}, version)

	if request.method == "GET":

		if parameters["isBuyer"] == 0 and parameters["isInternalUser"] == 0:
			return customResponse("4XX", {"error": "Authentication failure"})

		return buyer.get_buyer_shared_product_id_details(request,parameters)
	elif request.method == "DELETE":

		if parameters["isBuyer"] == 0 and parameters["isInternalUser"] == 0:
			return customResponse("4XX", {"error": "Authentication failure"})

		return buyer.delete_buyer_shared_product_id(request, parameters)

	return customResponse("4XX", {"error": "Invalid request"})

@csrf_exempt
def buyer_interest_details(request, version = "0"):

	version = getApiVersion(request.META["HTTP_ACCEPT"])

	parameters = populateBuyerParameters(request, {}, version )

	if request.method == "GET":

		if parameters["isBuyer"] == 0 and parameters["isInternalUser"] == 0:
			return customResponse("4XX", {"error": "Authentication failure"})

		return buyer.get_buyer_interest_details(request,parameters)
	elif request.method == "POST":
		if parameters["isBuyer"] == 0 and parameters["isInternalUser"] == 0:
			return customResponse("4XX", {"error": "Authentication failure"})
		return buyer.post_new_buyer_interest(request, parameters)
	elif request.method == "PUT":
		if parameters["isBuyer"] == 0 and parameters["isInternalUser"] == 0:
			return customResponse("4XX", {"error": "Authentication failure"})
		return buyer.update_buyer_interest(request, parameters)
	#elif request.method == "DELETE":
	#	if parameters["isBuyer"] == 0 and parameters["isInternalUser"] == 0:
	#		return customResponse("4XX", {"error": "Authentication failure"})
	#	return buyer.delete_buyer_interest(request, parameters)

	return customResponse("4XX", {"error": "Invalid request"})

@csrf_exempt
def buyer_product_details(request, version = "0"):

	version = getApiVersion(request.META["HTTP_ACCEPT"])

	parameters = populateBuyerProductParameters(request, {}, version )

	if request.method == "GET":

		if parameters["isBuyer"] == 0 and parameters["isInternalUser"] == 0 and parameters["isBuyerStore"] == 0:
			return customResponse("4XX", {"error": "Authentication failure"})

		return buyer.get_buyer_product_details(request,parameters)
	elif request.method == "POST":
		if parameters["isBuyer"] == 0 and parameters["isInternalUser"] == 0:
			return customResponse("4XX", {"error": "Authentication failure"})
		return buyer.post_new_buyer_product(request, parameters)
	elif request.method == "PUT":
		if parameters["isBuyer"] == 0 and parameters["isInternalUser"] == 0:
			return customResponse("4XX", {"error": "Authentication failure"})
		return buyer.update_buyer_product(request, parameters)
	#elif request.method == "DELETE":
	#	return buyer.delete_buyer_interest(request)

	return customResponse("4XX", {"error": "Invalid request"})

@csrf_exempt
def buyer_product_response_details(request, version = "0"):

	version = getApiVersion(request.META["HTTP_ACCEPT"])

	parameters = populateBuyerProductParameters(request, {}, version )

	if request.method == "GET":

		if parameters["isBuyer"] == 0 and parameters["isInternalUser"] == 0 and parameters["isBuyerStore"] == 0:
			return customResponse("4XX", {"error": "Authentication failure"})

		return buyer.get_buyer_product_response_details(request,parameters)

	elif request.method == "PUT":

		if parameters["isBuyer"] == 0 and parameters["isInternalUser"] == 0:
			return customResponse("4XX", {"error": "Authentication failure"})

		return buyer.update_buyer_product_response(request,parameters)
	

	return customResponse("4XX", {"error": "Invalid request"})

@csrf_exempt
def buyer_product_whatsapp_details(request, version = "0"):

	version = getApiVersion(request.META["HTTP_ACCEPT"])

	parameters = populateBuyerProductParameters(request, {}, version )
	
	if request.method == "PUT":
		if parameters["isBuyer"] == 0 and parameters["isInternalUser"] == 0:
			return customResponse("4XX", {"error": "Authentication failure"})
		return buyer.update_buyer_product_whatsapp(request, parameters)

	return customResponse("4XX", {"error": "Invalid request"})

@csrf_exempt
def buyer_product_landing_details(request, version = "0"):

	version = getApiVersion(request.META["HTTP_ACCEPT"])
	
	if request.method == "POST":
		return buyer.post_buyer_product_landing(request)

	return customResponse("4XX", {"error": "Invalid request"})

@csrf_exempt
def buyer_product_master_update(request,version = "0"):

	version = getApiVersion(request.META["HTTP_ACCEPT"])

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
	landing = request.GET.get("landing", "")
	
	if validate_bool(isActive):
		parameters["buyer_product_is_active"] = int(isActive)

	if validate_bool(landing):
		parameters["buyer_product_landing"] = int(landing)

	if validate_integer(responded):
		parameters["responded"] = int(responded)

	if buyerProductID != "":
		parameters["buyerProductsArr"] = getArrFromString(buyerProductID)

	if buyerInterestID != "":
		parameters["buyerInterestArr"] = getArrFromString(buyerInterestID)

	if productID != "":
		parameters["productsArr"] = getArrFromString(productID)

	parameters = getPaginationParameters(request, parameters, 1, version)

	from .catalog_handler import populateProductDetailsParameters

	parameters = populateProductDetailsParameters(request, parameters, version)

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

	buyerPurchasingStateDetails = request.GET.get("buyer_purchasing_state_details", None)
	if validate_bool(buyerPurchasingStateDetails):
		parameters["buyer_purchasing_state_details"] = int(buyerPurchasingStateDetails)
	else:
		parameters["buyer_purchasing_state_details"] = 0

	buyerBuysFromDetails = request.GET.get("buyer_buys_from_details", None)
	if validate_bool(buyerBuysFromDetails):
		parameters["buyer_buys_from_details"] = int(buyerBuysFromDetails)
	else:
		parameters["buyer_buys_from_details"] = 0

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

	version = getApiVersion(request.META["HTTP_ACCEPT"])

	buyerParameters = populateBuyerParameters(request, {}, version )
	"""
	if request.method == "POST":
		if buyerParameters["isBuyer"] == 0 and buyerParameters["isInternalUser"] == 0:
			return customResponse("4XX", {"error": "Authentication failure"})
		return buyer.post_new_buyer(request)
	elif request.method == "PUT":
		if buyerParameters["isBuyer"] == 0 and buyerParameters["isInternalUser"] == 0:
			return customResponse("4XX", {"error": "Authentication failure"})
		return buyer.update_buyer(request)
	elif request.method == "DELETE":
		if buyerParameters["isBuyer"] == 0 and buyerParameters["isInternalUser"] == 0:
			return customResponse("4XX", {"error": "Authentication failure"})
		return buyer.delete_buyer(request)
	"""

	return customResponse("4XX", {"error": "Invalid request"})

def populateBuyerIDParameters(request, parameters = {}, version = "0"):

	accessToken = request.GET.get("access_token", "")

	buyerID = request.GET.get("buyerID", "")
	tokenPayload = convert_keys_to_string(get_token_payload(accessToken, "buyerID"))
	parameters["isBuyer"] = 0
	parameters["isBuyerStore"] = 0
	if "buyerID" in tokenPayload and tokenPayload["buyerID"]!=None:
		parameters["buyersArr"] = [tokenPayload["buyerID"]]
		parameters["isBuyer"] = 1
	elif buyerID != "":
		parameters["buyersArr"] = getArrFromString(buyerID)

	storeUrl = request.GET.get("store_url", "")
	try:
		buyerPtr = Buyer.objects.get(store_url=storeUrl)
	except Exception as e:
		pass
	else:
		parameters["buyersArr"] = [buyerPtr.id]
		parameters["isBuyerStore"] = 1

	return parameters

### SELLER

@csrf_exempt
def seller_details(request, version = "0"):

	version = getApiVersion(request.META["HTTP_ACCEPT"])

	parameters = populateSellerParameters(request, {}, version)

	if request.method == "GET":

		if parameters["isSeller"] == 0 and parameters["isInternalUser"] == 0:
			return customResponse("4XX", {"error": "Authentication failure"})

		return seller.get_seller_details(request,parameters)
	elif request.method == "POST":
		return seller.post_new_seller(request)
	elif request.method == "PUT":
		if parameters["isSeller"] == 0 and parameters["isInternalUser"] == 0:
			return customResponse("4XX", {"error": "Authentication failure"})
		return seller.update_seller(request)
	elif request.method == "DELETE":
		if parameters["isSeller"] == 0 and parameters["isInternalUser"] == 0:
			return customResponse("4XX", {"error": "Authentication failure"})
		return seller.delete_seller(request)

	return customResponse("4XX", {"error": "Invalid request"})

def populateSellerParameters(request, parameters = {}, version = "0"):

	parameters = populateSellerIDParameters(request, parameters, version)

	parameters = populateInternalUserIDParameters(request, parameters, version)
	
	parameters = populateSellerDetailsParameters(request, parameters, version)

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

### BUSINESS TYPE

@csrf_exempt
def business_type_details(request, version = "0"):

	version = getApiVersion(request.META["HTTP_ACCEPT"])

	if request.method == "GET":

		parameters = populateBusinessTypeParameters(request, {}, version)
		
		return businesstype.get_business_type_details(request,parameters)

	return customResponse("4XX", {"error": "Invalid request"})

def populateBusinessTypeParameters(request, parameters = {}, version = "0"):

	canBuyerBuyFrom = request.GET.get("can_buyer_buy_from", None)
	if validate_bool(canBuyerBuyFrom):
		parameters["can_buyer_buy_from"] = int(canBuyerBuyFrom)

	canBeBuyer = request.GET.get("can_be_buyer", None)
	if validate_bool(canBeBuyer):
		parameters["can_be_buyer"] = int(canBeBuyer)

	canBeSeller = request.GET.get("can_be_seller", None)
	if validate_bool(canBeSeller):
		parameters["can_be_seller"] = int(canBeSeller)

	return parameters

### INTERNAL USER

@csrf_exempt
def internal_user_details(request, version = "0"):

	version = getApiVersion(request.META["HTTP_ACCEPT"])

	if request.method == "GET":

		parameters = populateInternalUserIDParameters(request, {}, version)
		
		#if parameters["isInternalUser"] == 0:
		#	return customResponse("4XX", {"error": "Authentication failure"})

		return internaluser.get_internal_user_details(request,parameters)

	return customResponse("4XX", {"error": "Invalid request"})

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

### LOGIN - BUYER

@csrf_exempt
def buyer_login(request, version = "0"):

	version = getApiVersion(request.META["HTTP_ACCEPT"])

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
			response = {
				"token": getBuyerToken(buyer),
				"buyer": serialize_buyer(buyer)
			}
			return customResponse("2XX", response)
		else:
			return customResponse("4XX", {"error": "Invalid buyer credentials"})

	return customResponse("4XX", {"error": "Invalid request"})

### LOGIN - SELLER

@csrf_exempt
def seller_login(request, version = "0"):

	version = getApiVersion(request.META["HTTP_ACCEPT"])

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
			return customResponse("4XX", {"error": "Invalid email"})

		if password == seller.password:
			response = {
				"token": getSellerToken(seller),
				"seller": serialize_seller(seller)
			}
			return customResponse("2XX", response)
		else:
			return customResponse("4XX", {"error": "Invalid password"})

	return customResponse("4XX", {"error": "Invalid request"})

### LOGIN - INTERNAL USER

@csrf_exempt
def internaluser_login(request, version = "0"):

	version = getApiVersion(request.META["HTTP_ACCEPT"])

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
			response = {
				"token": getInternalUserToken(internaluser),
				"internaluser": serialize_internaluser(internaluser)
			}
			return customResponse("2XX", response)
		else:
			return customResponse("4XX", {"error": "Invalid internaluser credentials"})

	return customResponse("4XX", {"error": "Invalid request"})