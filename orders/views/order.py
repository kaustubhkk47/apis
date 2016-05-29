from scripts.utils import customResponse, closeDBConnection, convert_keys_to_string
import json
from ..models.order import *
from ..models.orderItem import *
from ..models.orderShipment import *
from ..models.subOrder import *
from ..serializers.order import *
from ..models.payments import *
from users.models.buyer import *
from users.models.seller import *
from decimal import Decimal
import datetime


def get_order_shipment_details(request, statusArr=[], sellersArr=[], isSeller=0,internalusersArr=[],isInternalUser=0):
	try:
		if len(statusArr) == 0 and len(sellersArr) == 0:
			orderShipments = OrderShipment.objects.all()
		elif len(sellersArr) == 0 and len(statusArr) == 1:
			orderShipments = OrderShipment.objects.filter(current_status__in=statusArr)
		elif len(sellersArr) == 1 and len(statusArr) == 0:
			orderShipments = OrderItem.objects.filter(suborder__seller_id__in=sellersArr)
		else:
			orderShipments = OrderItem.objects.filter(current_status__in=statusArr,suborder__seller_id__in=sellersArr)
		closeDBConnection()
		body = parseOrderShipments(orderShipments)
		statusCode = "2XX"
		response = {"order_shipments": body}

	except Exception as e:
		statusCode = "4XX"
		response = {"error": "Invalid request"}

	return customResponse(statusCode, response)

def get_order_item_details(request, statusArr=[], sellersArr=[], isSeller=0,internalusersArr=[],isInternalUser=0):
	try:
		if len(statusArr) == 0 and len(sellersArr) == 0:
			orderItems = OrderItem.objects.all().select_related('product')
		elif len(sellersArr) == 0 and len(statusArr) == 1:
			orderItems = OrderItem.objects.filter(current_status__in=statusArr).select_related('product')
		elif len(sellersArr) == 1 and len(statusArr) == 0:
			orderItems = OrderItem.objects.filter(suborder__seller_id__in=sellersArr).select_related('product')
		else:
			orderItems = OrderItem.objects.filter(current_status__in=statusArr,suborder__seller_id__in=sellersArr).select_related('product')
		closeDBConnection()
		body = parseOrderItem(orderItems)
		statusCode = "2XX"
		response = {"order_items": body}

	except Exception as e:
		statusCode = "4XX"
		response = {"error": "Invalid request"}

	return customResponse(statusCode, response)

def get_suborder_details(request, statusArr=[], sellersArr=[], isSeller=0,internalusersArr=[],isInternalUser=0):
	try:
		if len(statusArr) == 0 and len(sellersArr) == 0:
			subOrders = SubOrder.objects.all().select_related('seller')
		elif len(sellersArr) == 0 and len(statusArr) == 1:
			subOrders = SubOrder.objects.filter(suborder_status__in=statusArr).select_related('seller')
		elif len(sellersArr) == 1 and len(statusArr) == 0:
			subOrders = SubOrder.objects.filter(seller_id__in=sellersArr).select_related('seller')
		else:
			subOrders = SubOrder.objects.filter(suborder_status__in=statusArr,	seller_id__in=sellersArr).select_related('seller')
		closeDBConnection()
		body = parseSubOrders(subOrders)
		statusCode = "2XX"
		response = {"sub_orders": body}

	except Exception as e:
		statusCode = "4XX"
		response = {"error": "Invalid request"}

	return customResponse(statusCode, response)

def get_order_details(request, statusArr=[], buyersArr=[], isBuyer=0,internalusersArr=[],isInternalUser=0):
	try:
		if len(statusArr) == 0 and len(buyersArr) == 0:
			Orders = Order.objects.all().select_related('buyer')
		elif len(buyersArr) == 0 and len(statusArr) == 1:
			Orders = Order.objects.filter(order_status__in=statusArr).select_related('buyer')
		elif len(buyersArr) == 1 and len(statusArr) == 0:
			Orders = Order.objects.filter(buyer_id__in=buyersArr).select_related('buyer')
		else:
			Orders = Order.objects.filter(order_status__in=statusArr,buyer_id__in=buyersArr).select_related('buyer')
		closeDBConnection()
		body = parseOrders(Orders)
		statusCode = "2XX"
		response = {"orders": body}

	except Exception as e:
		statusCode = "4XX"
		response = {"error": "Invalid request"}

	return customResponse(statusCode, response)

