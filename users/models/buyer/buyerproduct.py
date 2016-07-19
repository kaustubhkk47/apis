from django.db import models
from scripts.utils import validate_mobile_number, validate_email, validate_bool, validate_pincode, validate_integer, validate_number, getStrArrFromString, getArrFromString
from decimal import Decimal
import operator
from django.db.models import Q

from catalog.models.product import Product, filterProducts
import datetime

from pandas import DataFrame

class BuyerProducts(models.Model):

	buyer = models.ForeignKey('users.Buyer')
	product = models.ForeignKey('catalog.Product')
	buyer_interest = models.ForeignKey('users.BuyerInterest', null = True, blank = True)

	is_active = models.BooleanField(default=True)

	responded = models.IntegerField(default=0)

	shortlisted_time = models.DateTimeField(null=True, blank=True)
	disliked_time = models.DateTimeField(null=True, blank=True)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	delete_status = models.BooleanField(default=False)

	shared_on_whatsapp = models.BooleanField(default=False)

	class Meta:
		ordering = ["-product__id"]
		default_related_name = "buyerproduct"
		verbose_name="Buyer Product"
		verbose_name_plural = "Buyer Products"

	def __unicode__(self):
		return "{} - {}".format(str(self.buyer),str(self.product))

class BuyerSharedProductID(models.Model):

	buyer = models.ForeignKey('users.Buyer')
	productid_filter_text =  models.TextField(blank=True)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	delete_status = models.BooleanField(default=False)

	class Meta:
		default_related_name = "buyersharedproductid"
		verbose_name="Buyer Shared Product ID"
		verbose_name_plural = "Buyer Shared Product IDs"

	def __unicode__(self):
		return "{}".format(self.id)

class BuyerProductResponse(models.Model):
	buyer = models.ForeignKey('users.Buyer')
	product = models.ForeignKey('catalog.Product')
	buyer_product = models.ForeignKey('users.BuyerProducts', null = True, blank = True)

	response_code = models.IntegerField(default=0)

	has_swiped = models.BooleanField(default=False)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		default_related_name = "buyerproductresponse"
		verbose_name="Buyer Product Response"
		verbose_name_plural = "Buyer Product Responses"

	def __unicode__(self):
		return "{}".format(self.id)

BuyerProductResponseCodes = {
	1:{"display_value":"Shortlisted"},
	2:{"display_value":"Disliked"}
}

class BuyerProductLanding(models.Model):
	buyer = models.ForeignKey('users.Buyer')
	product = models.ForeignKey('catalog.Product')
	buyer_product = models.ForeignKey('users.BuyerProducts', null = True, blank = True)

	source = models.IntegerField(default=1)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		default_related_name = "buyerproductlanding"
		verbose_name="Buyer Product Landing"
		verbose_name_plural = "Buyer Product Landings"

	def __unicode__(self):
		return "{}".format(self.id)

BuyerProductLandingSource = {
	1:{"display_value":"Whatsapp"}
}

class BuyerProductResponseHistory(models.Model):

	buyer = models.ForeignKey('users.Buyer')
	product = models.ForeignKey('catalog.Product')
	buyer_product = models.ForeignKey('users.BuyerProducts', null = True, blank = True)

	response_code = models.IntegerField(default=0)
	has_swiped = models.BooleanField(default=False)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		default_related_name = "buyerproductresponsehistory"
		verbose_name="Buyer Product Response History"
		verbose_name_plural = "Buyer Product Response History"

	def __unicode__(self):
		return "{}".format(self.id)

BuyerProductResponseHistoryCodes = {
	1:{"display_value":"Like"},
	2:{"display_value":"Dislike"},
	3:{"display_value":"Dislike to Like"},
	4:{"display_value":"Like to Dislike"}
}

