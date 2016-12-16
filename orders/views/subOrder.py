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

def get_suborder_details(request,parameters):
	try:
		
		subOrders = filterSubOrder(parameters)

		paginator = Paginator(subOrders, parameters["itemsPerPage"])

		try:
			pageItems = paginator.page(parameters["pageNumber"])
		except Exception as e:
			pageItems = []

		body = parseSubOrders(pageItems,parameters)
		statusCode = 200
		response = {"sub_orders": body}
		responsePaginationParameters(response,paginator, parameters)

	except Exception as e:
		log.critical(e)
		statusCode = 500
		response = {}

	closeDBConnection()
	return customResponse(statusCode, response, error_code=0)

def update_suborder(request):
	try:
		requestbody = request.body.decode("utf-8")
		subOrder = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse(400, error_code=4)

	if not len(subOrder) or not "suborderID" in subOrder or not validate_integer(subOrder["suborderID"]):
		return customResponse(400, error_code=5,  error_details= "Id for suborder not sent")

	if not "status" in subOrder or not validate_integer(subOrder["status"]):
		return customResponse(400, error_code=5,  error_details= "Current status not sent")

	status = int(subOrder["status"])

	subOrderPtr = SubOrder.objects.filter(id=int(subOrder["suborderID"]))

	if len(subOrderPtr) == 0:
		return customResponse(400, error_code=6,  error_details="Invalid id for sub order sent")

	subOrderPtr = subOrderPtr[0]

	if not validateSubOrderStatus(status,subOrderPtr.suborder_status):
		return customResponse(400, error_code=6,  error_details="Improper status sent")

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
		return customResponse(500, error_code = 3)
	else:
		closeDBConnection()
		return customResponse(200, {"order": "order updated"})

def cancel_suborder(request):
	try:
		requestbody = request.body.decode("utf-8")
		subOrder = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse(400, error_code=4)

	if not len(subOrder) or not "suborderID" in subOrder or not validate_integer(subOrder["suborderID"]):
		return customResponse(400, error_code=5,  error_details="Id for suborder not sent")

	subOrderPtr = SubOrder.objects.filter(id=int(subOrder["suborderID"])).select_related('order')

	if len(subOrderPtr) == 0:
		return customResponse(400, error_code=6,  error_details="Invalid id for suborder sent")

	subOrderPtr = subOrderPtr[0]

	if not "cancellation_remarks" in subOrder or subOrder["cancellation_remarks"]==None:
		subOrder["cancellation_remarks"] = ""

	if subOrderPtr.suborder_status == -1:
		return customResponse(400, error_code=6,  error_details="Already cancelled")

	try:
		nowDateTime = timezone.now()
		subOrderPtr.suborder_status = -1
		subOrderPtr.cancellation_remarks = subOrder["cancellation_remarks"]
		subOrderPtr.cancellation_time = nowDateTime
		subOrderPtr.save()

		OrderItem.objects.filter(suborder_id = subOrderPtr.id).update(current_status=4, cancellation_time=nowDateTime, updated_at = timezone.now())

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
		#buyerAddressPtr = BuyerAddress.objects.filter(buyer_id=int(buyerPtr.id))
		#buyerAddressPtr = buyerAddressPtr[0]
		buyerAddressPtr = subOrderPtr.order.buyer_address_history
		seller_mail_dict = populateSellerMailDict(subOrderPtr, buyerPtr, buyerAddressPtr)
		seller_mail_dict["suborder"]["summary_title"] = "Order Cancelled"
		sendSubOrderCancellationMail(subOrderPtr, seller_mail_dict)

	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse(500, error_code = 3)
	else:
		closeDBConnection()
		return customResponse(200, {"order": "order updated"})