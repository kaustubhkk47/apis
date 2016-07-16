from django.db import models
from scripts.utils import validate_mobile_number, validate_email, validate_bool, validate_pincode, validate_integer, validate_number, getStrArrFromString, getArrFromString
from decimal import Decimal

class BuyerPurchasingState(models.Model):

	buyer = models.ForeignKey('users.Buyer')
	state = models.ForeignKey('address.State')

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	delete_status = models.BooleanField(default=False)

	def __unicode__(self):
		return str(self.buyer.id) + " - " + self.buyer.name + " - " + self.state.name

class BuyerBuysFrom(models.Model):

	buyer = models.ForeignKey('users.Buyer')
	business_type = models.ForeignKey('users.BusinessType',blank=True, null=True)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	delete_status = models.BooleanField(default=False)

	def __unicode__(self):
		return str(self.buyer.id) + " - " + self.buyer.name + " - " + self.business_type.name

class BuyerPanelInstructionsTracking(models.Model):

	buyer = models.ForeignKey('users.Buyer')
	page_closed = models.IntegerField(default=0)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return str(self.buyer.id)


def filterBuyerPurchasingState(parameters = {}):

	buyerPurchasingStates = BuyerPurchasingState.objects.filter(buyer__delete_status=False, delete_status=False)

	if "buyerPurchasingStateArr" in parameters:
		buyerPurchasingStates = buyerPurchasingStates.filter(id__in=parameters["buyerPurchasingStateArr"])

	if "buyersArr" in parameters:
		buyerPurchasingStates = buyerPurchasingStates.filter(buyer_id__in=parameters["buyersArr"])

	return buyerPurchasingStates

def filterBuyerBuysFrom(parameters = {}):

	buyerBuysFrom = BuyerBuysFrom.objects.filter(buyer__delete_status=False, delete_status=False)

	if "buyersArr" in parameters:
		buyerBuysFrom = buyerBuysFrom.filter(buyer_id__in=parameters["buyersArr"])

	return buyerBuysFrom