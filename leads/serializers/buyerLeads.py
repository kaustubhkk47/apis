from catalog.serializers.category import serialize_categories
from catalog.serializers.product import serialize_product

def serialize_buyer_lead(buyerlead_entry):

	buyerLead = {
		"buyerleadID" : buyerlead_entry.id,
		"name" : buyerlead_entry.name,
		"email" : buyerlead_entry.email,
		"mobile_number" : buyerlead_entry.mobile_number,
		"status" : buyerlead_entry.status,
		"comments" : buyerlead_entry.comments,
		"created_at" : buyerlead_entry.created_at,
		"updated_at" : buyerlead_entry.updated_at
	}

	try:
		buyerLead["product"] = serialize_product(buyerlead_entry.product)
	except:
		buyerLead["product"] = None

	try:
		buyerLead["category"] = serialize_categories(buyerlead_entry.category)
	except:
		buyerLead["category"] = None

	return buyerLead

def parseBuyerLeads(buyerLeadQuerySet):

	buyerLeads = []

	for buyerLead in buyerLeadQuerySet:
		buyerLeadEntry = serialize_buyer_lead(buyerLead)
		buyerLeads.append(buyerLeadEntry)

	return buyerLeads