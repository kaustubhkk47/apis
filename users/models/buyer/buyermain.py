from django.db import models
from django.contrib import admin
from scripts.utils import validate_mobile_number, validate_email, validate_bool, validate_pincode, validate_integer, validate_number, getStrArrFromString, getArrFromString, link_to_foreign_key, validate_percent, time_in_ist
from decimal import Decimal
import jwt as JsonWebToken
import settings
from address.models.pincode import Pincode
from .buyerauthentication import BuyerFireBaseToken
from django.template.defaultfilters import slugify

class Buyer(models.Model):
	name = models.CharField(max_length=200, blank=True)
	company_name = models.CharField(max_length=200, blank=True)
	mobile_number = models.CharField(max_length=11, blank=False, db_index=True)
	whatsapp_number = models.CharField(max_length=11, blank=True, null = True)
	email = models.EmailField(max_length=255, blank=True, null = True)
	password = models.CharField(max_length=255, blank=True, null = True, default = None)
	alternate_phone_number = models.CharField(max_length=11, blank=True)
	mobile_verification = models.BooleanField(default=False)
	email_verification = models.BooleanField(default=False)
	gender = models.CharField(max_length=10, blank=True)

	store_slug = models.TextField(blank=True)
	store_url = models.TextField(blank=True)
	store_active = models.BooleanField(default=False)
	store_global_margin = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null = True)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	blocked = models.BooleanField(default=False)
	delete_status = models.BooleanField(default=False)
	whatsapp_sharing_active = models.BooleanField(default=True)
	whatsapp_contact_name = models.CharField(max_length=200, blank=True)

	test_buyer = models.BooleanField(default=False)

	class Meta:
		default_related_name = "buyer"
		verbose_name="Buyer"
		verbose_name_plural = "Buyers"
		ordering = ["-id"]

	def __unicode__(self):
		return "{} - {} - {}".format(self.id,self.name,self.mobile_number)

	def latest_buyer_address_history(self, addressID = None):
		try:	
			if addressID == None:
				return BuyerAddressHistory.objects.filter(buyer=self, priority = 0).latest('created_at')
			else:
				return BuyerAddressHistory.objects.filter(buyer=self, buyeraddress_id = addressID).latest('created_at')
		except Exception, e:
			return None

	@staticmethod
	def validateBuyerStoreUrlData(data):
		if not "store_url" in data or data["store_url"] == None or len(data["store_url"]) < 6:
			return False
		if not "store_active" in data or not validate_bool(data["store_active"]):
			return False
		return True

	def get_firebase_tokens(self):
		return BuyerFireBaseToken.objects.filter(buyer_id = self.id, delete_status=False)

class BuyerAddress(models.Model):
	buyer = models.ForeignKey('users.Buyer')
	pincode = models.ForeignKey('address.Pincode', blank=True,null=True)

	address_line = models.CharField(max_length=255, blank=True, null=False)
	landmark = models.CharField(max_length=50, blank=True)
	city_name = models.CharField(max_length=50, blank=True)
	state_name = models.CharField(max_length=50, blank=True)
	country_name = models.CharField(max_length=50, blank=True, default="India")
	contact_number = models.CharField(max_length=11, blank=True)
	pincode_number = models.CharField(max_length=6, blank=True)
	priority = models.IntegerField(default=1)
	alias = models.CharField(max_length=255, blank=True, null=False)

	client_id = models.CharField(max_length=255, blank=True, null=False)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["priority"]
		default_related_name = "buyeraddress"
		verbose_name="Buyer Address"
		verbose_name_plural = "Buyer Addresses"

	def __unicode__(self):
		return  str(self.id) + " - " + str(self.buyer)

class BuyerAddressAdmin(admin.ModelAdmin):
	list_display = ["id", "link_to_buyer", "link_to_pincode","pincode_number", "address_line", "city_name", "state_name"]
	search_fields = ["buyer__id", "buyer__name", "buyer__company_name", "buyer__mobile_number"]
	list_display_links = ["id", "link_to_buyer", "link_to_pincode"]

	def link_to_buyer(self, obj):
		return link_to_foreign_key(obj, "buyer")
	link_to_buyer.short_description = "Buyer"
	link_to_buyer.allow_tags=True

	def link_to_pincode(self, obj):
		return link_to_foreign_key(obj, "pincode")
	link_to_pincode.short_description = "Pincode"
	link_to_pincode.allow_tags=True

