from scripts.utils import *
import json
import logging
log = logging.getLogger("django")
from django.utils import timezone
from ..models.order import filterOrder, Order, validateOrderProductsData, populateOrderData, sendOrderMail
from users.models.buyer import Buyer, BuyerAddress
from catalog.models.product import Product
from ..models.subOrder import SubOrder, populateSubOrderData, sendSubOrderMail, populateSellerMailDict, sendSubOrderCancellationMail
from ..models.orderItem import OrderItem, populateOrderItemData
from ..serializers.order import parseOrders, serializeOrder
from decimal import Decimal
from django.core.paginator import Paginator
import math

def get_order_details(request, parameters):
	try:
		orders = filterOrder(parameters)

		paginator = Paginator(orders, parameters["itemsPerPage"])

		try:
			pageItems = paginator.page(parameters["pageNumber"])
		except Exception as e:
			pageItems = []

		body = parseOrders(pageItems,parameters)
		statusCode = 200
		response = {"orders": body}
		responsePaginationParameters(response,paginator, parameters)

	except Exception as e:
		log.critical(e)
		statusCode = 500
		response = {}

	closeDBConnection()
	return customResponse(statusCode, response, error_code=0)

def post_new_order(request, parameters={}):
	try:
		requestbody = request.body.decode("utf-8")
		order = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse(400, error_code=4)

	if not len(order):
		return customResponse(400, error_code=5, error_details=  "Invalid data for order sent")

	if not "buyerID" in order or not validate_integer(order["buyerID"]):
		return customResponse(400, error_code=5, error_details= "Id for buyer not sent")

	buyerPtr = Buyer.objects.filter(id=int(order["buyerID"]), delete_status=False)

	if len(buyerPtr) == 0:
		return customResponse(400, error_code=6, error_details = "Invalid id for buyer sent")

	buyerPtr = buyerPtr[0]

	if not "products" in order or order["products"]==None:
		return customResponse(400, error_code=5, error_details="Products in order not sent")

	productsHash = {}
	productIDarr = []

	if not validateOrderProductsData(order["products"], productsHash, productIDarr):
		return customResponse(400, error_code=5, error_details="Products in order not sent properly sent")

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

	allProducts = Product.objects.filter(id__in=productIDarr, delete_status=False).select_related('seller')

	if not len(allProducts) == len(productIDarr):
		return customResponse(400, error_code=6, error_details="Improper product IDs in order sent")

	for productPtr in allProducts:
		
		orderProduct = orderProducts[productsHash[productPtr.id]]

		orderProduct["retail_price_per_piece"] = productPtr.price_per_unit
		orderProduct["lot_size"] = productPtr.lot_size

		orderProduct["final_price"] = Decimal(orderProduct["pieces"])*Decimal(orderProduct["edited_price_per_piece"])
		orderProduct["lots"] = int(math.ceil(float(orderProduct["pieces"])/productPtr.lot_size))
		orderProduct["calculated_price_per_piece"] = productPtr.getCalculatedPricePerPiece(int(orderProduct["lots"]))

		seller = productPtr.seller
		sellerID = seller.id

		orderProductCount += 1
		orderPieces += int(orderProduct["pieces"])
		orderRetailPrice += Decimal(orderProduct["pieces"])*Decimal(orderProduct["retail_price_per_piece"])
		orderCalculatedPrice += Decimal(orderProduct["pieces"])*Decimal(orderProduct["calculated_price_per_piece"])
		orderEditedPrice += Decimal(orderProduct["pieces"])*Decimal(orderProduct["edited_price_per_piece"])

		if sellerID in sellersHash:
			position = sellersHash[sellerID]
			subOrders[position]["order_products"].append(orderProduct)
			subOrders[position]["product_count"] += 1
			subOrders[position]["pieces"] += int(orderProduct["pieces"])
			subOrders[position]["retail_price"] += Decimal(orderProduct["pieces"])*Decimal(orderProduct["retail_price_per_piece"])
			subOrders[position]["calculated_price"] += Decimal(orderProduct["pieces"])*Decimal(orderProduct["calculated_price_per_piece"])
			subOrders[position]["edited_price"] += Decimal(orderProduct["pieces"])*Decimal(orderProduct["edited_price_per_piece"])			
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
		newOrder.placed_by = "Admin : Id = " + str(parameters["internalusersArr"][0])
		newOrder.save()
		
		for subOrder in subOrders:
			newSubOrder = SubOrder(order=newOrder, seller=subOrder["seller"])
			populateSubOrderData(newSubOrder,subOrder,newOrder.id)
			newSubOrder.save()

			orderItemstoCreate = []

			for orderItem in subOrder["order_products"]:
				newOrderItem = OrderItem(suborder=newSubOrder,product_id=int(orderItem["productID"]))
				populateOrderItemData(newOrderItem, orderItem)
				#newOrderItem.save()
				orderItemstoCreate.append(newOrderItem)

			OrderItem.objects.bulk_create(orderItemstoCreate)
		
		sendOrderMail(newOrder)
		newOrder.sendOrderNotification("Wholdus Order confirmed", "Order ID : " + newOrder.display_number)
		subOrders = SubOrder.objects.filter(order_id = newOrder.id)
		buyerAddressPtr = newOrder.buyer_address_history
		for SubOrderPtr in subOrders:
			seller_mail_dict = populateSellerMailDict(SubOrderPtr, buyerPtr, buyerAddressPtr)
			sendSubOrderMail(SubOrderPtr, seller_mail_dict)


	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse(500, error_code = 1)
	else:
		
		closeDBConnection()
		return customResponse(200, {"order": serializeOrder(newOrder)})

