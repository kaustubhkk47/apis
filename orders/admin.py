from django.contrib import admin

from .models.order import Order
from .models.orderItem import OrderItem
from .models.orderShipment import OrderShipment
from .models.subOrder import SubOrder
from .models.payments import BuyerPayment, SellerPayment

admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(OrderShipment)
admin.site.register(SubOrder)
admin.site.register(BuyerPayment)
admin.site.register(SellerPayment)
