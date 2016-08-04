from django.db import models
from django.contrib import admin
from scripts.utils import validate_integer, link_to_foreign_key, validate_bool

class Cart(models.Model):

	buyer = models.ForeignKey('users.Buyer')

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	status = models.IntegerField(default=0)

	class Meta:
		verbose_name="Cart"
		verbose_name_plural = "Cart"

	def __unicode__(self):
		return "{} - {}".format(str(self.buyer), self.status)

CartStatus = {
	0:{"display_value":"Active"},
	1:{"display_value":"Checked Out"},
}

CartStatusValues = [0,1]

class CartAdmin(admin.ModelAdmin):

	list_display = ["id", "buyer", "created_at"]

class CartItem(models.Model):

	buyer = models.ForeignKey('users.Buyer')
	cart =models.ForeignKey(Cart, null=True, blank=True)
	product = models.ForeignKey('catalog.Product')

	lots = models.PositiveIntegerField(default=0)
	pieces = models.PositiveIntegerField(default=0)
	lot_size = models.PositiveIntegerField(default=1)
	retail_price_per_piece = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)
	calculated_price_per_piece = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)
	final_price = models.DecimalField(max_digits=10, decimal_places=2)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True, db_index=True)

	status = models.IntegerField(default=0)

	#added_from values
	#0 : category_page, 1 : product_page, 2 : shortlist, 3 : homepage
	added_from = models.IntegerField(default=0)

	class Meta:
		ordering = ["-updated_at"]
		default_related_name = "cartitem"
		verbose_name="Cart Item"
		verbose_name_plural = "Cart Items"

	def __unicode__(self):
		return "{} - {} - {}".format(str(self.buyer), str(self.product), self.pieces)

	def validateCartItemData(self, cartitem):
		if not "lots" in cartitem or not validate_integer(cartitem["lots"]):
			return False
		if not "added_from" in cartitem or not validate_integer(cartitem["added_from"]):
			cartitem["added_from"] = 0
		return True

	def populateCartItemData(self, cartitem):
		self.lots = int(cartitem["lots"])
		if self.lots == 0:
			self.status = 1
		self.lot_size = self.product.lot_size
		self.pieces = self.lots*self.lot_size
		self.retail_price_per_piece = self.product.price_per_unit
		self.calculated_price_per_piece = self.product.getCalculatedPricePerPiece(self.lots)
		self.final_price = self.pieces*self.calculated_price_per_piece
		self.added_from = int(cartitem["added_from"])

CartItemStatus = {
	0:{"display_value":"Active"},
	1:{"display_value":"Removed"},
	2:{"display_value":"Checked Out"},
}

class CartItemAdmin(admin.ModelAdmin):
	search_fields = ["buyer_id", "buyer__name", "product_id","product__name"]
	list_display = ["id", "link_to_buyer", "link_to_product", "final_price", "pieces"]

	list_display_links = ["id","link_to_buyer","link_to_product"]

	list_filter = ["status"]

	def link_to_buyer(self, obj):
		return link_to_foreign_key(obj, "buyer")
	link_to_buyer.short_description = "Buyer"
	link_to_buyer.allow_tags=True

	def link_to_product(self, obj):
		return link_to_foreign_key(obj, "product")
	link_to_product.short_description = "Product"
	link_to_product.allow_tags=True

class CartItemHistory(models.Model):

	buyer = models.ForeignKey('users.Buyer')
	cart =models.ForeignKey(Cart, null=True, blank=True)
	cartitem =models.ForeignKey(CartItem, null=True, blank=True)
	product = models.ForeignKey('catalog.Product')

	lots = models.PositiveIntegerField(default=0)
	pieces = models.PositiveIntegerField(default=0)
	lot_size = models.PositiveIntegerField(default=1)
	retail_price_per_piece = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)
	calculated_price_per_piece = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)
	final_price = models.DecimalField(max_digits=10, decimal_places=2)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	status = models.IntegerField(default=0)

	added_from = models.IntegerField(default=0)

	class Meta:
		verbose_name="Cart Item History"
		verbose_name_plural = "Cart Item History"

	def __unicode__(self):
		return "{} - {} - {}".format(str(self.buyer), str(self.product), self.pieces)

	def populateCartItemHistoryData(self, cartItemPtr):
		self.buyer = cartItemPtr.buyer
		self.cart = cartItemPtr.cart
		self.cartitem = cartItemPtr
		self.product = cartItemPtr.product
		self.lots = cartItemPtr.lots
		self.pieces = cartItemPtr.pieces
		self.lot_size = cartItemPtr.lot_size
		self.retail_price_per_piece = cartItemPtr.retail_price_per_piece
		self.calculated_price_per_piece = cartItemPtr.calculated_price_per_piece
		self.final_price = cartItemPtr.final_price
		self.status = cartItemPtr.status
		self.added_from = cartItemPtr.added_from

def filterCartItem(parameters):

	cartItems = CartItem.objects.filter(cart__status=0).select_related('product')

	if "cartItemsArr" in parameters:
		cartItems = cartItems.filter(id__in=parameters["cartItemsArr"])

	if "buyersArr" in parameters:
		cartItems = cartItems.filter(buyer_id__in=parameters["buyersArr"])

	if "productsArr" in parameters:
		cartItems = cartItems.filter(product_id__in=parameters["productsArr"])

	if "cartItemStatusArr" in parameters:
		cartItems = cartItems.filter(status__in=parameters["cartItemStatusArr"])

	return cartItems


