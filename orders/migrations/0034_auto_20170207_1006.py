# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2017-02-07 10:06
from __future__ import unicode_literals

from django.db import migrations

def correct_shipping_charges(apps, schema_editor):

	Cart = apps.get_model("orders", "Cart")
	SubCart = apps.get_model("orders", "SubCart")
	CartItem = apps.get_model("orders", "CartItem")

	cartPtr = Cart.objects.filter(status=0, pieces__gt=0)

	for cart in cartPtr:
		cartShippingCharge = 0
		subCartPtr = SubCart.objects.filter(status=0, pieces__gt=0, cart_id=cart.id)

		for subcart in subCartPtr:
			cartItemPtr = CartItem.objects.filter(status=0, pieces__gt=0, subcart_id=subcart.id)

			subCartShippingCharge = 0

			for cartitem in cartItemPtr:
				subCartShippingCharge += cartitem.shipping_charge

			extraShippingCharge = 0
			if subCartShippingCharge < 75:
				extraShippingCharge = 75 - subCartShippingCharge
				subCartShippingCharge = 75

			subcart.extra_shipping_charge = extraShippingCharge
			subcart.shipping_charge = subCartShippingCharge
			subcart.final_price = subcart.shipping_charge + subcart.calculated_price
			subcart.save()
			cartShippingCharge += subCartShippingCharge
		cart.shipping_charge = cartShippingCharge
		cart.final_price = cart.shipping_charge + cart.calculated_price
		cart.save()

class Migration(migrations.Migration):

	dependencies = [
		('orders', '0033_auto_20170106_1758'),
	]

	operations = [migrations.RunPython(correct_shipping_charges)]
