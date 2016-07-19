from django.db import models
from scripts.utils import validate_mobile_number, validate_email, validate_bool, validate_pincode, validate_integer, validate_number, getStrArrFromString, getArrFromString
from decimal import Decimal

class BuyerInterest(models.Model):

	buyer = models.ForeignKey('users.Buyer')
	category = models.ForeignKey('catalog.Category',blank=True,null=True)

	## On a scale of 1 to 10
	scale = models.PositiveIntegerField(default=5)

	price_filter_applied = models.BooleanField(default=False)
	min_price_per_unit = models.DecimalField(max_digits=10, decimal_places=0, blank=True, default=0)
	max_price_per_unit = models.DecimalField(max_digits=10, decimal_places=0, blank=True, default=0)

	fabric_filter_text = models.TextField(blank=True)

	productid_filter_text =  models.TextField(blank=True) 

	is_active = models.BooleanField(default=True)

	delete_status = models.BooleanField(default=False)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		default_related_name = "buyerinterest"
		verbose_name="Buyer Interest"
		verbose_name_plural = "Buyer Interests"

	def __unicode__(self):
		return "{} - {} - {} - {}".format(self.id,self.buyer.id,self.buyer.name,self.category.name)

class BuyerInterestHistory(models.Model):

	buyer_interest = models.ForeignKey('users.BuyerInterest')

	scale = models.PositiveIntegerField(default=5)

	price_filter_applied = models.BooleanField(default=False)
	min_price_per_unit = models.DecimalField(max_digits=10, decimal_places=0, blank=True, default=0)
	max_price_per_unit = models.DecimalField(max_digits=10, decimal_places=0, blank=True, default=0)

	fabric_filter_text = models.TextField(blank=True)

	productid_filter_text =  models.TextField(blank=True)

	is_active = models.BooleanField(default=True)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		default_related_name = "buyerinteresthistory"
		verbose_name="Buyer Interest History"
		verbose_name_plural = "Buyer Interest History"

	def __unicode__(self):
		return "{} - {}".format(self.id,str(self.buyer_interest))

def validateBuyerInterestData(buyer_interest, old_buyer_interest, is_new):

	flag = 0

	if not "scale" in buyer_interest or not validate_buyer_interest_scale(buyer_interest["scale"]):
		buyer_interest["scale"] = old_buyer_interest.scale
	if not "min_price_per_unit" in buyer_interest or not validate_number(buyer_interest["min_price_per_unit"]) or not float(buyer_interest["min_price_per_unit"]) >= 0:
		buyer_interest["min_price_per_unit"] = old_buyer_interest.min_price_per_unit
	if not "max_price_per_unit" in buyer_interest or not validate_number(buyer_interest["max_price_per_unit"]) or not float(buyer_interest["max_price_per_unit"]) >= 0:
		buyer_interest["max_price_per_unit"] = old_buyer_interest.max_price_per_unit
	if not "fabric_filter_text" in buyer_interest or buyer_interest["fabric_filter_text"]==None:
		buyer_interest["fabric_filter_text"] = old_buyer_interest.fabric_filter_text
	if not "productid_filter_text" in buyer_interest or buyer_interest["productid_filter_text"]==None:
		buyer_interest["productid_filter_text"] = old_buyer_interest.productid_filter_text
	if not "is_active" in buyer_interest or not validate_bool(buyer_interest["is_active"]):
		buyer_interest["is_active"] = old_buyer_interest.is_active


	if float(buyer_interest["max_price_per_unit"]) > float(buyer_interest["min_price_per_unit"]):
		buyer_interest["price_filter_applied"] = True
	else:
		buyer_interest["price_filter_applied"] = False
		buyer_interest["min_price_per_unit"] = 0.0
		buyer_interest["max_price_per_unit"] = 0.0

	if is_new == 1 and flag == 1:
		return False

	return True

def validate_buyer_interest_scale(x):
	if not validate_integer(x) or not (0<=int(x)<=10):
		return False
	return True

def populateBuyerInterest(buyerInterestPtr, buyerInterest):
	buyerInterestPtr.scale = int(buyerInterest["scale"])
	buyerInterestPtr.min_price_per_unit = Decimal(buyerInterest["min_price_per_unit"])
	buyerInterestPtr.max_price_per_unit = Decimal(buyerInterest["max_price_per_unit"])
	buyerInterestPtr.price_filter_applied = int(buyerInterest["price_filter_applied"])
	buyerInterestPtr.fabric_filter_text = buyerInterest["fabric_filter_text"]
	buyerInterestPtr.productid_filter_text = buyerInterest["productid_filter_text"]
	buyerInterestPtr.is_active = int(buyerInterest["is_active"])

def filterBuyerInterest(parameters = {}):

	buyersInterest = BuyerInterest.objects.filter(delete_status=False,buyer__delete_status=False)

	if "buyersArr" in parameters:
		buyersInterest = buyersInterest.filter(buyer_id__in=parameters["buyersArr"])

	if "buyerInterestArr" in parameters:
		buyersInterest = buyersInterest.filter(id__in=parameters["buyerInterestArr"])

	if "is_active" in parameters:
		buyersInterest = buyersInterest.filter(is_active=parameters["is_active"])

	return buyersInterest