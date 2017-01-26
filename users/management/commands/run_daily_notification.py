from django.core.management.base import BaseCommand, CommandError
from users.views.buyer import send_non_registered_buyer_notification, send_buyer_welcome_notification

class Command(BaseCommand):
	help = "Useful for cron job for daily notifications"

	def handle(self, *args, **options):
		send_non_registered_buyer_notification()
		send_buyer_welcome_notification()