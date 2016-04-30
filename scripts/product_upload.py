import openpyxl
import requests
import json
import os
import shutil
import ast
from PIL import Image

productURL = "http://api.probzip.com/products/"
redFill = openpyxl.styles.PatternFill(start_color='FA5858',end_color='FA5858',fill_type='solid')
greenFill = openpyxl.styles.PatternFill(start_color='00FF40',end_color='00FF40',fill_type='solid')

imageDirectory = "./images/"
originalSizePath = ""
thumbnailSizePath = "200x200/"
mediumSizePath = "400x400/"
largeSizePath = "700x700/"

allSizePaths = [originalSizePath, thumbnailSizePath, mediumSizePath, largeSizePath]
allImageSizes = [2000.0, 200.0, 400.0, 700.0]
fileFormatExtensions = [".jpg", ".jpeg",".png"]


def read_file():
        #filename = raw_input()
	try:
		wb = openpyxl.load_workbook("./ProductDataSheet.xlsx")
		#wb = openpyxl.load_workbook(filename)
		send_products_data(wb)
	except Exception as e:
		print e

def send_products_data(wb):
	row = 5
	column = 1
	ws = wb.worksheets[1]

	while True:
		productName = str(ws.cell(row = row, column = column).value)
		if productName == "" or productName == None or productName == 'None':
			break
		productData = json.dumps(fill_product_data(wb, row))

		if productData != {}:
			response = requests.post(productURL, data = productData)
			if response.status_code == requests.codes.ok:
				try:
					jsonText = json.loads(response.text)

					if jsonText["statusCode"] != "2XX":
						post_feedback(wb, row, jsonText["body"]["error"])
					else:
						moveImages(jsonText, row, wb)
						post_feedback(wb, row, "Success")
				except Exception as e:
					print e
					post_feedback(wb, row, "Incorrect response from server")
			else:
				post_feedback(wb, row, "Error response from server")

		row += 1

	wb.save("./ProductDataSheetf.xlsx")

def moveImages(jsonText, row, wb):
	imgNo = 1
	body = jsonText["body"]["product"]
	image_path = body["image_path"]
	image_name = body["image_name"]
	image_numbers = body["image_numbers"]
	image_numbers = ast.literal_eval(image_numbers)
	for sizePath in allSizePaths:
		create_image_directory(image_path, sizePath)
	while True:
		check = 0
		for extension in fileFormatExtensions:
			imagePath = imageDirectory + str(row) + "-" + str(imgNo) + extension
			if os.path.isfile(imagePath):
				check = 1
				img = Image.open(imagePath)
				for i in range(len(allSizePaths)):
					sizePath = allSizePaths[i]
					directory = imageDirectory + image_path + sizePath
					newPath = directory + image_name + "-" + str(image_numbers[imgNo]) + ".jpg"
					imgnew = resize_image(img, allImageSizes[i])
					imgnew.save(newPath,format="JPEG",quality=75)
				os.remove(imagePath)
				
		if(check == 0):
			break
		else:
			imgNo += 1
	post_image_feedback(wb, row, imgNo-1)

def create_image_directory(image_path, size_path):
	directory = imageDirectory + image_path + size_path
	if not os.path.exists(directory):
		os.makedirs(directory)

def resize_image(img, x):
	width = img.width
	height = img.height
	if width > height and width > x:
		img = img.resize((int(x), int(x*float(height)/float(width))),Image.ANTIALIAS)
	if height >= width and height > x:
		img = img.resize((int(x*float(width)/float(height)), int(x)),Image.ANTIALIAS)
	return img
	
def post_image_feedback(wb, row, feedback):
	wb.worksheets[1]["V"+str(row)].value = str(feedback) + " images moved"

