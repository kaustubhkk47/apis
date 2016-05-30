from scripts.utils import *
import json

from ..models.buyerLeads import *
from ..serializers.buyerLeads import *
from catalog.models.product import Product
from catalog.models.category import Category

def get_buyer_leads(request):
	try:
		buyerLeads = BuyerLeads.objects.all()
		closeDBConnection()
		body = parseBuyerLeads(buyerLeads)
		statusCode = "2XX"
		response = {"buyer_leads": body}
	except Exception, e:
		statusCode = "4XX"
		response = {"error": "Invalid request"}
	return customResponse(statusCode, response)

def post_new_buyer_lead(request):
	try:
		requestbody = request.body.decode("utf-8")
		buyerLead = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse("4XX", {"error": "Invalid data sent in request"})

	if not len(buyerLead) or not validateBuyerLeadData(buyerLead, BuyerLeads(), 1):
		return customResponse("4XX", {"error": "Invalid data for buyer lead sent"})

	try:
		newBuyerLead = BuyerLeads()

		populateBuyerLead(newBuyerLead, buyerLead)

		if "productID" in buyerLead and buyerLead["productID"]!=None:
			productPtr = Product.objects.filter(id=buyerLead["productID"])

			if len(productPtr) == 0:
				return customResponse("4XX", {"error": "invalid product id sent"})
				
			productPtr = productPtr[0]
			newBuyerLead.product = productPtr

		if "categoryID" in buyerLead and buyerLead["categoryID"]!=None:
			categoryPtr = Category.objects.filter(id=buyerLead["categoryID"])

			if len(categoryPtr) == 0:
				return customResponse("4XX", {"error": "invalid category id sent"})
				
			categoryPtr = categoryPtr[0]
			newBuyerLead.category = categoryPtr

		newBuyerLead.save()
	except Exception as e:
		closeDBConnection()
		return customResponse("4XX", {"error": "unable to create entry in db"})
	else:
		closeDBConnection()

		if("email" in buyerLead and buyerLead["email"]):
			mail_template_file = "leads/buyer_lead.html"
			mail_dict = {}
			subject = "We at Wholdus have received your request"
			to = [buyerLead["email"]]
			from_email = "info@wholdus.com"
			create_email(mail_template_file,mail_dict,subject,from_email,to)

		return customResponse("2XX", {"buyer_lead" : serialize_buyer_lead(newBuyerLead)})