from users.serializers.seller import serialize_seller, serialize_seller_address
from users.serializers.buyer import serialize_buyer, serialize_buyer_address
from catalog.serializers.product import serialize_product
from ..models.orderItem import OrderItemStatus, OrderItem
from ..models.subOrder import SubOrder
from ..models.orderShipment import OrderShipment
from ..models.payments import BuyerPayment, SellerPayment

def parseOrderItem(orderItemQuerySet):

	orderItems = []

	for orderItem in orderItemQuerySet:
		orderItemEntry = serializeOrderItem(orderItem)
		orderItems.append(orderItemEntry)

	return orderItems

def serializeOrderItem(orderItemEntry):
	orderItem = {}
	orderItem["suborderID"] = orderItemEntry.suborder_id
	orderItem["ordershipmentID"] = orderItemEntry.order_shipment_id
	orderItem["sellerpaymentID"] = orderItemEntry.seller_payment_id
	orderItem["orderitemID"] = orderItemEntry.id
	orderItem["product"] = serialize_product(orderItemEntry.product)
	orderItem["pieces"] = orderItemEntry.pieces
	orderItem["lots"] = orderItemEntry.lots
	orderItem["retail_price_per_piece"] = orderItemEntry.retail_price_per_piece
	orderItem["calculated_price_per_piece"] = orderItemEntry.calculated_price_per_piece
	orderItem["edited_price_per_piece"] = orderItemEntry.edited_price_per_piece
	orderItem["final_price"] = orderItemEntry.final_price
	orderItem["lot_size"] = orderItemEntry.lot_size
	orderItem["created_at"] = orderItemEntry.created_at
	orderItem["updated_at"] = orderItemEntry.updated_at
	orderItem["current_status"] = orderItemEntry.current_status
	orderItem["remarks"] = orderItemEntry.remarks
	orderItem["cancellation_remarks"] = orderItemEntry.cancellation_remarks
	orderItem["cancellation_time"] = orderItemEntry.cancellation_time
	return orderItem

def serializeSubOrder(subOrderEntry):
	subOrder = {}
	subOrder["orderID"]=subOrderEntry.order_id
	subOrder["suborderID"]=subOrderEntry.id
	subOrder["seller"]=serialize_seller(subOrderEntry.seller)
	subOrder["product_count"] = subOrderEntry.product_count
	subOrder["retail_price"] = subOrderEntry.retail_price
	subOrder["calculated_price"] = subOrderEntry.calculated_price
	subOrder["edited_price"] = subOrderEntry.edited_price
	subOrder["cod_charge"] = subOrderEntry.cod_charge
	subOrder["shipping_charge"] = subOrderEntry.shipping_charge
	subOrder["final_price"] = subOrderEntry.final_price
	subOrder["suborder_status"] = subOrderEntry.suborder_status
	subOrder["display_number"] = subOrderEntry.display_number
	subOrder["created_at"] = subOrderEntry.created_at
	subOrder["updated_at"] = subOrderEntry.updated_at
	subOrder["merchant_notified_time"] = subOrderEntry.merchant_notified_time
	subOrder["completed_time"] = subOrderEntry.completed_time
	subOrder["closed_time"] = subOrderEntry.closed_time

	sellerPaymentQuerySet = SellerPayment.objects.filter(suborder_id = subOrderEntry.id)
	sellerPayments = []

	for sellerPayment in sellerPaymentQuerySet:
		sellerPaymentEntry = serializeSellerPayment(sellerPayment)
		sellerPayments.append(sellerPaymentEntry)

	subOrder["seller_payments"] = sellerPayments

	orderShipmentQuerySet = OrderShipment.objects.filter(suborder_id = subOrderEntry.id)
	orderShipments = []

	for orderShipment in orderShipmentQuerySet:
		orderShipmentEntry = serializeOrderShipment(orderShipment)
		orderShipments.append(orderShipmentEntry)

	subOrder["order_shipments"] = orderShipments

	orderItemQuerySet = OrderItem.objects.filter(suborder_id = subOrderEntry.id).select_related('product')
	orderItems = []

	for orderItem in orderItemQuerySet:
		orderItemEntry = serializeOrderItem(orderItem)
		orderItems.append(orderItemEntry)

	subOrder["order_items"] = orderItems
		
	return subOrder

def parseSubOrders(subOrderQuerySet):

	subOrders = []

	for subOrder in subOrderQuerySet:
		subOrderEntry = serializeSubOrder(subOrder)
		subOrders.append(subOrderEntry)

	return subOrders

def serializeSellerPayment(SellerPaymentEntry):
	sellerPayment = {}
	sellerPayment["suborderID"] = SellerPaymentEntry.suborder_id
	sellerPayment["sellerpaymentID"] = SellerPaymentEntry.id
	sellerPayment["payment_status"] = SellerPaymentEntry.payment_status
	sellerPayment["payment_method"] = SellerPaymentEntry.payment_method
	sellerPayment["reference_number"] = SellerPaymentEntry.reference_number
	sellerPayment["payment_time"] = SellerPaymentEntry.payment_time
	sellerPayment["details"] = SellerPaymentEntry.details
	sellerPayment["payment_value"] = SellerPaymentEntry.payment_value
	sellerPayment["created_at"] = SellerPaymentEntry.created_at
	sellerPayment["updated_at"] = SellerPaymentEntry.updated_at

	orderItemQuerySet = OrderItem.objects.filter(seller_payment_id = SellerPaymentEntry.id).select_related('product')
	orderItems = []

	for orderItem in orderItemQuerySet:
		orderItemEntry = serializeOrderItem(orderItem)
		orderItems.append(orderItemEntry)

	sellerPayment["order_items"] = orderItems

	return sellerPayment

