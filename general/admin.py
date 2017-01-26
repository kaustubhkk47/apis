from django.contrib import admin

# Register your models here.

from .models.alexastats import *
from .models.smssent import *
from .models.faqs import *

admin.site.register(AlexaStats, AlexaStatsAdmin)
admin.site.register(SMSSent, SMSSentAdmin)
admin.site.register(FAQEntry)
admin.site.register(TermsAndConditions)
admin.site.register(AboutUs)
admin.site.register(PrivacyPolicy)
