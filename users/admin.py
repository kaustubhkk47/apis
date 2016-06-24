from django.contrib import admin

from .models.buyer import *
from .models.seller import *
from .models.internalUser import *
from .models.businessType import *

admin.site.register(Buyer)
admin.site.register(BuyerAddress)
admin.site.register(BuyerDetails)
admin.site.register(BuyerInterest)
admin.site.register(BuyerInterestHistory)
admin.site.register(BuyerProducts)
admin.site.register(BuyerPurchasingState)
admin.site.register(BuyerBuysFrom)

admin.site.register(Seller,SellerAdmin)
admin.site.register(SellerAddress)
admin.site.register(SellerDetails)
admin.site.register(SellerBankDetails)

admin.site.register(InternalUser)

admin.site.register(BusinessType)
