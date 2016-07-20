from django.core.management.base import BaseCommand, CommandError
from general.views.alexastats import scrape_data

class Command(BaseCommand):
	help = "Useful for cron job for getting alexa stats"

	def handle(self, *args, **options):
		scrape_data()