def post_new_order_shipment(request):
	try:
		requestbody = request.body.decode("utf-8")
		orderShipment = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse("4XX", {"error": "Invalid data sent in request"})

	if not len(orderShipment) or not validateOrderShipmentData(orderShipment):
		return customResponse("4XX", {"error": "Invalid data for order shipment sent"})

	if not "suborderID" in orderShipment or orderShipment["suborderID"]==None:
		return customResponse("4XX", {"error": "Id for sub order not sent"})

	subOrderPtr = SubOrder.objects.filter(id=int(orderShipment["suborderID"])).select_related('order')

	if len(subOrderPtr) == 0:
		return customResponse("4XX", {"error": "Invalid id for sub order sent"})

	subOrderPtr = subOrderPtr[0]

	sellerAddressPtr = SellerAddress.objects.filter(seller_id=subOrderPtr.seller_id)
	sellerAddressPtr = sellerAddressPtr[0]

	buyerAddressPtr = BuyerAddress.objects.filter(buyer_id=subOrderPtr.order.buyer_id)
	buyerAddressPtr = buyerAddressPtr[0]

	if not "order_items" in orderShipment or orderShipment["order_items"]==None:
		return customResponse("4XX", {"error": "Order items in order shipment not sent"})

	if not validateOrderShipmentItemsData(orderShipment["order_items"]):
		return customResponse("4XX", {"error": "Order items in order shipment not sent properly sent"})

	try:
		newOrderShipment = OrderShipment(suborder=subOrderPtr, pickup_address=sellerAddressPtr, drop_address=buyerAddressPtr)
		populateOrderShipment(newOrderShipment, orderShipment)
		newOrderShipment.save()

		subOrderPtr.cod_charge += newOrderShipment.cod_charge
		subOrderPtr.shipping_charge += newOrderShipment.shipping_charge
		subOrderPtr.final_price += (newOrderShipment.cod_charge + newOrderShipment.shipping_charge)
		subOrderPtr.save()

		subOrderPtr.order.cod_charge += newOrderShipment.cod_charge
		subOrderPtr.order.shipping_charge += newOrderShipment.shipping_charge
		subOrderPtr.order.final_price += (newOrderShipment.cod_charge + newOrderShipment.shipping_charge)
		subOrderPtr.order.save()

		for orderItem in orderShipment["order_items"]:
			orderItemPtr = OrderItem.objects.filter(id=int(orderItem["orderitemID"]))
			orderItemPtr = orderItemPtr[0]
			orderItemPtr.order_shipment = newOrderShipment
			orderItemPtr.save()	

	except Exception as e:
		closeDBConnection()
		return customResponse("4XX", {"error": "unable to create entry in db"})
	else:
		closeDBConnection()
		return customResponse("2XX", {"order_shipment": serializeOrderShipment(newOrderShipment)})


def post_new_order(request):
	try:
		requestbody = request.body.decode("utf-8")
		order = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse("4XX", {"error": "Invalid data sent in request"})

	if not len(order):
		return customResponse("4XX", {"error": "Invalid data for order sent"})

	if not "buyerID" in order or order["buyerID"]==None:
		return customResponse("4XX", {"error": "Id for buyer not sent"})

	buyerPtr = Buyer.objects.filter(id=int(order["buyerID"]))

	if len(buyerPtr) == 0:
		return customResponse("4XX", {"error": "Invalid id for buyer sent"})

	buyerPtr = buyerPtr[0]

	if not "products" in order or order["products"]==None:
		return customResponse("4XX", {"error": "Products in order not sent"})
	if not validateOrderProductsData(order["products"]):
		return customResponse("4XX", {"error": "Products in order not sent properly sent"})

	orderProducts = order["products"]

	sellersHash = {}

	if not "remarks" in order or order["remarks"]==None:
		order["remarks"] = ""
	orderRemarks = order["remarks"]

	subOrders = []

	orderProductCount = 0
	orderRetailPrice = Decimal(0.0)
	orderCalculatedPrice = Decimal(0.0)
	orderEditedPrice = Decimal(0.0)

	for orderProduct in orderProducts:
		
		productPtr = Product.objects.filter(id=orderProduct["productID"]).select_related('seller')
		productPtr = productPtr[0]

		seller = productPtr.seller
		sellerID = seller.id

		orderProductCount += 1
		orderRetailPrice += Decimal(orderProduct["pieces"])*Decimal(orderProduct["retail_price_per_piece"])
		orderCalculatedPrice += Decimal(orderProduct["pieces"])*Decimal(orderProduct["calculated_price_per_piece"])
		orderEditedPrice += Decimal(orderProduct["pieces"])*Decimal(orderProduct["edited_price_per_piece"])

		if sellerID in sellersHash:
			subOrders[sellersHash[sellerID]]["order_products"].append(orderProduct)
			subOrders[sellersHash[sellerID]]["product_count"] += 1
			subOrders[sellersHash[sellerID]]["retail_price"] += Decimal(orderProduct["pieces"])*Decimal(orderProduct["retail_price_per_piece"])
			subOrders[sellersHash[sellerID]]["calculated_price"] += Decimal(orderProduct["pieces"])*Decimal(orderProduct["calculated_price_per_piece"])
			subOrders[sellersHash[sellerID]]["edited_price"] += Decimal(orderProduct["pieces"])*Decimal(orderProduct["edited_price_per_piece"])			
		else:
			sellersHash[sellerID] = len(sellersHash)
			subOrderItem = {}
			subOrderItem["order_products"] = [orderProduct]
			subOrderItem["product_count"] = 1
			subOrderItem["retail_price"] = Decimal(orderProduct["pieces"])*Decimal(orderProduct["retail_price_per_piece"])
			subOrderItem["calculated_price"] = Decimal(orderProduct["pieces"])*Decimal(orderProduct["calculated_price_per_piece"])
			subOrderItem["edited_price"] = Decimal(orderProduct["pieces"])*Decimal(orderProduct["edited_price_per_piece"])
			subOrderItem["seller"] = seller
			subOrders.append(subOrderItem)	

	buyerAddressPtr = BuyerAddress.objects.filter(buyer_id=int(buyerPtr.id))
	buyerAddressPtr = buyerAddressPtr[0]

	orderData = {}
	orderData["product_count"] = orderProductCount
	orderData["retail_price"] = orderRetailPrice
	orderData["calculated_price"] = orderCalculatedPrice
	orderData["edited_price"] = orderEditedPrice
	orderData["remarks"] = orderRemarks
	orderData["buyerID"] = int(order["buyerID"])

	try:
		newOrder = Order(buyer=buyerPtr)
		populateOrderData(newOrder, orderData)
		newOrder.save()


		for subOrder in subOrders:
			newSubOrder = SubOrder(order=newOrder, seller=subOrder["seller"])
			populateSubOrderData(newSubOrder,subOrder,newOrder.id)
			newSubOrder.save()

			

			for orderItem in subOrder["order_products"]:

				#newSellerPayment = SellerPayment(suborder=newSubOrder)
				#newSellerPayment.save()

				#newOrderShipment = OrderShipment(suborder=newSubOrder,pickup=sellerAddressPtr,drop=buyerAddressPtr)
				#newOrderShipment.save()

				productPtr = Product.objects.filter(id=orderItem["productID"])
				productPtr = productPtr[0]

				newOrderItem = OrderItem(suborder=newSubOrder,product=productPtr)
				populateOrderItemData(newOrderItem, orderItem)
				newOrderItem.save()

	except Exception as e:
		closeDBConnection()
		return customResponse("4XX", {"error": "unable to create entry in db"})
	else:
		closeDBConnection()
		return customResponse("2XX", {"order": serializeOrder(newOrder)})

