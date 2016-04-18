from scripts.utils import customResponse, closeDBConnection

from ..models.category import Category
from ..models.product import Product
from ..models.productLot import ProductLot
from ..serializers.product import multiple_products_parser

def get_product_details(productsArr = []):

	try:
		if len(productsArr) == 0:
			return customResponse("4XX", {"error": "Specify product id"})
		elif len(productsArr) == 1:
			products = ProductLot.objects.filter(product__id=productsArr[0]).select_related('product','product__category','product__seller','product__productdetails').order_by('product__id','lot_size_from')
			closeDBConnection()
			return customResponse("2XX", {"products": multiple_products_parser(products)})
		else:
			products = ProductLot.objects.filter(product__id__in=productsArr).select_related('product','product__category','product__seller','product__productdetails').order_by('product__id','lot_size_from')
			closeDBConnection()
			return customResponse("2XX", {"products": multiple_products_parser(products)})

	except Exception as e:
		return customResponse("4XX", {"error": "Invalid product"})
