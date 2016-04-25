from django.db import models

from catalog.models.product import Product
from decimal import Decimal

class ProductLot(models.Model):
    product = models.ForeignKey(Product)

    lot_size_from = models.IntegerField()
    lot_size_to = models.IntegerField()

    price_per_unit = models.DecimalField(max_digits=7, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.product.name

def validateProductLotData(product_lots):
	flag = 1
	for i in range(len(product_lots)):
		product_lot = product_lots[i]
		if not "lot_size_from" in product_lot or not product_lot["lot_size_from"]!=None:
			flag = 0
		if not "lot_size_to" in product_lot or not product_lot["lot_size_to"]!=None:
			flag = 0
		if not "price_per_unit" in product_lot or not product_lot["price_per_unit"]!=None:
			flag = 0

	return flag

def populateProductLotData(ProductLotPtr, productLot):
	ProductLotPtr.lot_size_from = int(productLot["lot_size_from"])
	ProductLotPtr.lot_size_to = int(productLot["lot_size_to"])
	ProductLotPtr.price_per_unit = Decimal(productLot["price_per_unit"])

def parseMinPricePerUnit(product_lots):
	return product_lots[len(product_lots)-1]["price_per_unit"]
