from django.views.decorators.csrf import csrf_exempt

from users.views import user, buyer, seller

@csrf_exempt
def user_details(request):

	if request.method == "GET":
		return user.get_user_details(request)

	return customResponse("4XX", {"error": "Invalid request"})

@csrf_exempt
def buyer_details(request, buyerID = ""):

	if request.method == "GET":
		buyerID = request.GET.get("buyerID", "")
		if buyerID == "":
			buyersArr = []
		else:
			buyersArr = [int(e) if e.isdigit() else e for e in buyerID.split(",")]
		return buyer.get_buyer_details(request,buyersArr)
	elif request.method == "POST":
		return buyer.post_new_buyer(request)

	return customResponse("4XX", {"error": "Invalid request"})	

@csrf_exempt
def seller_details(request, sellerID = ""):

	if request.method == "GET":
		sellerID = request.GET.get("sellerID", "")
		if sellerID == "":
			sellersArr = []
		else:
			sellersArr = [int(e) if e.isdigit() else e for e in sellerID.split(",")]
		return seller.get_seller_details(request,sellersArr)

	return customResponse("4XX", {"error": "Invalid request"})	
