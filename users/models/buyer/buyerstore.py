from django.db import models
from django.contrib import admin

from scripts.utils import validate_mobile_number, validate_email, validate_bool, validate_pincode, validate_integer, validate_number, getStrArrFromString, getArrFromString, link_to_foreign_key, create_email

class BuyerStoreLead(models.Model):
	buyer = models.ForeignKey('users.Buyer')
	product = models.ForeignKey('catalog.Product')

	status = models.IntegerField(default=0)
	sizes = models.CharField(max_length=100, blank=True)
	quantity = models.IntegerField(default=1)

	name = models.CharField(max_length=255, blank=True)
	mobile_number = models.CharField(max_length=11, blank=False)
	email = models.CharField(max_length=255, blank=True)

	class Meta:
		verbose_name="Buyer Store Lead"
		verbose_name_plural = "Buyer Store Leads"

	def __unicode__(self):
		return "{} - {} - {}".format(self.buyer,self.name,self.mobile_number)

	def validateBuyerStoreLeadData(self, buyer_store_lead, is_new):
		flag = 0

		if not "name" in buyer_store_lead or buyer_store_lead["name"] == None:
			flag = 1
			buyer_store_lead["name"] = self.name
		if not "mobile_number" in buyer_store_lead or not validate_mobile_number(buyer_store_lead["mobile_number"]):
			flag = 1
			buyer_store_lead["mobile_number"] = self.mobile_number
		if not "email" in buyer_store_lead or  not validate_email(buyer_store_lead["email"]):
			buyer_store_lead["email"] = self.email
		if not "status" in buyer_store_lead or  not validate_integer(buyer_store_lead["status"]):
			buyer_store_lead["status"] = self.status
		if not "sizes" in buyer_store_lead or buyer_store_lead["sizes"]==None:
			buyer_store_lead["sizes"] = self.sizes
		if not "quantity" in buyer_store_lead or  not validate_integer(buyer_store_lead["quantity"]):
			buyer_store_lead["quantity"] = self.quantity

		if is_new == 1 and flag == 1:
			return False

		return True

	def populateBuyerStoreLead(self, buyer_store_lead):
		self.status = int(buyer_store_lead["status"])
		self.sizes = buyer_store_lead["sizes"]
		self.quantity = int(buyer_store_lead["quantity"])
		self.name = buyer_store_lead["name"]
		self.mobile_number = buyer_store_lead["mobile_number"]
		self.email = buyer_store_lead["email"]

	def sendRetailerMail(self, parameters = {}):

		buyerPtr = self.buyer

		if buyerPtr.email == None or buyerPtr.email == "":
			return

		from_email = "Wholdus Info <info@wholdus.com>"
		mail_template_file = "buyer_store/buyer_store_lead.html"
		subject = "New purchase request on your online store on Wholdus"
		to_email = [buyerPtr.email]

		from users.serializers.buyer import serialize_buyer_store_lead

		mail_dict = serialize_buyer_store_lead(self, parameters)

		bcc = ["manish@wholdus.com","kushagra@wholdus.com"]
		bcc = []

		create_email(mail_template_file, mail_dict, subject, from_email, to_email, bcc = bcc)


class BuyerStoreLeadAdmin(admin.ModelAdmin):
	list_display = ["id", "link_to_buyer", "link_to_product", "name", "mobile_number", "status"]
	list_filter = ["buyer", "status"]
	list_display_links = ["id", "link_to_buyer", "link_to_product"]

	def link_to_buyer(self, obj):
		return link_to_foreign_key(obj, "buyer")
	link_to_buyer.short_description = "Buyer"
	link_to_buyer.allow_tags=True

	def link_to_product(self, obj):
		return link_to_foreign_key(obj, "product")
	link_to_product.short_description = "Product"
	link_to_product.allow_tags=True

def filterBuyerStoreLeads(parameters):

	buyerStoreLeads = BuyerStoreLead.objects.all()

	if "buyerStoreLeadsArr" in parameters:
		buyerStoreLeads = buyerStoreLeads.filter(id__in=parameters["buyerStoreLeadsArr"])

	if "buyersArr" in parameters:
		buyerStoreLeads = buyerStoreLeads.filter(buyer_id__in=parameters["buyersArr"])

	if "productsArr" in parameters:
		buyerStoreLeads = buyerStoreLeads.filter(product_id__in=parameters["productsArr"])

	if "buyer_store_lead_status" in parameters:
		buyerStoreLeads = buyerStoreLeads.filter(status__in=parameters["buyer_store_lead_status"])

	return buyerStoreLeads