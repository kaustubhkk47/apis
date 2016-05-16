import openpyxl
import requests
import json

buyerURL = "http://api.probzip.com/users/buyer/"

redFill = openpyxl.styles.PatternFill(start_color='FA5858',end_color='FA5858',fill_type='solid')
greenFill = openpyxl.styles.PatternFill(start_color='00FF40',end_color='00FF40',fill_type='solid')

inputFileName = "./BuyerDataSheet.xlsx"
outputFileName = "./BuyerDataSheetF.xlsx"

def upload_buyers():
	wb = read_file()
	try:
		send_buyers_data(wb)
	except Exception as e:
		print e

def read_file():
	try:
		wb = openpyxl.load_workbook(inputFileName,data_only=True)
		print "File read correctly"	
	except Exception as e:
		print e
	return wb

def send_buyers_data(wb):
	row = 2
	column = 1
	ws = wb.worksheets[0]

	while True:
		buyerName = str(ws.cell(row = row, column = column).value)
		if buyerName == "" or buyerName == None or buyerName == 'None':
			break
		buyerData = json.dumps(fill_buyer_data(wb, row))

		if not (buyerData == {} or buyerData == "{}"):
			response = requests.post(buyerURL, data = buyerData)
			if response.status_code == requests.codes.ok:
				try:
					jsonText = json.loads(response.text)

					if jsonText["statusCode"] != "2XX":
						post_feedback(wb, row, jsonText["body"]["error"])
						print jsonText["body"]["error"]
					else:
						post_feedback(wb, row, "Success",jsonText["body"]["buyer"]["buyerID"])
						print "Success"
				except Exception as e:
					print e
					post_feedback(wb, row, e)
			else:
				post_feedback(wb, row, "Error response from server")

		row += 1

	wb.save(outputFileName)

def fill_buyer_data(wb , i):
	buyerData = {}

	try:
		buyerData["name"] = str(wb.worksheets[0]["A"+str(i)].value)
		buyerData["company_name"] = str(wb.worksheets[0]["B"+str(i)].value)
		buyerData["mobile_number"] = str(wb.worksheets[0]["C"+str(i)].value)
		buyerData["email"] = str(wb.worksheets[0]["D"+str(i)].value)
		buyerData["password"] = str(wb.worksheets[0]["E"+str(i)].value)
		buyerData["alternate_phone_number"] = str(wb.worksheets[0]["F"+str(i)].value)
		buyerData["mobile_verification"] = True
		buyerData["email_verification"] = True
		buyerData["gender"] = str(wb.worksheets[0]["G"+str(i)].value)
	
		buyerDetails = {}
		buyerDetails["vat_tin"] = str(wb.worksheets[0]["H"+str(i)].value)
		buyerDetails["cst"] = str(wb.worksheets[0]["I"+str(i)].value)
		buyerDetails["buyer_interest"] = str(wb.worksheets[0]["J"+str(i)].value)
		buyerDetails["customer_type"] = str(wb.worksheets[0]["K"+str(i)].value)
		buyerDetails["purchase_duration"] = str(wb.worksheets[0]["L"+str(i)].value)
		buyerDetails["buying_capacity"] = str(wb.worksheets[0]["M"+str(i)].value)
		buyerDetails["buys_from"] = str(wb.worksheets[0]["N"+str(i)].value)
		buyerDetails["purchasing_states"] = str(wb.worksheets[0]["O"+str(i)].value)

		buyerData["details"] = buyerDetails

		buyerAddress = {}
		buyerAddress["address"] = str(wb.worksheets[0]["P"+str(i)].value)
		buyerAddress["landmark"] = str(wb.worksheets[0]["Q"+str(i)].value)
		buyerAddress["city"] = str(wb.worksheets[0]["R"+str(i)].value)
		buyerAddress["state"] = str(wb.worksheets[0]["S"+str(i)].value)
		buyerAddress["country"] = str(wb.worksheets[0]["T"+str(i)].value)
		buyerAddress["contact_number"] = str(wb.worksheets[0]["U"+str(i)].value)
		buyerAddress["pincode"] = str(wb.worksheets[0]["V"+str(i)].value)
		
		buyerData["address"] = buyerAddress

	except Exception as e:
		buyerData = {}
		print e
		print "Data was incorrect"
		post_feedback(wb, i, "Data was incorrect")

	return buyerData

def post_feedback(wb, i, feedback, buyerID=0):
	wb.worksheets[0]["X"+str(i)].value = feedback
	if feedback == "Success":
		wb.worksheets[0]["X"+str(i)].fill = greenFill
		wb.worksheets[0]["Y"+str(i)] = int(buyerID)
	else:
		wb.worksheets[0]["X"+str(i)].fill = redFill

def parseFloat(x):
	if x == None or x == 0:
		return float(0)
	else:
		return float(x)

def parseInt(x):
	if x == None or x == 0:
		return int(0)
	else:
		return int(x)