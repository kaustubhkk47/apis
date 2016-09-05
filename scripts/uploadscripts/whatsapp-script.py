from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

import requests
import os, time, platform, sys

class ConstantValues():
	env = 'production'
	operatingSystem = ''
	accessToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiaW50ZXJuYWx1c2VyIiwiaW50ZXJuYWx1c2VySUQiOjF9.O2uFNT9QzwY6L064s4u60cevLwXxOxjG_vKldIr0yOo'

	productFileName = "./productfile.txt"

	defaultNumberOfProducts = 10

	def __init__(self):
		self.operatingSystem = platform.system()

	def setEnvironment(self, argv):
		if isinstance(argv, list) and len(argv) > 0:
			if argv[0] == 'test':
				self.env = 'test'
				print 'Running in testing mode'
			else:
				self.env = 'production'

	def getEnvironment(self):
		return self.env

	def getOperatingSystem(self):
		return self.operatingSystem

	def getAccessToken(self):
		return self.accessToken

constantValuesInstance = ConstantValues()

def getDefaultNumberOfProducts():
	return 10

def getBaseWebsiteUrl():
	env = constantValuesInstance.getEnvironment()
	if env == 'test':
		#return 'http://webapp.wholdus.localhost.com/'
		return 'http://www.wholdus.com/'
	else:
		return 'http://www.wholdus.com/'

def parseFloat(value):
	try:
		return int(value)
	except:
		return float(value)

def getChromeDriverPath():
	dir = os.path.dirname(os.path.realpath('__file__'))

	if constantValuesInstance.getOperatingSystem() == 'Linux':
		chrome_path = dir + '/chromedriver'
	else:
		chrome_path = dir + '/chromedriver.exe'

	return chrome_path

def getSharingUrl(product, urlPart, buyerProductID):
	url = getBaseWebsiteUrl() + 'bp/' + str(urlPart) + '-' + str(buyerProductID)
	url += '?utm_source=whatsapp'
	return url

def generateCaption(product, urlPart, buyerProductID):
	id = product['productID']
	# name = product['display_name']
	# price = product['min_price_per_unit']
	#margin = parseFloat(product['margin'])
	url = getSharingUrl(product, urlPart, buyerProductID)
	caption = '*ID: ' + str(id) + '* more details at: ' + str(url)
	return caption

def updateProductShownStatus(ids):
	payload = {}
	payload['buyerproductID'] = ids
	url = 'http://api.wholdus.com/users/buyer/buyerproducts/whatsapp/'
	r = requests.put(url, json=payload)

	if r.status_code == 200:
		data = r.json()
		print data
	else:
		print 'Could not update status'

class Products():
	baseUrl = 'http://api.wholdus.com/users/buyer/?whatsapp_sharing_active=1&access_token=' + constantValuesInstance.getAccessToken()
	totalBuyers = 0
	buyers = {}

	def generateQueryString(self, obj):
		ret = ''
		for key, value in obj.iteritems():
			ret += '&' + str(key) + '=' + str(value)
		return ret

	def parseProductsData(self, data):
		self.totalBuyers = len(data['buyers'])
		self.buyers = data['buyers']

	def fetchProducts(self, buyerIDs, numberOfProducts, specificProducts = "",maxID=-1):
		obj = {}
		if buyerIDs != '0':
			obj['buyerID'] = buyerIDs

		obj['buyer_product_count'] = numberOfProducts
		obj['buyer_product_details'] = 1
		obj['test_buyer'] = 0

		if maxID != -1:
			obj['buyer_max_ID'] = maxID

		if constantValuesInstance.getEnvironment() == 'test':
			obj['test_buyer'] = 1

		if not specificProducts == "":
			obj["productID"] = specificProducts

		url = self.baseUrl + self.generateQueryString(obj)

		print url
		r = requests.get(url)
		data = r.json()

		if data['statusCode'] == '2XX':
			data = data['body']
			self.parseProductsData(data)
			return data
		else:
			print 'Something went wrong while fetching data'
			return {}

