from django.contrib import admin

from .models.buyer import *
from .models.seller import *
from .models.internalUser import *

admin.site.register(Buyer)
admin.site.register(BuyerAddress)
admin.site.register(BuyerDetails)

admin.site.register(Seller)
admin.site.register(SellerAddress)
admin.site.register(SellerDetails)

admin.site.register(InternalUser)
