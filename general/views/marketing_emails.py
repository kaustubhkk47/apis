from scripts.utils import *

from ..models.marketing_emails import *

import logging
log = logging.getLogger("django")

def unsubscribe_marketing_email(request, parameters):

	try:
		marketingEmailID = request.GET.get("marketingemailID","")
		if marketingEmailID != "" and validate_integer(marketingEmailID):
			marketingEmailPtr = MarketingEmail.objects.filter(id=int(marketingEmailID))
			if len(marketingEmailPtr) > 0:
				marketingEmailPtr = marketingEmailPtr[0]
				marketingEmailPtr.unsubscribed = True
				marketingEmailPtr.save()

	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse(500, error_code = 1)
	else:
		closeDBConnection()
		return customResponse(200, {"success" : "You have unsubscribed successfully from the mailing list"})