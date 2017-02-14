def serialize_marketing_contact(marketing_contact_entry, parameters = {}):
	marketing_contact = {}

	marketing_contact["marketingcontactID"] = marketing_contact_entry.id
	marketing_contact["mobile_number"] = marketing_contact_entry.mobile_number
	marketing_contact["contact_name"] = marketing_contact_entry.contact_name
	marketing_contact["sharing_link"] = marketing_contact_entry.sharing_link

	return marketing_contact

def parse_marketing_contact(marketing_contact_queryset, parameters = {}):

	marketing_contacts = []

	for marketing_contact in marketing_contact_queryset:
		marketing_contacts.append(serialize_marketing_contact(marketing_contact, parameters))

	return marketing_contacts