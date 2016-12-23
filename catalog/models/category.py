from django.db import models
from django.contrib import admin

from scripts.utils import validate_bool

class Category(models.Model):
	name = models.CharField(max_length=50, blank=False)
	display_name = models.CharField(max_length=50, blank=False)
	slug = models.CharField(max_length=100, blank=True)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	image_url = models.TextField(blank=True)

	priority = models.PositiveIntegerField(default=0)

	delete_status = models.BooleanField(default=False)
	show_online = models.BooleanField(default=True)

	class Meta:
		ordering = ["priority","id"]
		default_related_name = "category"
		verbose_name="Category"
		verbose_name_plural = "Categories"

	def __unicode__(self):
		return "{} - {}".format(self.id,self.display_name)

class CategoryAdmin(admin.ModelAdmin):
	list_display = ["id", "display_name"]


def validateCategoryData(category, oldcategory, is_new):
	flag = 0
	if not "name" in category or category["name"]==None:
		flag = 1
		category["name"] = oldcategory.name
	if not "display_name" in category or category["display_name"]==None:
		if not is_new == 1:
			category["display_name"] = oldcategory.display_name
		else:
			category["display_name"] = category["name"]
	if not "show_online" in category or  not validate_bool(category["show_online"]):
		category["show_online"] = oldcategory.show_online

	if is_new == 1 and flag == 1:
		return False

	return True

def populateCategoryData(categoryPtr, category):
	categoryPtr.name = category["name"]
	categoryPtr.display_name = category["display_name"]
	categoryPtr.show_online = int(category["show_online"])
	categoryPtr.slug = category["slug"]

def filterCategories(parameters):
	categories = Category.objects.filter(delete_status=False)

	if "categoriesArr" in parameters:
		categories = categories.filter(id__in=parameters["categoriesArr"])

	if "category_show_online" in parameters:
		categories = categories.filter(show_online=parameters["category_show_online"])

	return categories