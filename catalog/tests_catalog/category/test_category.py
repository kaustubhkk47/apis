from django.test import TestCase
from unittest import TestCase as uTestCase
import json
from catalog.models.category import Category

class category_test_case_get(TestCase):

	CATEGORY_FIXTURE = ['category_models_testdata.json']
	fixtures = CATEGORY_FIXTURE

	def setUp(self):
		self.BASE_URL = '/category/'

	def test_category_get_all(self):
		
		jsonBody = self.getMethod()
		categories = jsonBody["categories"]
		self.assertEqual(len(categories), 3)

		category1 = categories[0]
		categoryPtr = Category.objects.get(id=3)
		self.compareCategories(category1, categoryPtr)

		category2 = categories[1]
		categoryPtr = Category.objects.get(id=1)
		self.compareCategories(category2, categoryPtr)

	def test_category_get_specific(self):
		
		jsonBody = self.getMethod({"categoryID":"1"})
		categories = jsonBody["categories"]
		self.assertEqual(len(categories), 1)

		jsonBody = self.getMethod({"categoryID":"1,2"})
		categories = jsonBody["categories"]
		self.assertEqual(len(categories), 2)

		jsonBody = self.getMethod({"categoryID":"3,4"})
		categories = jsonBody["categories"]
		self.assertEqual(len(categories), 1)

		jsonBody = self.getMethod({"categoryID":"10"})
		categories = jsonBody["categories"]
		self.assertEqual(len(categories), 0)

		jsonBody = self.getMethod({"categoryID":""})
		categories = jsonBody["categories"]
		self.assertEqual(len(categories), 3)

		jsonBody = self.getMethod({"categoryID":"hello"})
		categories = jsonBody["categories"]
		self.assertEqual(len(categories), 0)

	def getMethod(self, parameters = {}):
		resp = self.client.get(self.BASE_URL, parameters)
		self.assertEqual(resp.status_code, 200)
		respJson = resp.json()
		self.assertEqual(respJson["statusCode"], '2XX')
		jsonBody = respJson["body"]
		return jsonBody

	def compareCategories(self, category, categoryPtr):
		self.assertEqual(category["display_name"], categoryPtr.display_name)
		self.assertEqual(category["name"], categoryPtr.name)
		self.assertEqual(category["url"], "{}-{}".format(categoryPtr.slug, categoryPtr.id))
		self.assertEqual(category["slug"], categoryPtr.slug)
		self.assertEqual(category["id"], categoryPtr.id)
		self.assertEqual(category["categoryID"], categoryPtr.id)
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

