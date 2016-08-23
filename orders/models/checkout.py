from django.db import models
from django.contrib import admin
from scripts.utils import validate_integer, link_to_foreign_key, validate_bool, time_in_ist
from decimal import Decimal

class Checkout(models.Model):

	cart = models.ForeignKey('orders.Cart', null=True, blank=True)
	buyer_address_history = models.ForeignKey('users.BuyerAddressHistory', null=True, blank=True)

	status =  models.IntegerField(default=0)

	payment_method =  models.IntegerField(default=-1)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	address_given_time = models.DateTimeField(null=True, blank=True)
	summary_confirmed_time = models.DateTimeField(null=True, blank=True)
	payment_done_time = models.DateTimeField(null=True, blank=True)

	class Meta:
		verbose_name="Checkout"
		verbose_name_plural = "Checkout"

	def __unicode__(self):
		return "{} - {}".format(self.id,str(self.cart))

	def validateCheckoutData(self, checkout):
		status = int(checkout["status"])
		if self.status == 0 and status == 1:
			return True
		elif self.status == 1 and status == 2:
			return True
		elif self.status == 2 and status ==3:
			if "payment_method" in checkout and validate_integer(checkout["payment_method"]) and int(checkout["payment_method"]) in [0,1]:
				return True

		return False

class CheckoutAdmin(admin.ModelAdmin):
	list_display = ["id", "link_to_cart","status", "payment_method", "created_at_ist"]

	list_display_links = ["id","link_to_cart"]

	list_filter = ["status", "payment_method"]

	def link_to_cart(self, obj):
		return link_to_foreign_key(obj, "cart")
	link_to_cart.short_description = "Cart"
	link_to_cart.allow_tags=True

	#def link_to_buyer_address(self, obj):
	#	return link_to_foreign_key(obj, "buyer_address_history")
	#link_to_buyer_address.short_description = "Buyer Address"
	#link_to_buyer_address.allow_tags=True

	def created_at_ist(self, obj):
		return time_in_ist(obj.created_at)


CheckoutStatus = {
	0:{"display_value":"Created"},
	1:{"display_value":"Address Given"},
	2:{"display_value":"Summary Confirmed"},
	3:{"display_value":"Payment done"}
}

CheckoutStatusArr = [0,1,2,3]

def filterCheckouts(parameters):

	checkouts = Checkout.objects.filter(status__in=[0,1,2])

	if "buyersArr" in parameters:
		checkouts = checkouts.filter(cart__buyer_id__in=parameters["buyersArr"])

	return checkouts