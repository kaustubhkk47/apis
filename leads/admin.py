from django.contrib import admin

# Register your models here.

from .models.buyerLeads import *
from .models.contactUsLead import *
from .models.sellerLeads import *

admin.site.register(BuyerLeads, BuyerLeadsAdmin)
admin.site.register(ContactUsLead, ContactUsLeadAdmin)
admin.site.register(SellerLeads, SellerLeadsAdmin)

