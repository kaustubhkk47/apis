from django.views.decorators.csrf import csrf_exempt

from orders.views import order, orderItem, orderShipment, payments, subOrder
from scripts.utils import customResponse, get_token_payload, getArrFromString, validate_bool, getPaginationParameters
import jwt as JsonWebToken

from .user_handler import populateBuyerDetailsParameters, populateSellerDetailsParameters, populateAllUserIDParameters
from .catalog_handler import populateProductDetailsParameters

@csrf_exempt
def order_shipment_details(request):

	if request.method == "GET":

		orderShipmentParameters = populateOrderParameters(request)

		if orderShipmentParameters["isSeller"] == 0 and orderShipmentParameters["isInternalUser"] == 0:
			return customResponse("4XX", {"error": "Authentication failure"})

		return orderShipment.get_order_shipment_details(request,orderShipmentParameters)
	elif request.method == "POST":
		return orderShipment.post_new_order_shipment(request)
	elif request.method == "PUT":
		return orderShipment.update_order_shipment(request)

	return customResponse("4XX", {"error": "Invalid request"})

@csrf_exempt
def suborder_details(request):

	if request.method == "GET":

		subOrderParameters = populateOrderParameters(request)

		if subOrderParameters["isSeller"] == 0 and subOrderParameters["isInternalUser"] == 0:
			return customResponse("4XX", {"error": "Authentication failure"})

		return subOrder.get_suborder_details(request,subOrderParameters)
	#elif request.method == "PUT":
	#	return subOrder.update_suborder(request)

	return customResponse("4XX", {"error": "Invalid request"})

@csrf_exempt
def order_details(request):

	if request.method == "GET":

		orderParameters = populateOrderParameters(request)

		if orderParameters["isBuyer"] == 0 and orderParameters["isInternalUser"] == 0:
			return customResponse("4XX", {"error": "Authentication failure"})

		return order.get_order_details(request,orderParameters)
	elif request.method == "POST":
		return order.post_new_order(request)

	return customResponse("4XX", {"error": "Invalid request"})

@csrf_exempt
def order_item_details(request):

	if request.method == "GET":

		orderItemParameters = populateOrderParameters(request)

		if orderItemParameters["isSeller"] == 0 and orderItemParameters["isInternalUser"] == 0:
			return customResponse("4XX", {"error": "Authentication failure"})

		return orderItem.get_order_item_details(request,orderItemParameters)
	elif request.method == "DELETE":
		return orderItem.cancel_order_item(request)

	return customResponse("4XX", {"error": "Invalid request"})

@csrf_exempt
def buyer_payment_details(request):

	if request.method == "GET":

		buyerPaymentParameters = populateOrderParameters(request)

		if buyerPaymentParameters["isBuyer"] == 0 and buyerPaymentParameters["isInternalUser"] == 0:
			return customResponse("4XX", {"error": "Authentication failure"})

		return payments.get_buyer_payment_details(request,buyerPaymentParameters)
	elif request.method == "POST":
		return payments.post_new_buyer_payment(request)


	return customResponse("4XX", {"error": "Invalid request"})

@csrf_exempt
def seller_payment_details(request):

	if request.method == "GET":

		sellerPaymentParameters = populateOrderParameters(request)

		if sellerPaymentParameters["isSeller"] == 0 and sellerPaymentParameters["isInternalUser"] == 0:
			return customResponse("4XX", {"error": "Authentication failure"})

		return payments.get_seller_payment_details(request,sellerPaymentParameters)
	elif request.method == "POST":
		return payments.post_new_seller_payment(request)

	return customResponse("4XX", {"error": "Invalid request"})

