from scripts.utils import *
import json
import logging
log = logging.getLogger("django")

from ..models.subOrder import SubOrder, filterSubOrder, validateSubOrderStatus, populateSellerMailDict, sendSubOrderCancellationMail
from ..models.orderItem import OrderItem
from ..serializers.subOrder import parseSubOrders
from users.serializers.buyer import BuyerAddress
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone

def get_suborder_details(request,subOrderParameters):
	try:
		
		subOrders = filterSubOrder(subOrderParameters)

		paginator = Paginator(subOrders, subOrderParameters["itemsPerPage"])

		try:
			pageItems = paginator.page(subOrderParameters["pageNumber"])
		except Exception as e:
			pageItems = []

		body = parseSubOrders(pageItems,subOrderParameters)
		statusCode = "2XX"
		response = {"sub_orders": body,"total_items":paginator.count, "total_pages":paginator.num_pages, "page_number":subOrderParameters["pageNumber"], "items_per_page":subOrderParameters["itemsPerPage"]}


	except Exception as e:
		log.critical(e)
		statusCode = "4XX"
		response = {"error": "Invalid request"}

	closeDBConnection()
	return customResponse(statusCode, response)

def update_suborder(request):
	try:
		requestbody = request.body.decode("utf-8")
		subOrder = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse("4XX", {"error": "Invalid data sent in request"})

	if not len(subOrder) or not "suborderID" in subOrder or not validate_integer(subOrder["suborderID"]):
		return customResponse("4XX", {"error": "Id for suborder not sent"})

	if not "status" in subOrder or not validate_integer(subOrder["status"]):
		return customResponse("4XX", {"error": "Current status not sent"})

	status = int(subOrder["status"])

	subOrderPtr = SubOrder.objects.filter(id=int(subOrder["suborderID"]))

	if len(subOrderPtr) == 0:
		return customResponse("4XX", {"error": "Invalid id for sub order sent"})

	subOrderPtr = subOrderPtr[0]

	if not validateSubOrderStatus(status,subOrderPtr.suborder_status):
		return customResponse("4XX", {"error": "Improper status sent"})

	try:

		if status == 2:
			subOrderPtr.merchant_notified_time = timezone.now()

			orderItemQuerySet = OrderItem.objects.filter(suborder_id = subOrderPtr.id)
			for orderItem in orderItemQuerySet:
				if 	orderItem.current_status in [0,1]:
					orderItem.current_status = 2
					orderItem.save()
		
		subOrderPtr.suborder_status = status
		subOrderPtr.save()
	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse("4XX", {"error": "could not update"})
	else:
		closeDBConnection()
		return customResponse("2XX", {"order": "order updated"})

def cancel_suborder(request):
	try:
		requestbody = request.body.decode("utf-8")
		subOrder = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse("4XX", {"error": "Invalid data sent in request"})

	if not len(subOrder) or not "suborderID" in subOrder or not validate_integer(subOrder["suborderID"]):
		return customResponse("4XX", {"error": "Id for suborder not sent"})

	subOrderPtr = SubOrder.objects.filter(id=int(subOrder["suborderID"])).select_related('order')

	if len(subOrderPtr) == 0:
		return customResponse("4XX", {"error": "Invalid id for suborder sent"})

	subOrderPtr = subOrderPtr[0]

	if not "cancellation_remarks" in subOrder or subOrder["cancellation_remarks"]==None:
		subOrder["cancellation_remarks"] = ""

	if subOrderPtr.suborder_status == -1:
		return customResponse("4XX", {"error": "Already cancelled"})

	try:
		nowDateTime = timezone.now()
		subOrderPtr.suborder_status = -1
		subOrderPtr.cancellation_remarks = subOrder["cancellation_remarks"]
		subOrderPtr.cancellation_time = nowDateTime
		subOrderPtr.save()

		OrderItem.objects.filter(suborder_id = subOrderPtr.id).update(current_status=4, cancellation_time=nowDateTime)

		isOrderCancelled = 1

		allSubOrders = SubOrder.objects.filter(order_id=subOrderPtr.order_id)

		for subOrderItr in allSubOrders:
			if subOrderItr.suborder_status != -1:
				isOrderCancelled = 0
				break

		if isOrderCancelled == 1:
			subOrderPtr.order.order_status = -1
			subOrderPtr.order.save()

		buyerPtr = subOrderPtr.order.buyer
		buyerAddressPtr = BuyerAddress.objects.filter(buyer_id=int(buyerPtr.id))
		buyerAddressPtr = buyerAddressPtr[0]
		seller_mail_dict = populateSellerMailDict(subOrderPtr, buyerPtr, buyerAddressPtr)
		seller_mail_dict["suborder"]["summary_title"] = "Order Cancelled"
		sendSubOrderCancellationMail(subOrderPtr, seller_mail_dict)

	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse("4XX", {"error": "could not update"})
	else:
		closeDBConnection()
		return customResponse("2XX", {"order": "order updated"})