from scripts.utils import customResponse, closeDBConnection, convert_keys_to_string
import json

from ..serializers.state import parse_state
from ..models.state import filterState

import logging
log = logging.getLogger("django")

def get_state_details(request,stateParameters):
	try:
		states = filterState(stateParameters)

		response = {
			"states" : parse_state(states)
		}
		closeDBConnection()

		return customResponse(200, response)
	except Exception as e:
		log.critical(e)
		return customResponse(500, error_code=0)