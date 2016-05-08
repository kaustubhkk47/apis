from django.db import models

from users.models.buyer import *
from users.models.internalUser import *

#from orders.models.orderItem import OrderItem


class BuyerPayment(models.Model):

	#order_item = models.ForeignKey(OrderItem)
	payment_status = models.IntegerField(default=0)
	payment_method = models.IntegerField(default = 0)
	reference_number = models.CharField(max_length=255, blank=True)
	payment_date = models.DateTimeField(blank=True, null=True)
	details = models.TextField(blank=True)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return self.reference_number

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