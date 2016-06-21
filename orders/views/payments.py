from scripts.utils import *
import json
import logging
log = logging.getLogger("django")

from ..models.order import Order
from ..models.orderItem import OrderItem
from ..models.subOrder import SubOrder
from ..models.orderShipment import OrderShipment
from ..models.payments import BuyerPayment, SellerPayment, filterSellerPayment, filterBuyerPayment, validateBuyerPaymentData, validateSellerPaymentData, populateBuyerPayment, populateSellerPayment, validateSellerPaymentItemsData
from ..serializers.payments import parseSellerPayments, parseBuyerPayments, serializeBuyerPayment, serializeSellerPayment

def get_seller_payment_details(request, sellerPaymentParameters):
	try:
		sellerPayments = filterSellerPayment(sellerPaymentParameters)

		body = parseSellerPayments(sellerPayments,sellerPaymentParameters)
		statusCode = "2XX"
		response = {"seller_payments": body}

	except Exception as e:
		log.critical(e)
		statusCode = "4XX"
		response = {"error": "Invalid request"}

	closeDBConnection()
	return customResponse(statusCode, response)

def get_buyer_payment_details(request, buyerPaymentParameters):
	try:

		buyerPayments = filterBuyerPayment(buyerPaymentParameters)
		
		body = parseBuyerPayments(buyerPayments,buyerPaymentParameters)
		statusCode = "2XX"
		response = {"buyer_payments": body}

	except Exception as e:
		log.critical(e)
		statusCode = "4XX"
		response = {"error": "Invalid request"}

	closeDBConnection()
	return customResponse(statusCode, response)

def post_new_buyer_payment(request):
	try:
		requestbody = request.body.decode("utf-8")
		buyerPayment = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse("4XX", {"error": "Invalid data sent in request"})

	if not len(buyerPayment) or not validateBuyerPaymentData(buyerPayment):
		return customResponse("4XX", {"error": "Invalid data for buyer payment sent"})

	if not "orderID" in buyerPayment or buyerPayment["orderID"]==None or not validate_integer(buyerPayment["orderID"]):
		return customResponse("4XX", {"error": "Id for order not sent"})

	OrderPtr = Order.objects.filter(id=int(buyerPayment["orderID"]))

	if len(OrderPtr) == 0:
		return customResponse("4XX", {"error": "Invalid id for order sent"})

	OrderPtr = OrderPtr[0]

	if int(buyerPayment["payment_method"]) == 0:
		if not "ordershipmentID" in buyerPayment or buyerPayment["ordershipmentID"]==None or not validate_integer(buyerPayment["ordershipmentID"]):
			return customResponse("4XX", {"error": "Id for order shipment not sent"})

		OrderShipmentPtr = OrderShipment.objects.filter(id=int(buyerPayment["ordershipmentID"]))

		if len(OrderShipmentPtr) == 0:
			return customResponse("4XX", {"error": "Invalid id for order shipment sent"})

		OrderShipmentPtr = OrderShipmentPtr[0]

		if OrderShipmentPtr.suborder.order_id != int(buyerPayment["orderID"]):
			return customResponse("4XX", {"error": "Invalid id for order shipment sent"})

	try:
		newBuyerPayment = BuyerPayment(order=OrderPtr)
		populateBuyerPayment(newBuyerPayment, buyerPayment)
		if int(buyerPayment["payment_method"]) == 0:
			newBuyerPayment.order_shipment = OrderShipmentPtr

		if bool(buyerPayment["fully_paid"]) == 1:
			OrderPtr.order_payment_status = 1
		else:
			OrderPtr.order_payment_status = 2
		OrderPtr.save()
		newBuyerPayment.save()
	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse("4XX", {"error": "unable to create entry in db"})
	else:
		closeDBConnection()
		return customResponse("2XX", {"buyer_payment": serializeBuyerPayment(newBuyerPayment)})

def post_new_seller_payment(request):
	try:
		requestbody = request.body.decode("utf-8")
		sellerPayment = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse("4XX", {"error": "Invalid data sent in request"})

	if not len(sellerPayment) or not validateSellerPaymentData(sellerPayment):
		return customResponse("4XX", {"error": "Invalid data for seller payment sent"})

	if not "suborderID" in sellerPayment or sellerPayment["suborderID"]==None or not validate_integer(sellerPayment["suborderID"]):
		return customResponse("4XX", {"error": "Id for suborder not sent"})

	SubOrderPtr = SubOrder.objects.filter(id=int(sellerPayment["suborderID"]))

	if len(SubOrderPtr) == 0:
		return customResponse("4XX", {"error": "Invalid id for suborder sent"})

	SubOrderPtr = SubOrderPtr[0]

	if bool(sellerPayment["fully_paid"]) == 0:
		if not "order_items" in sellerPayment or sellerPayment["order_items"]==None:
			return customResponse("4XX", {"error": "Order items in order shipment not sent"})

		if not validateSellerPaymentItemsData(sellerPayment["order_items"], SubOrderPtr.id):
			return customResponse("4XX", {"error": "Order items in order shipment not sent properly sent"})

	try:
		newSellerPayment = SellerPayment(suborder=SubOrderPtr)
		populateSellerPayment(newSellerPayment, sellerPayment)
		newSellerPayment.save()

		if bool(sellerPayment["fully_paid"]) == 1:
			SubOrderPtr.suborder_payment_status = 1

			orderItemQuerySet = OrderItem.objects.filter(suborder_id = SubOrderPtr.id).exclude(current_status = 4)
			for orderItem in orderItemQuerySet:
				orderItem.seller_payment = newSellerPayment
				orderItem.save()
		else:
			SubOrderPtr.suborder_payment_status = 2

			for orderItem in sellerPayment["order_items"]:
				orderItemPtr = OrderItem.objects.filter(id=int(orderItem["orderitemID"]))
				orderItemPtr = orderItemPtr[0]
				orderItemPtr.seller_payment = newSellerPayment
				orderItemPtr.save()

		SubOrderPtr.save()

	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse("4XX", {"error": "unable to create entry in db"})
	else:
		closeDBConnection()
		return customResponse("2XX", {"order_shipment": serializeSellerPayment(newSellerPayment)})

