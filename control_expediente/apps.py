from django.apps import AppConfig


class ControlExpedienteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'control_expediente'

    def ready(self):
        import control_expediente.signals
