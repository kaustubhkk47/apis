from django.db import models
from django.contrib import admin

from scripts.utils import create_email, link_to_foreign_key, validate_integer, validate_number

from users.models.buyer import Buyer, BuyerAddress

from general.models.smssent import send_sms

from catalog.models.product import Product
from catalog.models.productLot import getCalculatedPricePerPiece
from .orderItem import OrderItem, OrderItemNonCompletionStatus
from .subOrder import SubOrder, populateSellerMailDict
from users.serializers.buyer import serialize_buyer_address
from users.models.buyer import sendNotification

from decimal import Decimal
import math

class Order(models.Model):

	buyer = models.ForeignKey('users.Buyer')
	cart = models.ForeignKey('orders.Cart', null=True, blank=True)
	buyer_address_history = models.ForeignKey('users.BuyerAddressHistory', null=True, blank=True)

	pieces = models.PositiveIntegerField(default=1)
	product_count = models.PositiveIntegerField(default=1)
	retail_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
	calculated_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
	edited_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
	cod_charge = models.DecimalField(max_digits=10, decimal_places=2,default=0)
	shipping_charge = models.DecimalField(max_digits=10, decimal_places=2,default=0)
	final_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
	
	order_status = models.IntegerField(default=0)
	order_payment_status = models.IntegerField(default=0)

	display_number = models.CharField(max_length=20, blank=True)

	remarks = models.TextField(blank=True)
	placed_by = models.CharField(max_length=100)
	
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	cancellation_remarks = models.TextField(blank=True)
	cancellation_time = models.DateTimeField(null=True, blank=True)

	class Meta:
		ordering = ["-id"]
		default_related_name = "order"
		verbose_name="Order"
		verbose_name_plural = "Orders"

	def __unicode__(self):
		return "{} - {} - {}".format(self.id,self.display_number,self.buyer.name)

	def populateDataFromCart(self, cartPtr):
		self.cart = cartPtr
		self.buyer_id = cartPtr.buyer_id
		self.product_count = cartPtr.product_count
		self.pieces = cartPtr.pieces
		self.retail_price = cartPtr.retail_price
		self.calculated_price = cartPtr.calculated_price
		self.edited_price = cartPtr.calculated_price
		self.shipping_charge = cartPtr.shipping_charge
		self.cod_charge = cartPtr.cod_charge
		self.final_price = cartPtr.final_price
		self.order_status = 0
		self.placed_by = "buyer"
		self.save()
		self.display_number = "1" +"%06d" %(self.id,)

	def validateOrderStatus(self, status):
		current_status = self.order_status
		if current_status == 0 and (status == 1):
			return True
		return False

	def sendOrderNotification(self, title, body):
		notification = {}
		notification["title"] = title
		notification["body"] = body
		data = {}
		data["activity"] = "OrderDetails"
		data["orderID"] = str(self.id)
		sendNotification(self.buyer.get_firebase_tokens(), notification = notification, data = data)

	def sendOrderSMS(self, body):
		buyer = self.buyer
		message_text = "Hi"
		if buyer.name != "":
			message_text += " " + buyer.name
		elif buyer.company_name != "":
			message_text += " " +  buyer.company_name

		message_text += ", your order " + self.display_number + " "
		message_text += body
		send_sms(message_text, buyer.mobile_number, "buyer", "Order notification")

class OrderAdmin(admin.ModelAdmin):
	search_fields = ["buyer__name", "display_number", "buyer__company_name", "buyer__mobile_number"]
	list_display = ["id", "display_number", "link_to_buyer", "final_price", "pieces"]

	list_display_links = ["display_number","link_to_buyer"]

	list_filter = ["order_status", "order_payment_status"]

	def link_to_buyer(self, obj):
		return link_to_foreign_key(obj, "buyer")
	link_to_buyer.short_description = "Buyer"
	link_to_buyer.allow_tags=True

def populateOrderData(orderPtr, order):
	orderPtr.product_count = int(order["product_count"])
	orderPtr.pieces = int(order["pieces"])
	orderPtr.retail_price = Decimal(order["retail_price"])
	orderPtr.calculated_price = Decimal(order["calculated_price"])
	orderPtr.edited_price = Decimal(order["edited_price"])
	orderPtr.final_price = order["edited_price"]
	orderPtr.remarks = order["remarks"]
	orderPtr.order_status = 1
	orderPtr.save()
	orderPtr.buyer_address_history = orderPtr.buyer.latest_buyer_address_history(int(order["addressID"]))
	orderPtr.display_number = "1" +"%06d" %(orderPtr.id,)

