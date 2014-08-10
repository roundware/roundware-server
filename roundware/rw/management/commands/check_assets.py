from . import RoundwareCommand

class Command(RoundwareCommand):
    args = ''
    help = 'Checks that Assets exist as files in the media directory'

    def handle(self, *args, **options):
        self.stdout.write("Checking all Roundware Assets")

        (found, not_found) = self.check_assets()

        self.stdout.write("Assets found:   %s" % len(found))
        self.stdout.write("Assets missing: %s" % len(not_found))