"""

class category_test_case_put(TestCase):

	CATEGORY_FIXTURE = ['category_models_testdata.json']
	fixtures = CATEGORY_FIXTURE

	def test_category_update(self):

		resp = self.client.put('/category/')
		self.assertEqual(resp.status_code, 200)
		respJson = resp.json()
		self.assertEqual(respJson["statusCode"], '4XX')
		jsonBody = respJson["body"]
		self.assertEqual(jsonBody["error"], "Invalid data sent in request")

		jsonStr = json.dumps({})
		resp = self.client.put('/category/', data= jsonStr, content_type='application/json')
		self.assertEqual(resp.status_code, 200)
		respJson = resp.json()
		self.assertEqual(respJson["statusCode"], '4XX')
		jsonBody = respJson["body"]
		self.assertEqual(jsonBody["error"], "Id for category not sent")

		jsonStr = json.dumps({"hello":1})
		resp = self.client.put('/category/', data= jsonStr, content_type='application/json')
		self.assertEqual(resp.status_code, 200)
		respJson = resp.json()
		self.assertEqual(respJson["statusCode"], '4XX')
		jsonBody = respJson["body"]
		self.assertEqual(jsonBody["error"], "Id for category not sent")

		jsonStr = json.dumps({"categoryID":"None"})
		resp = self.client.put('/category/', data= jsonStr, content_type='application/json')
		self.assertEqual(resp.status_code, 200)
		respJson = resp.json()
		self.assertEqual(respJson["statusCode"], '4XX')
		jsonBody = respJson["body"]
		self.assertEqual(jsonBody["error"], "Id for category not sent")

		jsonStr = json.dumps({"categoryID":"5"})
		resp = self.client.put('/category/', data= jsonStr, content_type='application/json')
		self.assertEqual(resp.status_code, 200)
		respJson = resp.json()
		self.assertEqual(respJson["statusCode"], '4XX')
		jsonBody = respJson["body"]
		self.assertEqual(jsonBody["error"], "Invalid id for category sent")

		jsonStr = json.dumps({"categoryID":5})
		resp = self.client.put('/category/', data= jsonStr, content_type='application/json')
		self.assertEqual(resp.status_code, 200)
		respJson = resp.json()
		self.assertEqual(respJson["statusCode"], '4XX')
		jsonBody = respJson["body"]
		self.assertEqual(jsonBody["error"], "Invalid id for category sent")

		jsonStr = json.dumps({"categoryID":5})
		resp = self.client.put('/category/', data= jsonStr, content_type='application/json')
		self.assertEqual(resp.status_code, 200)
		respJson = resp.json()
		self.assertEqual(respJson["statusCode"], '4XX')
		jsonBody = respJson["body"]
		self.assertEqual(jsonBody["error"], "Invalid id for category sent")

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

		jsonStr = json.dumps({})
		resp = self.client.delete('/category/', data= jsonStr, content_type='application/json')
		self.assertEqual(resp.status_code, 200)
		respJson = resp.json()
		self.assertEqual(respJson["statusCode"], '4XX')
		jsonBody = respJson["body"]
		self.assertEqual(jsonBody["error"], "Id for category not sent")

		jsonStr = json.dumps({"hello":1})
		resp = self.client.delete('/category/', data= jsonStr, content_type='application/json')
		self.assertEqual(resp.status_code, 200)
		respJson = resp.json()
		self.assertEqual(respJson["statusCode"], '4XX')
		jsonBody = respJson["body"]
		self.assertEqual(jsonBody["error"], "Id for category not sent")

		jsonStr = json.dumps({"categoryID":"None"})
		resp = self.client.delete('/category/', data= jsonStr, content_type='application/json')
		self.assertEqual(resp.status_code, 200)
		respJson = resp.json()
		self.assertEqual(respJson["statusCode"], '4XX')
		jsonBody = respJson["body"]
		self.assertEqual(jsonBody["error"], "Id for category not sent")

		jsonStr = json.dumps({"categoryID":"5"})
		resp = self.client.delete('/category/', data= jsonStr, content_type='application/json')
		self.assertEqual(resp.status_code, 200)
		respJson = resp.json()
		self.assertEqual(respJson["statusCode"], '4XX')
		jsonBody = respJson["body"]
		self.assertEqual(jsonBody["error"], "Invalid id for category sent")

		jsonStr = json.dumps({"categoryID":5})
		resp = self.client.delete('/category/', data= jsonStr, content_type='application/json')
		self.assertEqual(resp.status_code, 200)
		respJson = resp.json()
		self.assertEqual(respJson["statusCode"], '4XX')
		jsonBody = respJson["body"]
		self.assertEqual(jsonBody["error"], "Invalid id for category sent")

		jsonStr = json.dumps({"categoryID":4})
		resp = self.client.delete('/category/', data= jsonStr, content_type='application/json')
		self.assertEqual(resp.status_code, 200)
		respJson = resp.json()
		self.assertEqual(respJson["statusCode"], '4XX')
		jsonBody = respJson["body"]
		self.assertEqual(jsonBody["error"], "Already deleted")

		jsonStr = json.dumps({"categoryID":3})
		resp = self.client.delete('/category/', data= jsonStr, content_type='application/json')
		self.assertEqual(resp.status_code, 200)
		respJson = resp.json()
		self.assertEqual(respJson["statusCode"], '2XX')
		jsonBody = respJson["body"]
		self.assertEqual(jsonBody["success"], "category deleted")

		resp = self.client.get('/category/')
		self.assertEqual(resp.status_code, 200)
		respJson = resp.json()
		self.assertEqual(respJson["statusCode"], '2XX')
		jsonBody = respJson["body"]
		categories = jsonBody["categories"]
		self.assertEqual(len(categories), 2)
