from users.serializers.seller import serialize_seller, serialize_seller_address
from users.serializers.buyer import serialize_buyer, serialize_buyer_address
from catalog.serializers.product import serialize_product
from ..models.orderItem import OrderItemStatus, OrderItem, OrderItemStatus
from ..models.subOrder import SubOrder, SubOrderStatus, SubOrderPaymentStatus
from ..models.orderShipment import OrderShipment, OrderShipmentStatus
from ..models.payments import BuyerPayment, SellerPayment, BuyerPaymentStatus, BuyerPaymentMethod, SellerPaymentStatus, SellerPaymentMethod
from ..models.order import Order, OrderStatus, OrderPaymentStatus

def parseOrderItem(orderItemQuerySet, orderItemParameters = {}):

	orderItems = []

	for orderItem in orderItemQuerySet:
		orderItemEntry = serializeOrderItem(orderItem, orderItemParameters)
		orderItems.append(orderItemEntry)

	return orderItems

def serializeOrderItem(orderItemEntry, orderItemParameters = {}):
	orderItem = {}
	orderItem["suborderID"] = orderItemEntry.suborder_id
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
	
	orderItem["order_item_status"] = {
		"value": orderItemEntry.current_status,
		"display_value":OrderItemStatus[orderItemEntry.current_status]["display_value"]
	}

	if orderItemEntry.order_shipment_id != None:
		orderItem["ordershipmentID"] = orderItemEntry.order_shipment_id
		orderItem["tracking_url"] = orderItemEntry.order_shipment.tracking_url

	if orderItemEntry.seller_payment_id != None:
		orderItem["sellerpaymentID"] = orderItemEntry.seller_payment_id

	return orderItem

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

def parseSellerPayments(sellerPaymentQuerySet, sellerPaymentParameters = {}):

	sellerPayments = []

	for sellerPayment in sellerPaymentQuerySet:
		sellerPaymentEntry = serializeSellerPayment(sellerPayment, sellerPaymentParameters)
		sellerPayments.append(sellerPaymentEntry)

	return sellerPayments

def serializeSellerPayment(SellerPaymentEntry, sellerPaymentParameters = {}):
	sellerPayment = {}
	sellerPayment["suborderID"] = SellerPaymentEntry.suborder_id
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

def serializeOrderShipment(orderShipmentEntry, orderShipmentParameters = {}):
	orderShipment = {}
	orderShipment["suborderID"] = orderShipmentEntry.suborder_id
	orderShipment["suborder_display_number"] =orderShipmentEntry.suborder.display_number
	orderShipment["ordershipmentID"] = orderShipmentEntry.id
	orderShipment["pickup_address"] = serialize_seller_address(orderShipmentEntry.pickup_address)
	orderShipment["drop_address"] = serialize_buyer_address(orderShipmentEntry.drop_address)
	orderShipment["invoice_number"] = orderShipmentEntry.invoice_number
	orderShipment["invoice_date"] = orderShipmentEntry.invoice_date
	orderShipment["logistics_partner"] = orderShipmentEntry.logistics_partner_name
	orderShipment["waybill_number"] = orderShipmentEntry.waybill_number
	orderShipment["packaged_weight"] = orderShipmentEntry.packaged_weight
	orderShipment["packaged_length"] = orderShipmentEntry.packaged_length
	orderShipment["packaged_breadth"] = orderShipmentEntry.packaged_breadth
	orderShipment["packaged_height"] = orderShipmentEntry.packaged_height
	orderShipment["cod_charge"] = orderShipmentEntry.cod_charge
	orderShipment["shipping_charge"] = orderShipmentEntry.shipping_charge
	orderShipment["remarks"] = orderShipmentEntry.remarks
	orderShipment["tpl_manifested_time"] = orderShipmentEntry.tpl_manifested_time
	orderShipment["tpl_in_transit_time"] = orderShipmentEntry.tpl_in_transit_time
	orderShipment["tpl_stuck_in_transit_time"] = orderShipmentEntry.tpl_stuck_in_transit_time
	orderShipment["delivered_time"] = orderShipmentEntry.delivered_time
	orderShipment["rto_in_transit_time"] = orderShipmentEntry.rto_in_transit_time
	orderShipment["rto_delivered_time"] = orderShipmentEntry.rto_delivered_time
	orderShipment["sent_for_pickup_time"] = orderShipmentEntry.sent_for_pickup_time
	orderShipment["lost_time"] = orderShipmentEntry.lost_time
	orderShipment["tracking_url"] =orderShipmentEntry.tracking_url
	orderShipment["rto_remarks"] = orderShipmentEntry.rto_remarks
	orderShipment["created_at"] = orderShipmentEntry.created_at
	orderShipment["updated_at"] = orderShipmentEntry.updated_at

	orderShipment["buyer"] = serialize_buyer(orderShipmentEntry.suborder.order.buyer)

	orderItemQuerySet = filterOrderItem(orderShipmentParameters)
	orderItemQuerySet = orderItemQuerySet.filter(order_shipment_id=orderShipmentEntry.id)
		
	orderItems = []

	for orderItem in orderItemQuerySet:
		orderItemEntry = serializeOrderItem(orderItem)
		orderItems.append(orderItemEntry)

	orderShipment["order_items"] = orderItems
	orderShipment["final_price"] = orderShipmentEntry.final_price

	orderShipment["order_shipment_status"] = {
		"value": orderShipmentEntry.current_status,
		"display_value":OrderShipmentStatus[orderShipmentEntry.current_status]["display_value"]
	}

	try:
		orderShipment["order_shipment_status"]["display_time"] = getattr(orderShipmentEntry,OrderShipmentStatus[orderShipmentEntry.current_status]["display_time"])
		orderShipment["order_shipment_status"]["display_time_name"] = OrderShipmentStatus[orderShipmentEntry.current_status]["display_time"]
	except Exception, e:
		pass
	
	return orderShipment

