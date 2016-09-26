from decimal import Decimal
import settings

from ..models.productLot import ProductLot
from ..models.product import Product, filterProducts
from .category import serialize_categories
from users.serializers.seller import serialize_seller
from users.models.buyer import filterBuyerProductResponse, Buyer
from orders.models.cart import filterCartItem, CartItem
from orders.models.orderItem import OrderItem
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
	product["absolute_path"] = productsItem.get_absolute_url()
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

		image_numbers = productsItem.get_image_numbers_arr()
	
		image["absolute_path"] = productsItem.get_image_url()

		image["image_numbers"] = image_numbers
		image["image_count"] = len(image_numbers)
		image["image_path"] = productsItem.image_path
		image["image_name"] = productsItem.image_name

		product["image"] = image

	if "isBuyer" in parameters and parameters["isBuyer"] == 1:
		
		response = {}
		buyerProductResponsePtr = filterBuyerProductResponse(parameters)
		buyerProductResponsePtr = buyerProductResponsePtr.filter(product_id = productsItem.id)
		if len(buyerProductResponsePtr) == 0:
			response["response_code"] = 0
		else:
			buyerProductResponsePtr = buyerProductResponsePtr[0]
			response["response_code"] = buyerProductResponsePtr.response_code 

		product["response"] = response

		"""
		cartitem = {}
		cartItemPtr =filterCartItem(parameters)
		cartItemPtr = cartItemPtr.filter(product_id = productsItem.id, status=0)
		if len(cartItemPtr) == 0:
			cartitem["lots"] = 0
		else:
			cartItemPtr = cartItemPtr[0]
			cartitem["lots"] = cartItemPtr.lots

		product["cartitem"] = cartitem
		"""

	if ("isBuyerStore" in parameters and parameters["isBuyerStore"] == 1) or ("isBuyer" in parameters and parameters["isBuyer"] == 1):

		buyerstore = {}

		buyerstore["buyer_store_discounted_price"] = None
		buyerstore["buyer_store_discount"] = None

		buyerProductResponsePtr = filterBuyerProductResponse(parameters)
		buyerProductResponsePtr = buyerProductResponsePtr.filter(product_id = productsItem.id)
		flag = 0
		if not len(buyerProductResponsePtr) == 0:
			buyerProductResponsePtr = buyerProductResponsePtr[0]
			if buyerProductResponsePtr.store_discount != None and buyerProductResponsePtr.store_discount != 0:
				discount_factor =  1 - buyerProductResponsePtr.store_discount/100
				buyerstore["buyer_store_discounted_price"] = productsItem.price_per_unit*discount_factor
				buyerstore["buyer_store_discount"] = buyerProductResponsePtr.store_discount
				flag = 1

		if flag == 0:
			buyerPtr = Buyer.objects.filter(id=parameters["buyersArr"][0])
			if len(buyerPtr) > 0:
				buyerPtr = buyerPtr[0]
				if buyerPtr.store_global_discount != None and buyerPtr.store_global_discount != 0:
					discount_factor =  1 - buyerPtr.store_global_discount/100
					buyerstore["buyer_store_discounted_price"] = productsItem.price_per_unit*discount_factor
					buyerstore["buyer_store_discount"] = buyerPtr.store_global_discount

		product["buyerstore"] = buyerstore

		orderitem = {}
		orderItemPtr = OrderItem.objects.filter(product_id = productsItem.id, current_status=11, suborder__order__buyer_id=parameters["buyersArr"][0])
		if len(orderItemPtr) == 0:
			orderitem["pieces"] = 0
		else:
			orderItemPtr = orderItemPtr[0]
			orderitem["pieces"] = orderItemPtr.pieces

		product["orderitem"] = orderitem


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