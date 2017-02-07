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
		cartitemDict = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse(400, error_code=4)

	if not len(cartitemDict):
		return customResponse(400, error_code=5)

	buyerID = 0

	try:
		if not filterBuyer(parameters).exists():
			return customResponse(400, error_code=6, error_details=  "Invalid buyer id sent")
		buyerID = parameters["buyersArr"][0]
	except Exception as e:
		return customResponse(400, error_code=6, error_details= "Invalid buyer id sent")

	if not "products" in cartitemDict:
		cartitemDict["products"] = [cartitemDict.copy()]

	cartProducts = cartitemDict["products"]

	productsHash = {}
	productIDarr = []

	if not CartItem.validateCartItemData(cartProducts, productsHash, productIDarr):
		return customResponse(400, error_code=5, error_details= " Invalid data for cart item sent")

	productParameters = {}
	productParameters["product_show_online"] = True
	productParameters["product_verification"] = True
	productParameters["productsArr"] = productIDarr
	allProducts = filterProducts(productParameters)

	if len(allProducts) == 0:
		return customResponse(400, error_code=6, error_details= " Invalid product id sent")

	cartPtr, cartCreated = Cart.objects.get_or_create(buyer_id=buyerID, status = 0)
	
	try:
		for productPtr in allProducts:
			
			cartitem = cartProducts[productsHash[productPtr.id]]
			subCartPtr, cartItemCreated = SubCart.objects.get_or_create(cart_id=cartPtr.id, seller_id = productPtr.seller_id)
			cartItemPtr , cartItemCreated= CartItem.objects.get_or_create(subcart_id = subCartPtr.id, buyer_id=buyerID, product = productPtr)

			if not cartItemPtr.lots ==  int(cartitem["lots"]):
				initialPrices = cartItemPtr.getPrices()
				cartItemPtr.populateCartItemData(cartitem)
				finalPrices =  cartItemPtr.getPrices()

				initialPrices["extra_shipping_charge"] = subCartPtr.extra_shipping_charge
				subCartPtr.populateSubCartData(initialPrices, finalPrices)
				finalPrices["extra_shipping_charge"] = subCartPtr.extra_shipping_charge

				cartPtr.populateCartData(initialPrices, finalPrices)	

				subCartPtr.save()

				cartItemPtr.save()

				cartItemHistoryPtr = CartItemHistory()
				cartItemHistoryPtr.populateCartItemHistoryData(cartItemPtr)
				cartItemHistoryPtr.save()
			elif not int(cartitem["lots"]) == 0:
				cartItemPtr.remarks = cartitem["remarks"]
				cartItemPtr.save()
				subCartPtr.save()

		cartPtr.save()

	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse(500, error_code = 1)
	else:

		mail_template_file = "extras/cart_addition.html"
		mail_dict = {}
		mail_dict["buyerID"] = buyerID
		mail_dict["cart"] = serializeCart(cartPtr)
		mail_dict["cartProducts"] = cartProducts
		subject = "New cart item addition for buyer ID " + str(buyerID)
		from_email = "Wholdus Info <info@wholdus.com>"
		to = ["manish@wholdus.com","kushagra@wholdus.com"]
		create_email(mail_template_file,mail_dict,subject,from_email,to)

		closeDBConnection()
		return customResponse(200, {"carts": parseCart(filterCarts(parameters),parameters)})



