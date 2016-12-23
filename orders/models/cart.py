from django.db import models
from django.contrib import admin
from scripts.utils import validate_integer, link_to_foreign_key, validate_bool, time_in_ist
from decimal import Decimal

class Cart(models.Model):

	buyer = models.ForeignKey('users.Buyer')

	pieces = models.PositiveIntegerField(default=0)
	product_count = models.PositiveIntegerField(default=0)
	retail_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
	calculated_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
	
	shipping_charge = models.DecimalField(max_digits=10, decimal_places=2,default=0)
	cod_charge = models.DecimalField(max_digits=10, decimal_places=2,default=0)
	final_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	status = models.IntegerField(default=0)

	class Meta:
		verbose_name="Cart"
		verbose_name_plural = "Cart"

	def __unicode__(self):
		return "{} - {}".format(str(self.buyer), self.status)

	def populateCartData(self,  initialPrices, finalPrices):
		self.pieces += finalPrices["pieces"] - initialPrices["pieces"]
		self.product_count +=  finalPrices["product_count"] - initialPrices["product_count"]
		self.retail_price +=  finalPrices["retail_price"] - initialPrices["retail_price"]
		self.calculated_price +=  finalPrices["calculated_price"] - initialPrices["calculated_price"]
		self.shipping_charge +=  finalPrices["shipping_charge"] - initialPrices["shipping_charge"] + finalPrices["extra_shipping_charge"] - initialPrices["extra_shipping_charge"]
		self.final_price +=  finalPrices["final_price"] - initialPrices["final_price"]+ finalPrices["extra_shipping_charge"] - initialPrices["extra_shipping_charge"]

	def setCODPaymentMethod(self, CODextracost):
		self.cod_charge = Decimal(CODextracost*float(self.calculated_price))
		self.final_price += self.cod_charge
		self.save()
		parameters = {}
		subCarts = filterSubCarts(parameters)
		subCarts = subCarts.filter(cart_id = self.id)
		for subCartPtr in subCarts:
			subCartPtr.setCODPaymentMethod(CODextracost)

CartStatus = {
	0:{"display_value":"Active"},
	1:{"display_value":"Checked Out"},
}

CartStatusValues = [0,1]

class CartAdmin(admin.ModelAdmin):

	list_display = ["id", "buyer", "created_at_ist"]

	def created_at_ist(self, obj):
		return time_in_ist(obj.created_at)

class SubCart(models.Model):

	cart = models.ForeignKey(Cart, null=True, blank=True)
	seller = models.ForeignKey('users.Seller')

	pieces = models.PositiveIntegerField(default=0)
	product_count = models.PositiveIntegerField(default=0)
	retail_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
	calculated_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
	
	shipping_charge = models.DecimalField(max_digits=10, decimal_places=2,default=0)
	extra_shipping_charge = models.DecimalField(max_digits=10, decimal_places=2,default=0)
	cod_charge = models.DecimalField(max_digits=10, decimal_places=2,default=0)
	final_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	status = models.IntegerField(default=0)

	class Meta:
		verbose_name="Sub Cart"
		verbose_name_plural = "Sub Cart"

	def __unicode__(self):
		return "{} - {}".format(str(self.seller), self.status)

	def populateSubCartData(self, initialPrices, finalPrices):
		self.pieces += finalPrices["pieces"] - initialPrices["pieces"]
		self.product_count +=  finalPrices["product_count"] - initialPrices["product_count"]
		self.retail_price +=  finalPrices["retail_price"] - initialPrices["retail_price"]
		self.calculated_price +=  finalPrices["calculated_price"] - initialPrices["calculated_price"]
		self.shipping_charge +=  finalPrices["shipping_charge"] - initialPrices["shipping_charge"] - self.extra_shipping_charge
		self.final_price +=  finalPrices["final_price"] - initialPrices["final_price"] - self.extra_shipping_charge
		if self.shipping_charge < 175 and self.product_count>0:
			self.extra_shipping_charge = (175-self.shipping_charge)
			self.shipping_charge += self.extra_shipping_charge
			self.final_price += self.extra_shipping_charge
		else:
			self.extra_shipping_charge = 0

	def setCODPaymentMethod(self, CODextracost):
		self.cod_charge = Decimal(CODextracost*float(self.calculated_price))
		self.final_price += self.cod_charge
		self.save()

