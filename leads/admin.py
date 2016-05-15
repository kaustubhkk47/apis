from django.contrib import admin

# Register your models here.

from .models.buyerLeads import *
from .models.contactUsLead import *

admin.site.register(BuyerLeads)
admin.site.register(ContactUsLead)
