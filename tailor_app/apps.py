from django.apps import AppConfig


class TailorAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tailor_app'

    def ready(self):
        import tailor_app.signals