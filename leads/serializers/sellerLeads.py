def serialize_seller_lead(sellerlead_entry):

	sellerLead = {
		"sellerleadID" : sellerlead_entry.id,
		"company_name" : sellerlead_entry.company_name,
		"email" : sellerlead_entry.email,
		"mobile_number" : sellerlead_entry.mobile_number
	}

	return sellerLead