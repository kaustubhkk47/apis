from django.contrib import admin

from .models.order import Order
from .models.orderItem import OrderItem
from .models.orderShipment import OrderShipment

admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(OrderShipment)
