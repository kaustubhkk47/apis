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

		statusCode = 200

		body = parseCart(pageItems,parameters)
		response = {"carts": body}
		responsePaginationParameters(response, paginator, parameters)

	except Exception as e:
		log.critical(e)
		statusCode = 500
		response = {}

	closeDBConnection()
	return customResponse(statusCode, response, error_code=0)

def get_cart_item_details(request, parameters):
	try:

		cartItems = filterCartItem(parameters)

		body = parseCartItem(cartItems,parameters)
		statusCode = 200
		response = {"cart_items": body}

	except Exception as e:
		log.critical(e)
		statusCode = 500
		response = {}

	closeDBConnection()
	return customResponse(statusCode, response, error_code=0)

def post_new_cart_item(request, parameters):
	try:
		requestbody = request.body.decode("utf-8")
		cartitem = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse(400, error_code=4)

	if not len(cartitem):
		return customResponse(400, error_code=5)

	buyerID = 0

	try:
		if not filterBuyer(parameters).exists():
			return customResponse(400, error_code=6, error_details=  "Invalid buyer id sent")
		buyerID = parameters["buyersArr"][0]
	except Exception as e:
		return customResponse(400, error_code=6, error_details= "Invalid buyer id sent")

	if not "productID" in cartitem or not validate_integer(cartitem["productID"]):
		return customResponse(400, error_code=5, error_details= "Product id not sent")

	productParameters = {}
	productParameters["product_show_online"] = True
	productParameters["product_verification"] = True
	productParameters["productsArr"] = [int(cartitem["productID"])]
	productPtr = filterProducts(productParameters)

	if len(productPtr) == 0:
		return customResponse(400, error_code=6, error_details= " Invalid product id sent")

	productPtr = productPtr[0]

	isCartNew = 1
	isSubCartNew = 1
	isCartItemNew = 1

	cartPtr = Cart.objects.filter(buyer_id=buyerID, status = 0)

	if len(cartPtr) == 0:
		cartPtr = Cart(buyer_id = buyerID)
		subCartPtr = SubCart(seller_id =productPtr.seller_id)
		cartItemPtr = CartItem(buyer_id = buyerID, product = productPtr)
	else:
		isCartNew = 0
		cartPtr = cartPtr[0]

		subCartPtr = SubCart.objects.filter(cart=cartPtr, seller_id = productPtr.seller_id)

		if len(subCartPtr) == 0:
			subCartPtr = SubCart(seller_id=productPtr.seller_id)
			cartItemPtr = CartItem(buyer_id = buyerID, product = productPtr)
		else:
			isSubCartNew = 0
			subCartPtr = subCartPtr[0]

			cartItemPtr = CartItem.objects.filter(buyer_id=buyerID, product = productPtr, status = 0)

			if len(cartItemPtr) == 0:
				cartItemPtr = CartItem(buyer_id = buyerID, product = productPtr)
			else:
				isCartItemNew = 0
				cartItemPtr = cartItemPtr[0]

	if not cartItemPtr.validateCartItemData(cartitem):
		return customResponse(400, error_code=5, error_details= " Invalid data for cart item sent")

	if isCartItemNew == 1 and int(cartitem["lots"]) == 0:
		return customResponse(400, error_code=6, error_details= "Zero lots sent for new cart item")

	try:
		if not cartItemPtr.lots ==  int(cartitem["lots"]):
			initialPrices = cartItemPtr.getPrices()
			cartItemPtr.populateCartItemData(cartitem)
			finalPrices =  cartItemPtr.getPrices()
		
			cartPtr.populateCartData(initialPrices, finalPrices)
			subCartPtr.populateSubCartData(initialPrices, finalPrices)

			if subCartPtr.shipping_charge < 175:
				extra_shipping_charge = (175-subCartPtr.shipping_charge)
				cartPtr.shipping_charge += extra_shipping_charge
				cartPtr.final_price += extra_shipping_charge
				subCartPtr.shipping_charge += extra_shipping_charge
				subCartPtr.final_price += extra_shipping_charge

			cartPtr.save()
		
			subCartPtr.cart = cartPtr
			subCartPtr.save()

			cartItemPtr.subcart = subCartPtr
			cartItemPtr.save()

			if not CartItem.objects.filter(subcart=subCartPtr, status=0).exists():
				extra_shipping_charge = subCartPtr.shipping_charge
				cartPtr.shipping_charge -= extra_shipping_charge
				cartPtr.final_price -= extra_shipping_charge
				subCartPtr.shipping_charge -= extra_shipping_charge
				subCartPtr.final_price -= extra_shipping_charge
				cartPtr.save()
				subCartPtr.save()

			cartItemHistoryPtr = CartItemHistory()
			cartItemHistoryPtr.populateCartItemHistoryData(cartItemPtr)
			cartItemHistoryPtr.save()

	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse(500, error_code = 1)
	else:
		closeDBConnection()
		return customResponse(200, {"carts": serializeCart(cartItemPtr.subcart.cart, parameters)})



