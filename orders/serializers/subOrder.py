from users.serializers.seller import serialize_seller, serialize_seller_address
from users.serializers.buyer import serialize_buyer
from ..models.subOrder import SubOrderStatus, SubOrderPaymentStatus
from ..models.orderItem import filterOrderItem
from ..models.orderShipment import filterOrderShipment
from ..models.payments import filterSellerPayment
from .orderItem import serializeOrderItem, parseOrderItem
from .orderShipment import serializeOrderShipment, parseOrderShipments
from .payments import serializeSellerPayment, parseSellerPayments

def serializeSubOrder(subOrderEntry, parameters = {}):
	subOrder = {}
	subOrder["orderID"]=subOrderEntry.order_id
	subOrder["suborderID"]=subOrderEntry.id
	subOrder["product_count"] = subOrderEntry.product_count
	subOrder["pieces"] = subOrderEntry.pieces
	subOrder["retail_price"] = '{0:.0f}'.format(float(subOrderEntry.retail_price))
	subOrder["calculated_price"] = '{0:.0f}'.format(float(subOrderEntry.calculated_price))
	subOrder["edited_price"] = '{0:.0f}'.format(float(subOrderEntry.edited_price))
	subOrder["cod_charge"] = '{0:.0f}'.format(float(subOrderEntry.cod_charge))
	subOrder["shipping_charge"] = '{0:.0f}'.format(float(subOrderEntry.shipping_charge))
	subOrder["final_price"] = '{0:.0f}'.format(float(subOrderEntry.final_price))
	subOrder["display_number"] = subOrderEntry.display_number
	subOrder["created_at"] = subOrderEntry.created_at
	subOrder["updated_at"] = subOrderEntry.updated_at
	subOrder["merchant_notified_time"] = subOrderEntry.merchant_notified_time
	subOrder["completed_time"] = subOrderEntry.completed_time
	subOrder["closed_time"] = subOrderEntry.closed_time

	subOrder["sub_order_status"] = {
		"value": subOrderEntry.suborder_status,
		"display_value":SubOrderStatus[subOrderEntry.suborder_status]["display_value"]
	}

	subOrder["sub_order_payment_status"] = {
		"value": subOrderEntry.suborder_payment_status,
		"display_value":SubOrderPaymentStatus[subOrderEntry.suborder_payment_status]["display_value"]
	}

	subOrder["seller_address"] = serialize_seller_address(subOrderEntry.seller_address_history)

	if "seller_details" in parameters and parameters["seller_details"] == 1:
		subOrder["seller"]=serialize_seller(subOrderEntry.seller, parameters)
	else:
		seller = {}
		seller["sellerID"] = subOrderEntry.seller.id
		seller["name"] = subOrderEntry.seller.name
		subOrder["seller"] = seller

	if "buyer_details" in parameters and parameters["buyer_details"] == 1:
		subOrder["buyer"]=serialize_buyer(subOrderEntry.order.buyer, parameters)
	else:
		buyer = {}
		buyer["buyerID"] = subOrderEntry.order.buyer.id
		buyer["name"] = subOrderEntry.order.buyer.name
		subOrder["buyer"] = buyer
	
	if "seller_payment_details" in parameters and parameters["seller_payment_details"] == 1:
		sellerPaymentQuerySet = filterSellerPayment(parameters)
		sellerPaymentQuerySet = sellerPaymentQuerySet.filter(suborder_id=subOrderEntry.id)
		subOrder["seller_payments"] = parseSellerPayments(sellerPaymentQuerySet, parameters)

	if "order_shipment_details" in parameters and parameters["order_shipment_details"] == 1:
		orderShipmentQuerySet = filterOrderShipment(parameters)
		orderShipmentQuerySet = orderShipmentQuerySet.filter(suborder_id=subOrderEntry.id)
		subOrder["order_shipments"] = parseOrderShipments(orderShipmentQuerySet, parameters)

	if "order_item_details" in parameters and parameters["order_item_details"] == 1:
		orderItemQuerySet = filterOrderItem(parameters)
		orderItemQuerySet = orderItemQuerySet.filter(suborder_id=subOrderEntry.id)
		subOrder["order_items"] = parseOrderItem(orderItemQuerySet, parameters)
		
	return subOrder

def parseSubOrders(subOrderQuerySet, parameters = {}):

	subOrders = []

	for subOrder in subOrderQuerySet:
		subOrderEntry = serializeSubOrder(subOrder, parameters)
		subOrders.append(subOrderEntry)

	return subOrders