def serializeOrder(orderEntry):
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
	order["order_status"]=orderEntry.order_status
	order["display_number"]=orderEntry.display_number
	order["remarks"]=orderEntry.remarks
	order["created_at"]=orderEntry.created_at
	order["updated_at"]=orderEntry.updated_at

	subOrderQuerySet = SubOrder.objects.filter(order_id = orderEntry.id).select_related('seller')
	subOrders = []

	for subOrder in subOrderQuerySet:
		subOrderEntry = serializeSubOrder(subOrder)
		subOrders.append(subOrderEntry)

	order["sub_orders"] = subOrders

	buyerPaymentQuerySet = BuyerPayment.objects.filter(order_id = orderEntry.id)
	buyerPayments = []

	for buyerPayment in buyerPaymentQuerySet:
		buyerPaymentEntry = serializeBuyerPayment(buyerPayment)
		buyerPayments.append(buyerPaymentEntry)

	order["buyer_payments"] = buyerPayments
	
	return order

def parseOrders(OrderQuerySet):

	Orders = []

	for Order in OrderQuerySet:
		OrderEntry = serializeOrder(Order)
		Orders.append(OrderEntry)

	return Orders

def serializeBuyerPayment(BuyerPaymentEntry):
	buyerPayment = {}
	buyerPayment["orderID"] = BuyerPaymentEntry.order_id
	buyerPayment["buyerpaymentID"] = BuyerPaymentEntry.id
	buyerPayment["payment_status"] = BuyerPaymentEntry.payment_status
	buyerPayment["payment_method"] = BuyerPaymentEntry.payment_method
	buyerPayment["reference_number"] = BuyerPaymentEntry.reference_number
	buyerPayment["payment_time"] = BuyerPaymentEntry.payment_time
	buyerPayment["details"] = BuyerPaymentEntry.details
	buyerPayment["payment_value"] = BuyerPaymentEntry.payment_value
	buyerPayment["created_at"] = BuyerPaymentEntry.created_at
	buyerPayment["updated_at"] = BuyerPaymentEntry.updated_at

	return buyerPayment

def serializeOrderShipment(orderShipmentEntry):
	orderShipment = {
		"suborderID":orderShipmentEntry.suborder_id,
		"ordershipmentID": orderShipmentEntry.id,
		"pickup_address": serialize_seller_address(orderShipmentEntry.pickup_address),
		"drop_address": serialize_buyer_address(orderShipmentEntry.drop_address),
		"invoice_number": orderShipmentEntry.invoice_number,
		"invoice_date": orderShipmentEntry.invoice_date,
		"logistics_partner": orderShipmentEntry.logistics_partner,
		"waybill_number": orderShipmentEntry.waybill_number,
		"packaged_weight": orderShipmentEntry.packaged_weight,
		"packaged_length": orderShipmentEntry.packaged_length,
		"packaged_breadth": orderShipmentEntry.packaged_breadth,
		"packaged_height": orderShipmentEntry.packaged_height,
		"cod_charge": orderShipmentEntry.cod_charge,
		"shipping_charge": orderShipmentEntry.shipping_charge,
		"remarks": orderShipmentEntry.remarks,
		"current_status": orderShipmentEntry.current_status,
		"tpl_manifested_time": orderShipmentEntry.tpl_manifested_time,
		"tpl_in_transit_time": orderShipmentEntry.tpl_in_transit_time,
		"tpl_stuck_in_transit_time": orderShipmentEntry.tpl_stuck_in_transit_time,
		"delivered_time": orderShipmentEntry.delivered_time,
		"rto_in_transit_time": orderShipmentEntry.rto_in_transit_time,
		"rto_delivered_time":orderShipmentEntry.rto_delivered_time,
		"sent_for_pickup_time":orderShipmentEntry.sent_for_pickup_time,
		"lost_time":orderShipmentEntry.lost_time,
		"tracking_url":orderShipmentEntry.tracking_url,
		"rto_remarks": orderShipmentEntry.rto_remarks,
		"created_at": orderShipmentEntry.created_at,
		"updated_at": orderShipmentEntry.updated_at
	}

	orderItemQuerySet = OrderItem.objects.filter(order_shipment_id = orderShipmentEntry.id).select_related('product')
	orderItems = []

	for orderItem in orderItemQuerySet:
		orderItemEntry = serializeOrderItem(orderItem)
		orderItems.append(orderItemEntry)

	orderShipment["order_items"] = orderItems
	
	return orderShipment

def parseOrderShipments(orderShipmentQuerySet):

	orderShipments = []

	for orderShipment in orderShipmentQuerySet:
		orderShipmentEntry = serializeOrderShipment(orderShipment)
		orderShipments.append(orderShipmentEntry)

	return orderShipments
