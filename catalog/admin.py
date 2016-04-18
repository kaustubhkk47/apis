from django.contrib import admin

from .models.product import *
from .models.productLot import *
from .models.category import *

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductLot)
admin.site.register(ProductDetails)