def populateOrderParameters(request, parameters = {}):

	parameters = populateAllUserIDParameters(request, parameters)

	orderID = request.GET.get("orderID", "")
	orderStatus = request.GET.get("order_status", "")
	orderPaymentStatus = request.GET.get("order_payment_status", "")

	if orderID != "":
		parameters["orderArr"] = getArrFromString(orderID)
	if orderStatus != "":
		parameters["orderStatusArr"] = getArrFromString(orderStatus)
	if orderPaymentStatus != "":
		parameters["orderPaymentStatusArr"] = getArrFromString(orderPaymentStatus)

	subOrderID = request.GET.get("suborderID", "")
	subOrderStatus = request.GET.get("sub_order_status", "")
	subOrderPaymentStatus = request.GET.get("sub_order_payment_status", "")

	if subOrderID != "":
		parameters["subOrderArr"] = getArrFromString(subOrderID)
	if subOrderStatus != "":
		parameters["subOrderStatusArr"] = getArrFromString(subOrderStatus)
	if subOrderPaymentStatus != "":
		parameters["subOrderPaymentStatusArr"] = getArrFromString(subOrderPaymentStatus)	

	orderShipmentID = request.GET.get("ordershipmentID", "")
	orderShipmentStatus = request.GET.get("order_shipment_status", "")

	if orderShipmentID != "":
		parameters["orderShipmentArr"] = getArrFromString(orderShipmentID)
	if orderShipmentStatus != "":
		parameters["orderShipmentStatusArr"] = getArrFromString(orderShipmentStatus)
	
	orderItemID = request.GET.get("orderitemID", "")
	orderItemStatus = request.GET.get("order_item_status", "")

	if orderItemID != "":
		parameters["orderItemArr"] = getArrFromString(orderItemID)
	if orderItemStatus != "":
		parameters["orderItemStatusArr"] = getArrFromString(orderItemStatus)

	buyerPaymentID = request.GET.get("buyerpaymentID", "")
	buyerPaymentStatus = request.GET.get("buyer_payment_status", "")

	if buyerPaymentID != "":
		parameters["buyerPaymentArr"] = getArrFromString(buyerPaymentID)
	if buyerPaymentStatus != "":
		parameters["buyerPaymentStatusArr"] = getArrFromString(buyerPaymentStatus)

	sellerPaymentID = request.GET.get("sellerpaymentID", "")
	sellerPaymentStatus = request.GET.get("seller_payment_status", "")
	
	if sellerPaymentID != "":
		parameters["sellerPaymentArr"] = getArrFromString(sellerPaymentID)
	if sellerPaymentStatus != "":
		parameters["sellerPaymentStatusArr"] = getArrFromString(sellerPaymentStatus)

	parameters = getPaginationParameters(request, parameters, 10)

	return parameters

def populateOrderDetailsParameters(request, parameters = {}):

	orderDetails = request.GET.get("order_details", None)
	if validate_bool(orderDetails):
		parameters["order_details"] = int(orderDetails)
	else:
		parameters["order_details"] = 1

	subOrderDetails = request.GET.get("sub_order_details", None)
	if validate_bool(subOrderDetails):
		parameters["sub_order_details"] = int(subOrderDetails)
	else:
		parameters["sub_order_details"] = 1

	orderShipmentDetails = request.GET.get("order_shipment_details", None)
	if validate_bool(orderShipmentDetails):
		parameters["order_shipment_details"] = int(orderShipmentDetails)
	else:
		parameters["order_shipment_details"] = 1

	orderItemDetails = request.GET.get("order_item_details", None)
	if validate_bool(orderItemDetails):
		parameters["order_item_details"] = int(orderItemDetails)
	else:
		parameters["order_item_details"] = 1

	buyerPaymentDetails = request.GET.get("buyer_payment_details", None)
	if validate_bool(buyerPaymentDetails):
		parameters["buyer_payment_details"] = int(buyerPaymentDetails)
	else:
		parameters["buyer_payment_details"] = 1

	sellerPaymentDetails = request.GET.get("seller_payment_details", None)
	if validate_bool(sellerPaymentDetails):
		parameters["seller_payment_details"] = int(sellerPaymentDetails)
	else:
		parameters["seller_payment_details"] = 1

	parameters = populateBuyerDetailsParameters(request, parameters)

	parameters = populateSellerDetailsParameters(request, parameters)

	parameters = populateProductDetailsParameters(request, parameters)

	return parameters