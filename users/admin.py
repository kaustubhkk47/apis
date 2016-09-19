from django.contrib import admin

from .models.buyer import *
from .models.seller import *
from .models.internalUser import *
from .models.businessType import *

admin.site.register(Buyer, BuyerAdmin)
admin.site.register(BuyerAddress)
admin.site.register(BuyerAddressHistory)
admin.site.register(BuyerDetails)
admin.site.register(BuyerInterest, BuyerInterestAdmin)
admin.site.register(BuyerInterestHistory)
admin.site.register(BuyerProducts)
admin.site.register(BuyerProductResponse, BuyerProductResponseAdmin)
admin.site.register(BuyerSharedProductID)
admin.site.register(BuyerProductResponseHistory)
admin.site.register(BuyerBuysFrom)
admin.site.register(BuyerPurchasingState)
admin.site.register(BuyerProductLanding, BuyerProductLandingAdmin)
admin.site.register(BuyerPanelInstructionsTracking)

admin.site.register(BuyerStoreLead, BuyerStoreLeadAdmin)

admin.site.register(Seller,SellerAdmin)
admin.site.register(SellerAddress)
admin.site.register(SellerAddressHistory)
admin.site.register(SellerDetails)
admin.site.register(SellerBankDetails)
admin.site.register(SellerCategory, SellerCategoryAdmin)

admin.site.register(InternalUser)

admin.site.register(BusinessType)