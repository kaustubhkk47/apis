from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=50, blank=False)
    display_name = models.CharField(max_length=50, blank=False)
    slug = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.display_name
