from django.contrib import admin

# Register your models here.

from .models.alexastats import *

admin.site.register(AlexaStats, AlexaStatsAdmin)