from django.db import models
from django.contrib import admin

#from users.models import Seller
from .category import Category
from django.template.defaultfilters import slugify
from decimal import Decimal
from django.utils import timezone
import math

from scripts.utils import validate_integer, validate_number, validate_bool, arrToFilename, link_to_foreign_key

import operator
from django.db.models import Q

import settings
import ast
#Make changes in model, validate, populate and serializer 
#Also make changes in upload script

class Product(models.Model):
	seller = models.ForeignKey('users.Seller')
	category = models.ForeignKey('catalog.Category')

	name = models.CharField(max_length=255, blank=False)

	price_per_unit = models.DecimalField(max_digits=10, decimal_places=2, blank=False)
	unit = models.CharField(max_length=15, blank=False)
	tax = models.DecimalField(max_digits=5, decimal_places=2)
	min_price_per_unit = models.DecimalField(max_digits=7, decimal_places=2, default=0)

	lot_size = models.PositiveIntegerField(default=1)
	price_per_lot = models.DecimalField(max_digits=10, decimal_places=2, blank=False)

	image_path = models.TextField(blank=True)
	image_name = models.TextField(blank=True)
	image_numbers = models.TextField(blank=True)

	verification = models.BooleanField(default=False)
	show_online = models.BooleanField(default=True)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	slug = models.CharField(max_length=100, blank=True)

	display_name = models.TextField(blank=True, default="")

	new_in_product_matrix = models.BooleanField(default=True)

	delete_status = models.BooleanField(default=False)
	is_catalog = models.BooleanField(default=False)

	def get_absolute_url(self):
		return r"{}/{}-{}/{}-{}".format(settings.BASE_URL, self.category.slug,self.category.id,self.slug,self.id)

	def get_image_url(self, resolution="700"):
		resolutionString = "{}x{}".format(resolution,resolution)
		image_numbers_arr = self.get_image_numbers_arr()
		if len(image_numbers_arr) > 0:
			return r"{}/{}{}/{}-{}.jpg".format(settings.API_BASE_URL, self.image_path,resolutionString,self.image_name,image_numbers_arr[0])
		else:
			return settings.BASE_URL

	def get_image_numbers_arr(self):
		image_numbers = str(self.image_numbers)
		try:
			image_numbers_arr = ast.literal_eval(image_numbers)
		except Exception as e:
			print e
			image_numbers_arr = []

		return image_numbers_arr


	class Meta:
		ordering = ["-id"]
		default_related_name = "product"
		verbose_name="Product"
		verbose_name_plural = "Products"

	def __unicode__(self):
		return "{} - {} - {}".format(self.id,self.name,self.seller.name)

	def getCalculatedPricePerPiece(self, lots):
		productLotsQuerySet = self.productlot.all().order_by('lot_size_from')
		if lots < productLotsQuerySet[0].lot_size_from:
			return productLotsQuerySet[0].price_per_unit
		for productLot in productLotsQuerySet:
			if lots <= productLot.lot_size_to:
				return productLot.price_per_unit
		return productLotsQuerySet[len(productLotsQuerySet)-1].price_per_unit

	def getShippingPerPiece(self):
		try:
			return float((self.productdetails.weight_per_unit+50)/1000*35)
		except Exception as e:
			return  (float(350))/1000*35


class ProductDetails(models.Model):

	product = models.OneToOneField(Product)

	seller_catalog_number = models.CharField(max_length=200, blank=True)
	brand = models.CharField(max_length=100, blank=True)

	description = models.TextField(blank=True, default="")
	gender = models.CharField(max_length=20, blank=True)
	pattern = models.CharField(max_length=40, blank=True)
	style = models.CharField(max_length=40, blank=True)
	fabric_gsm = models.CharField(max_length=40, blank=True)
	sleeve = models.CharField(max_length=40, blank=True)
	neck_collar_type = models.CharField(max_length=40, blank=True)
	length = models.CharField(max_length=40, blank=True)
	work_decoration_type = models.CharField(max_length=40, blank=True)
	colours = models.CharField(max_length=100, blank=True)
	sizes = models.CharField(max_length=100, blank=True)
	#fabric = models.CharField(max_length=100, blank=True)
	special_feature = models.TextField(blank=True)
	packaging_details = models.TextField(blank=True)
	availability = models.TextField(blank=True)
	dispatched_in = models.TextField(blank=True)
	lot_description = models.TextField(blank=True)
	weight_per_unit = models.DecimalField(max_digits=10, decimal_places=2, default=0)

	sample_type = models.TextField(blank=True)
	sample_description = models.TextField(blank=True)
	sample_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

	manufactured_country = models.CharField(max_length=50, blank=True, default="India")
	manufactured_city = models.CharField(max_length=50, blank=True)
	warranty = models.CharField(max_length=100, blank=True)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	remarks = models.TextField(blank=True)

	class Meta:
		default_related_name = "productdetails"
		verbose_name="Product Details"
		verbose_name_plural = "Product Details"

	def __unicode__(self):
		return "{} - {}".format(self.product.id,self.product.name)

