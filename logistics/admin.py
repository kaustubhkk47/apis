from django.contrib import admin

# Register your models here.

from.models.logisticspartner import *
from.models.serviceability import *

admin.site.register(LogisticsPartner)
admin.site.register(PincodeServiceability, PincodeServiceabilityAdmin)
