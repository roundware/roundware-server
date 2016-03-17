from . import RoundwareCommand
from django.conf import settings
import os

class Command(RoundwareCommand):
    args = ''
    help = 'Clean Roundware Media directory by organizing mp3/wav into project_id subdirectories'

    def handle(self, *args, **options):
        self.stdout.write("Cleaning Roundware Media directory")
        # TODO: Optionally delete all unknown files/media
        # (known, unknown) = self.check_media()

        # TODO: Optionally delete all missing assets
        (found, not_found) = self.check_assets()

        moved = 0
        # Move all found files into a project specific sub-directory. This
        # is useful for old Roundware installs. The code should be removed in
        # the future.
        for asset in found:
            correct_project_id = str(asset.project.id)

            # Expecting "filename.wav" or "1/filename.jpg" data formats.
            filepath = os.path.dirname(asset.filename)

            # If the directory value in the filepath is not the project_id, correct it.
            if filepath != correct_project_id:

                project_directory = os.path.join(settings.MEDIA_ROOT, correct_project_id)

                # Create the directory if it doesn't exist.
                if not os.path.isdir(project_directory):
                    os.mkdir(project_directory)

                old_filepath = os.path.join(settings.MEDIA_ROOT, asset.filename)
                new_filepath = os.path.join(project_directory, asset.filename)
                new_filename = os.path.join(correct_project_id, asset.filename)

                # TODO: Why is this in two DB columns? Fix that.
                # Update both columns.
                asset.file = new_filename
                asset.filename = new_filename

                os.rename(old_filepath, new_filepath)
                self.stdout.write("Moved: %s" % new_filepath)

                # Move the mp3 also.
                # TODO: Remove this when all files are managed.
                old_filepath = old_filepath.replace('wav', 'mp3')
                new_filepath = new_filepath.replace('wav', 'mp3')
                os.rename(old_filepath, new_filepath)
                self.stdout.write("Moved: %s" % new_filepath)

                # Save *after* file move.
                asset.save()

                moved += 2

        self.stdout.write("Moved %s files." % moved)
