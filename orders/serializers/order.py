from users.serializers.buyer import serialize_buyer
from ..models.order import OrderStatus, OrderPaymentStatus
from ..models.subOrder import filterSubOrder
from ..models.payments import filterBuyerPayment
from .subOrder import serializeSubOrder
from .payments import serializeBuyerPayment

def serializeOrder(orderEntry, orderParameters = {}):
	order = {}
	order["orderID"]=orderEntry.id
	order["buyer"]=serialize_buyer(orderEntry.buyer)
	order["product_count"]=orderEntry.product_count
	order["retail_price"]=orderEntry.retail_price
	order["calculated_price"]=orderEntry.calculated_price
	order["edited_price"]=orderEntry.edited_price
	order["cod_charge"]=orderEntry.cod_charge
	order["shipping_charge"]=orderEntry.shipping_charge
	order["final_price"]=orderEntry.final_price	
	order["display_number"]=orderEntry.display_number
	order["remarks"]=orderEntry.remarks
	order["created_at"]=orderEntry.created_at
	order["updated_at"]=orderEntry.updated_at

	order["order_status"] = {
		"value": orderEntry.order_status,
		"display_value":OrderStatus[orderEntry.order_status]["display_value"]
	}

	order["order_payment_status"]= {
		"value": orderEntry.order_payment_status,
		"display_value":OrderPaymentStatus[orderEntry.order_payment_status]["display_value"]
	}

	subOrderQuerySet = filterSubOrder(orderParameters)
	subOrderQuerySet = subOrderQuerySet.filter(order_id = orderEntry.id)

	subOrders = []

	for subOrder in subOrderQuerySet:
		subOrderEntry = serializeSubOrder(subOrder)
		subOrders.append(subOrderEntry)

	order["sub_orders"] = subOrders

	buyerPaymentQuerySet = filterBuyerPayment(orderParameters)
	buyerPaymentQuerySet = buyerPaymentQuerySet.filter(order_id = orderEntry.id)
	buyerPayments = []

	for buyerPayment in buyerPaymentQuerySet:
		buyerPaymentEntry = serializeBuyerPayment(buyerPayment)
		buyerPayments.append(buyerPaymentEntry)

	order["buyer_payments"] = buyerPayments
	
	return order

def parseOrders(OrderQuerySet, orderParameters = {}):

	Orders = []

	for Order in OrderQuerySet:
		OrderEntry = serializeOrder(Order, orderParameters)
		Orders.append(OrderEntry)

	return Orders