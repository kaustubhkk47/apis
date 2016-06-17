from django.db import models

class BusinessType(models.Model):

    business_type = models.CharField(max_length=30)
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return str(self.id) + " - " + self.business_type