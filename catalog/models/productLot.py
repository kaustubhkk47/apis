from django.db import models

from catalog.models.product import Product
from decimal import Decimal

from scripts.utils import validate_number, validate_integer, validate_bool

class ProductLot(models.Model):
    product = models.ForeignKey(Product)

    lot_size_from = models.IntegerField()
    lot_size_to = models.IntegerField()

    price_per_unit	 = models.DecimalField(max_digits=7, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.product.name

def validateProductLotData(product_lots):
	flag = 1
	for i in range(len(product_lots)):
		product_lot = product_lots[i]
		if not "lot_size_from" in product_lot or not validate_integer(product_lot["lot_size_from"]):
			flag = 0
		if not "lot_size_to" in product_lot or not validate_integer(product_lot["lot_size_to"]):
			flag = 0
		if not "price_per_unit" in product_lot or product_lot["price_per_unit"]==None or not validate_number(product_lot["price_per_unit"]):
			flag = 0

	return flag

def populateProductLotData(ProductLotPtr, productLot):
	ProductLotPtr.lot_size_from = int(productLot["lot_size_from"])
	ProductLotPtr.lot_size_to = int(productLot["lot_size_to"])
	ProductLotPtr.price_per_unit = Decimal(productLot["price_per_unit"])

def parseMinPricePerUnit(product_lots):
	return product_lots[len(product_lots)-1]["price_per_unit"]

def getCalculatedPricePerPiece(productID, lots):
    productLotsQuerySet = ProductLot.objects.filter(product_id = productID).order_by('lot_size_from')
    
    if lots < productLotsQuerySet[0].lot_size_from:
        return productLotsQuerySet[0].price_per_unit

    for productLot in productLotsQuerySet:
        if lots <= productLot.lot_size_to:
            return productLot.price_per_unit

    return productLotsQuerySet[len(productLotsQuerySet)-1].price_per_unit