class ProductDetailsAdmin(admin.ModelAdmin):
	search_fields = ["product__name", "product__category__name", "product__seller__name"]
	list_display = ["id", "link_to_product"]

	list_display_links = ["id","link_to_product"]

	def link_to_product(self, obj):
		return link_to_foreign_key(obj, "product")
	link_to_product.short_description = "Product"
	link_to_product.allow_tags=True

class ProductDetailsInline(admin.StackedInline):
	model = ProductDetails

class ProductAdmin(admin.ModelAdmin):
	search_fields = ["name", "category__name", "seller__name"]
	list_display = ["id", "name", "link_to_seller", "link_to_category", "link_to_productdetails"]

	list_display_links = ["name","link_to_seller", "link_to_category"]

	list_filter = ["category", "seller", "verification", "show_online", "delete_status"]

	def link_to_seller(self, obj):
		return link_to_foreign_key(obj, "seller")
	link_to_seller.short_description = "Seller"
	link_to_seller.allow_tags=True

	def link_to_category(self, obj):
		return link_to_foreign_key(obj, "category")
	link_to_category.short_description = "Category"
	link_to_category.allow_tags=True

	def link_to_productdetails(self, obj):
		return link_to_foreign_key(obj, "productdetails")
	link_to_productdetails.short_description = "Product Details"
	link_to_productdetails.allow_tags=True
	inlines = [ProductDetailsInline,]



def validateProductData(product, oldproduct, is_new):

	flag = 0

	if not "name" in product or product["name"]==None:
		flag = 1
		product["name"] = oldproduct.name
	if not "price_per_unit" in product or not validate_number(product["price_per_unit"]):
		flag = 1
		product["price_per_unit"] = oldproduct.price_per_unit
	if not "unit" in product or product["unit"]==None:
		product["unit"] = oldproduct.unit
	if not "tax" in product or not validate_number(product["tax"]):
		product["tax"] = oldproduct.tax
	if not "min_price_per_unit" in product or not validate_number(product["min_price_per_unit"]):
		product["min_price_per_unit"] = oldproduct.min_price_per_unit
	if not "lot_size" in product or not validate_integer(product["lot_size"]):
		flag = 1
		product["lot_size"] = oldproduct.lot_size
	if not "price_per_lot" in product or not validate_number(product["price_per_lot"]):
		flag = 1
		product["price_per_lot"] = oldproduct.price_per_lot
	if not "verification" in product or not validate_bool(product["verification"]):
		product["verification"] = oldproduct.verification
	if not "show_online" in product or not validate_bool(product["show_online"]):
		product["show_online"] = oldproduct.show_online
	if not "slug" in product or product["slug"]==None:
		product["slug"] = oldproduct.slug
	if not "display_name" in product or product["display_name"]==None:
		product["display_name"] = oldproduct.display_name
	if not "is_catalog" in product or not validate_bool(product["is_catalog"]):
		product["is_catalog"] = oldproduct.is_catalog
	if not "delete_status" in product or not validate_bool(product["delete_status"]):
		product["delete_status"] = oldproduct.delete_status
	
	if not float(product["min_price_per_unit"]) > 0 or not float(product["price_per_lot"]) > 0 or not float(product["price_per_unit"]) > 0:
		return False

	if not float(product["price_per_unit"]) >= float(product["min_price_per_unit"]) or not  float(product["price_per_lot"]) >= float(product["price_per_unit"]) :
		return False

	if is_new == 1 and flag == 1:
		return False

	return True

