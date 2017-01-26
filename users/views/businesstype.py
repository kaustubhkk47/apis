from scripts.utils import customResponse, closeDBConnection, convert_keys_to_string, validate_integer, validate_bool, getArrFromString
import json

from users.models.businessType import *
from users.serializers.businesstype import *

import logging
log = logging.getLogger("django")

def get_business_type_details(request,parameters = {}):
	try:
		businessTypes = filterBusinessType(parameters)

		response = {
			"business_types" : parse_business_type(businessTypes, parameters)
		}
		closeDBConnection()

		return customResponse(200, response)
	except Exception as e:
		log.critical(e)
		return customResponse(500, error_code=0)