from scripts.utils import customResponse, closeDBConnection, convert_keys_to_string, validate_integer, generateProductFile, generateProductCatalog, generate_pdf,responsePaginationParameters

from ..models.category import Category
from ..models.product import Product, validateProductData, ProductDetails, validateProductDetailsData, populateProductData, populateProductDetailsData, filterProducts, getProductFileName
from ..models.productLot import ProductLot, validateProductLotData, parseMinPricePerUnit, populateProductLotData
from ..models.productData import ColourType, FabricType, filterProductFabricType, filterProductColourType

from ..serializers.product import multiple_products_parser, serialize_product
from ..serializers.productData import parseProductColourType, parseProductFabricType
from users.models.seller import Seller, SellerCategory
import json
from django.template.defaultfilters import slugify
from decimal import Decimal
from django.core.paginator import Paginator

import logging
log = logging.getLogger("django")

def get_product_details(request, parameters = {}):
	try:

		if "isBuyer" in parameters and parameters["isBuyer"] == 1:
			parameters["product_verification"] = True
		elif "isBuyerStore" in parameters and parameters["isBuyerStore"] ==1:
			parameters["product_verification"] = True
		elif "isSeller" in parameters and parameters["isSeller"] == 1:
			pass
		elif "isInternalUser" in parameters and parameters["isInternalUser"] == 1:
			pass
		else:
			# Might have to change in case consumer website is made
			parameters["product_verification"] = True
			#parameters["product_show_online"] = True
		
		products = filterProducts(parameters)

		

		
		paginator = Paginator(products, parameters["itemsPerPage"])

		try:
			pageProducts = paginator.page(parameters["pageNumber"])
		except Exception as e:
			pageProducts = []

		body = multiple_products_parser(pageProducts, parameters)
		response["products"] = body
		response["total_products"] = paginator.count

		responsePaginationParameters(response, paginator, parameters)
			
		statusCode = 200
	except Exception as e:
		log.critical(e)
		statusCode = 500
		response = {}

	closeDBConnection()
	return customResponse(statusCode, response,error_code=0)

def get_deleted_offline_products(request, parameters = {}):
	try:
		response = {}
		if not "product_updated_at" in parameters:
			parameters["product_updated_at"] = "2016-01-01T00:00:00.000Z"

		response["offline_products"] = ",".join(map(str,Product.objects.filter(updated_at__gte=parameters["product_updated_at"],show_online=0).values_list('id',flat=True)))
		response["deleted_products"] = ",".join(map(str,Product.objects.filter(updated_at__gte=parameters["product_updated_at"],delete_status=1).values_list('id',flat=True)))

		statusCode = 200

	except Exception as e:
		log.critical(e)
		statusCode = 500
		response = {}

	closeDBConnection()
	return customResponse(statusCode, response,error_code=0)

def get_product_colour_details(request, parameters = {}):
	try:
		productColours = filterProductColourType(parameters)

		statusCode = 200
		body = {"product_colour_types": parseProductColourType(productColours)}

	except Exception as e:
		log.critical(e)
		statusCode = 500
		body = {}
		
	closeDBConnection()
	return customResponse(statusCode, body,error_code=0)

def get_product_fabric_details(request, parameters = {}):
	try:
		productFabrics = filterProductFabricType(parameters)

		statusCode = 200
		body = {"product_fabric_types": parseProductFabricType(productFabrics)}

	except Exception as e:
		log.critical(e)
		statusCode = 500
		body = {}
		
	closeDBConnection()
	return customResponse(statusCode, body, error_code=0)

def get_product_file(request, productParameters):
	
	try:
		parameters["product_show_online"] = True
		parameters["product_verification"] = True
		products = filterProducts(productParameters)

		products = products.values_list('id',flat=True)

		#filename = getProductFileName("productfile_", ".txt",productParameters)

		filename = "productfile.txt"

		return generateProductFile(products, filename)

	except Exception as e:
		log.critical(e)
		statusCode = 500
		body = {}

		closeDBConnection()
		return customResponse(statusCode, body,  error_code=0)

def get_product_catalog(request, productParameters):
	
	try:
		parameters["product_show_online"] = True
		parameters["product_verification"] = True
		products = filterProducts(productParameters)

		products = {"products":multiple_products_parser(products, productParameters)}

		filename = getProductFileName("productcatalog_", ".pdf",productParameters)

		return generateProductCatalog(products, filename)

	except Exception as e:
		log.critical(e)
		statusCode = 500
		body = {}

		closeDBConnection()
		return customResponse(statusCode, body, error_code=0)

