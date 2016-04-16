from django.views.decorators.csrf import csrf_exempt

from catalog.views.categories import *

@csrf_exempt
def categories_details(request):
    
    if request.method == "GET":
        return get_categories_details()
    
    return customResponse("4XX", {"error": "Invalid request"})
