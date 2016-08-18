from django.db import models
from django.contrib import admin
from scripts.utils import validate_integer, link_to_foreign_key, validate_bool
from decimal import Decimal

class Checkout(models.Model):

	cart = models.ForeignKey('orders.Cart', null=True, blank=True)