from scripts.utils import customResponse, closeDBConnection, convert_keys_to_string
import json

from ..serializers.pincodeserviceability import *
from ..models.serviceability import *

import logging
log = logging.getLogger("django")

def get_pincode_serviceability_details(request,parameters = {}):
	try:
		serviceable_pincodes = filterServiceablePincodes(parameters)

		paginator = Paginator(serviceable_pincodes, parameters["itemsPerPage"])

		try:
			pageItems = paginator.page(parameters["pageNumber"])
		except Exception as e:
			pageItems = []


		body = parseCart(pageItems,parameters)

		response = responsePaginationParameters(response, paginator, parameters)

		closeDBConnection()

		return customResponse("2XX", response)
	except Exception as e:
		log.critical(e)
		return customResponse("4XX", {"error": "Invalid request"})