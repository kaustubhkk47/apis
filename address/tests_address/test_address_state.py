from scripts.baseTestCases import *
from address.models.state import State

class state_test_case_get(masterTestCase):

	fixtures = ADDRESS_FIXTURE
	BASE_URL = '/address/state/'

	def test_state_get(self):

		states = self.getMethod("states",{})[0]
		self.assertEqual(len(states), 2)
		state1 = states[0]
		statePtr = State.objects.get(id=1)
		self.compareStates(state1, statePtr)

class state_test_case_post(masterTestCase):

	fixtures = []
	BASE_URL = '/address/state/'
	METHOD_NAME = "post"
	
	def test_state_post(self):

		self.blankMethod("Invalid request")

class state_test_case_put(masterTestCase):

	fixtures = []
	BASE_URL = '/address/state/'
	METHOD_NAME = "put"

	def test_state_put(self):

		self.blankMethod("Invalid request")

class state_test_case_delete(masterTestCase):

	fixtures = []
	BASE_URL = '/address/state/'
	METHOD_NAME = "delete"

	def test_state_delete(self):

		self.blankMethod("Invalid request")