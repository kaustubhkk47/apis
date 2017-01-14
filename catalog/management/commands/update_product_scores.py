from django.core.management.base import BaseCommand, CommandError
from catalog.views.product_update import update_product_likes_dislikes

class Command(BaseCommand):
	help = "Useful for cron job for daily notifications"

	def handle(self, *args, **options):
		update_product_likes_dislikes()