def validateProductDetailsData(productdetails, oldproductdetails):
	if not "seller_catalog_number" in productdetails or productdetails["seller_catalog_number"]==None:
		productdetails["seller_catalog_number"] = oldproductdetails.seller_catalog_number
	if not "brand" in productdetails or productdetails["brand"]==None:
		productdetails["brand"] = oldproductdetails.brand
	if not "description" in productdetails or productdetails["description"]==None:
		productdetails["description"] = oldproductdetails.description
	if not "gender" in productdetails or productdetails["gender"]==None:
		productdetails["gender"] = oldproductdetails.gender
	if not "pattern" in productdetails or productdetails["pattern"]==None:
		productdetails["pattern"] = oldproductdetails.pattern
	if not "style" in productdetails or productdetails["style"]==None:
		productdetails["style"] = oldproductdetails.style
	if not "sleeve" in productdetails or productdetails["sleeve"]==None:
		productdetails["sleeve"] = oldproductdetails.sleeve
	if not "fabric_gsm" in productdetails or productdetails["fabric_gsm"]==None:
		productdetails["fabric_gsm"] = oldproductdetails.fabric_gsm
	if not "neck_collar_type" in productdetails or productdetails["neck_collar_type"]==None:
		productdetails["neck_collar_type"] = oldproductdetails.neck_collar_type
	if not "length" in productdetails or productdetails["length"]==None:
		productdetails["length"] = oldproductdetails.length
	if not "work_decoration_type" in productdetails or productdetails["work_decoration_type"]==None:
		productdetails["work_decoration_type"] = oldproductdetails.work_decoration_type
	if not "colours" in productdetails or productdetails["colours"]==None:
		productdetails["colours"] = oldproductdetails.colours
	if not "sizes" in productdetails or productdetails["sizes"]==None:
		productdetails["sizes"] = oldproductdetails.sizes
	if not "special_feature" in productdetails or productdetails["special_feature"]==None:
		productdetails["special_feature"] = oldproductdetails.special_feature
	if not "manufactured_country" in productdetails or productdetails["manufactured_country"]==None:
		productdetails["manufactured_country"] = oldproductdetails.manufactured_country
	if not "warranty" in productdetails or productdetails["warranty"]==None:
		productdetails["warranty"] = oldproductdetails.warranty
	if not "remarks" in productdetails or productdetails["remarks"]==None:
		productdetails["remarks"] = oldproductdetails.remarks
	if not "packaging_details" in productdetails or productdetails["packaging_details"]==None:
		productdetails["packaging_details"] = oldproductdetails.packaging_details
	if not "availability" in productdetails or productdetails["availability"]==None:
		productdetails["availability"] = oldproductdetails.availability
	if not "dispatched_in" in productdetails or productdetails["dispatched_in"]==None:
		productdetails["dispatched_in"] = oldproductdetails.dispatched_in
	if not "manufactured_city" in productdetails or productdetails["manufactured_city"]==None:
		productdetails["manufactured_city"] = oldproductdetails.manufactured_city
	if not "lot_description" in productdetails or productdetails["lot_description"]==None:
		productdetails["lot_description"] = oldproductdetails.lot_description
	if not "weight_per_unit" in productdetails or not validate_number(productdetails["weight_per_unit"]):
		productdetails["weight_per_unit"] = oldproductdetails.weight_per_unit
	if not "sample_type" in productdetails or productdetails["sample_type"]==None:
		productdetails["sample_type"] = oldproductdetails.sample_type
	if not "sample_description" in productdetails or productdetails["sample_description"]==None:
		productdetails["sample_description"] = oldproductdetails.sample_description
	if not "sample_price" in productdetails or not validate_number(productdetails["sample_price"]):
		productdetails["sample_price"] = oldproductdetails.sample_price

def populateProductData(productPtr, product):
	productPtr.name = product["name"]
	productPtr.price_per_unit = Decimal(product["price_per_unit"])
	productPtr.unit = product["unit"]
	productPtr.tax = Decimal(product["tax"])
	productPtr.min_price_per_unit = Decimal(product["min_price_per_unit"])
	productPtr.lot_size = int(product["lot_size"])
	productPtr.price_per_lot = Decimal(product["price_per_lot"])
	productPtr.verification = int(product["verification"])
	productPtr.show_online = int(product["show_online"])
	productPtr.slug = slugify(product["name"])
	productPtr.display_name = product["display_name"]
	productPtr.is_catalog = int(product["is_catalog"])
	productPtr.delete_status = int(product["delete_status"])
	productPtr.new_in_product_matrix = 1
	if "image_count" in product and product["image_count"]!=None:
		nowtime = timezone.now()
		productPtr.image_path = "media/productimages/" + str(productPtr.seller.id) + "/" + nowtime.strftime('%Y%m%d%H%M%S') + "/"
		productPtr.image_name = slugify(productPtr.display_name)
		image_numbers = range(1,int(product["image_count"])+1)
		productPtr.image_numbers = str(image_numbers)

