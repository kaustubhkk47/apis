from users.models.seller import filterSellerCategory
from users.serializers.seller import parse_seller_category
def serialize_categories(categoriesItem, parameters = {}):
	category = {}
	category["name"]= categoriesItem.name
	category["display_name"]= categoriesItem.display_name
	category["slug"]= categoriesItem.slug
	category["created_at"]= categoriesItem.created_at
	category["updated_at"]= categoriesItem.updated_at
	category["categoryID"]= categoriesItem.id
	category["id"]= categoriesItem.id
	category["url"]= categoriesItem.slug + "-" + str(categoriesItem.id)

	if "seller_category_details" in parameters and parameters["seller_category_details"] == 1:
		sellerCategoryPtr = filterSellerCategory(parameters)
		sellerCategoryPtr = sellerCategoryPtr.filter(category_id=categoriesItem.id)
		category["seller_categories"] = parse_seller_category(sellerCategoryPtr, parameters)
	
	return category


def categories_parser(categoryQuerySet, parameters={}):
	categories = []

	for i in range(len(categoryQuerySet)):
		categories.append(serialize_categories(categoryQuerySet[i], parameters))

	return categories
