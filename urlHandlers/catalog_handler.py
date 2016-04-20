from django.views.decorators.csrf import csrf_exempt

from catalog.views import categories
from catalog.views import product

@csrf_exempt
def categories_details(request, categoryID = ""):


	if request.method == "GET":
		categoryID = request.GET.get("categoryID", "")
		if categoryID == "":
			categoriesArr = []
		else:
			categoriesArr = [int(e) if e.isdigit() else e for e in categoryID.split(",")]
		return categories.get_categories_details(request, categoriesArr)

	return customResponse("4XX", {"error": "Invalid request"})


@csrf_exempt
def product_details(request, productID = ""):


	if request.method == "GET":
		productID = request.GET.get("productID", "")
		productsArr = [int(e) if e.isdigit() else e for e in productID.split(",")]
		return product.get_product_details(request,productsArr)

	return customResponse("4XX", {"error": "Invalid request"})