def post_new_product(request, parameters = {}):
	try:
		requestbody = request.body.decode("utf-8")
		product = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse(400, error_code=4)

	if not len(product) or not validateProductData(product, Product(), 1):
		return customResponse(400, error_code=5, error_details= "Invalid data for product sent")

	if not "sellerID" in product or not validate_integer(product["sellerID"]):
		return customResponse(400, error_code=5, error_details="Seller id for product not sent")

	sellerPtr = Seller.objects.filter(id=int(product["sellerID"]), delete_status=False)
	if not sellerPtr.exists():
		return customResponse(400, error_code=6, error_details = "Invalid id for seller sent")

	if not "categoryID" in product or not validate_integer(product["categoryID"]):
		return customResponse(400, error_code=5, error_details= "Category id for product not sent")

	categoryPtr = Category.objects.filter(id=int(product["categoryID"]))
	if not categoryPtr.exists():
		return customResponse(400, error_code=6, error_details = "Invalid id for category sent")

	sellerCategoryPtr = SellerCategory.objects.filter(category_id=int(product["categoryID"]), seller_id=int(product["sellerID"]))

	if not sellerCategoryPtr.exists():
		newSellerCategory = SellerCategory(seller_id=int(product["sellerID"]), category_id=int(product["categoryID"]))
		try:
			newSellerCategory.save()
		except Exception as e:
			pass

	if not "product_lot" in product or not product["product_lot"] or not validateProductLotData(product["product_lot"]):
		return customResponse(400, error_code=5, error_details="Product lots for product not properly sent")

	if not "details" in product or not product["details"]:
		product["details"] = {}

	validateProductDetailsData(product["details"], ProductDetails())

	product["slug"] = slugify(product["name"])
	product["min_price_per_unit"] = parseMinPricePerUnit(product["product_lot"])
	product["display_name"] = product["details"]["brand"] + " " +product["name"] + " " + product["details"]["seller_catalog_number"]

	try:

		newProduct = Product(category_id=int(product["categoryID"]),seller_id=int(product["sellerID"]))
		populateProductData(newProduct, product)
		newProduct.save()

		productLots = product["product_lot"]
		for productLot in productLots:
			newProductLot = ProductLot(product=newProduct)
			populateProductLotData(newProductLot, productLot)
			newProductLot.save()

		productdetails = product["details"]
		newProductDetails = ProductDetails(product=newProduct)
		populateProductDetailsData(newProductDetails, productdetails)

		newProductDetails.save()

	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse(500, error_code = 1)
	else:
		closeDBConnection()
		return customResponse(200, {"product": serialize_product(newProduct, parameters)})

def update_product(request, parameters = {}):
	try:
		requestbody = request.body.decode("utf-8")
		product = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse(400, error_code=4)

	if not len(product) or not "productID" in product or not validate_integer(product["productID"]):
		return customResponse(400, error_code=5, error_details= "Id for product not sent")

	productPtr = Product.objects.filter(id=int(product["productID"])).select_related('productdetails')

	if len(productPtr) == 0:
		return customResponse(400, error_code=6, error_details ="Invalid id for product sent")

	productPtr = productPtr[0]

	detailsPresent = 1
	detailsSent = 0
	productlotSent = 0

	if not validateProductData(product, productPtr, 0):
		return customResponse(400, error_code=5, error_details= "Invalid data for product sent")

	product["slug"] = slugify(product["name"])

	try:
		populateProductData(productPtr, product)
		
		if "details" in product and product["details"]:
			detailsSent = 1
			productdetails = product["details"]
			productPtr.display_name = product["details"]["brand"] + " " +product["name"] + " " + product["details"]["seller_catalog_number"]
			if hasattr(productPtr, "productdetails"):
				validateProductDetailsData(productdetails, productPtr.productdetails)
				populateProductDetailsData(productPtr.productdetails, productdetails)
			else:
				detailsPresent = 0
				validateProductDetailsData(productdetails, ProductDetails())
				newProductDetails = ProductDetails(product=productPtr)
				populateProductDetailsData(newProductDetails, productdetails)

		if "product_lot" in product and product["product_lot"]:
			productlotSent = 1
			if not validateProductLotData(product["product_lot"]):
				return customResponse(400, error_code=5, error_details="Product lots for product not properly sent")

			productLots = product["product_lot"]

			ProductLot.objects.filter(product_id=int(product["productID"])).delete()
			productPtr.min_price_per_unit = Decimal(parseMinPricePerUnit(productLots))    

			for productLot in productLots:
				newProductLot = ProductLot(product=productPtr)
				populateProductLotData(newProductLot, productLot)
				newProductLot.save()
				
		productPtr.save()
		if detailsSent == 1 and detailsPresent == 1:
			productPtr.productdetails.save()
		if detailsPresent == 0:
			newProductDetails.save()
		
	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse(500, error_code = 3)
	else:
		closeDBConnection()
		return customResponse(200, {"product": serialize_product(productPtr , parameters)})

def delete_product(request):
	try:
		requestbody = request.body.decode("utf-8")
		product = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse(400, error_code=4)

	if not len(product) or not "productID" in product or not validate_integer(product["productID"]):
		return customResponse(400, error_code=5,  error_details= "Id for product not sent")

	productPtr = Product.objects.filter(id=int(product["productID"]), delete_status=False)

	if len(productPtr) == 0:
		return customResponse(400, error_code=6, error_details = "Invalid id for product sent")

	productPtr = productPtr[0]

	try:
		productPtr.delete_status = True
		productPtr.save()
	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse(500, error_code = 3)
	else:
		closeDBConnection()
		return customResponse(200, {"product": "product deleted"})