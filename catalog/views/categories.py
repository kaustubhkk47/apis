from scripts.utils import customResponse, closeDBConnection

from ..models.category import Category

from ..serializers.category import categories_parser


def get_categories_details():
    

    try:
        categories = Category.objects.all()
        closeDBConnection()
    except Exception as e:
    	print e
        return customResponse("4XX", {"error": "Invalid category"})

    return customResponse("2XX", {"categories": categories_parser(categories)})