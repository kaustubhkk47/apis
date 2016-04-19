from django.contrib import admin

from .models.buyer import *
from .models.seller import *
from .models.buyerAddress import *
from .models.internalUser import *
from .models.sellerAddress import *

admin.site.register(Buyer)
admin.site.register(Seller)
admin.site.register(InternalUser)
admin.site.register(BuyerAddress)
admin.site.register(SellerAddress)