class BuyerAddressHistory(models.Model):
	buyer = models.ForeignKey('users.Buyer')
	buyeraddress = models.ForeignKey('users.BuyerAddress', blank=True,null=True)
	pincode = models.ForeignKey('address.Pincode', blank=True,null=True)

	address_line = models.CharField(max_length=255, blank=True, null=False)
	landmark = models.CharField(max_length=50, blank=True)
	city_name = models.CharField(max_length=50, blank=True)
	state_name = models.CharField(max_length=50, blank=True)
	country_name = models.CharField(max_length=50, blank=True, default="India")
	contact_number = models.CharField(max_length=11, blank=True)
	pincode_number = models.CharField(max_length=6, blank=True)
	priority = models.IntegerField(default=1)
	alias = models.CharField(max_length=255, blank=True, null=False)

	client_id = models.CharField(max_length=255, blank=True, null=False)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name="Buyer Address History"
		verbose_name_plural = "Buyer Address History"

	def __unicode__(self):
		return str(self.buyer)

	def populateFromBuyerAddress(self, buyerAddressPtr):
		self.buyer_id = buyerAddressPtr.buyer_id
		self.buyeraddress = buyerAddressPtr
		self.pincode = buyerAddressPtr.pincode
		self.address_line = buyerAddressPtr.address_line
		self.landmark = buyerAddressPtr.landmark
		self.city_name = buyerAddressPtr.city_name
		self.state_name = buyerAddressPtr.state_name
		self.country_name = buyerAddressPtr.country_name
		self.contact_number = buyerAddressPtr.contact_number
		self.pincode_number = buyerAddressPtr.pincode_number
		self.priority = buyerAddressPtr.priority
		self.alias = buyerAddressPtr.alias
		self.client_id = buyerAddressPtr.client_id

class BuyerDetails(models.Model):
	buyer = models.OneToOneField('users.Buyer')
	buyer_type = models.ForeignKey('users.BusinessType',blank=True, null=True, on_delete=models.PROTECT)

	vat_tin = models.CharField(max_length=20, blank=True)
	cst = models.CharField(max_length=20, blank=True)

	customer_type = models.IntegerField(blank=True, default=0)

	# in number of pieces per month
	buying_capacity = models.IntegerField(blank=True, default=0)

	# in days
	purchase_duration = models.IntegerField(blank=True, default=0)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		default_related_name = "buyerdetails"
		verbose_name="Buyer Details"
		verbose_name_plural = "Buyer Details"

	def __unicode__(self):
		return str(self.buyer_type)

class BuyerDetailsInline(admin.StackedInline):
	model = BuyerDetails

class BuyerAdmin(admin.ModelAdmin):
	list_display = ["id", "name", "company_name", "mobile_number", "email", "buyerdetails", "created_at_ist"]
	list_filter = ["mobile_verification", "email_verification", "whatsapp_sharing_active", "delete_status", "test_buyer"]
	search_fields = ["id", "name", "company_name", "mobile_number", "email"]
	list_display_links = ["name"]
	inlines = [BuyerDetailsInline,]

	def created_at_ist(self, obj):
		return time_in_ist(obj.created_at)


