from django.contrib import admin

from .models.buyerPayment import BuyerPayment
from .models.sellerPayment import SellerPayment

admin.site.register(BuyerPayment)
admin.site.register(SellerPayment)
