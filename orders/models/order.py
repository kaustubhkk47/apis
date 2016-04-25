from django.db import models

from users.models.buyer import *
#from users.models.seller import *

class Order(models.Model):

    buyer = models.ForeignKey(Buyer)

    product_count = models.PositiveIntegerField(default=1)
    undiscounted_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    #order_status = models.IntegerField(default=0)    

    remarks = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return str(self.id)

        

orderPaymentStatus = {
    "not_paid":{
        "value":0,
        "display_value":"Not paid"
    },
    "buyer_paid":{
        "value":1,
        "display_value":"Paid by buyer"
    },
    "paid_to_seller":{
        "value":2,
        "display_value":"Paid to all merchants"
    }
}


orderStatus = {
    "unconfirmed" : {
        "value":0,
        "display_value":"Pending confirmation"
    },
    "confirmed" : {
        "value":1,
        "display_value":"Confirmed by buyer"
    },
    "completed" :{
        "value":2,
        "display_value":"Completed"
    },
    "cancelled":{
        "value":3,
        "display_value":"Cancelled"
    }
}

