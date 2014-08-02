from django.core.management.base import BaseCommand, CommandError
from roundware.rw.models import Asset
from django.conf import settings
import os.path

class Command(BaseCommand):
    args = ''
    help = 'Checks that Assets exist as files in the media directory'

    def handle(self, *args, **options):
        self.stdout.write("Checking all Roundware Assets")
        assets = Asset.objects.all()
        
        assets_found = 0
        assets_not_found = 0

        for asset in assets:
            filepath = settings.MEDIA_BASE_DIR + asset.filename
            if os.path.isfile(filepath):
                assets_found += 1
            else:
                assets_not_found += 1
                self.stderr.write("Missing file: %s" % filepath)
        
        self.stdout.write("Roundware Assets found:     %s" % assets_found)
        self.stdout.write("Roundware Assets not found: %s" % assets_not_found)
