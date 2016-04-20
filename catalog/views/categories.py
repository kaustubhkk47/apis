from scripts.utils import customResponse, closeDBConnection

from ..models.category import Category
from ..models.product import Product
from ..models.productLot import ProductLot
from ..serializers.category import categories_parser
from ..serializers.product import category_products_parser

def get_categories_details(request, categoriesArr = []):
	try:
		if len(categoriesArr) == 0:
			categories = Category.objects.all()
			closeDBConnection()
			return customResponse("2XX", {"categories": categories_parser(categories)})
		else:
			categoriesWithProducts = Product.objects.filter(category__id__in=categoriesArr).select_related('category','seller')
			closeDBConnection()
			return customResponse("2XX", {"products": category_products_parser(categoriesWithProducts)})

	except Exception as e:
		return customResponse("4XX", {"error": "Invalid category"})
