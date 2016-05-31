from django.db import models

from catalog.models.product import Product
from catalog.models.category import Category

class BuyerLeads(models.Model):

	product = models.ForeignKey(Product, blank = True, null=True)
	category = models.ForeignKey(Category, blank = True, null=True)

	name = models.CharField(max_length=200, blank=True)
	email = models.EmailField(max_length=255, blank=True)
	mobile_number = models.CharField(max_length=11, blank=True, db_index=True)

	status = models.IntegerField(default=0)
	comments = models.TextField(blank=True)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return self.mobile_number

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
	if not "status" in buyerlead or buyerlead["status"]==None:
		buyerlead["status"] = oldbuyerlead.status
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
	buyerleadPtr.comments = buyerlead["comments"]