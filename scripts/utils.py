from django.http import JsonResponse
from django.db import connection
from django.core import urlresolvers
import datetime
import jwt as JsonWebToken
import settings
import os
import re
import csv
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
import json

from django.core.mail import EmailMessage
#from django.template import Context
from django.template.loader import get_template
from django.core.files import File
import pdfkit
import io

def closeDBConnection():
	connection.close()

def customResponse(statusCode, body):
	response = {}
	response["statusCode"] = statusCode
	response["body"] = body

	return JsonResponse(response)

def convert_keys_to_string(dictionary):
	"""Recursively converts dictionary keys to strings."""
	if not isinstance(dictionary, dict):
		return dictionary
	return dict((str(k), convert_keys_to_string(v))
		for k, v in dictionary.items())

def validate_date(date_text):
	try:
		datetime.datetime.strptime(date_text, '%Y-%m-%d')
	except ValueError:
		return False

	return True

def validate_date_time(date_text):
	try:
		datetime.datetime.strptime(date_text, '%Y-%m-%d %H:%M:%S.%f')
	except ValueError:
		return False

	return True

def validate_integer(x):
	try:
		x = int(x)
	except Exception, e:
		return False
	return True

def getArrFromString(strArr):
	strArr = str(strArr)
	return [int(e) for e in strArr.split(",") if validate_integer(e)]

def getStrArrFromString(strArr):
	return [str(e).strip() for e in strArr.split(",")]

def validate_number(x):
	try:
		x = float(x)
	except Exception, e:
		return False
	return True

def validate_mobile_number(x):
	x = str(x)
	if len(x) != 10:
		return False
	if not (x[0] == '9' or x[0] == '8' or x[0] == '7'):
		return False
	return True

def validate_email(x):
	if not re.match(r"[^@]+@[^@]+\.[^@]+", x):
		return False
	return True

def validate_bool(x):
	if not validate_integer(x) or not (int(x)==1 or int(x)==0):
		return False
	return True

def validate_pincode(x):
	if not validate_integer(x) or not len(x) == 6:
		return False
	return True

def check_token_validity(access_token):
	if not access_token:
		## log the exception into db
		return {}
	try:
		tokenPayload = JsonWebToken.decode(access_token, settings.SECRET_KEY, algorithms=['HS256'])
	except Exception as ex:
		## log the exception into db
		return {}

	return tokenPayload


def get_token_payload(access_token, userID):
	tokenPayload = check_token_validity(access_token)

	if not "user" in tokenPayload or not userID in tokenPayload:
		return {}

	return tokenPayload

def create_email(mail_template_file,mail_dict,subject,from_email,to,attachment="",bcc=[]):
	mail_template = get_template(mail_template_file)   
	#mail_context = Context(mail_dict)
	html_message = mail_template.render(mail_dict)
		
	email = EmailMessage(subject=subject,body=html_message,from_email=from_email,to=to,bcc=bcc)

	if (attachment != "" and os.path.isfile(attachment)):
		email.attach_file(attachment)

	email.content_subtype = "html"
	email.send(fail_silently=True)

def generate_pdf(template_src, context_dict, output_directory, output_file_name):
	template = get_template(template_src)
	html  = template.render(context_dict)

	if not os.path.exists(output_directory):
		os.makedirs(output_directory)

	filename = os.path.join(output_directory,output_file_name)

	options = {
	'quiet': '',
	'margin-top': '0in',
	'margin-right': '0in',
	'margin-bottom': '0in',
	'margin-left': '0in',
	'no-outline': None,
	}

	config = pdfkit.configuration(wkhtmltopdf=settings.WKHTMLTOPDFPATH)

	pdfkit.from_string(html, filename, options=options, configuration=config)

def save_file_from_request(request, output_directory, output_file_name):
	if not os.path.exists(output_directory):
		os.makedirs(output_directory)

	filename = os.path.join(output_directory, output_file_name)

	if os.path.exists(filename):
		os.remove(filename)

	file = request.FILES["file"].file

	with open(filename, 'wb+') as destination:
		destination.write(file.read())

def generateProductCatalog(products, filename):

	template_src = 'product/product_catalog.html'

	template = get_template(template_src)

	html  = template.render(products)

	options = {
	'quiet': '',
	'margin-top': '0in',
	'margin-right': '0in',
	'margin-bottom': '0in',
	'margin-left': '0in',
	'no-outline': None,
	}

	config = pdfkit.configuration(wkhtmltopdf=settings.WKHTMLTOPDFPATH)

	contentString = "attachment; filename=" + filename

	pdf = pdfkit.PDFKit(html, "string", options=options,configuration=config).to_pdf()

	response = HttpResponse(pdf)
	response['Content-Type'] = 'application/pdf'
	response['Content-disposition'] = contentString

	return response
	

def generateProductFile(products, filename):

	contentString = "attachment; filename=" + filename
	response = HttpResponse(content_type='text/plain')
	response['Content-Disposition'] = contentString

	writer = csv.writer(response)

	writer.writerow(products)

	return response

def arrToFilename(arr):
	x = ""
	for a in arr:
		x += str(a) + "-"

	x = x[0:len(x)-1]

	return x

def getPaginationParameters(request, parameters={}, defaultItemsPerPage = 10, version = "0"):

	try:
		pageNumber = int(request.GET.get("page_number", 1))
		itemsPerPage = int(request.GET.get("items_per_page", defaultItemsPerPage))
	except Exception as e:
		pageNumber = 1
		itemsPerPage = defaultItemsPerPage

	if not pageNumber > 0 or not itemsPerPage > 0:
		pageNumber = 1
		itemsPerPage = defaultItemsPerPage

	parameters["pageNumber"] = pageNumber
	parameters["itemsPerPage"] = itemsPerPage

	return parameters

def responsePaginationParameters(response, paginator, parameters):
	response["total_items"] = paginator.count
	response["total_pages"] = paginator.num_pages
	response["page_number"] = parameters["pageNumber"]
	response["items_per_page"] = parameters["itemsPerPage"]
	return response

def link_to_foreign_key(obj, fk_name):
	fk_instance = getattr(obj, fk_name)
	app_label = fk_instance._meta.app_label.lower()
	model_name = fk_instance._meta.model_name.lower()
	link=urlresolvers.reverse("admin:{}_{}_change".format(app_label, model_name), args=[fk_instance.id])
	return u'<a href="%s" target="_blank">%s</a>' % (link,str(fk_instance))

def time_in_ist(dt):
	return  dt + datetime.timedelta(0,0,0,0,30,5,0)

def djangoEncodedTime(obj):
	t = json.dumps(obj, cls=DjangoJSONEncoder)
	return t[1:len(t)-1]

def getApiVersion(text):
	version = "0"
	try:
		version = re.search("version=(.+?)", text).group(1)
	except Exception as e:
		pass
	return version