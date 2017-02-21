import json
import logging
log = logging.getLogger("django")
from scripts.utils import *

from django.utils import timezone

from orders.models.cart import *
from orders.models.order import Order, sendOrderMail, filterOrder
from orders.models.subOrder import SubOrder
from orders.models.orderItem import OrderItem
from orders.models.payments import BuyerPayment
from orders.models.checkout import Checkout, filterCheckouts

from users.models.buyer import Buyer, BuyerAddress

from orders.serializers.order import serializeOrder
from orders.serializers.checkout import serializeCheckout, parseCheckout

from logistics.models.serviceability import filterServiceablePincodes

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
		NEFTDict["company_name"] = "PROBZIP BUSINESS SOLUTIONS PVT LTD"
		NEFTDict["ifsc"] = "ICIC0000171"
		NEFTDict["account_number"] = "017105008405"
		NEFTDict["account_type"] = "CURRENT"
		NEFTDict["branch"] = "SAKET, Delhi, 110017"
		body.append(NEFTDict)

		CreditDict = {}
		minCreditTransactions = 15
		CreditDict["display_value"] = "Credit"
		CreditDict["payment_method"] = 9
		CreditDict["min_transactions"] = minCreditTransactions
		parameters["orderStatusArr"] = [3, 4]
		buyerCompletedOrders = filterOrder(parameters)
		leftOrders = max(minCreditTransactions - buyerCompletedOrders.count(), 0)
		CreditDict["left_orders"] = leftOrders
		body.append(CreditDict)

		response = {"payment_methods": body}
		statusCode = 200
	except Exception as e:
		log.critical(e)
		statusCode = 500
		response = {}

	closeDBConnection()
	return customResponse(statusCode, response, error_code=0)

def get_checkout_details(request, parameters):

	try:
		checkouts = filterCheckouts(parameters)
		try:
			checkouts = checkouts.latest('created_at')
			body = serializeCheckout(checkouts,parameters)
			response = {"checkout": body}
			statusCode = 200
		except Exception as e:
			return customResponse(400, error_code=6, error_details ="No checkout for buyer")

	except Exception as e:
		log.critical(e)
		statusCode = 500
		response = {}

	closeDBConnection()
	return customResponse(statusCode, response, error_code=0)

def create_checkout_details(request, parameters):
	try:
		requestbody = request.body.decode("utf-8")
		checkout = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse(400, error_code=4)

	#if len(checkout) == 0:
	#	return customResponse("4XX", {"error": "Invalid data sent in request"})

	buyerID = parameters["buyersArr"][0]

	buyerPtr = Buyer.objects.filter(id=buyerID, delete_status=False)

	if not buyerPtr.exists():
		return customResponse(400, error_code=6, error_details = "Invalid id for buyer sent")

	cartPtr = Cart.objects.filter(buyer_id=buyerID, product_count__gt=0, status=0)

	if len(cartPtr) ==0:
		return customResponse(400, error_code=6, error_details = "No product in cart")

	cartPtr = cartPtr[0]

	try:
		newCheckout = Checkout(cart=cartPtr)
		newCheckout.save()

	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse(500, error_code = 1)
	else:
		closeDBConnection()
		return customResponse(200, {"checkout": serializeCheckout(newCheckout, parameters)})

