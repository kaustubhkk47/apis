from django.contrib import admin

from .models.order import Order, OrderAdmin
from .models.orderItem import OrderItem, OrderItemAdmin
from .models.orderShipment import OrderShipment, OrderShipmentAdmin
from .models.subOrder import SubOrder, SubOrderAdmin
from .models.payments import BuyerPayment, SellerPayment, BuyerPaymentAdmin, SellerPaymentAdmin
from .models.cart import Cart, CartAdmin, CartItem, CartItemAdmin, CartItemHistory

admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(OrderShipment, OrderShipmentAdmin)
admin.site.register(SubOrder, SubOrderAdmin)
admin.site.register(BuyerPayment, BuyerPaymentAdmin)
admin.site.register(SellerPayment, SellerPaymentAdmin)

admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)
admin.site.register(CartItemHistory)