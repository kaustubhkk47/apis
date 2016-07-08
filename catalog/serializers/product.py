from decimal import Decimal
import settings

from ..models.productLot import ProductLot
from ..models.product import Product, filterProducts
from .category import serialize_categories
from users.serializers.seller import serialize_seller
import ast

def serialize_product_lots(productsItem, parameters = {}):

	productLotsQuerySet = ProductLot.objects.filter(product_id = productsItem.id)
	productLots = []

	for productLot in productLotsQuerySet:
		productLotEntry = {
			"productlotID" : productLot.id,
			"lot_size_from":productLot.lot_size_from,
			"lot_size_to":productLot.lot_size_to,
			"price_per_unit":productLot.price_per_unit
		}
		productLots.append(productLotEntry)

	return productLots

def serialize_product(productsItem, parameters = {}):

	product = {}

	product["productID"] = productsItem.id
	product["name"] = productsItem.name
	product["price_per_unit"] = productsItem.price_per_unit
	product["unit"] = productsItem.unit
	product["tax"] = productsItem.tax
	product["min_price_per_unit"] = productsItem.min_price_per_unit
	product["lot_size"] = productsItem.lot_size
	product["price_per_lot"] = productsItem.price_per_lot
	product["verification"] = productsItem.verification
	product["show_online"] = productsItem.show_online
	product["created_at"] = productsItem.created_at
	product["updated_at"] = productsItem.updated_at
	product["slug"] = productsItem.slug
	product["display_name"] = productsItem.display_name
	product["is_catalog"] = productsItem.is_catalog
	product["delete_status"] = productsItem.delete_status
	product["absolute_path"] = "http://www.wholdus.com/" + productsItem.category.slug + "-" + str(productsItem.category_id) + "/" +productsItem.slug +"-" + str(productsItem.id)
	product["margin"] = '{0:.1f}'.format((float(productsItem.price_per_unit) - float(productsItem.min_price_per_unit))/float(productsItem.price_per_unit)*100)
	product["url"] = productsItem.category.slug + "-" + str(productsItem.category.id) + "/" + productsItem.slug+ "-" + str(productsItem.id)

	if "seller_details" in parameters and parameters["seller_details"] == 1:
		product["seller"] = serialize_seller(productsItem.seller, parameters)
	else:
		seller = {}
		seller["sellerID"] =productsItem.seller.id
		seller["name"] =productsItem.seller.name
		product["seller"] = seller

	if "category_details" in parameters and parameters["category_details"] == 1:
		product["category"] = serialize_categories(productsItem.category, parameters)
	else:
		category = {}
		category["categoryID"] = productsItem.category.id
		category["name"] = productsItem.category.name
		product["category"] = category
	
	if "product_details_details" in parameters and parameters["product_details_details"] == 1 and hasattr(productsItem, 'productdetails'):
		product["details"] = serialize_product_details(productsItem, parameters)
	else:
		product_details = {}
		product_details["seller_catalog_number"] = productsItem.productdetails.seller_catalog_number
		product_details["fabric_gsm"] = productsItem.productdetails.fabric_gsm
		product_details["colours"] = productsItem.productdetails.colours
		product_details["sizes"] = productsItem.productdetails.sizes
		product["details"] = product_details

	if "product_lot_details" in parameters and parameters["product_lot_details"] == 1:
		product["product_lot"] = serialize_product_lots(productsItem, parameters)

	if "product_image_details" in parameters and parameters["product_image_details"] == 1:
		image = {}

		image_numbers = str(productsItem.image_numbers)
		try:
			image_numbers = ast.literal_eval(image_numbers)
		except Exception as e:
			image_numbers = {}

		image_numbers_arr = []
		for i in range(len(image_numbers)):
			image_numbers_arr.append(image_numbers[i+1])

		if len(image_numbers_arr) > 0:
			imageLink = "http://api.wholdus.com/" + productsItem.image_path + "700x700/" + productsItem.image_name + "-" + str(image_numbers_arr[0]) +".jpg"		
			image["absolute_path"] = imageLink

		image["image_numbers"] = image_numbers_arr
		image["image_count"] = len(image_numbers)
		image["image_path"] = productsItem.image_path
		image["image_name"] = productsItem.image_name

		product["image"] = image

	return product

def serialize_product_details(productsItem, parameters = {}):

	details ={}

	details["detailsID"] = productsItem.productdetails.id
	details["seller_catalog_number"] = productsItem.productdetails.seller_catalog_number
	details["brand"] = productsItem.productdetails.brand
	details["description"] = productsItem.productdetails.description
	details["gender"] = productsItem.productdetails.gender
	details["pattern"] = productsItem.productdetails.pattern
	details["style"] = productsItem.productdetails.style
	details["fabric_gsm"] = productsItem.productdetails.fabric_gsm
	details["sleeve"] = productsItem.productdetails.sleeve
	details["neck_collar_type"] = productsItem.productdetails.neck_collar_type
	details["length"] = productsItem.productdetails.length
	details["work_decoration_type"] = productsItem.productdetails.work_decoration_type
	details["colours"] = productsItem.productdetails.colours
	details["sizes"] = productsItem.productdetails.sizes
	details["special_feature"] = productsItem.productdetails.special_feature
	details["packaging_details"] = productsItem.productdetails.packaging_details
	details["availability"] = productsItem.productdetails.availability
	details["dispatched_in"] = productsItem.productdetails.dispatched_in
	details["lot_description"] = productsItem.productdetails.lot_description
	details["weight_per_unit"] = productsItem.productdetails.weight_per_unit
	details["sample_type"] = productsItem.productdetails.sample_type
	details["sample_description"] = productsItem.productdetails.sample_description
	details["sample_price"] = productsItem.productdetails.sample_price

	details["manufactured_country"] = productsItem.productdetails.manufactured_country
	details["manufactured_city"] = productsItem.productdetails.manufactured_city
	details["warranty"] = productsItem.productdetails.warranty
	details["remarks"] = productsItem.productdetails.remarks

	return details

def multiple_products_parser(productQuerySet, parameters = {}):
	products = []
	for productsItem in productQuerySet:
		product = serialize_product(productsItem, parameters)
		products.append(product)
	return products