from users.serializers.seller import serialize_seller, serialize_seller_address
from users.serializers.buyer import serialize_buyer, serialize_buyer_address
from ..models.orderShipment import OrderShipmentStatus

from ..models.orderItem import filterOrderItem
from .orderItem import serializeOrderItem, parseOrderItem

def serializeOrderShipment(orderShipmentEntry, parameters = {}):
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
	orderShipment["cod_charge"] = '{0:.0f}'.format(float(orderShipmentEntry.cod_charge))
	orderShipment["shipping_charge"] = '{0:.0f}'.format(float(orderShipmentEntry.shipping_charge))
	orderShipment["pieces"] = orderShipmentEntry.pieces
	orderShipment["product_count"] = orderShipmentEntry.product_count
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
	orderShipment["manifest_link"] = orderShipmentEntry.manifest_link
	orderShipment["label_link"] = orderShipmentEntry.label_link
	orderShipment["soft_data_csv_link"] = orderShipmentEntry.soft_data_csv_link
	orderShipment["vendor_pickup_csv_link"] = orderShipmentEntry.vendor_pickup_csv_link
	orderShipment["final_price"] = '{0:.0f}'.format(float(orderShipmentEntry.final_price))
	orderShipment["amount_to_collect"] = '{0:.0f}'.format(float(orderShipmentEntry.final_price) + float(orderShipmentEntry.cod_charge) + float(orderShipmentEntry.shipping_charge))

	if "buyer_details" in parameters and parameters["buyer_details"] == 1:
		orderShipment["buyer"] = serialize_buyer(orderShipmentEntry.suborder.order.buyer, parameters)
	else:
		buyer = {}
		buyer["buyerID"] = orderShipmentEntry.suborder.order.buyer.id
		buyer["name"] = orderShipmentEntry.suborder.order.buyer.name
		orderShipment["buyer"] = buyer

	if "seller_details" in parameters and parameters["seller_details"] == 1:
		orderShipment["seller"] = serialize_seller(orderShipmentEntry.suborder.seller, parameters)
	else:
		seller = {}
		seller["sellerID"] = orderShipmentEntry.suborder.seller.id
		seller["name"] = orderShipmentEntry.suborder.seller.name
		orderShipment["seller"] = seller

	if "order_item_details" in parameters and parameters["order_item_details"] ==1:
		orderItemQuerySet = filterOrderItem(parameters)
		orderItemQuerySet = orderItemQuerySet.filter(order_shipment_id=orderShipmentEntry.id)
		orderShipment["order_items"] = parseOrderItem(orderItemQuerySet,parameters)

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

def parseOrderShipments(orderShipmentQuerySet, parameters = {}):

	orderShipments = []

	for orderShipment in orderShipmentQuerySet:
		orderShipmentEntry = serializeOrderShipment(orderShipment, parameters)
		orderShipments.append(orderShipmentEntry)

	return orderShipments