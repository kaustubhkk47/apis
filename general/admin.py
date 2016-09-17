from django.contrib import admin

# Register your models here.

from .models.alexastats import *
from .models.smssent import *

admin.site.register(AlexaStats, AlexaStatsAdmin)
admin.site.register(SMSSent, SMSSentAdmin)