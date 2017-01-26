from users.models.seller import filterSellerCategory
from users.serializers.seller import parse_seller_category
from users.models.buyer import filterBuyerInterest
from catalog.models.product import filterProducts

def serialize_categories(categoriesItem, parameters = {}):
	category = {}
	category["name"]= categoriesItem.name
	category["display_name"]= categoriesItem.display_name
	category["slug"]= categoriesItem.slug
	category["image_url"]= categoriesItem.image_url
	category["created_at"]= categoriesItem.created_at
	category["updated_at"]= categoriesItem.updated_at
	category["categoryID"]= categoriesItem.id
	category["id"]= categoriesItem.id
	category["url"]= categoriesItem.slug + "-" + str(categoriesItem.id)
	category["show_online"]= categoriesItem.show_online

	if "seller_category_details" in parameters and parameters["seller_category_details"] == 1:
		sellerCategoryPtr = filterSellerCategory(parameters)
		sellerCategoryPtr = sellerCategoryPtr.filter(category_id=categoriesItem.id)
		category["seller_categories"] = parse_seller_category(sellerCategoryPtr, parameters)

	if "isBuyer" in parameters and parameters["isBuyer"] == 1:

		buyerInterestPtr = filterBuyerInterest(parameters)
		buyerInterestPtr = buyerInterestPtr.filter(category_id=categoriesItem.id)

		if len(buyerInterestPtr) > 0:
			buyerInterestPtr = buyerInterestPtr[0]
			from users.serializers.buyer import serialize_buyer_interest
			category["buyer_interest"] = serialize_buyer_interest(buyerInterestPtr, parameters)

	if "category_product_details" in parameters and parameters["category_product_details"] == 1:
		parameters["product_show_online"] = 1
		parameters["product_verification"] = 1
		productPtr = filterProducts(parameters)
		productPtr = productPtr.filter(category_id=categoriesItem.id)[0:12]
		from .product import multiple_products_parser
		category["products"] = multiple_products_parser(productPtr, parameters)

	
	return category


def categories_parser(categoryQuerySet, parameters={}):
	categories = []

	for i in range(len(categoryQuerySet)):
		categories.append(serialize_categories(categoryQuerySet[i], parameters))

	return categories
