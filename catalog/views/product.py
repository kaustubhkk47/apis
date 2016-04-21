from scripts.utils import customResponse, closeDBConnection

from ..models.category import Category
from ..models.product import Product
from ..models.productLot import ProductLot
from ..serializers.product import multiple_products_parser

def get_product_details(request,productsArr = []):

	try:
		if len(productsArr) == 0:
			products = Product.objects.all().select_related('seller','productdetails','category')
			closeDBConnection()
		else:
			products = Product.objects.filter(id__in=productsArr).select_related('seller','productdetails','category')
			closeDBConnection()

		response = multiple_products_parser(products)
		statusCode = "2XX"
		body = {"products": response}
	except Exception as e:
		statusCode = "4XX"
		body = {"error": "Invalid product"}

	return customResponse(statusCode, body)
