from django.contrib import admin

# Register your models here.

from.models.state import State
from.models.pincode import Pincode
from.models.city import City
from.models.country import Country

admin.site.register(State)
admin.site.register(Pincode)
admin.site.register(City)
admin.site.register(Country)