# Roundware Server is released under the GNU Affero General Public License v3.
# See COPYRIGHT.txt, AUTHORS.txt, and LICENSE.txt in the project root directory.

from django.apps import AppConfig

class RoundwareApi2Config(AppConfig):
    name = 'rw_api_2'

    def ready(self):
        import roundware.api2.signals