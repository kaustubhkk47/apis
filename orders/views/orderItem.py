from scripts.utils import *
import json
import logging
log = logging.getLogger("django")
from ..models.orderItem import filterOrderItem, OrderItem
from ..models.subOrder import sendSubOrderCancellationMail, populateSellerMailDict
from users.models.buyer import BuyerAddress
from ..serializers.orderItem import parseOrderItem
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def get_order_item_details(request, orderItemParameters):
	try:

		orderItems = filterOrderItem(orderItemParameters)

		statusCode = "2XX"

		paginator = Paginator(orderItems, orderItemParameters["itemsPerPage"])

		try:
			pageItems = paginator.page(orderItemParameters["pageNumber"])
		except Exception as e:
			pageItems = []

		body = parseOrderItem(pageItems,orderItemParameters)
		statusCode = "2XX"
		response = {"order_items": body,"total_items":paginator.count, "total_pages":paginator.num_pages, "page_number":orderItemParameters["pageNumber"], "items_per_page":orderItemParameters["itemsPerPage"]}

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

	if not len(orderItem) or not "orderitemID" in orderItem or not validate_integer(orderItem["orderitemID"]):
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
		orderItemPtr.cancellation_time = timezone.now()
		orderItemPtr.save()
		"""
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
		"""

		isOrderCancelled = 1

		allOrderItems = OrderItem.objects.filter(suborder__order_id=orderItemPtr.suborder.order_id)

		for orderItem in allOrderItems:
			if orderItem.current_status != 4:
				isOrderCancelled = 0
				break

		if isOrderCancelled == 1:
			orderItemPtr.suborder.order.order_status = -1
			orderItemPtr.suborder.order.save()

		isSubOrderCancelled = 1

		allSubOrderItems = OrderItem.objects.filter(suborder_id=orderItemPtr.suborder_id)

		for orderItem in allSubOrderItems:
			if orderItem.current_status != 4:
				isSubOrderCancelled = 0
				break

		if isSubOrderCancelled == 1:
			SubOrderPtr = orderItemPtr.suborder
			SubOrderPtr.suborder_status = -1
			SubOrderPtr.save()
			buyerPtr = SubOrderPtr.order.buyer
			#buyerAddressPtr = BuyerAddress.objects.filter(buyer_id=int(buyerPtr.id))
			#buyerAddressPtr = buyerAddressPtr[0]
			buyerAddressPtr = SubOrderPtr.order.buyer_address_history
			seller_mail_dict = populateSellerMailDict(SubOrderPtr, buyerPtr, buyerAddressPtr)
			seller_mail_dict["suborder"]["summary_title"] = "Order Cancelled"
			sendSubOrderCancellationMail(SubOrderPtr, seller_mail_dict)
		
	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse("4XX", {"error": "could not update"})
	else:
		closeDBConnection()
		return customResponse("2XX", {"order": "order updated"})