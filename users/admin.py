from django.contrib import admin

from .models import buyer
from .models import seller
from .models import internalUser

admin.site.register(buyer.Buyer)
admin.site.register(seller.Seller)
admin.site.register(internalUser.InternalUser)
admin.site.register(buyer.BuyerAddress)
admin.site.register(seller.SellerAddress)
