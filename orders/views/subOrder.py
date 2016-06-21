from scripts.utils import *
import json
import logging
log = logging.getLogger("django")

from ..models.subOrder import SubOrder, filterSubOrder, validateSubOrderStatus
from ..models.orderItem import OrderItem
from ..serializers.subOrder import parseSubOrders

def get_suborder_details(request,subOrderParameters):
	try:
		
		subOrders = filterSubOrder(subOrderParameters)

		body = parseSubOrders(subOrders,subOrderParameters)
		statusCode = "2XX"
		response = {"sub_orders": body}

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

	if not len(subOrder) or not "suborderID" in subOrder or subOrder["suborderID"]==None or not validate_integer(subOrder["suborderID"]):
		return customResponse("4XX", {"error": "Id for suborder not sent"})

	if not "status" in subOrder or subOrder["status"]==None or not validate_integer(subOrder["status"]):
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
			subOrderPtr.merchant_notified_time = datetime.datetime.now()

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