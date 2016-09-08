from scripts.utils import customResponse, closeDBConnection, convert_keys_to_string, validate_integer, validate_bool, getArrFromString
import json

from ..models.internalUser import filterInternalUser
from ..serializers.internalUser import parseInternalUser

import logging
log = logging.getLogger("django")

def get_internal_user_details(request,parameters = {}):
	try:
		internalUsers = filterInternalUser(parameters)

		response = {
			"internal_users" : parseInternalUser(internalUsers, parameters)
		}
		closeDBConnection()

		return customResponse("2XX", response)
	except Exception as e:
		log.critical(e)
		return customResponse("4XX", {"error": "Invalid request"})