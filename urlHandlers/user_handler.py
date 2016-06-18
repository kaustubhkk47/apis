from django.views.decorators.csrf import csrf_exempt

from users.views import user, buyer, seller
from scripts.utils import customResponse, get_token_payload
from users.models.buyer import *
from users.serializers.buyer import *
from users.models.seller import *
from users.serializers.seller import *
from users.models.internalUser import *
from users.serializers.internalUser import *
import jwt as JsonWebToken

import settings

@csrf_exempt
def user_details(request):

	if request.method == "GET":
		return user.get_user_details(request)

	return customResponse("4XX", {"error": "Invalid request"})

@csrf_exempt
def buyer_details(request):

	if request.method == "GET":

		buyerParameters = {}

		buyerID = request.GET.get("buyerID", "")
		accessToken = request.GET.get("access_token", "")
		
		tokenPayload = get_token_payload(accessToken, "buyerID")
		buyerParameters["isBuyer"] = 0
		if "buyerID" in tokenPayload and tokenPayload["buyerID"]!=None:
			buyerParameters["buyersArr"] = [tokenPayload["buyerID"]]
			buyerParameters["isBuyer"] = 1
		elif buyerID != "":
			buyerParameters["buyersArr"] = [int(e) if e.isdigit() else e for e in buyerID.split(",")]

		tokenPayload = get_token_payload(accessToken, "internaluserID")
		buyerParameters["isInternalUser"] = 0
		if "internaluserID" in tokenPayload and tokenPayload["internaluserID"]!=None:
			buyerParameters["internalusersArr"] = [tokenPayload["internaluserID"]]
			buyerParameters["isInternalUser"] = 1

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
def buyer_address_details(request):

	
	if request.method == "POST":
		return buyer.post_new_buyer(request)
	elif request.method == "PUT":
		return buyer.update_buyer(request)
	elif request.method == "DELETE":
		return buyer.delete_buyer(request)

	return customResponse("4XX", {"error": "Invalid request"})	

@csrf_exempt
def seller_details(request):

	if request.method == "GET":
		
		sellerParameters = {}

		sellerID = request.GET.get("sellerID", "")
		accessToken = request.GET.get("access_token", "")
		
		tokenPayload = get_token_payload(accessToken, "sellerID")
		sellerParameters["isSeller"] = 0
		if "sellerID" in tokenPayload and tokenPayload["sellerID"]!=None:
			sellerParameters["sellersArr"] = [tokenPayload["sellerID"]]
			sellerParameters["isSeller"] = 1
		elif sellerID != "":
			sellerParameters["sellersArr"] = [int(e) if e.isdigit() else e for e in sellerID.split(",")]

		tokenPayload = get_token_payload(accessToken, "internaluserID")
		sellerParameters["isInternalUser"] = 0
		if "internaluserID" in tokenPayload and tokenPayload["internaluserID"]!=None:
			sellerParameters["internalusersArr"] = [tokenPayload["internaluserID"]]
			sellerParameters["isInternalUser"] = 1

		if sellerParameters["isSeller"] == 0 and sellerParameters["isInternalUser"] == 0:
			return customResponse("4XX", {"error": "Authentication failure"})

		return seller.get_seller_details(request,sellerParameters)
	elif request.method == "POST":
		return seller.post_new_seller(request)
	elif request.method == "PUT":
		return seller.update_seller(request)
	elif request.method == "DELETE":
		return seller.delete_seller(request)

	return customResponse("4XX", {"error": "Invalid request"})

@csrf_exempt
def buyer_login(request):

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
def seller_login(request):

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
def internaluser_login(request):

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
