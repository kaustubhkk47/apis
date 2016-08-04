from scripts.baseTestCases import *
from users.models.seller import *

class seller_test_case_get(masterTestCase):

	fixtures = ADDRESS_FIXTURE + TOTAL_SELLER_FIXTURE
	BASE_URL = '/users/seller/'

	def test_seller_get(self):

		error = self.getMethod("error", {}, "4XX")[0]
		self.assertEqual(error, "Authentication failure")
		"""
		sellerAllKeys = {"email":"kausthegreat@gmail.com", "password":"glam123"}
		seller_access_token = self.loginMethod("token", sellerAllKeys, "2XX")[0]
		print seller_access_token

		sellerKeys = {"access_token":seller_access_token}
		result = self.getMethod("sellers", sellerKeys, "2XX")[0]
		self.assertEqual(len(result), 1)
		sellerPtr = Seller.objects.get(id=2)
		self.assertEqual(access_token, getSellerToken(sellerPtr))
		self.compareSeller(result, sellerPtr)
		"""
		