def validateBuyerProductData(buyer_product, old_buyer_product, is_new, buyer_product_populator):

	if "has_swiped" in buyer_product and validate_bool(buyer_product["has_swiped"]):
		buyer_product_populator["has_swiped"] = buyer_product["has_swiped"]

	if "is_active" in buyer_product and validate_bool(buyer_product["is_active"]):
		if int(buyer_product["is_active"]) != int(old_buyer_product.is_active) and old_buyer_product.responded == 0:
			buyer_product_populator["is_active"] = int(buyer_product["is_active"])
			return True

	if old_buyer_product.is_active == 0:
		return False

	if "responded" in buyer_product and validate_integer(buyer_product["responded"]):
		if int(buyer_product["responded"]) == 1:
			buyer_product_populator["shortlisted_time"] = datetime.datetime.now()
			buyer_product_populator["responded"] = 1
			if old_buyer_product.responded == 2:
				buyer_product_populator["response_code"] = 3
			elif old_buyer_product.responded == 0:
				buyer_product_populator["response_code"] = 1
			else:
				return False
			return True
		elif int(buyer_product["responded"]) == 2:
			buyer_product_populator["disliked_time"] = datetime.datetime.now()
			buyer_product_populator["responded"] = 2
			if  old_buyer_product.responded == 0:
				buyer_product_populator["response_code"] = 2
			elif old_buyer_product.responded == 1:
				buyer_product_populator["response_code"] = 4
			else:
				return False
			return True

	return False

def populateBuyerProduct(buyerProductPtr, buyerproduct):

	if "is_active" in buyerproduct:
		buyerProductPtr.is_active = int(buyerproduct["is_active"])
	if "responded" in buyerproduct:
		buyerProductPtr.responded = int(buyerproduct["responded"])    
	if "shortlisted_time" in buyerproduct:
		buyerProductPtr.shortlisted_time = buyerproduct["shortlisted_time"]    
	if "disliked_time" in buyerproduct:
		buyerProductPtr.disliked_time = buyerproduct["disliked_time"]

def populateBuyerProductResponseHistory(buyerProductResponsePtr,buyerProductResponse):
	buyerProductResponsePtr.response_code = int(buyerProductResponse["response_code"])
	if "has_swiped" in buyerProductResponse:
		buyerProductResponsePtr.has_swiped = int(buyerProductResponse["has_swiped"])

def populateBuyerProductResponse(buyerProductResponsePtr,buyerProductResponse):
	buyerProductResponsePtr.response_code = int(buyerProductResponse["response_code"])
	if "has_swiped" in buyerProductResponse:
		buyerProductResponsePtr.has_swiped = int(buyerProductResponse["has_swiped"])

def filterBuyerSharedProductID(parameters = {}):

	buyerSharedProductID = BuyerSharedProductID.objects.filter(delete_status=False)

	if "buyersArr" in parameters:
		buyerSharedProductID = buyerSharedProductID.filter(buyer_id__in=parameters["buyersArr"])

	if "buyersharedproductID" in parameters:
		buyerSharedProductID = buyerSharedProductID.filter(id=parameters["buyersharedproductID"])

	return buyerSharedProductID