def update_order(request,parameters={}):
	try:
		requestbody = request.body.decode("utf-8")
		order = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse(400, error_code=4)

	if not len(order) or not "orderID" in order or not validate_integer(order["orderID"]):
		return customResponse(400, error_code=5,  error_details= "Id for order not sent")

	orderPtr = Order.objects.filter(id=int(order["orderID"]))

	if len(orderPtr) == 0:
		return customResponse(400, error_code=6, error_details = "Invalid id for order sent")

	orderPtr = orderPtr[0]

	if not "order_status" in order or not validate_integer(order["order_status"]):
		return customResponse(400, error_code=5,  error_details="Current status not sent")

	status = int(order["order_status"])

	if not orderPtr.validateOrderStatus(status):
		return customResponse(400, error_code=6,  error_details="Improper status sent")

	try:
		orderPtr.order_status = 1
		orderPtr.save()

		nowTime = timezone.now()
		
		OrderItem.objects.filter(suborder__order_id = orderPtr.id, current_status=0).update(current_status=1, updated_at = nowTime)
		allSubOrders = SubOrder.objects.filter(order_id = orderPtr.id,suborder_status=0)
		allSubOrders.update(suborder_status=1, updated_at=nowTime)

		buyerPtr = orderPtr.buyer
		#buyerAddressPtr = BuyerAddress.objects.filter(buyer_id=int(buyerPtr.id))
		#buyerAddressPtr = buyerAddressPtr[0]
		buyerAddressPtr = orderPtr.buyer_address_history

		buyer_subject = "Order Confirmed with order ID {}".format(orderPtr.display_number)
		sendOrderMail(orderPtr, buyer_subject)
		orderPtr.sendOrderNotification("Order No {} Confirmed".format(newOrder.display_number), "Order will be shipped shortly")
		allSubOrders = SubOrder.objects.filter(order_id = orderPtr.id,suborder_status=1)
		for subOrderPtr in allSubOrders: 
			seller_mail_dict = populateSellerMailDict(subOrderPtr, buyerPtr, buyerAddressPtr)
			sendSubOrderMail(subOrderPtr, seller_mail_dict)

	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse(500, error_code = 3)
	else:
		closeDBConnection()
		return customResponse(200, {"order": "order updated"})

def cancel_order(request,parameters={}):
	try:
		requestbody = request.body.decode("utf-8")
		order = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse(400, error_code=4)

	if not len(order) or not "orderID" in order or not validate_integer(order["orderID"]):
		return customResponse(400, error_code=5,  error_details="Id for order not sent")

	orderPtr = Order.objects.filter(id=int(order["orderID"]))

	if len(orderPtr) == 0:
		return customResponse(400, error_code=6, error_details ="Invalid id for order sent")

	orderPtr = orderPtr[0]

	if not "cancellation_remarks" in order or order["cancellation_remarks"]==None:
		order["cancellation_remarks"] = ""

	if orderPtr.order_status == -1:
		return customResponse(400, error_code=6,  error_details="Already cancelled")

	try:
		nowDateTime = timezone.now()
		orderPtr.order_status = -1
		orderPtr.cancellation_remarks = order["cancellation_remarks"]
		orderPtr.cancellation_time = nowDateTime
		orderPtr.save()

		OrderItem.objects.filter(suborder__order_id = orderPtr.id).update(current_status=4, cancellation_time=nowDateTime, updated_at = nowDateTime)
		allSubOrders = SubOrder.objects.filter(order_id = orderPtr.id)
		allSubOrders.update(suborder_status=-1, cancellation_time=nowDateTime, updated_at = nowDateTime)

		buyerPtr = orderPtr.buyer
		#buyerAddressPtr = BuyerAddress.objects.filter(buyer_id=int(buyerPtr.id))
		#buyerAddressPtr = buyerAddressPtr[0]
		buyerAddressPtr = orderPtr.buyer_address_history

		allSubOrders = SubOrder.objects.filter(order_id = orderPtr.id,suborder_status=-1)

		for subOrderPtr in allSubOrders:
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