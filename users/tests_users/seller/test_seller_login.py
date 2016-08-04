from scripts.baseTestCases import *
from users.models.seller import *

class seller_login_test_case_get(masterTestCase):

	fixtures = []
	BASE_URL = '/users/seller/login/'

	def test_seller_login_get(self):

		error = self.getMethod("error", {}, "4XX")[0]
		self.assertEqual(error, "Invalid request")

class seller_login_test_case_post(masterTestCase):

	fixtures = ONLY_SELLER_FIXTURE
	BASE_URL = '/users/seller/login/'
	METHOD_NAME = "post"

	def test_seller_login_post(self):

		allKeys = {"email":"kausthegreat@gmail.com", "password":"glam123"}

		error = self.loginMethod("error", {}, "4XX")[0]
		self.assertEqual(error, "Either email or password was empty")

		tempDict = allKeys.copy()
		tempDict.pop("email")
		error = self.loginMethod("error", tempDict, "4XX")[0]
		self.assertEqual(error, "Either email or password was empty")

		tempDict = allKeys.copy()
		tempDict.pop("password")
		error = self.loginMethod("error", tempDict, "4XX")[0]
		self.assertEqual(error, "Either email or password was empty")

		tempDict = allKeys.copy()
		tempDict["password"] = ""
		error = self.loginMethod("error", tempDict, "4XX")[0]
		self.assertEqual(error, "Either email or password was empty")

		tempDict = allKeys.copy()
		tempDict["email"] = ""
		error = self.loginMethod("error", tempDict, "4XX")[0]
		self.assertEqual(error, "Either email or password was empty")

		tempDict = allKeys.copy()
		tempDict["email"] = "hello"
		error = self.loginMethod("error", tempDict, "4XX")[0]
		self.assertEqual(error, "Invalid email")

		tempDict = allKeys.copy()
		tempDict["password"] = "hello"
		error = self.loginMethod("error", tempDict, "4XX")[0]
		self.assertEqual(error, "Invalid password")

		result = self.loginMethod("token", allKeys, "2XX", "seller")
		access_token = result[0]
		seller = result[1]
		sellerPtr = Seller.objects.get(id=2)
		self.assertEqual(access_token, getSellerToken(sellerPtr))
		self.compareSeller(seller, sellerPtr)


class seller_login_test_case_put(masterTestCase):

	fixtures = []
	BASE_URL = '/users/seller/login/'
	METHOD_NAME = "put"

	def test_seller_login_put(self):

		self.blankMethod("Invalid request")

class seller_login_test_case_delete(masterTestCase):

	fixtures = []
	BASE_URL = '/users/seller/login/'
	METHOD_NAME = "delete"

	def test_seller_login_put(self):

		self.blankMethod("Invalid request")

