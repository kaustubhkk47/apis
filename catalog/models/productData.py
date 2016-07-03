from django.db import models

class FabricType(models.Model):

    fabric_type = models.CharField(max_length=100, null=True, blank=True)
    #description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    delete_status = models.BooleanField(default=False)

    def __unicode__(self):
        return str(self.id) + " - " + self.fabric_type


class ColourType(models.Model):

    colour_type = models.CharField(max_length=100, null=True, blank=True)
    #description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    delete_status = models.BooleanField(default=False)

    def __unicode__(self):
        return str(self.id) + " - " + self.colour_type

def filterProductColourType(parameters = {}):

	colourType = ColourType.objects.filter(delete_status=False)

	return colourType

def filterProductFabricType(parameters = {}):

	fabricType = FabricType.objects.filter(delete_status=False)

	return fabricType