SubCartStatus = {
	0:{"display_value":"Active"},
	1:{"display_value":"Checked Out"},
}

SubCartStatusValues = [0,1]

class CartItem(models.Model):

	buyer = models.ForeignKey('users.Buyer')
	subcart =models.ForeignKey(SubCart, null=True, blank=True)
	product = models.ForeignKey('catalog.Product')

	lots = models.PositiveIntegerField(default=0)
	pieces = models.PositiveIntegerField(default=0)
	lot_size = models.PositiveIntegerField(default=1)
	retail_price_per_piece = models.DecimalField(max_digits=10, decimal_places=2,default=0)
	calculated_price_per_piece = models.DecimalField(max_digits=10, decimal_places=2,default=0)

	shipping_charge = models.DecimalField(max_digits=10, decimal_places=2,default=0)

	final_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

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

	@staticmethod
	def validateCartItemData(cartProducts, productsHash, productIDarr):

		for cartitem in cartProducts:
			if not "productID" in cartitem or not validate_integer(cartitem["productID"]):
				return False

			productID = int(cartitem["productID"])

			if not "lots" in cartitem or not validate_integer(cartitem["lots"]):
				return False
			if not "added_from" in cartitem or not validate_integer(cartitem["added_from"]):
				cartitem["added_from"] = 0

			productsHash[productID] = len(productsHash)
			productIDarr.append(productID)

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
		self.shipping_charge = Decimal(self.product.getShippingPerPiece()*self.pieces)

	def getPrices(self):
		initialPrices = {}
		initialPrices["pieces"] = self.pieces 
		if self.pieces > 0:
			initialPrices["product_count"] = 1
		else:
			initialPrices["product_count"] = 0
		initialPrices["retail_price"] = Decimal(self.retail_price_per_piece*self.pieces)
		initialPrices["calculated_price"] = Decimal(self.final_price)
		initialPrices["shipping_charge"] = Decimal(self.shipping_charge)
		initialPrices["final_price"] = Decimal(self.final_price + self.shipping_charge)
		return initialPrices

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
	subcart =models.ForeignKey(SubCart, null=True, blank=True)
	cartitem =models.ForeignKey(CartItem, null=True, blank=True)
	product = models.ForeignKey('catalog.Product')

	lots = models.PositiveIntegerField(default=0)
	pieces = models.PositiveIntegerField(default=0)
	lot_size = models.PositiveIntegerField(default=1)
	retail_price_per_piece = models.DecimalField(max_digits=10, decimal_places=2,default=0)
	calculated_price_per_piece = models.DecimalField(max_digits=10, decimal_places=2,default=0)

	shipping_charge = models.DecimalField(max_digits=10, decimal_places=2,default=0)

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
		self.subcart = cartItemPtr.subcart
		self.cartitem = cartItemPtr
		self.product = cartItemPtr.product
		self.lots = cartItemPtr.lots
		self.pieces = cartItemPtr.pieces
		self.lot_size = cartItemPtr.lot_size
		self.retail_price_per_piece = cartItemPtr.retail_price_per_piece
		self.calculated_price_per_piece = cartItemPtr.calculated_price_per_piece
		self.shipping_charge = cartItemPtr.shipping_charge
		self.final_price = cartItemPtr.final_price
		self.status = cartItemPtr.status
		self.added_from = cartItemPtr.added_from

def filterCartItem(parameters):

	cartItems = CartItem.objects.filter(subcart__status=0, status=0).select_related('product')

	if "cartItemsArr" in parameters:
		cartItems = cartItems.filter(id__in=parameters["cartItemsArr"])

	if "buyersArr" in parameters:
		cartItems = cartItems.filter(buyer_id__in=parameters["buyersArr"])

	if "productsArr" in parameters:
		cartItems = cartItems.filter(product_id__in=parameters["productsArr"])

	if "cartItemStatusArr" in parameters:
		cartItems = cartItems.filter(status__in=parameters["cartItemStatusArr"])

	return cartItems

def filterCarts(parameters):

	carts = Cart.objects.filter(status=0, pieces__gt=0)

	if "buyersArr" in parameters:
		carts = carts.filter(buyer_id__in=parameters["buyersArr"])

	return carts

def filterSubCarts(parameters):

	subcarts = SubCart.objects.filter(status=0, pieces__gt=0)

	return subcarts