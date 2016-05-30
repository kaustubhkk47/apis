def serialize_seller_lead(sellerlead_entry):

	sellerLead = {
		"sellerleadID" : sellerlead_entry.id,
		"company_name" : sellerlead_entry.company_name,
		"email" : sellerlead_entry.email,
		"mobile_number" : sellerlead_entry.mobile_number,
		"status" : sellerlead_entry.status,
		"comments" : sellerlead_entry.comments,
		"created_at" : sellerlead_entry.created_at,
		"updated_at" : sellerlead_entry.updated_at
	}

	return sellerLead

def parseSellerLeads(sellerLeadQuerySet):

	sellerLeads = []

	for sellerLead in sellerLeadQuerySet:
		sellerLeadEntry = serialize_seller_lead(sellerLead)
		sellerLeads.append(sellerLeadEntry)

	return sellerLeads