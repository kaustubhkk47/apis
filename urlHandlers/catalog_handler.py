from django.views.decorators.csrf import csrf_exempt

from catalog.views import categories
from catalog.views import product
from scripts.utils import customResponse

@csrf_exempt
def categories_details(request, categoryID = ""):

	if request.method == "GET":
		categoryID = request.GET.get("categoryID", "")
		if categoryID == "":
			categoriesArr = []
		else:
			categoriesArr = [int(e) if e.isdigit() else e for e in categoryID.split(",")]
		return categories.get_categories_details(request, categoriesArr)
	elif request.method == "POST":
		return categories.post_new_category(request)
	elif request.method == "PUT":
		return categories.update_category(request)
	elif request.method == "DELETE":
		return categories.delete_category(request)

	return customResponse("4XX", {"error": "Invalid request"})


@csrf_exempt
def product_details(request, productID = ""):

	if request.method == "GET":
		productID = request.GET.get("productID", "")
		if productID == "":
			productsArr = []
		else:
			productsArr = [int(e) if e.isdigit() else e for e in productID.split(",")]
		return product.get_product_details(request,productsArr)
	elif request.method == "POST":
		return product.post_new_product(request)
	elif request.method == "PUT":
		return product.update_product(request)
	elif request.method == "DELETE":
		return product.delete_product(request)

	return customResponse("4XX", {"error": "Invalid request"})
