from django.apps import AppConfig


class BetsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "bets"
    verbose_name = "Apuestas"

    def ready(self):
        import bets.signals  # noqa
