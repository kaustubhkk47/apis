from django.views.decorators.csrf import csrf_exempt

from catalog.views.categories import *
from catalog.views.product import *

@csrf_exempt
def categories_details(request, categoryIds = ""):

    
    if request.method == "GET":
    	categoryIds = request.GET.get("categoryIds", "")
        return get_categories_details(categoryIds)
    
    return customResponse("4XX", {"error": "Invalid request"})


@csrf_exempt
def product_details(request, productIds = ""):

    
    if request.method == "GET":
    	productIds = request.GET.get("productIds", "")
        return get_product_details(productIds)
    
    return customResponse("4XX", {"error": "Invalid request"})
