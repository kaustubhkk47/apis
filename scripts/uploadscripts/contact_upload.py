import os
import csv
import requests
import json

contactsDirectory = "./contacts/"
contactsURL = "http://api.wholdus.com/general/marketingcontact/"

def getAllFiles(activeDir):
	return [f for f in os.listdir(activeDir) if os.path.isfile(os.path.join(activeDir, f)) and os.path.splitext(f)[1] in ".csv"]

def getAllNumbers(fileName):
	contacts = []
	with open(fileName, 'rb') as csvfile:
		fileReader = csv.reader(csvfile, delimiter=',')
		for row in fileReader:
			if validate_mobile_number(row[1]):
				contacts.append({"mobile_number":row[1]})

	print("{} contacts read from {}".format(len(contacts),fileName))
	if len(contacts) > 0:
		return {"contacts":contacts}
	else:
		postFeedback(fileName, 0, "no useful contacts found in file")
		return None

def validate_mobile_number(x):
	try:
		x = str(x)
	except Exception as e:
		return False
	if len(x) != 10:
		return False
	if not (x[0] == '9' or x[0] == '8' or x[0] == '7'):
		return False
	return True

def postFeedback(fileName, success, message):
	print("{} - success: {} - message".format(fileName, success, message))
	with open('feedback.csv', 'ab+') as csvfile:
		writer = csv.writer(csvfile, delimiter=',')
		writer.writerow([fileName, str(success), message])

def upload_contacts():
	fileList = getAllFiles(contactsDirectory)
	print("{} files read from folder".format(len(fileList)))
	for fileName in fileList:
		contactsDict = getAllNumbers(os.path.join(contactsDirectory, fileName))
		if contactsDict != None:
			response = requests.post(contactsURL, data=json.dumps(contactsDict))
			if response.status_code == requests.codes.ok:
				postFeedback(fileName, 1, "successfully uploaded")
				try:
					os.remove(os.path.join(contactsDirectory, fileName))
				except OSError as e:
					pass
			else:
				try:
					jsonText = json.loads(response.text)
					postFeedback(fileName, 0, jsonText["error"])
				except Exception as e:
					postFeedback(fileName, 0, str(e))

	pass

if __name__ == "__main__":
	print "Starting to upload contacts"
	upload_contacts()
	raw_input("Press enter to exit")