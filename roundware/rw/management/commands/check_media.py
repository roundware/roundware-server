from . import RoundwareCommand

class Command(RoundwareCommand):
    args = ''
    help = 'Checks that Files in the media directory exist as Assets'

    def handle(self, *args, **options):
        self.stdout.write("Checking all Roundware Media files")

        (known, unknown) = self.check_media()

        self.stdout.write("Known files:   %s" % len(known))
        self.stdout.write("Unknown files: %s" % len(unknown))
