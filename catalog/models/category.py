from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=50, blank=False)
    display_name = models.CharField(max_length=50, blank=False)
    slug = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    delete_status = models.BooleanField(default=False)

    def __unicode__(self):
        return self.display_name


def validateCategoryData(category, oldcategory, is_new):
    flag = 0
    if not "name" in category or not category["name"]:
        flag = 1
        category["name"] = oldcategory.name
    if not "display_name" in category or not category["display_name"]:
        flag = 1
        category["display_name"] = oldcategory.display_name
    if not "slug" in category or not category["slug"]:
        category["slug"] = oldcategory.slug

    if is_new == 1 and flag == 1:
        return False

    return True

def populateCategoryData(categoryPtr, category):
	categoryPtr.name = category["name"]
	categoryPtr.display_name = category["display_name"]
	categoryPtr.slug = category["slug"]
    