def parseOrderShipments(orderShipmentQuerySet, orderShipmentParameters = {}):

	orderShipments = []

	for orderShipment in orderShipmentQuerySet:
		orderShipmentEntry = serializeOrderShipment(orderShipment, orderShipmentParameters)
		orderShipments.append(orderShipmentEntry)

	return orderShipments

def filterOrderShipment(orderShipmentParameters):
	orderShipments = OrderShipment.objects.all().select_related('suborder','pickup_address','drop_address')
		
	if "orderShipmentArr" in orderShipmentParameters:
		orderShipments = orderShipments.filter(id__in=orderShipmentParameters["orderShipmentArr"])

	if "orderShipmentStatusArr" in orderShipmentParameters:
		orderShipments = orderShipments.filter(current_status__in=orderShipmentParameters["orderShipmentStatusArr"])

	if "subOrderArr" in orderShipmentParameters:
		orderShipments = orderShipments.filter(suborder_id__in=orderShipmentParameters["subOrderArr"])

	if "sellersArr" in orderShipmentParameters:
		orderShipments = orderShipments.filter(suborder__seller_id__in=orderShipmentParameters["sellersArr"])

	return orderShipments

def filterOrderItem(orderItemParameters):
	orderItems = OrderItem.objects.all().select_related('product')
		
	if "orderItemArr" in orderItemParameters:
		orderItems = orderItems.filter(id__in=orderItemParameters["orderItemArr"])

	if "orderItemStatusArr" in orderItemParameters:
		orderItems = orderItems.filter(current_status__in=orderItemParameters["orderItemStatusArr"])

	if "sellersArr" in orderItemParameters:
		orderItems = orderItems.filter(suborder__seller_id__in=orderItemParameters["sellersArr"])

	if "subOrderArr" in orderItemParameters:
		orderItems = orderItems.filter(suborder_id__in=orderItemParameters["subOrderArr"])

	if "orderArr" in orderItemParameters:
		orderItems = orderItems.filter(suborder__order_id__in=orderItemParameters["orderArr"])

	if "orderShipmentArr" in orderItemParameters:
		orderItems = orderItems.filter(order_shipment_id__in=orderItemParameters["orderShipmentArr"])

	return orderItems

def filterSellerPayment(sellerPaymentParameters):
	sellerPayments = SellerPayment.objects.all()

	if "sellerPaymentArr" in sellerPaymentParameters:
		sellerPayments = sellerPayments.filter(id__in=sellerPaymentParameters["sellerPaymentArr"])

	if "sellerPaymentStatusArr" in sellerPaymentParameters:
		sellerPayments = sellerPayments.filter(payment_status__in=sellerPaymentParameters["sellerPaymentStatusArr"])

	if "sellersArr" in sellerPaymentParameters:
		sellerPayments = sellerPayments.filter(suborder__seller_id__in=sellerPaymentParameters["sellersArr"])

	if "subOrderArr" in sellerPaymentParameters:
		sellerPayments = sellerPayments.filter(suborder_id__in=sellerPaymentParameters["subOrderArr"])

	return sellerPayments

def filterBuyerPayment(buyerPaymentParameters):
	buyerPayments = BuyerPayment.objects.all()

	if "buyerPaymentArr" in buyerPaymentParameters:
		buyerPayments = buyerPayments.filter(id__in=buyerPaymentParameters["buyerPaymentArr"])

	if "buyerPaymentStatusArr" in buyerPaymentParameters:
		buyerPayments = buyerPayments.filter(payment_status__in=buyerPaymentParameters["buyerPaymentStatusArr"])

	if "buyersArr" in buyerPaymentParameters:
		buyerPayments = buyerPayments.filter(order__buyer_id__in=buyerPaymentParameters["buyersArr"])

	if "orderArr" in buyerPaymentParameters:
		buyerPayments = buyerPayments.filter(order_id__in=buyerPaymentParameters["orderArr"])

	return buyerPayments

def filterSubOrder(subOrderParameters):
	subOrders = SubOrder.objects.all().select_related('seller','order__buyer')
		
	if "subOrderArr" in subOrderParameters:
		subOrders = subOrders.filter(id__in=subOrderParameters["subOrderArr"])

	if "subOrderStatusArr" in subOrderParameters:
		subOrders = subOrders.filter(suborder_status__in=subOrderParameters["subOrderStatusArr"])

	if "subOrderPaymentStatusArr" in subOrderParameters:
		subOrders = subOrders.filter(suborder_payment_status__in=subOrderParameters["subOrderPaymentStatusArr"])

	if "sellersArr" in subOrderParameters:
		subOrders = subOrders.filter(seller_id__in=subOrderParameters["sellersArr"])

	if "orderArr" in subOrderParameters:
		subOrders = subOrders.filter(order_id__in=subOrderParameters["orderArr"])

	return subOrders

def filterOrder(orderParameters):
	orders = Order.objects.all().select_related('buyer')
		
	if "orderArr" in orderParameters:
		orders = orders.filter(id__in=orderParameters["orderArr"])

	if "orderStatusArr" in orderParameters:
		orders = orders.filter(order_status__in=orderParameters["orderStatusArr"])

	if "orderPaymentStatusArr" in orderParameters:
		orders = orders.filter(order_payment_status__in=orderParameters["orderPaymentStatusArr"])

	if "buyersArr" in orderParameters:
		orders = orders.filter(buyer_id__in=orderParameters["buyersArr"])

	return orders