def update_checkout_details(request, parameters):
	try:
		requestbody = request.body.decode("utf-8")
		checkout = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse(400, error_code=4)

	if not len(checkout):
		return customResponse(400, error_code=5,  error_details="Invalid data sent in request")

	buyerID = parameters["buyersArr"][0]

	buyerPtr = Buyer.objects.filter(id=buyerID, delete_status=False)

	if len(buyerPtr)==0:
		return customResponse(400, error_code=6, error_details ="Invalid id for buyer sent")

	buyerPtr = buyerPtr[0]

	if not "checkoutID" in checkout or not validate_integer(checkout["checkoutID"]):
		return customResponse(400, error_code=5,  error_details="Id for checkout not sent")

	checkoutPtr = Checkout.objects.filter(id=int(checkout["checkoutID"]))

	if len(checkoutPtr) ==0:
		return customResponse(400, error_code=6, error_details = "Invalid id for checkout sent")

	checkoutPtr = checkoutPtr[0]

	if not checkoutPtr.cart.status ==0:
		return customResponse(400, error_code=6,  error_details="Checkout for cart already completed")

	if not "status" in checkout or not validate_integer(checkout["status"]):
		return customResponse(400, error_code=5,  error_details="Status not sent")

	if not checkoutPtr.validateCheckoutData(checkout):
		return customResponse(400, error_code=6,  error_details= "Invalid status sent")

	orderBody = {}

	try:
		nowTime = timezone.now()
		status = int(checkout["status"])
		if status == 1:
			buyerAddressPtr = BuyerAddress.objects.filter(id=int(checkout["addressID"]))
			if len(buyerAddressPtr) == 0:
				return customResponse(400, error_code=6,  error_details= "Invalid address ID sent")
			buyerAddressPtr = buyerAddressPtr[0]
			pincodeParameters = {}
			pincodeParameters["pincodesCodesArr"] = [buyerAddressPtr.pincode_number]
			pincodeParameters["cod_available"] = True
			pincodeParameters["regular_delivery_available"] = True
			if not filterServiceablePincodes(pincodeParameters).exists():
				return customResponse(400, error_code=6, error_details="Cannot deliver to pincode")
			checkoutPtr.buyer_address_history = buyerPtr.latest_buyer_address_history(int(checkout["addressID"]))
			checkoutPtr.address_given_time = nowTime
		elif status == 2:
			checkoutPtr.summary_confirmed_time = nowTime
		elif status == 3:
			checkoutPtr.payment_done_time = nowTime
			checkoutPtr.payment_method = int(checkout["payment_method"])
			if checkoutPtr.payment_method == 0:
				CODextracost = 0.02
				checkoutPtr.cart.setCODPaymentMethod(CODextracost)
			orderBody = checkout_new_order(checkoutPtr, parameters)

		checkoutPtr.status = status
		checkoutPtr.save()

	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse(500, error_code = 3)
	else:
		closeDBConnection()
		body = {"checkout": serializeCheckout(checkoutPtr, parameters)}
		if status ==3:
			body["order"] = orderBody
		return customResponse(200, body)

def checkout_new_order(checkoutPtr, parameters):
	
	cartPtr = checkoutPtr.cart

	try:
		newOrder = Order()
		newOrder.populateDataFromCart(cartPtr)
		newOrder.buyer_address_history = checkoutPtr.buyer_address_history
		newOrder.save()

		subCarts = SubCart.objects.filter(cart=cartPtr, product_count__gt=0, status=0)

		nowTime = timezone.now()

		for subCartPtr in subCarts:
			newSubOrder = SubOrder(order=newOrder)
			newSubOrder.populateDataFromSubCart(subCartPtr)
			newSubOrder.save()

			cartItems = CartItem.objects.filter(subcart=subCartPtr, status=0, pieces__gt=0)

			for cartItemPtr in cartItems:
				newOrderItem = OrderItem(suborder=newSubOrder)
				newOrderItem.populateDataFromCartItem(cartItemPtr)
				newOrderItem.save()

			cartItems.update(status=2,updated_at = nowTime)

		newBuyerPayment = BuyerPayment(order = newOrder)
		newBuyerPayment.populateFromCheckout(checkoutPtr, cartPtr)
		newBuyerPayment.save()

		cartPtr.status = 1
		cartPtr.save()

		subCarts.update(status = 1, updated_at = nowTime)
	
		sendOrderMail(newOrder)
		
		return serializeOrder(newOrder, parameters)
	except Exception as e:
		log.critical(e)
		return {}