def fill_product_data(wb , i):
	productData = {}

	try:
		productData["categoryID"] = get_categoryID(wb.worksheets[1]["D"+str(i)].value, wb)
		productData["sellerID"] = parseInt(wb.worksheets[0]["F4"].value)

		productData["name"] = str(wb.worksheets[1]["A"+str(i)].value)
		productData["price_per_unit"] = parseFloat(wb.worksheets[2]["G"+str(i)].value)
		productData["unit"] = str(wb.worksheets[2]["E"+str(i)].value)
		productData["tax"] = parseFloat(wb.worksheets[2]["K"+str(i)].value)
		productData["lot_size"] = parseInt(wb.worksheets[2]["H"+str(i)].value)
		productData["price_per_lot"] = parseFloat(productData["lot_size"]*productData["price_per_unit"])
		productData["image_count"] = countImages(i)
	
		productDetails = {}
		productDetails["seller_catalog_number"] = str(wb.worksheets[1]["B"+str(i)].value)
		productDetails["brand"] = str(wb.worksheets[1]["C"+str(i)].value)
		productDetails["description"] = str(wb.worksheets[1]["E"+str(i)].value)
		productDetails["gender"] = str(wb.worksheets[1]["F"+str(i)].value)
		productDetails["pattern"] = str(wb.worksheets[1]["G"+str(i)].value)
		productDetails["style"] = str(wb.worksheets[1]["H"+str(i)].value)
		productDetails["fabric_gsm"] = str(wb.worksheets[1]["I"+str(i)].value)
		productDetails["sleeve"] = str(wb.worksheets[1]["J"+str(i)].value)
		productDetails["neck_collar_type"] = str(wb.worksheets[1]["K"+str(i)].value)
		productDetails["length"] = str(wb.worksheets[1]["L"+str(i)].value)
		productDetails["work_decoration_type"] = str(wb.worksheets[1]["M"+str(i)].value)
		productDetails["colours"] = str(wb.worksheets[1]["N"+str(i)].value)
		productDetails["sizes"] = str(wb.worksheets[1]["O"+str(i)].value)
		productDetails["special_feature"] = str(wb.worksheets[1]["P"+str(i)].value)
		productDetails["packaging_details"] = str(wb.worksheets[1]["Q"+str(i)].value)
		productDetails["availability"] = str(wb.worksheets[1]["R"+str(i)].value)
		productDetails["weight_per_unit"] = parseFloat(wb.worksheets[2]["F"+str(i)].value)
		productDetails["dispatched_in"] = str(wb.worksheets[1]["S"+str(i)].value)
		productDetails["sample_type"] = str(wb.worksheets[2]["M"+str(i)].value)
		productDetails["sample_description"] = str(wb.worksheets[2]["N"+str(i)].value)
		productDetails["sample_price"] = parseFloat(wb.worksheets[2]["O"+str(i)].value)

		productDetails["manufactured_country"] = "India"
		productDetails["manufactured_city"] = str(wb.worksheets[0]["C7"].value)

		productData["details"] = productDetails

		productData["product_lot"] = fill_product_lot_data(wb,i)

	except Exception as e:
		post_feedback(wb, i, "Data was incorrect")

	return productData

def get_categoryID(value, wb):
	ws = wb.worksheets[3]
	row = 2
	for i in range(2,10):
		if ws["A"+str(i)].value == value:
			return parseInt(ws["B" +str(i)].value)

def countImages(row):
	imgNo = 1
	while True:
		check = 0
		for extension in fileFormatExtensions:
			imagePath = imageDirectory + str(row) + "-" + str(imgNo) + extension
			if os.path.isfile(imagePath):
				check = 1
		if(check == 0):
			break
		else:
			imgNo += 1
	return imgNo-1


def fill_product_lot_data(wb,i):
	productLotData = []

	column = 13
	ws = wb.worksheets[2]

	while True:
		from_lot = str(ws.cell(row = i, column = column).value)
		if from_lot == 0 or from_lot == None or from_lot == "None":
			return productLotData
		to_lot = parseInt(ws.cell(row = i, column = column+1).value)
		price = parseFloat(ws.cell(row = i, column = column+2).value)

		productLot = {}
		productLot["lot_size_from"] = parseInt(from_lot)
		productLot["lot_size_to"] = to_lot
		productLot["price_per_unit"] = price
		productLotData.append(productLot)

		column += 3
		

	return productLotData

def post_feedback(wb, i, feedback):
	wb.worksheets[1]["U"+str(i)].value = feedback
	if feedback == "Success":
		wb.worksheets[1]["U"+str(i)].fill = greenFill
	else:
		wb.worksheets[1]["U"+str(i)].fill = redFill

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
