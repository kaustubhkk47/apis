from scripts.utils import *
import json
import logging
log = logging.getLogger("django")
import datetime
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

def get_order_shipment_details(request, orderShipmentParameters):
	try:

		orderShipments = filterOrderShipment(orderShipmentParameters)
		
		statusCode = "2XX"

		paginator = Paginator(orderShipments, orderShipmentParameters["itemsPerPage"])

		try:
			pageItems = paginator.page(orderShipmentParameters["pageNumber"])
		except Exception as e:
			pageItems = []

		body = parseOrderShipments(pageItems,orderShipmentParameters)
		statusCode = "2XX"
		response = {"order_shipments": body,"total_items":paginator.count, "total_pages":paginator.num_pages, "page_number":orderShipmentParameters["pageNumber"], "items_per_page":orderShipmentParameters["itemsPerPage"]}

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

	subOrderPtr = SubOrder.objects.filter(id=int(orderShipment["suborderID"])).select_related('order')

	if len(subOrderPtr) == 0:
		return customResponse("4XX", {"error": "Invalid id for sub order sent"})

	subOrderPtr = subOrderPtr[0]

	sellerAddressPtr = SellerAddress.objects.filter(seller_id=subOrderPtr.seller_id)
	sellerAddressPtr = sellerAddressPtr[0]

	buyerAddressPtr = BuyerAddress.objects.filter(buyer_id=subOrderPtr.order.buyer_id)
	buyerAddressPtr = buyerAddressPtr[0]

	if (int(orderShipment["all_items"]) == 0):
		if not "order_items" in orderShipment or orderShipment["order_items"]==None:
			return customResponse("4XX", {"error": "Order items in order shipment not sent"})

		if not validateOrderShipmentItemsData(orderShipment["order_items"], subOrderPtr.id):
			return customResponse("4XX", {"error": "Inappropriate order items in order shipment sent"})

		sentOrderItems = []
		for orderItem in orderShipment["order_items"]:
			sentOrderItems.append(int(orderItem["orderitemID"]))

		if len(sentOrderItems) == 0:
			return customResponse("4XX", {"error": "No order items in order shipment sent"})

		allOrderItems = OrderItem.objects.filter(id__in=sentOrderItems)

	elif (int(orderShipment["all_items"]) == 1):
		allOrderItems = OrderItem.objects.filter(suborder_id= subOrderPtr.id, current_status__in=[0,1,2,3])
		if len(allOrderItems) == 0:
			return customResponse("4XX", {"error": "No order items left to ship"})
	else:
		return customResponse("4XX", {"error": "Wrong value for all_items sent"})
	try:
		newOrderShipment = OrderShipment(suborder=subOrderPtr, pickup_address=sellerAddressPtr, drop_address=buyerAddressPtr)
		populateOrderShipment(newOrderShipment, orderShipment)
		newOrderShipment.save()

		finalPrice = 0.0
		manifest_dict = {}
		manifest_dict["orderItems"] = []

		for orderItemPtr in allOrderItems:
			orderItemPtr.order_shipment = newOrderShipment
			orderItemPtr.current_status = 8
			finalPrice += float(orderItemPtr.final_price)
			orderItemPtr.save()

			manifestOrderItem = {
				"name":orderItemPtr.product.display_name,
				"pieces":orderItemPtr.pieces
			}

			manifest_dict["orderItems"].append(manifestOrderItem)

		isSubOrderShipped = 1

		if orderShipment["all_items"] == 0:
			OrderItemPtr = OrderItem.objects.filter(suborder_id= subOrderPtr.id)

			for orderItem in OrderItemPtr:
				if orderItem.current_status in [0,1,2]:
					isSubOrderShipped = 0
					break

		isOrderShipped = 1

		OrderItemPtr = OrderItem.objects.filter(suborder__order_id= subOrderPtr.order_id)

		for orderItem in OrderItemPtr:
			if orderItem.current_status in [0,1,2]:
				isOrderShipped = 0
				break

		if isSubOrderShipped == 1:
			subOrderPtr.suborder_status = 4
		else:
			subOrderPtr.suborder_status = 3

		subOrderPtr.cod_charge += newOrderShipment.cod_charge
		subOrderPtr.shipping_charge += newOrderShipment.shipping_charge
		subOrderPtr.final_price += (newOrderShipment.cod_charge + newOrderShipment.shipping_charge)
		
		subOrderPtr.save()

		if isOrderShipped == 1:
			subOrderPtr.order.order_status = 3
		else:
			subOrderPtr.order.order_status = 2

		subOrderPtr.order.cod_charge += newOrderShipment.cod_charge
		subOrderPtr.order.shipping_charge += newOrderShipment.shipping_charge
		subOrderPtr.order.final_price += (newOrderShipment.cod_charge + newOrderShipment.shipping_charge)
		
		subOrderPtr.order.save()

		buyerPtr = subOrderPtr.order.buyer
		sellerPtr = subOrderPtr.seller

		outputLink = "media/generateddocs/shipmentmanifest/" + str(sellerPtr.id) +"/" + str(subOrderPtr.display_number) + "/"
		outputDirectory = settings.STATIC_ROOT + outputLink
		outputFileName = "WholdusManifest-" + str(newOrderShipment.id) + "-" + str(subOrderPtr.display_number) + ".pdf"

		newOrderShipment.final_price = finalPrice
		newOrderShipment.manifest_link = outputLink + outputFileName
		newOrderShipment.save()

		manifest_dict["order"] = {
			"display_number": subOrderPtr.display_number
		}

		manifest_dict["buyer"] = {
			"name": buyerPtr.name
		}

		manifest_dict["buyer_address"] = serialize_buyer_address(buyerAddressPtr)

		manifest_dict["seller"] = {
			"name": sellerPtr.name,
			"company_name": sellerPtr.company_name,
			"vat_tin": sellerPtr.sellerdetails.vat_tin
		}

		manifest_dict["seller_address"] = serialize_seller_address(sellerAddressPtr)

		manifest_dict["shipment"] = {
			"waybill_number": newOrderShipment.waybill_number,
			"shipping_amount": '{0:.0f}'.format(newOrderShipment.cod_charge + newOrderShipment.shipping_charge),
			"logistics_partner": newOrderShipment.logistics_partner_name,
			"invoice_number": newOrderShipment.invoice_number,
			"final_price": '{0:.0f}'.format(newOrderShipment.final_price),
			"amount_to_collect":'{0:.0f}'.format(float(newOrderShipment.cod_charge) + float(newOrderShipment.shipping_charge) + float(newOrderShipment.final_price)),
			"packaged_length": '{0:.0f}'.format(newOrderShipment.packaged_length),
			"packaged_breadth": '{0:.0f}'.format(newOrderShipment.packaged_breadth),
			"packaged_height": '{0:.0f}'.format(newOrderShipment.packaged_height),
			"packaged_weight": '{0:.2f}'.format(newOrderShipment.packaged_weight)
		}

		
		template_file = "manifest/shipment_manifest.html"

		generate_pdf(template_file, manifest_dict, outputDirectory, outputFileName)

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
			orderShipmentPtr.tpl_in_transit_time = datetime.datetime.now()
			update_order_item_status(orderShipmentPtr.id, 9)
		elif status == 5:
			orderShipmentPtr.tpl_stuck_in_transit_time = datetime.datetime.now()
			update_order_item_status(orderShipmentPtr.id, 10)
		elif status == 6:
			orderShipmentPtr.delivered_time = datetime.datetime.now()
			update_order_item_status(orderShipmentPtr.id, 11)
			update_order_completion_status(orderShipmentPtr.suborder.order)
			update_suborder_completion_status(orderShipmentPtr.suborder)
		elif status == 7:
			orderShipmentPtr.rto_in_transit_time = datetime.datetime.now()
			if "rto_remarks" in orderShipment and not orderShipment["rto_remarks"]==None:
				orderShipmentPtr.rto_remarks = orderShipment["rto_remarks"]
			update_order_item_status(orderShipmentPtr.id, 12)
		elif status == 8:
			orderShipmentPtr.rto_delivered_time = datetime.datetime.now()
			update_order_item_status(orderShipmentPtr.id, 13)
			update_order_completion_status(orderShipmentPtr.suborder.order)
			update_suborder_completion_status(orderShipmentPtr.suborder)
		elif status == 9:
			orderShipmentPtr.lost_time = datetime.datetime.now()
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