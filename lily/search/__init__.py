from django.utils.module_loading import autodiscover_modules
from . import signals


def autodiscover():
    autodiscover_modules('search')


default_app_config = 'lily.search.apps.SearchConfig'
