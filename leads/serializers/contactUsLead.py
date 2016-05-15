def serialize_contactus_lead(contactUslead_entry):

	contactUsLead = {
		"contact_us_leadID" : contactUslead_entry.id,
		"remarks" : contactUslead_entry.remarks,
		"email" : contactUslead_entry.email,
		"mobile_number" : contactUslead_entry.mobile_number
	}

	return contactUsLead