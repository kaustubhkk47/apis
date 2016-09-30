from catalog.serializers.product import serialize_product
from users.serializers.buyer import serialize_buyer
from users.serializers.seller import serialize_seller
from ..models.cart import filterCartItem, filterSubCarts

def parseCartItem(cartItemQuerySet, parameters = {}):

	cartItems = []

	for cartItem in cartItemQuerySet:
		cartItemEntry = serializeCartItem(cartItem, parameters)
		cartItems.append(cartItemEntry)

	return cartItems

def parseCart(cartQuerySet, parameters = {}):

	carts = []

	for cart in cartQuerySet:
		cartEntry = serializeCart(cart, parameters)
		carts.append(cartEntry)

	return carts

def serializeCart(cartEntry, parameters = {}):
	cart = {}
	cart["cartID"] = cartEntry.id

	cart["pieces"] = cartEntry.pieces
	cart["product_count"] = cartEntry.product_count
	cart["retail_price"] = cartEntry.retail_price
	cart["calculated_price"] = cartEntry.calculated_price
	cart["shipping_charge"] = cartEntry.shipping_charge
	cart["final_price"] = cartEntry.final_price

	cart["created_at"] = cartEntry.created_at
	cart["updated_at"] = cartEntry.updated_at

	if "buyer_details" in parameters and parameters["buyer_details"] == 1:
		cart["buyer"]=serialize_buyer(cartEntry.buyer, parameters)
	else:
		buyer = {}
		buyer["buyerID"] = cartEntry.buyer.id
		buyer["name"] = cartEntry.buyer.name
		cart["buyer"] = buyer

	if "sub_cart_details" in parameters and parameters["sub_cart_details"] == 1:
		subCarts = filterSubCarts(parameters)
		subCarts = subCarts.filter(cart_id = cartEntry.id)
		cart["sub_carts"] = parseSubCart(subCarts,parameters)

	return cart

def parseSubCart(subcartQuerySet, parameters = {}):

	subcarts = []

	for subcart in subcartQuerySet:
		subcartEntry = serializeSubCart(subcart, parameters)
		subcarts.append(subcartEntry)

	return subcarts

def serializeSubCart(subcartEntry, parameters = {}):
	subcart = {}
	subcart["subcartID"] = subcartEntry.id

	subcart["pieces"] = subcartEntry.pieces
	subcart["product_count"] = subcartEntry.product_count
	subcart["retail_price"] = subcartEntry.retail_price
	subcart["calculated_price"] = subcartEntry.calculated_price
	subcart["shipping_charge"] = subcartEntry.shipping_charge
	subcart["final_price"] = subcartEntry.final_price
	
	subcart["created_at"] = subcartEntry.created_at
	subcart["updated_at"] = subcartEntry.updated_at

	if "seller_details" in parameters and parameters["seller_details"] == 1:
		subcart["seller"]=serialize_seller(subcartEntry.seller, parameters)
	else:
		seller = {}
		seller["sellerID"] = subcartEntry.seller.id
		seller["name"] = subcartEntry.seller.name
		subcart["seller"] = seller

	if "cart_item_details" in parameters and parameters["cart_item_details"] == 1:
		cartItems = filterCartItem(parameters)
		cartItems = cartItems.filter(subcart_id = subcartEntry.id)
		subcart["cart_items"] = parseCartItem(cartItems,parameters)

	return subcart

def serializeCartItem(cartItemEntry, parameters = {}):
	cartItem = {}
	cartItem["cartitemID"] = cartItemEntry.id
	cartItem["buyerID"] = cartItemEntry.buyer_id
	cartItem["subcartID"] = cartItemEntry.subcart_id
	cartItem["pieces"] = cartItemEntry.pieces
	cartItem["lots"] = cartItemEntry.lots
	cartItem["lot_size"] = cartItemEntry.lot_size

	cartItem["retail_price_per_piece"] = cartItemEntry.retail_price_per_piece
	cartItem["calculated_price_per_piece"] = cartItemEntry.calculated_price_per_piece
	cartItem["shipping_charge"] = cartItemEntry.shipping_charge
	cartItem["final_price"] = cartItemEntry.final_price
	
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