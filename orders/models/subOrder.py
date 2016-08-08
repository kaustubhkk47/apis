from django.db import models
from django.contrib import admin
from scripts.utils import create_email, link_to_foreign_key
from users.models.seller import Seller
from users.serializers.buyer import serialize_buyer_address
#from orders.models.order import Order
from orders.models.orderItem import OrderItem, OrderItemCompletionStatus, populateMailOrderItem

from django.utils import timezone
from decimal import Decimal

class SubOrder(models.Model):

	order = models.ForeignKey('orders.Order')
	seller = models.ForeignKey('users.Seller')

	pieces = models.PositiveIntegerField(default=1)
	product_count = models.PositiveIntegerField(default=1)
	retail_price = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)
	calculated_price = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)
	edited_price = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)
	cod_charge = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)
	shipping_charge = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)
	final_price = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)

	suborder_status = models.IntegerField(default=0)
	suborder_payment_status = models.IntegerField(default=0)

	display_number = models.CharField(max_length=20, blank=True)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	confirmed_time = models.DateTimeField(null=True, blank=True)
	merchant_notified_time = models.DateTimeField(null=True, blank=True)
	completed_time = models.DateTimeField(null=True, blank=True)
	closed_time = models.DateTimeField(null=True, blank=True)

	cancellation_remarks = models.TextField(blank=True)
	cancellation_time = models.DateTimeField(null=True, blank=True)

	class Meta:
		ordering = ["-id"]
		default_related_name = "suborder"
		verbose_name="Suborder"
		verbose_name_plural = "Suborders"

	def __unicode__(self):
		return "{} - {} - {}".format(self.id,self.display_number,self.seller.name)

class SubOrderAdmin(admin.ModelAdmin):
	search_fields = ["seller__name", "display_number", "seller__company_name"]
	list_display = ["id", "display_number", "link_to_seller", "link_to_order","final_price", "pieces"]

	list_display_links = ["display_number","link_to_seller", "link_to_order"]

	list_filter = ["suborder_status", "suborder_payment_status"]

	def link_to_seller(self, obj):
		return link_to_foreign_key(obj, "seller")
	link_to_seller.short_description = "Seller"
	link_to_seller.allow_tags=True

	def link_to_order(self, obj):
		return link_to_foreign_key(obj, "order")
	link_to_order.short_description = "Order"
	link_to_order.allow_tags=True

def populateSubOrderData(subOrderPtr, subOrder,orderID):
	
	subOrderPtr.product_count = int(subOrder["product_count"])
	subOrderPtr.pieces = int(subOrder["pieces"])
	subOrderPtr.retail_price = Decimal(subOrder["retail_price"])
	subOrderPtr.calculated_price = Decimal(subOrder["calculated_price"])
	subOrderPtr.edited_price = Decimal(subOrder["edited_price"])
	subOrderPtr.final_price = subOrder["edited_price"]
	subOrderPtr.suborder_status = 1
	subOrderPtr.confirmed_time = timezone.now()
	subOrderPtr.save()
	subOrderPtr.display_number = "%04d" %(subOrder["seller"].id,) + "-" + "1" + "%06d" %(orderID,)

def validateSubOrderStatus(status, current_status):

	if status not in [2]:
		return False

	if current_status == 0:
		return False
	elif current_status == 1 and not(status == 2):
		return False
	elif current_status == 2:
		return False
	elif current_status == 3:
		return False
	elif current_status == 4:
		return False

	return True

def filterSubOrder(subOrderParameters):
	subOrders = SubOrder.objects.all().select_related('seller','order__buyer')
		
	if "subOrderArr" in subOrderParameters:
		subOrders = subOrders.filter(id__in=subOrderParameters["subOrderArr"])

	if "subOrderStatusArr" in subOrderParameters:
		subOrders = subOrders.filter(suborder_status__in=subOrderParameters["subOrderStatusArr"])

	if "subOrderPaymentStatusArr" in subOrderParameters:
		subOrders = subOrders.filter(suborder_payment_status__in=subOrderParameters["subOrderPaymentStatusArr"])

	if "sellersArr" in subOrderParameters:
		subOrders = subOrders.filter(seller_id__in=subOrderParameters["sellersArr"])

	if "orderArr" in subOrderParameters:
		subOrders = subOrders.filter(order_id__in=subOrderParameters["orderArr"])

	return subOrders

def update_suborder_completion_status(subOrder):

	orderItemQuerySet = OrderItem.objects.filter(suborder_id = subOrder.id)
	for orderItem in orderItemQuerySet:
		if orderItem.current_status not in OrderItemCompletionStatus:
			return

	subOrder.suborder_status = 4
	subOrder.save()

SubOrderStatus = {
	-1:{"display_value":"Cancelled"},
	0:{"display_value":"Unconfirmed"},
	1:{"display_value":"Confirmed"},
	2:{"display_value":"Merchant Notified"},
	3:{"display_value":"Partially Shipped"},
	4:{"display_value":"Shipped"},
	5:{"display_value":"Completed"}
}

SubOrderPaymentStatus = {
	0:{"display_value":"Not Paid"},
	1:{"display_value":"Paid"},
	2:{"display_value":"Partially paid"}
}

def sendSubOrderMail(SubOrderPtr, seller_mail_dict):
	from_email = "Wholdus Info <info@wholdus.com>"
	seller_mail_template_file = "seller/new_suborder.html"
	seller_subject = "New order received with order ID " + SubOrderPtr.display_number
	seller_to = [SubOrderPtr.seller.email]
	seller_bcc = ["manish@wholdus.com"]
	create_email(seller_mail_template_file,seller_mail_dict,seller_subject,from_email,seller_to,bcc=seller_bcc)

def sendSubOrderCancellationMail(SubOrderPtr, seller_mail_dict):
	from_email = "Wholdus Info <info@wholdus.com>"
	seller_mail_template_file = "seller/suborder_cancelled.html"
	seller_subject = "Cancellation of order with order ID " + SubOrderPtr.display_number
	seller_to = [SubOrderPtr.seller.email]
	seller_bcc = ["manish@wholdus.com"]
	create_email(seller_mail_template_file,seller_mail_dict,seller_subject,from_email,seller_to,bcc=seller_bcc)

def populateSellerMailDict(SubOrderPtr, buyerPtr, buyerAddressPtr):
	seller_mail_dict = {}
	seller_mail_dict["suborder"] = {
		"suborderNumber":SubOrderPtr.display_number,
		"product_count":SubOrderPtr.product_count,
		"final_price":'{0:.0f}'.format(SubOrderPtr.final_price),
		"pieces":SubOrderPtr.pieces
	}
	seller_mail_dict["buyer"] = {
		"name":buyerPtr.name,
		"company_name":buyerPtr.company_name
	}
	seller_mail_dict["buyerAddress"] = serialize_buyer_address(buyerAddressPtr)
	
	seller_mail_dict["orderItems"] = []

	orderItems = OrderItem.objects.filter(suborder_id=SubOrderPtr.id)

	for OrderItemPtr in orderItems:
		mailOrderItem = populateMailOrderItem(OrderItemPtr)
		seller_mail_dict["orderItems"].append(mailOrderItem)
		seller_mail_dict["suborder"]["items_title"] = "Order Items"

	return seller_mail_dict