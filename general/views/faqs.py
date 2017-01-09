from ..models.faqs import *
from ..serializers.faqs import *
from scripts.utils import customResponse, closeDBConnection

import logging
log = logging.getLogger("django")

def get_faq_details(request):
	try:
		faqentries = FAQEntry.objects.all().order_by('topic')

		body = []
		last_topic = None
		for faqentry in faqentries:
			if last_topic != faqentry.topic:
				body.append({"topic": faqentry.topic, "faqentries": []})
				last_topic = faqentry.topic

			body[len(body) - 1]["faqentries"].append(serialize_faq_entry(faqentry))
		
		statusCode = 200
		response = {"faqs": body}
	except Exception as e:
		log.critical(e)
		statusCode = 500
		response = {}

	closeDBConnection()
	return customResponse(statusCode, response, error_code=0)