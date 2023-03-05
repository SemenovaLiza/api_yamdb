from django.apps import AppConfig


class ApiConfig(AppConfig):
    """Base configuration class for the API app."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
