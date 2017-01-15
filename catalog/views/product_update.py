from django.db import connection
from django.utils import timezone
from catalog.models.product import Product

def update_product_likes_dislikes():
 	cursor = connection.cursor()
 	nowTime = "'" + timezone.now().strftime("%Y-%m-%d %H:%M:%S") + "'"
 	cursor.execute("UPDATE catalog_product cp JOIN (SELECT product_id, SUM(IF(response_code = 1, 1, 0)) as likes, SUM(IF(response_code = 2, 1, 0)) as dislikes FROM users_buyerproductresponse WHERE 1 GROUP BY product_id) AS temp ON cp.id = temp.product_id SET cp.product_likes = temp.likes, cp.product_dislikes = temp.dislikes, updated_at = " + nowTime)
 	cursor.close()

def update_scores():
	cursor = connection.cursor()
 	startTime = "'" + Product.objects.earliest('created_at').created_at.strftime("%Y-%m-%d %H:%M:%S") + "'"
 	nowTime = "'" + timezone.now().strftime("%Y-%m-%d %H:%M:%S") + "'"
 	cursor.execute("UPDATE catalog_product SET product_score = (DATEDIFF(created_at," +startTime +  ")/DATEDIFF("+ nowTime +", " + startTime+" )*30 + ((product_likes + 20)/(product_likes + product_dislikes + 40))*70)")
 	cursor.close()

 	