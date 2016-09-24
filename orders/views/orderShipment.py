from scripts.utils import *
import json
import logging
log = logging.getLogger("django")
from django.utils import timezone
from ..models.order import update_order_completion_status
from ..models.orderShipment import OrderShipment, filterOrderShipment, validateOrderShipmentData, populateOrderShipment, validateOrderShipmentItemsData, validateOrderShipmentStatus
from ..models.subOrder import SubOrder, update_suborder_completion_status
from ..models.orderItem import OrderItem, update_order_item_status
from ..serializers.orderShipment import parseOrderShipments, serializeOrderShipment
from users.models.buyer import BuyerAddress
from users.models.seller import SellerAddress
from users.serializers.seller import serialize_seller_address
from users.serializers.buyer import serialize_buyer_address
import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Sum
from decimal import Decimal

def get_order_shipment_details(request, parameters):
	try:

		orderShipments = filterOrderShipment(parameters)
		
		statusCode = "2XX"

		paginator = Paginator(orderShipments, parameters["itemsPerPage"])

		try:
			pageItems = paginator.page(parameters["pageNumber"])
		except Exception as e:
			pageItems = []

		body = parseOrderShipments(pageItems,parameters)
		statusCode = "2XX"
		response = {"order_shipments": body}

		responsePaginationParameters(response,paginator, parameters)

	except Exception as e:
		log.critical(e)
		statusCode = "4XX"
		response = {"error": "Invalid request"}
	closeDBConnection()
	return customResponse(statusCode, response)

def post_new_order_shipment(request):
	try:
		requestbody = request.body.decode("utf-8")
		orderShipment = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse("4XX", {"error": "Invalid data sent in request"})

	if not len(orderShipment) or not validateOrderShipmentData(orderShipment):
		return customResponse("4XX", {"error": "Invalid data for order shipment sent"})

	if not "suborderID" in orderShipment or not validate_integer(orderShipment["suborderID"]):
		return customResponse("4XX", {"error": "Id for sub order not sent"})

	subOrderPtr = SubOrder.objects.filter(id=int(orderShipment["suborderID"]), suborder_status__gt=0).select_related('order')

	if len(subOrderPtr) == 0:
		return customResponse("4XX", {"error": "Invalid id for sub order sent"})

	subOrderPtr = subOrderPtr[0]

	sellerAddressPtr = subOrderPtr.seller_address_history

	buyerAddressPtr = subOrderPtr.order.buyer_address_history

	if (int(orderShipment["all_items"]) == 0):
		if not "order_items" in orderShipment or orderShipment["order_items"]==None:
			return customResponse("4XX", {"error": "Order items in order shipment not sent"})

		sentOrderItems = []

		if len(orderShipment["order_items"]) == 0:
			return customResponse("4XX", {"error": "No order items in order shipment sent"})

		if not validateOrderShipmentItemsData(orderShipment["order_items"], sentOrderItems):
			return customResponse("4XX", {"error": "Inappropriate order items in order shipment sent"})

		allOrderItems = OrderItem.objects.filter(id__in=sentOrderItems, current_status__in=[0,1,2], suborder_id=subOrderID)

		if not len(allOrderItems) == len(orderItems):
			return customResponse("4XX", {"error": "Inappropriate order items in order shipment sent"})

	elif (int(orderShipment["all_items"]) == 1):
		allOrderItems = OrderItem.objects.filter(suborder_id= subOrderPtr.id, current_status__in=[0,1,2])
		if len(allOrderItems) == 0:
			return customResponse("4XX", {"error": "No order items left to ship"})
	else:
		return customResponse("4XX", {"error": "Wrong value for all_items sent"})
	try:
		newOrderShipment = OrderShipment(suborder=subOrderPtr, pickup_address=sellerAddressPtr, drop_address=buyerAddressPtr)
		populateOrderShipment(newOrderShipment, orderShipment)
		finalPrice = allOrderItems.aggregate(Sum('final_price'))["final_price__sum"]
		newOrderShipment.final_price = finalPrice
		newOrderShipment.save()

		allOrderItems.update(current_status=8, order_shipment_id=newOrderShipment.id)

		OrderItemPtr = OrderItem.objects.filter(suborder_id= subOrderPtr.id, current_status__in=[0,1,2])

		if OrderItemPtr.exists():
			subOrderPtr.suborder_status = 3
		else:
			subOrderPtr.suborder_status = 4

		OrderItemPtr = OrderItem.objects.filter(suborder__order_id= subOrderPtr.order_id, current_status__in=[0,1,2])

		if OrderItemPtr.exists():
			subOrderPtr.order.order_status = 2
		else:
			subOrderPtr.order.order_status = 3

		if subOrderPtr.order.placed_by == 0:
			subOrderPtr.cod_charge += newOrderShipment.cod_charge
			subOrderPtr.shipping_charge += newOrderShipment.shipping_charge
			subOrderPtr.final_price += (newOrderShipment.cod_charge + newOrderShipment.shipping_charge)
			subOrderPtr.save()

			subOrderPtr.order.cod_charge += newOrderShipment.cod_charge
			subOrderPtr.order.shipping_charge += newOrderShipment.shipping_charge
			subOrderPtr.order.final_price += (newOrderShipment.cod_charge + newOrderShipment.shipping_charge)
		else:
			if subOrderPtr.suborder_status == 4:
				oldOrderShipments = OrderShipment.objects.filter(suborder_id= subOrderPtr.id).exclude(id=newOrderShipment.id)
				oldOrderShipmentValues = oldOrderShipments.aggregate(Sum('cod_charge'),Sum('shipping_charge'))
				oldShippingCharge = oldOrderShipmentValues["shipping_charge__sum"]
				oldCODCharge = oldOrderShipmentValues["cod_charge__sum"]
				newOrderShipment.cod_charge = subOrderPtr.cod_charge - oldShippingCharge
				newOrderShipment.shipping_charge  = subOrderPtr.shipping_charge - oldShippingCharge
			else:
				currentOrderItems = OrderItem.objects.filter(order_shipment_id=newOrderShipment.id)
				oldOrderItems = OrderItem.objects.filter(suborder_id= subOrderPtr.id)

				oldOrderItemPrices = oldOrderItems.aggregate(Sum('final_price'))["final_price__sum"]
				currentOrderItemPrices = currentOrderItems.aggregate(Sum('final_price'))["final_price__sum"]

				ratio = currentOrderItemPrices/oldOrderItemPrices

				newOrderShipment.cod_charge = subOrderPtr.cod_charge*ratio
				newOrderShipment.shipping_charge  = subOrderPtr.shipping_charge*ratio

			newOrderShipment.save()
		
		subOrderPtr.save()
		subOrderPtr.order.save()
		
		newOrderShipment.create_manifest()

	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse("4XX", {"error": "unable to create entry in db"})
	else:
		closeDBConnection()
		return customResponse("2XX", {"order_shipment": serializeOrderShipment(newOrderShipment)})