def validateBuyerData(buyer, oldbuyer, is_new):

	flag = 0

	if not "name" in buyer or buyer["name"]==None:
		flag = 1
		buyer["name"] = oldbuyer.name
	if not "company_name" in buyer or buyer["company_name"]==None:
		buyer["company_name"] = oldbuyer.company_name
	if not "mobile_number" in buyer or not validate_mobile_number(buyer["mobile_number"]):
		flag = 1
		buyer["mobile_number"] = oldbuyer.mobile_number
	if not "email" in buyer or buyer["email"]==None or not validate_email(buyer["email"]):
		buyer["email"] = oldbuyer.email
		if is_new == 1:
			buyer["email"] = None
	if not "alternate_phone_number" in buyer or buyer["alternate_phone_number"]==None:
		buyer["alternate_phone_number"] = oldbuyer.alternate_phone_number
	if not "mobile_verification" in buyer or not validate_bool(buyer["mobile_verification"]):
		buyer["mobile_verification"] = oldbuyer.mobile_verification
	if not "email_verification" in buyer  or not validate_bool(buyer["email_verification"]):
		buyer["email_verification"] = oldbuyer.email_verification
	if not "gender" in buyer or buyer["gender"]:
		buyer["gender"] = oldbuyer.gender
	if not "whatsapp_number" in buyer or buyer["whatsapp_number"]==None:
		if oldbuyer.whatsapp_number==None or oldbuyer.whatsapp_number=="":
			buyer["whatsapp_number"] = buyer["mobile_number"]
		else:
			buyer["whatsapp_number"] = oldbuyer.whatsapp_number
	if not "whatsapp_sharing_active" in buyer or not validate_bool(buyer["whatsapp_sharing_active"]):
		buyer["whatsapp_sharing_active"] = oldbuyer.whatsapp_sharing_active
	if not "store_global_margin" in buyer or not validate_percent(buyer["store_global_margin"], False):
		buyer["store_global_margin"] = oldbuyer.store_global_margin

	if is_new == 1 and flag == 1:
		return False

	return True

def validateBuyerDetailsData(buyerdetails, oldbuyerdetails, is_new):

	if not "vat_tin" in buyerdetails or buyerdetails["vat_tin"]==None:
		buyerdetails["vat_tin"] = oldbuyerdetails.vat_tin
	if not "cst" in buyerdetails or buyerdetails["cst"]==None:
		buyerdetails["cst"] = oldbuyerdetails.cst
	if not "customer_type" in buyerdetails or buyerdetails["customer_type"]==None or not validate_buyer_customer_type(buyerdetails["customer_type"]):
		buyerdetails["customer_type"] = oldbuyerdetails.customer_type
	if not "buying_capacity" in buyerdetails  or not validate_integer(buyerdetails["buying_capacity"]):
		buyerdetails["buying_capacity"] = oldbuyerdetails.buying_capacity
	if not "purchase_duration" in buyerdetails or not validate_integer(buyerdetails["purchase_duration"]):
		buyerdetails["purchase_duration"] = oldbuyerdetails.purchase_duration

def validateBuyerAddressData(buyeraddress, oldbuyeraddress, is_new = False):

	flag = 0

	if not "address" in buyeraddress or buyeraddress["address"]==None:
		buyeraddress["address"] = oldbuyeraddress.address_line
		flag =1
	if not "landmark" in buyeraddress or buyeraddress["landmark"]==None:
		buyeraddress["landmark"] = oldbuyeraddress.landmark
	if not "city" in buyeraddress or buyeraddress["city"]==None:
		buyeraddress["city"] = oldbuyeraddress.city_name
		flag =1
	if not "state" in buyeraddress or buyeraddress["state"]==None:
		buyeraddress["state"] = oldbuyeraddress.state_name
		flag =1
	if not "country" in buyeraddress or buyeraddress["country"]==None:
		buyeraddress["country"] = oldbuyeraddress.country_name
	if not "contact_number" in buyeraddress or buyeraddress["contact_number"]==None:
		buyeraddress["contact_number"] = oldbuyeraddress.contact_number
	if not "pincode" in buyeraddress or buyeraddress["pincode"]==None or not validate_pincode(buyeraddress["pincode"]):
		buyeraddress["pincode"] = oldbuyeraddress.pincode_number
		flag = 1
	if not "alias" in buyeraddress or buyeraddress["alias"]==None:
		buyeraddress["alias"] = oldbuyeraddress.alias
	if not "client_id" in buyeraddress or buyeraddress["client_id"]==None:
		buyeraddress["client_id"] = oldbuyeraddress.client_id

	if is_new == 1 and flag == 1:
		return False

	return True