class Whatsapp():
	whatsAppWeb = 'http://web.whatsapp.com'
	userSearchBoxXpath = '//*[@id="side"]/div[2]/div/label/input'
	#resultXpath = '/html/body/div/div/div[3]/div[2]/div[3]/div/div/div/div[1]/div/div/div[1]/div'
	resultXpath = '//*[@id="pane-side"]/div/div/div/div[1]/div/div/div[2]/div[2]/div[1]/span[3]'
	resultXpath2 = '//*[@id="pane-side"]/div/div/div/div[1]/div/div/div[2]/div[1]/div[1]/span/span'
	optionsDropdownButtonXpath = '//*[@id="main"]/header/div[3]/div/div[1]/button'
	optionsDropdownButtonClassName = 'icon-clip'
	photosVideosXpath = '//*[@id="main"]/header/div[3]/div/div[1]/span/div/div/ul/li[1]/button/div'
	imageUploadXpath = '//*[@id="main"]/header/div[3]/div/div[1]/span/div/input[2]'
	#captionXpath = '//*[@id="app"]/div/div[3]/div[1]/span[2]/span/div/div[2]/div/span/div/div[2]/div/div/div/div[2]'
	captionXpath = '//*[@id="app"]/div/div[3]/div[1]/span[2]/span/div/div[2]/div/span/div/div[2]/div/div[2]/div[1]/div'
	submitButtonXpath = '//*[@id="app"]/div/div[3]/div[1]/span[2]/span/div/div[2]/span[2]/div/button'

	def launchChrome(self):
		chromeOptions = webdriver.ChromeOptions()
		chromeOptions.add_experimental_option("excludeSwitches", ['ignore-certificate-errors'])
		self.driver = webdriver.Chrome(getChromeDriverPath(), chrome_options=chromeOptions)
		self.driver.maximize_window()

	def openUrl(self):
		self.driver.get(self.whatsAppWeb)

	def selectUser(self):
		time.sleep(3)
		try:
			#WebDriverWait(self.driver, 10).until(expected_conditions.visibility_of_element_located((By.CLASS_NAME,'chat-body')))
			try:
				WebDriverWait(self.driver, 10).until(expected_conditions.visibility_of_element_located((By.XPATH, self.resultXpath)))
				WebDriverWait(self.driver, 10).until(expected_conditions.element_to_be_clickable((By.XPATH, self.resultXpath))).click()
				return True
			except Exception as e:
				WebDriverWait(self.driver, 10).until(
					expected_conditions.visibility_of_element_located((By.XPATH, self.resultXpath2)))
				WebDriverWait(self.driver, 10).until(
					expected_conditions.element_to_be_clickable((By.XPATH, self.resultXpath2))).click()
			return True
		except Exception as e:
			print e
			return False


	def openUser(self, userName):
		WebDriverWait(self.driver, 100).until(expected_conditions.visibility_of_element_located((By.XPATH, self.userSearchBoxXpath)))
		userSearchBox = self.driver.find_element_by_xpath(self.userSearchBoxXpath)
		userSearchBox.click()
		userSearchBox.clear()

		userSearchBox.send_keys(userName)

		return self.selectUser()

	def uploadData(self, data, bpUrl):
		uploaded = ''
		for product in data:
			buyerProductID = product['buyerproductID']
			product = product['product']
			if product['image'] and product['image']['absolute_path']:
				url = product['image']['absolute_path']
				r = requests.get(url, stream=True)
				if r.status_code == 200:
					path = os.path.dirname(os.path.realpath('__file__'))

					if constantValuesInstance.getOperatingSystem() == 'Linux':
						path += '/products'
						if os.path.exists(path) == False:
							os.makedirs(path)
						path +=  '/' + str(product['productID']) + '.jpg'
					else:
						path += '\products'
						if os.path.exists(path) == False:
							os.makedirs(path)
						path +=  '\\' + str(product['productID']) + '.jpg'

					with open(path, 'wb') as f:
						for chunk in r.iter_content(128):
							f.write(chunk)
						f.close()

					WebDriverWait(self.driver, 100).until(expected_conditions.visibility_of_element_located(
						(By.CLASS_NAME, self.optionsDropdownButtonClassName))).click()
					WebDriverWait(self.driver, 100).until(
						expected_conditions.visibility_of_element_located((By.XPATH, self.photosVideosXpath)))
					self.driver.find_element_by_xpath(self.imageUploadXpath).send_keys(path)

					WebDriverWait(self.driver, 100).until(
						expected_conditions.visibility_of_element_located((By.XPATH, self.captionXpath))).send_keys(generateCaption(product, bpUrl, buyerProductID))
					WebDriverWait(self.driver, 100).until(
						expected_conditions.visibility_of_element_located((By.XPATH, self.submitButtonXpath))).click()

					uploaded += str(buyerProductID) + ','
		uploaded = uploaded[0:len(uploaded)-1]
		updateProductShownStatus(uploaded)

	def quit(self):
		self.driver.quit()

def main(argv):

	constantValuesInstance.setEnvironment(argv)

	ws = Whatsapp()
	ws.launchChrome()
	ws.openUrl()

	while 1:
		print 'Run Script for?'
		print 'Enter 0 to run script for all buyers or comma separated buyer IDs for specific buyer i.e. 1,2,3'

		t = raw_input()
		t = t.strip()

		p = Products()

		specificProducts = ""

		print 'Enter 0 to run script for default products or 1 to enter script for specific products. If entering 1 keep file with product Ids in same folder with filename productfile.txt'

		while 1:
			
			productInput = raw_input()
			productInput = productInput.strip()

			if productInput == '1':
				try:
					f = open(constantValuesInstance.productFileName, 'r')
					first_line = f.readline()
					first_line = first_line.rstrip()
				except Exception as e:
                                        print e
					print "Could not read product file"
					print "Enter 1 to try reading file again"
					continue
				else:
					print "Product IDs are {}".format(first_line) 
					specificProducts = first_line
					break
			else:
				break
			


		if t == '0':
			print 'Enter buyer id to start from'
			maxID = raw_input().strip()
			print 'Running Script for all buyers'
			p.fetchProducts(t, getDefaultNumberOfProducts(), specificProducts, maxID)
		else:
			print 'Enter number of products to send. Enter 0 for default settings'
			numberOfProducts = int(raw_input().strip())

			if numberOfProducts == 0:
				numberOfProducts = constantValuesInstance.defaultNumberOfProducts

			print 'Running Script for buyers with id: ' + t + ' and for ' + str(numberOfProducts) + ' products'
			p.fetchProducts(t, numberOfProducts, specificProducts)


		for d in p.buyers:
			print d['whatsapp_contact_name']
			print len(d['buyer_products'])
			if ws.openUser(d['whatsapp_contact_name']):
				ws.uploadData(d['buyer_products'], d['buyer_panel_url'])
			else:
				print "could not upload products for this buyer"

		if len(p.buyers) == 0:
			print "No buyer found"

		print 'Done'
		print 'Enter 0 to terminate the program or 1 to continue'
		f = raw_input().strip()

		if f == '0':
			print 'Quitting..'
			time.sleep(10)
			break

	ws.quit()
main(sys.argv[1:])