def update_order_shipment(request):
	try:
		requestbody = request.body.decode("utf-8")
		orderShipment = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse("4XX", {"error": "Invalid data sent in request"})

	if not len(orderShipment) or not "ordershipmentID" in orderShipment or not validate_integer(orderShipment["ordershipmentID"]):
		return customResponse("4XX", {"error": "Id for order shipment not sent"})

	if not "status" in orderShipment or not validate_integer(orderShipment["status"]):
		return customResponse("4XX", {"error": "Current status not sent"})

	status = int(orderShipment["status"])

	orderShipmentPtr = OrderShipment.objects.filter(id=int(orderShipment["ordershipmentID"]))

	if len(orderShipmentPtr) == 0:
		return customResponse("4XX", {"error": "Invalid id for order shipment sent"})

	orderShipmentPtr = orderShipmentPtr[0]

	if not validateOrderShipmentStatus(status,orderShipmentPtr.current_status):
		return customResponse("4XX", {"error": "Improper status sent"})

	try:
		if status == 4:
			orderShipmentPtr.tpl_in_transit_time = timezone.now()
			update_order_item_status(orderShipmentPtr.id, 9)
		elif status == 5:
			orderShipmentPtr.tpl_stuck_in_transit_time = timezone.now()
			update_order_item_status(orderShipmentPtr.id, 10)
		elif status == 6:
			orderShipmentPtr.delivered_time = timezone.now()
			update_order_item_status(orderShipmentPtr.id, 11)
			update_order_completion_status(orderShipmentPtr.suborder.order)
			update_suborder_completion_status(orderShipmentPtr.suborder)
		elif status == 7:
			orderShipmentPtr.rto_in_transit_time = timezone.now()
			if "rto_remarks" in orderShipment and not orderShipment["rto_remarks"]==None:
				orderShipmentPtr.rto_remarks = orderShipment["rto_remarks"]
			update_order_item_status(orderShipmentPtr.id, 12)
		elif status == 8:
			orderShipmentPtr.rto_delivered_time = timezone.now()
			update_order_item_status(orderShipmentPtr.id, 13)
			update_order_completion_status(orderShipmentPtr.suborder.order)
			update_suborder_completion_status(orderShipmentPtr.suborder)
		elif status == 9:
			orderShipmentPtr.lost_time = timezone.now()
			update_order_item_status(orderShipmentPtr.id, 14)
			update_order_completion_status(orderShipmentPtr.suborder.order)
			update_suborder_completion_status(orderShipmentPtr.suborder)
		
		orderShipmentPtr.current_status = status
		orderShipmentPtr.save()
	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse("4XX", {"error": "could not update"})
	else:
		closeDBConnection()
		return customResponse("2XX", {"order": "order updated"})