def populateBuyer(buyerPtr, buyer):
	buyerPtr.name = buyer["name"]
	buyerPtr.company_name = buyer["company_name"]
	if buyerPtr.company_name != "":
		buyerPtr.store_slug = slugify(buyerPtr.company_name)
	else:
		buyerPtr.store_slug = slugify(buyerPtr.name)
	buyerPtr.mobile_number = buyer["mobile_number"]
	buyerPtr.whatsapp_number = buyer["whatsapp_number"]
	buyerPtr.email = buyer["email"]
	buyerPtr.alternate_phone_number = buyer["alternate_phone_number"]
	buyerPtr.mobile_verification = int(buyer["mobile_verification"])
	buyerPtr.email_verification = int(buyer["email_verification"])
	buyerPtr.whatsapp_sharing_active = int(buyer["whatsapp_sharing_active"])
	buyerPtr.gender = buyer["gender"]
	buyerPtr.save()
	#buyerPtr.store_url = "{}-{}".format(buyerPtr.store_slug,buyerPtr.id)
	if validate_percent(buyer["store_global_margin"], False):
		buyerPtr.store_global_margin = Decimal(buyer["store_global_margin"])
		buyerPtr.save()
	buyerPtr.whatsapp_contact_name = str(buyerPtr.id) + " Wholdus " + buyerPtr.name

def populateBuyerDetails(buyerDetailsPtr, buyerdetails):
	buyerDetailsPtr.cst = buyerdetails["cst"]
	buyerDetailsPtr.customer_type = int(buyerdetails["customer_type"])
	buyerDetailsPtr.buying_capacity = int(buyerdetails["buying_capacity"])
	buyerDetailsPtr.purchase_duration = int(buyerdetails["purchase_duration"])
	buyerDetailsPtr.vat_tin = buyerdetails["vat_tin"]

def populateBuyerAddress(buyerAddressPtr, buyeraddress):
	buyerAddressPtr.address_line = buyeraddress["address"]
	buyerAddressPtr.landmark = buyeraddress["landmark"]
	buyerAddressPtr.contact_number = buyeraddress["contact_number"]
	buyerAddressPtr.pincode_number = buyeraddress["pincode"]
	buyerAddressPtr.alias = buyeraddress["alias"]
	buyerAddressPtr.client_id = buyeraddress["client_id"]

	try:
		pincode = Pincode.objects.get(pincode=buyeraddress["pincode"])
		buyerAddressPtr.pincode = pincode
		buyerAddressPtr.city_name = pincode.city.name
		buyerAddressPtr.state_name = pincode.city.state.name
		buyerAddressPtr.country_name = pincode.city.state.country.name

	except Exception as e:
		buyerAddressPtr.city_name = buyeraddress["city"]
		buyerAddressPtr.state_name = buyeraddress["state"]
		buyerAddressPtr.country_name = "India"

def filterBuyer(parameters = {}):

	buyers = Buyer.objects.filter(delete_status=False).select_related('buyerdetails')

	if "buyersArr" in parameters:
		buyers = buyers.filter(id__in=parameters["buyersArr"])

	if "buyer_min_ID" in parameters:
		buyers = buyers.filter(id__gte=parameters["buyer_min_ID"])

	if "buyer_max_ID" in parameters:
		buyers = buyers.filter(id__lte=parameters["buyer_max_ID"])

	if "whatsapp_sharing_active" in parameters:
		buyers = buyers.filter(whatsapp_sharing_active=parameters["whatsapp_sharing_active"])

	if "test_buyer" in parameters:
		buyers = buyers.filter(test_buyer=parameters["test_buyer"])

	return buyers

def buyerEmailExists(email):
	buyerPtr = Buyer.objects.filter(email=email)

	if len(buyerPtr) > 0:
		return True

	return False

def buyerMobileNumberExists(mobileNumber):
	buyerPtr = Buyer.objects.filter(mobile_number=mobileNumber)

	if len(buyerPtr) > 0:
		return True

	return False

BuyerCustomerType = {
	1:{"display_value":"Average"},
	2:{"display_value":"Premium"},
	3:{"display_value":"Average and Premium"},
	4:{"display_value":"Low"},
	5:{"display_value":"All"},
	6:{"display_value":"Average and Low"},
}

BuyerCustomerTypeValues = [1,2,3,4,5,6]

def validate_buyer_customer_type(x):
	if not validate_integer(x) or not (int(x) in BuyerCustomerTypeValues):
		return False
	return True

def getBuyerToken(buyer):
	tokenPayload = {
		"user": "buyer",
		"buyerID": buyer.id,
		"password":buyer.password,
	}
	encoded = JsonWebToken.encode(tokenPayload, settings.SECRET_KEY, algorithm='HS256')
	return encoded.decode("utf-8")