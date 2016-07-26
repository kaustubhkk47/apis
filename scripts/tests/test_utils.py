from django.test import TestCase
from unittest import TestCase as uTestCase
from scripts.utils import *

class validate_bool_test_case(uTestCase):

	def validate_bool_true():
		self.assertTrue(validate_bool(0))
		self.assertTrue(validate_bool(1))
		self.assertTrue(validate_bool(True))
		self.assertTrue(validate_bool(False))
		self.assertTrue(validate_bool("0"))
		self.assertTrue(validate_bool("1"))

	def validate_bool_false():
		self.assertFalse(validate_bool("-1"))
		self.assertFalse(validate_bool(-1))
		self.assertFalse(validate_bool("5"))
		self.assertFalse(validate_bool(5))
		self.assertFalse(validate_bool("RandomString"))