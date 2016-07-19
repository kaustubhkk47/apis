from django.contrib import admin

# Register your models here.

from.models.state import *
from.models.pincode import *
from.models.city import *
from.models.country import *

admin.site.register(State, StateAdmin)
admin.site.register(Pincode, PincodeAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(Country, CountryAdmin)