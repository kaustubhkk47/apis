from catalog.models.category import Category
from scripts.baseTestCases import *

class category_test_case_get(masterTestCase):

	fixtures = CATEGORY_FIXTURE
	BASE_URL = '/category/'

	def test_category_get(self):
		
		result = self.getMethod("categories", {})[0]
		categories = Category.objects.filter(delete_status=False)
		self.assertEqual(len(result), len(categories))

		for i in range(len(result)):
			self.compareCategories(result[i], categories[i])

		result = self.getMethod("categories",{"categoryID":"1"})[0]
		self.assertEqual(len(result), 1)

		result = self.getMethod("categories",{"categoryID":"1,2"})[0]
		self.assertEqual(len(result), 2)

		result = self.getMethod("categories",{"categoryID":"3,4"})[0]
		self.assertEqual(len(result), 1)

		result = self.getMethod("categories",{"categoryID":"10"})[0]
		self.assertEqual(len(result), 0)

		result = self.getMethod("categories",{"categoryID":""})[0]
		self.assertEqual(len(result), 3)

		result = self.getMethod("categories",{"categoryID":"hello"})[0]
		self.assertEqual(len(result), 0)

class category_test_case_post(masterTestCase):

	fixtures = []
	BASE_URL = '/category/'
	METHOD_NAME = "post"

	def test_category_create(self):

		self.blankMethod()

		allKeys = {"name":"New Name", "display_name":"Display Name"}

		tempDict = allKeys.copy()
		tempDict.pop("name")
		error = self.generalMethod("error", {}, "4XX")
		self.assertEqual(error, "Invalid data for category sent")

		tempDict = allKeys.copy()
		tempDict.pop("display_name")
		result = self.generalMethod("categories", tempDict, "2XX")
		categoryPtr = Category.objects.get(id=1)
		tempDict["slug"] = "new-name"
		tempDict["url"] = "new-name-1"
		tempDict["id"] = 1
		self.compareCategories(tempDict, categoryPtr, 0)

		tempDict = allKeys.copy()
		result = self.generalMethod("categories", tempDict, "2XX")
		categoryPtr = Category.objects.get(id=2)
		tempDict["slug"] = "new-name"
		tempDict["url"] = "new-name-2"
		tempDict["id"] = 2
		self.compareCategories(tempDict, categoryPtr, 0)

	
class category_test_case_put(masterTestCase):

	fixtures = CATEGORY_FIXTURE
	BASE_URL = '/category/'
	METHOD_NAME = "put"

	def test_category_update(self):

		self.blankMethod()

		allKeys = {"categoryID":3, "name":"New Name"}

		error = self.generalMethod("error", {}, "4XX")
		self.assertEqual(error, "Id for category not sent")

		error = self.generalMethod("error", {"hello":1}, "4XX")
		self.assertEqual(error, "Id for category not sent")

		error = self.generalMethod("error", {"categoryID":"None"}, "4XX")
		self.assertEqual(error, "Id for category not sent")

		error = self.generalMethod("error", {"categoryID":"5"}, "4XX")
		self.assertEqual(error, "Invalid id for category sent")

		error = self.generalMethod("error", {"categoryID":5}, "4XX")
		self.assertEqual(error, "Invalid id for category sent")

		result = self.generalMethod("categories", {"categoryID":4}, "2XX")
		categoryPtr = Category.objects.get(id=4)
		self.compareCategories(result, categoryPtr)

		tempDict = {"categoryID":3, "name":"New Name"}
		result = self.generalMethod("categories", tempDict, "2XX")
		categoryPtr = Category.objects.get(id=3)
		tempDict["slug"] = "new-name"
		tempDict["url"] = "new-name-3"
		self.compareCategories(tempDict, categoryPtr, 0)

class category_test_case_delete(masterTestCase):

	fixtures = CATEGORY_FIXTURE
	BASE_URL = '/category/'
	METHOD_NAME = "delete"

	def test_category_delete(self):

		self.blankMethod()

		error = self.generalMethod("error", {}, "4XX")
		self.assertEqual(error, "Id for category not sent")

		error = self.generalMethod("error", {"hello":1}, "4XX")
		self.assertEqual(error, "Id for category not sent")

		error = self.generalMethod("error", {"categoryID":"None"}, "4XX")
		self.assertEqual(error, "Id for category not sent")

		error = self.generalMethod("error", {"categoryID":"5"}, "4XX")
		self.assertEqual(error, "Invalid id for category sent")

		error = self.generalMethod("error", {"categoryID":5}, "4XX")
		self.assertEqual(error, "Invalid id for category sent")

		error = self.generalMethod("error", {"categoryID":4}, "4XX")
		self.assertEqual(error, "Already deleted")

		success = self.generalMethod("success", {"categoryID":3}, "2XX")
		self.assertEqual(success, "category deleted")

		categories = self.getMethod("categories")[0]
		self.assertEqual(len(categories), 2)
