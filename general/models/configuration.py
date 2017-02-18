from django.db import models


class CartMinValue(models.Model):

	value = models.IntegerField()

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name="Cart Min Value"
		verbose_name_plural = "Cart Min Value"

	def __unicode__(self):
		return "{}".format(self.value)

class CartSellerMinPieces(models.Model):

	value = models.IntegerField()

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name="Cart Seller Min Pieces"
		verbose_name_plural = "Cart Seller Min Pieces"

	def __unicode__(self):
		return "{}".format(self.value)