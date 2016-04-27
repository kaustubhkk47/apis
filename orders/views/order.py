from scripts.utils import customResponse, closeDBConnection, convert_keys_to_string
import json
from ..models.order import *
from ..models.orderItem import *
from ..models.orderShipment import *
from ..models.subOrder import *
from ..serializers.orderitem import *
from payments.models.sellerPayment import *
from users.models.buyer import *
from users.models.seller import *
from decimal import Decimal
import datetime


def get_order_details(request, statusArr=[]):
	try:
		if len(statusArr) == 0:
			orderItems = OrderItem.objects.all().select_related('suborder', 'suborder__seller', 'suborder__order',
													   'suborder__order__buyer', 'order_shipment', 'order_shipment__pickup', 'order_shipment__drop', 'seller_payment')
		else:
			orderItems = OrderItem.objects.filter(current_status__in=statusArr).select_related(
				'suborder', 'suborder__seller', 'suborder__order', 'suborder__order__buyer', 'ordershipment', 'ordershipment__pickup', 'ordershipment__drop', 'sellerpayment')
		closeDBConnection()
		body = parseOrderItem(orderItems)
		statusCode = "2XX"
		response = {"order_items": body}

	except Exception as e:
		statusCode = "4XX"
		response = {"error": "Invalid request"}

	return customResponse(statusCode, response)


def post_new_order(request):
	try:
		requestbody = request.body.decode("utf-8")
		order = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		print e
		return customResponse("4XX", {"error": "Invalid data sent in request"})

	if not len(order):
		return customResponse("4XX", {"error": "Invalid data for buyer sent"})

	if not "buyerID" in order or not order["buyerID"]!=None:
		return customResponse("4XX", {"error": "Id for buyer not sent"})

	buyerPtr = Buyer.objects.filter(id=int(order["buyerID"]))

	if len(buyerPtr) == 0:
		return customResponse("4XX", {"error": "Invalid id for buyer sent"})

	buyerPtr = buyerPtr[0]

	if not "products" in order or not order["products"]!=None:
		return customResponse("4XX", {"error": "Products in order not sent"})
	if not validateOrderProductsData(order["products"]):
		return customResponse("4XX", {"error": "Products in order not sent properly sent"})

	orderProducts = order["products"]

	sellersHash = {}

	if not "remarks" in order or not order["remarks"]!=None:
		order["remarks"] = ""
	orderRemarks = order["remarks"]

	subOrders = []

	orderProductCount = 0
	orderUndiscountedPrice = Decimal(0.0)
	orderFinalPrice = Decimal(0.0)

	for orderProduct in orderProducts:
		
		productPtr = Product.objects.filter(id=orderProduct["productID"]).select_related('seller')
		productPtr = productPtr[0]

		seller = productPtr.seller
		sellerID = seller.id

		orderProductCount += 1
		orderUndiscountedPrice += Decimal(orderProduct["lots"])*Decimal(orderProduct["undiscounted_price_per_piece"])*Decimal(orderProduct["lot_size"])
		orderFinalPrice += Decimal(orderProduct["final_price"])

		if sellerID in sellersHash:
			subOrders[sellersHash[sellerID]]["order_products"].append(orderProduct)
			subOrders[sellersHash[sellerID]]["product_count"] += 1
			subOrders[sellersHash[sellerID]]["undiscounted_price"] += Decimal(orderProduct["lots"])*Decimal(orderProduct["undiscounted_price_per_piece"])*Decimal(orderProduct["lot_size"])
			subOrders[sellersHash[sellerID]]["final_price"] += Decimal(orderProduct["final_price"])
			subOrders[sellersHash[sellerID]]["total_price"] += Decimal(orderProduct["total_price"])
		else:
			sellersHash[sellerID] = len(sellersHash)
			subOrderItem = {}
			subOrderItem["order_products"] = [orderProduct]
			subOrderItem["product_count"] = 1
			subOrderItem["undiscounted_price"] = Decimal(orderProduct["lots"])*Decimal(orderProduct["undiscounted_price_per_piece"])*Decimal(orderProduct["lot_size"])
			subOrderItem["final_price"] = Decimal(orderProduct["final_price"])
			subOrderItem["total_price"] = Decimal(orderProduct["total_price"])
			subOrderItem["seller"] = seller
			subOrders.append(subOrderItem)	

	buyerAddressPtr = BuyerAddress.objects.filter(buyer__id=int(buyerPtr.id))
	buyerAddressPtr = buyerAddressPtr[0]

	try:
		newOrder = Order(buyer=buyerPtr)
		newOrder.product_count = orderProductCount
		newOrder.undiscounted_price = orderUndiscountedPrice
		newOrder.total_price = orderFinalPrice
		newOrder.remarks = orderRemarks
		newOrder.save()

		for subOrder in subOrders:
			newSubOrder = SubOrder(order=newOrder, seller=subOrder["seller"])
			newSubOrder.product_count = subOrder["product_count"]
			newSubOrder.undiscounted_price = subOrder["undiscounted_price"]
			newSubOrder.total_price = subOrder["total_price"]
			newSubOrder.final_price = subOrder["final_price"]
			newSubOrder.save()

			sellerAddressPtr = SellerAddress.objects.filter(seller__id=int(subOrder["seller"].id))
			sellerAddressPtr = sellerAddressPtr[0]

			for orderItem in subOrder["order_products"]:

				newSellerPayment = SellerPayment(suborder=newSubOrder)
				newSellerPayment.save()

				newOrderShipment = OrderShipment(suborder=newSubOrder,pickup=sellerAddressPtr,drop=buyerAddressPtr)
				newOrderShipment.save()

				productPtr = Product.objects.filter(id=orderItem["productID"])
				productPtr = productPtr[0]

				newOrderItem = OrderItem(suborder=newSubOrder,product=productPtr,order_shipment=newOrderShipment,seller_payment=newSellerPayment)
				newOrderItem.lots = orderItem["lots"]
				newOrderItem.undiscounted_price_per_piece = Decimal(orderItem["undiscounted_price_per_piece"])
				newOrderItem.actual_price_per_piece = Decimal(orderItem["actual_price_per_piece"])
				newOrderItem.total_price = Decimal(orderItem["total_price"])
				newOrderItem.cod_charge = Decimal(orderItem["cod_charge"])
				newOrderItem.shipping_charge = Decimal(orderItem["shipping_charge"])
				newOrderItem.final_price = Decimal(orderItem["final_price"])
				newOrderItem.lot_size = int(orderItem["lot_size"])
				newOrderItem.current_status = 0
				newOrderItem.save()
	except Exception as e:
		closeDBConnection()
		print e
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

	if not len(order) or not "orderitemID" in order or not order["orderitemID"]!=None:
		return customResponse("4XX", {"error": "Id for order item not sent"})

	if not "status" in order or not order["status"]!=None:
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


