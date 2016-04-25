from django.db import models

from users.models.seller import *
from users.models.internalUser import *
from orders.models.subOrder import *

#from orders.models.subOrder import OrderItem

class SellerPayment(models.Model):

    suborder = models.ForeignKey(SubOrder)

    payment_status = models.IntegerField(default=0)

    payment_method = models.IntegerField(default=0)
    #reference_number = models.CharField(max_length=255, blank=True)
    payment_date = models.DateTimeField(blank=True, null=True)

    details = models.TextField(blank=True)

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