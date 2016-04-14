from django.apps import AppConfig

class RoundwareApi2Config(AppConfig):
    name = 'api2'

    def ready(self):
        import roundware.api2.signals