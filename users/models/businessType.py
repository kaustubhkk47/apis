from django.db import models

class BusinessType(models.Model):

	business_type = models.CharField(max_length=30)
	description = models.TextField(blank=True)

	can_buyer_buy_from = models.BooleanField(default=False)

	can_be_buyer = models.BooleanField(default=False)
	can_be_seller = models.BooleanField(default=False)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		default_related_name = "businesstype"
		verbose_name="Business Type"
		verbose_name_plural = "Business Types"

	def __unicode__(self):
		return "{} - {}".format(self.id,self.business_type)

def filterBusinessType(parameters = {}):

	businesstypes = BusinessType.objects.all()

	if "can_buyer_buy_from" in parameters:
		businesstypes = businesstypes.filter(can_buyer_buy_from=parameters["can_buyer_buy_from"])

	if "can_be_buyer" in parameters:
		businesstypes = businesstypes.filter(can_be_buyer=parameters["can_be_buyer"])

	if "can_be_seller" in parameters:
		businesstypes = businesstypes.filter(can_be_seller=parameters["can_be_seller"])

	return businesstypes