from django.db import models
from django.contrib import admin

class Category(models.Model):
    name = models.CharField(max_length=50, blank=False)
    display_name = models.CharField(max_length=50, blank=False)
    slug = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    priority = models.PositiveIntegerField(default=0)

    delete_status = models.BooleanField(default=False)

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
        flag = 1
        if is_new == 1:
            pass
        else:
            category["display_name"] = oldcategory.display_name

    if is_new == 1 and flag == 1:
        return False

    return True

def populateCategoryData(categoryPtr, category):
	categoryPtr.name = category["name"]
	categoryPtr.display_name = category["display_name"]
	categoryPtr.slug = category["slug"]