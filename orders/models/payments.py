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
	"not_paid":{
		"value":0,
		"display_value":"Not paid"
	},
	"paid":{
		"value":0,
		"display_value":"Paid"
	}
}

SellerPaymentMethod = {
	"neft":{
		"value":0,
		"display_value": "NEFT"
	},
	"imps":{
		"value":1,
		"display_value":"IMPS"
	},
	"rtgs":{
		"value":2,
		"display_value":"RTGS"
	}
}

"""
BuyerPaymentStatus = {
	"not_paid":{
		"value":0,
		"display_value":"Not paid"
	},
	"paid":{
		"value":0,
		"display_value":"Paid"
	}
}

BuyerPaymentMethod = {
	"cod":{
		"value" = 0,
		"display_value" = "Cash on delivery"
	}
	"neft":{
		"value":1,
		"display_value" = "NEFT"
	},
	"demand_draft":{
		"value":2,
		"display_value":"Demand draft"
	},
	"cash_deposit":{
		"value":3,
		"display_value":"Cash deposit"
	},
	"cheque":{
		"value":4,
		"display_value":"Cheque"
	},
	"debit_card":{
		"value":5,
		"display_value":"Debit card"
	},
	"credit_card":{
		"value":6,
		"display_value":"Credit card"
	},
	"net_banking":{
		"value":7,
		"display_value":"Net banking"
	},
	"wallet":{
		"value":8,
		"display_value":"Wallet"
	}
}
"""