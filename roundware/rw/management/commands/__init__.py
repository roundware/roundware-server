import os.path
from django.core.management.base import BaseCommand
from roundware.rw.models import Asset
from django.conf import settings


class RoundwareCommand(BaseCommand):

    def check_assets(self):
        """
        Check that every file in the Roundware asset table exists.

        Returns a tuple of a list of found assets and list of missing assets.
        """
        assets = Asset.objects.all()

        found = []
        not_found = []

        for asset in assets:
            filepath = os.path.join(settings.MEDIA_BASE_DIR, asset.filename)
            if os.path.isfile(filepath):
                found.append(asset)
            else:
                not_found.append(asset)
                self.stderr.write("Missing file: %s" % filepath)

        return (found, not_found)

    def check_media(self):
        """
        Check that every file in the media directory is associated with an
        asset.

        Returns a tuple of a list of assets with matching files and a list of
        unknown file paths.
        """
        known = []
        unknown = []

        # Recursively search /var/www/roundware/rwmedia for files.
        for dirpath, dirnames, filenames in os.walk(settings.MEDIA_BASE_DIR):
            for filename in filenames:
                full_path = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(full_path, settings.MEDIA_BASE_DIR)
                try:
                    asset = Asset.objects.get(filename=rel_path)
                except Asset.DoesNotExist:
                    # File is not associated with an asset
                    unknown.append(full_path)
                    self.stderr.write("Unknown file: %s" % full_path)
                else:
                    # File is referenced by an asset
                    known.append(asset)

        return (known, unknown)

