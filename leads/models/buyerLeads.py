from django.db import models
from django.contrib import admin

from catalog.models.product import Product
from catalog.models.category import Category

from scripts.utils import validate_bool, time_in_ist

class BuyerLeads(models.Model):

	product = models.ForeignKey('catalog.Product', blank = True, null=True)
	category = models.ForeignKey('catalog.Category', blank = True, null=True)

	name = models.CharField(max_length=200, blank=True)
	email = models.EmailField(max_length=255, blank=True)
	mobile_number = models.CharField(max_length=11, blank=True)
	signup = models.BooleanField(default=True)

	status = models.IntegerField(default=0)
	comments = models.TextField(blank=True)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-id"]
		default_related_name = "buyerlead"
		verbose_name="Buyer Lead"
		verbose_name_plural = "Buyer Leads"

	def __unicode__(self):
		return "{} - {} - {} - {}".format(self.id,self.mobile_number,self.name,self.email)

class BuyerLeadsAdmin(admin.ModelAdmin):

	list_display = ["id", "mobile_number", "name", "email", "comments", "signup", "created_at_ist"]
	list_filter = ["status"]

	list_display_links = ["id", "mobile_number"]

	actions = ["resolve_leads"]

	def resolve_leads(self, request, queryset):
		rows_updated = queryset.update(status=1)
		if rows_updated == 1:
			message_bit = "1 lead was"
		else:
			message_bit = "%s leads were" % rows_updated
		self.message_user(request, "%s marked as resolved." % message_bit)

	def created_at_ist(self, obj):
		return time_in_ist(obj.created_at)

def validateBuyerLeadData(buyerlead, oldbuyerlead, is_new):

	flag = 0

	if not "name" in buyerlead or buyerlead["name"]==None:
		flag = 1
		buyerlead["name"] = oldbuyerlead.name
	if not "mobile_number" in buyerlead or buyerlead["mobile_number"]==None:
		flag = 1
		buyerlead["mobile_number"] = oldbuyerlead.mobile_number
	if not "email" in buyerlead or buyerlead["email"]==None:
		buyerlead["email"] = oldbuyerlead.email
	if not "status" in buyerlead or not validate_bool(buyerlead["status"]):
		buyerlead["status"] = oldbuyerlead.status
	if not "signup" in buyerlead or not validate_bool(buyerlead["signup"]):
		buyerlead["signup"] = oldbuyerlead.signup
	if not "comments" in buyerlead or buyerlead["comments"]==None:
		buyerlead["comments"] = oldbuyerlead.comments

	if is_new == 1 and flag == 1:
		return False

	return True

def populateBuyerLead(buyerleadPtr, buyerlead):
	buyerleadPtr.name = buyerlead["name"]
	buyerleadPtr.email = buyerlead["email"]
	buyerleadPtr.mobile_number = buyerlead["mobile_number"]
	buyerleadPtr.status = int(buyerlead["status"])
	buyerleadPtr.signup = int(buyerlead["signup"])
	buyerleadPtr.comments = buyerlead["comments"]

BuyerLeadStatus = {
	0:{"display_value":"New"},
	1:{"display_value":"Resolved"}
}