def filterBuyerProducts(parameters = {}):

	buyerProducts = BuyerProducts.objects.filter(buyer__delete_status=False,product__delete_status=False, product__show_online=True, product__verification=True, product__seller__delete_status=False, product__seller__show_online=True, product__category__delete_status=False)\

	if "buyerProductsArr" in parameters:
		buyerProducts = buyerProducts.filter(id__in=parameters["buyerProductsArr"])

	if "buyer_product_landing" in parameters and parameters["buyer_product_landing"] == 1:
		return buyerProducts

	if "buyer_interest_active" in parameters:
		query = reduce(operator.or_, (Q(buyer_interest__is_active = item) for item in [None,parameters["buyer_interest_active"]]))
		buyerProducts = buyerProducts.filter(query)

	if "buyer_product_delete_status" in parameters:
		buyerProducts = buyerProducts.filter(delete_status=parameters["buyer_product_delete_status"])

	if "buyer_product_shared_on_whatsapp" in parameters:
		buyerProducts = buyerProducts.filter(shared_on_whatsapp=parameters["buyer_product_shared_on_whatsapp"])

	if "buyer_product_is_active" in parameters:
		buyerProducts = buyerProducts.filter(is_active=parameters["buyer_product_is_active"])

	if "product_new_in_product_matrix" in parameters:
		buyerProducts = buyerProducts.filter(product__new_in_product_matrix=parameters["product_new_in_product_matrix"])
	
	if "responded" in parameters:
		buyerProducts = buyerProducts.filter(responded= parameters["responded"])

	if "buyersArr" in parameters:
		buyerProducts = buyerProducts.filter(buyer_id__in=parameters["buyersArr"])

	if "buyerInterestArr" in parameters:
		buyerProducts = buyerProducts.filter(buyer_interest_id__in=parameters["buyerInterestArr"])

	if "buyersharedproductID" in parameters:
		buyerSharedProductIDPtr = BuyerSharedProductID.objects.filter(id=int(parameters["buyersharedproductID"]))
		if len(buyerSharedProductIDPtr) > 0:
			productIds =  getArrFromString(buyerSharedProductIDPtr[0].productid_filter_text)
		else:
			productIds = []
		buyerProducts = buyerProducts.filter(product_id__in=productIds)

	if "productsArr" in parameters:
		buyerProducts = buyerProducts.filter(product_id__in=parameters["productsArr"])

	return buyerProducts

def filterBuyerInterestProducts(BuyerInterestPtr, parameters = {}):

	parameters["product_verification"] = True
	parameters["product_show_online"] = True
	parameters["seller_show_online"] = True

	if BuyerInterestPtr.price_filter_applied == True:
		parameters["price_filter_applied"] = True
		parameters["min_price_per_unit"] = BuyerInterestPtr.min_price_per_unit
		parameters["max_price_per_unit"] = BuyerInterestPtr.max_price_per_unit

	if BuyerInterestPtr.category_id != None:
		parameters["categoriesArr"] = [BuyerInterestPtr.category_id]

	if BuyerInterestPtr.fabric_filter_text != None and BuyerInterestPtr.fabric_filter_text != "":
		fabricArr = getStrArrFromString(BuyerInterestPtr.fabric_filter_text)
		parameters["fabricArr"] = fabricArr

	if BuyerInterestPtr.productid_filter_text!= None and BuyerInterestPtr.productid_filter_text != "":
		productIDs = getArrFromString(BuyerInterestPtr.productid_filter_text)
		parameters["productsArr"] = productIDs

	productPtr = filterProducts(parameters)

	return productPtr

def getIntersectingProducts(leftPtr, rightPtr):
	leftList = []
	innerList = []
	rightList = []

	if len(leftPtr) > 0 and len(rightPtr) > 0:

		productsToAdd = DataFrame(list(leftPtr.values('id')))

		productAgainstBuyer = DataFrame(list(rightPtr.values('product_id','id')))

		innerFrame = productAgainstBuyer[(productAgainstBuyer.product_id.isin(productsToAdd.id))]

		#innerFrame = merge(productsToAdd, productAgainstBuyer, how="inner", left_on="id", right_on="product_id", sort=False)

		innerList = innerFrame["id"].tolist()

		leftOnlyFrame = productsToAdd[(~productsToAdd.id.isin(innerFrame.product_id))]

		rightOnlyFrame = productAgainstBuyer[(~productAgainstBuyer.id.isin(innerFrame.id))]

		leftList = leftOnlyFrame["id"].tolist()
		rightList = rightOnlyFrame["id"].tolist()
	elif len(rightPtr) > 0 and len(leftPtr) == 0:
		rightList = [int(e) for e in list(rightPtr.values_list('id',flat=True))]
	elif len(rightPtr) == 0 and len(leftPtr) > 0:
		leftList = [int(e) for e in list(leftPtr.values_list('id',flat=True))]

	return [leftList, innerList, rightList]