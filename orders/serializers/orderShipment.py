from users.serializers.seller import serialize_seller, serialize_seller_address
from users.serializers.buyer import serialize_buyer, serialize_buyer_address
from ..models.orderShipment import OrderShipmentStatus

from ..models.orderItem import filterOrderItem
from .orderItem import serializeOrderItem

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
	orderShipment["seller"] = serialize_seller(orderShipmentEntry.suborder.seller)

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