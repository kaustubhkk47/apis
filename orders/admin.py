from django.contrib import admin

from .models.order import Order, OrderAdmin
from .models.orderItem import OrderItem, OrderItemAdmin
from .models.orderShipment import OrderShipment, OrderShipmentAdmin
from .models.subOrder import SubOrder, SubOrderAdmin
from .models.payments import BuyerPayment, SellerPayment, BuyerPaymentAdmin, SellerPaymentAdmin

admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(OrderShipment, OrderShipmentAdmin)
admin.site.register(SubOrder, SubOrderAdmin)
admin.site.register(BuyerPayment, BuyerPaymentAdmin)
admin.site.register(SellerPayment, SellerPaymentAdmin)
