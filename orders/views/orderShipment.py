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
		
		paginator = Paginator(orderShipments, parameters["itemsPerPage"])

		try:
			pageItems = paginator.page(parameters["pageNumber"])
		except Exception as e:
			pageItems = []

		body = parseOrderShipments(pageItems,parameters)
		statusCode = 200
		response = {"order_shipments": body}

		responsePaginationParameters(response,paginator, parameters)

	except Exception as e:
		log.critical(e)
		statusCode = 500
		response = {"error": "Invalid request"}
	closeDBConnection()
	return customResponse(statusCode, response, error_code=0)

def post_new_order_shipment(request):
	try:
		requestbody = request.body.decode("utf-8")
		orderShipment = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse(400, error_code=4)

	if not len(orderShipment) or not validateOrderShipmentData(orderShipment):
		return customResponse(400, error_code=5, error_details= "Invalid data for order shipment sent")

	if not "suborderID" in orderShipment or not validate_integer(orderShipment["suborderID"]):
		return customResponse(400, error_code=5, error_details=  "Id for sub order not sent")

	subOrderPtr = SubOrder.objects.filter(id=int(orderShipment["suborderID"]), suborder_status__gt=0).select_related('order')

	if len(subOrderPtr) == 0:
		return customResponse(400, error_code=6, error_details = "Invalid id for sub order sent")

	subOrderPtr = subOrderPtr[0]

	sellerAddressPtr = subOrderPtr.seller_address_history

	buyerAddressPtr = subOrderPtr.order.buyer_address_history

	if (int(orderShipment["all_items"]) == 0):
		if not "order_items" in orderShipment or orderShipment["order_items"]==None:
			return customResponse(400, error_code=5, error_details= "Order items in order shipment not sent")

		sentOrderItems = []

		if len(orderShipment["order_items"]) == 0:
			return customResponse(400, error_code=5, error_details= "No order items in order shipment sent")

		if not validateOrderShipmentItemsData(orderShipment["order_items"], sentOrderItems):
			return customResponse(400, error_code=6, error_details = "Inappropriate order items in order shipment sent")

		allOrderItems = OrderItem.objects.filter(id__in=sentOrderItems, current_status__in=[0,1,2], suborder_id=subOrderPtr.id)

		if not len(allOrderItems) == len(orderItems):
			return customResponse(400, error_code=6, error_details ="Inappropriate order items in order shipment sent")

	elif (int(orderShipment["all_items"]) == 1):
		allOrderItems = OrderItem.objects.filter(suborder_id= subOrderPtr.id, current_status__in=[0,1,2])
		if len(allOrderItems) == 0:
			return customResponse(400, error_code=6, error_details = "No order items left to ship")
	else:
		return customResponse(400, error_code=6, error_details ="Wrong value for all_items sent")
	try:
		newOrderShipment = OrderShipment(suborder=subOrderPtr, pickup_address=sellerAddressPtr, drop_address=buyerAddressPtr)
		populateOrderShipment(newOrderShipment, orderShipment)
		allOrderItemsValues = allOrderItems.aggregate(Sum('final_price'), Sum('pieces'))
		newOrderShipment.pieces = allOrderItemsValues["pieces__sum"]
		newOrderShipment.final_price = allOrderItemsValues["final_price__sum"]
		newOrderShipment.product_count = len(allOrderItems)
		newOrderShipment.save()

		allOrderItems.update(current_status=8, order_shipment_id=newOrderShipment.id, updated_at =timezone.now())

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

		if subOrderPtr.order.placed_by != "buyer":
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
				oldShippingCharge = oldOrderShipmentValues["shipping_charge__sum"] if oldOrderShipmentValues["shipping_charge__sum"] != None else 0
				oldCODCharge = oldOrderShipmentValues["cod_charge__sum"] if oldOrderShipmentValues["cod_charge__sum"] != None else 0
				newOrderShipment.cod_charge = subOrderPtr.cod_charge - oldCODCharge
				newOrderShipment.shipping_charge = subOrderPtr.shipping_charge - oldShippingCharge
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
		newOrderShipment.create_label()
		newOrderShipment.create_csv()

	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse(500, error_code = 1)
	else:
		closeDBConnection()
		return customResponse(200, {"order_shipment": serializeOrderShipment(newOrderShipment)})

def update_order_shipment(request):
	try:
		requestbody = request.body.decode("utf-8")
		orderShipment = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse(400, error_code=4)

	if not len(orderShipment) or not "ordershipmentID" in orderShipment or not validate_integer(orderShipment["ordershipmentID"]):
		return customResponse(400, error_code=5,  error_details=  "Id for order shipment not sent")

	if not "status" in orderShipment or not validate_integer(orderShipment["status"]):
		return customResponse(400, error_code=5,  error_details= "Current status not sent")

	status = int(orderShipment["status"])

	orderShipmentPtr = OrderShipment.objects.filter(id=int(orderShipment["ordershipmentID"]))

	if len(orderShipmentPtr) == 0:
		return customResponse(400, error_code=6, error_details =  "Invalid id for order shipment sent")

	orderShipmentPtr = orderShipmentPtr[0]

	if not validateOrderShipmentStatus(status,orderShipmentPtr.current_status):
		return customResponse(400, error_code=6, error_details =  "Improper status sent")

	try:
		if status == 4:
			orderShipmentPtr.tpl_in_transit_time = timezone.now()
			update_order_item_status(orderShipmentPtr.id, 9)
			orderPtr = orderShipmentPtr.suborder.order
			orderPtr.sendOrderNotification("Order No {} Shipped".format(orderPtr.display_number), "Track it from my orders tab")
			orderPtr.sendOrderSMS("has been dispated. Track the order from the My Orders tab in your Wholdus app")
		elif status == 5:
			orderShipmentPtr.tpl_stuck_in_transit_time = timezone.now()
			update_order_item_status(orderShipmentPtr.id, 10)
		elif status == 6:
			orderShipmentPtr.delivered_time = timezone.now()
			update_order_item_status(orderShipmentPtr.id, 11)
			update_order_completion_status(orderShipmentPtr.suborder.order)
			update_suborder_completion_status(orderShipmentPtr.suborder)
			orderPtr = orderShipmentPtr.suborder.order
			orderPtr.sendOrderNotification("Order No {} Delivered".format(orderPtr.display_number), "We were happy to serve you :)")
			orderPtr.sendOrderSMS("has been successfully delivered. We were happy to serve you :)")
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
		return customResponse(500, error_code = 3)
	else:
		closeDBConnection()
		return customResponse(200, {"order": "order updated"})