from scripts.utils import *
import json
import logging
log = logging.getLogger("django")
from ..models.order import filterOrder, Order, validateOrderProductsData, populateOrderData, sendOrderMail
from users.models.buyer import Buyer, BuyerAddress
from catalog.models.product import Product
from ..models.subOrder import SubOrder, populateSubOrderData, sendSubOrderMail, populateSellerMailDict, sendSubOrderCancellationMail
from ..models.orderItem import OrderItem, populateOrderItemData
from ..serializers.order import parseOrders, serializeOrder
from decimal import Decimal
from django.core.paginator import Paginator

def get_order_details(request, orderParameters):
	try:
		orders = filterOrder(orderParameters)

		paginator = Paginator(orders, orderParameters["itemsPerPage"])

		try:
			pageItems = paginator.page(orderParameters["pageNumber"])
		except Exception as e:
			pageItems = []

		body = parseOrders(pageItems,orderParameters)
		statusCode = "2XX"
		response = {"orders": body,"total_items":paginator.count, "total_pages":paginator.num_pages, "page_number":orderParameters["pageNumber"], "items_per_page":orderParameters["itemsPerPage"]}

	except Exception as e:
		log.critical(e)
		statusCode = "4XX"
		response = {"error": "Invalid request"}

	closeDBConnection()
	return customResponse(statusCode, response)

def post_new_order(request):
	try:
		requestbody = request.body.decode("utf-8")
		order = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse("4XX", {"error": "Invalid data sent in request"})

	if not len(order):
		return customResponse("4XX", {"error": "Invalid data for order sent"})

	if not "buyerID" in order or not validate_integer(order["buyerID"]):
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
	orderPieces = 0
	orderRetailPrice = Decimal(0.0)
	orderCalculatedPrice = Decimal(0.0)
	orderEditedPrice = Decimal(0.0)

	for orderProduct in orderProducts:
		
		productPtr = Product.objects.filter(id=int(orderProduct["productID"])).select_related('seller')
		productPtr = productPtr[0]

		seller = productPtr.seller
		sellerID = seller.id

		orderProductCount += 1
		orderPieces += int(orderProduct["pieces"])
		orderRetailPrice += Decimal(orderProduct["pieces"])*Decimal(orderProduct["retail_price_per_piece"])
		orderCalculatedPrice += Decimal(orderProduct["pieces"])*Decimal(orderProduct["calculated_price_per_piece"])
		orderEditedPrice += Decimal(orderProduct["pieces"])*Decimal(orderProduct["edited_price_per_piece"])

		if sellerID in sellersHash:
			subOrders[sellersHash[sellerID]]["order_products"].append(orderProduct)
			subOrders[sellersHash[sellerID]]["product_count"] += 1
			subOrders[sellersHash[sellerID]]["pieces"] += int(orderProduct["pieces"])
			subOrders[sellersHash[sellerID]]["retail_price"] += Decimal(orderProduct["pieces"])*Decimal(orderProduct["retail_price_per_piece"])
			subOrders[sellersHash[sellerID]]["calculated_price"] += Decimal(orderProduct["pieces"])*Decimal(orderProduct["calculated_price_per_piece"])
			subOrders[sellersHash[sellerID]]["edited_price"] += Decimal(orderProduct["pieces"])*Decimal(orderProduct["edited_price_per_piece"])			
		else:
			sellersHash[sellerID] = len(sellersHash)
			subOrderItem = {}
			subOrderItem["order_products"] = [orderProduct]
			subOrderItem["product_count"] = 1
			subOrderItem["pieces"] = int(orderProduct["pieces"])
			subOrderItem["retail_price"] = Decimal(orderProduct["pieces"])*Decimal(orderProduct["retail_price_per_piece"])
			subOrderItem["calculated_price"] = Decimal(orderProduct["pieces"])*Decimal(orderProduct["calculated_price_per_piece"])
			subOrderItem["edited_price"] = Decimal(orderProduct["pieces"])*Decimal(orderProduct["edited_price_per_piece"])
			subOrderItem["seller"] = seller
			subOrders.append(subOrderItem)	

	buyerAddressPtr = BuyerAddress.objects.filter(buyer_id=int(buyerPtr.id))
	buyerAddressPtr = buyerAddressPtr[0]

	orderData = {}
	orderData["product_count"] = orderProductCount
	orderData["pieces"] = orderPieces
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
				newOrderItem = OrderItem(suborder=newSubOrder,product_id=int(orderItem["productID"]))
				populateOrderItemData(newOrderItem, orderItem)
				newOrderItem.save()

	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse("4XX", {"error": "unable to create entry in db"})
	else:
		sendOrderMail(newOrder)
		subOrders = SubOrder.objects.filter(order_id = newOrder.id)
		for SubOrderPtr in subOrders:
			seller_mail_dict = populateSellerMailDict(SubOrderPtr, buyerPtr, buyerAddressPtr)
			sendSubOrderMail(SubOrderPtr, seller_mail_dict)
		closeDBConnection()
		return customResponse("2XX", {"order": serializeOrder(newOrder)})

def cancel_order(request):
	try:
		requestbody = request.body.decode("utf-8")
		order = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse("4XX", {"error": "Invalid data sent in request"})

	if not len(order) or not "orderID" in order or not validate_integer(order["orderID"]):
		return customResponse("4XX", {"error": "Id for order not sent"})

	orderPtr = Order.objects.filter(id=int(order["orderID"]))

	if len(orderPtr) == 0:
		return customResponse("4XX", {"error": "Invalid id for order sent"})

	orderPtr = orderPtr[0]

	if not "cancellation_remarks" in order or order["cancellation_remarks"]==None:
		order["cancellation_remarks"] = ""

	if orderPtr.order_status == -1:
		return customResponse("4XX", {"error": "Already cancelled"})

	try:
		nowDateTime = datetime.datetime.now()
		orderPtr.order_status = -1
		orderPtr.cancellation_remarks = order["cancellation_remarks"]
		orderPtr.cancellation_time = nowDateTime
		orderPtr.save()

		OrderItem.objects.filter(suborder__order_id = orderPtr.id).update(current_status=4, cancellation_time=nowDateTime)
		allSubOrders = SubOrder.objects.filter(order_id = orderPtr.id)
		allSubOrders.update(suborder_status=-1, cancellation_time=nowDateTime)

		buyerPtr = orderPtr.buyer
		buyerAddressPtr = BuyerAddress.objects.filter(buyer_id=int(buyerPtr.id))
		buyerAddressPtr = buyerAddressPtr[0]

		for subOrderPtr in allSubOrders:
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