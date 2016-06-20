from users.serializers.seller import serialize_seller
from users.serializers.buyer import serialize_buyer
from ..models.payments import BuyerPaymentStatus, BuyerPaymentMethod, SellerPaymentStatus, SellerPaymentMethod
from ..models.orderItem import filterOrderItem
from .orderItem import serializeOrderItem

def parseSellerPayments(sellerPaymentQuerySet, sellerPaymentParameters = {}):

	sellerPayments = []

	for sellerPayment in sellerPaymentQuerySet:
		sellerPaymentEntry = serializeSellerPayment(sellerPayment, sellerPaymentParameters)
		sellerPayments.append(sellerPaymentEntry)

	return sellerPayments

def serializeSellerPayment(SellerPaymentEntry, sellerPaymentParameters = {}):
	sellerPayment = {}
	sellerPayment["suborderID"] = SellerPaymentEntry.suborder_id
	sellerPayment["suborder_display_number"] = SellerPaymentEntry.suborder.display_number
	sellerPayment["sellerpaymentID"] = SellerPaymentEntry.id	
	sellerPayment["reference_number"] = SellerPaymentEntry.reference_number
	sellerPayment["payment_time"] = SellerPaymentEntry.payment_time
	sellerPayment["details"] = SellerPaymentEntry.details
	sellerPayment["payment_value"] = SellerPaymentEntry.payment_value
	sellerPayment["created_at"] = SellerPaymentEntry.created_at
	sellerPayment["updated_at"] = SellerPaymentEntry.updated_at

	sellerPayment["seller"] = serialize_seller(SellerPaymentEntry.suborder.seller)

	sellerPayment["seller_payment_status"] = {
		"value": SellerPaymentEntry.payment_status,
		"display_value":SellerPaymentStatus[SellerPaymentEntry.payment_status]["display_value"]
	}

	sellerPayment["seller_payment_method"] = {
		"value": SellerPaymentEntry.payment_method,
		"display_value":SellerPaymentMethod[SellerPaymentEntry.payment_method]["display_value"]
	}

	orderItemQuerySet = filterOrderItem(sellerPaymentParameters)
	orderItemQuerySet = orderItemQuerySet.filter(seller_payment_id = SellerPaymentEntry.id)
	orderItems = []

	for orderItem in orderItemQuerySet:
		orderItemEntry = serializeOrderItem(orderItem)
		orderItems.append(orderItemEntry)

	sellerPayment["order_items"] = orderItems

	return sellerPayment

def serializeBuyerPayment(BuyerPaymentEntry, buyerPaymentParameters= {}):
	buyerPayment = {}
	buyerPayment["orderID"] = BuyerPaymentEntry.order_id
	buyerPayment["buyerpaymentID"] = BuyerPaymentEntry.id
	buyerPayment["reference_number"] = BuyerPaymentEntry.reference_number
	buyerPayment["payment_time"] = BuyerPaymentEntry.payment_time
	buyerPayment["details"] = BuyerPaymentEntry.details
	buyerPayment["payment_value"] = BuyerPaymentEntry.payment_value
	buyerPayment["created_at"] = BuyerPaymentEntry.created_at
	buyerPayment["updated_at"] = BuyerPaymentEntry.updated_at

	buyerPayment["buyer"] = serialize_buyer(BuyerPaymentEntry.order.buyer)

	buyerPayment["buyer_payment_status"] = {
		"value": BuyerPaymentEntry.payment_status,
		"display_value":BuyerPaymentStatus[BuyerPaymentEntry.payment_status]["display_value"]
	}

	buyerPayment["buyer_payment_method"] = {
		"value": BuyerPaymentEntry.payment_method,
		"display_value":BuyerPaymentMethod[BuyerPaymentEntry.payment_method]["display_value"]
	}

	if BuyerPaymentEntry.order_shipment != None:
		buyerPayment["ordershipmentID"] = BuyerPaymentEntry.order_shipment.id

	return buyerPayment

def parseBuyerPayments(buyerPaymentQuerySet, buyerPaymentParameters = {}):

	buyerPayments = []

	for buyerPayment in buyerPaymentQuerySet:
		buyerPaymentEntry = serializeBuyerPayment(buyerPayment, buyerPaymentParameters)
		buyerPayments.append(buyerPaymentEntry)

	return buyerPayments