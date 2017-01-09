from django.core.management.base import BaseCommand, CommandError
from users.views.buyer import send_filled_cart_notification

class Command(BaseCommand):
	help = "Useful for cron job for hourly notifications"

	def handle(self, *args, **options):
		send_filled_cart_notification()