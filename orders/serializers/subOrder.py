from users.serializers.seller import serialize_seller
from users.serializers.buyer import serialize_buyer
from ..models.subOrder import SubOrderStatus, SubOrderPaymentStatus
from ..models.orderItem import filterOrderItem
from ..models.orderShipment import filterOrderShipment
from ..models.payments import filterSellerPayment
from .orderItem import serializeOrderItem
from .orderShipment import serializeOrderShipment
from .payments import serializeSellerPayment

def serializeSubOrder(subOrderEntry, subOrderParameters = {}):
	subOrder = {}
	subOrder["orderID"]=subOrderEntry.order_id
	subOrder["suborderID"]=subOrderEntry.id
	subOrder["seller"]=serialize_seller(subOrderEntry.seller)
	subOrder["buyer"]=serialize_buyer(subOrderEntry.order.buyer)
	subOrder["product_count"] = subOrderEntry.product_count
	subOrder["retail_price"] = subOrderEntry.retail_price
	subOrder["calculated_price"] = subOrderEntry.calculated_price
	subOrder["edited_price"] = subOrderEntry.edited_price
	subOrder["cod_charge"] = subOrderEntry.cod_charge
	subOrder["shipping_charge"] = subOrderEntry.shipping_charge
	subOrder["final_price"] = subOrderEntry.final_price
	
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

	sellerPaymentQuerySet = filterSellerPayment(subOrderParameters)
	sellerPaymentQuerySet = sellerPaymentQuerySet.filter(suborder_id=subOrderEntry.id)
	sellerPayments = []

	for sellerPayment in sellerPaymentQuerySet:
		sellerPaymentEntry = serializeSellerPayment(sellerPayment)
		sellerPayments.append(sellerPaymentEntry)

	subOrder["seller_payments"] = sellerPayments

	orderShipmentQuerySet = filterOrderShipment(subOrderParameters)
	orderShipmentQuerySet = orderShipmentQuerySet.filter(suborder_id=subOrderEntry.id)
	orderShipments = []

	for orderShipment in orderShipmentQuerySet:
		orderShipmentEntry = serializeOrderShipment(orderShipment)
		orderShipments.append(orderShipmentEntry)

	subOrder["order_shipments"] = orderShipments

	orderItemQuerySet = filterOrderItem(subOrderParameters)
	orderItemQuerySet = orderItemQuerySet.filter(suborder_id=subOrderEntry.id)
	orderItems = []

	for orderItem in orderItemQuerySet:
		orderItemEntry = serializeOrderItem(orderItem)
		orderItems.append(orderItemEntry)

	subOrder["order_items"] = orderItems
		
	return subOrder

def parseSubOrders(subOrderQuerySet, subOrderParameters = {}):

	subOrders = []

	for subOrder in subOrderQuerySet:
		subOrderEntry = serializeSubOrder(subOrder, subOrderParameters)
		subOrders.append(subOrderEntry)

	return subOrders
