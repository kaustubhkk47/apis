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
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone

def get_seller_payment_details(request, parameters):
	try:
		sellerPayments = filterSellerPayment(parameters)

		paginator = Paginator(sellerPayments, parameters["itemsPerPage"])

		try:
			pageItems = paginator.page(parameters["pageNumber"])
		except Exception as e:
			pageItems = []

		body = parseSellerPayments(pageItems,parameters)
		statusCode = 200
		response = {"seller_payments": body}

		responsePaginationParameters(response,paginator, parameters)

	except Exception as e:
		log.critical(e)
		statusCode = 500
		response = {}

	closeDBConnection()
	return customResponse(statusCode, response, error_code=0)

def get_buyer_payment_details(request, parameters):
	try:

		buyerPayments = filterBuyerPayment(parameters)
		
		paginator = Paginator(buyerPayments, parameters["itemsPerPage"])

		try:
			pageItems = paginator.page(parameters["pageNumber"])
		except Exception as e:
			pageItems = []

		body = parseBuyerPayments(pageItems,parameters)
		statusCode = 200
		response = {"buyer_payments": body}

		responsePaginationParameters(response,paginator, parameters)


	except Exception as e:
		log.critical(e)
		statusCode = 500
		response = {}

	closeDBConnection()
	return customResponse(statusCode, response, error_code=0)

def post_new_buyer_payment(request):
	try:
		requestbody = request.body.decode("utf-8")
		buyerPayment = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse(400, error_code=4)

	if not len(buyerPayment) or not validateBuyerPaymentData(buyerPayment):
		return customResponse(400, error_code=5, error_details= "Invalid data for buyer payment sent")

	if not "orderID" in buyerPayment or not validate_integer(buyerPayment["orderID"]):
		return customResponse(400, error_code=5, error_details= "Id for order not sent")

	OrderPtr = Order.objects.filter(id=int(buyerPayment["orderID"]))

	if len(OrderPtr) == 0:
		return customResponse(400, error_code=6, error_details ="Invalid id for order sent")

	OrderPtr = OrderPtr[0]

	if int(buyerPayment["payment_method"]) == 0:
		if not "ordershipmentID" in buyerPayment or not validate_integer(buyerPayment["ordershipmentID"]):
			return customResponse(400, error_code=5, error_details ="Id for order shipment not sent")

		OrderShipmentPtr = OrderShipment.objects.filter(id=int(buyerPayment["ordershipmentID"]))

		if len(OrderShipmentPtr) == 0:
			return customResponse(400, error_code=6, error_details ="Invalid id for order shipment sent")

		OrderShipmentPtr = OrderShipmentPtr[0]

		if OrderShipmentPtr.suborder.order_id != int(buyerPayment["orderID"]):
			return customResponse(400, error_code=6, error_details = "Invalid id for order shipment sent")

	try:
		newBuyerPayment = BuyerPayment(order=OrderPtr)
		populateBuyerPayment(newBuyerPayment, buyerPayment)
		if int(buyerPayment["payment_method"]) == 0:
			newBuyerPayment.order_shipment = OrderShipmentPtr

		if int(buyerPayment["fully_paid"]) == 1:
			OrderPtr.order_payment_status = 1
			OrderItem.objects.filter(suborder__order_id=OrderPtr.id).exclude(current_status__in=[4]).update(buyer_payment_status=True, updated_at = timezone.now())
		else:
			OrderPtr.order_payment_status = 2
		OrderPtr.save()
		newBuyerPayment.save()
	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse(500, error_code = 1)
	else:
		closeDBConnection()
		return customResponse(200, {"buyer_payment": serializeBuyerPayment(newBuyerPayment)})

def post_new_seller_payment(request):
	try:
		requestbody = request.body.decode("utf-8")
		sellerPayment = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse(400, error_code=4)

	if not len(sellerPayment) or not validateSellerPaymentData(sellerPayment):
		return customResponse(400, error_code=5, error_details="Invalid data for seller payment sent")

	if not "suborderID" in sellerPayment or not validate_integer(sellerPayment["suborderID"]):
		return customResponse(400, error_code=5, error_details= "Id for suborder not sent")

	SubOrderPtr = SubOrder.objects.filter(id=int(sellerPayment["suborderID"]))

	if len(SubOrderPtr) == 0:
		return customResponse(400, error_code=6, error_details="Invalid id for suborder sent")

	SubOrderPtr = SubOrderPtr[0]

	if int(sellerPayment["fully_paid"]) == 0:
		if not "order_items" in sellerPayment or sellerPayment["order_items"]==None:
			return customResponse(400, error_code=5, error_details="Order items in order shipment not sent")

		if not validateSellerPaymentItemsData(sellerPayment["order_items"], SubOrderPtr.id):
			return customResponse(400, error_code=5, error_details= "Order items in order shipment not sent properly sent")

	try:
		newSellerPayment = SellerPayment(suborder=SubOrderPtr)
		populateSellerPayment(newSellerPayment, sellerPayment)
		newSellerPayment.save()

		if int(sellerPayment["fully_paid"]) == 1:
			SubOrderPtr.suborder_payment_status = 1
			OrderItem.objects.filter(suborder_id = SubOrderPtr.id).exclude(current_status = 4).update(seller_payment_id=newSellerPayment.id, updated_at = timezone.now())
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
		return customResponse(500, error_code = 1)
	else:
		closeDBConnection()
		return customResponse(200, {"order_shipment": serializeSellerPayment(newSellerPayment)})

