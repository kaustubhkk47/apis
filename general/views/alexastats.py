## fetch details from alexa page of wholdus.com
## save it into sqlite db unless more better solution
## Author: "Aditya Jha"

import requests
from bs4 import BeautifulSoup

from ..models.alexastats import AlexaStats

import logging
log = logging.getLogger("django")

def fetchData(url):
    r = requests.get(url)

    if r.status_code == 200:
        return r.text
    else:
        return None

def findImportantInfo(data):
    info = BeautifulSoup(data, "html.parser")

    requiredInfo = info.find_all('strong', {'class': 'metrics-data align-vmiddle'})

    returnValue = {
        "global": 0,
        "india": 0,
        "bounce_rate": 0,
        "daily_page_views_per_visitor": 0,
        "daily_time_on_site": 0,
        "search_visits": 0,
    }

    if len(requiredInfo) == 0:
        log.error(str(returnValue))
        return

    i = 0
    while i<len(requiredInfo):
        if i == 0:
            returnValue["global"] = requiredInfo[i].text.strip().replace(",",'')
        elif i == 1:
            returnValue["india"] = requiredInfo[i].text.strip().replace(",",'')
        elif i == 2:
            returnValue["bounce_rate"] = requiredInfo[i].text.strip().replace("%",'')
        elif i == 3:
            returnValue["daily_page_views_per_visitor"] = requiredInfo[i].text.strip().replace(",",'')
        elif i == 4:
            returnValue["daily_time_on_site"] = requiredInfo[i].text.strip().replace(",",'')
        elif i == 5:
            returnValue["search_visits"] = requiredInfo[i].text.strip().replace("%",'')

        i += 1

    return returnValue

def saveToDB(data):

    newAlexaStats = AlexaStats()

    try:

        newAlexaStats.global_rank = int(data["global"])
        newAlexaStats.india_rank = int(data["india"])
        newAlexaStats.bounce_rate = str(data["bounce_rate"])
        newAlexaStats.daily_page_views_per_visitor = str(data["daily_page_views_per_visitor"])
        newAlexaStats.daily_time_on_site = str(data["daily_time_on_site"])
        newAlexaStats.search_visits = str(data["search_visits"])
    
        newAlexaStats.save()
    except Exception as e:
        log.error(e)

def scrape_data():
    url = 'http://www.alexa.com/siteinfo/wholdus.com'

    data = fetchData(url)

    if not data:
        log.error("Could not fetch alexa data")
        return

    finalData = findImportantInfo(data)

    saveToDB(finalData)

if __name__ == "__main__":
    scrape_data()
