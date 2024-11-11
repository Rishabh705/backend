# core/management/commands/ingest_data.py
from django.core.management.base import BaseCommand
from core.tasks import start_data_ingestion

class Command(BaseCommand):
    help = 'Ingest customer and loan data from Excel files'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting data ingestion...'))
        start_data_ingestion()
        self.stdout.write(self.style.SUCCESS('Data ingestion running...'))
