import json
import logging
log = logging.getLogger("django")
from scripts.utils import *

from orders.models.cart import *
from orders.models.order import Order, sendOrderMail, filterOrder
from orders.models.subOrder import SubOrder
from orders.models.orderItem import OrderItem

from orders.serializers.order import serializeOrder

def get_payment_method(request, parameters):

	try:
		body = []

		CODDict = {}
		CODDict["display_value"] = "Cash on Delivery"
		CODDict["payment_method"] = 0
		CODDict["cod_rate_percent"] = 2
		body.append(CODDict)

		NEFTDict = {}
		NEFTDict["display_value"] = "NEFT"
		NEFTDict["payment_method"] = 1
		NEFTDict["ifsc"] = ""
		NEFTDict["account_number"] = ""
		body.append(NEFTDict)

		CreditDict = {}
		CreditDict["display_value"] = "Credit"
		CreditDict["payment_method"] = 9
		CreditDict["min_transactions"] = 15
		parameters["orderStatusArr"] = [3, 4]
		buyerCompletedOrders = filterOrder(parameters)
		leftOrders = max(15 - buyerCompletedOrders.count(), 0)
		CreditDict["left_orders"] = leftOrders
		body.append(CreditDict)

		response = {"payment_methods": body}
		statusCode = "2XX"
	except Exception as e:
		log.critical(e)
		statusCode = "4XX"
		response = {"error": "Invalid request"}

	closeDBConnection()
	return customResponse(statusCode, response)

def post_new_order(request, parameters):
	try:
		requestbody = request.body.decode("utf-8")
		cart = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse("4XX", {"error": "Invalid data sent in request"})

	if not len(cart):
		return customResponse("4XX", {"error": "Invalid data sent in request"})

	if not "cartID" in cart or not validate_integer(cart["cartID"]):
		return customResponse("4XX", {"error": "Cart id not properly sent"})

	cartPtr = Cart.objects.filter(id=int(cart["cartID"]), product_count__gt=0, status=0)

	if len(cartPtr) ==0:
		return customResponse("4XX", {"error": "Invalid cart ID sent"})

	cartPtr = cartPtr[0]

	buyerID = parameters["buyersArr"][0]

	if not cartPtr.buyer_id == buyerID:
		return customResponse("4XX", {"error": "Invalid cart ID for buyer sent"})

	try:
		newOrder = Order()
		newOrder.populateDataFromCart(cartPtr)
		newOrder.save()

		subCarts = SubCart.objects.filter(cart=cartPtr, product_count__gt=0, status=0)

		for subCartPtr in subCarts:
			newSubOrder = SubOrder(order=newOrder, seller=subOrder["seller"])
			newSubOrder.populateDataFromSubCart(subCartPtr)
			newSubOrder.save()

			cartItems = CartItem.objects.filter(subcart=subCartPtr, status=0)

			for cartItemPtr in cartItems:
				newOrderItem = OrderItem(suborder=newSubOrder)
				newOrderItem.populateDataFromCartItem(cartItemPtr)
				newOrderItem.save()

			cartItems.update(status=2)

		cartPtr.status = 1
		cartPtr.save()

		subCarts.update(status = 1)

	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse("4XX", {"error": "unable to create entry in db"})
	else:
		sendOrderMail(newOrder)
		closeDBConnection()
		return customResponse("2XX", {"order": serializeOrder(newOrder)})