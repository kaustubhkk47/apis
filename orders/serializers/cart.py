from catalog.serializers.product import serialize_product

def parseCartItem(cartItemQuerySet, cartItemParameters = {}):

	cartItems = []

	for cartItem in cartItemQuerySet:
		cartItemEntry = serializeCartItem(cartItem, cartItemParameters)
		cartItems.append(cartItemEntry)

	return cartItems

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