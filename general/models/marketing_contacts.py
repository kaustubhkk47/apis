from django.db import models


class MarketingContact(models.Model):

	internal_user = models.ForeignKey('users.InternalUser', null=True, on_delete=models.SET_NULL)

	mobile_number = models.CharField(max_length=11, blank=False, db_index=True)
	contact_name = models.CharField(max_length=100, blank=True)

	sharing_link = models.CharField(max_length=100, blank=True)
	sharing_link_clicks = models.IntegerField(default=0)
	sharing_link_click_time = models.DateTimeField(null=True)

	message_sent_time = models.DateTimeField(null=True)
	message_sent_count = models.IntegerField(default=0)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name="Marketing Contact"
		verbose_name_plural = "Marketing Contacts"

	def __unicode__(self):
		return "{} - {}".format(self.mobile_number,self.contact_name)


def validateMarketingContactData(contacts):
	for contact in contacts:
		if not "mobile_number" in contact or contact["mobile_number"] == None:
			return False
	return True

def filterMarketingContacts(parameters):

	marketingContacts = MarketingContact.objects.filter(message_sent_count=0)

	if "new_contacts" in parameters and parameters["new_contacts"] == 1:
		marketingContacts = marketingContacts.filter(internal_user_id = None)
	else:
		marketingContacts = marketingContacts.filter(internal_user_id = parameters["internalusersArr"][0])

	return marketingContacts