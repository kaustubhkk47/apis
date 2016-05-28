from django.db import models

from users.models.seller import *
from users.models.internalUser import *
from users.models.buyer import *
from .subOrder import *
from .order import *

class BuyerPayment(models.Model):

	order = models.ForeignKey(Order)

	payment_status = models.IntegerField(default=0)
	payment_method = models.IntegerField(default = 0)
	reference_number = models.CharField(max_length=255, blank=True)
	payment_time = models.DateTimeField(blank=True, null=True)
	details = models.TextField(blank=True)

	payment_value = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

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

    def __unicode__(self):
        return str(self.suborder.order.id) + "-" + str(self.suborder.id)

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
	1:"Paid"
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
