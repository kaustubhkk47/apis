from orders.models.cart import *
from orders.serializers.cart import *
import json
import logging
log = logging.getLogger("django")
from scripts.utils import *
from users.models.buyer import filterBuyer
from catalog.models.product import filterProducts
from django.core.paginator import Paginator

def get_cart_details(request, parameters):
	try:

		carts = filterCarts(parameters)

		paginator = Paginator(carts, parameters["itemsPerPage"])

		try:
			pageItems = paginator.page(parameters["pageNumber"])
		except Exception as e:
			pageItems = []

		statusCode = "2XX"

		body = parseCart(pageItems,parameters)
		statusCode = "2XX"
		response = {"carts": body}
		response = responsePaginationParameters(response, paginator, parameters)

	except Exception as e:
		log.critical(e)
		statusCode = "4XX"
		response = {"error": "Invalid request"}

	closeDBConnection()
	return customResponse(statusCode, response)

def get_cart_item_details(request, parameters):
	try:

		cartItems = filterCartItem(parameters)

		statusCode = "2XX"

		body = parseCartItem(cartItems,parameters)
		statusCode = "2XX"
		response = {"cart_items": body}

	except Exception as e:
		log.critical(e)
		statusCode = "4XX"
		response = {"error": "Invalid request"}

	closeDBConnection()
	return customResponse(statusCode, response)

def post_new_cart_item(request, parameters):
	try:
		requestbody = request.body.decode("utf-8")
		cartitem = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse("4XX", {"error": "Invalid data sent in request"})

	if not len(cartitem):
		return customResponse("4XX", {"error": "Invalid data sent in request"})

	buyerID = 0

	try:
		if not filterBuyer(parameters).exists():
			return customResponse("4XX", {"error": "Invalid buyer id sent"})
		buyerID = parameters["buyersArr"][0]
	except Exception as e:
		return customResponse("4XX", {"error": "Invalid buyer id sent"})

	if not "productID" in cartitem or not validate_integer(cartitem["productID"]):
		return customResponse("4XX", {"error": "Product id not properly sent"})

	productParameters = {}
	productParameters["product_show_online"] = True
	productParameters["seller_show_online"] = True
	productParameters["product_verification"] = True
	productParameters["product_verification"] = True
	productParameters["productsArr"] = [int(cartitem["productID"])]
	productPtr = filterProducts(productParameters)

	if len(productPtr) == 0:
		return customResponse("4XX", {"error": " Invalid product id sent"})

	productPtr = productPtr[0]

	cartPtr = Cart.objects.filter(buyer_id=buyerID, status = 0)

	if len(cartPtr) == 0:
		cartPtr = Cart(buyer_id = buyerID)
	else:
		cartPtr = cartPtr[0]

	cartItemPtr = CartItem.objects.filter(buyer_id=buyerID, product = productPtr, status = 0)

	if len(cartItemPtr) == 0:
		cartItemPtr = CartItem(buyer_id = buyerID, product = productPtr)
	else:
		cartItemPtr = cartItemPtr[0]

	if not cartItemPtr.validateCartItemData(cartitem):
		return customResponse("4XX", {"error": " Invalid data for cart item sent"})

	try:
		cartPtr.save()
		cartItemPtr.cart = cartPtr
		cartItemPtr.populateCartItemData(cartitem)
		cartItemPtr.save()

		cartItemHistoryPtr = CartItemHistory()
		cartItemHistoryPtr.populateCartItemHistoryData(cartItemPtr)
		cartItemHistoryPtr.save()

	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse("4XX", {"error": "could not update"})
	else:
		closeDBConnection()
		return customResponse("2XX", {"cart_items": serializeCartItem(cartItemPtr, parameters)})