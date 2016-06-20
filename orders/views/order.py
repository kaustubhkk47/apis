from scripts.utils import *
import json
import logging
log = logging.getLogger("django")
from ..models.order import filterOrder, Order, validateOrderProductsData, populateOrderData
from users.models.buyer import Buyer, BuyerAddress
from catalog.models.product import Product
from ..models.subOrder import SubOrder, populateSubOrderData
from ..models.orderItem import OrderItem, populateOrderItemData
from ..serializers.order import parseOrders, serializeOrder
from users.serializers.buyer import serialize_buyer_address
from decimal import Decimal

def get_order_details(request, orderParameters):
	try:
		orders = filterOrder(orderParameters)
		body = parseOrders(orders,orderParameters)
		statusCode = "2XX"
		response = {"orders": body}

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

		from_email = "Wholdus Info <info@wholdus.com>"

		buyer_mail_template_file = "buyer/new_order.html"
		buyer_subject = "New order received with order ID " + newOrder.display_number
		buyer_to = [buyerPtr.email]
		buyer_bcc = ["aditya.rana@wholdus.com", "kushagra@wholdus.com"]
		buyer_mail_dict = {}

		buyer_mail_dict["order"] = {
			"orderNumber":newOrder.display_number,
			"product_count":newOrder.product_count,
			"final_price":'{0:.0f}'.format(newOrder.final_price)
		}

		buyerMargin = (float(newOrder.retail_price) - float(newOrder.final_price))/float(newOrder.retail_price)*100
		buyer_mail_dict["order"]["total_margin"] = '{0:.1f}'.format(buyerMargin)

		buyerTotalPieces = 0

		buyer_mail_dict["subOrders"] = []
		
		for subOrder in subOrders:
			newSubOrder = SubOrder(order=newOrder, seller=subOrder["seller"])
			populateSubOrderData(newSubOrder,subOrder,newOrder.id)
			newSubOrder.save()

			seller_mail_template_file = "seller/new_suborder.html"
			seller_subject = "New order received with order ID " + newSubOrder.display_number
			seller_to = [subOrder["seller"].email]
			seller_bcc = ["manish@wholdus.com"]
			seller_mail_dict = {}

			seller_mail_dict["suborder"] = {
				"suborderNumber":newSubOrder.display_number,
				"product_count":newSubOrder.product_count,
				"final_price":'{0:.0f}'.format(newSubOrder.final_price)
			}
			seller_mail_dict["buyer"] = {
				"name":buyerPtr.name,
				"company_name":buyerPtr.company_name
			}
			seller_mail_dict["buyerAddress"] = serialize_buyer_address(buyerAddressPtr)
			
			seller_mail_dict["orderItems"] = []
			totalPieces = 0

			for orderItem in subOrder["order_products"]:

				productPtr = Product.objects.filter(id=orderItem["productID"])
				productPtr = productPtr[0]

				newOrderItem = OrderItem(suborder=newSubOrder,product=productPtr)
				populateOrderItemData(newOrderItem, orderItem)
				newOrderItem.save()

				imageLink = "http://api.wholdus.com/" + productPtr.image_path + "200x200/" + productPtr.image_name + "-1.jpg"
				productLink = "http://www.wholdus.com/" + productPtr.category.slug + "-" + str(productPtr.category_id) + "/" +productPtr.slug +"-" + str(productPtr.id)

				mailOrderItem = {
					"name":productPtr.display_name,
					"catalog_number":productPtr.productdetails.seller_catalog_number,
					"pieces":newOrderItem.pieces,
					"price_per_piece":newOrderItem.edited_price_per_piece,
					"final_price":newOrderItem.final_price,
					"image_link":imageLink,
					"product_link":productLink
				}

				itemMargin = float((newOrderItem.retail_price_per_piece - newOrderItem.edited_price_per_piece)/newOrderItem.retail_price_per_piece*100)
				mailOrderItem["margin"] = '{0:.1f}'.format(itemMargin)

				if newOrderItem.remarks != "":
					mailOrderItem["remarks"] = newOrderItem.remarks

				totalPieces += newOrderItem.pieces
				buyerTotalPieces += newOrderItem.pieces

				seller_mail_dict["orderItems"].append(mailOrderItem)

			seller_mail_dict["suborder"]["pieces"] = totalPieces
			seller_mail_dict["suborder"]["items_title"] = "Order Items"

			create_email(seller_mail_template_file,seller_mail_dict,seller_subject,from_email,seller_to,bcc=seller_bcc)

			seller_mail_dict["suborder"]["isBuyer"] = "Yes"
			if subOrder["seller"].company_name != None and subOrder["seller"].company_name != "":
				seller_mail_dict["suborder"]["items_title"] = subOrder["seller"].company_name
			else:
				seller_mail_dict["suborder"]["items_title"] = subOrder["seller"].name
			buyer_mail_dict["subOrders"].append(seller_mail_dict)

		buyer_mail_dict["order"]["pieces"] = buyerTotalPieces

		if buyerPtr.email != None and buyerPtr.email != "":	
			create_email(buyer_mail_template_file,buyer_mail_dict,buyer_subject,from_email,buyer_to,bcc=buyer_bcc)

	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse("4XX", {"error": "unable to create entry in db"})
	else:
		closeDBConnection()
		return customResponse("2XX", {"order": serializeOrder(newOrder)})