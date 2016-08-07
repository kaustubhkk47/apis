from catalog.serializers.product import serialize_product
from users.serializers.buyer import serialize_buyer
from ..models.cart import filterCartItem

def parseCartItem(cartItemQuerySet, cartItemParameters = {}):

	cartItems = []

	for cartItem in cartItemQuerySet:
		cartItemEntry = serializeCartItem(cartItem, cartItemParameters)
		cartItems.append(cartItemEntry)

	return cartItems

def parseCart(cartQuerySet, cartParameters = {}):

	carts = []

	for cart in cartQuerySet:
		cartEntry = serializeCart(cart, cartParameters)
		carts.append(cartEntry)

	return carts

def serializeCart(cartEntry, parameters = {}):
	cart = {}
	cart["cartID"] = cartEntry.id
	cart["created_at"] = cartEntry.created_at
	cart["updated_at"] = cartEntry.updated_at

	if "buyer_details" in parameters and parameters["buyer_details"] == 1:
		cart["buyer"]=serialize_buyer(cartEntry.buyer, parameters)
	else:
		buyer = {}
		buyer["buyerID"] = cartEntry.buyer.id
		buyer["name"] = cartEntry.buyer.name
		cart["buyer"] = buyer

	if "cart_item_details" in parameters and parameters["cart_item_details"] == 1:
		cartItems = filterCartItem(parameters)
		cartItems = cartItems.filter(cart_id = cartEntry.id)
		cart["cart_items"] = parseCartItem(cartItems,parameters)

	return cart

def serializeCartItem(cartItemEntry, parameters = {}):
	cartItem = {}
	cartItem["cartitemID"] = cartItemEntry.id
	cartItem["buyerID"] = cartItemEntry.buyer_id
	cartItem["cartID"] = cartItemEntry.cart_id
	cartItem["pieces"] = cartItemEntry.pieces
	cartItem["lots"] = cartItemEntry.lots
	cartItem["lot_size"] = cartItemEntry.lot_size

	cartItem["retail_price_per_piece"] = cartItemEntry.retail_price_per_piece
	cartItem["calculated_price_per_piece"] = cartItemEntry.calculated_price_per_piece
	cartItem["final_price"] = '{0:.0f}'.format(float(cartItemEntry.final_price))
	
	cartItem["created_at"] = cartItemEntry.created_at
	cartItem["updated_at"] = cartItemEntry.updated_at
	cartItem["status"] = cartItemEntry.status
	
	if "product_details" in parameters and parameters["product_details"] == 1:
		cartItem["product"] = serialize_product(cartItemEntry.product, parameters)
	else:
		product = {}
		product["id"] = cartItemEntry.product.id
		product["display_name"] = cartItemEntry.product.display_name
		product["min_price_per_unit"] = cartItemEntry.product.min_price_per_unit
		cartItem["product"] = product

	return cartItem