from django.views.decorators.csrf import csrf_exempt

from orders.views import order
from scripts.utils import customResponse, get_token_payload
import jwt as JsonWebToken

@csrf_exempt
def order_shipment_details(request):

	if request.method == "GET":

		orderShipmentParameters = {}

		status = request.GET.get("status", "")
		sellerID = request.GET.get("sellerID", "")
		orderShipmentID = request.GET.get("ordershipmentID", "")
		accessToken = request.GET.get("access_token", "")

		tokenPayload = get_token_payload(accessToken, "sellerID")
		orderShipmentParameters["isSeller"] = 0
		if "sellerID" in tokenPayload and tokenPayload["sellerID"]!=None:
			orderShipmentParameters["sellersArr"] = [tokenPayload["sellerID"]]
			orderShipmentParameters["isSeller"] = 1
		elif sellerID != "":
			orderShipmentParameters["sellersArr"] = [int(e) if e.isdigit() else e for e in sellerID.split(",")]

		tokenPayload = get_token_payload(accessToken, "internaluserID")
		orderShipmentParameters["isInternalUser"] = 0
		if "internaluserID" in tokenPayload and tokenPayload["internaluserID"]!=None:
			orderShipmentParameters["internalusersArr"] = [tokenPayload["internaluserID"]]
			orderShipmentParameters["isInternalUser"] = 1

		if status != "":
			orderShipmentParameters["statusArr"] = [int(e) if e.isdigit() else e for e in status.split(",")]

		if orderShipmentID != "":
			orderShipmentParameters["orderShipmentArr"] = [int(e) if e.isdigit() else e for e in orderShipmentID.split(",")]

		if orderShipmentParameters["isSeller"] == 0 and orderShipmentParameters["isInternalUser"] == 0:
			return customResponse("4XX", {"error": "Authentication failure"})

		return order.get_order_shipment_details(request,orderShipmentParameters)
	elif request.method == "POST":
		return order.post_new_order_shipment(request)
	elif request.method == "PUT":
		return order.update_order_shipment(request)

	return customResponse("4XX", {"error": "Invalid request"})

@csrf_exempt
def suborder_details(request):

	if request.method == "GET":

		subOrderParameters = {}

		status = request.GET.get("status", "")
		sellerID = request.GET.get("sellerID", "")
		subOrderID = request.GET.get("suborderID", "")
		accessToken = request.GET.get("access_token", "")

		tokenPayload = get_token_payload(accessToken, "sellerID")
		subOrderParameters["isSeller"] = 0
		if "sellerID" in tokenPayload and tokenPayload["sellerID"]!=None:
			subOrderParameters["sellersArr"] = [tokenPayload["sellerID"]]
			subOrderParameters["isSeller"] = 1
		elif sellerID != "":
			subOrderParameters["sellersArr"] = [int(e) if e.isdigit() else e for e in sellerID.split(",")]

		tokenPayload = get_token_payload(accessToken, "internaluserID")
		subOrderParameters["isInternalUser"] = 0
		if "internaluserID" in tokenPayload and tokenPayload["internaluserID"]!=None:
			subOrderParameters["internalusersArr"] = [tokenPayload["internaluserID"]]
			subOrderParameters["isInternalUser"] = 1

		if status != "":
			subOrderParameters["statusArr"] = [int(e) if e.isdigit() else e for e in status.split(",")]

		if subOrderID != "":
			subOrderParameters["subOrderArr"] = [int(e) if e.isdigit() else e for e in subOrderID.split(",")]

		if subOrderParameters["isSeller"] == 0 and subOrderParameters["isInternalUser"] == 0:
			return customResponse("4XX", {"error": "Authentication failure"})

		return order.get_suborder_details(request,subOrderParameters)
	#elif request.method == "PUT":
	#	return order.update_suborder(request)

	return customResponse("4XX", {"error": "Invalid request"})

@csrf_exempt
def order_details(request):

	if request.method == "GET":

		orderParameters = {}

		status = request.GET.get("status", "")
		buyerID = request.GET.get("buyerID", "")
		orderID = request.GET.get("orderID", "")
		accessToken = request.GET.get("access_token", "")

		tokenPayload = get_token_payload(accessToken, "buyerID")
		orderParameters["isBuyer"] = 0
		if "buyerID" in tokenPayload and tokenPayload["buyerID"]!=None:
			orderParameters["buyerssArr"] = [tokenPayload["buyerID"]]
			orderParameters["isBuyer"] = 1
		elif buyerID != "":
			orderParameters["buyerssArr"] = [int(e) if e.isdigit() else e for e in buyerID.split(",")]

		tokenPayload = get_token_payload(accessToken, "internaluserID")
		orderParameters["isInternalUser"] = 0
		if "internaluserID" in tokenPayload and tokenPayload["internaluserID"]!=None:
			orderParameters["internalusersArr"] = [tokenPayload["internaluserID"]]
			orderParameters["isInternalUser"] = 1

		if orderID != "":
			orderParameters["orderArr"] = [int(e) if e.isdigit() else e for e in orderID.split(",")]

		if status != "":
			orderParameters["statusArr"] = [int(e) if e.isdigit() else e for e in status.split(",")]

		if orderParameters["isBuyer"] == 0 and orderParameters["isInternalUser"] == 0:
			return customResponse("4XX", {"error": "Authentication failure"})

		return order.get_order_details(request,orderParameters)
	elif request.method == "POST":
		return order.post_new_order(request)

	return customResponse("4XX", {"error": "Invalid request"})

