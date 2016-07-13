from users.serializers.seller import serialize_seller
from users.serializers.buyer import serialize_buyer
from ..models.payments import BuyerPaymentStatus, BuyerPaymentMethod, SellerPaymentStatus, SellerPaymentMethod
from ..models.orderItem import filterOrderItem
from .orderItem import serializeOrderItem, parseOrderItem

def parseSellerPayments(sellerPaymentQuerySet, parameters = {}):

	sellerPayments = []

	for sellerPayment in sellerPaymentQuerySet:
		sellerPaymentEntry = serializeSellerPayment(sellerPayment, parameters)
		sellerPayments.append(sellerPaymentEntry)

	return sellerPayments

def serializeSellerPayment(SellerPaymentEntry, parameters = {}):
	sellerPayment = {}
	sellerPayment["suborderID"] = SellerPaymentEntry.suborder_id
	sellerPayment["suborder_display_number"] = SellerPaymentEntry.suborder.display_number
	sellerPayment["sellerpaymentID"] = SellerPaymentEntry.id	
	sellerPayment["reference_number"] = SellerPaymentEntry.reference_number
	sellerPayment["payment_time"] = SellerPaymentEntry.payment_time
	sellerPayment["details"] = SellerPaymentEntry.details
	sellerPayment["payment_value"] = '{0:.0f}'.format(float(SellerPaymentEntry.payment_value))
	sellerPayment["created_at"] = SellerPaymentEntry.created_at
	sellerPayment["updated_at"] = SellerPaymentEntry.updated_at

	sellerPayment["seller_payment_status"] = {
		"value": SellerPaymentEntry.payment_status,
		"display_value":SellerPaymentStatus[SellerPaymentEntry.payment_status]["display_value"]
	}

	sellerPayment["seller_payment_method"] = {
		"value": SellerPaymentEntry.payment_method,
		"display_value":SellerPaymentMethod[SellerPaymentEntry.payment_method]["display_value"]
	}

	if "seller_details" in parameters and parameters["seller_details"] == 1:
		sellerPayment["seller"] = serialize_seller(SellerPaymentEntry.suborder.seller, parameters)
	else:
		seller = {}
		seller["sellerID"] = SellerPaymentEntry.suborder.seller.id
		seller["name"] = SellerPaymentEntry.suborder.seller.name
		sellerPayment["seller"] = seller

	if "order_item_details" in parameters and parameters["order_item_details"] == 1:
		orderItemQuerySet = filterOrderItem(parameters)
		orderItemQuerySet = orderItemQuerySet.filter(seller_payment_id = SellerPaymentEntry.id)
		sellerPayment["order_items"] = parseOrderItem(orderItemQuerySet, parameters)

	return sellerPayment

def serializeBuyerPayment(BuyerPaymentEntry, parameters= {}):
	buyerPayment = {}
	buyerPayment["orderID"] = BuyerPaymentEntry.order_id
	buyerPayment["buyerpaymentID"] = BuyerPaymentEntry.id
	buyerPayment["reference_number"] = BuyerPaymentEntry.reference_number
	buyerPayment["payment_time"] = BuyerPaymentEntry.payment_time
	buyerPayment["details"] = BuyerPaymentEntry.details
	buyerPayment["payment_value"] = '{0:.0f}'.format(float(BuyerPaymentEntry.payment_value))
	buyerPayment["created_at"] = BuyerPaymentEntry.created_at
	buyerPayment["updated_at"] = BuyerPaymentEntry.updated_at

	if "buyer_details" in parameters and parameters["buyer_details"] == 1:
		buyerPayment["buyer"] = serialize_buyer(BuyerPaymentEntry.order.buyer, parameters)
	else:
		buyer = {}
		buyer["buyerID"] = BuyerPaymentEntry.order.buyer.id
		buyer["name"] = BuyerPaymentEntry.order.buyer.name
		buyerPayment["buyer"] = buyer

	buyerPayment["buyer_payment_status"] = {
		"value": BuyerPaymentEntry.payment_status,
		"display_value":BuyerPaymentStatus[BuyerPaymentEntry.payment_status]["display_value"]
	}

	buyerPayment["buyer_payment_method"] = {
		"value": BuyerPaymentEntry.payment_method,
		"display_value":BuyerPaymentMethod[BuyerPaymentEntry.payment_method]["display_value"]
	}

	if BuyerPaymentEntry.order_shipment != None:
		buyerPayment["ordershipmentID"] = BuyerPaymentEntry.order_shipment_id

	return buyerPayment

def parseBuyerPayments(buyerPaymentQuerySet, parameters = {}):

	buyerPayments = []

	for buyerPayment in buyerPaymentQuerySet:
		buyerPaymentEntry = serializeBuyerPayment(buyerPayment, parameters)
		buyerPayments.append(buyerPaymentEntry)

	return buyerPayments