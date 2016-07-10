from catalog.serializers.product import serialize_product
from ..models.orderItem import OrderItemStatus

def parseOrderItem(orderItemQuerySet, orderItemParameters = {}):

	orderItems = []

	for orderItem in orderItemQuerySet:
		orderItemEntry = serializeOrderItem(orderItem, orderItemParameters)
		orderItems.append(orderItemEntry)

	return orderItems

def serializeOrderItem(orderItemEntry, parameters = {}):
	orderItem = {}
	orderItem["suborderID"] = orderItemEntry.suborder_id
	orderItem["orderitemID"] = orderItemEntry.id
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

	if "product_details" in parameters and parameters["product_details"] == 1:
		orderItem["product"] = serialize_product(orderItemEntry.product)
	else:
		product = {}
		product["id"] = orderItemEntry.product.id
		product["display_name"] = orderItemEntry.product.display_name
		product["min_price_per_unit"] = orderItemEntry.product.min_price_per_unit
		orderItem["product"] = product

	return orderItem