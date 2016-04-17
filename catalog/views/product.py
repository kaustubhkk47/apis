from scripts.utils import customResponse, closeDBConnection

from ..models.category import Category
from ..models.product import Product
from ..models.productLot import ProductLot
from ..serializers.product import multiple_products_parser

def get_product_details(productIds = ""):
    
    try:
    	if productIds == "":
    		return customResponse("4XX", {"error": "Specify product id"})
    	else:
    		productsArr = [int(e) if e.isdigit() else e for e in productIds.split(",")]
    		if len(productsArr) == 1:
    			products = ProductLot.objects.filter(product__id=productsArr[0]).select_related('product','product__category','product__seller').order_by('product__id','lot_size_from')
    			closeDBConnection()
    			return customResponse("2XX", {"products": multiple_products_parser(products)})
    		else:
    			products = ProductLot.objects.filter(product__id__in=productsArr).select_related('product','product__category','product__seller').order_by('product__id','lot_size_from')
    			closeDBConnection()
    			return customResponse("2XX", {"products": multiple_products_parser(products)})

    except Exception as e:
        return customResponse("4XX", {"error": "Invalid product"})