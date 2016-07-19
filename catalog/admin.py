from django.contrib import admin

from .models.product import *
from .models.productLot import *
from .models.productData import *
from .models.category import *

admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductLot)
admin.site.register(ProductDetails, ProductDetailsAdmin)
admin.site.register(FabricType)
admin.site.register(ColourType)