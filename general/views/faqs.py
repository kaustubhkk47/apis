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

def get_privacy_policy_details(request):
	try:
		privacyPolicy = PrivacyPolicy.objects.all()

		body = ""
		if len(privacyPolicy) != 0:
			privacyPolicy = privacyPolicy[0]
			body = privacyPolicy.text
		
		statusCode = 200
		response = {"privacy_policy": body}
	except Exception as e:
		log.critical(e)
		statusCode = 500
		response = {}

	closeDBConnection()
	return customResponse(statusCode, response, error_code=0)

def get_about_us_details(request):
	try:
		aboutUs = AboutUs.objects.all()

		body = ""
		if len(aboutUs) != 0:
			aboutUs = aboutUs[0]
			body = aboutUs.text
		
		statusCode = 200
		response = {"about_us": body}
	except Exception as e:
		log.critical(e)
		statusCode = 500
		response = {}

	closeDBConnection()
	return customResponse(statusCode, response, error_code=0)

def get_terms_and_conditions_details(request):
	try:
		tandc = TermsAndConditions.objects.all()

		body = ""
		if len(tandc) != 0:
			tandc = tandc[0]
			body = tandc.text
		
		statusCode = 200
		response = {"terms_and_conditions": body}
	except Exception as e:
		log.critical(e)
		statusCode = 500
		response = {}

	closeDBConnection()
	return customResponse(statusCode, response, error_code=0)