def populateProductDetailsData(productDetailsPtr, productdetails):
	productDetailsPtr.seller_catalog_number = productdetails["seller_catalog_number"]
	productDetailsPtr.brand = productdetails["brand"]
	productDetailsPtr.description = productdetails["description"]
	productDetailsPtr.gender = productdetails["gender"]
	productDetailsPtr.pattern = productdetails["pattern"]
	productDetailsPtr.style = productdetails["style"]
	productDetailsPtr.fabric_gsm = productdetails["fabric_gsm"]
	productDetailsPtr.sleeve = productdetails["sleeve"]
	productDetailsPtr.neck_collar_type = productdetails["neck_collar_type"]
	productDetailsPtr.length = productdetails["length"]
	productDetailsPtr.work_decoration_type = productdetails["work_decoration_type"]
	productDetailsPtr.colours = productdetails["colours"]
	productDetailsPtr.sizes = productdetails["sizes"]
	productDetailsPtr.special_feature = productdetails["special_feature"]
	productDetailsPtr.manufactured_country = productdetails["manufactured_country"]
	productDetailsPtr.warranty = productdetails["warranty"]
	productDetailsPtr.remarks = productdetails["remarks"]
	productDetailsPtr.packaging_details = productdetails["packaging_details"]
	productDetailsPtr.availability = productdetails["availability"]
	productDetailsPtr.dispatched_in = productdetails["dispatched_in"]
	productDetailsPtr.manufactured_city = productdetails["manufactured_city"]
	productDetailsPtr.lot_description = productdetails["lot_description"]
	productDetailsPtr.weight_per_unit = Decimal(productdetails["weight_per_unit"])
	productDetailsPtr.sample_type = productdetails["sample_type"]
	productDetailsPtr.sample_description = productdetails["sample_description"]
	productDetailsPtr.sample_price = Decimal(productdetails["sample_price"])

def filterProducts(parameters = {}):
	products = Product.objects.filter(delete_status=False, seller__delete_status=False, category__delete_status=False).select_related('seller', 'productdetails', 'category')

	if "categoriesArr" in parameters:
		products = products.filter(category_id__in=parameters["categoriesArr"])

	if "productsArr" in parameters:
		products = products.filter(id__in=parameters["productsArr"])

	if "sellersArr" in parameters:
		products = products.filter(seller_id__in=parameters["sellersArr"])

	if "fabricArr" in parameters:
		query = reduce(operator.or_, (Q(productdetails__fabric_gsm__icontains = item) for item in parameters["fabricArr"]))
		products = products.filter(query)

	if "colourArr" in parameters:
		query = reduce(operator.or_, (Q(productdetails__colours__icontains = item) for item in parameters["colourArr"]))
		products = products.filter(query)

	if "price_filter_applied" in parameters:
		products = products.filter(min_price_per_unit__range=(parameters["min_price_per_unit"],parameters["max_price_per_unit"]))

	if "product_verification" in parameters:
		products = products.filter(verification=parameters["product_verification"])
	
	if "product_show_online" in parameters:
		products = products.filter(show_online=parameters["product_show_online"])

	if "product_order_by" in parameters:
		print "here " + parameters["product_order_by"]
		if parameters["product_order_by"] == "latest":
			products = products.order_by('-id')
		elif parameters["product_order_by"] == "price_ascending":
			products = products.order_by('min_price_per_unit', '-id')
		elif parameters["product_order_by"] == "price_descending":
			products = products.order_by('-min_price_per_unit', '-id')
		else :
			products = products.order_by('-id')
	else:
		products = products.order_by('-id')

	"""
	if "seller_show_online" in parameters:
		products = products.filter(seller__show_online=parameters["seller_show_online"])

	if "category_show_online" in parameters:
		products = products.filter(category__show_online=parameters["category_show_online"])
	"""

	if "product_new_in_product_matrix" in parameters:
		products = products.filter(new_in_product_matrix=parameters["product_new_in_product_matrix"])

	return products

def getProductFileName(filename, extension, productParameters):

	if "categoriesArr" in productParameters:
		filename += "categories-" + arrToFilename(productParameters["categoriesArr"]) + "_"

	if "sellerArr" in productParameters:
		filename += "seller-" + arrToFilename(productParameters["sellerArr"]) + "_"

	if "fabricArr" in productParameters:
		filename += "fabric-" + arrToFilename(productParameters["fabricArr"]) + "_"

	if "colourArr" in productParameters:
		filename += "colour-" + arrToFilename(productParameters["colourArr"]) + "_"

	if "price_filter_applied" in productParameters:
		filename += "pricerange-" + str(productParameters["min_price_per_unit"]) +"to" + str(productParameters["max_price_per_unit"]) + "_"

	filename = filename[0:len(filename)-1]

	filename += extension

	return filename