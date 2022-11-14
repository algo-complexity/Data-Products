from django.apps import apps
from django.contrib import admin

from .apps import ApiConfig

app = apps.get_app_config(ApiConfig.name)
for model in app.get_models():
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass
