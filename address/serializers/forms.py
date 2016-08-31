def parse_form(formQuerySet):
	forms = []
	for formsItem in formQuerySet:
		form = serialize_form(formsItem)
		forms.append(form)
	return forms

def serialize_form(formItem):

	form = {}

	form["formID"] = formItem.id
	form["name"] = formItem.name
	form["min_amount"] = formItem.min_amount
	form["availability"] = formItem.availability

	return form