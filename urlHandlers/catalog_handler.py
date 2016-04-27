from django.views.decorators.csrf import csrf_exempt

from catalog.views import categories
from catalog.views import product
from scripts.utils import customResponse, get_token_payload
import jwt as JsonWebToken

@csrf_exempt
def categories_details(request):

	if request.method == "GET":
		categoryID = request.GET.get("categoryID", "")
		if categoryID == "":
			categoriesArr = []
		else:
			categoriesArr = [int(e) if e.isdigit() else e for e in categoryID.split(",")]
		return categories.get_categories_details(request,categoriesArr)
	elif request.method == "POST":
		return categories.post_new_category(request)
	elif request.method == "PUT":
		return categories.update_category(request)
	elif request.method == "DELETE":
		return categories.delete_category(request)

	return customResponse("4XX", {"error": "Invalid request"})


@csrf_exempt
def product_details(request):

	if request.method == "GET":
		productID = request.GET.get("productID", "")
		categoryID = request.GET.get("categoryID", "")
		sellerID = request.GET.get("sellerID", "")
		if productID == "":
			productsArr = []
		else:
			productsArr = [int(e) if e.isdigit() else e for e in productID.split(",")]
		if categoryID == "":
			categoriesArr = []
		else:
			categoriesArr = [int(e) if e.isdigit() else e for e in categoryID.split(",")]
		accessToken = request.GET.get("access_token", "")
		tokenPayload = get_token_payload(accessToken, "sellerID")
		if "sellerID" in tokenPayload and tokenPayload["sellerID"]!=None:
			sellerArr = [tokenPayload["sellerID"]]
		elif sellerID == "":
			sellerArr = []
		else:
			sellerArr = [int(e) if e.isdigit() else e for e in sellerID.split(",")]
		return product.get_product_details(request,productsArr,categoriesArr,sellerArr)
	elif request.method == "POST":
		return product.post_new_product(request)
	elif request.method == "PUT":
		return product.update_product(request)
	elif request.method == "DELETE":
		return product.delete_product(request)

	return customResponse("4XX", {"error": "Invalid request"})
