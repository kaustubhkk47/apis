from django.db import connection
from django.utils import timezone
from catalog.models.product import Product
from django.db.models import Sum
from users.models.buyer import Buyer

def update_product_likes_dislikes():
	Product.objects.all().update(product_likes=0, product_dislikes=0)
 	cursor = connection.cursor()
 	nowTime = "'" + timezone.now().strftime("%Y-%m-%d %H:%M:%S") + "'"
 	testBuyers = Buyer.objects.filter(test_buyer=1).values_list('id', flat=True)
 	testBuyerIDs = ','.join(map(str, testBuyers))
 	cursor.execute("UPDATE catalog_product cp JOIN (SELECT product_id, SUM(IF(response_code = 1, 1, 0)) as likes, SUM(IF(response_code = 2, 1, 0)) as dislikes FROM users_buyerproductresponse WHERE buyer_id NOT IN ( " + testBuyerIDs + ") GROUP BY product_id) AS temp ON cp.id = temp.product_id SET cp.product_likes = temp.likes, cp.product_dislikes = temp.dislikes, updated_at = " + nowTime)
 	cursor.close()

def update_scores():
	cursor = connection.cursor()
 	startTime = "'" + Product.objects.earliest('created_at').created_at.strftime("%Y-%m-%d %H:%M:%S") + "'"
 	nowTime = "'" + timezone.now().strftime("%Y-%m-%d %H:%M:%S") + "'"
 	summary = Product.objects.aggregate(total_likes = Sum('product_likes'), total_dislikes=Sum('product_dislikes'))
 	avgRating = (float(summary["total_likes"]))/(summary["total_likes"] + summary["total_dislikes"])
 	threshold = 50
 	cursor.execute("UPDATE catalog_product SET product_score = (DATEDIFF(created_at," +startTime +  ")/DATEDIFF("+ nowTime +", " + startTime+" )*30 + ((product_likes + "+str(threshold*avgRating)+")/(product_likes + product_dislikes + "+ str(threshold) +"))*70)")
 	cursor.close()

 	