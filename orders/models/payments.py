from django.db import models

from users.models.seller import *
from users.models.internalUser import *
from users.models.buyer import *
from .subOrder import *
from .orderShipment import *
from .order import *

from scripts.utils import validate_date_time
from decimal import Decimal

class BuyerPayment(models.Model):

	order = models.ForeignKey(Order)
	order_shipment = models.ForeignKey(OrderShipment,null=True,blank=True)

	payment_status = models.IntegerField(default=0)
	payment_method = models.IntegerField(default = 0)
	reference_number = models.CharField(max_length=255, blank=True)
	payment_time = models.DateTimeField(blank=True, null=True)
	details = models.TextField(blank=True)

	payment_value = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-id"]

	def __unicode__(self):
		return str(self.id)

class SellerPayment(models.Model):

	suborder = models.ForeignKey(SubOrder)

	payment_status = models.IntegerField(default=0)
	payment_method = models.IntegerField(default=0)
	reference_number = models.CharField(max_length=255, blank=True)
	payment_time = models.DateTimeField(blank=True, null=True)
	details = models.TextField(blank=True)

	payment_value = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-id"]

	def __unicode__(self):
		return str(self.suborder.order.id) + "-" + str(self.suborder.id)

def validateBuyerPaymentData(buyerPayment):

	if not "payment_method" in buyerPayment or buyerPayment["payment_method"]==None:
		return False
	if not "reference_number" in buyerPayment or buyerPayment["reference_number"]==None:
		return False
	if not "details" in buyerPayment or buyerPayment["details"]==None:
		buyerPayment["details"] = ""
	if not "payment_time" in buyerPayment or buyerPayment["payment_time"]==None or not validate_date_time(buyerPayment["payment_time"]):
		return False
	if not "payment_value" in buyerPayment or buyerPayment["payment_value"]==None:
		return False
	if not "fully_paid" in buyerPayment or buyerPayment["fully_paid"]==None:
		return False

	return True

def populateBuyerPayment(BuyerPaymentPtr, buyerPayment):
	BuyerPaymentPtr.payment_method = int(buyerPayment["payment_method"])
	BuyerPaymentPtr.reference_number = buyerPayment["reference_number"]
	BuyerPaymentPtr.details = buyerPayment["details"]
	BuyerPaymentPtr.payment_time = buyerPayment["payment_time"]
	BuyerPaymentPtr.payment_value = Decimal(buyerPayment["payment_value"])
	BuyerPaymentPtr.payment_status = 1

def validateSellerPaymentData(sellerPayment):

	if not "payment_method" in sellerPayment or sellerPayment["payment_method"]==None:
		return False
	if not "reference_number" in sellerPayment or sellerPayment["reference_number"]==None:
		return False
	if not "details" in sellerPayment or sellerPayment["details"]==None:
		sellerPayment["details"] = ""
	if not "payment_time" in sellerPayment or sellerPayment["payment_time"]==None or not validate_date_time(sellerPayment["payment_time"]):
		return False
	if not "payment_value" in sellerPayment or sellerPayment["payment_value"]==None:
		return False
	if not "fully_paid" in sellerPayment or sellerPayment["fully_paid"]==None:
		return False

	return True

def populateSellerPayment(SellerPaymentPtr, sellerPayment):
	SellerPaymentPtr.payment_method = int(sellerPayment["payment_method"])
	SellerPaymentPtr.reference_number = sellerPayment["reference_number"]
	SellerPaymentPtr.details = sellerPayment["details"]
	SellerPaymentPtr.payment_time = sellerPayment["payment_time"]
	SellerPaymentPtr.payment_value = Decimal(sellerPayment["payment_value"])
	SellerPaymentPtr.payment_status = 1

SellerPaymentStatus = {
	0:"Not Paid",
	1:"Paid"
}

SellerPaymentMethod = {
	0:"NEFT",
	1:"IMPS",
	2:"RTGS"
}

BuyerPaymentStatus = {
	0:"Not Paid",
	1:"Paid",
	2:"Partially Paid"
}

BuyerPaymentMethod = {
	0:"COD",
	1:"NEFT",
	2:"Demand Draft",
	3:"Cash deposit",
	4:"Cheque",
	5:"Debit Card",
	6:"Credit Card",
	7:"Net Banking",
	8:"Wallet"
}
