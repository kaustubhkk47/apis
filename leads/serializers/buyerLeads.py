def serialize_buyer_lead(buyerlead_entry):

	buyerLead = {
		"buyerleadID" : buyerlead_entry.id,
		"name" : buyerlead_entry.name,
		"email" : buyerlead_entry.email,
		"mobile_number" : buyerlead_entry.mobile_number
	}

	try:
		buyerLead["productID"] = buyerlead_entry.product.id
	except:
		buyerLead["productID"] = None

	try:
		buyerLead["categoryID"] = buyerlead_entry.category.id
	except:
		buyerLead["categoryID"] = None

	return buyerLead