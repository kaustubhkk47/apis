from django.db import models

from scripts.utils import create_email

from users.models.buyer import Buyer, BuyerAddress

from catalog.models.product import Product
from catalog.models.productLot import getCalculatedPricePerPiece
from .orderItem import OrderItem, OrderItemCompletionStatus
from .subOrder import SubOrder, populateSellerMailDict
from users.serializers.buyer import serialize_buyer_address

from decimal import Decimal
import math

from scripts.utils import validate_integer, validate_number

class Order(models.Model):

	buyer = models.ForeignKey('users.Buyer')

	pieces = models.PositiveIntegerField(default=1)
	product_count = models.PositiveIntegerField(default=1)
	retail_price = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)
	calculated_price = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)
	edited_price = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)
	cod_charge = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)
	shipping_charge = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)
	final_price = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)
	
	order_status = models.IntegerField(default=0)
	order_payment_status = models.IntegerField(default=0)

	display_number = models.CharField(max_length=20, blank=True)

	remarks = models.TextField(blank=True)
	
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
		return "{} - {} - {} - Price: {}".format(self.id,self.display_number,self.buyer.name,self.final_price)

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

def validateOrderProductsData(orderProducts):

	for orderProduct in orderProducts:
		if not "productID" in orderProduct or not validate_integer(orderProduct["productID"]):
			return False

		productPtr = Product.objects.filter(id=int(orderProduct["productID"]))
		if len(productPtr) == 0:
			return False

		productPtr = productPtr[0]

		if not "pieces" in orderProduct or not validate_integer(orderProduct["pieces"]):
			return False
		if not "edited_price_per_piece" in orderProduct or not validate_number(orderProduct["edited_price_per_piece"]):
			return False
		if not "remarks" in orderProduct or orderProduct["remarks"]==None:
			orderProduct["remarks"] = ""

		orderProduct["retail_price_per_piece"] = productPtr.price_per_unit
		orderProduct["lot_size"] = productPtr.lot_size

		orderProduct["final_price"] = Decimal(orderProduct["pieces"])*Decimal(orderProduct["edited_price_per_piece"])
		orderProduct["lots"] = int(math.ceil(float(orderProduct["pieces"])/productPtr.lot_size))
		orderProduct["calculated_price_per_piece"] = getCalculatedPricePerPiece(int(orderProduct["productID"]),orderProduct["lots"])

	return True

def update_order_completion_status(order):

	orderItemQuerySet = OrderItem.objects.filter(suborder__order_id = order.id)
	for orderItem in orderItemQuerySet:
		if orderItem.current_status not in OrderItemCompletionStatus:
			return

	order.order_status = 3
	order.save()

OrderStatus = {
	-1:{"display_value":"Cancelled"},
	0:{"display_value":"Placed"},
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

def sendOrderMail(OrderPtr):
	from_email = "Wholdus Info <info@wholdus.com>"
	buyerPtr = OrderPtr.buyer

	if buyerPtr.email != None and buyerPtr.email != "":
		buyer_mail_template_file = "buyer/new_order.html"
		buyer_subject = "New order received with order ID " + OrderPtr.display_number
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

	buyerAddressPtr = BuyerAddress.objects.filter(buyer_id=int(buyerPtr.id))
	buyerAddressPtr = buyerAddressPtr[0]

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