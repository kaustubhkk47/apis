from scripts.utils import *
import json

from ..models.buyerLeads import *
from ..serializers.buyerLeads import *
from catalog.models.product import Product
from catalog.models.category import Category

import logging
log = logging.getLogger("django")

def get_buyer_leads(request, buyerLeadParameters):
	try:
		buyerLeads = BuyerLeads.objects.all().select_related('product','category','product__seller')
		if "buyerLeadsArr" in buyerLeadParameters:
			buyerLeads = buyerLeads.filter(id__in=buyerLeadParameters["buyerLeadsArr"])

		if "statusArr" in buyerLeadParameters:
			buyerLeads = buyerLeads.filter(status__in=buyerLeadParameters["statusArr"])
		body = parseBuyerLeads(buyerLeads)
		statusCode = 200
		response = {"buyer_leads": body}
	except Exception, e:
		log.critical(e)
		statusCode = 500
		response = {}

	closeDBConnection()
	return customResponse(statusCode, response, error_code=0)

def post_new_buyer_lead(request):
	try:
		requestbody = request.body.decode("utf-8")
		buyerLead = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse(400, error_code=4)

	if not len(buyerLead) or not validateBuyerLeadData(buyerLead, BuyerLeads(), 1):
		return customResponse(400, error_code=5, error_details= "Invalid data for buyerLead sent")

	try:
		newBuyerLead = BuyerLeads()

		populateBuyerLead(newBuyerLead, buyerLead)

		if "productID" in buyerLead and validate_integer(buyerLead["productID"]):
			productPtr = Product.objects.filter(id=int(buyerLead["productID"]))

			if len(productPtr) == 0:
				return customResponse(400, error_code=6, error_details =  "invalid product id sent")

			productPtr = productPtr[0]
				
			newBuyerLead.product_id = int(buyerLead["productID"])

		if "categoryID" in buyerLead and validate_integer(buyerLead["categoryID"]):
			categoryPtr = Category.objects.filter(id=int(buyerLead["categoryID"]))

			if not categoryPtr.exists():
				return customResponse(400, error_code=6, error_details = "invalid category id sent")
				
			newBuyerLead.category_id = int(buyerLead["categoryID"])

		newBuyerLead.save()
	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse(500, error_code = 1)
	else:
		

		if("email" in buyerLead and buyerLead["email"] and validate_email(buyerLead["email"])):
			mail_template_file = "leads/buyer_lead.html"
			mail_dict = {}
			subject = "We at Wholdus have received your request"
			to = [buyerLead["email"]]
			from_email = "Wholdus Info <info@wholdus.com>"
			bcc = ["manish@wholdus.com","kushagra@wholdus.com"]
			
			if newBuyerLead.product_id != None:
				mail_dict["product_name"] = newBuyerLead.product.display_name
				mail_dict["product_link"] = productPtr.get_absolute_url()
				mail_dict["image_link"] = productPtr.get_image_url(400)

			if newBuyerLead.category_id != None:
				mail_dict["category_name"] = newBuyerLead.category.display_name

			mail_dict["mobile_number"] = buyerLead["mobile_number"]
			mail_dict["name"] = buyerLead["name"]

			create_email(mail_template_file,mail_dict,subject,from_email,to,bcc=bcc)

		closeDBConnection()

		return customResponse(200, {"buyer_lead" : serialize_buyer_lead(newBuyerLead)})

def update_buyer_lead(request):
	try:
		requestbody = request.body.decode("utf-8")
		buyerLead = convert_keys_to_string(json.loads(requestbody))
	except Exception as e:
		return customResponse(400, error_code=4)

	if not len(buyerLead) or not "buyerleadID" in buyerLead or not validate_integer(buyerLead["buyerleadID"]):
		return customResponse(400, error_code=5,  error_details= "Id for buyer lead not sent")

	buyerLeadPtr = BuyerLeads.objects.filter(id=int(buyerLead["buyerleadID"]))

	if len(buyerLeadPtr) == 0:
		return customResponse(400, error_code=6, error_details = "Invalid id for buyer lead sent")

	buyerLeadPtr = buyerLeadPtr[0]

	if not validateBuyerLeadData(buyerLead, buyerLeadPtr, 0):
		return customResponse(400, error_code=5, error_details= "Invalid data for buyerLead sent")

	try:
		populateBuyerLead(buyerLeadPtr, buyerLead)
		buyerLeadPtr.save()

	except Exception as e:
		log.critical(e)
		closeDBConnection()
		return customResponse(500, error_code = 3)
	else:
		closeDBConnection()
		return customResponse(200, {"buyer_lead" : serialize_buyer_lead(buyerLeadPtr)})