def update_order(request):
	try:
		requestbody = request.body.decode("utf-8")
		order = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse("4XX", {"error": "Invalid data sent in request"})

	if not len(order) or not "orderitemID" in order or order["orderitemID"]==None:
		return customResponse("4XX", {"error": "Id for order item not sent"})

	if not "status" in order or order["status"]==None:
		return customResponse("4XX", {"error": "Current status not sent"})

	status = int(order["status"])

	orderItemPtr = OrderItem.objects.filter(id= int(order["orderitemID"])).select_related('order_shipment','seller_payment')

	if len(orderItemPtr) == 0:
		return customResponse("4XX", {"error": "Invalid id for order item sent"})

	orderItemPtr = orderItemPtr[0]

	if not validateOrderItemStatus(status,orderItemPtr.current_status):
		return customResponse("4XX", {"error": "Improper status sent"})

	try:

		if status == 1:
			orderItemPtr.merchant_notified_time = datetime.datetime.now()
		elif status == 2:
			orderItemPtr.sent_for_pickup_time = datetime.datetime.now()
		elif status == 3:
			orderItemPtr.order_shipment.tpl_manifested_time = datetime.datetime.now()
		elif status == 4:
			orderItemPtr.order_shipment.tpl_in_transit_time = datetime.datetime.now()
		elif status == 5:
			orderItemPtr.order_shipment.tpl_stuck_in_transit_time = datetime.datetime.now()
		elif status == 6:
			orderItemPtr.order_shipment.delivered_time = datetime.datetime.now()
		elif status == 7:
			orderItemPtr.order_shipment.rto_in_transit_time = datetime.datetime.now()
		elif status == 8:
			orderItemPtr.order_shipment.rto_delivered_time = datetime.datetime.now()
		elif status == 9:
			orderItemPtr.lost_time = datetime.datetime.now()
		elif status == 10:
			orderItemPtr.cancellation_time = datetime.datetime.now()
		elif status == 11:
			orderItemPtr.completed_time = datetime.datetime.now()
		elif status == 12:
			orderItemPtr.seller_payment.payment_status = 1
			orderItemPtr.seller_payment.payment_method = order["payment_method"]
			orderItemPtr.seller_payment.payment_date = datetime.datetime.now()
			orderItemPtr.seller_payment.details = order["details"]
			orderItemPtr.closed_time = datetime.datetime.now()
		
		orderItemPtr.current_status = status
		orderItemPtr.save()
	except Exception as e:
		closeDBConnection()
		return customResponse("4XX", {"error": "could not update"})
	else:
		closeDBConnection()
		return customResponse("2XX", {"order": "order updated"})


