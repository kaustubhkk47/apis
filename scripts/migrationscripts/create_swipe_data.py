from users.models.buyer import Buyer, BuyerProductResponse, BuyerProducts, BuyerProductResponseHistory
from django.db.models import Count, Max

from django.utils import timezone
import datetime

import random

nowTime = timezone.now()

def get_all_buyers_list(buyer_count):
	buyers_list = BuyerProductResponse.objects.annotate(num_responses=Count('buyer_id')).filter(num_responses__lt=100).values_list('buyer_id', flat=True).annotate(num_responses=Count('buyer_id'))
	all_buyers = Buyer.objects.filter().values_list('id', flat =True)
	non_swiping_buyers = [val for val in all_buyers if val not in buyers_list]
	return random.sample(non_swiping_buyers, min(buyer_count, len(non_swiping_buyers)))

def get_last_swiped_time(buyerPtr):
	#max_created_at = BuyerProductResponse.objects.filter(buyer_id=buyerPtr.id).aggregate(Max('created_at'))['created_at__max']
	return buyerPtr.created_at

def getSwipingStartDate(last_swiped_time):
	daysTillToday = (nowTime - last_swiped_time).days
	daysFromStart = random.randint(1, daysTillToday/2)
	return (last_swiped_time + datetime.timedelta(days=daysFromStart)).date()

def getSwipingEndDate(last_swiped_time):
	daysTillToday = (nowTime - last_swiped_time).days
	daysFromStart = random.randint(daysTillToday/4*3, daysTillToday)
	return (last_swiped_time + datetime.timedelta(days=daysFromStart)).date()

def getSwipingDaysList(swipingStartDate, swipingEndDate):
	totalDays = (swipingEndDate - swipingStartDate).days
	noOfSwipingDays = random.randint(totalDays/8, totalDays/3)
	daysOffset = random.sample(range(0, totalDays), noOfSwipingDays)
	swipingDays = [(swipingStartDate + datetime.timedelta(days=val)) for val in daysOffset]
	return swipingDays

def getDaySwipeStartTime(swipingDay):
	minTime = 3
	maxTime = 17
	hour = random.randint(minTime, maxTime)
	minute = random.randint(0, 59)
	second = random.randint(0, 59)
	actualTime = datetime.datetime(year = swipingDay.year, month = swipingDay.month, day = swipingDay.day, hour = hour, minute = minute, second = second, tzinfo = nowTime.tzinfo)
	return actualTime

def getSwipingInterval(seconds):
	return random.randint(seconds/2, seconds/2*3)

def nonNaiveDate(dateObject):
	return datetime.datetime(year = dateObject.year, month = dateObject.month, day = dateObject.day, hour = 0, minute = 0, second = 0, tzinfo = nowTime.tzinfo)

def generateResponseCode(probability_of_like):
	return (random.random() > probability_of_like) + 1

def generateSwipeData(probability_of_swipe):
	return random.random() < probability_of_swipe

def insert_values():
	buyers_list = get_all_buyers_list(25)

	for buyer_id in buyers_list:
		buyerPtr = Buyer.objects.get(id=buyer_id)
		last_swiped_time = get_last_swiped_time(buyerPtr)
		swipingStartDate = getSwipingStartDate(last_swiped_time)
		swipingEndDate = getSwipingEndDate(last_swiped_time)
		swipingDaysList = getSwipingDaysList(swipingStartDate, swipingEndDate)

		gapInSwipes = random.randint(10, 35)

		for swipingDay in swipingDaysList:
			noOfSwipes = random.randint(5, 50)
			swipeDayStartTime = getDaySwipeStartTime(swipingDay)
			buyerProductPtr = BuyerProducts.objects.filter(buyer_id=buyerPtr.id, responded=0, created_at__lt=nonNaiveDate(swipingDay))[0:noOfSwipes]

			for buyerProduct in buyerProductPtr:
				responseCode = generateResponseCode(0.2)
				hasSwiped = generateSwipeData(0.8)
				buyerProduct.responded = responseCode
				buyerProduct.save()

				newBuyerProductResponseHistory = BuyerProductResponseHistory(buyer_id=buyerProduct.buyer_id,product_id=buyerProduct.product_id,buyer_product_id=buyerProduct.id, responded_from = 0, has_swiped=hasSwiped, response_code=responseCode)
				newBuyerProductResponseHistory.save()
				newBuyerProductResponseHistory.created_at = swipeDayStartTime
				newBuyerProductResponseHistory.save()

				newBuyerProductResponse = BuyerProductResponse(buyer_id=buyerProduct.buyer_id,product_id=buyerProduct.product_id,buyer_product_id=buyerProduct.id, responded_from = 0, has_swiped=hasSwiped, response_code=responseCode)
				newBuyerProductResponse.save()
				newBuyerProductResponse.created_at = swipeDayStartTime
				newBuyerProductResponse.save()

				swipeDayStartTime = swipeDayStartTime + datetime.timedelta(seconds=getSwipingInterval(gapInSwipes))


		