def filterOrder(orderParameters):
	orders = Order.objects.all().select_related('buyer')
		
	if "orderArr" in orderParameters:
		orders = orders.filter(id__in=orderParameters["orderArr"])

	if "orderStatusArr" in orderParameters:
		orders = orders.filter(order_status__in=orderParameters["orderStatusArr"])

	if "orderPaymentStatusArr" in orderParameters:
		orders = orders.filter(order_payment_status__in=orderParameters["orderPaymentStatusArr"])

	if "buyersArr" in orderParameters:
		orders = orders.filter(buyer_id__in=orderParameters["buyersArr"])

	return orders

def validateOrderProductsData(orderProducts,  productsHash, productIDarr):

	for orderProduct in orderProducts:
		if not "productID" in orderProduct or not validate_integer(orderProduct["productID"]):
			return False

		productID = int(orderProduct["productID"])

		if not "pieces" in orderProduct or not validate_integer(orderProduct["pieces"]):
			return False
		if not "edited_price_per_piece" in orderProduct or not validate_number(orderProduct["edited_price_per_piece"]):
			return False
		if not "remarks" in orderProduct or orderProduct["remarks"]==None:
			orderProduct["remarks"] = ""

		productsHash[productID] = len(productsHash)
		productIDarr.append(productID)

	return True

def update_order_completion_status(order):

	orderItemQuerySet = OrderItem.objects.filter(suborder__order_id = order.id, current_status__in=OrderItemNonCompletionStatus)
	if not orderItemQuerySet.exists():
		order.order_status = 3
		order.save()

OrderStatus = {
	-1:{"display_value":"Cancelled"},
	0:{"display_value":"Unconfirmed"},
	1:{"display_value":"Confirmed"},
	2:{"display_value":"Partially Shipped"},
	3:{"display_value":"Shipped"},
	4:{"display_value":"Completed"}
}

OrderPaymentStatus = {
	0:{"display_value":"Not Paid"},
	1:{"display_value":"Paid"},
	2:{"display_value":"Partially paid"}
}

## Status: Placed, confirmed, shipped, delivered
## Payment status : paid, not paid, partially paid

def sendOrderMail(OrderPtr, buyer_subject = ""):
	from_email = "Wholdus Info <info@wholdus.com>"
	buyerPtr = OrderPtr.buyer

	if buyerPtr.email != None and buyerPtr.email != "":
		buyer_mail_template_file = "buyer/new_order.html"
		if buyer_subject == "":
			buyer_subject = "New order placed with order ID " + OrderPtr.display_number
		buyer_to = [buyerPtr.email]
		buyer_bcc = ["aditya.rana@wholdus.com", "kushagra@wholdus.com"]
		buyer_mail_dict = populateBuyerMailDict(OrderPtr, buyerPtr)

		create_email(buyer_mail_template_file,buyer_mail_dict,buyer_subject,from_email,buyer_to,bcc=buyer_bcc)

def populateBuyerMailDict(OrderPtr, buyerPtr):
	buyer_mail_dict = {}
	buyerMargin = (float(OrderPtr.retail_price) - float(OrderPtr.final_price))/float(OrderPtr.retail_price)*100

	buyer_mail_dict["order"] = {
		"orderNumber":OrderPtr.display_number,
		"product_count":OrderPtr.product_count,
		"final_price":'{0:.0f}'.format(OrderPtr.final_price),
		"pieces":OrderPtr.pieces,
		"total_margin":'{0:.1f}'.format(buyerMargin)
	}

	#buyerAddressPtr = BuyerAddress.objects.filter(buyer_id=int(buyerPtr.id))
	#buyerAddressPtr = buyerAddressPtr[0]

	buyerAddressPtr = OrderPtr.buyer_address_history

	buyer_mail_dict["subOrders"] = []

	subOrders = SubOrder.objects.filter(order_id = OrderPtr.id)

	for SubOrderPtr in subOrders:
		
		seller_mail_dict = populateSellerMailDict(SubOrderPtr, buyerPtr, buyerAddressPtr)
		
		seller_mail_dict["suborder"]["isBuyer"] = "Yes"
		if SubOrderPtr.seller.company_name != None and SubOrderPtr.seller.company_name != "":
			seller_mail_dict["suborder"]["items_title"] = SubOrderPtr.seller.company_name
		else:
			seller_mail_dict["suborder"]["items_title"] = SubOrderPtr.seller.name
		buyer_mail_dict["subOrders"].append(seller_mail_dict)

	return buyer_mail_dict