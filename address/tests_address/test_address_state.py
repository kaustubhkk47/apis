from django.test import TestCase
from unittest import TestCase as uTestCase

class state_test_case(TestCase):

	ADDRESS_FIXTURE = ['country_models_testdata.json', 'state_models_testdata.json', 'city_models_testdata.json','pincode_models_testdata.json']
	fixtures = ADDRESS_FIXTURE

	def test_state_get(self):

		resp = self.client.get('/address/state/')
		self.assertEqual(resp.status_code, 200)
		respJson = resp.json()
		self.assertEqual(respJson["statusCode"], '2XX')
		jsonBody = respJson["body"]
		states = jsonBody["states"]
		self.assertEqual(len(states), 2)
		state1 = states[0]
		self.assertEqual(state1["stateID"], 1)
		self.assertEqual(state1["short_form"], "AN")
		self.assertEqual(state1["name"], "Andaman and Nicobar Islands")
	
	def test_state_post(self):

		resp = self.client.post('/address/state/')
		self.assertEqual(resp.status_code, 200)
		respJson = resp.json()
		self.assertEqual(respJson["statusCode"], '4XX')
		jsonBody = respJson["body"]
		self.assertEqual(jsonBody["error"], "Invalid request")

	def test_state_put(self):

		resp = self.client.put('/address/state/')
		self.assertEqual(resp.status_code, 200)
		respJson = resp.json()
		self.assertEqual(respJson["statusCode"], '4XX')
		jsonBody = respJson["body"]
		self.assertEqual(jsonBody["error"], "Invalid request")

	def test_state_delete(self):

		resp = self.client.delete('/address/state/')
		self.assertEqual(resp.status_code, 200)
		respJson = resp.json()
		self.assertEqual(respJson["statusCode"], '4XX')
		jsonBody = respJson["body"]
		self.assertEqual(jsonBody["error"], "Invalid request")