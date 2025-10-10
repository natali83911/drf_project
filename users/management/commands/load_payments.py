import os

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Load payment data from fixture"

    def handle(self, *args, **options):
        fixture_file = "payment_fixture.json"
        if os.path.exists(fixture_file):
            call_command("loaddata", fixture_file)
            self.stdout.write(self.style.SUCCESS("Payment data loaded successfully"))
        else:
            self.stdout.write(self.style.ERROR("Fixture file not found"))
