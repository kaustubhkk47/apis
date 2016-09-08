from orders.serializers.cart import serializeCart
from users.serializers.buyer import serialize_buyer_address

from orders.models.checkout import CheckoutStatus

def parseCheckout(checkoutQuerySet, parameters = {}):

	checkouts = []

	for checkout in checkoutQuerySet:
		checkoutEntry = serializeCheckout(checkout, parameters)
		checkouts.append(checkoutEntry)

	return checkouts

def serializeCheckout(checkoutEntry, parameters = {}):
	checkout = {}

	checkout["checkoutID"] = checkoutEntry.id

	checkout["cart"] = serializeCart(checkoutEntry.cart, parameters)

	if hasattr(checkoutEntry, "buyer_address_history") and checkoutEntry.buyer_address_history != None:
		checkout["buyer_address"] = serialize_buyer_address(checkoutEntry.buyer_address_history, parameters)

	checkout["status"] = {
		"value": checkoutEntry.status,
		"display_value":CheckoutStatus[checkoutEntry.status]["display_value"]
	}

	checkout["payment_method"] = checkoutEntry.payment_method

	checkout["created_at"] = checkoutEntry.created_at
	checkout["updated_at"] = checkoutEntry.updated_at
	checkout["address_given_time"] = checkoutEntry.address_given_time
	checkout["summary_confirmed_time"] = checkoutEntry.summary_confirmed_time
	checkout["payment_done_time"] = checkoutEntry.payment_done_time

	return checkout