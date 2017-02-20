from django.contrib import admin

# Register your models here.

from .models.alexastats import *
from .models.smssent import *
from .models.faqs import *
from .models.configuration import *
from .models.marketing_contacts import *

admin.site.register(AlexaStats, AlexaStatsAdmin)

admin.site.register(SMSSent, SMSSentAdmin)

admin.site.register(FAQEntry)
admin.site.register(TermsAndConditions)
admin.site.register(AboutUs)
admin.site.register(PrivacyPolicy)

admin.site.register(CartMinValue)
admin.site.register(CartSellerMinPieces)

admin.site.register(MarketingContact, MarketingContactAdmin)