@csrf_exempt
def order_item_details(request):

	if request.method == "GET":

		orderItemParameters = {}

		status = request.GET.get("status", "")
		sellerID = request.GET.get("sellerID", "")
		orderItemID = request.GET.get("orderitemID", "")
		accessToken = request.GET.get("access_token", "")

		tokenPayload = get_token_payload(accessToken, "sellerID")
		orderItemParameters["isSeller"] = 0
		if "sellerID" in tokenPayload and tokenPayload["sellerID"]!=None:
			orderItemParameters["sellersArr"] = [tokenPayload["sellerID"]]
			orderItemParameters["isSeller"] = 1
		elif sellerID != "":
			orderItemParameters["sellersArr"] = [int(e) if e.isdigit() else e for e in sellerID.split(",")]

		tokenPayload = get_token_payload(accessToken, "internaluserID")
		orderItemParameters["isInternalUser"] = 0
		if "internaluserID" in tokenPayload and tokenPayload["internaluserID"]!=None:
			orderItemParameters["internalusersArr"] = [tokenPayload["internaluserID"]]
			orderItemParameters["isInternalUser"] = 1

		if status != "":
			orderItemParameters["statusArr"] = [int(e) if e.isdigit() else e for e in status.split(",")]

		if orderItemID != "":
			orderItemParameters["orderItemArr"] = [int(e) if e.isdigit() else e for e in orderItemID.split(",")]

		if orderItemParameters["isSeller"] == 0 and orderItemParameters["isInternalUser"] == 0:
			return customResponse("4XX", {"error": "Authentication failure"})

		return order.get_order_item_details(request,orderItemParameters)
	elif request.method == "DELETE":
		return order.cancel_order_item(request)

	return customResponse("4XX", {"error": "Invalid request"})

@csrf_exempt
def buyer_payment_details(request):

	if request.method == "GET":
		status = request.GET.get("status", "")
		buyerID = request.GET.get("buyerID", "")

		accessToken = request.GET.get("access_token", "")
		tokenPayload = get_token_payload(accessToken, "buyerID")
		isBuyer = 0
		if "buyerID" in tokenPayload and tokenPayload["buyerID"]!=None:
			buyersArr = [tokenPayload["buyerID"]]
			isBuyer = 1
		elif buyerID == "":
			buyersArr = []
		else:
			buyersArr = [int(e) if e.isdigit() else e for e in buyerID.split(",")]

		tokenPayload = get_token_payload(accessToken, "internaluserID")
		isInternalUser = 0
		internalusersArr = []
		if "internaluserID" in tokenPayload and tokenPayload["internaluserID"]!=None:
			internalusersArr = [tokenPayload["internaluserID"]]
			isInternalUser = 1

		if status == "":
			statusArr = []
		else:
			statusArr = [int(e) if e.isdigit() else e for e in status.split(",")]

		return order.get_buyer_payment_details(request,statusArr,buyersArr, isBuyer,internalusersArr,isInternalUser)
	elif request.method == "POST":
		return order.post_new_buyer_payment(request)


	return customResponse("4XX", {"error": "Invalid request"})

@csrf_exempt
def seller_payment_details(request):

	if request.method == "GET":
		status = request.GET.get("status", "")
		sellerID = request.GET.get("sellerID", "")

		accessToken = request.GET.get("access_token", "")
		tokenPayload = get_token_payload(accessToken, "sellerID")
		isSeller = 0
		if "sellerID" in tokenPayload and tokenPayload["sellerID"]!=None:
			sellersArr = [tokenPayload["sellerID"]]
			isSeller = 1
		elif sellerID == "":
			sellersArr = []
		else:
			sellersArr = [int(e) if e.isdigit() else e for e in sellerID.split(",")]

		tokenPayload = get_token_payload(accessToken, "internaluserID")
		isInternalUser = 0
		internalusersArr = []
		if "internaluserID" in tokenPayload and tokenPayload["internaluserID"]!=None:
			internalusersArr = [tokenPayload["internaluserID"]]
			isInternalUser = 1

		if status == "":
			statusArr = []
		else:
			statusArr = [int(e) if e.isdigit() else e for e in status.split(",")]

		return order.get_seller_payment_details(request,statusArr,sellersArr, isSeller,internalusersArr,isInternalUser)
	elif request.method == "POST":
		return order.post_new_seller_payment(request)

	return customResponse("4XX", {"error": "Invalid request"})