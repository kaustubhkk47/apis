from django.contrib import admin

# Register your models here.

from.models.state import State
from.models.pincode import Pincode

admin.site.register(State)
admin.site.register(Pincode)