from django.contrib import admin

# Register your models here.

from .models.buyerLeads import *
from .models.contactUsLead import *
from .models.sellerLeads import *

admin.site.register(BuyerLeads)
admin.site.register(ContactUsLead)
admin.site.register(SellerLeads)

