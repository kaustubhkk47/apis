from django.test import TestCase
import json
from .utils import djangoEncodedTime

ADDRESS_FIXTURE = ['country_models_testdata.json', 'state_models_testdata.json', 'city_models_testdata.json','pincode_models_testdata.json']

CATEGORY_FIXTURE = ['category_models_testdata.json']

ONLY_SELLER_FIXTURE = ['seller_models_testdata.json']
TOTAL_SELLER_FIXTURE = ONLY_SELLER_FIXTURE + ['seller_details_models_testdata.json', 'seller_address_models_testdata.json']

class masterTestCase(TestCase):

	def getMethod(self, objectName, parameters = {}, statusCode = "2XX"):
		resp = self.client.get(self.BASE_URL, parameters)
		self.assertEqual(resp.status_code, 200)
		respJson = resp.json()
		self.assertEqual(respJson["statusCode"], statusCode)
		jsonBody = respJson["body"]
		return [jsonBody[objectName]]

	def generalMethod(self, objectName, parameters = {}, statusCode = "2XX"):
		jsonStr = json.dumps(parameters)
		resp = getattr(self.client, self.METHOD_NAME)(self.BASE_URL, data= jsonStr, content_type='application/json')
		self.assertEqual(resp.status_code, 200)
		respJson = resp.json()
		self.assertEqual(respJson["statusCode"], statusCode)
		jsonBody = respJson["body"]
		return jsonBody[objectName]

	def blankMethod(self, errorMessage = "Invalid data sent in request"):
		resp = getattr(self.client, self.METHOD_NAME)(self.BASE_URL)
		self.assertEqual(resp.status_code, 200)
		respJson = resp.json()
		self.assertEqual(respJson["statusCode"], '4XX')
		jsonBody = respJson["body"]
		self.assertEqual(jsonBody["error"], errorMessage)

	def loginMethod(self, objectName, loginParameters,statusCode = "2XX", objectName2=None):
		resp= self.client.post(self.BASE_URL, loginParameters)
		self.assertEqual(resp.status_code, 200)
		respJson = resp.json()
		self.assertEqual(respJson["statusCode"], statusCode)
		jsonBody = respJson["body"]
		result = [jsonBody[objectName]]
		if not objectName2 == None:
			result.append(jsonBody[objectName2])
		return result

	def compareCategories(self, category, categoryPtr, serialized = 1):
		if serialized or "display_name" in category:
			self.assertEqual(category["display_name"], categoryPtr.display_name)
		if serialized or "name" in category:
			self.assertEqual(category["name"], categoryPtr.name)
		if serialized or "url" in category:
			self.assertEqual(category["url"], "{}-{}".format(categoryPtr.slug, categoryPtr.id))
		if serialized or "slug" in category:
			self.assertEqual(category["slug"], categoryPtr.slug)
		if serialized or "id" in category:
			self.assertEqual(category["id"], categoryPtr.id)
		if serialized or "categoryID" in category:
			self.assertEqual(category["categoryID"], categoryPtr.id)

	def compareStates(self, state, statePtr):
		self.assertEqual(state["stateID"], statePtr.id)
		self.assertEqual(state["short_form"], statePtr.short_form)
		self.assertEqual(state["name"], statePtr.name)

	def compareSeller(self, seller, sellerPtr, serialized = 1):
		if serialized or "show_online" in seller or serialized:
			self.assertEqual(seller["show_online"], sellerPtr.show_online)
		if serialized or "alternate_phone_number" in seller or serialized:
			self.assertEqual(seller["alternate_phone_number"], sellerPtr.alternate_phone_number)
		if serialized or "name" in seller or serialized:
			self.assertEqual(seller["name"], sellerPtr.name)
		if serialized or "email_verification" in seller or serialized:
			self.assertEqual(seller["email_verification"], sellerPtr.email_verification)
		if serialized or "created_at" in seller or serialized:
			self.assertEqual(seller["created_at"], djangoEncodedTime(sellerPtr.created_at))
		if serialized or "mobile_verification" in seller or serialized:
			self.assertEqual(seller["mobile_verification"], sellerPtr.mobile_verification)
		if serialized or "concerned_person_number" in seller or serialized:
			self.assertEqual(seller["concerned_person_number"], sellerPtr.concerned_person_number)
		if serialized or "updated_at" in seller:
			self.assertEqual(seller["updated_at"], djangoEncodedTime(sellerPtr.updated_at))
		if serialized or "company_profile" in seller:
			self.assertEqual(seller["company_profile"], sellerPtr.company_profile)
		if serialized or "seller_conditions" in seller:
			self.assertEqual(seller["seller_conditions"], sellerPtr.seller_conditions)
		if serialized or "company_name" in seller:
			self.assertEqual(seller["company_name"], sellerPtr.company_name)
		if serialized or "mobile_number" in seller:
			self.assertEqual(seller["mobile_number"], sellerPtr.mobile_number)
		if serialized or "sellerID" in seller:
			self.assertEqual(seller["sellerID"], sellerPtr.id)
		if serialized or "email" in seller:
			self.assertEqual(seller["email"], sellerPtr.email)
		if serialized or "concerned_person" in seller:
			self.assertEqual(seller["concerned_person"], sellerPtr.concerned_person)

		"""
		def compareSellerDetails(self, seller, sellerPtr, serialized = 1):
			if serialized or "show_online" in seller or serialized:
				self.assertEqual(seller["show_online"], sellerPtr.show_online)
			"pan_verification": true,
          "tin_verification": true,
          "name_on_pan": "",
          "vat_tin": "",
          "detailsID": 1,
          "dob_on_pan": null,
          "cst": "",
          "pan": ""
        """

