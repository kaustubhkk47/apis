from django.views.decorators.csrf import csrf_exempt

from users.views import user, buyer, seller
from scripts.utils import customResponse

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
def seller_details(request):

	if request.method == "GET":
		sellerID = request.GET.get("sellerID", "")
		if sellerID == "":
			sellersArr = []
		else:
			sellersArr = [int(e) if e.isdigit() else e for e in sellerID.split(",")]
		return seller.get_seller_details(request,sellersArr)
	elif request.method == "POST":
		return seller.post_new_seller(request)
	elif request.method == "PUT":
		return seller.update_seller(request)
	elif request.method == "DELETE":
		return seller.delete_seller(request)

	return customResponse("4XX", {"error": "Invalid request"})	
