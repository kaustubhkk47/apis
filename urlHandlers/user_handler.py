from django.views.decorators.csrf import csrf_exempt

from users.views import user, buyer, buyer
from scripts.utils import customResponse
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
		buyerID = request.GET.get("buyerID", "")
		if buyerID == "":
			buyersArr = []
		else:
			buyersArr = [int(e) if e.isdigit() else e for e in buyerID.split(",")]
		return buyer.get_buyer_details(request,buyersArr)
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
def buyer_details(request):

	if request.method == "GET":
		buyerID = request.GET.get("buyerID", "")
		if buyerID == "":
			buyersArr = []
		else:
			buyersArr = [int(e) if e.isdigit() else e for e in buyerID.split(",")]
		return buyer.get_buyer_details(request,buyersArr)
	elif request.method == "POST":
		return buyer.post_new_buyer(request)
	elif request.method == "PUT":
		return buyer.update_buyer(request)
	elif request.method == "DELETE":
		return buyer.delete_buyer(request)

	return customResponse("4XX", {"error": "Invalid request"})

@csrf_exempt
def buyer_login(request):

    response = {}
    if request.method == 'POST':
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')

        if not email or not password:
            return customResponse("4XX", {"error": "Either email or password was empty"})

        # if check_token(request)
        try:
            buyer = Buyer.objects.get(email=email)
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
        except Seller.DoesNotExist:
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
