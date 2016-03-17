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
            filepath = os.path.join(settings.MEDIA_ROOT, asset.filename)
            if os.path.isfile(filepath):
                found.append(asset)
            else:
                not_found.append(asset)
                self.stderr.write("Missing file: %s" % filepath)

            # Parse mp3 files, but don't count.
            mp3_filepath = filepath.replace('wav', 'mp3')
            if not os.path.isfile(mp3_filepath):
                self.stderr.write("Missing file: %s" % mp3_filepath)


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
        for dirpath, dirnames, filenames in os.walk(settings.MEDIA_ROOT):
            for filename in filenames:
                full_path = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(full_path, settings.MEDIA_ROOT)
                # DB only manages wav files, so check mp3 in the DB as wav.
                # TODO: Remove when all files are managed
                rel_path = rel_path.replace('mp3', 'wav')
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

