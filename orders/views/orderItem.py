from scripts.utils import *
import json
import logging
log = logging.getLogger("django")
from ..models.orderItem import filterOrderItem, OrderItem
from ..serializers.orderItem import parseOrderItem
import datetime

def get_order_item_details(request, orderItemParameters):
	try:

		orderItems = filterOrderItem(orderItemParameters)
		body = parseOrderItem(orderItems,orderItemParameters)
		statusCode = "2XX"
		response = {"order_items": body}

	except Exception as e:
		log.critical(e)
		statusCode = "4XX"
		response = {"error": "Invalid request"}

	closeDBConnection()
	return customResponse(statusCode, response)

def cancel_order_item(request):
	try:
		requestbody = request.body.decode("utf-8")
		orderItem = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse("4XX", {"error": "Invalid data sent in request"})

	if not len(orderItem) or not "orderitemID" in orderItem or orderItem["orderitemID"]==None:
		return customResponse("4XX", {"error": "Id for order item not sent"})

	orderItemPtr = OrderItem.objects.filter(id=int(orderItem["orderitemID"])).select_related('suborder', 'suborder__order')

	if len(orderItemPtr) == 0:
		return customResponse("4XX", {"error": "Invalid id for order item sent"})

	orderItemPtr = orderItemPtr[0]

	if not "cancellation_remarks" in orderItem or orderItem["cancellation_remarks"]==None:
		orderItem["cancellation_remarks"] = ""

	if orderItemPtr.current_status == 4:
		return customResponse("4XX", {"error": "Already cancelled"})

	try:
		orderItemPtr.current_status = 4
		orderItemPtr.cancellation_remarks = orderItem["cancellation_remarks"]
		orderItemPtr.cancellation_time = datetime.datetime.now()
		orderItemPtr.save()

		orderItemPtr.suborder.product_count -= 1
		orderItemPtr.suborder.retail_price -= orderItemPtr.pieces*orderItemPtr.retail_price_per_piece
		orderItemPtr.suborder.calculated_price -= orderItemPtr.pieces*orderItemPtr.calculated_price_per_piece
		orderItemPtr.suborder.edited_price -= orderItemPtr.pieces*orderItemPtr.edited_price_per_piece
		orderItemPtr.suborder.final_price -= orderItemPtr.final_price
		orderItemPtr.suborder.save()

		orderItemPtr.suborder.order.product_count -= 1
		orderItemPtr.suborder.order.retail_price -= orderItemPtr.pieces*orderItemPtr.retail_price_per_piece
		orderItemPtr.suborder.order.calculated_price -= orderItemPtr.pieces*orderItemPtr.calculated_price_per_piece
		orderItemPtr.suborder.order.edited_price -= orderItemPtr.pieces*orderItemPtr.edited_price_per_piece
		orderItemPtr.suborder.order.final_price -= orderItemPtr.final_price
		orderItemPtr.suborder.order.save()

		if orderItemPtr.order_shipment != None:
			orderItemPtr.order_shipment.final_price -= orderItemPtr.final_price
			orderItemPtr.order_shipment.save()
		
	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse("4XX", {"error": "could not update"})
	else:
		closeDBConnection()
		return customResponse("2XX", {"order": "order updated"})