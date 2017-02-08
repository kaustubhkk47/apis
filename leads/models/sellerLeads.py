from django.db import models
from django.contrib import admin
from scripts.utils import validate_bool, time_in_ist

class SellerLeads(models.Model):

	company_name = models.CharField(max_length=200, blank=True)
	email = models.EmailField(max_length=255, blank=True)
	mobile_number = models.CharField(max_length=11, blank=True)

	status = models.IntegerField(default=0)
	comments = models.TextField(blank=True)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-id"]
		default_related_name = "sellerlead"
		verbose_name="Seller Lead"
		verbose_name_plural = "Seller Leads"

	def __unicode__(self):
		return "{} - {} - {} - {}".format(self.id,self.mobile_number,self.company_name,self.email)

class SellerLeadsAdmin(admin.ModelAdmin):

	list_display = ["id", "mobile_number", "company_name", "email", "status", "created_at_ist"]
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

def validateSellerLeadData(sellerlead, oldsellerlead, is_new):

	flag = 0

	if not "company_name" in sellerlead or sellerlead["company_name"]==None:
		flag = 1
		sellerlead["company_name"] = oldsellerlead.company_name
	if not "mobile_number" in sellerlead or sellerlead["mobile_number"]==None:
		flag = 1
		sellerlead["mobile_number"] = oldsellerlead.mobile_number
	if not "email" in sellerlead or sellerlead["email"]==None:
		sellerlead["email"] = oldsellerlead.email
	if not "status" in sellerlead or not validate_bool(sellerlead["status"]):
		sellerlead["status"] = oldsellerlead.status
	if not "comments" in sellerlead or sellerlead["comments"]==None:
		sellerlead["comments"] = oldsellerlead.comments

	if is_new == 1 and flag == 1:
		return False

	return True

def populateSellerLead(sellerleadPtr, sellerlead):
	sellerleadPtr.company_name = sellerlead["company_name"]
	sellerleadPtr.email = sellerlead["email"]
	sellerleadPtr.mobile_number = sellerlead["mobile_number"]
	sellerleadPtr.status = int(sellerlead["status"])
	sellerleadPtr.comments = sellerlead["comments"]

SellerLeadStatus = {
	0:{"display_value":"New"},
	1:{"display_value":"Resolved"}
}