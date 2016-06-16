from django.contrib import admin

# Register your models here.

from.models.logisticspartner import LogisticsPartner
from.models.serviceability import PincodeServiceability

admin.site.register(LogisticsPartner)
admin.site.register(PincodeServiceability)
