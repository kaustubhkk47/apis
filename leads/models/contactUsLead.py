from django.db import models

class ContactUsLead(models.Model):

	email = models.EmailField(max_length=255, blank=True)
	mobile_number = models.CharField(max_length=11, blank=True, db_index=True)
	remarks = models.TextField(blank=True)

	status = models.IntegerField(default=0)
	comments = models.TextField(blank=True)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return self.mobile_number

def validateContactUsLeadData(contactUsLead, oldcontactUsLead, is_new):

	flag = 0

	if not "remarks" in contactUsLead or contactUsLead["remarks"]==None:
		contactUsLead["remarks"] = oldcontactUsLead.remarks
	if not "mobile_number" in contactUsLead or contactUsLead["mobile_number"]==None:
		contactUsLead["mobile_number"] = oldcontactUsLead.mobile_number
	if not "email" in contactUsLead or contactUsLead["email"]==None:
		contactUsLead["email"] = oldcontactUsLead.email
	if not "status" in contactUsLead or contactUsLead["status"]==None:
		contactUsLead["status"] = oldcontactUsLead.status
	if not "comments" in contactUsLead or contactUsLead["comments"]==None:
		contactUsLead["comments"] = oldcontactUsLead.comments

	if is_new == 1 and flag == 1:
		return False

	return True

def populateContactUsLead(contactUsLeadPtr, contactUsLead):
	contactUsLeadPtr.remarks = contactUsLead["remarks"]
	contactUsLeadPtr.email = contactUsLead["email"]
	contactUsLeadPtr.mobile_number = contactUsLead["mobile_number"]
	contactUsLeadPtr.status = int(contactUsLead["status"])
	contactUsLeadPtr.comments = contactUsLead["comments"]