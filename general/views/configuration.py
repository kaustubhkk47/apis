from ..models.configuration import *
from scripts.utils import customResponse, closeDBConnection

import logging
log = logging.getLogger("django")

def get_cart_min_value_details(request):
	try:
		cartMinValue = CartMinValue.objects.all()

		body = 2000
		if len(cartMinValue) != 0:
			cartMinValue = cartMinValue[0]
			body = cartMinValue.value
		
		statusCode = 200
		response = {"cart_min_value": body}
	except Exception as e:
		log.critical(e)
		statusCode = 500
		response = {}

	closeDBConnection()
	return customResponse(statusCode, response, error_code=0)


def get_cart_seller_min_pieces_details(request):
	try:
		cartSellerMinPieces = CartSellerMinPieces.objects.all()

		body = 5
		if len(cartSellerMinPieces) != 0:
			cartSellerMinPieces = cartSellerMinPieces[0]
			body = cartSellerMinPieces.value

		statusCode = 200
		response = {"cart_seller_min_pieces": body}
	except Exception as e:
		log.critical(e)
		statusCode = 500
		response = {}

	closeDBConnection()
	return customResponse(statusCode, response, error_code=0)