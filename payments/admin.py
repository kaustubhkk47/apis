from django.contrib import admin

from .models import BuyerPayment, SellerPayment

admin.site.register(BuyerPayment)
admin.site.register(SellerPayment)
