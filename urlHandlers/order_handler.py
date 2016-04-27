from django.views.decorators.csrf import csrf_exempt

from orders.views import order
from scripts.utils import customResponse, get_token_payload
import jwt as JsonWebToken

@csrf_exempt
def order_details(request):

	if request.method == "GET":
		status = request.GET.get("status", "")
		sellerID = request.GET.get("sellerID", "")
		accessToken = request.GET.get("access_token", "")
		tokenPayload = get_token_payload(accessToken, "sellerID")
		if "sellerID" in tokenPayload and tokenPayload["sellerID"]!=None:
			sellersArr = [tokenPayload["sellerID"]]
		elif sellerID == "":
			sellersArr = []
		else:
			sellersArr = [int(e) if e.isdigit() else e for e in sellerID.split(",")]
		if status == "":
			statusArr = []
		else:
			statusArr = [int(e) if e.isdigit() else e for e in status.split(",")]
		return order.get_order_details(request,statusArr,sellersArr)
	elif request.method == "POST":
		return order.post_new_order(request)
	elif request.method == "PUT":
		return order.update_order(request)

	return customResponse("4XX", {"error": "Invalid request"})