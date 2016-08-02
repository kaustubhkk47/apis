from django.test import TestCase
from unittest import TestCase as uTestCase

class category_test_case_get(TestCase):

	CATEGORY_FIXTURE = ['category_models_testdata.json']
	fixtures = CATEGORY_FIXTURE

	def test_category_get_all(self):

		resp = self.client.get('/category/')
		self.assertEqual(resp.status_code, 200)
		respJson = resp.json()
		self.assertEqual(respJson["statusCode"], '2XX')
		jsonBody = respJson["body"]
		categories = jsonBody["categories"]
		self.assertEqual(len(categories), 3)

		category1 = categories[0]
		self.assertEqual(category1["display_name"], "Sarees")
		self.assertEqual(category1["name"], "Sarees")
		self.assertEqual(category1["url"], "sarees-3")
		self.assertEqual(category1["slug"], "sarees")
		self.assertEqual(category1["id"], 3)
		self.assertEqual(category1["categoryID"], 3)

		category2 = categories[1]
		self.assertEqual(category2["display_name"], "Kurtis")
		self.assertEqual(category2["name"], "Kurtis")
		self.assertEqual(category2["url"], "kurtis-1")
		self.assertEqual(category2["slug"], "kurtis")
		self.assertEqual(category2["id"], 1)
		self.assertEqual(category2["categoryID"], 1)

	def test_category_get_specific(self):

		resp = self.client.get('/category/?categoryID=1')
		self.assertEqual(resp.status_code, 200)
		respJson = resp.json()
		self.assertEqual(respJson["statusCode"], '2XX')
		jsonBody = respJson["body"]
		categories = jsonBody["categories"]
		self.assertEqual(len(categories), 1)

		resp = self.client.get('/category/?categoryID=1,2')
		self.assertEqual(resp.status_code, 200)
		respJson = resp.json()
		self.assertEqual(respJson["statusCode"], '2XX')
		jsonBody = respJson["body"]
		categories = jsonBody["categories"]
		self.assertEqual(len(categories), 2)

		resp = self.client.get('/category/?categoryID=3,4')
		self.assertEqual(resp.status_code, 200)
		respJson = resp.json()
		self.assertEqual(respJson["statusCode"], '2XX')
		jsonBody = respJson["body"]
		categories = jsonBody["categories"]
		self.assertEqual(len(categories), 1)

		resp = self.client.get('/category/?categoryID=10')
		self.assertEqual(resp.status_code, 200)
		respJson = resp.json()
		self.assertEqual(respJson["statusCode"], '2XX')
		jsonBody = respJson["body"]
		categories = jsonBody["categories"]
		self.assertEqual(len(categories), 0)

		resp = self.client.get('/category/?categoryID=')
		self.assertEqual(resp.status_code, 200)
		respJson = resp.json()
		self.assertEqual(respJson["statusCode"], '2XX')
		jsonBody = respJson["body"]
		categories = jsonBody["categories"]
		self.assertEqual(len(categories), 3)

		resp = self.client.get('/category/?categoryID=hello')
		self.assertEqual(resp.status_code, 200)
		respJson = resp.json()
		self.assertEqual(respJson["statusCode"], '2XX')
		jsonBody = respJson["body"]
		categories = jsonBody["categories"]
		self.assertEqual(len(categories), 0)
"""
class category_test_case_post(TestCase):

	CATEGORY_FIXTURE = ['category_models_testdata.json']
	fixtures = CATEGORY_FIXTURE
	
	def test_state_url_post(self):

		resp = self.client.post('/address/state/')
		self.assertEqual(resp.status_code, 200)
		respJson = resp.json()
		self.assertEqual(respJson["statusCode"], '4XX')
		jsonBody = respJson["body"]
		self.assertEqual(jsonBody["error"], "Invalid request")

class category_test_case_put(TestCase):

	CATEGORY_FIXTURE = ['category_models_testdata.json']
	fixtures = CATEGORY_FIXTURE

	def test_state_url_put(self):

		resp = self.client.put('/address/state/')
		self.assertEqual(resp.status_code, 200)
		respJson = resp.json()
		self.assertEqual(respJson["statusCode"], '4XX')
		jsonBody = respJson["body"]
		self.assertEqual(jsonBody["error"], "Invalid request")
"""

class category_test_case_delete(TestCase):

	CATEGORY_FIXTURE = ['category_models_testdata.json']
	fixtures = CATEGORY_FIXTURE

	def test_category_delete(self):

		resp = self.client.delete('/category/')
		self.assertEqual(resp.status_code, 200)
		respJson = resp.json()
		self.assertEqual(respJson["statusCode"], '4XX')
		jsonBody = respJson["body"]
		self.assertEqual(jsonBody["error"], "Invalid data sent in request")