from django.core.management.base import BaseCommand, CommandError
from roundware.rw.models import Asset
from django.conf import settings
import os

class Command(BaseCommand):
    args = ''
    help = 'Checks that Files in the media directory exist as Assets'

    def handle(self, *args, **options):
        self.stdout.write("Checking all Roundware Media files")

        file_found = 0
        file_not_found = 0

        for file in os.listdir(settings.MEDIA_BASE_DIR):
            try:
                asset = Asset.objects.get(filename=file)
            except Asset.DoesNotExist:
                file_not_found += 1
                filepath = settings.MEDIA_BASE_DIR + file
                self.stderr.write("Unknown file: %s" % filepath)
            else:
                file_found += 1


        self.stdout.write("Media files found:     %s" % file_found)
        self.stdout.write("Media files not found: %s" % file_not_found)
