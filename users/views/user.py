from scripts.utils import customResponse, closeDBConnection

from ..models.buyer import Buyer, BuyerAddress
from ..models.seller import Seller, SellerAddress
from ..serializers.buyer import parse_buyer
from ..serializers.seller import parse_seller

import logging
log = logging.getLogger("django")

def get_user_details(request):
	try:
		buyers = Buyer.objects.filter(delete_status=False).select_related('buyerdetails')
		sellers = Seller.objects.filter(delete_status=False).select_related('sellerdetails')

		closeDBConnection()

		response = {
			"buyers" : parse_buyer(buyers),
			"sellers" : parse_seller(sellers)
		}

		return customResponse(200, {"users": response})
	except Exception as e:
		log.critical(e)
		return customResponse(500)