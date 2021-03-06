# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-09-27 08:25
from __future__ import unicode_literals

from django.db import migrations
from django.db.models import Sum

def populate_order_shipment_data(apps, schema_editor):
	
	OrderShipment = apps.get_model("orders","OrderShipment")
	OrderItem = apps.get_model("orders","OrderItem")

	orderShipments = OrderShipment.objects.all()

	for orderShipmentPtr in orderShipments:

		allOrderItems = OrderItem.objects.filter(order_shipment_id=orderShipmentPtr.id)
		allOrderItemsValues = allOrderItems.aggregate(Sum('pieces'))
		orderShipmentPtr.pieces = allOrderItemsValues["pieces__sum"]
		orderShipmentPtr.product_count = allOrderItems.count()
		
		orderShipmentPtr.save()


class Migration(migrations.Migration):

	dependencies = [
		('orders', '0027_auto_20160927_0825'),
	]

	operations = [
		migrations.RunPython(populate_order_shipment_data),
	]
