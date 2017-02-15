from scripts.utils import *

from django.utils import timezone
import datetime

from ..models.marketing_contacts import *
from ..serializers.marketing_contacts import *

from django.shortcuts import redirect
from django.core.paginator import Paginator
from django.db.models import F

import logging
log = logging.getLogger("django")

def get_marketing_contact_details(request, parameters):
	try:
		marketingContacts = filterMarketingContacts(parameters)

		paginator = Paginator(marketingContacts, parameters["itemsPerPage"])

		try:
			pageItems = paginator.page(parameters["pageNumber"])
		except Exception as e:
			pageItems = []

		body = parse_marketing_contact(pageItems,parameters)
		statusCode = 200
		response = {"marketing_contacts": body}

		responsePaginationParameters(response, paginator, parameters)

	except Exception as e:
		log.critical(e)
		statusCode = 500
		response = {}

	closeDBConnection()
	return customResponse(statusCode, response)

def post_new_marketing_contact(request, parameters):
	try:
		requestbody = request.body.decode("utf-8")
		contacts = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse(400, error_code=4)
	
	if not len(contacts) or not "contacts" in contacts or not isinstance(contacts["contacts"], list) or not len(contacts["contacts"]) > 0:
		return customResponse(400, error_code=5, error_details= "Invalid data sent in request")

	if not validateMarketingContactData(contacts["contacts"]):
		return customResponse(400, error_code=5, error_details="Mobile number not sent")

	try:
		defaultPlayStoreLink = "https://goo.gl/5Mu2vw"
		baseURL = settings.API_BASE_URL + "/buyerapplink/"
		for contact in contacts["contacts"]:
			marketingContactPtr, created = MarketingContact.objects.get_or_create(mobile_number=contact["mobile_number"])
			if created:
				marketingContactPtr.save()
				shortenedURL = getShortenedURL(baseURL + "?contactID=" + str(marketingContactPtr.id))
				if (shortenedURL != None):
					marketingContactPtr.sharing_link = shortenedURL
				else:
					marketingContactPtr.sharing_link = defaultPlayStoreLink
				marketingContactPtr.contact_name = "Script Contact {}".format(marketingContactPtr.id)
				marketingContactPtr.save()

	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse(500, error_code = 1)
	else:
		closeDBConnection()
		return customResponse(200, {"success" : "contacts saved"})

def redirect_to_buyer_app(request, parameters):
	contactID = request.GET.get("contactID", "")

	if contactID != "" and request.method == "GET":
		marketingContactPtr = MarketingContact.objects.filter(id=contactID)
		if len(marketingContactPtr) > 0:
			marketingContactPtr = marketingContactPtr[0]
			if (timezone.now() - marketingContactPtr.created_at) > datetime.timedelta(minutes=5):
				marketingContactPtr.sharing_link_clicks += 1
				marketingContactPtr.sharing_link_click_time = timezone.now()
				marketingContactPtr.save()

	return redirect("https://play.google.com/store/apps/details?id=com.wholdus.www.wholdusbuyerapp", permanent=True)

def update_marketing_contact(request, parameters):
	try:
		requestbody = request.body.decode("utf-8")
		contacts = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse(400, error_code=4)

	if not len(contacts):
		return customResponse(400, error_code=5, error_details= "Invalid data sent in request")

	if not "marketingContactsArr" in parameters:
		return customResponse(400, error_code=5, error_details="Marketing contact ids not sent")

	try:
		updated = False
		parameters.pop("new_contacts")

		if "message_sent" in contacts:
			updated = True
			filterMarketingContacts(parameters).update(message_sent_count=F('message_sent_count') + 1, message_sent_time = timezone.now())

		if "assign_user" in contacts:
			updated = True
			filterMarketingContacts(parameters).update(internal_user_id = parameters["internalusersArr"][0])

		if not updated:
			return customResponse(400, error_code=5, error_details="Invalid data sent in request")

	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse(500, error_code = 1)
	else:
		closeDBConnection()
		return customResponse(200, {"success" : "successfully updated"})

def remove_marketing_contact_user(request, parameters):
	try:
		requestbody = request.body.decode("utf-8")
		contacts = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse(400, error_code=4)

	try:
		MarketingContact.objects.filter(internal_user_id=parameters["internalusersArr"][0]).update(internal_user_id=None)
	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse(500, error_code = 1)
	else:
		closeDBConnection()
		return customResponse(200, {"success" : "successfully removed"})